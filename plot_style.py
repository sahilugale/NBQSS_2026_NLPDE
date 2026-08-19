"""Shared matplotlib style for all notebooks -- LaTeX-like (Computer Modern
mathtext, serif) fonts, consistent colors, no system LaTeX required."""

import matplotlib.pyplot as plt

# Unified palette, shared by the notebooks, scaling_analysis/figs.py and the
# report/paper figures. Colors carry a fixed *meaning*, not just an index, so
# that the same hue means the same thing in every figure of the writeup:
#
#   classical  reference / exact solution                (neutral gray)
#   blue       Carleman-QSVT, primary   (dense encoding)
#   blue_lt    Carleman-QSVT, secondary (Pauli-LCU / sparse oracle)
#   aqua       variational route, ideal quantum
#   orange     real hardware / physical world (noisy readout, analog platform)
#   red        reserved: the one fundamental obstruction (Re < pi/2)
COLORS = {
    "classical": "#8a9199",
    "blue": "#1f4e8c",
    "blue_lt": "#7fa9d8",
    "aqua": "#14796b",
    "orange": "#d2691e",
    "red": "#b3261e",
    "yellow": "#eda100",
}


def set_style():
    plt.rcParams.update({
        "font.family": "serif",
        "mathtext.fontset": "cm",
        "font.size": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.25,
        "legend.frameon": False,
        "lines.linewidth": 2.0,
        "lines.markersize": 5,
        "figure.dpi": 130,
        "savefig.dpi": 130,
    })
