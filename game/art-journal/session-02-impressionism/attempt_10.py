from PIL import Image
import random, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from brushes import dry, flat

OUT = os.path.dirname(os.path.abspath(__file__))
rng = random.Random(3)
img = Image.open(os.path.join(OUT, "attempt_09.png"))
px = img.load(); W, H = img.size

WATER_MID  = (115, 142, 136)
WATER_DARK = ( 85, 112, 106)
HORIZON_Y  = 76

# Scattered dry strokes across the water surface — horizontal, varied tone
for _ in range(18):
    y  = rng.randint(HORIZON_Y + 10, H - 20)
    x0 = rng.randint(0, W - 60)
    ln = rng.randint(20, 80)
    tone = rng.choice([WATER_MID, WATER_MID, WATER_DARK])
    dry(px, W, H, x0, y, ln, tone, gap=rng.uniform(0.3, 0.5),
        drift=0.6, rng=rng, clip_y=(HORIZON_Y, H))

img.save(os.path.join(OUT, "attempt_10.png")); print("done")
