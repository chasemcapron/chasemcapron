"""Generate assets/header.svg: pixel-block name in the Claude Code style.

Run:  python gen_header.py
Edit LINES to change the text (A-Z and space only).
"""
from pathlib import Path

LINES = ["CHASE", "CAPRON"]

CELL = 16          # px per block
GAP = 1            # cells between letters
LINE_GAP = 2       # cells between lines
PAD = 2            # cells of padding around everything

BG = "#0d1117"
FILL = "#39FF88"
GRID = "#1f9e55"
OUTLINE = "#39FF88"

FONT = {
    "A": ["XXXXX", "X...X", "X...X", "XXXXX", "X...X", "X...X", "X...X"],
    "B": ["XXXX.", "X...X", "X...X", "XXXX.", "X...X", "X...X", "XXXX."],
    "C": ["XXXXX", "X....", "X....", "X....", "X....", "X....", "XXXXX"],
    "D": ["XXXX.", "X...X", "X...X", "X...X", "X...X", "X...X", "XXXX."],
    "E": ["XXXXX", "X....", "X....", "XXXX.", "X....", "X....", "XXXXX"],
    "F": ["XXXXX", "X....", "X....", "XXXX.", "X....", "X....", "X...."],
    "G": ["XXXXX", "X....", "X....", "X..XX", "X...X", "X...X", "XXXXX"],
    "H": ["X...X", "X...X", "X...X", "XXXXX", "X...X", "X...X", "X...X"],
    "I": ["XXXXX", "..X..", "..X..", "..X..", "..X..", "..X..", "XXXXX"],
    "J": ["XXXXX", "....X", "....X", "....X", "....X", "X...X", "XXXXX"],
    "K": ["X...X", "X..X.", "X.X..", "XX...", "X.X..", "X..X.", "X...X"],
    "L": ["X....", "X....", "X....", "X....", "X....", "X....", "XXXXX"],
    "M": ["X...X", "XX.XX", "X.X.X", "X...X", "X...X", "X...X", "X...X"],
    "N": ["X...X", "XX..X", "XX..X", "X.X.X", "X..XX", "X..XX", "X...X"],
    "O": ["XXXXX", "X...X", "X...X", "X...X", "X...X", "X...X", "XXXXX"],
    "P": ["XXXXX", "X...X", "X...X", "XXXXX", "X....", "X....", "X...."],
    "Q": ["XXXXX", "X...X", "X...X", "X...X", "X.X.X", "X..X.", "XXX.X"],
    "R": ["XXXXX", "X...X", "X...X", "XXXXX", "X.X..", "X..X.", "X...X"],
    "S": ["XXXXX", "X....", "X....", "XXXXX", "....X", "....X", "XXXXX"],
    "T": ["XXXXX", "..X..", "..X..", "..X..", "..X..", "..X..", "..X.."],
    "U": ["X...X", "X...X", "X...X", "X...X", "X...X", "X...X", "XXXXX"],
    "V": ["X...X", "X...X", "X...X", "X...X", "X...X", ".X.X.", "..X.."],
    "W": ["X...X", "X...X", "X...X", "X...X", "X.X.X", "XX.XX", "X...X"],
    "X": ["X...X", "X...X", ".X.X.", "..X..", ".X.X.", "X...X", "X...X"],
    "Y": ["X...X", "X...X", ".X.X.", "..X..", "..X..", "..X..", "..X.."],
    "Z": ["XXXXX", "....X", "...X.", "..X..", ".X...", "X....", "XXXXX"],
    " ": [".....", ".....", ".....", ".....", ".....", ".....", "....."],
}

cells = set()
cursor = None
for li, line in enumerate(LINES):
    oy = PAD + li * (7 + LINE_GAP)
    for i, ch in enumerate(line):
        ox = PAD + i * (5 + GAP)
        for r, row in enumerate(FONT[ch]):
            for c, v in enumerate(row):
                if v == "X":
                    cells.add((ox + c, oy + r))
    if li == len(LINES) - 1:
        cursor = (PAD + len(line) * (5 + GAP), oy + 6)

w_cells = 2 * PAD + max(len(l) * (5 + GAP) - GAP for l in LINES) + 2  # room for cursor
h_cells = 2 * PAD + len(LINES) * 7 + (len(LINES) - 1) * LINE_GAP
W, H = w_cells * CELL, h_cells * CELL

# Silhouette outline: every cell edge that borders an empty cell.
segs = []
for (x, y) in cells:
    px, py = x * CELL, y * CELL
    if (x, y - 1) not in cells: segs.append(f"M{px} {py}h{CELL}")
    if (x, y + 1) not in cells: segs.append(f"M{px} {py + CELL}h{CELL}")
    if (x - 1, y) not in cells: segs.append(f"M{px} {py}v{CELL}")
    if (x + 1, y) not in cells: segs.append(f"M{px + CELL} {py}v{CELL}")
outline_d = "".join(segs)

rects = "".join(
    f'<rect x="{x * CELL}" y="{y * CELL}" width="{CELL}" height="{CELL}"/>'
    for (x, y) in sorted(cells)
)

cx, cy = cursor
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{' '.join(LINES)}">
<style>
  .blk{{fill:{FILL};stroke:{GRID};stroke-width:0.8}}
  .ol{{fill:none;stroke:{OUTLINE};stroke-width:2;stroke-linecap:square}}
  .cur{{fill:{FILL};animation:blink 1.1s steps(1,end) infinite}}
  @keyframes blink{{50%{{opacity:0}}}}
</style>
<rect width="{W}" height="{H}" rx="12" fill="{BG}"/>
<path class="ol" transform="translate(10,10)" d="{outline_d}"/>
<path class="ol" transform="translate(6,6)" d="{outline_d}"/>
<g class="blk">{rects}</g>
<rect class="cur" x="{cx * CELL}" y="{cy * CELL}" width="{CELL}" height="{CELL}"/>
</svg>
'''

out = Path(__file__).parent / "assets" / "header.svg"
out.parent.mkdir(exist_ok=True)
out.write_text(svg, encoding="utf-8")
print(f"wrote {out} ({W}x{H})")
