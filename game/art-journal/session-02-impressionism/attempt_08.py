#!/usr/bin/env python3
"""
Stroke: sink the near boat into the water.
Hull needs a dark reflection/shadow below it — the dark bleeds down.
Figures need to read as hunched bodies, not vertical bars.
"""
from PIL import Image
import random, os

OUT = os.path.dirname(os.path.abspath(__file__))
rng = random.Random(5)

img = Image.open(os.path.join(OUT, "attempt_07.png"))
px = img.load()
W, H = img.size

BOAT      = ( 18,  14,  10)
BOAT_FADE = ( 52,  58,  54)   # dark-but-not-black: shadow dissolving into water


def px_set(x, y, tone):
    if 0 <= x < W and 0 <= y < H:
        px[x, y] = tone


# Near boat reference: hull at y=136, x 64–110
ny = 136

# Shadow/reflection beneath hull — dark smear dissolving into water
for y in range(ny + 3, ny + 14):
    fade_t = (y - (ny + 3)) / 11   # 0 = dark, 1 = dissolved
    for x in range(68, 107):
        if rng.random() < (1.0 - fade_t * 0.75):
            # Interpolate from near-boat-dark toward water tone
            r = int(BOAT[0] + (BOAT_FADE[0] - BOAT[0]) * fade_t)
            g = int(BOAT[1] + (BOAT_FADE[1] - BOAT[1]) * fade_t)
            b = int(BOAT[2] + (BOAT_FADE[2] - BOAT[2]) * fade_t)
            px_set(x, y, (r, g, b))

# Redraw figures — erase the vertical bars first, replace with hunched forms
# Figure 1: left figure, slightly taller, bent forward (rower posture)
for y in range(ny - 18, ny):
    px_set(80, y, px[80, ny])    # clear (set to hull color at base)
    px_set(81, y, px[81, ny])
    px_set(82, y, px[82, ny])

# Figure 1: rower — head tilts forward, back rounds, arms reach
# Head: small cluster high
for dx in range(-1, 2):
    for dy in range(-2, 1):
        if rng.random() < 0.75:
            px_set(80 + dx, ny - 16 + dy, BOAT)
# Back/torso: rounded, leaning forward
for i in range(7):
    x_off = i // 2
    px_set(80 + x_off, ny - 14 + i, BOAT)
    if rng.random() < 0.6:
        px_set(81 + x_off, ny - 14 + i, BOAT)
# Arms reaching: diagonal strokes forward
for i in range(5):
    px_set(83 + i, ny - 8 + i // 2, BOAT)

# Figure 2: right figure, more upright, slight lean back (stroke recovery)
for y in range(ny - 13, ny):
    px_set(96, y, px[96, ny])
    px_set(97, y, px[97, ny])

# Head
for dx in range(-1, 2):
    for dy in range(-2, 1):
        if rng.random() < 0.7:
            px_set(96 + dx, ny - 12 + dy, BOAT)
# Torso: more upright
for i in range(6):
    px_set(96, ny - 10 + i, BOAT)
    if rng.random() < 0.55:
        px_set(97, ny - 10 + i, BOAT)

img.save(os.path.join(OUT, "attempt_08.png"))
print("done")
