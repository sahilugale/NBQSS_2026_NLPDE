"""Shared, general-n circuit primitives for the variational PDE pathway --
generalizes `kdv.py`'s n=2-specific ansatz/shift/Hadamard-test/
nonlinear-overlap circuits to arbitrary qubit count n (used by `burgers.py`).
See `kdv.py` for the derivations.

- `ansatz(n, theta)`: n-qubit real-amplitude circuit, full expressivity.
- `shift_gate(n)`: ripple-carry cyclic increment, |m> -> |m+1 mod 2**n>.
- `hadamard_test`: explicit controlled-unitary Hadamard test.
- `nonlinear_overlap`: two-register construction for the trilinear
  convection-term overlap (see kdv.py for why this needs a different circuit
  than a plain Hadamard test).
"""

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit
from qiskit.circuit.library import real_amplitudes
from qiskit.primitives import StatevectorSampler
from qiskit.quantum_info import Statevector


def ansatz(n, theta):
    """n-qubit real-amplitude ansatz (n(n+1) parameters), full expressivity."""
    return real_amplitudes(n, reps=n, entanglement="linear").assign_parameters(theta)


def num_ansatz_params(n):
    return real_amplitudes(n, reps=n, entanglement="linear").num_parameters


def shift_gate(n):
    """Ripple-carry cyclic increment: |m> -> |m+1 mod 2**n>."""
    qc = QuantumCircuit(n)
    for i in range(n - 1, 0, -1):
        qc.mcx(list(range(i)), i)
    qc.x(0)
    return qc


def shift_power(n, power, inverse):
    """`shift_gate(n)` (or its inverse) composed `power` times."""
    base = shift_gate(n).inverse() if inverse else shift_gate(n)
    qc = QuantumCircuit(n)
    for _ in range(power):
        qc = qc.compose(base)
    return qc


def get_state(n, xf):
    """Decode a parameter vector xf = [lambda, *theta] into the length-2**n
    classical field it encodes."""
    return np.real(Statevector(ansatz(n, xf[1:])).data) * xf[0]


def get_expval_ideal(circuit, anc=0, postselect=None):
    """Re<0|V|0> from the ancilla (qubit `anc`), optionally conditioned on a
    set of `postselect` qubits all reading 0."""
    probs = Statevector(circuit).probabilities_dict()
    p0 = p1 = 0.0
    for bitstring, p in probs.items():
        bits = bitstring[::-1]
        if postselect is not None and any(bits[q] != "0" for q in postselect):
            continue
        if bits[anc] == "0":
            p0 += p
        else:
            p1 += p
    return p0 - p1


def get_expval_shots(circuit, shots, anc=0, postselect=None, sampler=None):
    meas_qc = circuit.copy()
    meas_qubits = [anc] + (list(postselect) if postselect else [])
    cr = ClassicalRegister(len(meas_qubits), name="meas")
    meas_qc.add_register(cr)
    meas_qc.measure(meas_qubits, cr)
    sampler = sampler or StatevectorSampler()
    job = sampler.run([meas_qc], shots=shots)
    counts = job.result()[0].data.meas.get_counts()
    p0 = p1 = 0.0
    for bitstring, count in counts.items():
        bits = bitstring[::-1]
        if postselect and any(b != "0" for b in bits[1:]):
            continue
        if bits[0] == "0":
            p0 += count
        else:
            p1 += count
    return (p0 - p1) / shots


def hadamard_test(n, theta_old, theta_new, shift_qc, expval_fn, expval_kwargs):
    """Standard explicit-controlled-unitary Hadamard test for
    Re<theta_new| shift_qc |theta_old>, shift_qc=None for the bare overlap."""
    qc = QuantumCircuit(n + 1)
    qc.h(0)
    qc.append(ansatz(n, theta_old).to_gate().control(1), range(n + 1))
    if shift_qc is not None:
        qc.append(shift_qc.to_gate().control(1), range(n + 1))
    qc.append(ansatz(n, theta_new).inverse().to_gate().control(1), range(n + 1))
    qc.h(0)
    return expval_fn(qc, anc=0, **expval_kwargs)


def nonlinear_overlap(n, theta_old, theta_new, shift_power_val, shift_inverse, expval_fn, expval_kwargs):
    """sum_l psi_new*_l psi_old_l (S^{+-shift_power_val} psi_old)_l via the
    two-register construction derived in `kdv.py`'s docstring:
    prepare Ra, Rb both in state psi_old (controlled by the Hadamard
    ancilla), shift Rb only, correlate Ra/Rb into a check register, and
    uncompute Rb back to |0> in the matched subspace via CX(Ra -> Rb)."""
    anc = 0
    Ra = list(range(1, 1 + n))
    Rb = list(range(1 + n, 1 + 2 * n))
    chk = list(range(1 + 2 * n, 1 + 3 * n))
    qc = QuantumCircuit(1 + 3 * n)
    qc.h(anc)
    prep_old_gate = ansatz(n, theta_old).to_gate().control(1)
    qc.append(prep_old_gate, [anc] + Ra)
    qc.append(prep_old_gate, [anc] + Rb)
    qc.append(shift_power(n, shift_power_val, shift_inverse).to_gate().control(1), [anc] + Rb)
    for j in range(n):
        qc.cx(Ra[j], chk[j])
        qc.cx(Rb[j], chk[j])
        qc.cx(Ra[j], Rb[j])  # uncompute Rb -> 0 in the matched (chk=0) subspace
    qc.append(ansatz(n, theta_new).inverse().to_gate().control(1), [anc] + Ra)
    qc.h(anc)
    return expval_fn(qc, anc=anc, postselect=chk, **expval_kwargs)
