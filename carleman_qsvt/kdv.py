"""Carleman linearization of KdV,

    u_t + u u_x + delta * u_xxx = 0,   periodic BC on [0, 1],

Crank-Nicolson time marching via `periodic_carleman.PeriodicCarleman`;
only PDE-specific data here (`get_Fs`, `get_init_state`). Uses
`qsvt_toolkit.py` and `lcu.py`'s Pauli-LCU encoding, both PDE-agnostic.

F1 = -delta*D3 is skew-symmetric (non-dissipative), unlike Burgers'
symmetric diffusion. F2 is `construct_F2_periodic_skew` (not the plain
central-difference form): u^T F2(u kron u) = 0 identically, which is what
makes the exact-ODE reference satisfy the challenge's ||u(t)||_2=||u0||_2
bound instead of drifting. N_T=2 was checked sufficient (N_T=3 gives near-
identical RMSE); what actually limits accuracy at fixed dt is dispersion
stiffness (~delta/dx^3), which is why delta is kept fairly small.
"""

import sys
import os

import numpy as np

from periodic_carleman import PeriodicCarleman, get_implicit_solver_qsvt_lcu  # noqa: F401

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from discretization import periodic_D3, construct_F2_periodic_skew  # noqa: E402


class KdV_Carlemann(PeriodicCarleman):
    def __init__(self, N, N_T, total_time, delta, dt, ic="cos", dtype=np.float64):
        super().__init__(N, N_T, total_time, dt, dtype=dtype)
        self.DELTA = delta
        self.IC = ic

    def get_init_state(self):
        x, dx = self.get_x_dx()
        if isinstance(self.IC, np.ndarray):
            return self.IC.astype(self.DTYPE)
        elif self.IC == "cos":
            return np.cos(4 * np.pi * x).astype(self.DTYPE)
        elif self.IC == "cos2":
            # cos(4*pi*x) has a degenerate (zero) nonlinear term at some N; use this instead
            return np.cos(2 * np.pi * x).astype(self.DTYPE)
        elif self.IC == "soliton":
            return (1.0 / np.cosh(40 * (x - 0.5))) ** 2
        raise ValueError(f"Unknown initial condition {self.IC!r}")

    def get_Fs(self):
        x, dx = self.get_x_dx()
        D3 = periodic_D3(self.N, dx)
        F1 = (-self.DELTA * D3).astype(self.DTYPE)
        # skew-symmetric convection (u^T F2(u kron u) = 0 identically) -- needed
        # for the challenge's exact ||u(t)||_2 = ||u0||_2 bound: D3 alone is
        # already skew-symmetric, but the plain central-difference F2 isn't,
        # so a naive discretization's L2 norm drifts even though the PDE conserves it
        F2 = ((1.0 / dx) * construct_F2_periodic_skew(self.N)).astype(self.DTYPE)
        return F1, F2
