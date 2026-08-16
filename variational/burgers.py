"""Variational quantum time-propagation for viscous Burgers,

    u_t + u u_x = nu * u_xx,   periodic BC,

built on `pde_core.py`'s general-n primitives, same approach as `kdv.py`
(see that module for derivation background). Convection term ("-f*f_x")
is identical to KdV's, so `nonlinear_overlap` is reused unchanged. Only
the linear operator differs: diffusion is symmetric (D2 = (S+S^-1-2I)/dx^2,
equal-sign S/S^-1 plus a diagonal term) vs. KdV's skew-symmetric dispersion
(zero diagonal) -- hence the extra diffusion prefactor on the constant term
below, and a sum (not difference) for the shift contributions.
"""

import numpy as np

from pde_core import (
    ansatz,
    get_expval_ideal,
    get_expval_shots,
    get_state,
    hadamard_test,
    nonlinear_overlap,
    num_ansatz_params,
    shift_power,
)


def burgers_overlap(n, theta_old, theta_new, dt, dx, nu, expval_fn, **expval_kwargs):
    """Overlap = (constant term, with diffusion prefactor) + (diffusion
    term) + (nonlinear term) for a single explicit-Euler Burgers timestep
    from theta_old (amplitude theta_old[0]) to theta_new."""
    amp_old = theta_old[0]
    bare_overlap = hadamard_test(n, theta_old[1:], theta_new[1:], None, expval_fn, expval_kwargs)

    # --- constant term: diffusion's -2*I piece folds into this prefactor ---
    const_term = amp_old * (1.0 - 2.0 * nu * dt / dx ** 2) * bare_overlap

    # --- diffusion term: S and S^-1 contribute with the SAME sign (D2 is symmetric) ---
    overlap_S = hadamard_test(n, theta_old[1:], theta_new[1:], shift_power(n, 1, inverse=True), expval_fn, expval_kwargs)
    overlap_Sinv = hadamard_test(n, theta_old[1:], theta_new[1:], shift_power(n, 1, inverse=False), expval_fn, expval_kwargs)
    diffusion_term = amp_old * (nu * dt / dx ** 2) * (overlap_S + overlap_Sinv)

    # --- nonlinear term: convection, "-f*f_x" (identical to KdV's) ---
    convection_coeff = -1.0 / (2 * dx)
    overlap_fwd = nonlinear_overlap(n, theta_old[1:], theta_new[1:], 1, True, expval_fn, expval_kwargs)
    overlap_bwd = nonlinear_overlap(n, theta_old[1:], theta_new[1:], 1, False, expval_fn, expval_kwargs)
    nonlinear_term = dt * convection_coeff * amp_old ** 2 * (overlap_fwd - overlap_bwd)

    return const_term + diffusion_term + nonlinear_term


def burgers_cost(theta_new, theta_old, n, dt, dx, nu, expval_fn, **expval_kwargs):
    amp_new = theta_new[0]
    overlap = burgers_overlap(n, theta_old, theta_new, dt, dx, nu, expval_fn, **expval_kwargs)
    return np.abs(amp_new) ** 2 - 2 * np.real(np.conj(amp_new) * overlap), overlap
