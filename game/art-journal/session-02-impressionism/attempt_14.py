#!/usr/bin/env python3
"""
Attempt 14 — harbor into the fog, not above it.
The masts and vessel are too clean. They need to be present but porous —
in the same atmosphere as the sky, not cut against it.
Scatter fog back over the harbor. Let the sky strokes breathe through.
"""
from PIL import Image
import random, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from brushes import scatter, smear, sweep

OUT = os.path.dirname(os.path.abspath(__file__))
rng = random.Random(31)
img = Image.open(os.path.join(OUT, "attempt_13.png"))
px = img.load(); W, H = img.size

HORIZON_Y = 76

SKY_HAZE   = (168, 173, 166)
SKY_WARM_A = (196, 158, 106)

# Fog back over the harbor — not to erase it, but to make it porous.
# The harbor should read through the fog, not above it.
scatter(px, W, H, 0, 120, 0, HORIZON_Y, SKY_HAZE, density=0.22, rng=rng)

# A few warm sky sweeps back through the harbor zone — sky and harbor interleave
for _ in range(8):
    y  = rng.randint(6, HORIZON_Y - 8)
    x0 = rng.randint(0, 80)
    ln = rng.randint(30, 90)
    sweep(px, W, H, x0, y, ln, SKY_WARM_A, gap=0.18,
          curve=rng.uniform(0.1, 0.4), rng=rng, clip_y=(0, HORIZON_Y))

# Soften the hard vessel edge at horizon — smear the seam vertically
smear(px, W, H, 28, 108, HORIZON_Y - 6, HORIZON_Y + 6,
      direction='v', strength=0.35, rng=rng)

img.save(os.path.join(OUT, "attempt_14.png")); print("done")
