"""Carleman linearization of viscous Burgers (fixed-Dirichlet BC),
implicit-Euler time-marched, solved classically or via QSVT.

Two parts: a general-purpose QSVT linear-algebra toolkit (block encoding,
projector-controlled phase shift, QSVT circuit -- PDE-agnostic, reusable
for any QSVT linear solve), and `Burgers_Carlemann`, which builds the
Carleman-linearized system and time-marches it using that toolkit.
"""

import math
from functools import reduce

import numpy as np

from qiskit import QuantumCircuit
from qiskit.circuit.library import StatePreparation, UnitaryGate
from qiskit.quantum_info import Operator, Statevector


# =============================================================================
# General-purpose QSVT linear-algebra toolkit
# =============================================================================
#
# Circuit convention: an (n_wires)-qubit register is used, where qubit 0 is a
# single ancilla and qubits 1..n_wires-1 hold the block-encoded matrix / the
# state a vector is prepared in. Throughout, "qubit 0" refers to the
# most-significant qubit of the register (the leftmost bit of the state index)
# and "qubit n_wires-1" to the least-significant one; Qiskit numbers its
# qubits the opposite way (qubit 0 = least significant), so `_reversed_qubits`
# below performs the index relabelling needed to apply a matrix that was
# derived assuming the first convention on a circuit built in the second.


def next_power_of_two(n):
    """Smallest power of two greater than or equal to the positive integer n."""
    if n <= 1:
        return 1
    return 1 << (n - 1).bit_length()


def _sqrt_psd_matrix(M):
    """Matrix square root of a Hermitian positive-semidefinite matrix, via
    eigendecomposition (negative eigenvalues arising from floating-point
    error are clipped to zero)."""
    evs, vecs = np.linalg.eigh(M)
    evs = np.where(np.real(evs) > 0.0, np.real(evs), 0.0)
    return vecs @ np.diag(np.sqrt(evs)) @ np.conj(vecs.T)


def block_encode_matrix(A, n_wires):
    """Build the (2**n_wires x 2**n_wires) unitary matrix that block-encodes
    A in its top-left block:

        U(A) = [[ A_s,              sqrt(I - A_s A_s^dagger) ],
                [ sqrt(I - A_s^dagger A_s), -A_s^dagger        ]]

    where A_s = A / max(1, ||A A^dagger||_inf, ||A^dagger A||_inf) is A
    rescaled so that U(A) is unitary. Any leftover dimensions (when
    2**n_wires is larger than needed to fit A and its complement blocks) are
    padded with the identity.

    Returns the unitary matrix and the rescaling factor that was divided out
    of A (needed to undo the normalization on any quantity later extracted
    from a circuit using this block encoding).
    """
    A = np.atleast_2d(np.array(A, dtype=complex))
    d1, d2 = A.shape
    dim = 2 ** n_wires

    normalization = max(
        np.linalg.norm(A @ np.conj(A).T, ord=np.inf),
        np.linalg.norm(np.conj(A).T @ A, ord=np.inf),
    )
    A_scaled = A / max(normalization, 1.0)

    top_right = _sqrt_psd_matrix(np.eye(d1) - A_scaled @ np.conj(A_scaled).T)
    bottom_left = _sqrt_psd_matrix(np.eye(d2) - np.conj(A_scaled).T @ A_scaled)
    bottom_right = -np.conj(A_scaled).T

    U = np.block([[A_scaled, top_right], [bottom_left, bottom_right]])

    used = d1 + d2
    if used < dim:
        pad = dim - used
        U = np.block(
            [
                [U, np.zeros((used, pad), dtype=complex)],
                [np.zeros((pad, used), dtype=complex), np.eye(pad, dtype=complex)],
            ]
        )
    return U, normalization


def projector_phase_matrix(phi, dim, n_wires):
    """Diagonal projector-controlled phase shift: applies a phase e^{i*phi}
    to the first `dim` computational basis states of an n_wires-qubit
    register and e^{-i*phi} to the rest. This is the elementary gate that,
    interleaved with the block encoding, implements the QSVT polynomial."""
    N = 2 ** n_wires
    diag = np.concatenate(
        [np.full(dim, np.exp(1j * phi)), np.full(N - dim, np.exp(-1j * phi))]
    )
    return np.diag(diag)


def _reversed_qubits(wires, n_wires):
    """Relabel a most-significant-qubit-first wire list, defined over an
    n_wires-qubit register, into the Qiskit (least-significant-qubit-first)
    qubit indices that reproduce the same tensor structure for a matrix
    defined in the first convention."""
    mapped = [n_wires - 1 - w for w in wires]
    return mapped[::-1]


def build_qsvt_circuit(A, phi, n_wires=None, psi=None):
    """Build the circuit implementing QSVT on the block encoding of A with
    projector-controlled phase angles `phi`.

    If `psi` (a length-len(A) vector) is given, the circuit first prepares
    that state on the non-ancilla qubits, so that simulating the circuit
    yields QSVT(A) @ psi rather than just the QSVT(A) matrix.

    Returns the circuit and the block-encoding normalization factor (see
    `block_encode_matrix`).
    """
    if n_wires is None:
        n_wires = math.ceil(math.log2(A.shape[0])) + 1

    block_encoding, norm = block_encode_matrix(A, n_wires)
    projectors = [projector_phase_matrix(phi[i], len(A), n_wires) for i in range(len(phi))]

    UA_gate = UnitaryGate(block_encoding, label="U_A")
    UA_inv_gate = UA_gate.inverse()
    projector_gates = [UnitaryGate(P, label="Pi_phi") for P in projectors]

    qc = QuantumCircuit(n_wires)

    if psi is not None:
        state_wires = list(range(1, n_wires))
        qc.append(StatePreparation(psi), _reversed_qubits(state_wires, n_wires))

    qsvt_qubits = _reversed_qubits(list(range(n_wires)), n_wires)

    # QSVT sequence: Pi_0, U_A, Pi_1, U_A^-1, Pi_2, U_A, ..., ending on the
    # final projector-controlled phase shift.
    for idx, projector_gate in enumerate(projector_gates[:-1]):
        qc.append(projector_gate, qsvt_qubits)
        qc.append(UA_gate if idx % 2 == 0 else UA_inv_gate, qsvt_qubits)
    qc.append(projector_gates[-1], qsvt_qubits)

    return qc, norm


def qsvt_unitary(A, phi, n_wires=None):
    """Dense unitary matrix implementing QSVT on the block encoding of A."""
    qc, norm = build_qsvt_circuit(A, phi, n_wires=n_wires)
    return Operator(qc).data, norm


def qsvt_apply_state(A, phi, psi, n_wires=None):
    """Statevector obtained by preparing `psi` (length len(A)) on the
    non-ancilla qubits and applying QSVT on the block encoding of A."""
    qc, norm = build_qsvt_circuit(A, phi, n_wires=n_wires, psi=psi)
    return Statevector.from_instruction(qc).data, norm


def invert_matrix_qsvt(A, phi, s, n_wires=None):
    """Approximate A^{-1} by reading out the top-left block of QSVT(A) with
    phase angles `phi` chosen to implement (a bounded, scaled) 1/x, then
    undoing the block-encoding normalization and the 1/x scale factor s."""
    mat, norm = qsvt_unitary(A, phi, n_wires=n_wires)
    mat = mat[: A.shape[0], : A.shape[1]]
    return mat / (s * norm)


def solve_linear_system_qsvt(A, rhs, phi, s, n_wires=None):
    """Approximate the solution y of A @ y = rhs using the QSVT-based
    matrix inversion above, applied directly to the state |rhs> instead of
    reconstructing the dense inverse."""
    rhs_norm = np.linalg.norm(rhs, 2)
    rhs_normalized = rhs / rhs_norm
    out, norm = qsvt_apply_state(A, phi, rhs_normalized, n_wires=n_wires)
    out = out[: rhs_normalized.shape[0]].real
    return out * rhs_norm / (s * norm)


def qsvt_success_probability(A, psi_normalized, s):
    """Probability of post-selecting the ancilla branch that carries the
    QSVT-transformed target state, for a block encoding of A and QSVT scale
    factor s applied to the (normalized) input state psi_normalized."""
    A_scaled = A / np.linalg.norm(A, 2)
    _, singular_values, V = np.linalg.svd(A_scaled.T)
    overlap = V @ psi_normalized
    coeffs = (overlap * s) / singular_values
    return np.sum(coeffs ** 2)


def _qsp_to_qsvt_angles(angles):
    """Convert quantum-signal-processing phase angles (real-axis convention)
    into the equivalent projector-controlled-phase angles used directly by
    the QSVT circuit above. The two angle sequences implement the same
    polynomial transform, differing only by a fixed per-index offset."""
    angles = np.asarray(angles)
    num_angles = len(angles)
    offsets = np.empty(num_angles)
    offsets[0] = 3 * np.pi / 4 - (3 + num_angles % 4) * np.pi / 2
    offsets[1:-1] = np.pi / 2
    offsets[-1] = -np.pi / 4
    return angles + offsets


def compute_inverse_qsvt_angles(kappa, tolerance=1e-5):
    """Compute the QSVT phase angles implementing a bounded polynomial
    approximation of 1/x, valid for singular values within roughly [1/kappa,
    1] (larger kappa gives a better approximation over a wider range, at the
    cost of a longer phase-angle sequence / circuit).

    Returns the phase angles and the scale factor `s` by which the target
    polynomial was multiplied to keep it bounded on [-1, 1]; both are
    required by `invert_matrix_qsvt` / `solve_linear_system_qsvt` /
    `qsvt_success_probability` to recover the correctly-scaled result.
    """
    import pyqsp
    from pyqsp.angle_sequence import QuantumSignalProcessingPhases

    poly_coeffs, s = pyqsp.poly.PolyOneOverX().generate(
        kappa, return_coef=True, ensure_bounded=True, return_scale=True
    )
    qsp_angles = QuantumSignalProcessingPhases(
        poly_coeffs, signal_operator="Wx", tolerance=tolerance
    )
    qsvt_angles = _qsp_to_qsvt_angles(np.array(qsp_angles))
    return qsvt_angles, s


# =============================================================================
# Burgers' equation Carleman linearization
# =============================================================================


class Burgers_Carlemann:
    def __init__(self, N, N_T, total_time, mu, dt, u0, uN1, stencil='method_2', dtype=np.float64):
        super(Burgers_Carlemann, self).__init__()
        self.N = N
        self.N_T = N_T
        self.TOTAL_TIME = total_time
        self.MU = mu
        self.DT = dt
        self.U0 = u0
        self.UN1 = uN1
        self.DTYPE = dtype
        self.STENCIL = stencil
        return

    def get_x_dx(self):
        x = np.linspace(0, 1, self.N+2, dtype=self.DTYPE)
        dx = x[1] - x[0]
        return x, dx

    def get_n_timesteps(self):
        n_timesteps = int(np.round(self.TOTAL_TIME/self.DT))
        return n_timesteps

    def get_init_state(self):
        x, dx = self.get_x_dx()
        psi_init = np.sin(2*np.pi*x)
        return psi_init

    def get_u_desired(self):
        x, dx = self.get_x_dx()
        # Classical testing
        n_timesteps = int(np.round(self.TOTAL_TIME/self.DT))
        u = np.zeros((self.N+2, n_timesteps+1), dtype=self.DTYPE)
        u[:, 0] = np.sin(2*np.pi*x)
        # Forward in time central in space
        for j in range(n_timesteps):
            for i in range(1, self.N+1):
                if self.STENCIL == 'method_1':
                    t = (self.DT/(4*dx))*(u[i+1, j]**2 - u[i-1, j]**2)
                elif self.STENCIL == 'method_2':
                    t = (self.DT/(2*dx))*u[i, j]*(u[i+1, j] - u[i-1, j])
                u[i, j+1] = (u[i, j] +
                (self.MU*self.DT/(dx**2))*(u[i+1, j] - 2*u[i, j] + u[i-1, j]) -
                t
                )
        return u

    def construct_F2_matrix(self, n):
        """Constructs the F matrix for Carleman linearization given dy_i/dt = y_(i+1)^2 - y_(i-1)^2."""
        F = np.zeros((n, n**2), dtype=self.DTYPE)  # Shape (n, n^2)

        def index(i, j, n):
            """Maps (i, j) in y⊗2 to the corresponding index in flattened form (0-based)."""
            return (i-1) * n + (j-1)  # 0-based indexing

        if self.STENCIL == 'method_1':
            for i in range(1, n+1):  # 1-based indexing for y_i
                if i + 1 <= n:  # y_(i+1)^2 term
                    F[i-1, index(i+1, i+1, n)] = 1
                if i - 1 >= 1:  # y_(i-1)^2 term
                    F[i-1, index(i-1, i-1, n)] = -1
        elif self.STENCIL == 'method_2':
            for i in range(1, n+1):  # 1-based indexing for y_i
                if i + 1 <= n:  # y_i*y_(i+1) term
                    F[i-1, index(i, i+1, n)] = 1
                if i - 1 >= 1:  # y_i*y_(i-1) term
                    F[i-1, index(i, i-1, n)] = -1
        return F

    def get_a_b(self):
        x, dx = self.get_x_dx()
        a = self.MU/(dx**2)
        if self.STENCIL == 'method_1':
            b = -1/(4*dx)
        elif self.STENCIL == 'method_2':
            b = -1/(2*dx)
        return a, b

    def get_Fs(self):
        a, b = self.get_a_b()
        # F0
        F0 = np.zeros((self.N, 1), dtype=self.DTYPE)
        F0[0, 0] = a*self.U0 - b*(self.U0**2)
        F0[-1, 0] = a*self.UN1 + b*(self.UN1**2)
        # F1
        F1 = np.zeros((self.N, self.N), dtype=self.DTYPE)
        for i in range(self.N):
            if i == 0:
                F1[i, i] = -2*a
                F1[i, i+1] = a
            if i >0 and i < self.N-1:
                F1[i, i-1] = a
                F1[i, i] = -2*a
                F1[i, i+1] = a
            if i == self.N-1:
                F1[i, i-1] = a
                F1[i, i] = -2*a
        # F2
        F2 = self.construct_F2_matrix(self.N)
        F2 = F2*b
        return F0, F1, F2

    def kronecker_identity(self, d, n):
        I = np.eye(d, dtype=self.DTYPE)
        return reduce(np.kron, [I] * n)

    def get_A_ij(self, F0, F1, F2, j):
        A_j_jm1 = np.zeros((self.N**j, self.N**(j-1)), dtype=self.DTYPE)
        A_j_j = np.zeros((self.N**j, self.N**j), dtype=self.DTYPE)
        A_j_jp1 = np.zeros((self.N**j, self.N**(j+1)), dtype=self.DTYPE)
        for i in range(j):
            if i ==0:
                t2 = self.kronecker_identity(self.N, j-i-1)
                A_j_jm1 += np.kron(F0, t2)
                A_j_j += np.kron(F1, t2)
                A_j_jp1 += np.kron(F2, t2)
            if i>0 and i<(j-1):
                t1 = self.kronecker_identity(self.N, i)
                t2 = self.kronecker_identity(self.N, j-i-1)
                A_j_jm1 += np.kron(t1, np.kron(F0, t2))
                A_j_j += np.kron(t1, np.kron(F1, t2))
                A_j_jp1 += np.kron(t1, np.kron(F2, t2))
            if i==j-1:
                t1 = self.kronecker_identity(self.N, i)
                A_j_jm1 += np.kron(t1, F0)
                A_j_j += np.kron(t1, F1)
                A_j_jp1 += np.kron(t1, F2)
        return A_j_jm1, A_j_j, A_j_jp1

    def geometric_series(self, N, i):
        t = 0
        for j in range(1, i+1):
            t += self.N**j
        return t

    def get_A(self,):
        a, b = self.get_a_b()
        Dim = self.geometric_series(self.N, self.N_T)
        F0, F1, F2 = self.get_Fs()
        A = np.zeros((Dim, Dim), dtype=self.DTYPE)
        for i in range(1, self.N_T+1):
            if i == 1:
                r_min = 0
                r_max = self.geometric_series(self.N, i)
                c_min = 0
                c_max = self.geometric_series(self.N, i)
                A[r_min : r_max, c_min : c_max] = F1
                c_min = self.geometric_series(self.N, i)
                c_max = self.geometric_series(self.N, i+1)
                A[r_min : r_max, c_min : c_max] = F2
            if i>1 and i<self.N_T:
                A_j_jm1, A_j_j, A_j_jp1 = self.get_A_ij(F0, F1, F2, i)
                r_min = self.geometric_series(self.N, i-1)
                r_max = self.geometric_series(self.N, i)
                c_min = self.geometric_series(self.N, i-2)
                c_max = self.geometric_series(self.N, i-1)
                A[r_min : r_max, c_min : c_max] = A_j_jm1
                c_min = self.geometric_series(self.N, i-1)
                c_max = self.geometric_series(self.N, i)
                A[r_min : r_max, c_min : c_max] = A_j_j
                c_min = self.geometric_series(self.N, i)
                c_max = self.geometric_series(self.N, i+1)
                A[r_min : r_max, c_min : c_max] = A_j_jp1
            if i == self.N_T:
                A_j_jm1, A_j_j, A_j_jp1 = self.get_A_ij(F0, F1, F2, i)
                r_min = self.geometric_series(self.N, i-1)
                r_max = self.geometric_series(self.N, i)
                c_min = self.geometric_series(self.N, i-2)
                c_max = self.geometric_series(self.N, i-1)
                A[r_min : r_max, c_min : c_max] = A_j_jm1
                c_min = self.geometric_series(self.N, i-1)
                c_max = self.geometric_series(self.N, i)
                A[r_min : r_max, c_min : c_max] = A_j_j
        return A

    def kronecker_y(self, y, n):
        return reduce(np.kron, [y] * n)

    def get_B(self):
        a, b = self.get_a_b()
        Dim = self.geometric_series(self.N, self.N_T)
        F0, F1, F2 = self.get_Fs()
        b = np.zeros((Dim), dtype=self.DTYPE)
        b[:self.N] = F0[:, 0]
        return b

    def get_y_init(self):
        Dim = self.geometric_series(self.N, self.N_T)
        u = self.get_u_desired()
        y_init = np.zeros((Dim), dtype=self.DTYPE)
        t = u[1:-1, 0]
        for i in range(1, self.N_T+1):
            r_min = self.geometric_series(self.N, i-1)
            r_max = self.geometric_series(self.N, i)
            if i == 1:
                y_init[r_min : r_max] = t
            if i>1:
                y_init[r_min : r_max] = self.kronecker_y(t, i)
        return y_init

    def get_I_m_Adt(self):
        Dim = self.geometric_series(self.N, self.N_T)
        A_t = self.get_A()
        A = np.eye(Dim, dtype=self.DTYPE) - A_t*self.DT
        return A

    def get_I_p_Adt(self):
        Dim = self.geometric_series(self.N, self.N_T)
        A_t = self.get_A()
        A = np.eye(Dim, dtype=self.DTYPE) + A_t*self.DT
        return A

    def get_implicit_solver(self):
        y_init = self.get_y_init()
        n_timesteps = int(np.round(self.TOTAL_TIME/self.DT))
        A = self.get_I_m_Adt()
        B = self.get_B()
        u = self.get_u_desired()
        y_store = []
        RMSE_list = []
        t = np.concat(([self.U0], y_init[:self.N], [self.UN1]), dtype=self.DTYPE)
        y_prev = y_init.copy()
        y_store.append(t)
        for i in range(n_timesteps):
            print(f"Time step {i+1}/{n_timesteps}")
            L = y_prev + B*self.DT
            y_prev = np.linalg.solve(A, L)
            t = np.sum((y_prev[:self.N] - u[1:-1, i+1])**2)
            t = np.sqrt(t/self.N)
            RMSE_list.append(t)
            t = np.concat(([self.U0], y_prev[:self.N], [self.UN1]), dtype=self.DTYPE)
            y_store.append(t)
        RMSE_list = np.array(RMSE_list)
        return y_store, RMSE_list

    def get_explicit_solver(self):
        y_init = self.get_y_init()
        n_timesteps = int(np.round(self.TOTAL_TIME/self.DT))
        A = self.get_I_p_Adt()
        B = self.get_B()
        u = self.get_u_desired()
        y_store = []
        RMSE_list = []
        t = np.concat(([self.U0], y_init[:self.N], [self.UN1]), dtype=self.DTYPE)
        y_prev = y_init.copy()
        y_store.append(t)
        for i in range(n_timesteps):
            print(f"Time step {i+1}/{n_timesteps}")
            y_prev = A@y_prev + B*self.DT
            t = np.sum((y_prev[:self.N] - u[1:-1, i+1])**2)
            t = np.sqrt(t/self.N)
            RMSE_list.append(t)
            t = np.concat(([self.U0], y_prev[:self.N], [self.UN1]), dtype=self.DTYPE)
            y_store.append(t)
        RMSE_list = np.array(RMSE_list)
        return y_store, RMSE_list

    def get_implicit_solver_qsvt(self, phi, s, verbose=True):
        """Time-march the Carleman-linearized system with the same implicit
        Euler scheme as `get_implicit_solver`, but solving A @ y = rhs at
        each step approximately via the QSVT-based quantum linear solver
        (`solve_linear_system_qsvt`) instead of `numpy.linalg.solve`.

        `phi` and `s` are the QSVT phase angles and scale factor for a 1/x
        polynomial approximation, e.g. from `compute_inverse_qsvt_angles`.

        Returns the state history, the RMSE against the reference finite
        difference solution at each step, and the QSVT post-selection
        success probability at each step.
        """
        y_init = self.get_y_init()
        n_timesteps = self.get_n_timesteps()
        A = self.get_I_m_Adt()
        B = self.get_B()
        u = self.get_u_desired()

        # The block encoding requires a Hilbert space of size 2**n_wires;
        # round the (generally non-power-of-two) system dimension up so it
        # can be prepared exactly as a quantum state.
        Dim = A.shape[0]
        padded_dim = next_power_of_two(Dim)
        A_padded = np.eye(padded_dim, dtype=self.DTYPE)
        A_padded[:Dim, :Dim] = A

        y_store = []
        RMSE_list = []
        p_success_list = []

        t = np.concat(([self.U0], y_init[:self.N], [self.UN1]), dtype=self.DTYPE)
        y_prev = y_init.copy()
        y_store.append(t)

        for i in range(n_timesteps):
            if verbose:
                print(f"Time step {i+1}/{n_timesteps}")
            rhs = y_prev + B*self.DT
            rhs_padded = np.concatenate((rhs, np.zeros(padded_dim - Dim, dtype=self.DTYPE)))
            rhs_normalized = rhs_padded / np.linalg.norm(rhs_padded, 2)

            p_s = qsvt_success_probability(A_padded, rhs_normalized, s)
            p_success_list.append(p_s)

            y_prev = solve_linear_system_qsvt(A_padded.T, rhs_padded, phi, s)
            y_prev = y_prev[:Dim].real

            t = np.sum((y_prev[:self.N] - u[1:-1, i+1])**2)
            t = np.sqrt(t/self.N)
            RMSE_list.append(t)
            t = np.concat(([self.U0], y_prev[:self.N], [self.UN1]), dtype=self.DTYPE)
            y_store.append(t)

        RMSE_list = np.array(RMSE_list)
        return y_store, RMSE_list, p_success_list
