#!/usr/bin/env python3
"""
Tech stack card: four groups of logo tiles that pop in one after another.
Logos are vendored in data/stack-icons.json (Iconify "logos" set). Edit GROUPS
to change what's shown; any name used must exist in that file.

    python scripts/make_stack_svg.py [out.svg]      (STATIC=1 for a frozen frame)
"""
import json
import os
import re
import sys
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from term import BRIGHT, DIM, FRAME, GREEN, INK, TILE, TITLE_H, anim, open_svg  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "stack.svg")
ICONS = os.path.join(ROOT, "data", "stack-icons.json")
STATIC = bool(os.environ.get("STATIC"))

# each inner list is one row of groups, laid out left to right
GROUPS = [
    [("languages", ["Python", "Go", "Java", "JavaScript", "TypeScript"]),
     ("web", ["React", "Next.js", "FastAPI", "HTML", "CSS"])],
    [("ai-ml", ["PyTorch"]),
     ("cloud-tools", ["Azure", "Vercel", "Git", "Linux"])],
]
# logos drawn in black need a light fill to show on the dark tiles
RECOLOR = {"Vercel": BRIGHT}

W = 860
TILE_S = 52
LOGO = 30
STEP_X = 76
ROW_H = 118
TOP = TITLE_H + 22


def logo(name, icons, x, y, size, uid):
    ic = icons[name]
    body = ic["body"]
    # make gradient/clip ids unique per tile so logos never clash
    for old in set(re.findall(r'id="([^"]+)"', body)):
        body = body.replace(f'id="{old}"', f'id="{old}{uid}"').replace(f"#{old})", f"#{old}{uid})")
    if name in RECOLOR:
        body = body.replace("<path ", f'<path fill="{RECOLOR[name]}" ')
    scale = size / max(ic["w"], ic["h"])
    ox = x + (size - ic["w"] * scale) / 2
    oy = y + (size - ic["h"] * scale) / 2
    return f'<g transform="translate({ox:.2f} {oy:.2f}) scale({scale:.4f})">{body}</g>'


def main():
    with open(ICONS) as f:
        icons = json.load(f)

    H = TOP + 2 * ROW_H + 6
    p = open_svg(W, H, "raiyaan@github: ~$ ls ~/stack", STATIC)
    n = 0
    g = 0
    for row, groups in enumerate(GROUPS):
        gx = 24
        gy = TOP + row * ROW_H
        for label, names in groups:
            p.append(f'<text x="{gx + 6}" y="{gy + 10}" font-size="12.5" xml:space="preserve"'
                     f'{anim("fade", 0.1 + g * 0.15, STATIC)}><tspan fill="{GREEN}" font-weight="bold">'
                     f'{escape(label)}/</tspan><tspan fill="{DIM}">  {len(names)}</tspan></text>')
            for i, name in enumerate(names):
                tx = gx + 6 + i * STEP_X
                ty = gy + 24
                n += 1
                p.append(f'<g{anim("pop", 0.3 + n * 0.07, STATIC)}>'
                         f'<rect x="{tx}" y="{ty}" width="{TILE_S}" height="{TILE_S}" rx="10" '
                         f'fill="{TILE}" stroke="{FRAME}"/>'
                         + logo(name, icons, tx + (TILE_S - LOGO) / 2, ty + (TILE_S - LOGO) / 2, LOGO, f"_{n}")
                         + f'<text x="{tx + TILE_S/2}" y="{ty + TILE_S + 17}" fill="{INK}" font-size="10.5" '
                           f'text-anchor="middle">{escape(name)}</text></g>')
            gx += len(names) * STEP_X + 34
            g += 1

    p.append("</svg>")
    with open(OUT, "w") as f:
        f.write("".join(p))
    print("wrote", OUT, f"{W}x{H}")


if __name__ == "__main__":
    main()
