"""Shared matplotlib style for all notebooks -- LaTeX-like (Computer Modern
mathtext, serif) fonts, consistent colors, no system LaTeX required."""

import matplotlib.pyplot as plt

# fixed categorical order, validated for colorblind-safety
COLORS = {
    "classical": "#52514e",  # neutral gray -- reference/exact solution
    "blue": "#2a78d6",
    "orange": "#eb6834",
    "aqua": "#1baf7a",
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
