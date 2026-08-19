"""Space-time carpet plots, sized and styled for the poster.

These are the "what does the physics actually do" visuals -- the shock forming
in Burgers, the dispersive train in KdV -- so they carry large type, no chart
junk, and a clean viewing angle. Emitted as PNG (a 3-D surface is thousands of
polygons; PNG at print resolution is far smaller than the equivalent SVG).

    python3 poster_carpets.py
"""

import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from scipy.integrate import solve_ivp

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from discretization import get_F1_F2_burgers, get_F1_F2_kdv  # noqa: E402

OUT = os.path.join(ROOT, "prx_quantum", "figures")
BLUE, ORANGE = "#1f4e8c", "#d2691e"
INK = "#22262b"

CMAP = LinearSegmentedColormap.from_list("poster_div", [BLUE, "#eef2f7", ORANGE])


def integrate(F1, F2, u0, t_end, n_frames=140):
    def rhs(_t, u):
        return F1 @ u + F2 @ np.kron(u, u)
    sol = solve_ivp(rhs, (0.0, t_end), u0, t_eval=np.linspace(0, t_end, n_frames),
                    rtol=1e-10, atol=1e-12, method="RK45")
    return sol.t, sol.y.T


def carpet(x, t, U, fname, zlabel=r"$u(x,t)$", elev=25, azim=-110):
    # close the periodic domain so the surface has no artificial seam
    xs = np.concatenate([x, [1.0]])
    Us = np.hstack([U, U[:, :1]])
    X, T = np.meshgrid(xs, t)
    vmax = float(np.abs(Us).max())

    fig = plt.figure(figsize=(9.2, 7.0), dpi=190)
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(X, T, Us, cmap=CMAP,
                    norm=TwoSlopeNorm(vcenter=0.0, vmin=-vmax, vmax=vmax),
                    rstride=1, cstride=1, linewidth=0.12,
                    edgecolors="#5a6068", antialiased=True, shade=False)
    ax.set_xlabel("$x$", fontsize=25, labelpad=20, color=INK)
    ax.set_ylabel("$t$", fontsize=25, labelpad=20, color=INK)
    ax.set_zlabel(zlabel, fontsize=25, labelpad=18, color=INK)
    ax.tick_params(labelsize=19, colors=INK, pad=6)
    ax.view_init(elev=elev, azim=azim)
    for pane in (ax.xaxis, ax.yaxis, ax.zaxis):
        pane.pane.set_alpha(0.0)
        pane._axinfo["grid"]["color"] = (0.75, 0.75, 0.78, 0.55)
    fig.tight_layout()
    p = os.path.join(OUT, fname)
    fig.savefig(p, bbox_inches="tight", transparent=True)
    plt.close(fig)
    print(f"wrote {p}  ({os.path.getsize(p)/1024:.0f} KB)")


def main():
    # Burgers: sine steepening under weak viscosity -- the shock is the story,
    # so use the variational run's nu = 0.01 (not the Carleman nu = 0.1, where
    # diffusion smooths it away and the picture says nothing).
    n_x, nu, t_end = 80, 0.004, 0.28
    dx = 1.0 / n_x
    x = np.arange(n_x) * dx
    u0 = np.sin(2 * np.pi * x)
    F1, F2 = get_F1_F2_burgers(n_x, nu, dx)
    t, U = integrate(F1, F2, u0, t_end, n_frames=160)
    carpet(x, t, U, "poster_carpet_burgers.png")

    # KdV: dispersion splitting a smooth hump into a leading soliton plus a
    # trailing dispersive wave train -- the textbook KdV signature.
    n_x, delta, t_end = 48, 0.0015, 1.4
    dx = 1.0 / n_x
    x = np.arange(n_x) * dx
    u0 = 0.8 * np.exp(-150.0 * (x - 0.3) ** 2)
    F1, F2 = get_F1_F2_kdv(n_x, delta, dx)
    t, U = integrate(F1, F2, u0, t_end, n_frames=160)
    carpet(x, t, U, "poster_carpet_kdv.png", elev=24, azim=-58)


if __name__ == "__main__":
    main()
