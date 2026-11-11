"""Generate dark project cards (assets/proj-*.svg) in the header's palette.

Run:  python gen_cards.py
Edit PROJECTS to change cards. Descriptions wrap automatically (3 lines max).
"""
import textwrap
from pathlib import Path

W, H = 440, 172
BG, BORDER, ACCENT, TEXT, MUTED, PILL = "#161b22", "#30363d", "#39FF88", "#c9d1d9", "#8b949e", "#0d1117"

PROJECTS = [
    {
        "file": "proj-phishing.svg",
        "name": "gone-phishing",
        "desc": "Paste a link or text, get an explainable verdict. Typosquat, TLD and domain-age checks plus Safe Browsing, VirusTotal and URLhaus. Analyst view with IOCs and ATT&CK.",
        "tags": ["TypeScript", "React", "MITRE ATT&CK", "live app"],
    },
    {
        "file": "proj-ai-security.svg",
        "name": "ai-security",
        "desc": "Governed chat for a local LLM. A policy proxy blocks forbidden keywords, PII (SSNs, card numbers) and prompt-injection attempts before they reach the model.",
        "tags": ["Python", "Flask", "Ollama", "LLM guardrails"],
    },
    {
        "file": "proj-file-integrity.svg",
        "name": "file-integrity",
        "desc": "Host-based file integrity monitor. Baselines a directory with SHA-256 hashes, then alerts on modified, added or deleted files. Standard library only.",
        "tags": ["Python", "SHA-256", "HIDS", "CLI"],
    },
    {
        "file": "proj-wavelength.svg",
        "name": "wavelength",
        "desc": "Song recommendation tool built at the 2025 TAMU Datathon. Give it your favorite songs and it returns similar tracks.",
        "tags": ["Python", "Data", "Hackathon"],
    },
]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def card(p):
    lines = textwrap.wrap(p["desc"], 58)
    assert len(lines) <= 3, f"{p['name']}: description too long ({len(lines)} lines)"
    desc = "".join(
        f'<text x="20" y="{70 + i * 19}" class="d">{esc(l)}</text>' for i, l in enumerate(lines)
    )
    x = 20
    pills = []
    for t in p["tags"]:
        w = int(len(t) * 6.6) + 18
        pills.append(
            f'<rect x="{x}" y="{H - 44}" width="{w}" height="22" rx="11" class="p"/>'
            f'<text x="{x + w / 2}" y="{H - 29}" class="pt" text-anchor="middle">{esc(t)}</text>'
        )
        x += w + 8
    # three-block pixel glyph, echoing the header
    glyph = (
        f'<g fill="{ACCENT}"><rect x="20" y="22" width="7" height="7"/>'
        f'<rect x="28" y="22" width="7" height="7"/><rect x="20" y="30" width="7" height="7"/></g>'
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(p['name'])}">
<style>
  .t{{font:600 15px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;fill:{ACCENT}}}
  .r{{font:12px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;fill:{MUTED}}}
  .d{{font:13px -apple-system,"Segoe UI",Helvetica,Arial,sans-serif;fill:{TEXT}}}
  .p{{fill:{PILL};stroke:{BORDER}}}
  .pt{{font:11px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;fill:{ACCENT}}}
</style>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="6" fill="{BG}" stroke="{BORDER}"/>
{glyph}
<text x="44" y="35" class="t">{esc(p['name'])}</text>
<text x="{W - 20}" y="35" class="r" text-anchor="end">repo &#8599;</text>
{desc}
{''.join(pills)}
</svg>
'''


out = Path(__file__).parent / "assets"
out.mkdir(exist_ok=True)
for p in PROJECTS:
    (out / p["file"]).write_text(card(p), encoding="utf-8")
    print("wrote", out / p["file"])
