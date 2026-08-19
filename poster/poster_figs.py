"""Generate poster-scale vector SVG for the conference poster.

Not a copy of the manuscript figures: these are redrawn for reading at
2-3 m -- heavy strokes, large type, no gridline clutter, series labelled
directly instead of in a legend box. Values come from the same sources the
manuscript uses (analytic R* for the threshold; the executed notebooks'
printed rel-L2 errors for the accuracy ladder).

    python3 poster_figs.py        # writes fig_threshold.svg, fig_accuracy.svg
"""

import math
import os

C_INK      = "#22262b"
C_MUTED    = "#8a9199"
C_ROUTE1   = "#1f4e8c"
C_ROUTE1L  = "#7fa9d8"
C_ROUTE2   = "#14796b"
C_HARDWARE = "#d2691e"
C_LIMIT    = "#b3261e"

OUT = os.path.dirname(os.path.abspath(__file__))
FS = "'IBM Plex Sans', system-ui, sans-serif"
FM = "'IBM Plex Mono', ui-monospace, monospace"


# ---------------------------------------------------------------- threshold
def fig_threshold():
    """Carleman order required vs Reynolds number. Diverges at Re = pi/2."""
    W, H = 1180, 800
    L, R, T, B = 150, 55, 70, 130
    pw, ph = W - L - R, H - T - B

    x0, x1 = 0.0, 2.30                       # room to the right of the wall
    ly0, ly1 = 0.0, math.log10(300)

    def X(re): return L + (re - x0) / (x1 - x0) * pw
    def Y(n):  return T + ph - (math.log10(max(n, 1.0)) - ly0) / (ly1 - ly0) * ph

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
         f'font-family={FS!r} role="img" aria-label="Required Carleman order '
         f'diverges as the Reynolds number approaches pi over two">']

    for n in (1, 10, 100):
        y = Y(n)
        s.append(f'<line x1="{L}" y1="{y:.1f}" x2="{L+pw}" y2="{y:.1f}" '
                 f'stroke="{C_MUTED}" stroke-opacity="0.30" stroke-width="1.5"/>')
        s.append(f'<text x="{L-18}" y="{y+10:.1f}" text-anchor="end" font-size="30" '
                 f'fill="{C_MUTED}" font-family={FM!r}>{n}</text>')

    xpi = X(math.pi / 2)
    s.append(f'<rect x="{xpi:.1f}" y="{T}" width="{L+pw-xpi:.1f}" height="{ph}" '
             f'fill="{C_LIMIT}" fill-opacity="0.06"/>')

    for eps, dash, op in ((1e-2, "none", 0.42), (1e-3, "14 9", 0.68), (1e-4, "4 8", 1.0)):
        pts, target = [], math.log(1 / eps)
        re = 0.02
        while re < math.pi / 2 - 0.004:
            n = target / math.log(math.pi / (2 * re))
            if 1 <= n <= 320:
                pts.append(f"{X(re):.1f},{Y(n):.1f}")
            re += 0.004
        s.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{C_ROUTE1}" '
                 f'stroke-opacity="{op}" stroke-width="6" stroke-dasharray="{dash}" '
                 f'stroke-linecap="round"/>')

    # compact legend, upper-left where the plot is empty
    lx, lyy = L + 34, T + 34
    for i, (dash, op, lab) in enumerate(((("none"), 0.42, "10⁻²"), ("14 9", 0.68, "10⁻³"),
                                         ("4 8", 1.0, "10⁻⁴"))):
        y = lyy + i * 44
        s.append(f'<line x1="{lx}" y1="{y}" x2="{lx+62}" y2="{y}" stroke="{C_ROUTE1}" '
                 f'stroke-opacity="{op}" stroke-width="6" stroke-dasharray="{dash}" '
                 f'stroke-linecap="round"/>')
        s.append(f'<text x="{lx+78}" y="{y+11}" font-size="30" fill="{C_INK}" '
                 f'font-family={FM!r}>ε = {lab}</text>')

    s.append(f'<line x1="{xpi:.1f}" y1="{T-6}" x2="{xpi:.1f}" y2="{T+ph}" '
             f'stroke="{C_LIMIT}" stroke-width="6"/>')
    s.append(f'<text x="{xpi+26:.1f}" y="{T+46}" font-size="34" font-weight="600" '
             f'fill="{C_LIMIT}">Re = π/2</text>')
    s.append(f'<text x="{xpi+26:.1f}" y="{T+88}" font-size="30" fill="{C_LIMIT}">≈ 1.57</text>')
    s.append(f'<text x="{xpi+26:.1f}" y="{T+ph-96}" font-size="29" fill="{C_LIMIT}">no finite</text>')
    s.append(f'<text x="{xpi+26:.1f}" y="{T+ph-60}" font-size="29" fill="{C_LIMIT}">order suffices</text>')
    s.append(f'<text x="{xpi+26:.1f}" y="{T+ph-24}" font-size="29" fill="{C_LIMIT}">past here</text>')

    s.append(f'<line x1="{L}" y1="{T+ph}" x2="{L+pw}" y2="{T+ph}" stroke="{C_INK}" stroke-width="3"/>')
    s.append(f'<line x1="{L}" y1="{T}" x2="{L}" y2="{T+ph}" stroke="{C_INK}" stroke-width="3"/>')
    for re in (0.0, 0.5, 1.0, 1.5, 2.0):
        s.append(f'<text x="{X(re):.1f}" y="{T+ph+48}" text-anchor="middle" font-size="30" '
                 f'fill="{C_INK}" font-family={FM!r}>{re:g}</text>')
    s.append(f'<text x="{L+pw/2:.1f}" y="{T+ph+100}" text-anchor="middle" font-size="33" '
             f'fill="{C_INK}">Reynolds number  Re = UL/ν</text>')
    s.append(f'<text x="40" y="{T+ph/2:.1f}" transform="rotate(-90 40 {T+ph/2:.1f})" '
             f'text-anchor="middle" font-size="33" fill="{C_INK}">required Carleman order</text>')
    s.append('</svg>')
    return "\n".join(s)


# ----------------------------------------------------------------- accuracy
def fig_accuracy():
    """Measured relative L2 error per timestep: ideal circuit vs device noise."""
    W, H = 1180, 800
    L, R, T, B = 175, 235, 78, 130
    pw, ph = W - L - R, H - T - B

    series = [  # label, colour, dashed?, values at steps 1..3
        ("KdV, ideal",      C_ROUTE2,   False, [1.50e-8, 1.18e-7, 2.41e-7]),
        ("Burgers, ideal",  C_ROUTE1,   False, [2.09e-6, 1.94e-6, 1.76e-6]),
        ("KdV, on device",  C_HARDWARE, True,  [0.0477, 0.0568, 0.0827]),
        ("Burgers, on device", C_HARDWARE, False, [0.1857, 0.1778, 0.2103]),
    ]
    ly0, ly1 = -9.0, 0.0

    def X(i): return L + (i + 0.5) / 3 * pw
    def Y(v): return T + ph - (math.log10(v) - ly0) / (ly1 - ly0) * ph

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
         f'font-family={FS!r} role="img" aria-label="Measured relative L2 error '
         f'per timestep, ideal circuit versus device noise">']

    for e in range(-8, 1, 2):
        y = Y(10.0 ** e)
        s.append(f'<line x1="{L}" y1="{y:.1f}" x2="{L+pw}" y2="{y:.1f}" '
                 f'stroke="{C_MUTED}" stroke-opacity="0.28" stroke-width="1.5"/>')
        s.append(f'<text x="{L-20}" y="{y+10:.1f}" text-anchor="end" font-size="29" '
                 f'fill="{C_MUTED}" font-family={FM!r}>10{_sup(e)}</text>')

    # band marking the noise-dominated decade
    s.append(f'<rect x="{L}" y="{Y(1.0):.1f}" width="{pw}" height="{Y(0.02)-Y(1.0):.1f}" '
             f'fill="{C_HARDWARE}" fill-opacity="0.06"/>')

    for lab, col, dashed, vals in series:
        pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(vals))
        s.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="6" '
                 f'stroke-linecap="round"'
                 + (' stroke-dasharray="13 10"' if dashed else '') + '/>')
        for i, v in enumerate(vals):
            s.append(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="11" fill="{col}"/>')
        s.append(f'<text x="{X(2)+26:.1f}" y="{Y(vals[-1])+10:.1f}" font-size="28" '
                 f'fill="{col}" font-weight="500">{lab}</text>')

    s.append(f'<line x1="{L}" y1="{T+ph}" x2="{L+pw}" y2="{T+ph}" stroke="{C_INK}" stroke-width="3"/>')
    s.append(f'<line x1="{L}" y1="{T}" x2="{L}" y2="{T+ph}" stroke="{C_INK}" stroke-width="3"/>')
    for i in range(3):
        s.append(f'<text x="{X(i):.1f}" y="{T+ph+48}" text-anchor="middle" font-size="30" '
                 f'fill="{C_INK}" font-family={FM!r}>{i+1}</text>')
    s.append(f'<text x="{L+pw/2:.1f}" y="{T+ph+100}" text-anchor="middle" font-size="33" '
             f'fill="{C_INK}">timestep</text>')
    s.append(f'<text x="42" y="{T+ph/2:.1f}" transform="rotate(-90 42 {T+ph/2:.1f})" '
             f'text-anchor="middle" font-size="33" fill="{C_INK}">relative L² error vs. classical</text>')
    s.append('</svg>')
    return "\n".join(s)


# -------------------------------------------------------------- propagation
def fig_propagation():
    """Two snapshots of the variational Burgers run: target, ideal, on-device.

    The point of this panel is shape, not error: the device curve still tracks
    the wave. Drawn from propagation_data.json (poster_propagation.py).
    """
    import json
    d = json.load(open(os.path.join(OUT, "propagation_data.json"), encoding="utf-8"))
    xs = d["x"] + [1.0]                                   # close the period
    def close(row): return row + [row[0]]
    steps = [(1, "t = 0.10"), (3, "t = 0.30")]

    W, H = 1440, 690
    pad_l, pad_r, pad_t, pad_b, gap = 108, 26, 132, 108, 78
    panel_w = (W - pad_l - pad_r - gap) / 2
    ph = H - pad_t - pad_b
    y0, y1 = -1.35, 1.35

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
         f'font-family={FS!r} role="img" aria-label="Variational Burgers propagation: '
         f'the on-device curve still tracks the classical target">']

    for k, (idx, label) in enumerate(steps):
        ox = pad_l + k * (panel_w + gap)
        def X(v): return ox + v / 1.0 * panel_w
        def Y(v): return pad_t + ph - (v - y0) / (y1 - y0) * ph

        s.append(f'<line x1="{ox}" y1="{Y(0):.1f}" x2="{ox+panel_w:.1f}" y2="{Y(0):.1f}" '
                 f'stroke="{C_MUTED}" stroke-opacity="0.45" stroke-width="1.5"/>')
        s.append(f'<text x="{ox+panel_w/2:.1f}" y="{pad_t-34}" text-anchor="middle" '
                 f'font-size="34" fill="{C_INK}" font-family={FM!r}>{label}</text>')

        cl = " ".join(f"{X(x):.1f},{Y(v):.1f}" for x, v in zip(xs, close(d["classical"][idx])))
        s.append(f'<polyline points="{cl}" fill="none" stroke="{C_MUTED}" stroke-width="26" '
                 f'stroke-opacity="0.5" stroke-linecap="round" stroke-linejoin="round"/>')

        qm = " ".join(f"{X(x):.1f},{Y(v):.1f}" for x, v in zip(xs, close(d["quantum"][idx])))
        s.append(f'<polyline points="{qm}" fill="none" stroke="{C_ROUTE2}" stroke-width="6" '
                 f'stroke-linecap="round" stroke-linejoin="round"/>')
        for x, v in zip(xs[:-1], d["quantum"][idx]):
            s.append(f'<circle cx="{X(x):.1f}" cy="{Y(v):.1f}" r="10" fill="{C_ROUTE2}"/>')

        nz = " ".join(f"{X(x):.1f},{Y(v):.1f}" for x, v in zip(xs, close(d["noisy"][idx])))
        s.append(f'<polyline points="{nz}" fill="none" stroke="{C_HARDWARE}" stroke-width="6" '
                 f'stroke-dasharray="4 12" stroke-linecap="round"/>')
        for x, v in zip(xs[:-1], d["noisy"][idx]):
            s.append(f'<rect x="{X(x)-9:.1f}" y="{Y(v)-9:.1f}" width="18" height="18" '
                     f'fill="{C_HARDWARE}"/>')

        s.append(f'<line x1="{ox}" y1="{pad_t+ph}" x2="{ox+panel_w:.1f}" y2="{pad_t+ph}" '
                 f'stroke="{C_INK}" stroke-width="3"/>')
        for xv in (0.0, 0.5, 1.0):
            s.append(f'<text x="{X(xv):.1f}" y="{pad_t+ph+46}" text-anchor="middle" '
                     f'font-size="29" fill="{C_INK}" font-family={FM!r}>{xv:g}</text>')
        s.append(f'<text x="{ox+panel_w/2:.1f}" y="{pad_t+ph+92}" text-anchor="middle" '
                 f'font-size="31" fill="{C_INK}">x</text>')

    # shared y axis on the first panel
    def Y0(v): return pad_t + ph - (v - y0) / (y1 - y0) * ph
    s.append(f'<line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{pad_t+ph}" '
             f'stroke="{C_INK}" stroke-width="3"/>')
    for v in (-1, 0, 1):
        s.append(f'<text x="{pad_l-18}" y="{Y0(v)+10:.1f}" text-anchor="end" font-size="29" '
                 f'fill="{C_INK}" font-family={FM!r}>{v}</text>')
    s.append(f'<text x="34" y="{pad_t+ph/2:.1f}" transform="rotate(-90 34 {pad_t+ph/2:.1f})" '
             f'text-anchor="middle" font-size="31" fill="{C_INK}">u(x, t)</text>')

    # inline key, top-left
    key = [(C_MUTED, "classical target", 14, 0.5), (C_ROUTE2, "ideal circuit", 6, 1.0),
           (C_HARDWARE, "fake_sherbrooke, 4000 shots", 6, 1.0)]
    kx, ky = pad_l - 60, 40
    for col, lab, wdt, op in key:
        s.append(f'<line x1="{kx}" y1="{ky}" x2="{kx+58}" y2="{ky}" stroke="{col}" '
                 f'stroke-width="{wdt}" stroke-opacity="{op}" stroke-linecap="round"/>')
        s.append(f'<text x="{kx+72}" y="{ky+10}" font-size="28" fill="{C_INK}">{lab}</text>')
        kx += 72 + len(lab) * 15 + 46

    s.append('</svg>')
    return "\n".join(s)



# ---------------------------------------------------------- lane pipeline
def _icon_group(icon_fn, x, y, size, color):
    """Splice a poster_icons.py icon (a standalone '<svg ...>...</svg>' string,
    itself free of any id= attribute -- see poster_icons.py's own note on why)
    into this diagram as a positioned <g>, rather than a nested <svg>, so it
    reads as one shape inline with everything else in this document."""
    raw = icon_fn(color, 64)
    inner = raw.split(">", 1)[1].rsplit("</svg>", 1)[0]
    scale = size / 64
    return f'<g transform="translate({x},{y}) scale({scale})">{inner}</g>'


def fig_lane_pipeline(color, boxes, W=980, box_h=118, arrow_gap=46,
                       title_fs=35, sub_px=27, ann_px=26):
    """One route's mechanism as boxes + arrows, not prose.

    `boxes` is a list of (title, subtitle_latex_or_None, annotation_latex_or_None,
    annotation_label_or_None, annotation_color_or_None, icon_fn_or_None). `title` and
    `annotation_label` are plain SVG text; `subtitle_latex` and
    `annotation_latex` are real TeX, rendered by matplotlib's mathtext engine
    (mathsvg_image) to Computer-Modern vector paths and embedded as <image>
    elements -- so "Re < pi/2" is actually typeset, not a literal '<' and a
    Greek letter sitting next to plain text. `icon_fn`, if given, is one of
    poster_icons.py's hand-drawn mechanism icons, drawn in the box's top-right
    corner; the box's step number (1-based) is drawn as a filled circle in
    the top-left corner, the numbered-badge convention used throughout.

    Same node names and cost annotations as the manuscript's Fig. 1 pipeline
    diagram, redrawn at poster scale so a reader a metre away can follow the
    mechanism without the paper in hand. Layout runs top to bottom with a
    single cursor `y`: each box (title plus, if present, its subtitle or
    annotation as a second line inside the same box), then an arrow to the
    next box -- nothing but the arrow sits between boxes.
    """
    from mathsvg import mathsvg_image

    def esc(t):
        return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") if t else t

    n = len(boxes)
    cx = W / 2
    parts = []
    y = 10

    for i, box in enumerate(boxes):
        title, sub_latex, ann_latex, ann_label, ann_color = box[:5]
        icon_fn = box[5] if len(box) > 5 else None
        title = esc(title)
        cy_box = y + box_h / 2
        parts.append(f'<rect x="20" y="{y}" width="{W-40}" height="{box_h}" rx="10" '
                     f'fill="#ffffff" stroke="{color}" stroke-width="4"/>')

        # Icon sits on the right, sized as a fraction of the box's own
        # height so it always fits regardless of box_h.
        right_edge = W - 20 - 18
        if icon_fn:
            isz = round(box_h * 0.66)
            icon_x = right_edge - isz
            icon_y = y + (box_h - isz) / 2
            parts.append(_icon_group(icon_fn, icon_x, icon_y, isz, color))
            zone_right = icon_x - 28
        else:
            zone_right = right_edge

        badge_scale = min(1.4, box_h / 118)
        bxr = round(20 * badge_scale)
        bfs = round(20 * badge_scale)
        bx = 20 + 14 + bxr
        by = y + 14 + bxr
        parts.append(f'<circle cx="{bx}" cy="{by}" r="{bxr}" fill="{color}"/>')
        parts.append(f'<text x="{bx}" y="{by+bfs*0.36:.1f}" text-anchor="middle" '
                     f'font-size="{bfs}" font-weight="700" fill="#ffffff" '
                     f'font-family={FM!r}>{i+1}</text>')
        zone_left = 20 + 14 + 2 * bxr + 20

        # Title and its detail (subtitle or cost annotation) read as one
        # continuous line -- not two separately anchored blocks -- centred
        # as a single group in the space between the badge and the icon.
        # There's no way to measure real rendered text width without a
        # browser, so both this and the label below estimate it from
        # character count at the font's typical advance width. If that
        # estimate says the pair won't fit the available zone, both fonts
        # are scaled down together until it does -- a fixed centring
        # formula on an unfitted estimate is exactly what let long titles
        # ("Natural-gradient descent" + its annotation) overflow past the
        # box's own left edge.
        ac = ann_color or C_MUTED
        gap = 34
        zone_w = max(40, zone_right - zone_left)

        def measure(t_fs, d_px):
            t_w = len(title) * t_fs * 0.56
            d_w = 0
            if sub_latex:
                _, d_w, _ = mathsvg_image(sub_latex, 0, 0, px=d_px, anchor="start")
            elif ann_latex:
                _, d_w, _ = mathsvg_image(ann_latex, 0, 0, px=d_px, anchor="start")
                if ann_label:
                    d_w += 14 + len(f"— {ann_label}") * d_px * 0.52
            elif ann_label:
                d_w = len(f"— {ann_label}") * d_px * 0.52
            return t_w, d_w

        title_fs_eff = round(title_fs * max(0.82, badge_scale))
        detail_px_eff = ann_px if (ann_latex or ann_label) else sub_px
        t_w, d_w = measure(title_fs_eff, detail_px_eff)
        total_w = t_w + (gap + d_w if d_w else 0)
        # Width scales roughly but not exactly linearly with font size (the
        # label-count estimate and the rendered-math width don't shrink at
        # quite the same rate), so one scale pass can undershoot -- iterate
        # a couple of times, each with a small safety margin, until it
        # actually fits rather than trusting a single linear correction.
        for _ in range(3):
            if total_w <= zone_w:
                break
            scale = max(0.5, (zone_w / total_w) * 0.95)
            title_fs_eff = max(15, round(title_fs_eff * scale))
            detail_px_eff = max(13, round(detail_px_eff * scale))
            t_w, d_w = measure(title_fs_eff, detail_px_eff)
            total_w = t_w + (gap + d_w if d_w else 0)

        start_x = max(zone_left, (zone_left + zone_right) / 2 - total_w / 2)

        parts.append(f'<text x="{start_x:.1f}" y="{cy_box+title_fs_eff*0.34:.1f}" '
                     f'text-anchor="start" font-size="{title_fs_eff}" '
                     f'font-weight="600" fill="{C_INK}">{title}</text>')
        detail_x = start_x + t_w + gap

        if sub_latex:
            img, _, _ = mathsvg_image(sub_latex, detail_x, cy_box, px=detail_px_eff,
                                      color=C_MUTED, anchor="start")
            parts.append(img)
        elif ann_latex and ann_label:
            img, w, h = mathsvg_image(ann_latex, detail_x, cy_box, px=detail_px_eff,
                                      color=ac, anchor="start")
            parts.append(img)
            label = esc(f"— {ann_label}")
            parts.append(f'<text x="{detail_x+w+14:.1f}" y="{cy_box+detail_px_eff*0.32:.1f}" '
                         f'text-anchor="start" font-size="{detail_px_eff}" '
                         f'font-style="italic" fill="{ac}">{label}</text>')
        elif ann_latex:
            img, _, _ = mathsvg_image(ann_latex, detail_x, cy_box, px=detail_px_eff,
                                      color=ac, anchor="start")
            parts.append(img)
        elif ann_label:
            parts.append(f'<text x="{detail_x:.1f}" y="{cy_box+detail_px_eff*0.32:.1f}" '
                         f'text-anchor="start" font-size="{detail_px_eff}" '
                         f'font-style="italic" fill="{ac}">{esc(ann_label)}</text>')
        y += box_h

        if i < n - 1:
            y += 16
            head_h = 30
            base_y = y + arrow_gap - head_h
            parts.append(f'<line x1="{cx}" y1="{y:.1f}" x2="{cx}" y2="{base_y:.1f}" '
                         f'stroke="{color}" stroke-width="10"/>')
            tip_y = y + arrow_gap
            parts.append(f'<polygon points="{cx-24},{base_y:.1f} {cx+24},{base_y:.1f} '
                         f'{cx},{tip_y:.1f}" fill="{color}"/>')
            y += arrow_gap

    H = y + 16
    svg = ([f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'font-family={FS!r} role="img" aria-label="Pipeline stages for this route">']
           + parts + ['</svg>'])
    return "\n".join(svg), H


import poster_icons as _pi

ROUTE1_BOXES = [
    ("Carleman lift", r"\dot{y} = Ay + b", None, None, None, _pi.icon_vector),
    ("Crank–Nicolson", None, r"\mathrm{Re} < \pi/2", "fundamental", C_LIMIT, _pi.icon_grid),
    ("Block encoding", None,
     r"\alpha \approx n_x^{\,N_C-1}\lambda_{\mathrm{cfl}}", "fixable", C_MUTED, _pi.icon_block_matrix),
    ("QSVT inversion", None, r"d = \tilde{O}(\kappa_Q)", "fixable", C_MUTED, _pi.icon_qsvt_response),
]

ROUTE2_BOXES = [
    ("Amplitude encode u", None, None, "no linear embedding", C_MUTED, _pi.icon_bloch),
    ("Per-step target", None, None, "Euler / midpoint", C_MUTED, _pi.icon_clock),
    ("Natural-gradient descent", None, r"150\times/\mathrm{step}",
     "iterate; nonconvex, residual calls", C_MUTED, _pi.icon_gradient),
]

ROUTE3_BOXES = [
    ("Laser array", r"\kappa = Ke^{i\varphi}", None, None, None, _pi.icon_circuit),
    ("Sakaguchi–Kuramoto", None, None, None, None, _pi.icon_gradient),
    ("Continuum limit", None,
     r"\nu_{\mathrm{eff}} = K_{\mathrm{eff}}a^2\cos\varphi", "Re is a dial", C_MUTED, _pi.icon_scale),
]


def _sup(e):
    m = {"-": "⁻", "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
         "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹"}
    return "".join(m[c] for c in str(e))


if __name__ == "__main__":
    gens = [("fig_threshold.svg", fig_threshold), ("fig_accuracy.svg", fig_accuracy)]
    if os.path.exists(os.path.join(OUT, "propagation_data.json")):
        gens.append(("fig_propagation.svg", fig_propagation))
    for name, gen in gens:
        p = os.path.join(OUT, name)
        open(p, "w", encoding="utf-8").write(gen())
        print(f"wrote {p}  ({os.path.getsize(p)/1024:.1f} KB)")
