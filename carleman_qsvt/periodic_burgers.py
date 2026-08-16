"""Carleman linearization of viscous Burgers with PERIODIC BC,

    u_t + u u_x = nu * u_xx,   periodic BC on [0, 1],

on the same `periodic_carleman.PeriodicCarleman` base as `kdv.py`. Used by
`comparison/method_comparison.ipynb`: the main Burgers demo
(`burgers.py`'s `Burgers_Carlemann`) uses fixed-Dirichlet BC instead, so a
periodic version is needed for a same-footing comparison against the other
(all periodic) pathways.
"""

import sys
import os

import numpy as np

from periodic_carleman import PeriodicCarleman, get_implicit_solver_qsvt_lcu  # noqa: F401

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from discretization import periodic_D2, construct_F2_periodic  # noqa: E402


class PeriodicBurgers_Carlemann(PeriodicCarleman):
    def __init__(self, N, N_T, total_time, nu, dt, ic="sin", dtype=np.float64):
        super().__init__(N, N_T, total_time, dt, dtype=dtype)
        self.NU = nu
        self.IC = ic

    def get_init_state(self):
        x, dx = self.get_x_dx()
        if self.IC == "sin":
            return np.sin(2 * np.pi * x).astype(self.DTYPE)
        raise ValueError(f"Unknown initial condition {self.IC!r}")

    def get_Fs(self):
        x, dx = self.get_x_dx()
        D2 = periodic_D2(self.N, dx)
        F1 = (self.NU * D2).astype(self.DTYPE)
        b = -1.0 / (2 * dx)
        F2 = (b * construct_F2_periodic(self.N)).astype(self.DTYPE)
        return F1, F2
