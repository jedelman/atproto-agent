#!/usr/bin/env python3
"""
Stroke: weave cool passages back into the warm upper sky.
The warm took over — it needs something to be warm against.
Short, varied, fewer. Let the canvas show.
"""
from PIL import Image
import random, math, os

OUT = os.path.dirname(os.path.abspath(__file__))
rng = random.Random(13)

img = Image.open(os.path.join(OUT, "attempt_06.png"))
px = img.load()
W, H = img.size

SKY_COOL_A = (142, 155, 158)   # blue-grey cool
SKY_COOL_B = (158, 165, 162)   # lighter cool passage
HORIZON_Y  = 76


def stroke(x0, y, length, tone, gap=0.15, curve=0.3):
    cy = float(y)
    direction = rng.choice([-1, 1])
    for i in range(length):
        cy += direction * curve * math.sin(i / max(length, 1) * math.pi)
        cx = x0 + i
        if 0 <= cx < W and 0 <= int(cy) < HORIZON_Y:
            if rng.random() >= gap:
                px[cx, int(cy)] = tone


# Cool passages — vary length dramatically, don't fill uniformly
for _ in range(22):
    y  = rng.randint(0, HORIZON_Y // 2)
    x0 = rng.randint(0, W - 20)
    # Lengths vary widely: some short (barely a touch), some long sweeps
    ln = rng.choice([12, 18, 22, 45, 60, 80])
    tone = rng.choice([SKY_COOL_A, SKY_COOL_A, SKY_COOL_B])
    stroke(x0, y, ln, tone, gap=rng.uniform(0.12, 0.28),
           curve=rng.uniform(0.08, 0.35))

img.save(os.path.join(OUT, "attempt_07.png"))
print("done")
