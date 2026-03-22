#!/usr/bin/env python3
"""
Session 01 — Ink Wash Painting
Study: Sesshu Toyo, Haboku-sansui (1495)
Attempt 1: First contact. Expect to use too much ink.
Canvas: 128 x 512 (portrait, ~4:1, close to scroll's 4.5:1 ratio)
"""
from PIL import Image
import math, random, os

W, H = 128, 512
OUT = os.path.dirname(os.path.abspath(__file__))
RNG = random.Random(1)

# Five ink tones + paper
PAPER   = (245, 238, 218)  # aged silk/xuan — the ground
MIST    = (225, 216, 196)  # barely there — atmospheric wash
LIGHT   = (178, 166, 142)  # light ink — distant forms
MID     = (118, 106,  80)  # medium — near forms, rock faces
DARK    = ( 62,  52,  32)  # dark — tree masses, cliff edges
BLACK   = ( 18,  12,   4)  # near-black — calligraphic marks, detail


def new_canvas():
    img = Image.new("RGB", (W, H), PAPER)
    return img, img.load()


def splat(px, cx, cy, radius, tone, rng, wetness=0.6):
    """Ink drop with wet bleed — dark center fades outward."""
    tones = [BLACK, DARK, MID, LIGHT, MIST, PAPER]
    try:
        t_idx = tones.index(tone)
    except ValueError:
        t_idx = 2

    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            d = math.hypot(dx, dy)
            if d > radius:
                continue
            x, y = cx + dx, cy + dy
            if not (0 <= x < W and 0 <= y < H):
                continue
            # Falloff: darker at center, lighter at edge
            falloff = d / radius
            idx = t_idx + int(falloff * 2)
            idx = min(idx, len(tones) - 1)
            # Wetness: bleed irregularity
            if rng.random() > wetness * (1 - falloff * 0.5):
                px[x, y] = tones[idx]


def stroke(px, x1, y1, x2, y2, tone, width, rng, jitter=2):
    """Brushstroke from (x1,y1) to (x2,y2)."""
    steps = max(abs(x2 - x1), abs(y2 - y1), 1)
    for i in range(steps + 1):
        t = i / steps
        x = int(x1 + (x2 - x1) * t + rng.uniform(-jitter, jitter))
        y = int(y1 + (y2 - y1) * t)
        for w in range(width):
            for wx, wy in ((x + w, y), (x, y + w)):
                if 0 <= wx < W and 0 <= wy < H:
                    px[wx, wy] = tone


def wash(px, x0, y0, x1, y1, tone, rng, density=0.4):
    """Broad wash — scattered pixels simulating dilute ink on wet paper."""
    for y in range(y0, y1):
        for x in range(x0, x1):
            if rng.random() < density:
                px[x, y] = tone


# ── Composition ───────────────────────────────────────────────────────────────
# Scroll zones (top to bottom):
#   0 - 55   : inscription
#  55 - 80   : open sky
#  80 - 220  : main rocky cliff mass + trees + distant mountain behind
# 220 - 300  : middle water / mist (open)
# 300 - 400  : near shore, secondary forms
# 400 - 430  : boat and water marks
# 430 - 512  : open water

def compose(px, rng):

    # 1. INSCRIPTION ZONE — horizontal ink marks, not characters
    for i in range(6):
        y = 8 + i * 8
        stroke(px, 20, y, 108, y, DARK, 1, rng, jitter=1)
        # breaks in line — simulate character spacing
        for _ in range(rng.randint(2, 4)):
            bx = rng.randint(20, 100)
            for bw in range(rng.randint(3, 8)):
                if 0 <= bx + bw < W:
                    px[bx + bw, y] = PAPER

    # 2. DISTANT MOUNTAIN — behind main cliff, very light
    wash(px, 30, 85, 100, 160, MIST, rng, density=0.25)
    wash(px, 40, 90, 90, 145, LIGHT, rng, density=0.10)

    # 3. MAIN ROCKY CLIFF — left-center mass
    # Core dark splashes
    for cx, cy, r in [
        (52, 130, 18), (48, 150, 14), (58, 115, 12),
        (44, 165, 16), (62, 140, 10), (40, 148, 12),
    ]:
        splat(px, cx, cy, r, DARK, rng, wetness=0.7)

    # Mid-tone cliff face
    for cx, cy, r in [
        (55, 120, 20), (45, 145, 18), (60, 160, 15),
        (50, 175, 12), (35, 155, 14),
    ]:
        splat(px, cx, cy, r, MID, rng, wetness=0.55)

    # Cliff edge definition — dark strokes on right edge
    stroke(px, 68, 88, 72, 200, DARK, 2, rng, jitter=1)
    stroke(px, 30, 175, 68, 200, DARK, 1, rng, jitter=1)

    # 4. TREES at cliff top — vertical marks, darkest
    for tx in [42, 48, 55, 61, 38]:
        ty_base = rng.randint(88, 102)
        stroke(px, tx, ty_base, tx + rng.randint(-2, 2), ty_base - rng.randint(14, 22), BLACK, 1, rng, jitter=1)
        # branch marks
        for _ in range(2):
            bx = tx + rng.randint(-5, 5)
            by = ty_base - rng.randint(6, 16)
            stroke(px, tx, by + 2, bx, by, BLACK, 1, rng, jitter=0)

    # 5. NEAR SHORE (lower cliff section)
    for cx, cy, r in [
        (50, 330, 16), (42, 345, 12), (60, 320, 10),
        (38, 360, 14), (55, 350, 10),
    ]:
        splat(px, cx, cy, r, MID, rng, wetness=0.6)

    for cx, cy, r in [
        (48, 340, 10), (56, 328, 8),
    ]:
        splat(px, cx, cy, r, DARK, rng, wetness=0.65)

    # Shore trees
    for tx in [44, 52, 60]:
        stroke(px, tx, 310, tx, 310 - rng.randint(10, 18), BLACK, 1, rng, jitter=1)

    # 6. BOAT — a few marks in the open water zone
    # Simple form: hull curve + mast
    stroke(px, 50, 412, 72, 415, DARK, 1, rng, jitter=0)
    stroke(px, 61, 408, 61, 415, BLACK, 1, rng, jitter=0)

    # 7. WATER MARKS — sparse horizontal strokes
    for _ in range(8):
        wy = rng.randint(420, 500)
        wx = rng.randint(10, 60)
        wl = rng.randint(8, 20)
        stroke(px, wx, wy, wx + wl, wy, LIGHT, 1, rng, jitter=0)

    # 8. MIST — very light wash over transition zones
    wash(px, 0, 220, W, 300, MIST, rng, density=0.08)


def main():
    img, px = new_canvas()
    compose(px, RNG)
    out_path = os.path.join(OUT, "attempt_01.png")
    img.save(out_path)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
