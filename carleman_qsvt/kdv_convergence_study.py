"""Classical convergence check (no quantum code): does Carleman
linearization of KdV converge as truncation order N_T increases, the way
it does for dissipative Burgers? KdV's F1 = -delta*D3 is skew-symmetric
(non-dissipative), unlike Burgers' F1 = nu*D2 -- ground truth is the exact
(untruncated) nonlinear ODE via RK45, isolating Carleman truncation error
from spatial discretization error. Findings: see project report.
"""

import sys
import os

import numpy as np
from functools import reduce
from scipy.integrate import solve_ivp

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from discretization import (  # noqa: E402
    periodic_D1,
    periodic_D2,
    periodic_D3,
    construct_F2_periodic,
    get_F1_F2_kdv,
    get_F1_F2_burgers,
)


# =============================================================================
# Exact (untruncated) nonlinear reference solution
# =============================================================================

def reference_rhs(t, y, F1, F2, N):
    quad = F2 @ np.kron(y, y)
    return F1 @ y + quad


def reference_solution(u0, F1, F2, N, t_eval):
    sol = solve_ivp(
        reference_rhs, (t_eval[0], t_eval[-1]), u0, t_eval=t_eval,
        args=(F1, F2, N), method="RK45", rtol=1e-9, atol=1e-11,
    )
    if not sol.success:
        raise RuntimeError(f"Reference integration failed: {sol.message}")
    return sol.y.T  # shape (len(t_eval), N)


# =============================================================================
# Carleman linearization (no F0 forcing) -- block matrix assembly
# =============================================================================

def kronecker_identity(N, n):
    if n == 0:
        return np.eye(1)
    return reduce(np.kron, [np.eye(N)] * n)


def geometric_series(N, i):
    return sum(N ** j for j in range(1, i + 1))


def get_A_ij_noforce(F1, F2, N, j):
    """Same recurrence as Burgers_Carlemann.get_A_ij but without the F0
    (sub-diagonal) contribution, since there is no constant forcing term."""
    A_j_j = np.zeros((N ** j, N ** j))
    A_j_jp1 = np.zeros((N ** j, N ** (j + 1)))
    for i in range(j):
        t1 = kronecker_identity(N, i)
        t2 = kronecker_identity(N, j - i - 1)
        A_j_j += np.kron(t1, np.kron(F1, t2))
        A_j_jp1 += np.kron(t1, np.kron(F2, t2))
    return A_j_j, A_j_jp1


def build_carleman_A(F1, F2, N, N_T):
    Dim = geometric_series(N, N_T)
    A = np.zeros((Dim, Dim))
    for i in range(1, N_T + 1):
        A_j_j, A_j_jp1 = get_A_ij_noforce(F1, F2, N, i)
        r_min = geometric_series(N, i - 1)
        r_max = geometric_series(N, i)
        c_min = geometric_series(N, i - 1)
        c_max = geometric_series(N, i)
        A[r_min:r_max, c_min:c_max] = A_j_j
        if i < N_T:
            c_min2 = geometric_series(N, i)
            c_max2 = geometric_series(N, i + 1)
            A[r_min:r_max, c_min2:c_max2] = A_j_jp1
    return A


def get_y_init(u0, N, N_T):
    Dim = geometric_series(N, N_T)
    y0 = np.zeros(Dim)
    for i in range(1, N_T + 1):
        r_min = geometric_series(N, i - 1)
        r_max = geometric_series(N, i)
        y0[r_min:r_max] = reduce(np.kron, [u0] * i)
    return y0


def carleman_implicit_euler(F1, F2, N, N_T, u0, dt, n_steps):
    A = build_carleman_A(F1, F2, N, N_T)
    Dim = A.shape[0]
    M = np.eye(Dim) - A * dt
    y = get_y_init(u0, N, N_T)
    ys = [y[:N].copy()]
    for _ in range(n_steps):
        y = np.linalg.solve(M, y)
        ys.append(y[:N].copy())
    return np.array(ys), A


# =============================================================================
# Convergence sweep
# =============================================================================

def rmse(a, b):
    return np.sqrt(np.mean((a - b) ** 2))


def run_sweep(label, F1_builder, N, delta_or_mu, dx, u0, T, dt, N_T_values):
    F1, F2 = F1_builder(N, delta_or_mu, dx)
    n_steps = int(round(T / dt))
    t_eval = np.linspace(0, T, n_steps + 1)

    ref = reference_solution(u0, F1, F2, N, t_eval)

    sym_part = 0.5 * (F1 + F1.T)
    eigvals_sym = np.linalg.eigvalsh(sym_part)
    lin_mag = np.linalg.norm(F1 @ u0)
    quad_mag = np.linalg.norm(F2 @ np.kron(u0, u0))
    print(f"\n=== {label} ===")
    print(f"F1 symmetric-part eigenvalues (dissipation indicator): "
          f"max={eigvals_sym.max():.4g}, min={eigvals_sym.min():.4g}")
    print(f"  (Burgers: strictly negative => dissipative. "
          f"KdV: ~0 => no dissipation.)")
    print(f"  |F1 u0| = {lin_mag:.4g}   |F2 (u0 kron u0)| = {quad_mag:.4g}   "
          f"ratio linear/nonlinear = {lin_mag/max(quad_mag,1e-30):.3g}")

    results = {}
    for N_T in N_T_values:
        try:
            ys, A = carleman_implicit_euler(F1, F2, N, N_T, u0, dt, n_steps)
        except np.linalg.LinAlgError as e:
            print(f"  N_T={N_T}: implicit solve failed ({e})")
            results[N_T] = None
            continue
        errs = np.array([rmse(ys[k], ref[k]) for k in range(len(t_eval))])
        eigvals_A = np.linalg.eigvals(A)
        max_real = eigvals_A.real.max()
        blew_up = not np.all(np.isfinite(ys)) or errs[-1] > 10 * (errs[0] + 1e-12) and errs[-1] > 1.0
        print(f"  N_T={N_T}: dim={A.shape[0]:5d}  RMSE(t=0)={errs[0]:.3e}  "
              f"RMSE(t=T)={errs[-1]:.3e}  max Re(eig A)={max_real:.3g}"
              f"{'  <-- BLOWUP' if blew_up else ''}")
        results[N_T] = dict(errs=errs, t=t_eval, max_real_eig=max_real)
    return results, ref, t_eval


if __name__ == "__main__":
    N = 6          # grid points (small: Carleman dim grows as N + N^2 + N^3 + ...)
    T = 0.5
    dt = 0.01
    N_T_values = [1, 2, 3]

    x = np.linspace(0, 1, N, endpoint=False)
    dx = x[1] - x[0]

    # --- Baseline sanity check: Burgers (dissipative), should converge ---
    u0_burgers = 0.5 * np.sin(2 * np.pi * x)
    run_sweep("Burgers (mu=0.1, dissipative baseline)", get_F1_F2_burgers,
              N, 0.1, dx, u0_burgers, T, dt, N_T_values)

    # --- KdV, small amplitude ---
    u0_kdv_small = 0.1 * np.cos(4 * np.pi * x)
    run_sweep("KdV (delta=0.05, small amplitude)", get_F1_F2_kdv,
              N, 0.05, dx, u0_kdv_small, T, dt, N_T_values)

    # --- KdV, challenge-suggested amplitude ---
    u0_kdv = np.cos(4 * np.pi * x)
    run_sweep("KdV (delta=0.05, cos(4*pi*x), challenge amplitude)", get_F1_F2_kdv,
              N, 0.05, dx, u0_kdv, T, dt, N_T_values)

    # --- KdV, larger delta ---
    u0_kdv2 = np.cos(4 * np.pi * x)
    run_sweep("KdV (delta=0.2, cos(4*pi*x))", get_F1_F2_kdv,
              N, 0.2, dx, u0_kdv2, T, dt, N_T_values)

    # --- KdV, delta scan to find a regime where nonlinearity is not
    # swamped by the 1/dx^3 dispersion coefficient. Smaller delta pushes
    # toward the (undamped, undispersed) inviscid-Burgers limit, which can
    # form a shock in finite time -- the reference integrator failing is
    # itself informative, not just noise, so we catch and report it.
    for delta in [0.05, 0.02, 0.01, 0.005, 0.002]:
        try:
            run_sweep(f"KdV delta scan (delta={delta}, cos(4*pi*x))", get_F1_F2_kdv,
                      N, delta, dx, u0_kdv2, T, dt, N_T_values)
        except RuntimeError as e:
            print(f"\n=== KdV delta scan (delta={delta}) ===")
            print(f"  Reference integration blew up: {e}")
            print(f"  (likely shock formation: dispersion too weak relative "
                  f"to grid resolution to regularize the advection term)")
