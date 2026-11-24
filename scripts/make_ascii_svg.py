#!/usr/bin/env python3
"""
Turn an ASCII portrait into a monochrome terminal-window SVG. Rows print top
to bottom with a block cursor riding the wipe, once, then the art holds.

    python scripts/make_ascii_svg.py [data/portrait.txt | source-prepped.png] [out.svg]

A .txt source is used as-is (the portrait from the portfolio site). An image
source (from prep_photo.py) is converted with the density ramp below.

Env: COLS (detail, default 62), STATIC=1 for a frozen frame.
"""
import html
import os
import sys

from PIL import Image, ImageEnhance

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "data", "portrait.txt")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "ascii-portrait.svg")
STATIC = bool(os.environ.get("STATIC"))

RAMP = " .`:-=+*cs#%@"  # bright (sparse) to dark (dense)
GAMMA = float(os.environ.get("GAMMA", 1.15))
CONTRAST = float(os.environ.get("CONTRAST", 1.1))
WHITE_FLOOR = 0.82

W, H = 370, 440          # matches the info card height
TITLE_H, STATUS_H, PAD = 30, 38, 18
ART_W = W - 2 * PAD
ART_H_MAX = H - TITLE_H - STATUS_H - 16

BG, BG2 = "#0d1117", "#111722"
FRAME = "#30363d"
DIM = "#7d8590"
INK = "#c9d1d9"
GREEN = "#39d353"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
ASPECT = 1.875            # monospace glyph height / width


def from_image(path, cols):
    im = Image.open(path).convert("L")
    im = ImageEnhance.Contrast(im).enhance(CONTRAST)
    rows = round(cols * im.height / im.width / ASPECT)
    im = im.resize((cols, rows), Image.LANCZOS)
    px = im.load()
    out = []
    for y in range(rows):
        row = []
        for x in range(cols):
            lum = pow(px[x, y] / 255.0, GAMMA)
            if lum >= WHITE_FLOOR:
                row.append(" ")
                continue
            i = int((1.0 - lum) * (len(RAMP) - 1) + 0.5)
            row.append(RAMP[max(0, min(len(RAMP) - 1, i))])
        out.append("".join(row))
    return out


if SRC.endswith(".txt"):
    with open(SRC) as f:
        lines = [l.rstrip("\n").rstrip() for l in f]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
else:
    lines = from_image(SRC, int(os.environ.get("COLS", 62)))

COLS = max(len(l) for l in lines)
lines = [l.ljust(COLS) for l in lines]
ROWS = len(lines)
CELL_W = min(ART_W / COLS, ART_H_MAX / (ROWS * ASPECT))
CELL_H = CELL_W * ASPECT
ART_W = COLS * CELL_W
ART_H = ROWS * CELL_H
ART_X = (W - ART_W) / 2

ROW_DUR = 4.0 / ROWS     # whole portrait prints in about 4s

top = TITLE_H + 8 + (ART_H_MAX - ART_H) / 2
p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
     f'viewBox="0 0 {W} {H}" font-family="{MONO}">']
if not STATIC:
    p.append("<style>@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}"
             ".k{animation:blink 1s step-end infinite}</style>")
p.append(f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
         f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
         f'</linearGradient></defs>')
p.append(f'<rect width="{W}" height="{H}" rx="12" fill="url(#bg)"/>')
p.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}"/>')
p.append(f'<line x1="0" y1="{TITLE_H}" x2="{W}" y2="{TITLE_H}" stroke="{FRAME}"/>')
for i, col in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    p.append(f'<circle cx="{20 + i*16}" cy="{TITLE_H/2}" r="5" fill="{col}"/>')
p.append(f'<text x="{W/2 + 20}" y="{TITLE_H/2 + 4}" fill="{DIM}" font-size="12" '
         f'text-anchor="middle">~$ ./portrait.sh</text>')

fs = CELL_H * 0.92
for r, line in enumerate(lines):
    ry = top + r * CELL_H
    ty = ry + CELL_H * 0.78
    text = (f'<text xml:space="preserve" x="{ART_X:.1f}" y="{ty:.1f}" fill="#e6edf3" font-weight="bold" font-size="{fs:.2f}" '
            f'textLength="{ART_W:.1f}" lengthAdjust="spacingAndGlyphs">{html.escape(line)}</text>')
    if STATIC:
        p.append(text)
        continue
    d = r * ROW_DUR
    p.append(f'<clipPath id="r{r}"><rect x="{ART_X:.1f}" y="{ry:.1f}" height="{CELL_H:.2f}" width="0">'
             f'<animate attributeName="width" from="0" to="{ART_W:.1f}" begin="{d:.3f}s" '
             f'dur="{ROW_DUR:.3f}s" fill="freeze"/></rect></clipPath>')
    p.append(f'<g clip-path="url(#r{r})">{text}</g>')
    p.append(f'<rect y="{ry + 1:.1f}" width="{CELL_W:.2f}" height="{CELL_H - 2:.2f}" fill="{INK}" opacity="0">'
             f'<animate attributeName="x" from="{ART_X:.1f}" to="{ART_X + ART_W:.1f}" begin="{d:.3f}s" '
             f'dur="{ROW_DUR:.3f}s" fill="freeze"/>'
             f'<set attributeName="opacity" to="0.85" begin="{d:.3f}s"/>'
             f'<set attributeName="opacity" to="0" begin="{d + ROW_DUR:.3f}s"/></rect>')

sy = H - 18
p.append(f'<line x1="0" y1="{sy - 20}" x2="{W}" y2="{sy - 20}" stroke="{FRAME}"/>')
p.append(f'<text x="{PAD + 4}" y="{sy}" font-size="12.5" xml:space="preserve"><tspan fill="{GREEN}">~</tspan>'
         f'<tspan fill="{DIM}"> $ whoami </tspan><tspan fill="{INK}">Abdul Raiyaan</tspan></text>')
cx = PAD + 4 + len("~ $ whoami Abdul Raiyaan ") * 12.5 * 0.6
blink = "" if STATIC else ' class="k"'
p.append(f'<rect x="{cx:.1f}" y="{sy - 11}" width="7.5" height="14" fill="{INK}"{blink}/>')
p.append("</svg>")

with open(OUT, "w") as f:
    f.write("".join(p))
print("wrote", OUT, f"{COLS}x{ROWS}")
