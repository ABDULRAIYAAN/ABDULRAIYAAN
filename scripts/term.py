"""Shared terminal-window look for every card in the profile README."""
from html import escape

BG, BG2 = "#0d1117", "#111722"
TILE = "#161b22"
FRAME = "#30363d"
DIM = "#7d8590"
INK = "#c9d1d9"
BRIGHT = "#e6edf3"
GREEN = "#39d353"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
TITLE_H = 30

BASE_CSS = (
    "@keyframes rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}"
    "@keyframes fade{from{opacity:0}to{opacity:1}}"
    "@keyframes pop{0%{opacity:0;transform:scale(.4)}70%{opacity:1;transform:scale(1.08)}100%{opacity:1;transform:none}}"
    "@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}"
    "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}"
    ".rise{animation:rise .5s ease-out both}"
    ".fade{animation:fade .6s ease-out both}"
    ".pop{animation:pop .5s ease-out both;transform-box:fill-box;transform-origin:center}"
    ".grow{animation:grow .6s ease-out both;transform-box:fill-box;transform-origin:bottom}"
    ".k{animation:blink 1s step-end infinite}"
)


def open_svg(w, h, title, static=False, extra_css=""):
    css = "" if static else f"<style>{BASE_CSS}{extra_css}</style>"
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
         f'viewBox="0 0 {w} {h}" font-family="{MONO}">', css,
         f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
         f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
         f'</linearGradient></defs>',
         f'<rect width="{w}" height="{h}" rx="12" fill="url(#bg)"/>',
         f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="12" fill="none" stroke="{FRAME}"/>',
         f'<line x1="0" y1="{TITLE_H}" x2="{w}" y2="{TITLE_H}" stroke="{FRAME}"/>']
    for i, col in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        p.append(f'<circle cx="{20 + i*16}" cy="{TITLE_H/2}" r="5" fill="{col}"/>')
    p.append(f'<text x="{w/2}" y="{TITLE_H/2 + 4}" fill="{DIM}" font-size="12" '
             f'text-anchor="middle">{escape(title)}</text>')
    return p


def anim(cls, delay, static=False):
    if static:
        return ""
    return f' class="{cls}" style="animation-delay:{delay:.2f}s"'


def wrap(text, width):
    """Greedy word wrap to a max number of monospace characters per line."""
    lines, cur = [], ""
    for word in text.split():
        if cur and len(cur) + 1 + len(word) > width:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}" if cur else word
    if cur:
        lines.append(cur)
    return lines
