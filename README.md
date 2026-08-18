# Quantum Simulation of Nonlinear PDEs

Implementation for the **2026 Niels Bohr Quantum Summer School (NBQSS) Challenge on Quantum Simulation of Nonlinear Partial Differential Equations**.

### Team

- Andrei Poliakov
- Kyro Jeremy Gibling
- Nadav Carmel
- Pak Tik
- Sahil Ugale

This repository solves two nonlinear PDEs — the viscous Burgers equation and the Korteweg-de Vries
(KdV) equation — with periodic boundary conditions, using **two independent quantum algorithms**:

$$
\partial_t u + u\,\partial_x u = \nu\,\partial_{xx} u \qquad\text{(Burgers)}, \qquad
\partial_t u + u\,\partial_x u + \delta\,\partial_{xxx} u = 0 \qquad\text{(KdV)}.
$$

1. **Carleman linearization + QSVT** (`carleman_qsvt/`) — lift the discretized quadratic ODE into a
   truncated linear system, solve it with a QSVT-based quantum linear solver, using two different
   block encodings (dense/arbitrary-unitary, and Pauli-LCU).
2. **Variational time-propagation** (`variational/`) — amplitude-encode the field directly into a
   parametrized circuit and step forward in time via natural-gradient descent toward each timestep's
   forward-Euler target, avoiding Carleman's enlarged linear embedding entirely.

## Method 1: Carleman linearization + QSVT

**PDE → finite-difference discretization → quadratic ODE → Carleman linearization →
Crank-Nicolson → linear system → QSVT.**

After spatial discretization, both PDEs take the quadratic form
$\dot{\mathbf u} = F_1\mathbf u + F_2(\mathbf u\otimes\mathbf u)$, periodic BC as required by the
challenge (`carleman_qsvt/periodic_burgers.py`, `carleman_qsvt/kdv.py`, both built on the shared
`periodic_carleman.py` base, which also hosts `qsvt_toolkit.py`'s PDE-agnostic QSVT block-encoding
toolkit). Carleman linearization introduces the lifted state

$$
\mathbf y=\begin{bmatrix}\mathbf u\\ \mathbf u^{\otimes2}\\ \vdots\\ \mathbf u^{\otimes N_T}\end{bmatrix},
\qquad \dot{\mathbf y}=A\mathbf y+\mathbf b,
$$

and each timestep is a linear solve, approximated on a quantum computer via QSVT applied to a block
encoding of $A$ -- time-marched with Crank-Nicolson (trapezoidal rule),
$(I-\frac{\Delta t}{2}A)\mathbf y_{n+1} = (I+\frac{\Delta t}{2}A)\mathbf y_n$, not implicit Euler:
same block-encoded matrix, but $O(\Delta t^2)$ local error instead of $O(\Delta t)$ -- checked
classically, needs ~20x fewer timesteps for the same accuracy (motivated by Costa, Schleich,
Morales & Berry, npj Quantum Information 11:141 (2025)). Two block encodings are implemented and
compared: a dense/arbitrary-unitary one, and one built
from the matrix's Pauli decomposition (LCU) — the latter turns out to be the *more* expensive of the
two for this matrix family (`carleman_qsvt/resource_estimation.py` explains why: the Carleman
matrix's Kronecker-shift structure gives a dense Pauli decomposition despite being sparse in the
computational basis).

KdV's dispersion operator is skew-symmetric (non-dissipative), unlike Burgers' diffusion operator,
so the convergence guarantees Carleman linearization normally relies on don't transfer
automatically. Checked directly in the notebook: truncation order $N_T$ isn't what limits accuracy
here (N_T=2 vs. 3 give near-identical RMSE) -- dispersion stiffness ($\delta/dx^3$) at fixed $dt$
is, which is why $\delta$ is chosen fairly small.

**Satisfying the challenge's Section 3 norm bounds.** The plain central-difference discretization of
the convection term doesn't conserve the semi-discrete L2 norm (`u^T F2(u kron u) != 0`), so a naive
KdV solution's `||u(t)||_2` drifted ~11% even though the PDE conserves it exactly. Fixed with the
standard skew-symmetric ("conservative") form of the term
(`discretization.construct_F2_periodic_skew`, verified to `u^T F2(u kron u) = 0` at ~1e-16),
used by both Carleman classes' `get_Fs()`. Now `||u(t)||_2 = ||u0||_2` to ~1e-10 for KdV and
`||u(t)||_2` is monotonically non-increasing for Burgers, matching the challenge exactly.

Primary reference: A. Setty, *A quantum linear systems pathway for solving differential equations*,
J. Phys. A **59**, 185303 (2026); J.-P. Liu et al., *Efficient quantum algorithm for dissipative
nonlinear differential equations*, PNAS **118**, e2026805118 (2021).

## Method 2: Variational time-propagation

**PDE → finite-difference discretization → forward-Euler target each timestep → natural-gradient
descent on a parametrized circuit, one timestep at a time.**

Instead of an enlarged linear embedding, the field is amplitude-encoded directly into a
parametrized circuit, $\mathrm{amp}_t\,|\psi(\vec\theta_t)\rangle$. Each timestep minimizes
$\|\mathrm{amp}\cdot\psi(\vec\theta) - \mathbf u_{\mathrm{target}}\|^2$
($\mathbf u_{\mathrm{target}} = \mathbf u_{\mathrm{old}} + \Delta t\,F(\mathbf u_{\mathrm{old}})$, the
forward-Euler target) via natural-gradient descent with a backtracking line search. Every quantity
needed — the Fubini-Study metric $M_{kl}$ and the gradient of the cost — is measured with a **single
Pauli-generator insertion** at one specific gate, or a compute-uncompute circuit, rather than
controlling the whole ansatz as a Hadamard test would require. The general approach follows the
McLachlan variational principle (McLachlan, *Mol. Phys.* **8**, 39 (1964); quantum-simulation
formulation: Li & Benjamin, *Phys. Rev. X* **7**, 021050 (2017); Yuan et al., *Quantum* **3**, 191
(2019)) combined with the standard parameter-shift rule (Mitarai, Negoro, Kitagawa, Fujii, *Phys.
Rev. A* **98**, 032309 (2018)); every circuit construction in this repository
(`variational/pde_core.py`) is worked out and verified from scratch against brute-force linear
algebra, not adapted from any other implementation.

This method has a real path to near-term hardware: the Carleman/QSVT pathway's own resource
estimates put it at millions of gates for a toy N=5 problem (simulator-only), whereas every circuit
here is within a few times the depth of the shallowest possible design for this class of problem
(tens to ~150 gates, verified on real device connectivity via `FakeSherbrooke` in each notebook's
final section) — at the cost of needing many (cheap) circuit executions per timestep rather than a
single expensive one.

## Repository structure

```text
.
├── discretization.py              # shared periodic finite-difference operators (D1, D2, D3, F2)
├── plot_style.py                  # shared matplotlib style (LaTeX-like fonts, validated palette)
├── carleman_qsvt/                 # Method 1
│   ├── qsvt_toolkit.py            # QSVT toolkit (block encoding, phase angles) -- PDE-agnostic
│   ├── periodic_burgers.py        # PeriodicBurgers_Carlemann (periodic BC, used by the notebook)
│   ├── periodic_carleman.py       # shared periodic Carleman base (block assembly, time-marching)
│   ├── kdv.py                     # KdV_Carlemann (periodic BC, no forcing)
│   ├── lcu.py                     # Pauli-LCU block encoding
│   ├── resource_estimation.py     # dense vs. Pauli-LCU gate/qubit resource comparison
│   ├── Burgers_Carlemann_qiskit.ipynb
│   └── KdV_Carlemann_qiskit.ipynb
├── variational/                   # Method 2
│   ├── pde_core.py                # ansatz, metric, and cross-term circuits; natural_gradient_timestep
│   ├── Burgers_variational_qiskit.ipynb   # setup, time-propagation, results, resource estimates
│   └── KdV_variational_qiskit.ipynb       # setup, time-propagation, results, resource estimates
├── scaling_analysis/              # companion scaling-limitations study (Nadav Carmel)
│   └── qlsp_burgers.tex/.pdf, scaling.py, kappa.py, verify.py, figs.py
├── references/                    # challenge PDF and the original PennyLane prototype
├── requirements.txt
└── README.md
```

## Installation

```bash
git clone <repository-url>
cd NQSS_2026_Challenge
python3 -m venv nqss_2026
source nqss_2026/bin/activate
pip install -r requirements.txt
```

## Running

Each notebook is self-contained within its own folder (`carleman_qsvt/` or `variational/`) — open
Jupyter from that folder (or from the repo root and navigate in) and run top to bottom:

```bash
jupyter notebook carleman_qsvt/Burgers_Carlemann_qiskit.ipynb
jupyter notebook carleman_qsvt/KdV_Carlemann_qiskit.ipynb
jupyter notebook variational/Burgers_variational_qiskit.ipynb
jupyter notebook variational/KdV_variational_qiskit.ipynb
```

## Dependencies

Tested with Python 3.12 and the pinned versions in [`requirements.txt`](requirements.txt):

```text
NumPy, SciPy, Matplotlib, Qiskit, qiskit-aer, qiskit-ibm-runtime, pyqsp, IPython, nbclient, nbformat
```

`qiskit-ibm-runtime` is only used for its `fake_provider` (offline device calibration snapshots,
used for the resource estimates in each variational notebook's final section) -- no account or
network access needed.

## References

1. A. Setty, *A quantum linear systems pathway for solving differential equations*, J. Phys. A **59**, 185303 (2026).
2. A. Setty, *Block encoding of sparse matrices via coherent permutation*, arXiv:2508.21667 (2025).
3. J.-P. Liu, H. Kolden, H. Krovi, N. Loureiro, K. Trivisa, A. Childs, *Efficient quantum algorithm for dissipative nonlinear differential equations*, PNAS **118**, e2026805118 (2021).
4. A. C. McLachlan, *A variational solution of the time-dependent Schrodinger equation*, Mol. Phys. **8**, 39 (1964).
5. X. Yuan, S. Endo, Q. Zhao, Y. Li, S. Benjamin, *Theory of variational quantum simulation*, Quantum **3**, 191 (2019).
6. Y. Li, S. C. Benjamin, *Efficient variational quantum simulator incorporating active error minimization*, Phys. Rev. X **7**, 021050 (2017).
7. K. Mitarai, M. Negoro, M. Kitagawa, K. Fujii, *Quantum circuit learning*, Phys. Rev. A **98**, 032309 (2018).
8. Niels Bohr Quantum Summer School 2026, *Quantum Simulation of Nonlinear Partial Differential Equations*, Center for Quantum Mathematics, University of Southern Denmark.
