"""Variational quantum time-propagation for KdV,

    u_t + u u_x + delta * u_xxx = 0,   periodic BC.

Amplitude-encodes the field into a parametrized circuit and steps forward
in time by minimizing a Hadamard-test-based cost function, instead of
Carleman linearization + QSVT (`carleman_qsvt/`). General approach from
Lubasch et al., Phys. Rev. A 101, 010301 (2020); circuits below (ansatz,
shift operator, Hadamard tests) are derived from scratch here, not adapted
from any other implementation. Full derivation: see project report.

- `ansatz`: standard 3-param real-amplitude circuit, full expressivity.
- `shift_gate`: ancilla-free cyclic shift |m> -> |m+1 mod 4>.
- `kdv_overlap`: constant + dispersion + nonlinear terms. The nonlinear
  (convection) term needs a two-register construction (`_nonlinear_overlap`)
  since it's a trilinear overlap, not a plain Hadamard test.
"""

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit
from qiskit.primitives import StatevectorSampler
from qiskit.quantum_info import Statevector

N_QUBITS = 2
N_GRID = 2 ** N_QUBITS


# =============================================================================
# Ansatz and shift circuits
# =============================================================================


def ansatz(theta):
    """Standard 3-parameter real-amplitude ansatz on 2 qubits. Reaches the
    full real 4-dimensional unit sphere (see module docstring)."""
    qc = QuantumCircuit(2)
    qc.ry(theta[0], 0)
    qc.ry(theta[1], 1)
    qc.cx(0, 1)
    qc.ry(theta[2], 1)
    return qc


def shift_gate():
    """Minimal, ancilla-free cyclic shift-by-one on 2 qubits: |m> -> |m+1
    mod 4> (see module docstring)."""
    qc = QuantumCircuit(2)
    qc.cx(0, 1)
    qc.x(0)
    return qc


def _shift_power(power, inverse):
    """`shift_gate()` (or its inverse) composed `power` times."""
    base = shift_gate().inverse() if inverse else shift_gate()
    qc = QuantumCircuit(2)
    for _ in range(power):
        qc = qc.compose(base)
    return qc


def get_state(xf):
    """Decode a parameter vector xf = [lambda, theta0, theta1, theta2] into
    the length-4 classical field it encodes."""
    return np.real(Statevector(ansatz(xf[1:])).data) * xf[0]


# =============================================================================
# Expectation-value readout (ideal statevector, or shots via StatevectorSampler)
# =============================================================================


def get_expval_ideal(circuit, anc=0, postselect=None):
    """Re<0|V|0> from the ancilla (qubit `anc`), optionally conditioned on a
    set of `postselect` qubits all reading 0 (needed for the nonlinear-term
    circuit's check register; None for the plain overlap/dispersion
    circuits)."""
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
        bits = bitstring[::-1]  # bits[0] = anc, bits[1:] = postselect qubits, in meas_qubits order
        if postselect and any(b != "0" for b in bits[1:]):
            continue
        if bits[0] == "0":
            p0 += count
        else:
            p1 += count
    return (p0 - p1) / shots


# =============================================================================
# Cost function
# =============================================================================


def _hadamard_test(theta_old, theta_new, shift_qc, expval_fn, expval_kwargs):
    """Standard explicit-controlled-unitary Hadamard test for
    Re<theta_new| shift_qc |theta_old>, shift_qc=None for the bare overlap."""
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.append(ansatz(theta_old).to_gate().control(1), [0, 1, 2])
    if shift_qc is not None:
        qc.append(shift_qc.to_gate().control(1), [0, 1, 2])
    qc.append(ansatz(theta_new).inverse().to_gate().control(1), [0, 1, 2])
    qc.h(0)
    return expval_fn(qc, anc=0, **expval_kwargs)


def _nonlinear_overlap(theta_old, theta_new, shift_power, shift_inverse, expval_fn, expval_kwargs):
    """sum_l psi_new*_l psi_old_l (S^{+-shift_power} psi_old)_l via the
    two-register construction derived in the module docstring."""
    anc, Ra, Rb, chk = 0, [1, 2], [3, 4], [5, 6]
    qc = QuantumCircuit(7)
    qc.h(anc)
    prep_old_gate = ansatz(theta_old).to_gate().control(1)
    qc.append(prep_old_gate, [anc] + Ra)
    qc.append(prep_old_gate, [anc] + Rb)
    shift_qc = _shift_power(shift_power, shift_inverse)
    qc.append(shift_qc.to_gate().control(1), [anc] + Rb)
    for j in range(2):
        qc.cx(Ra[j], chk[j])
        qc.cx(Rb[j], chk[j])
        qc.cx(Ra[j], Rb[j])  # uncompute Rb -> 0 in the matched (chk=0) subspace
    qc.append(ansatz(theta_new).inverse().to_gate().control(1), [anc] + Ra)
    qc.h(anc)
    return expval_fn(qc, anc=anc, postselect=chk, **expval_kwargs)


def kdv_overlap(theta_old, theta_new, dt, dx, delta, expval_fn, **expval_kwargs):
    """Overlap = (constant term) + (dispersion term) + (nonlinear term) for a
    single explicit-Euler KdV timestep from theta_old (amplitude
    theta_old[0]) to theta_new."""
    amp_old = theta_old[0]

    # constant term: bare overlap (D3's diagonal is 0, so no prefactor correction)
    const_term = np.conj(amp_old) * _hadamard_test(theta_old[1:], theta_new[1:], None, expval_fn, expval_kwargs)

    # dispersion term: four shift contributions (S, S^-1, S^2, S^-2), linear in amp_old
    coeff_single_shift = delta * dt / dx ** 3
    coeff_double_shift = delta * dt / (2 * dx ** 3)

    def shifted(power, inverse):
        return _hadamard_test(theta_old[1:], theta_new[1:], _shift_power(power, inverse), expval_fn, expval_kwargs)

    fwd1, bwd1 = shifted(1, True), shifted(1, False)
    fwd2, bwd2 = shifted(2, True), shifted(2, False)
    dispersion_term = amp_old * (coeff_single_shift * (fwd1 - bwd1) - coeff_double_shift * (fwd2 - bwd2))

    # nonlinear term: convection "-f*f_x" (same as Burgers), quadratic in amp_old
    convection_coeff = -1.0 / (2 * dx)
    overlap_fwd = _nonlinear_overlap(theta_old[1:], theta_new[1:], 1, True, expval_fn, expval_kwargs)
    overlap_bwd = _nonlinear_overlap(theta_old[1:], theta_new[1:], 1, False, expval_fn, expval_kwargs)
    nonlinear_term = dt * convection_coeff * amp_old ** 2 * (overlap_fwd - overlap_bwd)

    return const_term + dispersion_term + nonlinear_term


def kdv_cost(theta_new, theta_old, dt, dx, delta, expval_fn, **expval_kwargs):
    amp_new = theta_new[0]
    overlap = kdv_overlap(theta_old, theta_new, dt, dx, delta, expval_fn, **expval_kwargs)
    return np.abs(amp_new) ** 2 - 2 * np.real(np.conj(amp_new) * overlap), overlap
