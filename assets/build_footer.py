#!/usr/bin/env python3
"""Generate assets/footer.svg — an animated purple starfield with shooting stars.

Matches banner.svg (same palette, self-contained SMIL, no JS). Re-run to rebuild.
"""

import os
import random

WIDTH, HEIGHT = 900, 150
STAR_SEED = 77


def _stars():
    rng = random.Random(STAR_SEED)
    out = []
    for _ in range(55):
        x = round(rng.uniform(0, WIDTH), 1)
        y = round(rng.uniform(0, HEIGHT), 1)
        r = round(rng.uniform(0.4, 1.5), 2)
        base = round(rng.uniform(0.3, 0.9), 2)
        dur = round(rng.uniform(1.6, 4.0), 2)
        out.append(
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="#e9d5ff">'
            f'<animate attributeName="opacity" values="{base};{round(base*0.2,2)};{base}" '
            f'dur="{dur}s" repeatCount="indefinite"/></circle>'
        )
    return "".join(out)


def _shooting_star(y0, delay, dur):
    """A head + tapered tail that streaks diagonally across, then repeats."""
    x_start, x_end = -80, WIDTH + 80
    y_end = y0 + 90
    return f"""
  <g opacity="0">
    <line x1="0" y1="0" x2="-46" y2="-17" stroke="url(#trail)" stroke-width="2.4"
          stroke-linecap="round"/>
    <circle cx="0" cy="0" r="2.6" fill="#ffffff"/>
    <animateTransform attributeName="transform" type="translate"
        values="{x_start} {y0}; {x_end} {y_end}" dur="{dur}s"
        begin="{delay}s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.1;0.8;1"
        dur="{dur}s" begin="{delay}s" repeatCount="indefinite"/>
  </g>"""


def build():
    shooting = "".join(
        _shooting_star(y0, delay, dur)
        for y0, delay, dur in [(20, 0, 3.2), (55, 1.4, 3.8), (10, 2.6, 2.8), (75, 3.9, 4.2)]
    )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}"
     width="{WIDTH}" height="{HEIGHT}" role="img" aria-label="thanks for stopping by">
  <defs>
    <linearGradient id="fsky" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#241040"/>
      <stop offset="50%" stop-color="#150827"/>
      <stop offset="100%" stop-color="#0d0221"/>
    </linearGradient>
    <radialGradient id="fneb" cx="50%" cy="120%" r="70%">
      <stop offset="0%" stop-color="#7b2ff7" stop-opacity="0.4"/>
      <stop offset="100%" stop-color="#7b2ff7" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="trail" x1="1" y1="1" x2="0" y2="0">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="#b388ff" stop-opacity="0"/>
    </linearGradient>
  </defs>

  <rect width="{WIDTH}" height="{HEIGHT}" rx="14" fill="url(#fsky)"/>
  <rect width="{WIDTH}" height="{HEIGHT}" rx="14" fill="url(#fneb)"/>
  {_stars()}
  {shooting}
  <text x="{WIDTH/2}" y="{HEIGHT/2+5}" text-anchor="middle"
        font-family="'JetBrains Mono','Fira Code',ui-monospace,monospace"
        font-size="18" fill="#d8b4ff" letter-spacing="4">
    &#10022; THANKS FOR STOPPING BY &#10022;
  </text>
</svg>
"""
    out = os.path.join(os.path.dirname(__file__), "footer.svg")
    with open(out, "w") as f:
        f.write(svg)
    print(f"wrote {out}")


if __name__ == "__main__":
    build()
