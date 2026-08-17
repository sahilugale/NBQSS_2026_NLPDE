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
   parametrized circuit and step forward in time by minimizing a Hadamard-test-based variational
   consistency cost function, avoiding Carleman's enlarged linear embedding entirely.

## Method 1: Carleman linearization + QSVT

**PDE → finite-difference discretization → quadratic ODE → Carleman linearization → implicit Euler
→ linear system → QSVT.**

After spatial discretization, both PDEs take the quadratic form
$\dot{\mathbf u} = F_1\mathbf u + F_2(\mathbf u\otimes\mathbf u)$ (plus a boundary-forcing term
$F_0$ for the fixed-Dirichlet Burgers construction in `carleman_qsvt/burgers.py`; the periodic KdV
construction in `carleman_qsvt/kdv.py` has none). Carleman linearization introduces the lifted state

$$
\mathbf y=\begin{bmatrix}\mathbf u\\ \mathbf u^{\otimes2}\\ \vdots\\ \mathbf u^{\otimes N_T}\end{bmatrix},
\qquad \dot{\mathbf y}=A\mathbf y+\mathbf b,
$$

and implicit Euler turns each timestep into a linear solve, $(I-\Delta t A)\mathbf y_{n+1} = \mathbf
y_n+\Delta t\,\mathbf b$, approximated on a quantum computer via QSVT applied to a block encoding of
$A$. Two block encodings are implemented and compared: a dense/arbitrary-unitary one, and one built
from the matrix's Pauli decomposition (LCU) — the latter turns out to be the *more* expensive of the
two for this matrix family (`carleman_qsvt/resource_estimation.py` explains why: the Carleman
matrix's Kronecker-shift structure gives a dense Pauli decomposition despite being sparse in the
computational basis).

A classical pre-check (`carleman_qsvt/kdv_convergence_study.py`) was necessary before trusting the
KdV pathway: KdV's dispersion operator is skew-symmetric (non-dissipative), unlike Burgers'
diffusion operator, so the convergence guarantees Carleman linearization normally relies on don't
transfer automatically — the study finds a genuine but narrow convergent window and uses it to
choose the KdV demo's parameters.

Primary reference: A. Setty, *A quantum linear systems pathway for solving differential equations*,
J. Phys. A **59**, 185303 (2026); J.-P. Liu et al., *Efficient quantum algorithm for dissipative
nonlinear differential equations*, PNAS **118**, e2026805118 (2021).

## Method 2: Variational time-propagation

**PDE → finite-difference discretization → Hadamard-test-based variational consistency cost
function → classical optimization, one timestep at a time.**

Instead of an enlarged linear embedding, the field is amplitude-encoded directly into a
parametrized circuit, $\Lambda_t|\Psi(\vec\theta_t)\rangle$, and time propagation is a sequence of
variational consistency steps: $\vec\theta_{t+\tau}$ is found by minimizing a cost function built
from Hadamard-test overlaps between the current and next timestep's states. The general form of
this approach originates with Lubasch, Joo, Moinier, Kiffner, Jaksch, *Variational quantum
algorithms for nonlinear problems*, Phys. Rev. A **101**, 010301 (2020); every ansatz, shift
operator, and Hadamard-test circuit construction in this repository (`variational/pde_core.py`) is
worked out and validated from scratch here, not adapted from any other implementation (see that
module's docstring for the full derivation, including a nontrivial two-register construction needed
for the nonlinear convection term).

This method is the one with a real path to near-term hardware: the Carleman/QSVT pathway's own
resource estimates put it at millions of gates for a toy N=5 problem (simulator-only), whereas the
variational method's circuits are shallow enough to be hardware-relevant, at the cost of needing a
classical optimization loop per timestep instead of a single quantum linear solve.

## Repository structure

```text
.
├── discretization.py              # shared periodic finite-difference operators (D1, D2, D3, F2)
├── carleman_qsvt/                 # Method 1
│   ├── burgers.py                 # generic QSVT toolkit + Burgers_Carlemann (Dirichlet BC)
│   ├── kdv.py                     # KdV_Carlemann (periodic BC, no forcing)
│   ├── lcu.py                     # Pauli-LCU block encoding (generic + Burgers driver)
│   ├── kdv_convergence_study.py   # classical Carleman-convergence check for KdV
│   ├── resource_estimation.py     # dense vs. Pauli-LCU gate/qubit resource comparison
│   ├── Burgers_Carlemann_qiskit.ipynb
│   └── KdV_Carlemann_qiskit.ipynb
├── variational/                   # Method 2
│   ├── pde_core.py                # shared ansatz / shift / Hadamard-test / nonlinear-overlap circuits
│   ├── burgers.py                 # viscous Burgers cost function (diffusion term)
│   ├── kdv.py                     # KdV cost function (dispersion term)
│   ├── fake_hardware.py           # noisy readout via a real fake-backend calibration snapshot
│   ├── Burgers_variational_qiskit.ipynb
│   ├── KdV_variational_qiskit.ipynb
│   ├── Burgers_fake_hardware_qiskit.ipynb
│   └── KdV_fake_hardware_qiskit.ipynb
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
jupyter notebook variational/Burgers_fake_hardware_qiskit.ipynb
jupyter notebook variational/KdV_fake_hardware_qiskit.ipynb
```

## Dependencies

Tested with Python 3.12 and the pinned versions in [`requirements.txt`](requirements.txt):

```text
NumPy, SciPy, Matplotlib, Qiskit, qiskit-aer, qiskit-ibm-runtime, pyqsp, IPython, nbclient, nbformat
```

`qiskit-ibm-runtime` is only used for its `fake_provider` (offline device calibration snapshots
used by `variational/fake_hardware.py`) -- no account or network access needed.

## References

1. A. Setty, *A quantum linear systems pathway for solving differential equations*, J. Phys. A **59**, 185303 (2026).
2. A. Setty, *Block encoding of sparse matrices via coherent permutation*, arXiv:2508.21667 (2025).
3. J.-P. Liu, H. Kolden, H. Krovi, N. Loureiro, K. Trivisa, A. Childs, *Efficient quantum algorithm for dissipative nonlinear differential equations*, PNAS **118**, e2026805118 (2021).
4. M. Lubasch, J. Joo, P. Moinier, M. Kiffner, D. Jaksch, *Variational quantum algorithms for nonlinear problems*, Phys. Rev. A **101**, 010301 (2020).
5. D. Jaksch, P. Givi, A. J. Daley, T. Rung, *Variational quantum algorithms for computational fluid dynamics*, AIAA Journal **61**, 1885 (2023).
6. Niels Bohr Quantum Summer School 2026, *Quantum Simulation of Nonlinear Partial Differential Equations*, Center for Quantum Mathematics, University of Southern Denmark.
