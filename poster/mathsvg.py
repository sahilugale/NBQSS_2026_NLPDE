"""Render LaTeX math to self-contained inline SVG.

The published artifact's CSP blocks external scripts, so MathJax/KaTeX from a
CDN is not an option, and HTML <sub>/<sup> with unicode looks nothing like real
typesetting. Matplotlib's mathtext engine renders a useful subset of LaTeX with
Computer Modern -- the actual TeX faces -- and can emit SVG with every glyph
converted to a <path>. That means no font dependency at all in the artifact:
the math is vector geometry, crisp at any poster size, and identical on every
machine.

    from mathsvg import mathsvg
    html = mathsvg(r"\\partial_t u + u\\,\\partial_x u = \\nu\\,\\partial_{xx}u", 40)
"""

import re
from io import StringIO, BytesIO

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

matplotlib.rcParams["svg.fonttype"] = "path"   # glyphs -> paths, no font needed
matplotlib.rcParams["mathtext.fontset"] = "cm"  # Computer Modern, the TeX look

_PT_PER_PX = 0.75  # CSS px -> pt


def mathsvg_raw(latex, px=36, color="#22262b", dpi_scale=4):
    """Render LaTeX to (data_uri, width_px, height_px) for embedding via an
    SVG <image> tag -- used when the math must sit INSIDE another SVG (e.g. a
    diagram's boxes), where a top-level <svg>...</svg> string can't be spliced
    in as a sibling element.

    Nested SVG-in-SVG via <image href="data:image/svg+xml;..."> is valid per
    spec but support is inconsistent across renderers; PNG-in-SVG is
    universally supported, so this renders PNG instead -- at `dpi_scale`x the
    final display size, so it stays crisp at the poster's print resolution
    even though the pixels are rasterised rather than path geometry.
    """
    fig = plt.figure(figsize=(0.01, 0.01), dpi=96 * dpi_scale)
    fig.text(0, 0, f"${latex}$", fontsize=px * _PT_PER_PX, color=color)
    buf = StringIO()
    # measure with a throwaway SVG pass (matplotlib reports bbox in points
    # reliably there); the actual embedded asset is the PNG below
    fig.savefig(buf, format="svg", bbox_inches="tight", pad_inches=0.02,
               transparent=True)
    svg = buf.getvalue()
    m = re.search(r'width="([\d.]+)pt" height="([\d.]+)pt"', svg)
    w_pt, h_pt = float(m.group(1)), float(m.group(2))
    w_px, h_px = w_pt / _PT_PER_PX, h_pt / _PT_PER_PX

    pbuf = BytesIO()
    fig.savefig(pbuf, format="png", bbox_inches="tight", pad_inches=0.02,
               transparent=True, dpi=96 * dpi_scale)
    plt.close(fig)

    uri = "data:image/png;base64," + _b64.b64encode(pbuf.getvalue()).decode("ascii")
    return uri, w_px, h_px


def mathsvg_image(latex, cx, cy, px=36, color="#22262b", anchor="middle"):
    """An <image> element for LaTeX math, embeddable inside another SVG.

    (cx, cy) is the horizontal anchor point and the vertical CENTER of the
    math (not its top), matching how a <text text-anchor> call would be
    positioned, so it drops into existing box/annotation layout code with
    the same coordinates a <text> element would have used.
    """
    uri, w, h = mathsvg_raw(latex, px, color)
    x = {"middle": cx - w / 2, "start": cx, "end": cx - w}[anchor]
    y = cy - h / 2
    return f'<image href="{uri}" x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}"/>', w, h


import base64 as _b64  # noqa: E402  (placed here to keep the top import block minimal)


def mathsvg(latex, px=36, color="#22262b", block=False, align="center"):
    """Return an inline <img> (wrapped in a div if block=True) for LaTeX math.

    `latex` is the math WITHOUT surrounding $...$ -- they are added here.
    `px` is the intended cap height in CSS pixels at the poster's 1:1 scale.
    Set `block=True` for a centred display equation on its own line.

    Renders to a PNG data URI (via mathsvg_raw) rather than splicing
    matplotlib's raw <svg> markup into the page. Matplotlib's SVG output
    reuses short, generic ids for every glyph/figure element (id="figure_1",
    id="Cmr10-1a", ...); when TWO OR MORE such fragments land in the same
    HTML document, later fragments' <use href="#..."> references can resolve
    against an EARLIER fragment's <defs> instead of their own -- multiple
    equations sharing one document silently corrupted each other's glyphs.
    A PNG has no internal id references at all, so this can't happen; it
    costs vector crispness (the pipeline-diagram math already paid this same
    trade via mathsvg_image, for the same reason) but is guaranteed correct
    regardless of how many equations end up on one page.
    """
    uri, w, h = mathsvg_raw(latex, px, color)
    img = (f'<img src="{uri}" alt="{latex}" '
          f'style="width:{w:.2f}px;height:{h:.2f}px;'
          f'vertical-align:middle;display:inline-block">')

    if block:
        just = {"center": "center", "left": "flex-start", "right": "flex-end"}[align]
        return (f'<div style="display:flex;justify-content:{just};'
                f'margin:2px 0">{img}</div>')
    return img


if __name__ == "__main__":
    tests = [
        r"\partial_t u + u\,\partial_x u = \nu\,\partial_{xx} u",
        r"\dot{y} = A y + b",
        r"\mathrm{Re} < \pi/2 \approx 1.57",
        r"D_{\mathrm{QSVT}} = \tilde{O}\!\left(\frac{\kappa_V\,T\,N_C^3}{\mathrm{Re}\,\epsilon}\right)",
        r"u^{\top} F_2(u \otimes u) = 0",
        r"\alpha \simeq n_x^{\,N_C-1}\lambda_{\mathrm{cfl}}",
    ]
    for t in tests:
        out = mathsvg(t, 40)
        print(f"{len(out):7d} bytes  {t[:55]}")
