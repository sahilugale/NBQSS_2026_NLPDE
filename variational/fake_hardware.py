"""Noisy readout of already-optimized variational circuits on a real fake
backend (FakeSherbrooke calibration snapshot), via qiskit-aer.

Transpiling straight to `backend=` embeds the circuit in its full qubit
count (127 here), which blows up density-matrix simulation -- so we
transpile against a coupling map reduced to just the qubits we need
(reduce() keeps their original indices, so the noise model's per-qubit
error rates still apply correctly).

`ansatz_fn(theta) -> QuantumCircuit` is passed in by the caller rather than
imported here, since Burgers and KdV use different ansatz constructions
(pde_core's general-n one vs. kdv.py's fixed n=2 one).
"""

import numpy as np
from qiskit import transpile
from qiskit_ibm_runtime.fake_provider import FakeSherbrooke
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit.quantum_info import Statevector, state_fidelity


def make_fake_backend(n_qubits):
    backend = FakeSherbrooke()
    noise_model = NoiseModel.from_backend(backend)
    sim = AerSimulator(noise_model=noise_model)
    reduced_cm = backend.coupling_map.reduce(list(range(n_qubits)))
    return noise_model, sim, reduced_cm


def noisy_density_matrix(ansatz_fn, theta, noise_model, sim, coupling_map):
    qc = transpile(ansatz_fn(theta), basis_gates=noise_model.basis_gates,
                    coupling_map=coupling_map, optimization_level=1)
    qc.save_density_matrix()
    result = sim.run(qc).result()
    return result.data(0)["density_matrix"]


def noisy_state_fidelity(ansatz_fn, theta, noise_model, sim, coupling_map):
    ideal_sv = Statevector(ansatz_fn(theta))
    rho = noisy_density_matrix(ansatz_fn, theta, noise_model, sim, coupling_map)
    return state_fidelity(ideal_sv, rho)


def noisy_decoded_state(ansatz_fn, theta_full, noise_model, sim, coupling_map):
    amp = theta_full[0]
    ideal_sv = np.real(Statevector(ansatz_fn(theta_full[1:])).data)
    rho = noisy_density_matrix(ansatz_fn, theta_full[1:], noise_model, sim, coupling_map)
    evals, evecs = np.linalg.eigh(rho.data)
    v = np.real(evecs[:, -1])
    if np.dot(v, ideal_sv) < 0:
        v = -v
    return v * amp
