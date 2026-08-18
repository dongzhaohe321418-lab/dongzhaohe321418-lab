#!/usr/bin/env python3
"""Generate assets/stats.svg — a stats terminal matching the profile's other terminals.

Reads GitHub GraphQL output from stats-data.json (produced by `gh api graphql` in CI),
renders a 900px-wide dark terminal SVG with the same typewriter loop as about.svg.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "stats-data.json"
OUT = ROOT / "assets" / "stats.svg"

LANG_COLORS = {
    "Python": "#3572A5", "HTML": "#e34c26", "TypeScript": "#3178c6",
    "Jupyter Notebook": "#DA5B0B", "Shell": "#89e051", "JavaScript": "#f1e05a",
    "CSS": "#663399", "Swift": "#F05138",
}

user = json.loads(DATA.read_text())["data"]["user"]
followers = user["followers"]["totalCount"]
repos = user["repositories"]
repo_count = repos["totalCount"]
stars = sum(n["stargazerCount"] for n in repos["nodes"])
commits = user["contributionsCollection"]["totalCommitContributions"]
prs = user["contributionsCollection"]["totalPullRequestContributions"]

langs = {}
for n in repos["nodes"]:
    lang = (n.get("primaryLanguage") or {}).get("name")
    if lang:
        langs[lang] = langs.get(lang, 0) + 1
top = sorted(langs.items(), key=lambda kv: -kv[1])[:3]
total_lang = sum(langs.values()) or 1

# language bars (printed after the second command types out)
BAR_X, BAR_W = 360, 300
lang_rows = []
for i, (name, cnt) in enumerate(top):
    pct = cnt / total_lang
    y = 240 + i * 28
    color = LANG_COLORS.get(name, "#8b949e")
    lang_rows.append(
        f'<g class="fd l{i}">'
        f'<text x="28" y="{y}"><tspan class="cmd">{name}</tspan>'
        f'<tspan class="out" x="{BAR_X + BAR_W + 16}">{pct:4.0%}</tspan></text>'
        f'<rect x="{BAR_X}" y="{y - 13}" width="{BAR_W}" height="12" rx="3" fill="#21262d"/>'
        f'<rect x="{BAR_X}" y="{y - 13}" width="{max(6, round(BAR_W * pct))}" height="12" rx="3" fill="{color}"/>'
        f"</g>"
    )
lang_svg = "\n    ".join(lang_rows)

# big-number stat cards: instant read, one glance
CARDS = [
    (commits, "commits · 12 mo", "#58a6ff"),
    (stars, "stars earned", "#d29922"),
    (repo_count, "public repos", "#bc8cff"),
    (followers, "followers", "#3fb950"),
]
card_rows = []
for i, (num, label, color) in enumerate(CARDS):
    x = 28 + i * 216
    card_rows.append(
        f'<g class="fd o{i}">'
        f'<rect x="{x}" y="88" width="200" height="76" rx="8" fill="#161b22" stroke="#30363d"/>'
        f'<rect x="{x}" y="88" width="200" height="3" rx="1.5" fill="{color}" opacity=".8"/>'
        f'<text x="{x + 100}" y="128" text-anchor="middle" style="font: 700 30px \'SFMono-Regular\', Consolas, monospace; fill: {color}">{num}</text>'
        f'<text x="{x + 100}" y="151" text-anchor="middle" class="out" style="font-size:12.5px">{label}</text>'
        f"</g>"
    )
cards_svg = "\n    ".join(card_rows)

svg = f'''<svg width="900" height="330" viewBox="0 0 900 330" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="GitHub stats: {commits} commits, {stars} stars, {repo_count} public repos, {followers} followers">
  <defs>
    <clipPath id="s1"><rect class="tw s1" x="28" y="52" height="24" width="0"/></clipPath>
    <clipPath id="s2"><rect class="tw s2" x="28" y="192" height="24" width="0"/></clipPath>
    <clipPath id="wc"><rect x="1" y="1" width="898" height="328" rx="12"/></clipPath>
    <linearGradient id="edge" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#58a6ff"/><stop offset="50%" stop-color="#bc8cff"/><stop offset="100%" stop-color="#3fb950"/>
    </linearGradient>
    <linearGradient id="crtg" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#8bb4ff" stop-opacity="0"/><stop offset="50%" stop-color="#8bb4ff" stop-opacity=".045"/><stop offset="100%" stop-color="#8bb4ff" stop-opacity="0"/>
    </linearGradient>
    <pattern id="grid" width="22" height="22" patternUnits="userSpaceOnUse">
      <circle cx="1" cy="1" r="1" fill="#1b2230"/>
    </pattern>
    <filter id="glow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="0" stdDeviation="8" flood-color="#58a6ff" flood-opacity="0.15"/>
    </filter>
    <style>
      .win {{ fill: #0d1117; stroke: #30363d; stroke-width: 1; }}
      .bar {{ fill: #161b22; }}
      .t {{ font: 500 15px 'SFMono-Regular', 'Fira Code', Consolas, monospace; }}
      .prompt {{ fill: #3fb950; }}
      .cmd {{ fill: #e6edf3; }}
      .out {{ fill: #8b949e; }}
      .hl {{ fill: #58a6ff; }}
      .tw {{ animation-duration: 12s; animation-iteration-count: infinite; animation-timing-function: linear; }}
      .s1 {{ animation-name: s1; }}
      .s2 {{ animation-name: s2; }}
      @keyframes s1 {{ 0%,2% {{ width: 0; animation-timing-function: steps(30); }} 10%,96% {{ width: 320px; }} 98%,100% {{ width: 0; }} }}
      @keyframes s2 {{ 0%,30% {{ width: 0; animation-timing-function: steps(18); }} 38%,96% {{ width: 200px; }} 98%,100% {{ width: 0; }} }}
      .fd {{ opacity: 0; animation-duration: 12s; animation-iteration-count: infinite; animation-timing-function: linear; }}
      .o0 {{ animation-name: o0; }} @keyframes o0 {{ 0%,11% {{opacity:0}} 12%,96% {{opacity:1}} 98%,100% {{opacity:0}} }}
      .o1 {{ animation-name: o1; }} @keyframes o1 {{ 0%,14% {{opacity:0}} 15%,96% {{opacity:1}} 98%,100% {{opacity:0}} }}
      .o2 {{ animation-name: o2; }} @keyframes o2 {{ 0%,17% {{opacity:0}} 18%,96% {{opacity:1}} 98%,100% {{opacity:0}} }}
      .o3 {{ animation-name: o3; }} @keyframes o3 {{ 0%,20% {{opacity:0}} 21%,96% {{opacity:1}} 98%,100% {{opacity:0}} }}
      .l0 {{ animation-name: l0; }} @keyframes l0 {{ 0%,40% {{opacity:0}} 42%,96% {{opacity:1}} 98%,100% {{opacity:0}} }}
      .l1 {{ animation-name: l1; }} @keyframes l1 {{ 0%,44% {{opacity:0}} 46%,96% {{opacity:1}} 98%,100% {{opacity:0}} }}
      .l2 {{ animation-name: l2; }} @keyframes l2 {{ 0%,48% {{opacity:0}} 50%,96% {{opacity:1}} 98%,100% {{opacity:0}} }}
      .o9 {{ animation-name: o9; }} @keyframes o9 {{ 0%,56% {{opacity:0}} 58%,96% {{opacity:1}} 98%,100% {{opacity:0}} }}
      .pulse2 {{ animation: pl2 2.4s ease-in-out infinite; }}
      @keyframes pl2 {{ 0%,100% {{ opacity: .3; }} 50% {{ opacity: 1; }} }}
      .crt {{ animation: crt 8s linear infinite; }}
      @keyframes crt {{ from {{ transform: translateY(-80px); }} to {{ transform: translateY(410px); }} }}
      .cursor {{ animation: blink 1s steps(1) infinite; }}
      @keyframes blink {{ 0%,49% {{ opacity: 1; }} 50%,100% {{ opacity: 0; }} }}
    </style>
  </defs>

  <rect x="1" y="1" width="898" height="328" rx="12" class="win" filter="url(#glow)"/>
  <rect x="1" y="1" width="898" height="328" rx="12" fill="url(#grid)" opacity=".55"/>
  <rect x="1" y="1" width="898" height="328" rx="12" fill="none" stroke="url(#edge)" opacity=".4"/>
  <g clip-path="url(#wc)"><rect x="1" y="0" width="898" height="70" fill="url(#crtg)" class="crt"/></g>
  <path d="M1 13 a12 12 0 0 1 12 -12 h874 a12 12 0 0 1 12 12 v27 h-898 z" class="bar"/>
  <circle cx="856" cy="21" r="4" fill="#3fb950" class="pulse2"/>
  <text x="866" y="25" class="t prompt" style="font-size:11px">live</text>
  <circle cx="24" cy="21" r="6" fill="#ff5f57"/>
  <circle cx="46" cy="21" r="6" fill="#febc2e"/>
  <circle cx="68" cy="21" r="6" fill="#28c840"/>
  <text x="450" y="26" text-anchor="middle" class="t out">eric@github: ~/stats · refreshed daily</text>

  <g class="t">
    <g clip-path="url(#s1)">
      <text x="28" y="70"><tspan class="prompt">$</tspan> <tspan class="cmd">gh stats --user dongzhaohe321418-lab</tspan></text>
    </g>
    {cards_svg}
    <g clip-path="url(#s2)">
      <text x="28" y="210"><tspan class="prompt">$</tspan> <tspan class="cmd">gh langs --top 3</tspan></text>
    </g>
    {lang_svg}
    <g class="fd o9">
      <text x="28" y="306"><tspan class="prompt">$</tspan></text>
      <rect x="46" y="293" width="9" height="17" fill="#e6edf3" class="cursor"/>
    </g>
  </g>
</svg>
'''

OUT.write_text(svg)
print(f"wrote {OUT} ({commits} commits, {stars} stars, {repo_count} repos, {followers} followers, langs: {[t[0] for t in top]})", file=sys.stderr)
