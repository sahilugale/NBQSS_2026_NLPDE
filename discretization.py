"""Shared periodic finite-difference building blocks, used by both the
Carleman/QSVT pathway (`carleman_qsvt/`) and the variational pathway
(`variational/`) for their classical reference solutions and (where
applicable) their linear-operator matrices. Centralizing these avoids
duplicating the same few dozen lines of circulant-matrix construction across
four notebooks and two Carleman modules.

All operators use central finite differences with periodic (circulant)
boundary conditions, matching the challenge PDF's periodic BC requirement.
"""

import numpy as np


def periodic_D1(N, dx):
    """Circulant first-derivative matrix, central difference, periodic BC."""
    D = np.zeros((N, N))
    for i in range(N):
        D[i, (i + 1) % N] = 1.0
        D[i, (i - 1) % N] = -1.0
    return D / (2 * dx)


def periodic_D2(N, dx):
    """Circulant second-derivative matrix, central difference, periodic BC
    (the diffusion operator for viscous Burgers)."""
    D = np.zeros((N, N))
    for i in range(N):
        D[i, (i - 1) % N] += 1.0
        D[i, i] += -2.0
        D[i, (i + 1) % N] += 1.0
    return D / dx ** 2


def periodic_D3(N, dx):
    """Circulant third-derivative matrix, central difference, periodic BC
    (the dispersion operator for KdV).

    f'''_i ~ (-f_{i-2} + 2 f_{i-1} - 2 f_{i+1} + f_{i+2}) / (2 dx^3)
    """
    D = np.zeros((N, N))
    for i in range(N):
        D[i, (i - 2) % N] += -1.0
        D[i, (i - 1) % N] += 2.0
        D[i, (i + 1) % N] += -2.0
        D[i, (i + 2) % N] += 1.0
    return D / (2 * dx ** 3)


def construct_F2_periodic_skew(N):
    """Skew-symmetric ('conservative') discretization of -u*u_x:
    -(1/3)[u*(D1 u) + D1(u^2)], as an (N, N**2) bilinear-form matrix (same
    convention as construct_F2_periodic: scale by 1/dx, contract with
    kron(u,u)). Satisfies u^T F2(u kron u) = 0 identically (verified to
    ~1e-16), unlike the plain form -- needed for the challenge's exact L2
    conservation bound for KdV (Section 3): the plain form doesn't have
    this identity, so a naive central-difference KdV solution's L2 norm
    drifts (~11% here) even though D3 (dispersion) is already skew-symmetric
    and contributes zero on its own."""
    D1 = periodic_D1(N, 1.0)
    F = np.zeros((N, N ** 2))

    def index(i, j):
        return i * N + j

    for i in range(N):
        for j in range(N):
            F[i, index(i, j)] += D1[i, j]
            F[i, index(j, j)] += D1[i, j]
    return -(1.0 / 3.0) * F


def construct_F2_periodic(N):
    """Quadratic-term matrix for -u*u_x ~ -(1/(2dx)) * u_i*(u_{i+1}-u_{i-1}),
    periodic wraparound. Shape (N, N**2), flattened index (i,j) -> i*N+j.
    Scale by -1/(2*dx) to get the actual convection-term matrix (kept
    unscaled here so callers can see the pure combinatorial structure)."""
    F = np.zeros((N, N ** 2))

    def index(i, j):
        return i * N + j

    for i in range(N):
        F[i, index(i, (i + 1) % N)] += 1.0
        F[i, index(i, (i - 1) % N)] += -1.0
    return F


def get_F1_F2_kdv(N, delta, dx):
    """F1 (dispersion, linear) and F2 (convection, quadratic) for
    u_t + u u_x + delta*u_xxx = 0. Skew-symmetric F2 (u^T F2(u kron u) = 0
    identically) -- needed for the exact ||u(t)||_2 = ||u0||_2 conservation."""
    F1 = -delta * periodic_D3(N, dx)
    F2 = (1.0 / dx) * construct_F2_periodic_skew(N)
    return F1, F2


def get_F1_F2_burgers(N, nu, dx):
    """F1 (diffusion, linear) and F2 (convection, quadratic) for
    u_t + u u_x = nu*u_xx. Skew-symmetric F2 (u^T F2(u kron u) = 0
    identically) -- combined with F1's negative semi-definiteness, this is
    what makes ||u(t)||_2 provably non-increasing for any N, matching the
    challenge's Section 3 bound; the plain (non-skew) F2 does not have this
    identity in general and can let ||u(t)||_2 grow at coarse N."""
    F1 = nu * periodic_D2(N, dx)
    F2 = (1.0 / dx) * construct_F2_periodic_skew(N)
    return F1, F2
