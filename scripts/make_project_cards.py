#!/usr/bin/env python3
"""
One terminal-style card per featured repo, written to cards/<repo>.svg so each
can link to its repo in the README. Edit PROJECTS to change them.

    python scripts/make_project_cards.py      (STATIC=1 for frozen frames)
"""
import os
import sys
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from term import BRIGHT, DIM, FRAME, GREEN, INK, TITLE_H, anim, open_svg, wrap  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "cards")
STATIC = bool(os.environ.get("STATIC"))

# (repo, display name, description, language, language colour, tags)
PROJECTS = [
    ("vaultdb", "VaultDB",
     "A database built from scratch in Go: crash-safe log, B-tree index, SQL, "
     "TCP server and HNSW vector search. Runs in your browser via WebAssembly.",
     "Go", "#00ADD8", ["databases", "systems", "wasm"]),
    ("gpt-from-scratch", "GPT from scratch",
     "A GPT language model built from scratch in PyTorch, trained on "
     "Shakespeare, running live in the browser.",
     "Python", "#3572A5", ["pytorch", "transformers", "llm"]),
    ("nexus", "NEXUS",
     "Advisor and client portal with an AI assistant. Next.js 16, React 19, "
     "TypeScript. Hackathon team project.",
     "TypeScript", "#3178C6", ["nextjs", "ai-assistant", "hackathon"]),
    ("vaXease", "VaXease",
     "Vaccination compliance platform with HR, parent and nurse portals. "
     "Hult Prize entry.",
     "HTML", "#E34C26", ["healthtech", "hult-prize", "web"]),
]

W, H = 430, 178
PAD = 22


def card(i, repo, name, desc, lang, color, tags):
    d = 0.15 + i * 0.12
    p = open_svg(W, H, f"~/{repo.lower()} $ cat README", STATIC)
    p.append(f'<text x="{PAD}" y="{TITLE_H + 32}" fill="{BRIGHT}" font-size="18" font-weight="bold"'
             f'{anim("rise", d, STATIC)}>{escape(name)}</text>')
    p.append(f'<text x="{W - PAD}" y="{TITLE_H + 31}" fill="{DIM}" font-size="11" text-anchor="end"'
             f'{anim("fade", d + 0.1, STATIC)}>github.com/ABDULRAIYAAN/{escape(repo)}</text>'
             if len(repo) < 12 else "")
    for j, line in enumerate(wrap(desc, 56)[:3]):
        p.append(f'<text x="{PAD}" y="{TITLE_H + 58 + j * 18}" fill="{INK}" font-size="12"'
                 f'{anim("fade", d + 0.15 + j * 0.06, STATIC)}>{escape(line)}</text>')
    fy = H - 20
    p.append(f'<line x1="0" y1="{fy - 20}" x2="{W}" y2="{fy - 20}" stroke="{FRAME}"/>')
    p.append(f'<g{anim("fade", d + 0.35, STATIC)}><circle cx="{PAD + 5}" cy="{fy - 4}" r="5.5" fill="{color}"/>'
             f'<text x="{PAD + 16}" y="{fy}" fill="{INK}" font-size="12">{escape(lang)}</text>')
    tx = PAD + 16 + len(lang) * 7.2 + 18
    for t in tags:
        tw = len(t) * 6.6 + 14
        p.append(f'<rect x="{tx:.1f}" y="{fy - 14}" width="{tw:.1f}" height="19" rx="9.5" fill="none" stroke="{FRAME}"/>'
                 f'<text x="{tx + tw/2:.1f}" y="{fy - 0.5}" fill="{GREEN}" font-size="11" text-anchor="middle">{escape(t)}</text>')
        tx += tw + 6
    p.append("</g></svg>")
    return "".join(p)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for i, pr in enumerate(PROJECTS):
        path = os.path.join(OUT_DIR, f"{pr[0].lower()}.svg")
        with open(path, "w") as f:
            f.write(card(i, *pr))
        print("wrote", path)


if __name__ == "__main__":
    main()
