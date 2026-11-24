#!/usr/bin/env python3
"""
Draw data/contributions.json as an animated terminal-window heatmap SVG:
53 weeks x 7 days of rounded cells that slide in once along the diagonal,
month labels, a legend and a stats footer.

    python scripts/render_heatmap_svg.py [out.svg]

Set STATIC=1 for a frozen frame (handy for previews).
"""
import datetime
import json
import os
import sys
from html import escape

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATA = os.environ.get("DATA_FILE", os.path.join(ROOT, "data", "contributions.json"))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "contrib-heatmap.svg")
STATIC = bool(os.environ.get("STATIC"))

BG, BG2 = "#0d1117", "#111722"
FRAME = "#30363d"
DIM = "#7d8590"
INK = "#c9d1d9"
GREEN = "#39d353"
LEVELS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

W = 860
TITLE_H = 30
CELL, GAP = 12, 3
STEP = CELL + GAP
GRID_X = 46
MONTH_Y = TITLE_H + 28
GRID_Y = MONTH_Y + 10
GRID_H = 7 * STEP - GAP
LEGEND_Y = GRID_Y + GRID_H + 26
RULE_Y = LEGEND_Y + 16
FOOT_Y = RULE_Y + 24
H = FOOT_Y + 18


def fmt_date(s):
    if not s:
        return "-"
    return datetime.date.fromisoformat(s).strftime("%d %b %Y")


def main():
    with open(DATA) as f:
        data = json.load(f)
    days = data["days"][-371:]
    if not days:
        sys.exit("contributions.json has no days")

    first = datetime.date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7  # Sunday = 0, like GitHub's calendar

    p = []
    p.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
             f'viewBox="0 0 {W} {H}" font-family="{MONO}">')
    p.append("<style>"
             "@keyframes in{from{opacity:0;transform:translate(-6px,-6px)}to{opacity:1;transform:none}}"
             "@keyframes fade{from{opacity:0}to{opacity:1}}"
             "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}"
             ".c{animation:in .45s ease-out both;transform-box:fill-box}"
             ".f{animation:fade .6s ease-out both}"
             ".k{animation:blink 1s step-end infinite}"
             "</style>" if not STATIC else "")
    p.append(f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
             f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
             f'</linearGradient></defs>')
    p.append(f'<rect width="{W}" height="{H}" rx="12" fill="url(#bg)"/>')
    p.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}"/>')
    p.append(f'<line x1="0" y1="{TITLE_H}" x2="{W}" y2="{TITLE_H}" stroke="{FRAME}"/>')
    for i, col in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        p.append(f'<circle cx="{20 + i*16}" cy="{TITLE_H/2}" r="5" fill="{col}"/>')
    p.append(f'<text x="{W/2}" y="{TITLE_H/2 + 4}" fill="{DIM}" font-size="12" text-anchor="middle">'
             f'raiyaan@github: ~$ ./contributions.sh --last-year</text>')

    # weekday labels
    for d, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        y = GRID_Y + d * STEP + CELL - 2
        p.append(f'<text x="14" y="{y}" fill="{DIM}" font-size="10">{name}</text>')

    # cells + month labels
    last_month = None
    last_label_x = -100
    for i, day in enumerate(days):
        idx = i + offset
        w, d = divmod(idx, 7)
        x = GRID_X + w * STEP
        y = GRID_Y + d * STEP
        date = datetime.date.fromisoformat(day["date"])
        # label a month at the first week column that starts in it
        if (d == 0 or i == 0) and date.month != last_month:
            if x - last_label_x > 30:
                p.append(f'<text x="{x}" y="{MONTH_Y}" fill="{DIM}" font-size="10">'
                         f'{date.strftime("%b")}</text>')
                last_label_x = x
            last_month = date.month
        color = LEVELS[max(0, min(4, day.get("level", 0)))]
        style = "" if STATIC else f' class="c" style="animation-delay:{(w + d) * 0.017:.3f}s"'
        p.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" fill="{color}"{style}>'
                 f'<title>{day["count"]} on {day["date"]}</title></rect>')

    fade = "" if STATIC else ' class="f" style="animation-delay:1.1s"'

    # total + legend
    p.append(f'<text x="{GRID_X}" y="{LEGEND_Y}" fill="{INK}" font-size="12"{fade}>'
             f'<tspan fill="{GREEN}" font-weight="bold">{data["total"]:,}</tspan> contributions in the last year</text>')
    lx = GRID_X + 53 * STEP - GAP - (5 * STEP - GAP) - 34
    p.append(f'<g{fade}><text x="{lx - 34}" y="{LEGEND_Y}" fill="{DIM}" font-size="10">Less</text>')
    for k, col in enumerate(LEVELS):
        p.append(f'<rect x="{lx + k*STEP}" y="{LEGEND_Y - 10}" width="{CELL}" height="{CELL}" rx="2.5" fill="{col}"/>')
    p.append(f'<text x="{lx + 5*STEP + 4}" y="{LEGEND_Y}" fill="{DIM}" font-size="10">More</text></g>')

    # footer stats
    p.append(f'<line x1="0" y1="{RULE_Y}" x2="{W}" y2="{RULE_Y}" stroke="{FRAME}"/>')
    best = data.get("best_day") or {}
    stats = [
        ("streak", f'{data["current_streak"]}d'),
        ("longest", f'{data["longest_streak"]}d'),
        ("active days", f'{data["active_days"]}'),
        ("best day", f'{best.get("count", 0)} on {fmt_date(best.get("date"))}'),
    ]
    spans = "  ".join(
        f'<tspan fill="{DIM}">{escape(k)}</tspan> <tspan fill="{INK}">{escape(v)}</tspan>'
        for k, v in stats)
    p.append(f'<text x="20" y="{FOOT_Y}" font-size="12" xml:space="preserve"{fade}>'
             f'<tspan fill="{GREEN}">$</tspan> {spans}</text>')
    p.append(f'<text x="{W - 20}" y="{FOOT_Y}" fill="{DIM}" font-size="11" text-anchor="end"{fade}>'
             f'updated {fmt_date(data.get("updated"))}</text>')

    p.append("</svg>")
    with open(OUT, "w") as f:
        f.write("".join(p))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
