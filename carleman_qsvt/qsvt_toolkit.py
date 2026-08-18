"""General-purpose QSVT linear-algebra toolkit -- block encoding,
projector-controlled phase shift, QSVT circuit construction, and the
Chebyshev-polynomial phase-angle computation for 1/x. PDE-agnostic, used
by both `periodic_burgers.py` and `kdv.py` (via `periodic_carleman.py`)
for their actual Carleman-linearized systems.
"""

import math

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

