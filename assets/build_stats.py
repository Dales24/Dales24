#!/usr/bin/env python3
"""Generate assets/stats.svg — a self-hosted GitHub stats card.

Pulls live numbers from the GitHub GraphQL API via the `gh` CLI (uses GH_TOKEN /
the Action's GITHUB_TOKEN) and renders a purple space-themed card that matches
banner.svg. No third-party image service, so it never breaks server-side.
"""

import json
import os
import random
import subprocess

USER = "Dales24"
WIDTH, HEIGHT = 900, 300
FONT = "'JetBrains Mono','Fira Code','SFMono-Regular',ui-monospace,monospace"
STAR_SEED = 5

QUERY = """
{ user(login:"%s") {
    followers { totalCount }
    repositories(first:100, ownerAffiliations:OWNER, isFork:false) {
      totalCount
      nodes {
        stargazerCount
        languages(first:8, orderBy:{field:SIZE, direction:DESC}) {
          edges { size node { name color } }
        }
      }
    }
    contributionsCollection { totalCommitContributions totalPullRequestContributions }
} }
""" % USER


def _fetch():
    out = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={QUERY}"],
        capture_output=True, text=True, check=True,
    ).stdout
    user = json.loads(out)["data"]["user"]
    repos = user["repositories"]["nodes"]

    langs: dict[str, dict] = {}
    for repo in repos:
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            entry = langs.setdefault(name, {"size": 0, "color": edge["node"]["color"] or "#b388ff"})
            entry["size"] += edge["size"]

    top = sorted(langs.items(), key=lambda kv: kv[1]["size"], reverse=True)[:5]
    total = sum(v["size"] for _, v in top) or 1

    return {
        "commits": user["contributionsCollection"]["totalCommitContributions"],
        "prs": user["contributionsCollection"]["totalPullRequestContributions"],
        "stars": sum(r["stargazerCount"] for r in repos),
        "repos": user["repositories"]["totalCount"],
        "followers": user["followers"]["totalCount"],
        "langs": [(n, v["color"], v["size"] / total) for n, v in top],
    }


def _stars_bg():
    rng = random.Random(STAR_SEED)
    out = []
    for _ in range(60):
        x, y = round(rng.uniform(0, WIDTH), 1), round(rng.uniform(0, HEIGHT), 1)
        r = round(rng.uniform(0.4, 1.5), 2)
        base = round(rng.uniform(0.25, 0.8), 2)
        dur = round(rng.uniform(1.8, 4.0), 2)
        out.append(
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="#e9d5ff">'
            f'<animate attributeName="opacity" values="{base};{round(base*0.2,2)};{base}" '
            f'dur="{dur}s" repeatCount="indefinite"/></circle>'
        )
    return "".join(out)


def _stat_cells(data):
    cells = [
        ("Commits (yr)", data["commits"]),
        ("Pull requests", data["prs"]),
        ("Stars", data["stars"]),
        ("Repos", data["repos"]),
        ("Followers", data["followers"]),
    ]
    out = ""
    step = (WIDTH - 120) / len(cells)
    for i, (label, value) in enumerate(cells):
        cx = 60 + step * (i + 0.5)
        out += (
            f'<text x="{cx:.1f}" y="150" text-anchor="middle" font-family="{FONT}" '
            f'font-size="34" font-weight="700" fill="#f0e6ff">{value}</text>'
            f'<text x="{cx:.1f}" y="174" text-anchor="middle" font-family="{FONT}" '
            f'font-size="12" fill="#9d84c9">{label}</text>'
        )
    return out


def _lang_bar(langs):
    bar_x, bar_y, bar_w, bar_h = 60, 220, WIDTH - 120, 16
    segments, legend = "", ""
    x = bar_x
    for i, (name, color, frac) in enumerate(langs):
        w = frac * bar_w
        segments += f'<rect x="{x:.1f}" y="{bar_y}" width="{w:.1f}" height="{bar_h}" fill="{color}"/>'
        x += w
        lx = bar_x + (bar_w / len(langs)) * i
        legend += (
            f'<circle cx="{lx+6:.1f}" cy="266" r="5" fill="{color}"/>'
            f'<text x="{lx+18:.1f}" y="270" font-family="{FONT}" font-size="12" '
            f'fill="#c9b8e8">{_esc(name)} {frac*100:.0f}%</text>'
        )
    return (
        f'<clipPath id="barclip"><rect x="{bar_x}" y="{bar_y}" width="{bar_w}" '
        f'height="{bar_h}" rx="8"/></clipPath>'
        f'<g clip-path="url(#barclip)">{segments}</g>'
        f'<text x="{bar_x}" y="208" font-family="{FONT}" font-size="13" '
        f'fill="#b388ff" letter-spacing="2">TOP LANGUAGES</text>{legend}'
    )


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build():
    data = _fetch()
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}"
     width="{WIDTH}" height="{HEIGHT}" role="img" aria-label="{USER} GitHub stats">
  <defs>
    <linearGradient id="ssky" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0d0221"/>
      <stop offset="55%" stop-color="#1a0b2e"/>
      <stop offset="100%" stop-color="#241040"/>
    </linearGradient>
    <radialGradient id="sneb" cx="85%" cy="15%" r="55%">
      <stop offset="0%" stop-color="#ff2fd0" stop-opacity="0.22"/>
      <stop offset="100%" stop-color="#ff2fd0" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="{WIDTH}" height="{HEIGHT}" rx="14" fill="url(#ssky)"/>
  <rect width="{WIDTH}" height="{HEIGHT}" rx="14" fill="url(#sneb)"/>
  <rect x="1" y="1" width="{WIDTH-2}" height="{HEIGHT-2}" rx="13" fill="none"
        stroke="#a55cff" stroke-opacity="0.5"/>
  {_stars_bg()}
  <text x="60" y="60" font-family="{FONT}" font-size="22" font-weight="700"
        fill="#e9b3ff">&#10022; {USER} &#183; GitHub stats</text>
  {_stat_cells(data)}
  {_lang_bar(data["langs"])}
</svg>
"""
    out = os.path.join(os.path.dirname(__file__), "stats.svg")
    with open(out, "w") as f:
        f.write(svg)
    print(f"wrote {out}  ({data['commits']} commits, {len(data['langs'])} langs)")


if __name__ == "__main__":
    build()
