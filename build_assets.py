#!/usr/bin/env python3
"""Generate the SVG figures for the profile README.

Direction: a printed chess score sheet annotated in coloured pencil.
  • Paper + ink base, then FOUR inks, each with one job:
      red   #A63A2B  the result — figure numbers, marks
      blue  #1F4E6E  the screen — anything the user touches
      green #2F6B4A  the API — server, data, infra; also the path off the board
      gold  #9A6B12  the clock — habits, hobbies, the part of the day that isn't work
  • Georgia = display + prose. Mono = labels, notation, data. Nothing else.
  • Zero border radius, zero shadows, zero gradients, zero emoji, no icons.
Run: python3 build_assets.py
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent

PAPER = "#F2EEE2"   # dominant neutral
PAPER2 = "#E6E0CE"  # one supporting tone, used only for board light squares
INK = "#15171A"
GRAPH = "#5C6058"   # secondary text
RULE = "#C6C0AE"    # hairlines
ACC = "#A63A2B"     # red ink: notation, annotations, the result
SCREEN = "#1F4E6E"  # blue ink: client / mobile / web
API = "#2F6B4A"     # green ink: server / data / infra
GOLD = "#9A6B12"    # gold ink: off the clock
INK_SOFT = "#AEB3A8"
BOARD = "#1B3446"   # board dark squares — prussian, not black

SERIF = "Georgia,'Times New Roman',Times,serif"
MONO = "ui-monospace,'SF Mono',Consolas,'Liberation Mono',Menlo,monospace"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def T(x, y, s, size, fill, font=SERIF, weight=None, ls=None, anchor=None,
      italic=False, opacity=None):
    a = [f'x="{x}"', f'y="{y}"', f'font-family="{font}"', f'font-size="{size}"',
         f'fill="{fill}"']
    if weight:
        a.append(f'font-weight="{weight}"')
    if ls is not None:
        a.append(f'letter-spacing="{ls}"')
    if anchor:
        a.append(f'text-anchor="{anchor}"')
    if italic:
        a.append('font-style="italic"')
    if opacity is not None:
        a.append(f'opacity="{opacity}"')
    return f'  <text {" ".join(a)}>{esc(s)}</text>'


def L(x1, y1, x2, y2, stroke=RULE, sw=1):
    return f'  <path d="M{x1} {y1}H{x2}V{y2}" fill="none" stroke="{stroke}" stroke-width="{sw}"/>' \
        if (x2 == x1 or y2 == y1) else \
        f'  <path d="M{x1} {y1}L{x2} {y2}" stroke="{stroke}" stroke-width="{sw}"/>'


def H(x1, x2, y, stroke=RULE, sw=1):
    return f'  <path d="M{x1} {y}H{x2}" stroke="{stroke}" stroke-width="{sw}"/>'


def V(y1, y2, x, stroke=RULE, sw=1):
    return f'  <path d="M{x} {y1}V{y2}" stroke="{stroke}" stroke-width="{sw}"/>'


def R(x, y, w, h, fill, stroke=None, sw=1):
    s = f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"'
    if stroke:
        s += f' stroke="{stroke}" stroke-width="{sw}"'
    return s + "/>"


def board(x, y, size, dark=INK, light=PAPER2, sw=1):
    """A real 8x8 board: dark squares + internal grid, 1px ink keyline."""
    cell = size / 8
    out = [R(x, y, size, size, light)]
    for r in range(8):
        for c in range(8):
            if (r + c) % 2 == 1:
                out.append(f'  <rect x="{x + c * cell:g}" y="{y + r * cell:g}" '
                           f'width="{cell:g}" height="{cell:g}" fill="{dark}"/>')
    for i in range(1, 8):
        out.append(V(y, y + size, f"{x + i * cell:g}", INK, sw))
        out.append(H(x, x + size, f"{y + i * cell:g}", INK, sw))
    out.append(f'  <rect x="{x}" y="{y}" width="{size}" height="{size}" fill="none" '
               f'stroke="{INK}" stroke-width="2"/>')
    return out


def path(d, stroke=ACC, sw=3, arrow=None, end_square=None):
    out = [f'  <path d="{d}" fill="none" stroke="{stroke}" stroke-width="{sw}" '
           f'stroke-linecap="square" stroke-linejoin="miter"/>']
    if end_square:
        ex, ey = end_square
        out.append(f'  <rect x="{ex - 5}" y="{ey - 5}" width="10" height="10" fill="{stroke}"/>')
    return out


def colorbar(x, y, unit=26, h=6, colors=(SCREEN, API, ACC, GOLD), reg=True):
    """A printer's registration bar: one solid segment per ink in the sheet."""
    out = []
    if reg:
        out.append(R(x - 13, y - 1, 7, 7, INK))
    for i, c in enumerate(colors):
        out.append(R(x + i * (unit + 4), y, unit, h, c))
    return out


def spans(x, y, size, parts, font=MONO, weight="700", ls=None):
    """One text run, coloured per fragment: parts = [(text, fill), ...]."""
    a = [f'x="{x}"', f'y="{y}"', f'font-family="{font}"', f'font-size="{size}"']
    if weight:
        a.append(f'font-weight="{weight}"')
    if ls is not None:
        a.append(f'letter-spacing="{ls}"')
    inner = "".join(f'<tspan fill="{c}">{esc(t)}</tspan>' for t, c in parts)
    return f'  <text {" ".join(a)}>{inner}</text>'


def fig(w, h, body, label):
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">',
        R(0, 0, w, h, PAPER),
        R(0.5, 0.5, w - 1, h - 1, "none", RULE),
        *body,
        "</svg>",
        "",
    ])


def masthead(w, left, right, y=52, x=64, rule_y=72, ink=ACC, indent=0):
    """Mono ID bar: coloured figure number, graphite note, tinted hairline."""
    out = [T(x + indent, y, left, 12, ink, MONO, "700", 2.4),
           T(w - x, y, right, 11, GRAPH, MONO, None, 1.9, "end"),
           H(x, w - x, rule_y, ink, 1)]
    return out


# ─────────────────────────────────────────────── MARKS (16×16, one ink) ──
# Every mark is drawn for this sheet: same 16px box, 1.5px stroke, single
# colour. Not official brand files — a consistent set that sits on paper.
def _g(a, b, c=None, fill=None):
    d = f'<path d="{a}" fill="none" stroke="{b}" stroke-width="{c}"/>' if c else ""
    return d


GLYPHS = {
    # client / screen
    "react": lambda k: (
        f'<g stroke="{k}" stroke-width="1.5" fill="none">'
        f'<ellipse cx="8" cy="8" rx="6.6" ry="2.5"/>'
        f'<ellipse cx="8" cy="8" rx="6.6" ry="2.5" transform="rotate(60 8 8)"/>'
        f'<ellipse cx="8" cy="8" rx="6.6" ry="2.5" transform="rotate(120 8 8)"/>'
        f'</g><circle cx="8" cy="8" r="1.6" fill="{k}"/>'),
    "expo": lambda k: (f'<path d="M2.6 13.4L8 3.2l5.4 10.2" fill="none" stroke="{k}" '
                       f'stroke-width="1.5" stroke-linejoin="round"/>'
                       f'<circle cx="8" cy="10.6" r="1.6" fill="{k}"/>'),
    "expo-router": lambda k: (f'<g stroke="{k}" stroke-width="1.5" fill="none">'
                              f'<rect x="2.6" y="3.6" width="7.4" height="8.8"/>'
                              f'<rect x="6.4" y="6" width="7" height="6.4" fill="{PAPER}"/>'
                              f'</g>'),
    "nativewind": lambda k: (f'<g stroke="{k}" stroke-width="1.5" fill="none" '
                             f'stroke-linecap="round">'
                             f'<path d="M2.6 6.4h6.6a1.9 1.9 0 1 0-1.9-1.9"/>'
                             f'<path d="M2.6 10.6h9.4a1.9 1.9 0 1 1-1.9 1.9"/></g>'),
    "zustand": lambda k: (f'<path d="M3.4 4.6h9.2L3.4 11.4h9.2" fill="none" stroke="{k}" '
                          f'stroke-width="1.6" stroke-linejoin="round"/>'),
    "query": lambda k: (f'<path d="M13 8a5 5 0 1 1-1.7-3.8" fill="none" stroke="{k}" '
                        f'stroke-width="1.5" stroke-linecap="round"/>'
                        f'<path d="M13.4 2.6v2.6h-2.6" fill="none" stroke="{k}" '
                        f'stroke-width="1.5" stroke-linecap="round"/>'),
    "axios": lambda k: (f'<g stroke="{k}" stroke-width="1.5" fill="none" stroke-linecap="round">'
                        f'<path d="M2.6 5.8h10.2M10.4 3.4l2.4 2.4-2.4 2.4"/>'
                        f'<path d="M13.4 10.2H3.2M5.6 7.8 3.2 10.2l2.4 2.4"/></g>'),
    # server
    "nestjs": lambda k: (f'<path d="M8 2.4l4.8 2.8v5.6L8 13.6l-4.8-2.8V5.2z" fill="none" '
                         f'stroke="{k}" stroke-width="1.5" stroke-linejoin="round"/>'
                         f'<circle cx="8" cy="8" r="1.5" fill="{k}"/>'),
    "express": lambda k: (f'<g stroke="{k}" stroke-width="1.5" fill="none" '
                          f'stroke-linecap="round">'
                          f'<path d="M3 12.4L10 3.6M6.6 12.4L13.6 3.6"/></g>'),
    "postgres": lambda k: (f'<g stroke="{k}" stroke-width="1.5" fill="none">'
                           f'<ellipse cx="8" cy="4.6" rx="5" ry="2"/>'
                           f'<path d="M3 4.6v6.8c0 1.1 2.2 2 5 2s5-.9 5-2V4.6"/>'
                           f'<path d="M3 8c0 1.1 2.2 2 5 2s5-.9 5-2"/></g>'),
    "prisma": lambda k: (f'<path d="M8.6 2.2l4 10.4-8.6.4z" fill="none" stroke="{k}" '
                         f'stroke-width="1.5" stroke-linejoin="round"/>'
                         f'<path d="M8.6 2.2L7 9.4h4.2" fill="none" stroke="{k}" '
                         f'stroke-width="1.2" opacity=".55"/>'),
    "redis": lambda k: (f'<g stroke="{k}" stroke-width="1.5" fill="none" stroke-linejoin="round">'
                        f'<path d="M2.8 5.4L8 3l5.2 2.4L8 7.8z"/>'
                        f'<path d="M2.8 9L8 11.4 13.2 9"/></g>'),
    "jwt": lambda k: (f'<g stroke="{k}" stroke-width="1.5" fill="none">'
                      f'<circle cx="5.4" cy="8" r="2.6"/>'
                      f'<path d="M8 8h6M11.4 8v2.4M13.6 8v1.8"/></g>'),
    # workflow / ship
    "pnpm": lambda k: (f'<g stroke="{k}" stroke-width="1.5" fill="none">'
                       f'<rect x="2.6" y="4.4" width="10.8" height="7.2"/>'
                       f'<path d="M6.2 7.6h.1M8 7.6h.1M9.8 7.6h.1" stroke-width="2.2" '
                       f'stroke-linecap="round"/></g>'),
    "turbo": lambda k: (f'<path d="M2.6 12.6L8 3.4l5.4 9.2z" fill="none" stroke="{k}" '
                        f'stroke-width="1.5" stroke-linejoin="round"/>'
                        f'<path d="M6.4 12.6L8 9.4l1.6 3.2z" fill="{k}"/>'),
    "typescript": lambda k: (f'<rect x="2.6" y="2.6" width="10.8" height="10.8" fill="none" '
                             f'stroke="{k}" stroke-width="1.5"/>'
                             f'<path d="M5.2 6.2h5.4M8 6.2v5" stroke="{k}" stroke-width="1.5"/>'),
    "git": lambda k: (f'<g stroke="{k}" stroke-width="1.5" fill="none">'
                      f'<circle cx="4.6" cy="3.6" r="1.6"/><circle cx="4.6" cy="12.4" r="1.6"/>'
                      f'<circle cx="11.4" cy="6.6" r="1.6"/><path d="M4.6 5.2v5.6"/>'
                      f'<path d="M6.2 11.6c2.6-.4 3.6-1.6 4-3.4"/></g>'),
    "bruno": lambda k: (f'<circle cx="8" cy="8" r="5.4" fill="none" stroke="{k}" '
                        f'stroke-width="1.5"/>'
                        f'<path d="M5.6 5.8c2.4-.4 4.4.6 4.4 2.6s-2 2.8-4.4 2.4" fill="none" '
                        f'stroke="{k}" stroke-width="1.5"/>'),
    "postman": lambda k: (f'<circle cx="8" cy="8" r="5.4" fill="none" stroke="{k}" '
                          f'stroke-width="1.5"/>'
                          f'<path d="M8 2.6a5.4 5.4 0 0 1 0 10.8" fill="none" stroke="{k}" '
                          f'stroke-width="1.5" opacity=".5"/>'
                          f'<circle cx="9.6" cy="6.4" r="1.3" fill="{k}"/>'),
    "docker": lambda k: (f'<g stroke="{k}" stroke-width="1.4" fill="none">'
                         f'<rect x="3" y="6.2" width="2.6" height="2.4"/>'
                         f'<rect x="6.2" y="6.2" width="2.6" height="2.4"/>'
                         f'<rect x="6.2" y="3.4" width="2.6" height="2.4"/>'
                         f'<path d="M2.2 10.4c3.4.6 8 .6 10.4-1.4 1 .6 1.8.4 2.4-.2-1 2.8-4 4-7.4 4-2.6 0-4.6-.8-5.4-2.4z"/></g>'),
    "eas": lambda k: (f'<path d="M8 13V4" stroke="{k}" stroke-width="1.5"/>'
                      f'<path d="M4.6 7.4L8 4l3.4 3.4" fill="none" stroke="{k}" '
                      f'stroke-width="1.5" stroke-linejoin="round"/>'
                      f'<path d="M3.4 13h9.2" stroke="{k}" stroke-width="1.5"/>'),
    "sentry": lambda k: (f'<g stroke="{k}" stroke-width="1.5" fill="none" stroke-linecap="round">'
                         f'<path d="M2.4 12.4c0-5 2.6-8.8 5.6-8.8s5.6 3.8 5.6 8.8"/>'
                         f'<path d="M5.4 12.4c0-3 1.2-5.2 2.6-5.2s2.6 2.2 2.6 5.2"/></g>'),
    "supabase": lambda k: (f'<path d="M9.2 2.4L3.6 9.4h4.2l-1 4.2 5.6-7H8.2z" fill="{k}"/>'),
    "firebase": lambda k: (f'<path d="M8 2.6c2.6 3 3.8 4.6 3.8 6.6a3.8 3.8 0 1 1-7.6 0c0-2 1.2-3.6 3.8-6.6z" '
                           f'fill="none" stroke="{k}" stroke-width="1.5" stroke-linejoin="round"/>'),
    "render": lambda k: (f'<path d="M4.4 10.4a2.8 2.8 0 0 1 .4-5.6 3.8 3.8 0 0 1 7 1.2 2.4 2.4 0 0 1-.6 4.4z" '
                         f'fill="none" stroke="{k}" stroke-width="1.5" stroke-linejoin="round"/>'
                         f'<path d="M4.4 12.8h7.2" stroke="{k}" stroke-width="1.4"/>'),
    "railway": lambda k: (f'<g stroke="{k}" stroke-width="1.4" fill="none">'
                          f'<path d="M5 2.4L4 13.6M11 2.4l1 11.2"/>'
                          f'<path d="M3 6h10M3.6 9.6h8.8"/></g>'),
    "monorepo": lambda k: (f'<g stroke="{k}" stroke-width="1.5" fill="none">'
                           f'<path d="M2.6 12.4V3.6h3.6l1.4 1.6h5.8v7.2z"/>'
                           f'<path d="M6 7.6h4.4M6 9.8h4.4"/></g>'),
    "pr": lambda k: (f'<g stroke="{k}" stroke-width="1.5" fill="none">'
                     f'<circle cx="4.4" cy="3.6" r="1.5"/><circle cx="4.4" cy="12.4" r="1.5"/>'
                     f'<path d="M4.4 5.2v5.6"/>'
                     f'<path d="M6 3.6h3.4a2.4 2.4 0 0 1 2.4 2.4v4"/></g>'
                     f'<path d="M9.6 10.4l2.2 2.2 2.2-2.2" fill="none" stroke="{k}" '
                     f'stroke-width="1.4" stroke-linejoin="round"/>'),
    "flyio": lambda k: (f'<path d="M13.4 2.6L2.6 7.8l4.4 1.4 1.4 4.4z" fill="none" stroke="{k}" '
                        f'stroke-width="1.5" stroke-linejoin="round"/>'),
}


def mark(key, x, y, ink):
    """Place a 16×16 mark at x,y in one ink."""
    body = GLYPHS[key](ink)
    return f'  <g transform="translate({x} {y})">{body}</g>'


# ────────────────────────────────────────────────────────────── 01 · BANNER ──
def banner(name="ALEKSIS A. ONG"):
    w, h = 1200, 360
    b = []
    b += [R(64, 41, 9, 9, ACC)]                         # registration mark
    b += masthead(w, "SCORE SHEET · NO. 001", "STUDENT · CAVITE STATE UNIVERSITY",
                  indent=22)
    size = 100 if len(name) <= 11 else 88 if len(name) <= 15 else 76
    b += [T(60, 200, name, size, INK, SERIF, "700", -3.2),
          T(64, 246, "Student. I build the screen, then the API behind it.", 24, GRAPH,
            SERIF, None, italic=True)]
    # right column: the sheet's real header block, one ink per field
    b += [V(108, 292, 792, RULE)]
    b += [H(812, 1136, 108, RULE),
          T(812, 132, "BASED", 10, GRAPH, MONO, "700", 1.6),
          T(920, 132, "CAVITE, PHILIPPINES · UTC+8", 11, INK, MONO, None, 0.9)]
    b += [H(812, 1136, 160, RULE),
          T(812, 184, "STACK", 10, GRAPH, MONO, "700", 1.6),
          spans(920, 184, 11, [("REACT NATIVE", SCREEN), (" · ", GRAPH),
                               ("LARAVEL", API), (" · ", GRAPH), ("PHP", API)],
                ls=0.9)]
    b += [H(812, 1136, 212, RULE),
          T(812, 236, "OFF CLOCK", 10, GRAPH, MONO, "700", 1.6),
          spans(920, 236, 11, [("CHESS", GOLD), (" · ", GRAPH), ("GAMES", GOLD),
                               (" · ", GRAPH), ("JOGGING", GOLD)], ls=0.9)]
    b += [H(812, 1136, 264, RULE),
          T(812, 288, "RESULT", 10, GRAPH, MONO, "700", 1.6),
          T(920, 288, "STILL PLAYING", 11, ACC, MONO, "700", 0.9)]
    b += [H(64, 1136, 320, RULE)]
    b += colorbar(64, 338)
    return fig(w, h, b, f"{name} — mobile and backend developer")


def banner_mobile(name="ALEKSIS A. ONG"):
    w, h = 600, 560
    b = [R(28, 29, 8, 8, ACC)]
    b += masthead(w, "SCORE SHEET · NO. 001", "CVSU", y=38, x=28, rule_y=54, indent=20)
    parts = name.split()
    b += [T(24, 152, parts[0] if parts else "YOUR", 82, INK, SERIF, "700", -2.6)]
    if len(parts) > 1:
        b += [T(24, 232, " ".join(parts[1:]), 82, INK, SERIF, "700", -2.6)]
    b += [T(28, 278, "Student. I build the screen, then", 19, GRAPH, SERIF, None, italic=True),
          T(28, 304, "the API behind it.", 19, GRAPH, SERIF, None, italic=True)]
    b += [H(28, 572, 346, RULE),
          T(28, 370, "BASED", 9.5, GRAPH, MONO, "700", 1.5),
          T(168, 370, "CAVITE, PHILIPPINES · UTC+8", 11, INK, MONO, None, 0.6),
          H(28, 572, 392, RULE),
          T(28, 416, "STACK", 9.5, GRAPH, MONO, "700", 1.5),
          spans(168, 416, 11, [("REACT NATIVE", SCREEN), (" · ", GRAPH),
                               ("LARAVEL", API), (" · ", GRAPH), ("PHP", API)],
                ls=0.6),
          H(28, 572, 438, RULE),
          T(28, 462, "OFF CLOCK", 9.5, GRAPH, MONO, "700", 1.5),
          spans(168, 462, 11, [("CHESS", GOLD), (" · ", GRAPH), ("GAMES", GOLD),
                               (" · ", GRAPH), ("JOGGING", GOLD)], ls=0.6),
          H(28, 572, 484, RULE),
          T(28, 508, "RESULT", 9.5, GRAPH, MONO, "700", 1.5),
          T(168, 508, "STILL PLAYING", 11, ACC, MONO, "700", 0.6),
          H(28, 572, 530, RULE)]
    b += colorbar(28, 542, unit=20, h=5)
    return fig(w, h, b, f"{name} — mobile and backend developer")


# ────────────────────────────────────────────────────────── 02 · THE MOVES ──
MOVES = [  # (tool, layer, ink) — blue = the screen, green = the API
    ("REACT NATIVE", "SCREEN", SCREEN),
    ("LARAVEL", "API", API),
    ("JAVASCRIPT", "SCREEN", SCREEN),
    ("BLADE", "SCREEN", SCREEN),
    ("DOCKER", "API", API),
    ("PYTHON", "API", API),
]


def moves():
    w, h = 1200, 440
    b = masthead(w, "FIG. 01 · THE MOVES", "SIX TOOLS", ink=SCREEN)
    b += [T(92, 108, "MOVE", 10, GRAPH, MONO, "700", 1.8),
          T(1136, 108, "LAYER", 10, GRAPH, MONO, "700", 1.8, "end"),
          H(64, 1136, 118, RULE)]
    for i, (tool, layer, ink) in enumerate(MOVES):
        y = 168 + i * 46
        b += [R(64, y - 16, 3, 21, ink),
              T(92, y, f"{i + 1}.", 15, ink, MONO, "700"),
              T(168, y, tool, 25, INK, SERIF, "700", -0.4),
              T(1136, y, layer, 11, ink, MONO, "700", 1.9, "end")]
        if i < len(MOVES) - 1:
            b += [H(64, 1136, y + 18, RULE)]
    b += [H(64, 1136, 416, RULE)]
    return fig(w, h, b, "Six moves: React Native, Laravel, JavaScript, Blade, Docker, Python")


def moves_mobile():
    w, h = 600, 452
    b = masthead(w, "FIG. 01 · THE MOVES", "SIX TOOLS", y=38, x=28, rule_y=54,
                ink=SCREEN)
    b += [T(48, 84, "MOVE", 9.5, GRAPH, MONO, "700", 1.7),
          T(572, 84, "LAYER", 9.5, GRAPH, MONO, "700", 1.7, "end"),
          H(28, 572, 92, RULE)]
    for i, (tool, layer, ink) in enumerate(MOVES):
        y = 128 + i * 50
        b += [R(28, y - 14, 3, 18, ink),
              T(48, y, f"{i + 1}.", 12, ink, MONO, "700"),
              T(88, y, tool, 21, INK, SERIF, "700"),
              T(572, y, layer, 9.5, ink, MONO, "700", 1.6, "end")]
        if i < len(MOVES) - 1:
            b += [H(28, 572, y + 18, RULE)]
    b += [H(28, 572, 428, RULE)]
    return fig(w, h, b, "Six moves: React Native, Laravel, JavaScript, Blade, Docker, Python")


# ──────────────────────────────────────────────────────── 02 · THE STACK ──
PHASES = [
    ("01", "SETUP", INK, [("pnpm", "pnpm"), ("turbo", "Turborepo"),
                          ("monorepo", "Monorepo"), ("typescript", "TypeScript")]),
    ("02", "DAILY LOOP", INK, [("git", "Git branches"), ("pr", "Pull requests"),
                               ("bruno", "Bruno"), ("postman", "Postman")]),
    ("03", "FRONTEND", SCREEN, [("react", "React Native"), ("expo", "Expo"),
                                ("expo-router", "Expo Router"),
                                ("nativewind", "NativeWind"),
                                ("zustand", "Zustand"), ("query", "React Query"),
                                ("axios", "Axios")]),
    ("04", "BACKEND", API, [("nestjs", "NestJS"), ("express", "Express"),
                            ("postgres", "PostgreSQL"), ("prisma", "Prisma"),
                            ("redis", "Redis"), ("jwt", "JWT auth")]),
    ("05", "SHIP", INK, [("docker", "Docker"), ("eas", "EAS Build"),
                         ("sentry", "Sentry"), ("render", "Render"),
                         ("railway", "Railway"), ("flyio", "Fly.io"),
                         ("supabase", "Supabase"), ("firebase", "Firebase")]),
]
def roadmap():
    w = 1200
    rows = max(len(p[3]) for p in PHASES)
    last = 158 + (rows - 1) * 27
    h = last + 46
    b = masthead(w, "FIG. 02 · THE ROADMAP", "29 TOOLS · 5 PHASES")
    for i, (num, name, ink, items) in enumerate(PHASES):
        x = 64 + i * 227
        if i:
            b += [V(100, last + 16, x - 13, RULE)]
        b += [T(x, 116, num, 10, ink, MONO, "700", 1.6),
              T(x + 26, 116, name, 10, ink, MONO, "700", 1.6),
              H(x, x + 200, 128, ink, 1.5)]
        for j, (key, label) in enumerate(items):
            y = 158 + j * 27
            b += [mark(key, x, y - 11, ink),
                  T(x + 24, y, label, 10.5, INK, MONO, None, 0.5)]
    b += [H(64, 1136, last + 26, RULE)]
    return fig(w, h, b, "The stack in five phases: setup, daily loop, frontend, "
                        "backend, ship — each tool with its mark")


def roadmap_mobile():
    w = 600
    col_w = 258
    y = 92
    b = masthead(w, "FIG. 02 · THE ROADMAP", "29 TOOLS", y=38, x=28, rule_y=54)
    for num, name, ink, items in PHASES:
        b += [T(28, y, f"{num}", 10, ink, MONO, "700", 1.6),
              T(62, y, name, 10, ink, MONO, "700", 1.6),
              H(28, 572, y + 11, ink, 1.5)]
        top = y + 34
        for j, (key, label) in enumerate(items):
            cx = 28 + (j % 2) * col_w
            cy = top + (j // 2) * 27
            b += [mark(key, cx, cy - 11, ink),
                  T(cx + 24, cy, label, 10.5, INK, MONO)]
        y = top + ((len(items) + 1) // 2) * 27 + 22
    b += [H(28, 572, y + 2, RULE)]
    return fig(w, y + 28, b, "The stack in five phases, each tool with its mark")


# ────────────────────────────────────────────────────── 03 · OFF THE BOARD ──
def grass():
    w, h = 1200, 300
    b = masthead(w, "FIG. 03 · OFF THE BOARD", "TOUCH GRASS", ink=GOLD)
    b += board(64, 92, 176, dark=BOARD)
    # a staircase that leaves the board from its right edge and climbs into the grass
    b += path("M240 246H302V224H370V202H446", API, 3, end_square=(451, 202))
    b += [T(520, 158, "Off the board.", 42, INK, SERIF, "700", -1.2),
          T(520, 206, "Chess for the thinking. Games for the unwind. Running", 17, GRAPH, SERIF),
          T(520, 230, "for the part of the day nobody can reach me.", 17, GRAPH, SERIF)]
    return fig(w, h, b, "A chessboard with a path leading off it: off the clock")


def grass_mobile():
    w, h = 600, 384
    b = masthead(w, "FIG. 03 · OFF THE BOARD", "TOUCH GRASS", y=38, x=28, rule_y=54,
                ink=GOLD)
    b += board(28, 84, 132, dark=BOARD)
    b += path("M160 200H214V178H272", API, 3, end_square=(277, 178))
    b += [T(28, 274, "Off the board.", 30, INK, SERIF, "700", -0.9),
          T(28, 310, "Chess for the thinking. Games for the", 15, GRAPH, SERIF),
          T(28, 332, "unwind. Running for the part of the day", 15, GRAPH, SERIF),
          T(28, 354, "nobody can reach me.", 15, GRAPH, SERIF)]
    return fig(w, h, b, "A chessboard with a path leading off it: off the clock")


# ────────────────────────────────────────────────────────── 04 · YOUR MOVE ──
SEND = [("01", "a repo, and the thing that breaks"),
        ("02", "the deadline you are really working to"),
        ("03", "a chess challenge — I will accept")]


def contact():
    w, h = 1200, 236
    b = [T(64, 52, "FIG. 04 · YOUR MOVE", 12, ACC, MONO, "700", 2.4),
         T(58, 158, "Send the first move.", 58, PAPER, SERIF, "700", -1.8),
         T(740, 92, "WHAT TO SEND", 10, ACC, MONO, "700", 1.9),
         H(740, 1136, 108, "#3A3E38")]
    for i, (n, text) in enumerate(SEND):
        y = 146 + i * 34
        b += [T(740, y, n, 11, INK_SOFT, MONO, "700"),
              T(784, y, text, 15.5, PAPER, SERIF)]
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="Send the first move — what to send">',
        R(0, 0, w, h, INK),
        R(0, 0, w * 0.4, 4, SCREEN),
        R(w * 0.4, 0, w * 0.35, 4, API),
        R(w * 0.75, 0, w * 0.25, 4, ACC),
        *b, "</svg>", ""])


def contact_mobile():
    w, h = 600, 356
    b = [T(28, 48, "FIG. 04 · YOUR MOVE", 11, ACC, MONO, "700", 2.2),
         T(24, 118, "Send the", 42, PAPER, SERIF, "700", -1.4),
         T(24, 164, "first move.", 42, PAPER, SERIF, "700", -1.4),
         T(28, 214, "WHAT TO SEND", 9.5, ACC, MONO, "700", 1.8),
         H(28, 572, 228, "#3A3E38")]
    for i, (n, text) in enumerate(SEND):
        y = 258 + i * 34
        b += [T(28, y, n, 10, INK_SOFT, MONO, "700"),
              T(64, y, text, 13, PAPER, SERIF)]
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="Send the first move — what to send">',
        R(0, 0, w, h, INK),
        R(0, 0, w * 0.4, 4, SCREEN),
        R(w * 0.4, 0, w * 0.35, 4, API),
        R(w * 0.75, 0, w * 0.25, 4, ACC),
        *b, "</svg>", ""])


FILES = {
    "banner.svg": banner(),
    "roadmap.svg": roadmap(),
    "roadmap-mobile.svg": roadmap_mobile(),
    "banner-mobile.svg": banner_mobile(),
    "moves.svg": moves(),
    "moves-mobile.svg": moves_mobile(),
    "grass.svg": grass(),
    "grass-mobile.svg": grass_mobile(),
    "contact.svg": contact(),
    "contact-mobile.svg": contact_mobile(),
}

for name, content in FILES.items():
    (OUT / name).write_text(content, encoding="utf-8")
    print(f"{name:24} {len(content):>6,} bytes")
