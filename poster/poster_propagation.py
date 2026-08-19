"""Reproduce the variational Burgers propagation and dump the three curves.

Same pipeline as variational/Burgers_variational_qiskit.ipynb (same seeds, same
parameters, same FakeSherbrooke noise model), run headless so the poster figure
can be drawn from the real arrays rather than from a shrunken manuscript raster.

    python3 poster_propagation.py     # -> propagation_data.json
"""

import json
import os
import sys

import numpy as np
import scipy as sp
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Operator

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "variational"))

import pde_core as pc  # noqa: E402
from discretization import periodic_D2, construct_F2_periodic_skew  # noqa: E402

# ------------------------------------------------ setup (notebook cell 3)
n = 3
N = 2 ** n
x = np.linspace(0, 1, N, endpoint=False)
dx = x[1] - x[0]
nu = 0.01
dt = 0.1
n_steps = 3

u0 = np.sin(2 * np.pi * x)
amp0 = np.linalg.norm(u0)
u0n = u0 / amp0

ansatz = pc.build_ansatz_template(n)
P = ansatz.num_parameters

shift_fwd = pc.shift_power(n, 1, inverse=True)
shift_bwd = pc.shift_power(n, 1, inverse=False)
S1 = np.real(Operator(shift_fwd).data)
S1inv = np.real(Operator(shift_bwd).data)
identity_qc = QuantumCircuit(n)

lin_terms = [
    ("S1", shift_fwd, S1, nu / dx ** 2),
    ("S1inv", shift_bwd, S1inv, nu / dx ** 2),
    ("id2", identity_qc, np.eye(N), -2 * nu / dx ** 2),
]

F1 = nu * periodic_D2(N, dx)
F2 = 1 / dx * construct_F2_periodic_skew(N)


def classical_rhs(u):
    return F1 @ u + F2 @ np.kron(u, u)


# ------------------------------------- initial encoding (notebook cell 5)
def init_loading(theta, target):
    return np.sum((pc.psi_of(ansatz, theta) - target) ** 2)


rng = np.random.default_rng(1)
best = None
for _ in range(10):
    guess = rng.random(P) * 2 * np.pi
    res = sp.optimize.minimize(init_loading, guess, args=(u0n,), method="BFGS")
    if best is None or res.fun < best.fun:
        best = res
theta, amp = best.x, amp0
print(f"encoding fit residual: {best.fun:.2e}", flush=True)

# ---------------------------------------- propagation (notebook cell 7)
classical_states = [u0.copy()]
quantum_states = [amp * pc.psi_of(ansatz, theta)]
theta_history, amp_history = [theta.copy()], [amp]
u_classical = u0.copy()

for step in range(n_steps):
    u_classical = u_classical + dt * classical_rhs(u_classical)
    theta, amp = pc.natural_gradient_timestep(
        ansatz, theta, amp, dt, lin_terms, shift_fwd, shift_bwd, n_iter=150)
    u_quantum = amp * pc.psi_of(ansatz, theta)
    rel = np.linalg.norm(u_quantum - u_classical) / np.linalg.norm(u_classical)
    print(f"step {step+1}/{n_steps}: rel L2 = {rel:.2e}", flush=True)
    classical_states.append(u_classical.copy())
    quantum_states.append(u_quantum.copy())
    theta_history.append(theta.copy())
    amp_history.append(amp)

# ------------------------------------ device-noise readout (cell 9)
from qiskit.primitives import BackendSamplerV2                      # noqa: E402
from qiskit_ibm_runtime.fake_provider import FakeSherbrooke          # noqa: E402
from qiskit_aer import AerSimulator                                  # noqa: E402
from qiskit_aer.noise import NoiseModel                              # noqa: E402

SHOTS = 4000
fake_backend = FakeSherbrooke()
noise_model = NoiseModel.from_backend(fake_backend)
sim = AerSimulator(method="statevector", noise_model=noise_model)
coupling_map = fake_backend.coupling_map.reduce(list(range(n)))
sampler = BackendSamplerV2(backend=sim)


def noisy_decoded_state(theta_t, amp_t, shots=SHOTS):
    qc = ansatz.assign_parameters(theta_t)
    qc_meas = qc.copy()
    qc_meas.measure_all()
    tqc = transpile(qc_meas, basis_gates=noise_model.basis_gates,
                    coupling_map=coupling_map, optimization_level=3)
    counts = sampler.run([tqc], shots=shots).result()[0].data.meas.get_counts()
    probs = np.zeros(N)
    for bits, c in counts.items():
        probs[int(bits, 2)] = c / shots
    signs = np.sign(pc.psi_of(ansatz, theta_t))
    return amp_t * signs * np.sqrt(probs)


fake_states = [noisy_decoded_state(th, a) for th, a in zip(theta_history, amp_history)]
print("noisy readout done", flush=True)

out = {
    "x": x.tolist(),
    "dt": dt, "nu": nu, "n": n, "shots": SHOTS, "backend": "fake_sherbrooke",
    "classical": np.array(classical_states).tolist(),
    "quantum": np.array(quantum_states).tolist(),
    "noisy": np.array(fake_states).tolist(),
}
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "propagation_data.json")
json.dump(out, open(p, "w"), indent=1)
print("wrote", p, flush=True)
