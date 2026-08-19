"""Small hand-drawn-style workflow icons for the poster's mechanism diagrams.

Decorative single-symbol markers (rocket, target, warning, trophy, ...) are
just literal emoji in poster_build.py -- no need to draw those. What needs
actual drawing is the small multi-stroke DIAGRAMS that stand in for a
concept inside a workflow step: a continuous field, a discretised grid, a
state vector, a Bloch sphere, a tiny circuit, a natural-gradient contour, a
block-encoded matrix, a QSVT response curve. All stroke-based, one colour,
sized to sit inside an ~90-110px step box.
"""

INK = "#1f4e8c"


def icon_field(color=INK, size=64):
    """A continuous wavy field u(x) with axes."""
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 64 64" fill="none">
  <path d="M6 54 H58 M6 54 V8" stroke="{color}" stroke-width="1.6" stroke-linecap="round"/>
  <path d="M10 40 Q18 16 28 34 T48 20" stroke="{color}" stroke-width="2.2"
        fill="none" stroke-linecap="round"/>
</svg>'''


def icon_grid(color=INK, size=64):
    """A discretised line: open endpoints, filled interior nodes."""
    xs = [8, 18, 28, 38, 48, 58]
    dots = "".join(
        f'<circle cx="{x}" cy="32" r="3.4" '
        f'fill="{"none" if i in (0, len(xs)-1) else color}" '
        f'stroke="{color}" stroke-width="1.6"/>'
        for i, x in enumerate(xs))
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 64 64" fill="none">'
           f'<line x1="8" y1="32" x2="58" y2="32" stroke="{color}" stroke-width="1.4" '
           f'stroke-dasharray="1 3.5"/>{dots}</svg>')


def icon_vector(color=INK, size=64, n=4):
    """A bracketed column vector, [u1 ... un]^T."""
    rows = "".join(
        f'<circle cx="32" cy="{16+i*11}" r="2" fill="{color}"/>' for i in range(n))
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 64 64" fill="none">
  <path d="M22 10 H16 V54 H22" stroke="{color}" stroke-width="1.8" fill="none"/>
  <path d="M42 10 H48 V54 H42" stroke="{color}" stroke-width="1.8" fill="none"/>
  {rows}
</svg>'''


def icon_bloch(color=INK, size=64):
    """A Bloch sphere: circle, equator ellipse, axis, state dot."""
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 64 64" fill="none">
  <circle cx="32" cy="32" r="22" stroke="{color}" stroke-width="1.6"/>
  <ellipse cx="32" cy="32" rx="22" ry="7" stroke="{color}" stroke-width="1.2" opacity="0.55"/>
  <line x1="32" y1="8" x2="32" y2="56" stroke="{color}" stroke-width="1.2" opacity="0.55"/>
  <line x1="32" y1="32" x2="46" y2="20" stroke="{color}" stroke-width="2"/>
  <circle cx="46" cy="20" r="3" fill="{color}"/>
</svg>'''


def icon_circuit(color=INK, size=64):
    """Two qubit wires, a couple of gates, one entangler."""
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 64 64" fill="none">
  <line x1="6" y1="22" x2="58" y2="22" stroke="{color}" stroke-width="1.4"/>
  <line x1="6" y1="42" x2="58" y2="42" stroke="{color}" stroke-width="1.4"/>
  <rect x="14" y="14" width="16" height="16" rx="3" stroke="{color}" stroke-width="1.8" fill="white"/>
  <rect x="34" y="34" width="16" height="16" rx="3" stroke="{color}" stroke-width="1.8" fill="white"/>
  <line x1="22" y1="30" x2="22" y2="42" stroke="{color}" stroke-width="1.6"/>
  <circle cx="22" cy="42" r="2.6" fill="{color}"/>
</svg>'''


def icon_gradient(color=INK, size=64):
    """Natural-gradient descent: nested contours, arrow spiralling in.

    No <marker>/<defs> with an id -- every icon on the page shares one
    document, and a repeated id is exactly the bug that once made the
    equations disappear (see mathsvg.py). The arrowhead is drawn as a
    plain filled polygon instead.
    """
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 64 64" fill="none">
  <ellipse cx="32" cy="34" rx="24" ry="17" stroke="{color}" stroke-width="1.3" opacity="0.4"/>
  <ellipse cx="32" cy="34" rx="16" ry="11" stroke="{color}" stroke-width="1.3" opacity="0.65"/>
  <ellipse cx="32" cy="34" rx="8" ry="5.5" stroke="{color}" stroke-width="1.4"/>
  <path d="M12 14 Q22 22 25.5 29" stroke="{color}" stroke-width="2" fill="none"
        stroke-linecap="round"/>
  <polygon points="25.5,29 20.5,26.5 24,33.5" fill="{color}"/>
  <circle cx="32" cy="34" r="2" fill="{color}"/>
</svg>'''


def icon_clock(color=INK, size=64):
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 64 64" fill="none">
  <circle cx="32" cy="32" r="22" stroke="{color}" stroke-width="1.8"/>
  <path d="M32 20 V32 L42 38" stroke="{color}" stroke-width="2.2" fill="none"
        stroke-linecap="round" stroke-linejoin="round"/>
</svg>'''


def icon_block_matrix(color=INK, size=64):
    """A block-structured matrix bracket."""
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 64 64" fill="none">
  <path d="M16 8 H8 V56 H16" stroke="{color}" stroke-width="1.8" fill="none"/>
  <path d="M48 8 H56 V56 H48" stroke="{color}" stroke-width="1.8" fill="none"/>
  <rect x="20" y="12" width="12" height="12" stroke="{color}" stroke-width="1.4" fill="none"/>
  <rect x="34" y="12" width="10" height="12" stroke="{color}" stroke-width="1.2" fill="none" opacity="0.5"/>
  <rect x="20" y="26" width="12" height="10" stroke="{color}" stroke-width="1.2" fill="none" opacity="0.5"/>
  <rect x="34" y="26" width="10" height="10" stroke="{color}" stroke-width="1.4" fill="none"/>
  <line x1="20" y1="42" x2="44" y2="42" stroke="{color}" stroke-width="1" stroke-dasharray="1 3" opacity="0.6"/>
  <rect x="20" y="46" width="24" height="6" stroke="{color}" stroke-width="1.2" fill="none" opacity="0.5"/>
</svg>'''


def icon_qsvt_response(color=INK, size=64):
    """A polynomial response curve approximating 1/x -- the QSVT signature."""
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 64 64" fill="none">
  <path d="M6 54 H58 M6 54 V8" stroke="{color}" stroke-width="1.4" stroke-linecap="round" opacity="0.6"/>
  <path d="M10 14 C 16 14, 18 46, 32 46 S 48 14, 54 14" stroke="{color}"
        stroke-width="2.2" fill="none" stroke-linecap="round"/>
</svg>'''


def icon_scale(color=INK, size=64):
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 64 64" fill="none">
  <line x1="32" y1="8" x2="32" y2="52" stroke="{color}" stroke-width="2" stroke-linecap="round"/>
  <line x1="12" y1="18" x2="52" y2="18" stroke="{color}" stroke-width="2" stroke-linecap="round"/>
  <path d="M12 18 L6 34 A8 6 0 0 0 18 34 Z" stroke="{color}" stroke-width="1.6" fill="none"/>
  <path d="M52 18 L46 34 A8 6 0 0 0 58 34 Z" stroke="{color}" stroke-width="1.6" fill="none"/>
  <line x1="22" y1="54" x2="42" y2="54" stroke="{color}" stroke-width="2" stroke-linecap="round"/>
</svg>'''


def icon_shield(color=INK, size=64, check=True):
    inner = ('<path d="M24 32 L30 38 L42 24" stroke="white" stroke-width="3" fill="none" '
            'stroke-linecap="round" stroke-linejoin="round"/>' if check else
            '<line x1="24" y1="24" x2="40" y2="40" stroke="white" stroke-width="3" stroke-linecap="round"/>'
            '<line x1="40" y1="24" x2="24" y2="40" stroke="white" stroke-width="3" stroke-linecap="round"/>')
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 64 64" fill="none">
  <path d="M32 6 L54 14 V30 C54 44 44 54 32 58 C20 54 10 44 10 30 V14 Z"
        fill="{color}" stroke="{color}" stroke-width="1.5"/>
  {inner}
</svg>'''
