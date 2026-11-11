"""Rewrite the header link buttons in README.md with custom green icons.

shields.io's icon set no longer includes LinkedIn or Outlook, so the icons
are drawn here and passed to shields as base64 data URIs.
Run:  python gen_badges.py
"""
import base64
import re
from pathlib import Path

G, BG = "#39FF88", "#161b22"

ICONS = {
    # terminal window with a >_ prompt
    "portfolio": f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
<rect x="2" y="3.5" width="20" height="17" rx="2.5" fill="none" stroke="{G}" stroke-width="2"/>
<path d="M6.5 9l3.5 3-3.5 3" fill="none" stroke="{G}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M12 15.5h5.5" stroke="{G}" stroke-width="2" stroke-linecap="round"/></svg>''',
    # rounded square with "in"
    "linkedin": f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
<rect x="1.5" y="1.5" width="21" height="21" rx="3.5" fill="{G}"/>
<circle cx="7.2" cy="7" r="1.7" fill="{BG}"/>
<rect x="5.7" y="10" width="3" height="8.5" fill="{BG}"/>
<path d="M11 10h2.9v1.3c.5-.9 1.7-1.6 3.1-1.6 2.6 0 3.2 1.7 3.2 3.9v4.9h-3v-4.3c0-1.1-.3-1.9-1.4-1.9-1.2 0-1.8.9-1.8 2.1v4.1H11z" fill="{BG}"/></svg>''',
    # envelope
    "email": f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
<rect x="2" y="4.5" width="20" height="15" rx="2.5" fill="none" stroke="{G}" stroke-width="2"/>
<path d="M3 6.5l9 6.5 9-6.5" fill="none" stroke="{G}" stroke-width="2" stroke-linejoin="round"/></svg>''',
}

LINKS = {
    "portfolio": ("Portfolio", "https://chasemcapron.github.io/chasecapron_io/"),
    "linkedin": ("LinkedIn", "https://www.linkedin.com/in/chasemcapron/"),
    "email": ("Email", "mailto:chasecapron@outlook.com"),
}


def badge(key):
    alt, url = LINKS[key]
    logo = base64.b64encode(" ".join(ICONS[key].split()).encode()).decode()
    src = f"https://img.shields.io/badge/{key}-161b22?style=for-the-badge&logo=data:image/svg%2bxml;base64,{logo}"
    return f'<a href="{url}"><img src="{src}" alt="{alt}"></a>'


readme = Path(__file__).parent / "README.md"
text = readme.read_text(encoding="utf-8")
for key in ICONS:
    # replace either the old markdown badge or a previously generated <a> badge
    text = re.sub(
        rf'(\[!\[{LINKS[key][0]}\]\(https://img\.shields\.io/badge/{key}-[^)]*\)\]\([^)]*\)'
        rf'|<a href="[^"]*"><img src="https://img\.shields\.io/badge/{key}-[^"]*" alt="{LINKS[key][0]}"></a>)',
        lambda _m, k=key: badge(k),
        text,
    )
readme.write_text(text, encoding="utf-8")
print("updated header badges")
