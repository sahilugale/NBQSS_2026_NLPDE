"""Noisy readout of optimized variational circuits on a FakeSherbrooke
calibration snapshot (qiskit-aer), via shot-based sampling -- BackendSamplerV2,
not Estimator or density-matrix simulation, since that's what a real QPU gives you.

ansatz_fn(theta) -> QuantumCircuit is passed in since Burgers and KdV use
different ansatz constructions.
"""

import numpy as np
from qiskit import transpile, QuantumCircuit, ClassicalRegister
from qiskit.primitives import BackendSamplerV2
from qiskit_ibm_runtime.fake_provider import FakeSherbrooke
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel


def make_fake_backend(n_qubits):
    backend = FakeSherbrooke()
    noise_model = NoiseModel.from_backend(backend)
    sim = AerSimulator(noise_model=noise_model)
    reduced_cm = backend.coupling_map.reduce(list(range(n_qubits)))
    return noise_model, sim, reduced_cm


def _amplitude_circuit(n, theta, i, ansatz_fn):
    """Hadamard test for Re<i|ansatz(theta)>."""
    qc = QuantumCircuit(n + 1)
    qc.h(0)
    qc.append(ansatz_fn(theta).to_gate().control(1), range(n + 1))
    bits = format(i, f"0{n}b")[::-1]
    for q, b in enumerate(bits):
        if b == "1":
            qc.cx(0, 1 + q)
    qc.h(0)
    qc.add_register(ClassicalRegister(1, "anc"))
    qc.measure(0, 0)
    return qc


def noisy_decoded_state(ansatz_fn, theta_full, noise_model, sim, coupling_map, n=None, shots=2000):
    amp = theta_full[0]
    theta = theta_full[1:]
    n = n if n is not None else int(np.log2(len(theta_full) - 1))
    N = 2 ** n
    sampler = BackendSamplerV2(backend=sim)

    values = []
    for i in range(N):
        qc = _amplitude_circuit(n, theta, i, ansatz_fn)
        tqc = transpile(qc, basis_gates=noise_model.basis_gates,
                         coupling_map=coupling_map, optimization_level=0)
        counts = sampler.run([tqc], shots=shots).result()[0].data.anc.get_counts()
        p0, p1 = counts.get("0", 0), counts.get("1", 0)
        values.append((p0 - p1) / (p0 + p1))
    return np.array(values) * amp
