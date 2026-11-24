#!/usr/bin/env python3
"""
Contributions per month for the last 12 months as animated bars, from
data/contributions.json. Refreshed daily by the workflow.

    python scripts/render_activity_svg.py [out.svg]      (STATIC=1 for a frozen frame)
"""
import datetime
import json
import os
import sys
from collections import OrderedDict
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from term import DIM, FRAME, GREEN, INK, TITLE_H, anim, open_svg  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATA = os.environ.get("DATA_FILE", os.path.join(ROOT, "data", "contributions.json"))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "activity.svg")
STATIC = bool(os.environ.get("STATIC"))

W, H = 860, 230
CHART_TOP = TITLE_H + 34
CHART_H = 110
BASE = CHART_TOP + CHART_H
LEVELS = ["#0e4429", "#006d32", "#26a641", "#39d353"]


def main():
    with open(DATA) as f:
        data = json.load(f)

    months = OrderedDict()
    for d in data["days"]:
        months[d["date"][:7]] = months.get(d["date"][:7], 0) + d["count"]
    items = list(months.items())[-12:]
    peak = max((v for _, v in items), default=0) or 1
    busiest = max(items, key=lambda kv: kv[1]) if items else ("", 0)

    p = open_svg(W, H, "raiyaan@github: ~$ ./activity.sh --by-month", STATIC)
    n = len(items)
    slot = (W - 80) / max(n, 1)
    bw = min(40, slot * 0.6)

    for k in range(1, 4):
        gy = BASE - CHART_H * k / 4
        p.append(f'<line x1="40" y1="{gy:.1f}" x2="{W - 40}" y2="{gy:.1f}" stroke="{FRAME}" '
                 f'stroke-dasharray="2 5"/>')
    p.append(f'<line x1="40" y1="{BASE}" x2="{W - 40}" y2="{BASE}" stroke="{FRAME}"/>')

    for i, (ym, v) in enumerate(items):
        cx = 40 + slot * i + slot / 2
        h = max(2, CHART_H * v / peak) if v else 2
        color = LEVELS[min(3, int(v / peak * 3.999))] if v else "#161b22"
        d = 0.2 + i * 0.07
        p.append(f'<rect x="{cx - bw/2:.1f}" y="{BASE - h:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="4" '
                 f'fill="{color}"{anim("grow", d, STATIC)}/>')
        p.append(f'<text x="{cx:.1f}" y="{BASE - h - 7:.1f}" fill="{INK}" font-size="11" text-anchor="middle"'
                 f'{anim("fade", d + 0.4, STATIC)}>{v}</text>')
        label = datetime.date.fromisoformat(ym + "-01").strftime("%b")
        p.append(f'<text x="{cx:.1f}" y="{BASE + 17}" fill="{DIM}" font-size="10.5" '
                 f'text-anchor="middle">{label}</text>')

    fy = H - 16
    p.append(f'<line x1="0" y1="{fy - 21}" x2="{W}" y2="{fy - 21}" stroke="{FRAME}"/>')
    bm = datetime.date.fromisoformat(busiest[0] + "-01").strftime("%B %Y") if busiest[0] else "-"
    avg = sum(v for _, v in items) / max(n, 1)
    p.append(f'<text x="20" y="{fy}" font-size="12" xml:space="preserve"{anim("fade", 1.2, STATIC)}>'
             f'<tspan fill="{GREEN}">$</tspan> <tspan fill="{DIM}">busiest month</tspan> '
             f'<tspan fill="{INK}">{escape(bm)} ({busiest[1]})</tspan>  '
             f'<tspan fill="{DIM}">monthly average</tspan> <tspan fill="{INK}">{avg:.0f}</tspan></text>')
    p.append("</svg>")
    with open(OUT, "w") as f:
        f.write("".join(p))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
