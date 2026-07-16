#!/usr/bin/env python3
"""Generate assets/banner.svg — an animated, space-themed 'typing code' banner.

Self-contained SVG (SMIL animation, no JS, no external service) so it animates
directly on the GitHub profile. Re-run after editing NAME or CODE to rebuild.
"""

import os
import random

WIDTH, HEIGHT = 900, 260
NAME = "Patrick Daley"

# The hero line that types out, split into syntax-coloured segments.
CODE_SEGMENTS = [
    ("const ", "#c792ea"),   # keyword
    ("dev ", "#b39dff"),     # identifier
    ("= ", "#89ddff"),       # operator
    (f'"{NAME}"', "#ff9cf5"),  # string (the name)
    (";", "#8a7cb8"),        # punctuation
]

FONT = "'JetBrains Mono','Fira Code','SFMono-Regular',ui-monospace,monospace"
FONT_SIZE = 28
ADV = 16.8            # per-char advance; text is stretched to match (see textLength)
CODE_X, CODE_Y = 150, 150
STAR_SEED = 24


def _stars():
    rng = random.Random(STAR_SEED)
    out = []
    for _ in range(70):
        x = round(rng.uniform(0, WIDTH), 1)
        y = round(rng.uniform(0, HEIGHT), 1)
        r = round(rng.uniform(0.4, 1.7), 2)
        base = round(rng.uniform(0.25, 0.9), 2)
        dim = round(base * 0.25, 2)
        dur = round(rng.uniform(1.6, 4.2), 2)
        out.append(
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="#e9d5ff">'
            f'<animate attributeName="opacity" values="{base};{dim};{base}" '
            f'dur="{dur}s" repeatCount="indefinite"/></circle>'
        )
    return "".join(out)


def _typing_animation():
    """Discrete clip-reveal + a cursor that walks with it, then holds."""
    full_text = "".join(text for text, _ in CODE_SEGMENTS)
    n = len(full_text)

    widths = [round(i * ADV, 2) for i in range(n + 1)] + [round(n * ADV, 2)]
    xs = [round(CODE_X + w, 2) for w in widths]
    # Type over the first 60% of the loop, hold full for the rest.
    key_times = [round((i / n) * 0.6, 4) for i in range(n + 1)] + [1.0]

    kt = ";".join(str(k) for k in key_times)
    w_vals = ";".join(str(w) for w in widths)
    x_vals = ";".join(str(x) for x in xs)

    tspans = "".join(
        f'<tspan fill="{color}">{_esc(text)}</tspan>' for text, color in CODE_SEGMENTS
    )
    text_len = round(n * ADV, 2)

    return f"""
  <clipPath id="reveal">
    <rect x="{CODE_X}" y="{CODE_Y - 34}" width="0" height="48">
      <animate attributeName="width" values="{w_vals}" keyTimes="{kt}"
               dur="5s" calcMode="discrete" repeatCount="indefinite"/>
    </rect>
  </clipPath>
  <text x="{CODE_X}" y="{CODE_Y}" font-family="{FONT}" font-size="{FONT_SIZE}"
        font-weight="600" textLength="{text_len}" lengthAdjust="spacingAndGlyphs"
        clip-path="url(#reveal)">{tspans}</text>
  <rect y="{CODE_Y - 24}" width="11" height="30" rx="1.5" fill="#e9b3ff">
    <animate attributeName="x" values="{x_vals}" keyTimes="{kt}"
             dur="5s" calcMode="discrete" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="1;0" keyTimes="0;0.5"
             dur="0.9s" calcMode="discrete" repeatCount="indefinite"/>
  </rect>"""


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build():
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}"
     width="{WIDTH}" height="{HEIGHT}" role="img" aria-label="{NAME}">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0d0221"/>
      <stop offset="55%" stop-color="#1a0b2e"/>
      <stop offset="100%" stop-color="#241040"/>
    </linearGradient>
    <radialGradient id="neb1" cx="22%" cy="26%" r="60%">
      <stop offset="0%" stop-color="#7b2ff7" stop-opacity="0.45"/>
      <stop offset="100%" stop-color="#7b2ff7" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="neb2" cx="80%" cy="82%" r="55%">
      <stop offset="0%" stop-color="#ff2fd0" stop-opacity="0.30"/>
      <stop offset="100%" stop-color="#ff2fd0" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <rect width="{WIDTH}" height="{HEIGHT}" rx="14" fill="url(#sky)"/>
  <rect width="{WIDTH}" height="{HEIGHT}" rx="14" fill="url(#neb1)"/>
  <rect width="{WIDTH}" height="{HEIGHT}" rx="14" fill="url(#neb2)"/>
  {_stars()}

  <!-- terminal card -->
  <rect x="90" y="70" width="720" height="120" rx="12"
        fill="#160a2b" fill-opacity="0.72" stroke="#a55cff" stroke-opacity="0.9"/>
  <rect x="91.5" y="71.5" width="717" height="117" rx="11"
        fill="none" stroke="#d8b4ff" stroke-opacity="0.25"/>
  <circle cx="116" cy="93" r="5" fill="#ff5f8f"/>
  <circle cx="134" cy="93" r="5" fill="#c792ea"/>
  <circle cx="152" cy="93" r="5" fill="#89ddff"/>
  <text x="150" y="97" font-family="{FONT}" font-size="12"
        fill="#9d84c9" opacity="0.8"> ~/whoami</text>
  {_typing_animation()}
  <text x="{CODE_X}" y="178" font-family="{FONT}" font-size="13"
        fill="#9d84c9" letter-spacing="3">SOFTWARE &#183; SYSTEMS &#183; SPACE</text>
</svg>
"""
    out = os.path.join(os.path.dirname(__file__), "banner.svg")
    with open(out, "w") as f:
        f.write(svg)
    print(f"wrote {out}")


if __name__ == "__main__":
    build()
