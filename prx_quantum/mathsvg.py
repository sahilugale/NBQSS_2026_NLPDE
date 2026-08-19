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
from io import StringIO

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

matplotlib.rcParams["svg.fonttype"] = "path"   # glyphs -> paths, no font needed
matplotlib.rcParams["mathtext.fontset"] = "cm"  # Computer Modern, the TeX look

_PT_PER_PX = 0.75  # CSS px -> pt


def mathsvg(latex, px=36, color="#22262b", block=False, align="center"):
    """Return an inline <svg> (wrapped in a span/div) for a LaTeX math string.

    `latex` is the math WITHOUT surrounding $...$ -- they are added here.
    `px` is the intended cap height in CSS pixels at the poster's 1:1 scale.
    Set `block=True` for a centred display equation on its own line.
    """
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.text(0, 0, f"${latex}$", fontsize=px * _PT_PER_PX, color=color)
    buf = StringIO()
    fig.savefig(buf, format="svg", bbox_inches="tight", pad_inches=0.02,
                transparent=True)
    plt.close(fig)
    svg = buf.getvalue()

    # keep only the <svg>...</svg> element; drop the XML/DOCTYPE preamble and
    # matplotlib's metadata block, which are noise inside an HTML document
    svg = svg[svg.index("<svg"):]
    svg = re.sub(r"<metadata>.*?</metadata>", "", svg, flags=re.S)
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S)

    # matplotlib sizes the root in pt; convert to px so it lands at the size
    # the caller asked for, and let width scale from the viewBox aspect.
    m = re.search(r'width="([\d.]+)pt" height="([\d.]+)pt"', svg)
    if m:
        w_pt, h_pt = float(m.group(1)), float(m.group(2))
        w_px, h_px = w_pt / _PT_PER_PX, h_pt / _PT_PER_PX
        svg = svg.replace(m.group(0),
                          f'width="{w_px:.2f}" height="{h_px:.2f}"')
        style = (f"width:{w_px:.2f}px;height:{h_px:.2f}px;"
                 "vertical-align:middle;display:inline-block")
        svg = svg.replace("<svg ", f'<svg style="{style}" ', 1)

    if block:
        just = {"center": "center", "left": "flex-start", "right": "flex-end"}[align]
        return (f'<div style="display:flex;justify-content:{just};'
                f'margin:2px 0">{svg}</div>')
    return svg


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
