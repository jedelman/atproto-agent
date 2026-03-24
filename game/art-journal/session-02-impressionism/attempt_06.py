#!/usr/bin/env python3
"""
Stroke: thicken the warm atmosphere in the upper sky.
Load attempt_05 as canvas. Add warm density, don't rebuild.
"""
from PIL import Image
import random, math, os

OUT = os.path.dirname(os.path.abspath(__file__))
rng = random.Random(7)

img = Image.open(os.path.join(OUT, "attempt_05.png"))
px = img.load()
W, H = img.size

SKY_WARM_A = (196, 158, 106)
SKY_WARM_B = (178, 138,  88)
SKY_COOL   = (148, 158, 158)   # cooler marks to weave between warm
HORIZON_Y  = 76


def curved_stroke(x0, y, length, tone, gap=0.10, curve=0.4):
    cy = float(y)
    direction = rng.choice([-1, 1])
    for i in range(length):
        cy += direction * curve * math.sin(i / max(length, 1) * math.pi)
        cx = x0 + i
        if 0 <= cx < W and 0 <= int(cy) < HORIZON_Y:
            if rng.random() >= gap:
                px[cx, int(cy)] = tone


# Upper sky: dense warm passes, upper-left biased
for _ in range(45):
    y  = rng.randint(0, HORIZON_Y // 2)
    x0 = rng.randint(-20, W // 2)
    ln = rng.randint(30, 110)
    tone = rng.choice([SKY_WARM_A, SKY_WARM_A, SKY_WARM_B, SKY_COOL])
    curved_stroke(x0, y, ln, tone, gap=0.10, curve=rng.uniform(0.2, 0.55))

# Lower sky (horizon zone): cooler, quieter — let it breathe before water
for _ in range(12):
    y  = rng.randint(HORIZON_Y // 2, HORIZON_Y - 4)
    x0 = rng.randint(0, W - 40)
    ln = rng.randint(20, 60)
    curved_stroke(x0, y, ln, SKY_COOL, gap=0.20, curve=rng.uniform(0.1, 0.25))

img.save(os.path.join(OUT, "attempt_06.png"))
print("done")
