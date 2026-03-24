#!/usr/bin/env python3
"""
Attempt 13 — paint from understanding, not from plan.

What I finally saw:
  The harbor isn't dissolved — it's present in the same register as the fog.
  Same value, same temperature, but it has MASS. A large dark vessel center-left.
  Masts with weight. And crucially: the harbor reflects INTO the water on the
  left side — cool blue-grey marks that I've been completely ignoring.

  The painting is two worlds in one fog:
    LEFT:   harbor, industry, cool blue-grey mass — reflected downward into water
    RIGHT:  sun, open water, the orange column
  Both present. Neither canceling the other. The fog is what lets them coexist.

  Paint that. Bold. Don't hold back.
"""
from PIL import Image
import random, math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from brushes import sweep, dry, flat, dab, scatter, smear

OUT = os.path.dirname(os.path.abspath(__file__))
rng = random.Random(44)
img = Image.open(os.path.join(OUT, "attempt_12.png"))
px = img.load(); W, H = img.size

HORIZON_Y = 76

# Harbor tones — cool blue-grey, same value as fog, but present
HARBOR_MID  = (118, 132, 140)
HARBOR_DARK = ( 82,  96, 106)
HARBOR_MASS = ( 68,  82,  94)   # the dark vessel — heaviest tone in left half

# Water left-side reflection tones — harbor reversed into water
WATER_REFL  = (106, 128, 132)   # cool blue-grey marks on left water
WATER_REFL_D= ( 84, 104, 108)   # darker reflection marks

# ── HARBOR MASS ────────────────────────────────────────────────────────────────
# Large vessel / industrial structure center-left — this is what I was erasing.
# It sits at the horizon, extends upward. Not ghostly: present.

# Main hull/mass — straddles horizon, heavy
for y in range(HORIZON_Y - 18, HORIZON_Y + 8):
    for x in range(30, 100):
        t = (y - (HORIZON_Y - 18)) / 26
        # Denser toward center of mass, looser at edges
        cx_dist = abs(x - 64) / 36
        prob = 0.55 * (1.0 - cx_dist * 0.6) * (1.0 - abs(t - 0.5) * 0.4)
        if rng.random() < prob:
            px[x, y] = HARBOR_MID

# Darker core — the vessel body
for y in range(HORIZON_Y - 12, HORIZON_Y + 4):
    for x in range(38, 82):
        if rng.random() < 0.38:
            px[x, y] = HARBOR_DARK

# Darkest accent — hull waterline
for y in range(HORIZON_Y - 2, HORIZON_Y + 5):
    for x in range(44, 78):
        if rng.random() < 0.45:
            px[x, y] = HARBOR_MASS

# Masts — now with actual weight, not probability ghosts
for mx, top in [(52, 8), (66, 12), (78, 18), (90, 22)]:
    for y in range(top, HORIZON_Y + 2):
        px[mx, y] = HARBOR_MID
        if rng.random() < 0.6:
            px[mx + 1, y] = HARBOR_DARK
    # Cross spars on main mast
    if mx == 52:
        for x in range(44, 62):
            if rng.random() < 0.7:
                px[x, top + 14] = HARBOR_MID

# Second vessel suggestion — right of main mass, fainter
for y in range(HORIZON_Y - 8, HORIZON_Y + 3):
    for x in range(104, 130):
        if rng.random() < 0.18:
            px[x, y] = HARBOR_MID

# ── HARBOR REFLECTIONS IN WATER ────────────────────────────────────────────────
# The harbor reflects downward into the left water.
# Cool blue-grey horizontal marks — mirror of the mass above.
# This is what the left water is MADE of.

for _ in range(40):
    y  = rng.randint(HORIZON_Y + 2, HORIZON_Y + 50)
    x0 = rng.randint(0, 100)
    ln = rng.randint(10, 50)
    tone = rng.choice([WATER_REFL, WATER_REFL, WATER_REFL_D])
    flat(px, W, H, x0, x0 + ln, y, tone, gap=rng.uniform(0.1, 0.3), rng=rng)

# Darker reflection directly below the vessel mass
for _ in range(18):
    y  = rng.randint(HORIZON_Y + 4, HORIZON_Y + 28)
    x0 = rng.randint(30, 80)
    ln = rng.randint(8, 32)
    dry(px, W, H, x0, y, ln, WATER_REFL_D,
        gap=0.25, drift=0.4, rng=rng, clip_y=(HORIZON_Y, H))

# Smear gently horizontal — reflections on water should have surface movement
smear(px, W, H, 0, 140, HORIZON_Y + 2, HORIZON_Y + 55,
      direction='h', strength=0.25, rng=rng)

img.save(os.path.join(OUT, "attempt_13.png")); print("done")
