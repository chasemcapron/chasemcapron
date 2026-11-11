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
BAR_LEVELS = ["#2a313c", "#1f8a4c", "#28b862", "#33e078", "#39FF88"]
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
    parts = []

    # ---- isometric 3D contribution map (left) ----
    S = 12.5
    C, HS = S * 0.866, S * 0.5          # week axis -> (C, HS), day axis -> (-C, HS)
    HMAX = 90
    OX, OY = 24 + 7 * C + 4, 58 + HMAX

    def P(w, d, h=0.0):
        return (OX + (w - d) * C, OY + (w + d) * HS - h)

    def poly(pts, fill):
        return '<polygon points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + f'" fill="{fill}"/>'

    def shade(hexc, f):
        r, g, b = (int(hexc[i:i + 2], 16) for i in (1, 3, 5))
        return "#%02x%02x%02x" % (int(r * f), int(g * f), int(b * f))

    cells = []
    for wi, w in enumerate(weeks):
        for d in w["contributionDays"]:
            r = dt.date.fromisoformat(d["date"]).isoweekday() % 7
            cells.append((wi, r, d))
    cells.sort(key=lambda t: (t[0] + t[1], t[0]))   # back to front

    g = 0.12
    for wi, r, d in cells:
        n = d["contributionCount"]
        lv = level(n, mx)
        h = 3 + (HMAX * (n / mx) ** 0.5 if n else 0)
        topc = BAR_LEVELS[lv] if n else "#2a313c"
        a, b = wi + g, wi + 1 - g
        c0, c1 = r + g, r + 1 - g
        # right face (+w side) and left face (+d side), then top
        parts.append(poly([P(b, c0, h), P(b, c1, h), P(b, c1), P(b, c0)], shade(topc, 0.45)))
        parts.append(poly([P(a, c1, h), P(b, c1, h), P(b, c1), P(a, c1)], shade(topc, 0.7)))
        parts.append(
            poly([P(a, c0, h), P(b, c0, h), P(b, c1, h), P(a, c1, h)], topc)[:-2]
            + f'><title>{d["date"]}: {n}</title></polygon>'
        )
    map_bottom = P(len(weeks), 7)[1]
    parts.append(f'<text x="24" y="34" class="h">contributions · last 12 months</text>')

    # ---- right column: stats + languages ----
    RX = 714
    parts.append(f'<line x1="{RX - 20}" x2="{RX - 20}" y1="24" y2="{map_bottom}" stroke="{BORDER}"/>')
    parts.append(f'<text x="{RX}" y="58" class="big">{cal["totalContributions"]:,}</text>')
    parts.append(f'<text x="{RX}" y="78" class="l">contributions, last year</text>')
    y = 112
    for num, label in ((current, "day current streak"), (longest, "day longest streak"), (active, "active days")):
        parts.append(f'<text x="{RX}" y="{y}" class="n">{num}</text>')
        parts.append(f'<text x="{RX + 40}" y="{y}" class="l">{label}</text>')
        y += 26
    y += 18
    parts.append(f'<text x="{RX}" y="{y}" class="h">top languages</text>')
    y += 10
    bw = W - 24 - RX
    shown_max = top[0][1] if top else 1
    for i, (name, size) in enumerate(top):
        pct = 100 * size / total_size
        y += 24
        parts.append(f'<text x="{RX}" y="{y}" class="lg">{name}</text>')
        parts.append(f'<text x="{W - 24}" y="{y}" class="m" text-anchor="end">{pct:.0f}%</text>')
        parts.append(f'<rect x="{RX}" y="{y + 5}" width="{bw}" height="4" rx="2" fill="#262c36"/>')
        parts.append(f'<rect x="{RX}" y="{y + 5}" width="{max(4, bw * size / shown_max):.1f}" height="4" rx="2" fill="{LANG_SHADES[i]}"/>')

    updated = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    H = int(max(map_bottom, y + 20)) + 28
    parts.append(f'<text x="{W - 24}" y="{H - 16}" class="m" text-anchor="end">updated {updated}</text>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="GitHub contributions for {USER}">
<style>
  .big{{font:700 34px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;fill:{ACCENT}}}
  .n{{font:700 18px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;fill:{ACCENT}}}
  .l{{font:12px -apple-system,"Segoe UI",Helvetica,Arial,sans-serif;fill:{MUTED}}}
  .m{{font:11px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;fill:{MUTED}}}
  .h{{font:600 13px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;fill:{ACCENT}}}
  .lg{{font:12px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;fill:{TEXT}}}
</style>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="6" fill="{BG}" stroke="{BORDER}"/>
{"".join(parts)}
</svg>
'''
    # GitHub's image caches ignore query strings, so give every version its own
    # file name (content hash) and point the README at it. A changed map is
    # then a new URL that no cache has seen.
    import hashlib, re
    here = Path(__file__).parent
    digest = hashlib.sha1(svg.encode()).hexdigest()[:10]
    mdir = here / "assets" / "metrics"
    mdir.mkdir(parents=True, exist_ok=True)
    name = f"contributions-{digest}.svg"
    for old in mdir.glob("contributions-*.svg"):
        if old.name != name:
            old.unlink()
    (mdir / name).write_text(svg, encoding="utf-8")
    legacy = here / "assets" / "github-metrics.svg"
    if legacy.exists():
        legacy.unlink()
    readme = here / "README.md"
    text = readme.read_text(encoding="utf-8")
    text = re.sub(r'src="assets/(?:github-metrics\.svg[^"]*|metrics/contributions-[0-9a-f]+\.svg)"',
                  f'src="assets/metrics/{name}"', text)
    readme.write_text(text, encoding="utf-8")
    print(f"wrote assets/metrics/{name}: {cal['totalContributions']} contributions, streak {current}/{longest}, langs {[n for n, _ in top]}, {W}x{H}")


if __name__ == "__main__":
    main()
