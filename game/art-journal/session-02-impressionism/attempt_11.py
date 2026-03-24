from PIL import Image
import random, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from brushes import dry, flat

OUT = os.path.dirname(os.path.abspath(__file__))
rng = random.Random(17)
img = Image.open(os.path.join(OUT, "attempt_10.png"))
px = img.load(); W, H = img.size

REFL_HOT  = (206,  68,  16)
REFL_WARM = (194, 108,  40)
SUN_X = 182
anchor = SUN_X - 6

# Extend reflection into the lower water — wider as it reaches foreground
rx = float(anchor)
for y in range(168, H - 4):
    rx += rng.gauss(0, 0.5)
    rx = max(anchor - 14, min(rx, anchor + 14))
    if rng.random() < 0.2:
        continue
    t = (y - 168) / (H - 4 - 168)
    ln = rng.randint(4, int(8 + t * 10))
    x0 = int(rx) - ln // 2
    tone = rng.choice([REFL_HOT, REFL_WARM, REFL_WARM])
    for x in range(x0, x0 + ln):
        if 0 <= x < W: px[x, y] = tone

img.save(os.path.join(OUT, "attempt_11.png")); print("done")
