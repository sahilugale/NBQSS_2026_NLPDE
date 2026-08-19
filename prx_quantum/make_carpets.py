"""Regenerate the space-time surface ("carpet") figures.

These are the only paper figures not produced directly by a notebook, so they
live here. Colors come from the shared palette in ../plot_style.py: the
diverging colormap is built from the same blue and orange the rest of the
figures use, so a surface reads consistently against the line plots.

    python3 make_carpets.py
"""

import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  (registers 3d projection)
from scipy.integrate import solve_ivp

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from plot_style import set_style, COLORS  # noqa: E402
from discretization import get_F1_F2_burgers, get_F1_F2_kdv  # noqa: E402

OUT = os.path.join(ROOT, "prx_quantum", "figures")

# diverging map anchored on the palette: blue (negative) - light (zero) - orange (positive)
CARPET_CMAP = LinearSegmentedColormap.from_list(
    "palette_div", [COLORS["blue"], "#eef1f4", COLORS["orange"]]
)


def integrate(F1, F2, u0, t_end, n_frames=120):
    """Dense-in-time reference trajectory of u' = F1 u + F2 (u kron u)."""
    def rhs(_t, u):
        return F1 @ u + F2 @ np.kron(u, u)

    t_eval = np.linspace(0.0, t_end, n_frames)
    sol = solve_ivp(rhs, (0.0, t_end), u0, t_eval=t_eval,
                    rtol=1e-10, atol=1e-12, method="RK45")
    return sol.t, sol.y.T


def carpet(x, t, U, title, fname):
    X, T = np.meshgrid(x, t)
    vmax = np.abs(U).max()
    fig = plt.figure(figsize=(6.5, 5.0))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(
        X, T, U, cmap=CARPET_CMAP,
        norm=TwoSlopeNorm(vcenter=0.0, vmin=-vmax, vmax=vmax),
        rstride=1, cstride=1, linewidth=0.15,
        edgecolors="0.35", antialiased=True, shade=False,
    )
    ax.set_xlabel("$x$")
    ax.set_ylabel("$t$")
    ax.set_zlabel("$u(x, t)$")
    ax.set_title(title)
    ax.view_init(elev=26, azim=-58)
    ax.xaxis.pane.set_alpha(0.0)
    ax.yaxis.pane.set_alpha(0.0)
    ax.zaxis.pane.set_alpha(0.0)
    fig.tight_layout()
    path = os.path.join(OUT, fname)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print("wrote", path)


def main():
    set_style()

    # --- Burgers, matching carleman_qsvt/Burgers_Carlemann_qiskit.ipynb ---
    n_x, nu, t_end = 5, 0.1, 0.3
    dx = 1.0 / n_x
    x = np.arange(n_x) * dx
    u0 = np.sin(2 * np.pi * x)
    F1, F2 = get_F1_F2_burgers(n_x, nu, dx)
    t, U = integrate(F1, F2, u0, t_end)
    carpet(x, t, U, r"Burgers: classical reference, space--time surface",
           "fig_burgers_carpet.pdf")

    # --- KdV, matching carleman_qsvt/KdV_Carlemann_qiskit.ipynb ---
    n_x, delta, t_end = 4, 0.0625, 0.3
    dx = 1.0 / n_x
    x = np.arange(n_x) * dx
    u0 = np.array([0.0, -0.5, 1 / np.sqrt(2), 0.5])
    u0 = u0 / np.linalg.norm(u0)
    F1, F2 = get_F1_F2_kdv(n_x, delta, dx)
    t, U = integrate(F1, F2, u0, t_end)
    carpet(x, t, U, r"KdV: classical reference, space--time surface",
           "fig_kdv_carpet.pdf")


if __name__ == "__main__":
    main()
