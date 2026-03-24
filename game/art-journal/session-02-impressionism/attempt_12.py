from PIL import Image
import random, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from brushes import scatter, smear

OUT = os.path.dirname(os.path.abspath(__file__))
rng = random.Random(21)
img = Image.open(os.path.join(OUT, "attempt_11.png"))
px = img.load(); W, H = img.size

WARM_GOLD = (200, 162, 108)
WARM_ROSE = (196, 148,  98)

# Dense warm scatter in upper-left sky — fill the field, not just strokes
scatter(px, W, H, 0, W//2, 0, 28, WARM_GOLD, density=0.18, rng=rng)
scatter(px, W, H, 0, W//3, 0, 40, WARM_ROSE, density=0.12, rng=rng)

# Horizontal smear to integrate the scatter with what's already there
smear(px, W, H, 0, W//2, 0, 44, direction='h', strength=0.3, rng=rng)

img.save(os.path.join(OUT, "attempt_12.png")); print("done")
