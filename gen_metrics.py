"""Generate assets/github-metrics.svg: contribution map, streaks and top languages.

Runs daily in GitHub Actions (uses the built-in GITHUB_TOKEN, no secret needed).
Locally:  python gen_metrics.py   (falls back to `gh auth token`)
"""
import datetime as dt
import json
import os
import subprocess
import urllib.request
from pathlib import Path

USER = "chasemcapron"
IGNORED_LANGS = {"HTML", "CSS", "SCSS"}

BG, BORDER, ACCENT, TEXT, MUTED = "#161b22", "#30363d", "#39FF88", "#e6edf3", "#8b949e"
LEVELS = ["#1c2128", "#0e4429", "#006d32", "#26a641", "#39FF88"]
LANG_SHADES = ["#39FF88", "#26c46a", "#1f9e55", "#177a42", "#10572f", "#0a3a20"]

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
      nodes {
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
      }
    }
  }
}
"""


def token():
    t = os.environ.get("GITHUB_TOKEN")
    if t:
        return t
    return subprocess.check_output(["gh", "auth", "token"], text=True).strip()


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {token()}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(data["errors"])
    return data["data"]["user"]


def level(n, mx):
    if n == 0:
        return 0
    q = n / mx
    return 1 if q <= 0.25 else 2 if q <= 0.5 else 3 if q <= 0.75 else 4


def streaks(days):
    longest = cur = 0
    for d in days:
        cur = cur + 1 if d["contributionCount"] else 0
        longest = max(longest, cur)
    # current streak: today may still be empty without breaking it
    current = 0
    seq = list(days)
    if seq and seq[-1]["contributionCount"] == 0:
        seq = seq[:-1]
    for d in reversed(seq):
        if not d["contributionCount"]:
            break
        current += 1
    return current, longest


def main():
    u = fetch()
    cal = u["contributionsCollection"]["contributionCalendar"]
    weeks = cal["weeks"]
    days = [d for w in weeks for d in w["contributionDays"]]
    mx = max((d["contributionCount"] for d in days), default=1) or 1
    current, longest = streaks(days)
    active = sum(1 for d in days if d["contributionCount"])

    langs = {}
    for repo in u["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            name = e["node"]["name"]
            if name not in IGNORED_LANGS:
                langs[name] = langs.get(name, 0) + e["size"]
    total_size = sum(langs.values()) or 1
    top = [kv for kv in sorted(langs.items(), key=lambda kv: -kv[1])[:6] if kv[1] / total_size >= 0.01]

    W = 900
    CELL, GAP = 12, 3
    gx, gy = 52, 92
    parts = []

    # stats row
    stats = [
        (f"{cal['totalContributions']:,}", "contributions, last year"),
        (f"{current}", "day current streak"),
        (f"{longest}", "day longest streak"),
        (f"{active}", "active days"),
    ]
    col = (W - 48) / len(stats)
    for i, (num, label) in enumerate(stats):
        x = 24 + col * i + col / 2
        parts.append(f'<text x="{x}" y="46" class="n" text-anchor="middle">{num}</text>')
        parts.append(f'<text x="{x}" y="66" class="l" text-anchor="middle">{label}</text>')
    parts.append(f'<line x1="24" x2="{W - 24}" y1="80" y2="80" stroke="{BORDER}"/>')

    # month labels
    last_month = None
    for wi, w in enumerate(weeks):
        d0 = dt.date.fromisoformat(w["contributionDays"][0]["date"])
        if d0.month != last_month and wi < len(weeks) - 2:
            parts.append(f'<text x="{gx + wi * (CELL + GAP)}" y="{gy + 4}" class="m">{d0.strftime("%b")}</text>')
            last_month = d0.month
    # weekday labels
    for r, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        parts.append(f'<text x="{gx - 8}" y="{gy + 14 + r * (CELL + GAP) + 10}" class="m" text-anchor="end">{name}</text>')

    # grid
    for wi, w in enumerate(weeks):
        for d in w["contributionDays"]:
            r = dt.date.fromisoformat(d["date"]).isoweekday() % 7  # Sun=0
            x = gx + wi * (CELL + GAP)
            y = gy + 14 + r * (CELL + GAP)
            c = LEVELS[level(d["contributionCount"], mx)]
            parts.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{c}">'
                f'<title>{d["date"]}: {d["contributionCount"]}</title></rect>'
            )
    grid_bottom = gy + 14 + 7 * (CELL + GAP)

    # legend
    lx = W - 24 - 5 * (CELL + GAP) - 34
    parts.append(f'<text x="{lx - 8}" y="{grid_bottom + 18}" class="m" text-anchor="end">less</text>')
    for i, c in enumerate(LEVELS):
        parts.append(f'<rect x="{lx + i * (CELL + GAP)}" y="{grid_bottom + 8}" width="{CELL}" height="{CELL}" rx="2" fill="{c}"/>')
    parts.append(f'<text x="{lx + 5 * (CELL + GAP) + 4}" y="{grid_bottom + 18}" class="m">more</text>')

    # languages bar
    ly = grid_bottom + 44
    parts.append(f'<line x1="24" x2="{W - 24}" y1="{ly - 10}" y2="{ly - 10}" stroke="{BORDER}"/>')
    parts.append(f'<text x="24" y="{ly + 14}" class="h">top languages</text>')
    bx, bw = 24, W - 48
    x = bx
    shown = sum(s for _, s in top) or 1
    parts.append(f'<clipPath id="bar"><rect x="{bx}" y="{ly + 26}" width="{bw}" height="10" rx="5"/></clipPath><g clip-path="url(#bar)">')
    for i, (name, size) in enumerate(top):
        w = bw * size / shown
        parts.append(f'<rect x="{x}" y="{ly + 26}" width="{w + 0.5}" height="10" fill="{LANG_SHADES[i]}"/>')
        x += w
    parts.append("</g>")
    x = bx
    for i, (name, size) in enumerate(top):
        pct = 100 * size / total_size
        parts.append(f'<rect x="{x}" y="{ly + 50}" width="9" height="9" rx="2" fill="{LANG_SHADES[i]}"/>')
        label = f"{name} {pct:.0f}%"
        parts.append(f'<text x="{x + 14}" y="{ly + 59}" class="lg">{label}</text>')
        x += 14 + len(label) * 7.4 + 22
    H = ly + 78

    updated = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    parts.append(f'<text x="{W - 24}" y="{ly + 14}" class="m" text-anchor="end">updated {updated}</text>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="GitHub contributions for {USER}">
<style>
  .n{{font:700 26px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;fill:{ACCENT}}}
  .l{{font:12px -apple-system,"Segoe UI",Helvetica,Arial,sans-serif;fill:{MUTED}}}
  .m{{font:11px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;fill:{MUTED}}}
  .h{{font:600 13px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;fill:{ACCENT}}}
  .lg{{font:12px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;fill:{TEXT}}}
</style>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="6" fill="{BG}" stroke="{BORDER}"/>
{"".join(parts)}
</svg>
'''
    out = Path(__file__).parent / "assets" / "github-metrics.svg"
    out.write_text(svg, encoding="utf-8")
    print(f"wrote {out}: {cal['totalContributions']} contributions, streak {current}/{longest}, langs {[n for n, _ in top]}")


if __name__ == "__main__":
    main()
