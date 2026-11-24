#!/usr/bin/env python3
"""
Hero banner: name in large type, then a prompt that types and deletes a few
lines about what I'm working on, on a loop. Edit LINES to change them.

    python scripts/make_hero_svg.py [out.svg]      (STATIC=1 for a frozen frame)
"""
import os
import sys
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from term import BRIGHT, DIM, FRAME, GREEN, INK, TITLE_H, anim, open_svg  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "hero.svg")
STATIC = bool(os.environ.get("STATIC"))

LINES = [
    "building VaultDB, a database from scratch in Go",
    "trained a GPT from scratch in PyTorch",
    "AI/ML and Data Science at Taylor's x UWE Bristol",
    "open to AI/ML internships from January 2027",
]
STATUS = [
    ("based in", "Malaysia, UTC+8"),
    ("studying", "Deep Learning, Big Data"),
    ("status", "open to internships"),
]

W, H = 860, 190
FS = 15                  # typing line font size
CW = FS * 0.6            # monospace char width
TYPE_X = 72
TYPE_Y = 152
PER_CHAR = 0.055         # seconds per typed character
HOLD = 1.8               # seconds a full line stays up
DELETE = 0.45            # seconds to clear it
GAP = 0.35               # pause before the next line


def main():
    p = open_svg(W, H, "raiyaan@github: ~$ whoami", STATIC)

    # name
    p.append(f'<text x="34" y="{TITLE_H + 62}" fill="{BRIGHT}" font-size="40" font-weight="bold" '
             f'letter-spacing="1"{anim("rise", 0.1, STATIC)}>Abdul Raiyaan</text>')
    p.append(f'<text x="36" y="{TITLE_H + 90}" fill="{DIM}" font-size="13.5"{anim("rise", 0.3, STATIC)}>'
             f'AI/ML engineering student. I build things end to end.</text>')

    # status block on the right
    sx = W - 290
    p.append(f'<line x1="{sx - 30}" y1="{TITLE_H + 26}" x2="{sx - 30}" y2="{TITLE_H + 98}" '
             f'stroke="{FRAME}"{anim("fade", 0.5, STATIC)}/>')
    for i, (k, v) in enumerate(STATUS):
        y = TITLE_H + 40 + i * 24
        dot = (f'<circle cx="{sx - 11}" cy="{y - 4}" r="3.5" fill="{GREEN}">'
               + ("" if STATIC else '<animate attributeName="opacity" values="1;.3;1" dur="2s" repeatCount="indefinite"/>')
               + "</circle>") if k == "status" else ""
        p.append(f'<g{anim("rise", 0.45 + i * 0.12, STATIC)}>'
                 f'<text x="{sx}" y="{y}" fill="{DIM}" font-size="12">{escape(k)}</text>'
                 f'<text x="{sx + 78}" y="{y}" fill="{INK}" font-size="12">{escape(v)}</text>{dot}</g>')

    p.append(f'<line x1="24" y1="{TYPE_Y - 26}" x2="{W - 24}" y2="{TYPE_Y - 26}" stroke="{FRAME}" '
             f'stroke-dasharray="2 4"{anim("fade", 0.6, STATIC)}/>')
    p.append(f'<text x="34" y="{TYPE_Y}" font-size="{FS}" xml:space="preserve"{anim("fade", 0.6, STATIC)}>'
             f'<tspan fill="{GREEN}">~</tspan><tspan fill="{DIM}"> $</tspan></text>')

    if STATIC:
        p.append(f'<text x="{TYPE_X}" y="{TYPE_Y}" fill="{INK}" font-size="{FS}">{escape(LINES[0])}</text>')
        p.append(f'<rect x="{TYPE_X + len(LINES[0]) * CW + 2:.1f}" y="{TYPE_Y - 13}" width="9" height="17" fill="{INK}"/>')
    else:
        # each line: type char by char, hold, delete, then hand over to the next
        spans = [len(l) * PER_CHAR + HOLD + DELETE + GAP for l in LINES]
        total = sum(spans)
        start = 0.0
        cursor_vals, cursor_times = [], []
        for idx, line in enumerate(LINES):
            n = len(line)
            vals, times = [], []

            def key(t, width):
                times.append(t / total)
                vals.append(width)

            key(0, 0)
            key(start, 0)
            for c in range(1, n + 1):
                key(start + c * PER_CHAR, c * CW)
            key(start + n * PER_CHAR + HOLD, n * CW)
            key(start + n * PER_CHAR + HOLD + DELETE, 0)
            key(total, 0)
            # keep keyTimes strictly non-decreasing and start at 0, end at 1
            times[0], times[-1] = 0, 1
            kt = ";".join(f"{t:.5f}" for t in times)
            vv = ";".join(f"{v:.1f}" for v in vals)
            cid = f"t{idx}"
            p.append(f'<clipPath id="{cid}"><rect x="{TYPE_X}" y="{TYPE_Y - 16}" height="22" width="0">'
                     f'<animate attributeName="width" values="{vv}" keyTimes="{kt}" calcMode="discrete" '
                     f'dur="{total:.2f}s" begin="0.8s" repeatCount="indefinite"/></rect></clipPath>')
            p.append(f'<text x="{TYPE_X}" y="{TYPE_Y}" fill="{INK}" font-size="{FS}" '
                     f'clip-path="url(#{cid})">{escape(line)}</text>')
            # cursor x follows the typing edge of the active line
            for t, v in zip(times[1:-1], vals[1:-1]):
                cursor_times.append(t)
                cursor_vals.append(TYPE_X + v + 2)
            start += spans[idx]

        order = sorted(zip(cursor_times, cursor_vals))
        ct = [0.0] + [t for t, _ in order] + [1.0]
        cv = [TYPE_X + 2] + [v for _, v in order] + [TYPE_X + 2]
        p.append(f'<rect x="{TYPE_X + 2}" y="{TYPE_Y - 13}" width="9" height="17" fill="{INK}">'
                 f'<animate attributeName="x" values="{";".join(f"{v:.1f}" for v in cv)}" '
                 f'keyTimes="{";".join(f"{t:.5f}" for t in ct)}" calcMode="discrete" '
                 f'dur="{total:.2f}s" begin="0.8s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.51;1" '
                 f'dur="1s" repeatCount="indefinite"/></rect>')

    p.append("</svg>")
    with open(OUT, "w") as f:
        f.write("".join(p))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
