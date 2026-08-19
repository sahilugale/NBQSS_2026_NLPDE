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
FIG_QR_LARGE = FIG_QR.replace(
    '<svg xmlns="http://www.w3.org/2000/svg" width="37" height="37">',
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 37 37" '
    'style="width:100%;height:100%;display:block">',
    1,
)

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


def chip(emoji, text, color=INK, bg="#ffffff"):
    """A short punchy emoji + one-liner callout, the witty-caption convention
    from the reference poster -- a quick aside a reader catches in passing,
    not another paragraph to read. `emoji` may be "" to skip the icon
    entirely, for text that doesn't have a clean one-glyph symbol."""
    icon = f'<span style="font-size:26px;line-height:1">{emoji}</span>' if emoji else ""
    return (f'<div style="display:inline-flex;align-items:center;gap:9px;'
            f'background:{bg};border:2px solid {color};border-radius:999px;'
            f'padding:6px 18px 6px 12px;width:fit-content">'
            f'{icon}'
            f'<span style="font-family:{MONO};font-size:21px;font-style:italic;'
            f'color:{color}">{text}</span></div>')


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


def lane(color, tag, title, boxes, price, price_unit, price_note, measured, quip):
    # box_h/gaps trimmed from the figure defaults -- three of these stack in
    # one narrow column now (not side by side across the full sheet), so the
    # diagram has to earn its height back or the column runs longer than its
    # neighbours.
    # W is wide relative to box_h -- landscape boxes that extend horizontally
    # without the vertical growth that kept pushing the footer off the page.
    svg, _ = _pf.fig_lane_pipeline(color, boxes, W=1360, box_h=126, arrow_gap=48,
                                    title_fs=46, sub_px=33, ann_px=30)
    # Deterministic sizing: cap the SVG's rendered WIDTH and let height follow
    # the viewBox aspect ratio (auto), rather than stretching to fill the
    # column. That keeps box/font size visually identical across all three
    # lanes regardless of how many pipeline stages each one has -- a lane
    # with fewer stages is simply a shorter diagram, not a stretched one.
    svg = svg.replace("<svg ",
      '<svg style="width:100%;max-width:700px;height:auto;display:block" ', 1)
    badge = "measured" if measured else "projected"
    badge_bg = INK if measured else MUTED
    return f"""
    <div style="flex:none;display:flex;flex-direction:column;background:{CARD};
                border:2px solid {RULE};border-top:10px solid {color}">
      <div style="padding:16px 26px 0;display:flex;flex-direction:column;gap:10px">
        <div style="display:flex;flex-direction:column;gap:4px">
          <div style="font-family:{MONO};font-size:25px;letter-spacing:.14em;
                      text-transform:uppercase;color:{color}">{tag}</div>
          <div style="font-family:{SERIF};font-size:42px;font-weight:600;color:{INK};
                      line-height:1.1">{title}</div>
        </div>
        <div style="display:flex;align-items:center;justify-content:center">{svg}</div>
        {quip}
      </div>
      <div style="margin-top:auto;display:flex;align-items:baseline;gap:18px;
                  padding:14px 26px 16px;border-top:2px solid {RULE};background:#f7f5f1">
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
         "needs a fault-tolerant computer, not built yet", False,
         chip("⏳", "waits on hardware that doesn't exist yet", BLUE))
    + lane(TEAL, "Route 2 · refuse the toll", "Variational propagation", _pf.ROUTE2_BOXES,
           "351", "gates, 6 qubits",
           "small enough to run on real hardware today", True,
           chip("✅", "already runs, today, on a real chip", TEAL))
    + lane(ORANGE, "Route 3 · change the hardware", "Degenerate cavity laser", _pf.ROUTE3_BOXES,
           "0", "gates",
           "no circuit at all &mdash; but it solves one equation", False,
           chip("💡", "no circuit at all &mdash; the physics does the work", ORANGE))
)

# Each entry: (logo basename in logos/, fallback label). The basename is
# matched against ANY extension actually present (png/jpg/jpeg/webp/svg), so
# it doesn't matter which format each institution's mark arrived in. If no
# file matches, a dashed placeholder with the label is drawn instead, so the
# poster always builds either way.
LOGO_SPECS = [
    ("citystgeorges",  "City St George&rsquo;s<br>Univ. of London"),
    ("technion",       "Technion &mdash; Israel<br>Institute of Technology"),
    ("sfu",            "Simon Fraser<br>University"),
    ("juelich",        "Forschungszentrum<br>J&uuml;lich &middot; PGI-8"),
    ("koeln",          "University<br>of Cologne"),
    ("weizmann",       "Weizmann Institute<br>of Science"),
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

# The DDCL platform's near-/far-field images (from the manuscript, reproduced from
# the platform paper).
_ddcl1_uri = _img_data_uri(os.path.join(HERE, "..", "prx_quantum", "figures", "ddcl_1.png"),
                           max_dim=460)
_ddcl2_uri = _img_data_uri(os.path.join(HERE, "..", "prx_quantum", "figures", "ddcl_2.png"),
                           max_dim=460)

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
            display:flex;flex-direction:column;gap:18px;position:relative">

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
        <sup>3</sup>Technion &mdash; Israel Institute of Technology &nbsp;
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

  </section>

  <!-- ========================= three columns ======================= -->
  <div style="display:grid;grid-template-columns:1400px 1430px 1380px;gap:36px;flex:1">

    <!-- ---------------- column A ---------------- -->
    <div style="display:flex;flex-direction:column;gap:20px">
          <div style="font-family:{MONO};font-size:44px;font-weight:700;letter-spacing:.06em;
            text-transform:uppercase;color:{MUTED}"
          >Motivation &amp; context</div>
      {panel("1", "What is the problem?", BLUE,
                 "Two nonlinear PDEs, one quantum bottleneck",
                 "Quantum hardware evolves states linearly, while fluid equations contain "
                 "nonlinear self-interaction. The two benchmark equations make the problem concrete:",
             f'''
          <div style="display:flex;flex-direction:column;gap:18px">
            <div style="background:#eef2f8;border-left:8px solid {BLUE};padding:20px 24px;
                        display:flex;align-items:center;gap:26px">
              <img src="{_img_data_uri(os.path.join(HERE,"figures","poster_carpet_burgers.png"), max_dim=960, jpeg=True)}"
                   alt="Burgers carpet plot: a sine wave steepening into a shock"
                   style="width:561px;height:480px;object-fit:contain;display:block;flex:none">
              <div style="display:flex;flex-direction:column;gap:11px">
                <div style="font-family:{MONO};font-size:23px;font-weight:600;letter-spacing:.08em;
                            text-transform:uppercase;color:{BLUE}">Viscous Burgers</div>
                <div style="font-family:{SERIF};font-size:43px;font-weight:600;color:{INK};
                            line-height:1.2;white-space:nowrap">∂ₜu + u∂ₓu = ν∂ₓₓu</div>
                <div style="font-size:24px;line-height:1.3;color:{MUTED}">Dissipative: viscosity fights the steepening.</div>
              </div>
        </div>
            <div style="background:#fdf1e6;border-left:8px solid {ORANGE};padding:20px 24px;
                        display:flex;align-items:center;gap:26px">
              <img src="{_img_data_uri(os.path.join(HERE,"figures","poster_carpet_kdv.png"), max_dim=960, jpeg=True)}"
                   alt="KdV carpet plot: a pulse splitting into a soliton and ripples"
                   style="width:573px;height:480px;object-fit:contain;display:block;flex:none">
              <div style="display:flex;flex-direction:column;gap:11px">
                <div style="font-family:{MONO};font-size:23px;font-weight:600;letter-spacing:.08em;
                            text-transform:uppercase;color:{ORANGE}">Korteweg&ndash;de Vries (KdV)</div>
                <div style="font-family:{SERIF};font-size:41px;font-weight:600;color:{INK};
                            line-height:1.2;white-space:nowrap">∂ₜu + u∂ₓu + δ∂ₓₓₓu = 0</div>
                <div style="font-size:24px;line-height:1.3;color:{MUTED}">Conservative: dispersion redistributes energy.</div>
              </div>
            </div>
          </div>''')}

            {panel("2", "Why is it hard?", RED,
              "Nonlinearity, physics, resources, and readout all become part of the cost.",
              "The quadratic term cannot be applied as a unitary gate; discretization must "
              "preserve dissipation or conservation; embedding, block encoding, QSVT degree, "
              "and readout compound.",
              f'''<div style="display:grid;grid-template-columns:250px 1fr;gap:14px 18px;
                  align-items:center;font-size:25px;line-height:1.28;color:{BODY}">
         <b>NONLINEARITY</b><span>{mathsvg(r"u\otimes u\notin\mathcal{U}", 34, color=INK)}</span>
         <b>PHYSICS</b><span>{mathsvg(r"u^\top F_2(u\otimes u)=0", 32, color=INK)}</span>
         <b>RESOURCES</b><span>embedding, encoding, degree, post-selection</span>
         <b>READOUT</b><span>compression does not return the full field</span>
            </div>''')}

      <div style="background:{INK};color:#f7f6f3;padding:22px 26px;
          display:flex;flex-direction:column;gap:10px;flex:none">
        <div style="display:flex;align-items:center;gap:14px">
          {icon_target("#7fa9d8", 40)}
            <div style="font-family:{MONO};font-size:27px;font-weight:600;letter-spacing:.16em;
            text-transform:uppercase;color:#cbd3dd">Current solutions available</div>
    </div>
    <ul style="font-size:22px;line-height:1.24;display:flex;flex-direction:column;gap:7px">
      <li><b style="color:#dfe3e8">CLASSICAL CFD</b> &mdash; still the default in practice:
        mature and well-understood, but cost explodes with resolution and dimension.</li>
      <li><b style="color:#7fa9d8">QUANTUM LINEAR SOLVERS</b> &mdash; promise big speedups
        for linear problems; nonlinearity still needs a workaround like ours.</li>
      <li><b style="color:#7fd0c2">VARIATIONAL QUANTUM ALGORITHMS</b> &mdash; an active
        line of work across many groups: shallow circuits, classical optimizer, runs today.</li>
      <li><b style="color:#c9a6e0">QUANTUM LATTICE METHODS</b> &mdash; recast the fluid as
        collide-and-stream rules that map more naturally onto quantum gates; still early.</li>
      <li><b style="color:#e0a064">ANALOG PHYSICAL SIMULATORS</b> &mdash; a device whose own
        physics obeys the target equation; no circuit, but limited to a matching equation.</li>
        </ul>
      </div>
    </div>

    <!-- ---------------- column B : the wall ---------------- -->
    <div style="display:flex;flex-direction:column;gap:20px">
      <div style="font-family:{MONO};font-size:44px;font-weight:700;letter-spacing:.06em;
                  text-transform:uppercase;color:{MUTED}">Our work</div>
      <div style="display:flex;flex-direction:column;gap:14px;flex:1;
                  justify-content:flex-start;margin-left:25px;margin-right:25px">
        {HERO_LANES}
      </div>

      <div style="border:3px solid {INK};padding:24px 28px;display:flex;
                  flex-direction:column;gap:12px;margin-left:25px;margin-right:25px">
        <div style="display:flex;align-items:center;gap:12px">
          {icon_warning(RED, 36)}
          <div style="font-family:{MONO};font-size:25px;letter-spacing:.14em;
                      text-transform:uppercase;color:{MUTED}">Where this breaks down</div>
        </div>
        <ul style="font-size:27px;line-height:1.36;color:{BODY};display:flex;
                   flex-direction:column;gap:9px">
          <li>Burgers has a well-known shortcut solution, so it can't prove a method
              handles hard nonlinear physics &mdash; that's why we insisted on KdV, too,
              which has no such shortcut.</li>
          <li>The classical optimiser can get stuck, and isn't guaranteed to find
              the right answer every time.</li>
          <li>The gate counts we measured reflect how we happened to build the
              circuit, not a hard limit &mdash; a smarter construction should do
              much better.</li>
          <li>These results are for a 1D fluid; a genuine speed advantage would need
              a much richer, higher-dimensional problem.</li>
        </ul>
      </div>
    </div>

    <!-- ---------------- column C : results ---------------- -->
    <div style="display:flex;flex-direction:column;gap:20px">
      <div style="font-family:{MONO};font-size:44px;font-weight:700;letter-spacing:.06em;
                  text-transform:uppercase;color:{MUTED}">Results</div>
      {panel("3", "Result &mdash; the wall", RED,
             "Only works for gentle flows",
             "There is a hard speed limit built into the maths: past a certain point "
             "(how fast the fluid moves, relative to how much it resists that motion), "
             "this approach simply stops being provably correct, no matter how much "
             "computer you throw at it.",
             f'''
      {figbox(FIG_THRESHOLD, 360)}
      <div style="border-top:3px solid {INK};padding-top:20px;display:flex;
                  flex-direction:column;gap:12px">
        <div style="font-size:27px;color:{BODY}">
          Even inside that safe zone, the honest price for one worked example:</div>
        <div style="display:flex;align-items:flex-end;gap:34px">
          <div style="display:flex;flex-direction:column">
            <span style="font-family:{MONO};font-size:92px;font-weight:600;color:{BLUE};
                         line-height:1">1.3&times;10<sup style="font-size:50px">12</sup></span>
            <span style="font-size:29px;color:{BODY}">quantum steps needed</span></div>
          <span style="font-size:48px;color:#8a9199;padding-bottom:30px">vs</span>
          <div style="display:flex;flex-direction:column">
            <span style="font-family:{MONO};font-size:92px;font-weight:600;color:{INK};
                         line-height:1">4.4&times;10<sup style="font-size:50px">6</sup></span>
            <span style="font-size:29px;color:{BODY}">steps on an ordinary laptop</span></div>
          <div style="margin-left:auto;text-align:right;font-size:27px;line-height:1.38;
                      color:{MUTED};max-width:340px">
            Roughly a day and a half on a future fault-tolerant machine, versus
            about a millisecond today.</div>
        </div>
        {chip("", "an honest wall, not a workaround", RED)}
      </div>''')}
      {panel("4", "Result &mdash; the way out", TEAL,
             "Skip the expensive step entirely",
             "A small quantum circuit holds a snapshot of the fluid, and a classical "
             "optimiser nudges it forward one step at a time &mdash; the wave's shape "
             "still comes through clearly on real hardware, steepening included.",
             f'''
      {figbox(FIG_PROPAGATION, 260)}
      {chip("🚀", "runs today, on real qubits", TEAL)}''')}

      {panel("5", "Result &mdash; the analog stand-in", ORANGE,
             "Seen through the cavity",
             "The programmable laser array itself: individual sites near-field (left), and "
             "the far-field pattern that reports how coherently they lock together (right) "
             "&mdash; the physical stand-in for solving the equation.",
             f'''
      <div style="display:flex;gap:16px;justify-content:center">
        <img src="{_ddcl1_uri}" alt="DDCL near-field: individual programmable laser sites"
             style="height:220px;width:370px;object-fit:cover;border:1px solid {RULE}">
        <img src="{_ddcl2_uri}" alt="DDCL far-field: collective coherence of the array"
             style="height:220px;width:370px;object-fit:cover;border:1px solid {RULE}">
      </div>
      {chip("🔬", "physics, not silicon, does the computing", ORANGE)}''')}
    </div>
  </div>

  <!-- ============================ footer =========================== -->
  <footer style="display:flex;flex-direction:column;gap:20px;
                 border-top:6px solid {INK};padding-top:22px;margin-bottom:150px">
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:34px;align-items:stretch">
      <div style="flex:1;display:flex;flex-direction:column;gap:8px">
        <div style="font-family:{MONO};font-size:24px;font-weight:600;letter-spacing:.14em;
                    text-transform:uppercase;color:{MUTED}">References</div>
        <div style="font-size:19px;line-height:1.32;color:{BODY}">
          1. Setty, <i>J. Phys. A</i> 59, 185303 (2026) &nbsp; 2. Setty, arXiv:2508.21667 (2025)<br>
          3. Liu et al., <i>PNAS</i> 118, e2026805118 (2021) &nbsp; 4. Forets &amp; Pouly, arXiv:1711.02552 (2017)<br>
          5. Wu et al., <i>SIAM J. Sci. Comput.</i> 47, A943 (2025) &nbsp; 6. Gonzalez-Conde et al., <i>PRResearch</i> 7, 023254 (2025)<br>
          7. Gily&eacute;n et al., STOC 2019 &nbsp; 8. Yuan et al., <i>Quantum</i> 3, 191 (2019)<br>
          9. Mitarai et al., <i>PRA</i> 98, 032309 (2018) &nbsp; 10. Costa et al., <i>npj Quantum Inf.</i> 11, 141 (2025)<br>
          11. Shende et al., IEEE TCAD 25, 1000 (2006) &nbsp; 12. NBQSS 2026 DDCL platform
        </div>
      </div>
      <div style="display:flex;flex-direction:column;gap:8px;
                  border-left:3px solid {RULE};padding-left:28px">
        <div style="display:flex;align-items:center;gap:12px">
          {icon_star(BLUE, 34)}
          <div style="font-family:{MONO};font-size:34px;font-weight:600;letter-spacing:.14em;
                      text-transform:uppercase;color:{BLUE}">Take home</div>
        </div>
        <div style="font-size:30px;line-height:1.32;color:{BODY}">
          <b>Memory:</b> linear embedding buys exponential compression, at a real cost.<br>
          <b>Limit:</b> Carleman convergence sets a hard wall, not just a hard problem.<br>
          <b>Today:</b> variational propagation already fits on shallow hardware.<br>
          <b>Physics:</b> the DDCL laser shows the equation can be built, not just simulated.
        </div>
      </div>
      <div style="display:flex;flex-direction:column;align-items:flex-start;gap:8px;
                  border-left:3px solid {RULE};padding-left:28px">
        <div style="font-family:{MONO};font-size:24px;font-weight:600;letter-spacing:.14em;
                    text-transform:uppercase;color:{MUTED}">Scan for code</div>
        <div style="display:flex;align-items:center;gap:18px">
            <div style="width:130px;height:130px;flex:none">{FIG_QR_LARGE}</div>
          <div style="display:flex;flex-direction:column;gap:8px">
            <div style="font-size:27px;font-weight:600;color:{INK};white-space:nowrap">Code, notebooks &amp; manuscript</div>
            <div style="font-family:{MONO};font-size:21px;line-height:1.34;color:{BLUE};white-space:nowrap">
              github.com/sahilugale/NBQSS_2026_NLPDE</div>
          </div>
        </div>
      </div>
    </div>
  </footer>

  <!-- ========================== logo band ========================== -->
  <div style="position:absolute;left:100px;right:100px;bottom:0;
              display:flex;align-items:center;gap:80px;background:{PAPER};
              border-top:6px solid {INK};padding-top:12px;padding-bottom:10px">
{LOGO_SLOTS}
    <div style="flex:none;padding-left:26px">
      <img src="{_nbqss_logo_uri}" alt="Niels Bohr Quantum Summer School 2026,
           Center for Quantum Mathematics, University of Southern Denmark"
           style="flex:none;width:104px;height:104px;border-radius:12px;object-fit:cover">
    </div>
  </div>
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
