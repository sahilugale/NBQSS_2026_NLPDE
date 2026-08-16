"""Resource comparison between the two QSVT block encodings (dense,
`burgers.block_encode_matrix`; Pauli-LCU, `lcu.py`) used by the
Carleman-linearized Burgers/KdV solves. Builds ONE block-encoding layer as
a transpiled Qiskit circuit per method, then extrapolates to the full
QSVT circuit (kappa=8, 560 phase angles) by multiplying out the per-layer
gate counts, rather than transpiling all 560 layers directly.

`_carleman_matrix` / `_carleman_matrix_kdv` build the Burgers/KdV systems
(N=5, N_T=2, matching each notebook). `dense_layer_stats` / `lcu_layer_stats`
/ `projector_layer_stats` / `extrapolate_total` are matrix-agnostic.

Run as a script: `python resource_estimation.py` (Burgers only).
"""

import time

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import PhaseGate, UnitaryGate

from burgers import (
    Burgers_Carlemann,
    block_encode_matrix,
    compute_inverse_qsvt_angles,
    next_power_of_two,
)
from kdv import KdV_Carlemann
from lcu import build_lcu_block_encoding_gate_circuit, pauli_lcu_terms

BASIS_GATES = ["cx", "u3"]
OPTIMIZATION_LEVEL = 1


def _carleman_matrix():
    """The padded implicit-Euler matrix actually block-encoded in the
    tutorial notebook (N=5, N_T=2, as used throughout)."""
    bc = Burgers_Carlemann(N=5, N_T=2, total_time=0.3, mu=0.01, dt=0.1, u0=0, uN1=0, stencil="method_2")
    A = bc.get_I_m_Adt()
    Dim = A.shape[0]
    padded_dim = next_power_of_two(Dim)
    A_padded = np.eye(padded_dim)
    A_padded[:Dim, :Dim] = A
    return A_padded.T, Dim, padded_dim


def _carleman_matrix_kdv(N=5, N_T=2, total_time=0.3, delta=0.02, dt=0.1, ic="cos"):
    """The padded implicit-Euler matrix for the KdV tutorial notebook.
    delta=0.02 at N=6 sits in the Carleman-convergent window identified by
    `kdv_convergence_study.py` (linear/nonlinear norm ratio ~4)."""
    kdv = KdV_Carlemann(N, N_T, total_time, delta, dt, ic=ic)
    A = kdv.get_I_m_Adt()
    Dim = A.shape[0]
    padded_dim = next_power_of_two(Dim)
    A_padded = np.eye(padded_dim)
    A_padded[:Dim, :Dim] = A
    return A_padded.T, Dim, padded_dim


def _transpiled_stats(qc, basis_gates=BASIS_GATES, optimization_level=OPTIMIZATION_LEVEL):
    t0 = time.time()
    tqc = transpile(qc, basis_gates=basis_gates, optimization_level=optimization_level)
    elapsed = time.time() - t0
    ops = tqc.count_ops()
    two_qubit_gates = sum(count for name, count in ops.items() if name in ("cx", "cz", "ecr", "swap"))
    return {
        "qubits": tqc.num_qubits,
        "gate_count": sum(ops.values()),
        "two_qubit_gates": two_qubit_gates,
        "depth": tqc.depth(),
        "transpile_seconds": elapsed,
        "ops": dict(ops),
    }


def dense_layer_stats(M, n_wires):
    U, norm = block_encode_matrix(M, n_wires)
    qc = QuantumCircuit(n_wires)
    qc.append(UnitaryGate(U, label="U_A"), range(n_wires))
    stats = _transpiled_stats(qc)
    stats["norm"] = norm
    stats["n_wires"] = n_wires
    return stats


def lcu_layer_stats(M, tol=1e-10):
    qc, alpha, m, n_sys, num_terms = build_lcu_block_encoding_gate_circuit(M, tol=tol)
    stats = _transpiled_stats(qc)
    stats["norm"] = alpha
    stats["n_wires"] = m + n_sys
    stats["ancilla_qubits"] = m
    stats["num_pauli_terms"] = num_terms
    return stats


def projector_layer_stats(n_wires, n_ancilla):
    """The other repeated QSVT ingredient: the projector-controlled phase
    shift. It only depends on whether the n_ancilla ancilla qubits are all
    zero (the rest of the register, however large, is untouched), so it is
    realized here as a single (n_ancilla - 1)-controlled phase gate plus a
    global phase -- not as a dense diagonal matrix over the whole register,
    which would defeat the purpose of comparing against a genuinely sparse
    method."""
    phi = 0.3
    qc = QuantumCircuit(n_wires)
    qc.global_phase += -phi
    if n_ancilla == 1:
        qc.append(PhaseGate(2 * phi), [0])
    else:
        gate = PhaseGate(2 * phi).control(n_ancilla - 1, ctrl_state=0, annotated=True)
        qc.append(gate, range(n_ancilla))
    return _transpiled_stats(qc)


def extrapolate_total(layer_stats, projector_stats, n_angles):
    """Estimate full-QSVT-circuit resources from per-layer stats: n_angles
    projector layers and (n_angles - 1) block-encoding layers (alternating
    U_A / U_A^-1, each costing the same as one transpiled U_A layer)."""
    n_layers = n_angles - 1
    return {
        "gate_count": n_layers * layer_stats["gate_count"] + n_angles * projector_stats["gate_count"],
        "two_qubit_gates": n_layers * layer_stats["two_qubit_gates"] + n_angles * projector_stats["two_qubit_gates"],
        "depth": n_layers * layer_stats["depth"] + n_angles * projector_stats["depth"],
        "qubits": layer_stats["qubits"],
    }


def _print_stats(name, stats):
    print(f"  {name}:")
    print(f"    qubits             : {stats['qubits']}")
    print(f"    gate count         : {stats['gate_count']}")
    print(f"    two-qubit (cx) count: {stats['two_qubit_gates']}")
    print(f"    depth              : {stats['depth']}")
    print(f"    transpile time (s) : {stats['transpile_seconds']:.3f}")


def main():
    M, Dim, padded_dim = _carleman_matrix()
    n_wires_dense = int(np.ceil(np.log2(M.shape[0]))) + 1

    labels, coeffs, n_sys = pauli_lcu_terms(M)
    print(f"Carleman system: N=5, N_T=2 -> Dim={Dim}, padded to {padded_dim} ({n_sys} system qubits)")
    print(f"Pauli-LCU decomposition: {len(coeffs)} nonzero terms out of {4**n_sys} possible\n")

    print("Per-layer resource cost of ONE block-encoding application (transpiled to {cx, u3}):")
    dense_stats = dense_layer_stats(M, n_wires_dense)
    _print_stats("Dense block encoding", dense_stats)
    print()
    lcu_stats = lcu_layer_stats(M)
    _print_stats(f"LCU block encoding (m={lcu_stats['ancilla_qubits']} ancilla, L={lcu_stats['num_pauli_terms']} terms)", lcu_stats)

    print("\nProjector-controlled-phase layer (for both methods' respective qubit/ancilla counts):")
    dense_proj = projector_layer_stats(n_wires_dense, n_ancilla=1)
    lcu_proj = projector_layer_stats(lcu_stats["n_wires"], n_ancilla=lcu_stats["ancilla_qubits"])
    _print_stats("Dense-method projector", dense_proj)
    _print_stats("LCU-method projector", lcu_proj)

    kappa = 8
    phi_qsvt, s = compute_inverse_qsvt_angles(kappa, tolerance=1e-5)
    n_angles = len(phi_qsvt)
    print(f"\nExtrapolated full QSVT circuit (kappa={kappa} -> {n_angles} phase angles, "
          f"{n_angles - 1} block-encoding layers):")
    dense_total = extrapolate_total(dense_stats, dense_proj, n_angles)
    lcu_total = extrapolate_total(lcu_stats, lcu_proj, n_angles)
    print(f"  Dense : qubits={dense_total['qubits']:>3}  gates={dense_total['gate_count']:>12,}  "
          f"cx={dense_total['two_qubit_gates']:>12,}  depth={dense_total['depth']:>12,}")
    print(f"  LCU   : qubits={lcu_total['qubits']:>3}  gates={lcu_total['gate_count']:>12,}  "
          f"cx={lcu_total['two_qubit_gates']:>12,}  depth={lcu_total['depth']:>12,}")

    print("\nRatio (LCU / dense) -- how many times more expensive LCU is here:")
    for key in ("gate_count", "two_qubit_gates", "depth"):
        print(f"  {key:16s}: {lcu_total[key] / dense_total[key]:.1f}x")

    print(
        "\nTakeaway: for this specific matrix, the dense block encoding is cheaper in\n"
        "absolute gate count, because its Pauli decomposition is not sparse (358 of\n"
        f"{4**n_sys} possible terms are nonzero, vs. only {int(np.max(np.sum(np.abs(M) > 1e-12, axis=1)))} nonzeros per row in the\n"
        "computational basis -- see the module docstring in lcu.py).\n"
        "LCU's real advantage is asymptotic and structural, not shown by this one data\n"
        "point: the dense encoding's cost is exponential in the number of block-encoded\n"
        "qubits (2**n_wires) *regardless of matrix structure*, whereas an LCU built from\n"
        "a genuinely sparse decomposition would scale with the matrix's sparsity instead."
    )


if __name__ == "__main__":
    main()
