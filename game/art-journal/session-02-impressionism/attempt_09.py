#!/usr/bin/env python3
"""
Stroke: fix the boat shadow — smear, not comb.
The hull's dark should bleed into the water organically, not in rows.
"""
from PIL import Image
import random, os

OUT = os.path.dirname(os.path.abspath(__file__))
rng = random.Random(9)

img = Image.open(os.path.join(OUT, "attempt_08.png"))
px = img.load()
W, H = img.size

BOAT_SHADOW = ( 38,  40,  36)   # dark but with slight teal — water eating the dark


def px_set(x, y, tone):
    if 0 <= x < W and 0 <= y < H:
        px[x, y] = tone


def get_px(x, y):
    if 0 <= x < W and 0 <= y < H:
        return px[x, y]
    return (0, 0, 0)


# Overwrite the comb zone with a proper diffuse smear
# Sample from the water color at each position and blend dark into it
ny = 136
for y in range(ny + 2, ny + 16):
    t = (y - (ny + 2)) / 14   # 0=dark, 1=water
    for x in range(64, 112):
        water = get_px(x, ny + 16)   # sample water color from below the smear
        # Probability of placing dark falls off with distance and distance from hull center
        center_dist = abs(x - 87) / 25.0
        prob = (1.0 - t * 0.85) * (1.0 - center_dist * 0.5)
        if rng.random() < prob:
            r = int(BOAT_SHADOW[0] + (water[0] - BOAT_SHADOW[0]) * t)
            g = int(BOAT_SHADOW[1] + (water[1] - BOAT_SHADOW[1]) * t)
            b = int(BOAT_SHADOW[2] + (water[2] - BOAT_SHADOW[2]) * t)
            px_set(x, y, (r, g, b))

img.save(os.path.join(OUT, "attempt_09.png"))
print("done")
