# Quantum Simulation of Nonlinear PDEs

Implementation for the **2026 Niels Bohr Quantum Summer School (NBQSS) Challenge on Quantum Simulation of Nonlinear Partial Differential Equations**.

### Team

- Andrei Poliakov
- Kyro Jeremy Gibling
- Nadav Carmel
- Pak Tik
- Sahil Ugale

This repository explores the solution of the one-dimensional viscous Burgers equation

$$
\frac{\partial u}{\partial t}
+
u\frac{\partial u}{\partial x}
=
\nu\frac{\partial^2u}{\partial x^2}
$$

using **Carleman linearization** followed by a **quantum linear systems approach based on block encoding and Quantum Singular Value Transformation (QSVT)**.

The implementation is primarily inspired by:

> A. Setty, *A quantum linear systems pathway for solving differential equations*, Journal of Physics A: Mathematical and Theoretical **59**, 185303 (2026).

## Method

The computational pipeline is

$$
\text{Burgers PDE}
\rightarrow
\text{finite-difference discretization}
\rightarrow
\text{quadratic ODE system}
\rightarrow
\text{Carleman linearization}
\rightarrow
\text{implicit Euler}
\rightarrow
\text{linear system}
\rightarrow
\text{QSVT}.
$$

After spatial discretization, the Burgers equation is written in the quadratic form

$$
\dot{\mathbf u}
=
F_0
+
F_1\mathbf u
+
F_2(\mathbf u\otimes\mathbf u).
$$

Carleman linearization introduces the lifted state

$$
\mathbf y=
\begin{bmatrix}
\mathbf u\\
\mathbf u^{\otimes2}\\
\vdots\\
\mathbf u^{\otimes N_T}
\end{bmatrix},
$$

giving a truncated linear system

$$
\dot{\mathbf y}=A\mathbf y+\mathbf b.
$$

Using implicit Euler,

$$
(I-\Delta t A)\mathbf y_{n+1}
=
\mathbf y_n+\Delta t\,\mathbf b.
$$

The resulting linear-system inversion is approximated using block encoding and QSVT.

## Repository Structure

```text
.
├── Burgers_Carlemann.ipynb
├── Carlemann.py
├── requirements.txt
├── README.md
└── references/
```

- `Carlemann.py` — finite-difference Burgers solver and Carleman linearization utilities.
- `Burgers_Carlemann.ipynb` — QSVT implementation and comparison with the classical linear solve.
- `references/` — papers and challenge material.

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd NQSS_2026_Challenge
```

Create and activate a virtual environment:

```bash
python3 -m venv nqss_2026
source nqss_2026/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Running

Start Jupyter:

```bash
jupyter notebook
```

and open:

```text
Burgers_Carlemann.ipynb
```

Run the notebook from top to bottom.

The current demonstration uses

$$
N=5,\qquad
N_T=2,\qquad
\nu=0.01,\qquad
\Delta t=0.1,\qquad
T=0.3.
$$

For $N=5$ and $N_T=2$, the truncated Carleman system has dimension

$$
D=N+N^2=30.
$$

## Dependencies

The implementation has been tested with Python 3.12 and the pinned versions in [`requirements.txt`](requirements.txt):

```text
NumPy 2.5.2
SciPy 1.18.0
Matplotlib 3.11.1
PennyLane 0.45.1
PennyLane-Lightning 0.45.0
pyqsp 0.2.0
Jupyter
IPython 9.16.1
```

## References

1. A. Setty, *A quantum linear systems pathway for solving differential equations*, Journal of Physics A: Mathematical and Theoretical **59**, 185303 (2026).

2. Niels Bohr Quantum Summer School 2026, *Quantum Simulation of Nonlinear Partial Differential Equations*, Center for Quantum Mathematics, University of Southern Denmark.

3. J.-P. Liu et al., *Efficient quantum algorithm for dissipative nonlinear differential equations*, PNAS **118**, e2026805118 (2021).