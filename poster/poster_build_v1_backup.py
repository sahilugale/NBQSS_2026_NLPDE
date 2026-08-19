"""Assemble Main.dc.html for the conference poster.

Authored here so the generated SVGs (threshold, propagation, accuracy ladder,
repo QR) are inlined verbatim rather than pasted by hand.

    python3 poster_propagation.py     # once, for the propagation data
    python3 poster_figs.py && python3 poster_build.py
"""

import os
import base64 as _b64
import io as _io

HERE = os.path.dirname(os.path.abspath(__file__))
from mathsvg import mathsvg
read = lambda n: open(os.path.join(HERE, n), encoding="utf-8").read().strip()

FIG_THRESHOLD = read("fig_threshold.svg")
FIG_ACCURACY = read("fig_accuracy.svg")
FIG_PROPAGATION = read("fig_propagation.svg")
FIG_QR = read("fig_qr.svg")

import poster_figs as _pf

def figbox(svg, height):
    """Inline an SVG inside a fixed-height box.

    The generated SVGs carry only a viewBox, so left alone they take the full
    column width and set their own height -- the threshold plot alone would
    claim ~1000 px. Sizing them here keeps the A0 sheet from overflowing.
    """
    svg = svg.replace("<svg ", '<svg style="width:100%;height:100%;display:block" ', 1)
    return (f'<div style="height:{height}px;display:flex;align-items:center;'
            f'justify-content:center">{svg}</div>')


INK, BODY, MUTED = "#22262b", "#3a4048", "#6b7280"
PAPER, CARD, RULE = "#f2f0ec", "#fdfcfa", "#d9d5cd"
BLUE, TEAL, ORANGE, RED = "#1f4e8c", "#14796b", "#d2691e", "#b3261e"

SERIF = "'IBM Plex Serif',Georgia,serif"
MONO = "'IBM Plex Mono',ui-monospace,monospace"


def icon_target(color, size=44):
    """Bullseye -- marks "here is our actual contribution"."""
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="1.7"><circle cx="12" cy="12" r="9"/>'
            f'<circle cx="12" cy="12" r="5.3"/>'
            f'<circle cx="12" cy="12" r="1.7" fill="{color}" stroke="none"/></svg>')


def icon_warning(color, size=44):
    """Triangle -- marks an honest limitation."""
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="1.7" stroke-linejoin="round" '
            f'stroke-linecap="round"><path d="M12 3.4 L21.7 20.2 H2.3 Z"/>'
            f'<line x1="12" y1="9.2" x2="12" y2="14.3"/>'
            f'<circle cx="12" cy="17.1" r="0.95" fill="{color}" stroke="none"/></svg>')


def icon_star(color, size=44):
    """Five-point star -- marks the take-home line."""
    pts = "12,3 14.7,9.3 21.5,9.9 16.3,14.4 17.9,21.1 12,17.4 6.1,21.1 7.7,14.4 2.5,9.9 9.3,9.3"
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24"><polygon points="{pts}" fill="{color}"/></svg>'


def badge(num, color, size=58):
    """A filled circular number badge, the numbered-step convention used
    throughout the poster's reference visual style."""
    return (f'<div style="flex:none;width:{size}px;height:{size}px;border-radius:50%;'
            f'background:#ffffff;display:flex;align-items:center;justify-content:center;'
            f'font-family:{MONO};font-size:{round(size*0.44)}px;font-weight:700;'
            f'color:{color}">{num}</div>')


def _img_data_uri(path, max_dim=1000, jpeg=False, bg="#fdfcfa", quality=84):
    from PIL import Image
    im = Image.open(path)
    if max(im.size) > max_dim:
        s = max_dim / max(im.size)
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    if jpeg:
        # flatten any alpha onto `bg` -- JPEG has no transparency, and this is
        # for photographic/gradient content (carpet plots, the NBQSS badge)
        # where PNG's lossless encoding wastes hundreds of KB on noise a
        # viewer will never perceive at poster scale.
        base = Image.new("RGB", im.size, bg)
        if im.mode in ("RGBA", "LA"):
            base.paste(im, mask=im.split()[-1])
        else:
            base.paste(im.convert("RGB"))
        buf = _io.BytesIO()
        base.save(buf, format="JPEG", quality=quality, optimize=True)
        return f"data:image/jpeg;base64,{_b64.b64encode(buf.getvalue()).decode('ascii')}"
    if im.mode not in ("RGBA", "RGB"):
        im = im.convert("RGBA")
    buf = _io.BytesIO()
    im.save(buf, format="PNG", optimize=True)
    return f"data:image/png;base64,{_b64.b64encode(buf.getvalue()).decode('ascii')}"


def panel(num, label, color, heading, body, extra=""):
    """A numbered section: a circular badge + label bar over a bordered body.

    The badge/heading/body triple is what carries the hierarchy -- a filled
    number circle, then large serif, then sans body -- so a section boundary
    is unmistakable from several metres away.
    """
    return f"""
  <section style="display:flex;flex-direction:column">
    <div style="display:flex;align-items:center;gap:18px;background:{color};
                padding:11px 26px 11px 14px">
      {badge(num, color, 50)}
      <span style="font-family:{MONO};font-size:29px;font-weight:600;letter-spacing:.16em;
                   text-transform:uppercase;color:#ffffff;line-height:1">{label}</span>
    </div>
    <div style="background:{CARD};border:2px solid {RULE};border-top:none;
                padding:28px 30px 30px;display:flex;flex-direction:column;gap:18px;flex:1">
      <h3 style="margin:0;font-family:{SERIF};font-size:46px;font-weight:600;
                 line-height:1.14;color:{INK};text-wrap:balance">{heading}</h3>
      <div style="font-size:30px;line-height:1.42;color:{BODY}">{body}</div>{extra}
    </div>
  </section>"""


def lane(color, tag, title, boxes, price, price_unit, price_note, measured):
    svg, _ = _pf.fig_lane_pipeline(color, boxes)
    # Deterministic sizing: cap the SVG's rendered WIDTH and let height follow
    # the viewBox aspect ratio (auto), rather than stretching to fill the
    # column. That keeps box/font size visually identical across all three
    # lanes regardless of how many pipeline stages each one has -- a lane
    # with fewer stages is simply a shorter diagram, not a stretched one.
    svg = svg.replace("<svg ",
        '<svg style="width:100%;max-width:520px;height:auto;display:block" ', 1)
    badge = "measured" if measured else "projected"
    badge_bg = INK if measured else MUTED
    return f"""
    <div style="flex:1;display:flex;flex-direction:column;background:{CARD};
                border:2px solid {RULE};border-top:10px solid {color}">
      <div style="padding:22px 26px 0;display:flex;flex-direction:column;gap:14px;flex:1">
        <div style="display:flex;flex-direction:column;gap:4px">
          <div style="font-family:{MONO};font-size:25px;letter-spacing:.14em;
                      text-transform:uppercase;color:{color}">{tag}</div>
          <div style="font-family:{SERIF};font-size:42px;font-weight:600;color:{INK};
                      line-height:1.1">{title}</div>
        </div>
        <div style="flex:1;display:flex;align-items:center;justify-content:center">{svg}</div>
      </div>
      <div style="margin-top:auto;display:flex;align-items:baseline;gap:18px;
                  padding:18px 26px 20px;border-top:2px solid {RULE};background:#f7f5f1">
        <span style="font-family:{MONO};font-size:80px;font-weight:600;color:{color};
                     line-height:1">{price}</span>
        <div style="display:flex;flex-direction:column;gap:2px">
          <span style="font-size:30px;color:{INK}">{price_unit}</span>
          <span style="font-size:24px;color:{MUTED}">{price_note}</span>
        </div>
        <span style="margin-left:auto;align-self:center;font-family:{MONO};font-size:21px;
                     letter-spacing:.1em;text-transform:uppercase;color:#fdfcfa;
                     background:{badge_bg};padding:5px 12px">{badge}</span>
      </div>
    </div>"""


HERO_LANES = (
    lane(BLUE, "Route 1 · pay the toll", "Carleman + QSVT", _pf.ROUTE1_BOXES,
         "10<sup style='font-size:44px'>12</sup>", "two-qubit gates",
         "Re = 1, &epsilon; = 10&#8315;&#179;; needs fault tolerance", False)
    + lane(TEAL, "Route 2 · refuse the toll", "Variational propagation", _pf.ROUTE2_BOXES,
           "351", "gates, 6 qubits",
           "largest circuit; runs on a queued device today", True)
    + lane(ORANGE, "Route 3 · change the hardware", "Degenerate cavity laser", _pf.ROUTE3_BOXES,
           "0", "gates",
           "no circuit at all &mdash; but it solves one equation", False)
)

# Each entry: (logo basename in logos/, fallback label). The basename is
# matched against ANY extension actually present (png/jpg/jpeg/webp/svg), so
# it doesn't matter which format each institution's mark arrived in. If no
# file matches, a dashed placeholder with the label is drawn instead, so the
# poster always builds either way.
LOGO_SPECS = [
    ("weizmann",       "Weizmann Institute<br>of Science"),
    ("citystgeorges",  "City St George&rsquo;s<br>Univ. of London"),
    ("technion",       "Technion &mdash; Israel<br>Institute of Technology"),
    ("sfu",            "Simon Fraser<br>University"),
    ("juelich",        "Forschungszentrum<br>J&uuml;lich &middot; PGI-8"),
    ("koeln",          "University<br>of Cologne"),
]

import base64 as _b64
import io as _io

_LOGO_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".svg")
_LOGO_MAX_DIM = 420  # px; the rendered slot is ~250px tall, this keeps print-quality margin


def _find_logo(basename):
    d = os.path.join(HERE, "logos")
    if not os.path.isdir(d):
        return None
    for ext in _LOGO_EXTS:
        p = os.path.join(d, basename + ext)
        if os.path.exists(p):
            return p
    return None


def _logo_data_uri(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".svg":
        # SVGs scale losslessly -- embed the markup verbatim as a data URI,
        # no rasterisation needed.
        raw = open(path, "rb").read()
        return f"data:image/svg+xml;base64,{_b64.b64encode(raw).decode('ascii')}"
    from PIL import Image
    im = Image.open(path)
    if im.mode not in ("RGBA", "RGB"):
        im = im.convert("RGBA")
    if max(im.size) > _LOGO_MAX_DIM:
        scale = _LOGO_MAX_DIM / max(im.size)
        im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))),
                       Image.LANCZOS)
    buf = _io.BytesIO()
    im.save(buf, format="PNG", optimize=True)
    return f"data:image/png;base64,{_b64.b64encode(buf.getvalue()).decode('ascii')}"


def _logo_slot(basename, label):
    path = _find_logo(basename)
    if path:
        uri = _logo_data_uri(path)
        return (f'      <div style="flex:1;height:104px;display:flex;align-items:center;'
                f'justify-content:center;padding:6px 14px">'
                f'<img src="{uri}" alt="{label}" '
                f'style="max-width:100%;max-height:100%;object-fit:contain"></div>')
    return (f'      <div style="flex:1;height:78px;border:2px dashed #c9c4ba;background:#faf9f6;'
            f'display:flex;align-items:center;justify-content:center;text-align:center">'
            f'<span style="font-size:20px;line-height:1.25;color:#a09a90">{label}</span></div>')

LOGO_SLOTS = "\n".join(_logo_slot(bn, lab) for bn, lab in LOGO_SPECS)

EQ = f"font-family:{SERIF};font-size:40px;font-style:italic;color:{INK};line-height:1.5"

_nbqss_path = _find_logo("NBQSS")
_nbqss_logo_uri = (_img_data_uri(_nbqss_path, max_dim=300, jpeg=True, bg="#2a1f4d")
                    if _nbqss_path else "")

POSTER = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Serif:ital,wght@0,400;0,600;0,700;1,400&display=swap">
  <style>
    body {{ margin: 0; background: {PAPER};
           font-family: 'IBM Plex Sans', system-ui, sans-serif;
           -webkit-font-smoothing: antialiased; }}
    a {{ color: {BLUE}; text-decoration: none; }}
    a:hover {{ color: #14396b; }}
    sup {{ font-size: .62em; }}
    ul {{ margin: 0; padding-left: 28px; }}
  </style>
</helmet>

<div style="width:4494px;height:3179px;background:{PAPER};color:{INK};
            padding:40px 100px 40px;box-sizing:border-box;
            display:flex;flex-direction:column;gap:18px">

  <!-- ========================== logo band ========================== -->
  <div style="display:flex;align-items:center;gap:22px">
{LOGO_SLOTS}
    <div style="flex:none;padding-left:26px;border-left:2px solid {RULE}">
      <img src="{_nbqss_logo_uri}" alt="Niels Bohr Quantum Summer School 2026,
           Center for Quantum Mathematics, University of Southern Denmark"
           style="flex:none;width:104px;height:104px;border-radius:12px;object-fit:cover">
    </div>
  </div>

  <!-- ========================== masthead =========================== -->
  <header style="display:flex;align-items:flex-end;gap:70px;
                 border-bottom:5px solid {INK};padding-bottom:18px">
    <div style="flex:1;display:flex;flex-direction:column;gap:14px">
      <div style="font-family:{MONO};font-size:28px;letter-spacing:.17em;
                  text-transform:uppercase;color:{BLUE}">
        Quantum simulation of nonlinear partial differential equations
      </div>
      <h1 style="margin:0;font-family:{SERIF};font-size:118px;font-weight:700;
                 line-height:0.97;letter-spacing:-0.022em">The Price of Linearity</h1>
      <div style="font-size:41px;line-height:1.22;color:{BODY};max-width:2500px;
                  text-wrap:balance">
        What it costs to run a nonlinear fluid on a machine that only does linear
        algebra &mdash; and what you get for refusing to pay.
      </div>
    </div>
    <div style="flex:none;width:1120px;text-align:right;display:flex;
                flex-direction:column;gap:12px;padding-bottom:6px">
      <div style="font-size:36px;font-weight:600;line-height:1.33;color:{INK}">
        Andrei Poliakov<sup>1</sup> &nbsp; Kyro Jeremy Gibling<sup>2</sup> &nbsp;
        Nadav Carmel<sup>3</sup><br>
        Pak Tik Fong<sup>4</sup> &nbsp; Sahil Ugale<sup>5,6</sup>
      </div>
      <div style="font-size:25px;line-height:1.5;color:{MUTED}">
        <sup>1</sup>Weizmann Institute of Science &nbsp;
        <sup>2</sup>City St George&rsquo;s, University of London<br>
        <sup>3</sup>Technion &mdash; Israel Institute of Technology, Haifa 3200003 &nbsp;
        <sup>4</sup>Simon Fraser University<br>
        <sup>5</sup>Forschungszentrum J&uuml;lich, PGI-8 &nbsp;
        <sup>6</sup>University of Cologne
      </div>
    </div>
  </header>

  <!-- ============================ hero ============================= -->
  <section style="display:flex;flex-direction:column;gap:22px">
    <h2 style="margin:0;font-family:{SERIF};font-size:50px;font-weight:600;
               line-height:1.08;color:{INK}">
      A quantum computer is a linear machine. A fluid is not. Something has to give.
    </h2>

    <div style="display:flex;flex-direction:column;gap:12px">
      <div style="font-family:{MONO};font-size:24px;letter-spacing:.14em;
                  text-transform:uppercase;color:{MUTED}">
        What the equations actually do
      </div>
      <div style="display:flex;gap:30px">
        <div style="flex:1.7;display:flex;align-items:center;gap:24px;background:{CARD};
                    border:2px solid {RULE};border-top:8px solid {BLUE};padding:18px 24px">
          <img src="{_img_data_uri(os.path.join(HERE,"figures","poster_carpet_burgers.png"), max_dim=760, jpeg=True)}"
               alt="Burgers space-time surface: a sine wave steepening into a sawtooth shock"
               style="flex:none;height:380px;width:auto;display:block">
          <div style="display:flex;flex-direction:column;gap:12px">
            <div style="font-family:{SERIF};font-size:34px;font-weight:600;color:{BLUE};
                        line-height:1.2">A smooth wave steepens into a shock</div>
            <div style="background:#eef2f8;padding:12px 18px;display:inline-flex">
              {mathsvg(r"\partial_t u + u\,\partial_x u = \nu\,\partial_{{xx}}u", 42, color=BLUE)}
            </div>
            <div style="font-size:25px;line-height:1.38;color:{MUTED}">
              Viscosity fights the steepening; the surface shows exactly where it loses.</div>
          </div>
        </div>
        <div style="flex:1.7;display:flex;align-items:center;gap:24px;background:{CARD};
                    border:2px solid {RULE};border-top:8px solid {ORANGE};padding:18px 24px">
          <img src="{_img_data_uri(os.path.join(HERE,"figures","poster_carpet_kdv.png"), max_dim=760, jpeg=True)}"
               alt="KdV space-time surface: a Gaussian pulse splitting into a leading soliton and trailing ripples"
               style="flex:none;height:380px;width:auto;display:block">
          <div style="display:flex;flex-direction:column;gap:12px">
            <div style="font-family:{SERIF};font-size:34px;font-weight:600;color:{ORANGE};
                        line-height:1.2">Dispersion splits a pulse into a soliton and a wave train</div>
            <div style="background:#fdf1e6;padding:12px 18px;display:inline-flex">
              {mathsvg(r"\partial_t u + u\,\partial_x u + \delta\,\partial_{{xxx}}u = 0", 42, color=ORANGE)}
            </div>
            <div style="font-size:25px;line-height:1.38;color:{MUTED}">
              No energy is lost &mdash; it just redistributes across a trailing ripple train.</div>
          </div>
        </div>
        <div style="flex:1;display:flex;flex-direction:column;align-items:center;
                    justify-content:center;gap:20px;background:#e8e5df;
                    border-left:10px solid {MUTED};padding:18px 22px">
          <span style="font-family:{MONO};font-size:26px;font-weight:600;letter-spacing:.08em;
                       text-transform:uppercase;color:{MUTED};text-align:center;line-height:1.35">
            Both discretise to<br>one quadratic ODE</span>
          {mathsvg(r"\dot{{u}} = F_1 u + F_2(u\otimes u)", 46, color=INK, block=True)}
        </div>
      </div>
    </div>

    <div style="display:flex;gap:40px;align-items:stretch">{HERO_LANES}
    </div>
  </section>

  <!-- ========================= three columns ======================= -->
  <div style="display:grid;grid-template-columns:1120px 1540px 1450px;gap:36px;flex:1">

    <!-- ---------------- column A ---------------- -->
    <div style="display:flex;flex-direction:column;gap:20px">
      {panel("1", "The problem", BLUE,
             "Discretising a conservation law usually breaks it",
             "The plain central-difference convective term does not conserve the "
             "semi-discrete energy: a naive KdV run drifts <b>11%</b> in a norm the equation "
             "conserves exactly &mdash; a discretisation quietly violating the physics it "
             "was built to model.",
             f'''
      <div style="background:#eef2f8;border-left:8px solid {BLUE};padding:22px 26px;
                  display:flex;flex-direction:column;gap:10px">
        {mathsvg(r"u^{\top}F_2(u \otimes u) = 0", 42, color=BLUE, block=True, align="left")}
        <div style="font-size:29px;line-height:1.4;color:{BODY}">
          The skew-symmetric closure makes this an <i>identity</i> &mdash; verified to
          10<sup>&#8722;17</sup>. With it &#8214;u&#8214;<sub>2</sub> is provably
          non-increasing for Burgers and exactly conserved for KdV, <b>at any
          resolution</b>.
        </div>
      </div>''')}

      {panel("2", "A trap in the time axis", BLUE,
             "Forward Euler adds energy to a conservative equation, every step",
             "&#8214;u<sub>n+1</sub>&#8214;&sup2; = &#8214;u<sub>n</sub>&#8214;&sup2; + "
             "&Delta;t&sup2;&#8214;f(u<sub>n</sub>)&#8214;&sup2; &mdash; exactly, for any "
             "step size, with a diligence no physicist requested. Implicit midpoint "
             "conserves the norm to 10<sup>&#8722;10</sup>; we use it for KdV.")}

      <div style="background:{INK};color:#f7f6f3;padding:28px 30px;
                  display:flex;flex-direction:column;gap:15px;flex:1">
        <div style="display:flex;align-items:center;gap:14px">
          {icon_target("#7fa9d8", 40)}
          <div style="font-family:{MONO};font-size:27px;font-weight:600;letter-spacing:.16em;
                      text-transform:uppercase;color:#cbd3dd">What is new here</div>
        </div>
        <ul style="font-size:27px;line-height:1.34;display:flex;flex-direction:column;gap:10px">
          <li>A cost decomposition that <b>localises</b> the obstruction: of five drivers,
              one is fundamental, three have identified fixes.</li>
          <li>A grid-independent convergence ratio R<sub>&#9733;</sub> = (2/&pi;)Re,
              replacing an estimate that grew with resolution.</li>
          <li>A <b>proven</b> Lipschitz certificate retiring most classical sign lookups
              (thousands &rarr; ~55 per step).</li>
          <li>Both equations end to end &mdash; KdV as the control Burgers cannot be.</li>
        </ul>
      </div>
    </div>

    <!-- ---------------- column B : the wall ---------------- -->
    <div style="display:flex;flex-direction:column;gap:20px">
      {panel("3", "Result &mdash; the wall", RED,
             "Provably convergent only where the fluid stops being interesting",
             "Sharpening the Carleman ratio on the tensor manifold gives "
             "R<sub>&#9733;</sub> = (2/&pi;)Re, so the series converges provably only for "
             "<b>Re &lt; &pi;/2 &asymp; 1.57</b>. Rescaling cannot help &mdash; the "
             "constraint is physical, not a normalisation artefact.",
             f'''
      {figbox(FIG_THRESHOLD, 360)}
      <div style="display:flex;gap:22px;align-items:stretch">
        <div style="flex:1;background:#fdf3f2;border-left:8px solid {RED};padding:20px 24px;
                    display:flex;flex-direction:column;gap:8px">
          <div style="font-size:29px;line-height:1.35;color:{BODY}">
            <b>Assembled cost</b>, sparse oracle + history-state dilation:</div>
          {mathsvg(r"D_{\mathrm{QSVT}} = \tilde{O}\!\left(\frac{\kappa_V\,T\,N_C^3}{\mathrm{Re}\,\epsilon}\right)", 34, color=RED, block=True, align="left")}
        </div>
        <div style="flex:1;background:#eeece7;padding:20px 24px;display:flex;
                    flex-direction:column;gap:8px">
          <div style="font-size:29px;line-height:1.35;color:{BODY}">
            <b>Measured</b>, one inversion, N = 5, &kappa; = 8:</div>
          <div style="font-family:{MONO};font-size:31px;line-height:1.4;color:{INK}">
            2,612,767 <span style="color:{MUTED}">dense</span><br>
            1,716,882,557 <span style="color:{MUTED}">Pauli-LCU</span></div>
        </div>
      </div>
      <div style="border-top:3px solid {INK};padding-top:20px;display:flex;
                  flex-direction:column;gap:12px">
        <div style="font-family:{MONO};font-size:25px;letter-spacing:.14em;
                    text-transform:uppercase;color:{MUTED}">
          The bill, at the largest Re the series provably survives</div>
        <div style="display:flex;align-items:flex-end;gap:34px">
          <div style="display:flex;flex-direction:column">
            <span style="font-family:{MONO};font-size:92px;font-weight:600;color:{BLUE};
                         line-height:1">1.3&times;10<sup style="font-size:50px">12</sup></span>
            <span style="font-size:29px;color:{BODY}">quantum two-qubit gates</span></div>
          <span style="font-size:48px;color:#8a9199;padding-bottom:30px">vs</span>
          <div style="display:flex;flex-direction:column">
            <span style="font-family:{MONO};font-size:92px;font-weight:600;color:{INK};
                         line-height:1">4.4&times;10<sup style="font-size:50px">6</sup></span>
            <span style="font-size:29px;color:{BODY}">classical flops, same instance</span></div>
          <div style="margin-left:auto;text-align:right;font-size:27px;line-height:1.38;
                      color:{MUTED};max-width:400px">
            Re = 1, &epsilon; = 10<sup>&#8722;3</sup>, T = 0.3, n<sub>x</sub> = 128.<br>
            ~36 h fault-tolerant vs. ~1 ms on a laptop.</div>
        </div>
      </div>''')}
    </div>

    <!-- ---------------- column C : the way out ---------------- -->
    <div style="display:flex;flex-direction:column;gap:20px">
      {panel("4", "Result &mdash; the way out", TEAL,
             "Keep the nonlinearity classical, and the circuits fit on today&rsquo;s hardware",
             "The variational route never builds the embedding: a shallow ansatz holds the "
             "field, a classical optimiser chases the nonlinear target. The device curve "
             "still tracks the wave &mdash; including the advective steepening at t = 0.30.",
             f'''
      {figbox(FIG_PROPAGATION, 290)}
      <div style="background:#edf5f3;border-left:8px solid {TEAL};padding:20px 26px;
                  font-size:29px;line-height:1.4;color:{BODY}">
        <b>What matters:</b> the method is not the limitation &mdash; the device is.
        Ideal circuits track the reference to 10<sup>&#8722;8</sup>&ndash;10<sup>&#8722;6</sup>;
        the same circuits under a real IBM calibration snapshot land at 5&ndash;21%,
        with no error mitigation and no post-selection.
      </div>''')}

      <div style="border:3px solid {INK};padding:24px 28px;display:flex;
                  flex-direction:column;gap:12px">
        <div style="display:flex;align-items:center;gap:12px">
          {icon_warning(RED, 36)}
          <div style="font-family:{MONO};font-size:25px;letter-spacing:.14em;
                      text-transform:uppercase;color:{MUTED}">Where this breaks down</div>
        </div>
        <ul style="font-size:27px;line-height:1.36;color:{BODY};display:flex;
                   flex-direction:column;gap:9px">
          <li><b>Burgers alone can't prove a method handles nonlinearity</b> &mdash;
              Cole&ndash;Hopf maps it exactly onto the linear heat equation, so we
              carry KdV (no such shortcut exists) through every stage as the control.</li>
          <li>Variational: nonconvex, no convergence guarantee; a residual
              O(2<sup>n</sup>) classical step is <i>reduced</i>, not eliminated.</li>
          <li>Our 2.6&times;10<sup>6</sup> is the cost of a <i>structure-blind</i>
              encoding &mdash; not intrinsic to Carleman.</li>
          <li>Analog route: phase-only effective model, stationary profile only.
              All of this is 1D &mdash; a crossover in work needs d &ge; 3.</li>
        </ul>
      </div>
    </div>
  </div>

  <!-- ============================ footer =========================== -->
  <footer style="display:flex;gap:50px;align-items:flex-start;
                 border-top:6px solid {INK};padding-top:24px">
    <div style="flex:1;display:flex;flex-direction:column;gap:14px">
      <div style="display:flex;align-items:center;gap:14px">
        {icon_star(BLUE, 38)}
        <div style="font-family:{MONO};font-size:27px;font-weight:600;letter-spacing:.16em;
                    text-transform:uppercase;color:{BLUE}">Take home</div>
      </div>
      <div style="display:flex;gap:38px">
        <div style="flex:1;font-size:31px;line-height:1.38;color:{BODY}">
          <b style="color:{INK}">1.</b> In one dimension the linear-embedding route buys
          exponential <i>memory</i> compression and nothing else.</div>
        <div style="flex:1;font-size:31px;line-height:1.38;color:{BODY}">
          <b style="color:{INK}">2.</b> The binding constraint is physics, not engineering:
          three of five cost drivers have fixes; Re &lt; &pi;/2 does not.</div>
        <div style="flex:1;font-size:31px;line-height:1.38;color:{BODY}">
          <b style="color:{INK}">3.</b> Declining the embedding already works &mdash; the
          remaining gap is device noise, not the method.</div>
      </div>
      <div style="font-size:24px;line-height:1.42;color:{MUTED};margin-top:4px">
        <b style="color:{BODY}">References</b> &nbsp;
        A. Setty, <i>J. Phys. A</i> <b>59</b>, 185303 (2026) &middot;
        J.-P. Liu <i>et al.</i>, <i>PNAS</i> <b>118</b>, e2026805118 (2021) &middot;
        A. Gily&eacute;n <i>et al.</i>, <i>STOC</i> 2019, 193 &middot;
        X. Yuan <i>et al.</i>, <i>Quantum</i> <b>3</b>, 191 (2019) &middot;
        A. C. McLachlan, <i>Mol. Phys.</i> <b>8</b>, 39 (1964)
      </div>
    </div>
    <div style="flex:none;display:flex;align-items:center;gap:22px;
                border-left:3px solid {RULE};padding-left:40px">
      <div style="width:240px;height:240px">{FIG_QR}</div>
      <div style="display:flex;flex-direction:column;gap:6px">
        <div style="font-size:29px;font-weight:600;color:{INK}">Code, notebooks<br>&amp; manuscript</div>
        <div style="font-family:{MONO};font-size:23px;line-height:1.38;color:{MUTED}">
          github.com/sahilugale/<br>NBQSS_2026_NLPDE</div>
      </div>
    </div>
  </footer>
</div>
</x-dc>

<script data-dc-script data-props='{{}}'>
class Component extends DCLogic {{
  renderVals() {{ return {{}}; }}
}}
</script>
</body>
</html>
"""

if __name__ == "__main__":
    p = os.path.join(HERE, "Main.dc.html")
    open(p, "w", encoding="utf-8").write(POSTER)
    print(f"wrote {p}  ({os.path.getsize(p)/1024:.1f} KB)")
