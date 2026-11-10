"""Generate assets/education.svg: education/certs panel with pixel-art icons.

Run:  python gen_edu.py
"""
from pathlib import Path

W = 900
ROW = 52
BG, BORDER, ACCENT, TEXT, MUTED = "#161b22", "#30363d", "#39FF88", "#e6edf3", "#8b949e"
PX = 3  # pixel size for icons (11x11 grid -> 33px)

ICONS = {
    "cap": [
        "...........",
        ".....X.....",
        "...XXXXX...",
        ".XXXXXXXXX.",
        "XXXXXXXXXXX",
        ".XXXXXXXXX.",
        "..XXXXXXX.X",
        "..X.....X.X",
        "..XXXXXXX.X",
        "..........X",
        ".........XX",
    ],
    "cert": [
        "XXXXXXXXXXX",
        "X.........X",
        "X.XXXXXXX.X",
        "X.........X",
        "X.XXXXX...X",
        "X.........X",
        "X.....XXX.X",
        "X....XXXXXX",
        "XXXXXXXXXXX",
        "......X.X..",
        "......X.X..",
    ],
    "shield": [
        "XXXXXXXXXXX",
        "X.........X",
        "X....X....X",
        "X...XXX...X",
        "X..XXXXX..X",
        "X....X....X",
        ".X...X...X.",
        ".X.......X.",
        "..X.....X..",
        "...X...X...",
        "....XXX....",
    ],
}

ROWS = [
    ("cap", "M.S. Management Information Systems", "Texas A&M University", "Dec 2026"),
    ("cert", "Cybersecurity Management Certificate", "Texas A&M University · Mays", "Dec 2026"),
    ("cap", "B.B.A. Management Information Systems", "University of Oklahoma", "2024"),
    ("shield", "CompTIA Security+", "CompTIA", "in progress"),
]


def esc(s):
    return s.replace("&", "&amp;")


def icon(name, x, y):
    return "".join(
        f'<rect x="{x + c * PX}" y="{y + r * PX}" width="{PX}" height="{PX}"/>'
        for r, row in enumerate(ICONS[name]) for c, v in enumerate(row) if v == "X"
    )


H = 16 + ROW * len(ROWS) + 16
parts = []
for i, (ic, title, org, when) in enumerate(ROWS):
    y = 16 + i * ROW
    if i:
        parts.append(f'<line x1="24" x2="{W - 24}" y1="{y}" y2="{y}" stroke="{BORDER}"/>')
    parts.append(f'<g fill="{ACCENT}">{icon(ic, 24, y + 9)}</g>')
    parts.append(f'<text x="76" y="{y + 32}" class="t">{esc(title)}</text>')
    parts.append(f'<text x="{W - 150}" y="{y + 32}" class="o" text-anchor="end">{esc(org)}</text>')
    status = "s2" if when == "in progress" else "s"
    parts.append(f'<text x="{W - 24}" y="{y + 32}" class="{status}" text-anchor="end">{esc(when)}</text>')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Education and certifications">
<style>
  .t{{font:600 15px -apple-system,"Segoe UI",Helvetica,Arial,sans-serif;fill:{TEXT}}}
  .o{{font:14px -apple-system,"Segoe UI",Helvetica,Arial,sans-serif;fill:{MUTED}}}
  .s{{font:13px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;fill:{ACCENT}}}
  .s2{{font:13px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;fill:{ACCENT};animation:p 1.6s ease-in-out infinite}}
  @keyframes p{{50%{{opacity:.35}}}}
</style>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="6" fill="{BG}" stroke="{BORDER}"/>
{"".join(parts)}
</svg>
'''
out = Path(__file__).parent / "assets" / "education.svg"
out.write_text(svg, encoding="utf-8")
print("wrote", out)
