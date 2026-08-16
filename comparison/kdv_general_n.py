"""General-n KdV variational cost function, for `method_comparison.ipynb`
only. `variational/kdv.py` is hardcoded to n=2; this reuses its
`kdv_overlap` coefficient derivation but built on `pde_core.py`'s
general-n primitives, so it can run at N=8 (n=3) to match the Burgers side
of the comparison. Validated against a direct classical matrix computation
before use (see the comparison notebook's validation cell).
"""

import sys
import os

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "variational"))
from pde_core import hadamard_test, nonlinear_overlap, shift_power  # noqa: E402


def kdv_overlap_general(n, theta_old, theta_new, dt, dx, delta, expval_fn, **expval_kwargs):
    amp_old = theta_old[0]

    const_term = np.conj(amp_old) * hadamard_test(n, theta_old[1:], theta_new[1:], None, expval_fn, expval_kwargs)

    coeff_single_shift = delta * dt / dx ** 3
    coeff_double_shift = delta * dt / (2 * dx ** 3)

    def shifted(power, inverse):
        return hadamard_test(n, theta_old[1:], theta_new[1:], shift_power(n, power, inverse), expval_fn, expval_kwargs)

    fwd1, bwd1 = shifted(1, True), shifted(1, False)
    fwd2, bwd2 = shifted(2, True), shifted(2, False)
    dispersion_term = amp_old * (coeff_single_shift * (fwd1 - bwd1) - coeff_double_shift * (fwd2 - bwd2))

    convection_coeff = -1.0 / (2 * dx)
    overlap_fwd = nonlinear_overlap(n, theta_old[1:], theta_new[1:], 1, True, expval_fn, expval_kwargs)
    overlap_bwd = nonlinear_overlap(n, theta_old[1:], theta_new[1:], 1, False, expval_fn, expval_kwargs)
    nonlinear_term = dt * convection_coeff * amp_old ** 2 * (overlap_fwd - overlap_bwd)

    return const_term + dispersion_term + nonlinear_term


def kdv_cost_general(theta_new, theta_old, n, dt, dx, delta, expval_fn, **expval_kwargs):
    amp_new = theta_new[0]
    overlap = kdv_overlap_general(n, theta_old, theta_new, dt, dx, delta, expval_fn, **expval_kwargs)
    return np.abs(amp_new) ** 2 - 2 * np.real(np.conj(amp_new) * overlap), overlap
