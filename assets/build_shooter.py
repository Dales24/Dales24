#!/usr/bin/env python3
"""Generate assets/shooter.svg — a self-contained space-shooter animation.

A ship sweeps the bottom firing bullets upward while a field of asteroids
explodes one by one, then the wave resets and loops. Pure SMIL SVG (no JS, no
external service), matching the banner/footer palette. Re-run to rebuild.
"""

import os
import random

WIDTH, HEIGHT = 900, 260
LOOP = 10.0          # seconds per wave
STAR_SEED = 91
ROCK_SEED = 42


def _stars():
    rng = random.Random(STAR_SEED)
    out = []
    for _ in range(55):
        x, y = round(rng.uniform(0, WIDTH), 1), round(rng.uniform(0, HEIGHT), 1)
        r = round(rng.uniform(0.4, 1.4), 2)
        base = round(rng.uniform(0.25, 0.8), 2)
        dur = round(rng.uniform(1.8, 4.0), 2)
        out.append(
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="#e9d5ff">'
            f'<animate attributeName="opacity" values="{base};{round(base*0.2,2)};{base}" '
            f'dur="{dur}s" repeatCount="indefinite"/></circle>'
        )
    return "".join(out)


def _asteroids():
    """Scattered rocks that drift, then explode in sequence across the wave."""
    rng = random.Random(ROCK_SEED)
    spots = []
    for _ in range(9):
        spots.append((round(rng.uniform(120, 780), 1), round(rng.uniform(35, 150), 1)))

    out = ""
    for i, (x, y) in enumerate(spots):
        # Each rock is destroyed at a staggered moment in the loop.
        hit = round(0.15 + (i / (len(spots) - 1)) * 0.7, 3)
        drift = round(rng.uniform(-8, 8), 1)
        dur = round(rng.uniform(4.0, 7.0), 1)
        tint = rng.choice(["#9f86d6", "#b388ff", "#8f78c0"])

        rock = (
            f'<g transform="translate({x} {y})">'
            f'<use href="#rock" fill="{tint}"/>'
            f'<animate attributeName="opacity" values="1;1;0;0" '
            f'keyTimes="0;{hit};{round(hit+0.02,3)};1" dur="{LOOP}s" '
            f'calcMode="discrete" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="translate" additive="sum" '
            f'values="0 0;{drift} 6;0 0" dur="{dur}s" repeatCount="indefinite"/>'
            f'</g>'
        )
        boom = (
            f'<use href="#boom" x="{x}" y="{y}" opacity="0">'
            f'<animate attributeName="opacity" values="0;0;1;0;0" '
            f'keyTimes="0;{round(hit-0.02,3)};{hit};{round(hit+0.05,3)};1" '
            f'dur="{LOOP}s" repeatCount="indefinite"/></use>'
        )
        out += rock + boom
    return out


def _ship_and_bullets():
    """Ship group sweeps left↔right; bullets rise from it and repeat."""
    bullets = ""
    for begin in (0.0, 0.35, 0.7, 1.05):
        bullets += (
            f'<rect x="-2" y="-14" width="4" height="14" rx="2" fill="#89ddff">'
            f'<animate attributeName="y" values="-14;-170" dur="0.75s" '
            f'begin="{begin}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="1;1;0" keyTimes="0;0.7;1" '
            f'dur="0.75s" begin="{begin}s" repeatCount="indefinite"/></rect>'
        )
    ship = (
        '<path d="M0 -16 L13 10 L4 6 L0 12 L-4 6 L-13 10 Z" fill="#c8a2ff" '
        'stroke="#e9b3ff" stroke-width="1.5" stroke-linejoin="round"/>'
        '<circle cx="0" cy="-2" r="3" fill="#89ddff"/>'
        '<path d="M-4 10 L0 20 L4 10 Z" fill="#ff9d3c" opacity="0.9">'
        '<animate attributeName="opacity" values="0.9;0.3;0.9" dur="0.25s" '
        'repeatCount="indefinite"/></path>'
    )
    return (
        f'<g transform="translate(120 216)">{bullets}{ship}'
        f'<animateTransform attributeName="transform" type="translate" '
        f'values="120 216;780 216;120 216" keyTimes="0;0.5;1" '
        f'dur="{LOOP/2}s" repeatCount="indefinite"/></g>'
    )


def build():
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}"
     width="{WIDTH}" height="{HEIGHT}" role="img" aria-label="space shooter">
  <defs>
    <linearGradient id="gsky" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0d0221"/>
      <stop offset="55%" stop-color="#160a2b"/>
      <stop offset="100%" stop-color="#241040"/>
    </linearGradient>
    <radialGradient id="gneb" cx="30%" cy="20%" r="60%">
      <stop offset="0%" stop-color="#7b2ff7" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="#7b2ff7" stop-opacity="0"/>
    </radialGradient>
    <!-- one asteroid: polygon inherits the instance fill; craters are fixed -->
    <g id="rock">
      <polygon points="-13,-4 -7,-12 5,-13 13,-4 11,7 2,13 -8,11 -14,3"/>
      <circle cx="-4" cy="-2" r="2.5" fill="#00000055"/>
      <circle cx="5" cy="4" r="2" fill="#00000055"/>
    </g>
    <!-- explosion burst -->
    <path id="boom" d="M0,-13 4,-4 13,-3 6,3 9,12 0,6 -9,12 -6,3 -13,-3 -4,-4 Z"
          fill="#ff5fd0" stroke="#ffd15c" stroke-width="1"/>
  </defs>

  <rect width="{WIDTH}" height="{HEIGHT}" rx="14" fill="url(#gsky)"/>
  <rect width="{WIDTH}" height="{HEIGHT}" rx="14" fill="url(#gneb)"/>
  {_stars()}
  {_asteroids()}
  {_ship_and_bullets()}
</svg>
"""
    out = os.path.join(os.path.dirname(__file__), "shooter.svg")
    with open(out, "w") as f:
        f.write(svg)
    print(f"wrote {out}")


if __name__ == "__main__":
    build()
