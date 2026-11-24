#!/usr/bin/env python3
"""
Hand-built neofetch-style info card. Rows fade in one after another, then a
cursor blinks on the prompt. Edit ROWS below to update the card.

    python scripts/make_info_card.py [out.svg]

Set STATIC=1 for a frozen frame.
"""
import os
import sys
from html import escape

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "info-card.svg")
STATIC = bool(os.environ.get("STATIC"))

USER = "raiyaan@github"
ROWS = [
    ("Name",    "Abdul Raiyaan"),
    ("Study",   "Bachelor's in Computer Science"),
    ("Uni",     "Taylor's University x UWE Bristol"),
    ("Focus",   "AI/ML, Data Science"),
    ("Now",     "VaultDB, a database from scratch in Go"),
    ("Built",   "GPT from scratch, NaviSense, UniResource Hub"),
    ("Prev",    "Python Developer Intern, Cogveel (x2)"),
    ("Stack",   "Python, Go, Java, TypeScript, PyTorch"),
    ("Wins",    "Dean's List x3, Cursor Hackathon Top 20"),
    ("Side",    "Cybersecurity, CTFs (4th at Hackverse)"),
    ("Seeking", "AI/ML internship from Jan 2027"),
    ("Mail",    "raiyaantopas@gmail.com"),
]

BG, BG2 = "#0d1117", "#111722"
FRAME = "#30363d"
DIM = "#7d8590"
INK = "#c9d1d9"
KEY = "#39d353"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
BLOCKS = ["#161b22", "#ff5f56", "#27c93f", "#ffbd2e", "#58a6ff", "#39d353", "#79c0ff", "#c9d1d9"]

W, H = 490, 440
TITLE_H = 30
PAD = 22
LINE = 22.5
FS = 12.5
KEY_W = 9 * FS * 0.6 + 8  # 9 monospace chars + a little air

STEP = 0.16  # seconds between rows


def anim(i):
    return "" if STATIC else f' class="r" style="animation-delay:{0.25 + i * STEP:.2f}s"'


def main():
    p = []
    p.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
             f'viewBox="0 0 {W} {H}" font-family="{MONO}">')
    if not STATIC:
        p.append("<style>"
                 "@keyframes r{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:none}}"
                 "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}"
                 ".r{animation:r .4s ease-out both}"
                 ".k{animation:blink 1s step-end infinite}"
                 "</style>")
    p.append(f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
             f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
             f'</linearGradient></defs>')
    p.append(f'<rect width="{W}" height="{H}" rx="12" fill="url(#bg)"/>')
    p.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}"/>')
    p.append(f'<line x1="0" y1="{TITLE_H}" x2="{W}" y2="{TITLE_H}" stroke="{FRAME}"/>')
    for i, col in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        p.append(f'<circle cx="{20 + i*16}" cy="{TITLE_H/2}" r="5" fill="{col}"/>')
    p.append(f'<text x="{W/2}" y="{TITLE_H/2 + 4}" fill="{DIM}" font-size="12" text-anchor="middle">'
             f'{USER}: ~$ neofetch</text>')

    y = TITLE_H + 30
    p.append(f'<text x="{PAD}" y="{y}" font-size="{FS + 1}" font-weight="bold"{anim(0)}>'
             f'<tspan fill="{KEY}">raiyaan</tspan><tspan fill="{INK}">@</tspan>'
             f'<tspan fill="{KEY}">github</tspan></text>')
    y += LINE * 0.8
    p.append(f'<text x="{PAD}" y="{y}" fill="{FRAME}" font-size="{FS}"{anim(0)}>{"-" * len(USER)}</text>')
    y += LINE * 0.95

    for i, (k, v) in enumerate(ROWS, start=1):
        p.append(f'<g{anim(i)}><text x="{PAD}" y="{y:.1f}" fill="{KEY}" font-size="{FS}" '
                 f'font-weight="bold">{escape(k)}</text>'
                 f'<text x="{PAD + KEY_W:.1f}" y="{y:.1f}" fill="{INK}" font-size="{FS}">{escape(v)}</text></g>')
        y += LINE

    # neofetch colour blocks
    y += 4
    blocks = "".join(f'<rect x="{PAD + j*22}" y="{y:.1f}" width="22" height="12" fill="{c}"/>'
                     for j, c in enumerate(BLOCKS))
    p.append(f'<g{anim(len(ROWS) + 1)}>{blocks}</g>')

    # prompt with blinking cursor
    py = H - 18
    p.append(f'<line x1="0" y1="{py - 20}" x2="{W}" y2="{py - 20}" stroke="{FRAME}"/>')
    p.append(f'<text x="{PAD}" y="{py}" font-size="12.5" xml:space="preserve"><tspan fill="{KEY}">~</tspan>'
             f'<tspan fill="{DIM}"> $ </tspan><tspan fill="{INK}">hire raiyaan --internship</tspan></text>')
    cursor_x = PAD + len("~ $ hire raiyaan --internship ") * 12.5 * 0.6
    blink = "" if STATIC else ' class="k"'
    p.append(f'<rect x="{cursor_x:.1f}" y="{py - 11}" width="7.5" height="14" fill="{INK}"{blink}/>')

    p.append("</svg>")
    with open(OUT, "w") as f:
        f.write("".join(p))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
