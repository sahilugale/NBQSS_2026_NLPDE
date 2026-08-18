"""Generic periodic-BC, unforced Carleman linearization,

    u_t = F1 u + F2 (u kron u),

used by `kdv.py` and `periodic_burgers.py`. Block assembly, Crank-Nicolson
and implicit-Euler marching, dense-QSVT and Pauli-LCU solves are all
PDE-agnostic; subclasses implement only `get_Fs()` and `get_init_state()`.
No F0 forcing term (periodic BC, autonomous/homogeneous ODE).
"""

from functools import reduce

import numpy as np
from scipy.integrate import solve_ivp

from qsvt_toolkit import next_power_of_two, qsvt_success_probability, solve_linear_system_qsvt
from lcu import solve_linear_system_qsvt_lcu


class PeriodicCarleman:
    def __init__(self, N, N_T, total_time, dt, dtype=np.float64):
        self.N = N
        self.N_T = N_T
        self.TOTAL_TIME = total_time
        self.DT = dt
        self.DTYPE = dtype

    def get_x_dx(self):
        x = np.linspace(0, 1, self.N, endpoint=False, dtype=self.DTYPE)
        dx = x[1] - x[0]
        return x, dx

    def get_n_timesteps(self):
        return int(np.round(self.TOTAL_TIME / self.DT))

    def get_Fs(self):
        """Returns (F1, F2): the linear and quadratic operators of
        u_t = F1 u + F2 (u kron u). PDE-specific, implemented by subclasses."""
        raise NotImplementedError

    def get_init_state(self):
        """PDE-specific, implemented by subclasses."""
        raise NotImplementedError

    # --- exact (untruncated) nonlinear reference, for the classical baseline ---

    def _reference_rhs(self, t, y, F1, F2):
        return F1 @ y + F2 @ np.kron(y, y)

    def get_u_desired(self):
        """Reference solution of the EXACT (non-Carleman-truncated) nonlinear
        ODE for this discretization, via high-accuracy RK45. Returns shape
        (N, n_timesteps+1)."""
        F1, F2 = self.get_Fs()
        n_timesteps = self.get_n_timesteps()
        t_eval = np.linspace(0, self.TOTAL_TIME, n_timesteps + 1)
        u0 = self.get_init_state()
        sol = solve_ivp(
            self._reference_rhs, (t_eval[0], t_eval[-1]), u0, t_eval=t_eval,
            args=(F1, F2), method="RK45", rtol=1e-9, atol=1e-11,
        )
        if not sol.success:
            raise RuntimeError(f"Reference integration failed: {sol.message}")
        return sol.y.astype(self.DTYPE)

    # --- Carleman block-matrix assembly (no F0 forcing) ---

    def kronecker_identity(self, d, n):
        if n == 0:
            return np.eye(1, dtype=self.DTYPE)
        return reduce(np.kron, [np.eye(d, dtype=self.DTYPE)] * n)

    def geometric_series(self, N, i):
        return sum(N ** j for j in range(1, i + 1))

    def get_A_ij(self, F1, F2, j):
        A_j_j = np.zeros((self.N ** j, self.N ** j), dtype=self.DTYPE)
        A_j_jp1 = np.zeros((self.N ** j, self.N ** (j + 1)), dtype=self.DTYPE)
        for i in range(j):
            t1 = self.kronecker_identity(self.N, i)
            t2 = self.kronecker_identity(self.N, j - i - 1)
            A_j_j += np.kron(t1, np.kron(F1, t2))
            A_j_jp1 += np.kron(t1, np.kron(F2, t2))
        return A_j_j, A_j_jp1

    def get_A(self):
        F1, F2 = self.get_Fs()
        Dim = self.geometric_series(self.N, self.N_T)
        A = np.zeros((Dim, Dim), dtype=self.DTYPE)
        for i in range(1, self.N_T + 1):
            A_j_j, A_j_jp1 = self.get_A_ij(F1, F2, i)
            r_min = self.geometric_series(self.N, i - 1)
            r_max = self.geometric_series(self.N, i)
            c_min = self.geometric_series(self.N, i - 1)
            c_max = self.geometric_series(self.N, i)
            A[r_min:r_max, c_min:c_max] = A_j_j
            if i < self.N_T:
                c_min2 = self.geometric_series(self.N, i)
                c_max2 = self.geometric_series(self.N, i + 1)
                A[r_min:r_max, c_min2:c_max2] = A_j_jp1
        return A

    def kronecker_y(self, y, n):
        return reduce(np.kron, [y] * n)

    def get_y_init(self):
        Dim = self.geometric_series(self.N, self.N_T)
        u0 = self.get_init_state()
        y_init = np.zeros(Dim, dtype=self.DTYPE)
        for i in range(1, self.N_T + 1):
            r_min = self.geometric_series(self.N, i - 1)
            r_max = self.geometric_series(self.N, i)
            y_init[r_min:r_max] = self.kronecker_y(u0, i) if i > 1 else u0
        return y_init

    def get_B(self):
        """No forcing term under periodic BC -- kept only so the shared
        (Burgers-Dirichlet-style) implicit-Euler step `L = y_prev + B*DT`
        still works unchanged, and so the LCU driver below has a symmetric
        interface."""
        Dim = self.geometric_series(self.N, self.N_T)
        return np.zeros(Dim, dtype=self.DTYPE)

    def get_I_m_Adt(self):
        Dim = self.geometric_series(self.N, self.N_T)
        A = self.get_A()
        return np.eye(Dim, dtype=self.DTYPE) - A * self.DT

    def get_crank_nicolson_matrices(self):
        """Trapezoidal-rule matrices (I - dt/2 A) y_{n+1} = (I + dt/2 A) y_n,
        O(dt^2) local error vs. implicit Euler's O(dt) -- Costa, Schleich,
        Morales & Berry, npj Quantum Information 11:141 (2025) motivate
        higher-order integrators for exactly this kind of Carleman-linearized
        solve. Same A (and hence same block-encoding norm/qubit count) as
        implicit Euler; only the coefficient changes."""
        Dim = self.geometric_series(self.N, self.N_T)
        A = self.get_A()
        I = np.eye(Dim, dtype=self.DTYPE)
        return I - 0.5 * self.DT * A, I + 0.5 * self.DT * A

    # --- time marching ---

    def get_implicit_solver(self):
        y_init = self.get_y_init()
        n_timesteps = self.get_n_timesteps()
        A = self.get_I_m_Adt()
        B = self.get_B()
        u = self.get_u_desired()

        y_store = [y_init[: self.N].copy()]
        RMSE_list = []
        y_prev = y_init.copy()
        for i in range(n_timesteps):
            L = y_prev + B * self.DT
            y_prev = np.linalg.solve(A, L)
            err = np.sqrt(np.mean((y_prev[: self.N] - u[:, i + 1]) ** 2))
            RMSE_list.append(err)
            y_store.append(y_prev[: self.N].copy())
        return y_store, np.array(RMSE_list)

    def get_crank_nicolson_solver(self):
        """Classical (no QSVT) Crank-Nicolson time march -- same structure as
        `get_implicit_solver`, for comparing convergence order directly."""
        y_init = self.get_y_init()
        n_timesteps = self.get_n_timesteps()
        LHS, RHS_op = self.get_crank_nicolson_matrices()
        u = self.get_u_desired()

        y_store = [y_init[: self.N].copy()]
        RMSE_list = []
        y_prev = y_init.copy()
        for i in range(n_timesteps):
            y_prev = np.linalg.solve(LHS, RHS_op @ y_prev)
            err = np.sqrt(np.mean((y_prev[: self.N] - u[:, i + 1]) ** 2))
            RMSE_list.append(err)
            y_store.append(y_prev[: self.N].copy())
        return y_store, np.array(RMSE_list)

    def get_crank_nicolson_solver_qsvt(self, phi, s, verbose=True):
        """QSVT analogue of `get_crank_nicolson_solver`: each linear solve
        block-encodes LHS = I - dt/2 A instead of implicit Euler's I - dt A;
        the RHS = (I + dt/2 A) y_prev is a classical matrix-vector product
        computed before state preparation, no extra quantum cost."""
        y_init = self.get_y_init()
        n_timesteps = self.get_n_timesteps()
        LHS, RHS_op = self.get_crank_nicolson_matrices()
        u = self.get_u_desired()

        Dim = LHS.shape[0]
        padded_dim = next_power_of_two(Dim)
        LHS_padded = np.eye(padded_dim, dtype=self.DTYPE)
        LHS_padded[:Dim, :Dim] = LHS

        y_store = [y_init[: self.N].copy()]
        RMSE_list, p_success_list = [], []
        y_prev = y_init.copy()

        for i in range(n_timesteps):
            if verbose:
                print(f"Time step {i+1}/{n_timesteps}")
            rhs = RHS_op @ y_prev
            rhs_padded = np.concatenate((rhs, np.zeros(padded_dim - Dim, dtype=self.DTYPE)))
            rhs_normalized = rhs_padded / np.linalg.norm(rhs_padded, 2)

            p_success_list.append(qsvt_success_probability(LHS_padded, rhs_normalized, s))

            y_prev = solve_linear_system_qsvt(LHS_padded.T, rhs_padded, phi, s)
            y_prev = y_prev[:Dim].real

            err = np.sqrt(np.mean((y_prev[: self.N] - u[:, i + 1]) ** 2))
            RMSE_list.append(err)
            y_store.append(y_prev[: self.N].copy())

        return y_store, np.array(RMSE_list), p_success_list

    def get_implicit_solver_qsvt(self, phi, s, verbose=True):
        """Same implicit-Euler time march as `get_implicit_solver`, but each
        A @ y = rhs solve is done via QSVT on a dense block encoding of A
        (see `qsvt_toolkit.solve_linear_system_qsvt`). Returns the state
        history, RMSE against the exact-ODE reference at each step, and the
        QSVT post-selection success probability at each step."""
        y_init = self.get_y_init()
        n_timesteps = self.get_n_timesteps()
        A = self.get_I_m_Adt()
        B = self.get_B()
        u = self.get_u_desired()

        Dim = A.shape[0]
        padded_dim = next_power_of_two(Dim)
        A_padded = np.eye(padded_dim, dtype=self.DTYPE)
        A_padded[:Dim, :Dim] = A

        y_store = [y_init[: self.N].copy()]
        RMSE_list, p_success_list = [], []
        y_prev = y_init.copy()

        for i in range(n_timesteps):
            if verbose:
                print(f"Time step {i+1}/{n_timesteps}")
            rhs = y_prev + B * self.DT
            rhs_padded = np.concatenate((rhs, np.zeros(padded_dim - Dim, dtype=self.DTYPE)))
            rhs_normalized = rhs_padded / np.linalg.norm(rhs_padded, 2)

            p_success_list.append(qsvt_success_probability(A_padded, rhs_normalized, s))

            y_prev = solve_linear_system_qsvt(A_padded.T, rhs_padded, phi, s)
            y_prev = y_prev[:Dim].real

            err = np.sqrt(np.mean((y_prev[: self.N] - u[:, i + 1]) ** 2))
            RMSE_list.append(err)
            y_store.append(y_prev[: self.N].copy())

        return y_store, np.array(RMSE_list), p_success_list


def get_implicit_solver_qsvt_lcu(carleman, phi, s, tol=1e-10, verbose=True):
    """Pauli-LCU-block-encoding analogue of
    `PeriodicCarleman.get_implicit_solver_qsvt`. Works with any
    `PeriodicCarleman` subclass (KdV or periodic Burgers)."""
    y_init = carleman.get_y_init()
    n_timesteps = carleman.get_n_timesteps()
    A = carleman.get_I_m_Adt()
    B = carleman.get_B()
    u = carleman.get_u_desired()
    N = carleman.N

    Dim = A.shape[0]
    padded_dim = next_power_of_two(Dim)
    A_padded = np.eye(padded_dim, dtype=carleman.DTYPE)
    A_padded[:Dim, :Dim] = A

    y_store = [y_init[:N].copy()]
    RMSE_list, p_success_list = [], []
    y_prev = y_init.copy()

    for i in range(n_timesteps):
        if verbose:
            print(f"Time step {i+1}/{n_timesteps}")
        rhs = y_prev + B * carleman.DT
        rhs_padded = np.concatenate((rhs, np.zeros(padded_dim - Dim, dtype=carleman.DTYPE)))
        rhs_normalized = rhs_padded / np.linalg.norm(rhs_padded, 2)

        p_success_list.append(qsvt_success_probability(A_padded, rhs_normalized, s))

        y_prev = solve_linear_system_qsvt_lcu(A_padded.T, rhs_padded, phi, s, tol=tol)
        y_prev = y_prev[:Dim].real

        err = np.sqrt(np.mean((y_prev[:N] - u[:, i + 1]) ** 2))
        RMSE_list.append(err)
        y_store.append(y_prev[:N].copy())

    return y_store, np.array(RMSE_list), p_success_list


def get_crank_nicolson_solver_qsvt_lcu(carleman, phi, s, tol=1e-10, verbose=True):
    """Pauli-LCU analogue of `PeriodicCarleman.get_crank_nicolson_solver_qsvt`
    (mirrors `get_implicit_solver_qsvt_lcu` above, LHS/RHS swapped for the
    trapezoidal rule)."""
    y_init = carleman.get_y_init()
    n_timesteps = carleman.get_n_timesteps()
    LHS, RHS_op = carleman.get_crank_nicolson_matrices()
    u = carleman.get_u_desired()
    N = carleman.N

    Dim = LHS.shape[0]
    padded_dim = next_power_of_two(Dim)
    LHS_padded = np.eye(padded_dim, dtype=carleman.DTYPE)
    LHS_padded[:Dim, :Dim] = LHS

    y_store = [y_init[:N].copy()]
    RMSE_list, p_success_list = [], []
    y_prev = y_init.copy()

    for i in range(n_timesteps):
        if verbose:
            print(f"Time step {i+1}/{n_timesteps}")
        rhs = RHS_op @ y_prev
        rhs_padded = np.concatenate((rhs, np.zeros(padded_dim - Dim, dtype=carleman.DTYPE)))
        rhs_normalized = rhs_padded / np.linalg.norm(rhs_padded, 2)

        p_success_list.append(qsvt_success_probability(LHS_padded, rhs_normalized, s))

        y_prev = solve_linear_system_qsvt_lcu(LHS_padded.T, rhs_padded, phi, s, tol=tol)
        y_prev = y_prev[:Dim].real

        err = np.sqrt(np.mean((y_prev[:N] - u[:, i + 1]) ** 2))
        RMSE_list.append(err)
        y_store.append(y_prev[:N].copy())

    return y_store, np.array(RMSE_list), p_success_list
