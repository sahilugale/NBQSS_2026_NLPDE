"""Linear-Combination-of-Unitaries (LCU) block encoding, alternative to the
dense/arbitrary block encoding in `qsvt_toolkit.py`. Standard PREPARE / SELECT /
PREPARE-dagger construction from A's Pauli decomposition A = sum_k c_k P_k;
postselecting the ancilla on |0..0> yields A/alpha in the system block
(alpha = sum_k |c_k|).

Two representations: `qsvt_apply_state_lcu` (fast statevector simulator,
never forms the block-encoding matrix explicitly) and
`build_lcu_block_encoding_gate_circuit` (real gate-level circuit, for
resource estimation). `lcu_block_encode_matrix` is dense-matrix only, for
validation on small examples.

Note: the Carleman-linearized matrix's Pauli decomposition is NOT sparse
(shift/Kronecker structure, not Pauli-diagonal) despite being sparse in the
computational basis -- see `resource_estimation.py` for the consequence.
"""

import math

import numpy as np

from qiskit import QuantumCircuit
from qiskit.circuit.library import StatePreparation, UnitaryGate
from qiskit.quantum_info import Operator, Pauli, SparsePauliOp, Statevector

from qsvt_toolkit import _reversed_qubits, projector_phase_matrix


# =============================================================================
# Pauli-LCU decomposition
# =============================================================================


def pauli_lcu_terms(A, tol=1e-10):
    """Decompose A into Pauli strings: returns (labels, coeffs, n_sys) with
    |coeffs| > tol, where A == sum_k coeffs[k] * Pauli(labels[k]).to_matrix()
    (up to the dropped small terms)."""
    A = np.asarray(A, dtype=complex)
    n_sys = int(round(np.log2(A.shape[0])))
    op = SparsePauliOp.from_operator(Operator(A))
    coeffs = op.coeffs
    keep = np.abs(coeffs) > tol
    labels = list(np.array(op.paulis.to_labels())[keep])
    coeffs = np.array(coeffs[keep])
    return labels, coeffs, n_sys


def _prepare_amplitudes(coeffs):
    """PREPARE target amplitudes sqrt(|c_k|)/sqrt(alpha), zero-padded to the
    next power of two, plus the ancilla qubit count and normalization
    alpha = sum_k |c_k|."""
    L = len(coeffs)
    m = max(1, math.ceil(math.log2(L))) if L > 1 else 1
    alpha = np.sum(np.abs(coeffs))
    prep = np.zeros(2 ** m, dtype=complex)
    prep[:L] = np.sqrt(np.abs(coeffs))
    prep = prep / np.sqrt(alpha)
    return prep, m, alpha


# =============================================================================
# Fast statevector-level simulation (used for the actual physics pipeline)
# =============================================================================


def _prepare_matrix(prep):
    """Dense (2**m x 2**m) unitary matrix for PREPARE|0> = prep. m is small
    (a handful of qubits worth of Pauli terms after rounding up to a power
    of two), so this matrix is cheap to form -- unlike the full block
    encoding, which would additionally carry a factor of the (much larger)
    system dimension."""
    m = int(round(np.log2(len(prep))))
    qc = QuantumCircuit(m)
    qc.append(StatePreparation(prep), range(m))
    return Operator(qc).data


def _apply_select(state_2d, labels, coeffs, conjugate):
    """Apply SELECT (or SELECT-dagger) in place to state_2d, shaped
    (dim_anc, dim_sys): branch k<len(coeffs) gets phase_k * Pauli(labels[k]),
    branch k>=len(coeffs) is left untouched (identity)."""
    for k, (label, coeff) in enumerate(zip(labels, coeffs)):
        phase = coeff / np.abs(coeff)
        if conjugate:
            phase = np.conj(phase)
        Pk = Pauli(label).to_matrix()
        state_2d[k, :] = phase * (Pk @ state_2d[k, :])
    return state_2d


def _apply_projector_phase(state, phi, dim_sys):
    """Diagonal projector-controlled phase shift: +phi on the ancilla-zero
    branch (the first dim_sys entries of the flat state), -phi elsewhere."""
    out = state.copy()
    out[:dim_sys] *= np.exp(1j * phi)
    out[dim_sys:] *= np.exp(-1j * phi)
    return out


def qsvt_apply_state_lcu(A, phi, psi, tol=1e-10):
    """Statevector obtained by preparing `psi` (length len(A)) in the
    ancilla-zero branch and applying QSVT with phase angles `phi` on the LCU
    block encoding of A, without ever forming that block encoding as a dense
    matrix. Returns (state, alpha), state of length 2**m * len(A)."""
    labels, coeffs, n_sys = pauli_lcu_terms(A, tol=tol)
    prep, m, alpha = _prepare_amplitudes(coeffs)
    PREPARE = _prepare_matrix(prep)
    PREPARE_dag = np.conj(PREPARE).T

    dim_anc = 2 ** m
    dim_sys = A.shape[0]

    def apply_UA(state, adjoint):
        state_2d = state.reshape(dim_anc, dim_sys)
        state_2d = PREPARE @ state_2d
        state_2d = _apply_select(state_2d, labels, coeffs, conjugate=adjoint)
        state_2d = PREPARE_dag @ state_2d
        return state_2d.reshape(-1)

    state = np.zeros(dim_anc * dim_sys, dtype=complex)
    state[:dim_sys] = psi

    n_angles = len(phi)
    for idx in range(n_angles - 1):
        state = _apply_projector_phase(state, phi[idx], dim_sys)
        state = apply_UA(state, adjoint=(idx % 2 == 1))
    state = _apply_projector_phase(state, phi[-1], dim_sys)

    return state, alpha


def solve_linear_system_qsvt_lcu(A, rhs, phi, s, tol=1e-10):
    """LCU-block-encoding analogue of `solve_linear_system_qsvt`: approximate
    the solution y of A @ y = rhs via QSVT applied to the LCU block
    encoding of A."""
    rhs_norm = np.linalg.norm(rhs, 2)
    rhs_normalized = rhs / rhs_norm
    out, alpha = qsvt_apply_state_lcu(A, phi, rhs_normalized, tol=tol)
    out = out[: rhs_normalized.shape[0]].real
    return out * rhs_norm / (s * alpha)


# =============================================================================
# Dense matrix form (small examples / validating the gate-level circuit only)
# =============================================================================


def lcu_block_encode_matrix(A, tol=1e-10):
    """Exact dense unitary matrix for the PREPARE/SELECT/PREPARE-dagger LCU
    block encoding of A. Only practical when the number of Pauli terms L is
    small (a handful of ancilla qubits) -- forming this matrix costs
    O((2**m * len(A))**2), which is exactly what `qsvt_apply_state_lcu`
    avoids for the actual Burgers-Carlemann system. Returns
    (U, alpha, m, n_sys) with U[:dim, :dim] == A / alpha for dim = len(A).
    """
    labels, coeffs, n_sys = pauli_lcu_terms(A, tol=tol)
    prep, m, alpha = _prepare_amplitudes(coeffs)
    dim_anc = 2 ** m
    dim_sys = A.shape[0]
    L = len(coeffs)

    PREPARE = _prepare_matrix(prep)

    SELECT = np.zeros((dim_anc * dim_sys, dim_anc * dim_sys), dtype=complex)
    for k in range(dim_anc):
        if k < L:
            phase = coeffs[k] / np.abs(coeffs[k])
            block = phase * Pauli(labels[k]).to_matrix()
        else:
            block = np.eye(dim_sys, dtype=complex)
        SELECT[k * dim_sys:(k + 1) * dim_sys, k * dim_sys:(k + 1) * dim_sys] = block

    U = np.kron(np.conj(PREPARE).T, np.eye(dim_sys)) @ SELECT @ np.kron(PREPARE, np.eye(dim_sys))
    return U, alpha, m, n_sys


# =============================================================================
# Gate-level circuits (for resource estimation only -- see resource_estimation.py)
# =============================================================================


def build_prepare_gate_circuit(coeffs):
    """Gate-level PREPARE circuit: a `StatePreparation` instruction on
    m = ceil(log2(len(coeffs))) ancilla qubits realizing PREPARE|0> as
    defined in the module docstring."""
    prep, m, alpha = _prepare_amplitudes(coeffs)
    qc = QuantumCircuit(m, name="PREPARE")
    qc.append(StatePreparation(prep), range(m))
    return qc, m, alpha


def build_select_gate_circuit(labels, coeffs, n_sys, m):
    """Gate-level SELECT circuit: for each Pauli term k, apply its
    non-identity single-qubit Pauli factors to the system register, each
    controlled on the m-qubit ancilla register reading out state k. The
    phase c_k / |c_k| is folded into the system-qubit-0 factor of each term
    (using an identity factor there, carrying only the phase, if the term
    would not otherwise touch qubit 0).

    The ancilla register occupies the top m qubits (indices n_sys .. n_sys +
    m - 1) and the system register the bottom n_sys qubits (indices 0 ..
    n_sys - 1), so that Qiskit's own (little-endian) qubit ordering makes
    "ancilla = 0" exactly the top-left (dim_sys x dim_sys) block of the
    resulting unitary -- matching the flat-index convention used by
    `lcu_block_encode_matrix` and the fast statevector simulator above.
    """
    qc = QuantumCircuit(m + n_sys, name="SELECT")
    ancilla = list(range(n_sys, n_sys + m))
    system = list(range(n_sys))

    pauli_x = np.array([[0, 1], [1, 0]], dtype=complex)
    pauli_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    pauli_z = np.array([[1, 0], [0, -1]], dtype=complex)

    for k, (label, coeff) in enumerate(zip(labels, coeffs)):
        pauli_obj = Pauli(label)
        phase = coeff / np.abs(coeff)
        phase_applied = False

        for q in range(n_sys):
            x_bit, z_bit = bool(pauli_obj.x[q]), bool(pauli_obj.z[q])
            if x_bit and not z_bit:
                mat = pauli_x
            elif x_bit and z_bit:
                mat = pauli_y
            elif z_bit:
                mat = pauli_z
            else:
                mat = None

            if mat is None:
                continue
            if q == 0 and not phase_applied:
                mat = phase * mat
                phase_applied = True

            gate = UnitaryGate(mat, label=f"P{k}_{q}").control(m, ctrl_state=k, annotated=True)
            qc.append(gate, ancilla + [system[q]])

        if not phase_applied:
            # All-identity string (or a term whose qubit-0 factor is
            # identity): apply the phase alone, controlled on ancilla = k.
            gate = UnitaryGate(phase * np.eye(2, dtype=complex)).control(m, ctrl_state=k, annotated=True)
            qc.append(gate, ancilla + [system[0]])

    return qc


def build_lcu_block_encoding_gate_circuit(A, tol=1e-10):
    """Full gate-level PREPARE / SELECT / PREPARE-dagger circuit for the LCU
    block encoding of A, for resource estimation (real controlled-Pauli
    gates, not a single opaque `UnitaryGate`). Returns
    (circuit, alpha, m, n_sys, num_terms)."""
    labels, coeffs, n_sys = pauli_lcu_terms(A, tol=tol)
    prepare_qc, m, alpha = build_prepare_gate_circuit(coeffs)
    select_qc = build_select_gate_circuit(labels, coeffs, n_sys, m)

    ancilla = list(range(n_sys, n_sys + m))
    qc = QuantumCircuit(m + n_sys, name="U_A_lcu")
    qc.append(prepare_qc.to_instruction(), ancilla)
    qc.append(select_qc.to_instruction(), range(m + n_sys))
    qc.append(prepare_qc.inverse().to_instruction(), ancilla)
    return qc, alpha, m, n_sys, len(coeffs)
