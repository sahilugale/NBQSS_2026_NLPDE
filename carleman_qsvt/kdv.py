"""Carleman linearization of KdV,

    u_t + u u_x + delta * u_xxx = 0,   periodic BC on [0, 1],

implicit-Euler time marching via `periodic_carleman.PeriodicCarleman`;
only PDE-specific data here (`get_Fs`, `get_init_state`). Uses `burgers.py`'s
QSVT toolkit and `lcu.py`'s Pauli-LCU encoding, both PDE-agnostic.

F1 = -delta*D3 is skew-symmetric (non-dissipative), unlike Burgers'
symmetric diffusion -- `kdv_convergence_study.py` found the narrow
Carleman-convergent window this module's delta/N_T are chosen from
(||F1 u0|| / ||F2(u0 kron u0)|| ~ 3-6). Details: see project report.
"""

import sys
import os

import numpy as np

from periodic_carleman import PeriodicCarleman, get_implicit_solver_qsvt_lcu  # noqa: F401

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from discretization import periodic_D3, construct_F2_periodic  # noqa: E402


class KdV_Carlemann(PeriodicCarleman):
    def __init__(self, N, N_T, total_time, delta, dt, ic="cos", dtype=np.float64):
        super().__init__(N, N_T, total_time, dt, dtype=dtype)
        self.DELTA = delta
        self.IC = ic

    def get_init_state(self):
        x, dx = self.get_x_dx()
        if self.IC == "cos":
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
        b = -1.0 / (2 * dx)
        F2 = (b * construct_F2_periodic(self.N)).astype(self.DTYPE)
        return F1, F2
