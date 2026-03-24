#!/usr/bin/env python3
"""
Session 02 — French Impressionism
Study: Claude Monet, Impression, Sunrise (1872)

Attempt 2: Fix the fog.
  Attempt 1 failed the core test: sky and water read as two separate regions
  with a hard line between them. The painting is NOT two regions — it's one
  continuous atmospheric field. The horizon is in there somewhere but the fog
  dissolves it.

  Fixes:
  - Soft horizon: blend sky tones downward, water tones upward, let them meet
  - Water much closer in value/saturation to sky (desaturate)
  - Reflection narrower — a column of short broken marks, not a stripe
  - Warmer sky overall, more orange-grey strokes prominent
  - Sun slightly smaller (radius 3 not 4)
"""
from PIL import Image
import random, os

W, H = 128, 96
OUT = os.path.dirname(os.path.abspath(__file__))

# Palette — revised: water desaturated, sky warmer
SKY_BASE   = (172, 170, 158)  # warm grey (warmer than attempt 1)
SKY_WARM   = (192, 152, 102)  # orange-warm sky catches
SKY_LIGHT  = (194, 190, 178)  # lighter sky near horizon
WATER_BASE = (118, 148, 142)  # desaturated teal — much closer to sky now
WATER_DARK = ( 86, 116, 110)  # darker water strokes
FOG_GHOST  = (148, 152, 156)  # harbor: barely cooler/darker than sky
SUN        = (222,  50,  12)  # vivid red-orange
REFL_HOT   = (200,  72,  20)  # reflection core
REFL_WARM  = (188, 110,  44)  # reflection warm
REFL_CREAM = (222, 155,  65)  # reflection bright
BOAT       = ( 20,  18,  14)  # near-black

HORIZON_Y = 38
SUN_X, SUN_Y = 90, 17


def new_canvas():
    img = Image.new("RGB", (W, H), SKY_BASE)
    return img, img.load()


def px_set(px, x, y, tone):
    if 0 <= x < W and 0 <= y < H:
        px[x, y] = tone


def blend(c1, c2, t):
    """Linear blend between two RGB tuples. t=0 → c1, t=1 → c2."""
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def h_stroke(px, x0, x1, y, tone, rng, gap=0.1, wobble=1):
    for x in range(x0, x1):
        if rng.random() < gap:
            continue
        dy = rng.randint(-wobble, wobble) if wobble else 0
        px_set(px, x, y + dy, tone)


def sky_layer(px, rng):
    """
    Sky: warm grey base, active orange-warm strokes especially upper third.
    Lightens toward horizon (fog glow).
    """
    # Gradient toward lighter horizon
    for y in range(0, HORIZON_Y):
        t = y / HORIZON_Y   # 0 at top, 1 at horizon
        row_tone = blend(SKY_BASE, SKY_LIGHT, t * 0.6)
        for x in range(W):
            px_set(px, x, y, row_tone)

    # Orange-warm strokes — heavier in upper half, lighter near horizon
    for _ in range(28):
        y  = rng.randint(0, HORIZON_Y - 2)
        x0 = rng.randint(0, W - 25)
        ln = rng.randint(20, 60)
        # Strokes more prominent away from horizon
        density = 1.0 - (y / HORIZON_Y) * 0.5
        if rng.random() < density:
            h_stroke(px, x0, x0 + ln, y, SKY_WARM, rng, gap=0.15, wobble=1)


def water_layer(px, rng):
    """
    Water: close to sky but slightly cooler/darker. Soft horizon seam.
    The key fix: water should feel like 'foggy sky reflected' not a distinct zone.
    Gradients from horizon downward (darker further down).
    """
    for y in range(HORIZON_Y, H):
        t = (y - HORIZON_Y) / (H - HORIZON_Y)  # 0 at horizon, 1 at bottom
        row_tone = blend(SKY_LIGHT, WATER_BASE, t * 0.85)
        for x in range(W):
            px_set(px, x, y, row_tone)

    # Horizontal stroke texture on water — darker strokes suggest surface
    for _ in range(35):
        y  = rng.randint(HORIZON_Y + 4, H - 5)
        x0 = rng.randint(0, W - 12)
        ln = rng.randint(5, 20)
        h_stroke(px, x0, x0 + ln, y, WATER_DARK, rng, gap=0.22, wobble=1)

    # Soft horizon blend — a few rows that mix sky and water
    for y in range(HORIZON_Y - 2, HORIZON_Y + 5):
        for x in range(W):
            t = (y - (HORIZON_Y - 2)) / 7
            tone = blend(SKY_LIGHT, WATER_BASE, t * 0.5)
            if rng.random() < 0.6:
                px_set(px, x, y, tone)


def harbor_ghosts(px, rng):
    """
    Harbor shapes: masts, hull, crane. Left half.
    Fog test: same value as sky, barely cooler. Sparse.
    """
    # Vague hull at horizon
    for y in range(HORIZON_Y - 5, HORIZON_Y + 3):
        for x in range(5, 48):
            if rng.random() < 0.24:
                px_set(px, x, y, FOG_GHOST)

    # Masts
    for mx in [15, 25, 34, 43]:
        top_y = rng.randint(4, 11)
        for y in range(top_y, HORIZON_Y + 2):
            if rng.random() < 0.65:
                px_set(px, mx, y, FOG_GHOST)
            if rng.random() < 0.2:
                px_set(px, mx + 1, y, FOG_GHOST)

    # Crane — faint structure right of masts
    for y in range(HORIZON_Y - 12, HORIZON_Y):
        for x in range(50, 60):
            if rng.random() < 0.14:
                px_set(px, x, y, FOG_GHOST)


def sun_disc(px, rng):
    """Smaller vivid disc (r=3). Soft warm glow at edge."""
    r = 3
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r:
                px_set(px, SUN_X + dx, SUN_Y + dy, SUN)
    for dy in range(-(r + 2), r + 3):
        for dx in range(-(r + 2), r + 3):
            d2 = dx * dx + dy * dy
            if r * r < d2 <= (r + 2) ** 2:
                if rng.random() < 0.4:
                    px_set(px, SUN_X + dx, SUN_Y + dy, SKY_WARM)


def reflection(px, rng):
    """
    Narrower broken column. Each row: one short stroke.
    Not a stripe — individual marks that happen to form a column.
    The marks widen slightly toward foreground (reflection spreads on water).
    """
    rx = SUN_X - 2
    for y in range(HORIZON_Y + 1, H - 10):
        rx += rng.randint(-1, 1)
        rx = max(72, min(rx, 98))

        if rng.random() < 0.28:  # more gaps than attempt 1
            continue

        # Stroke length: short near horizon, slightly wider toward bottom
        t = (y - HORIZON_Y) / (H - 10 - HORIZON_Y)
        ln = rng.randint(2, int(4 + t * 5))
        x0 = rx - ln // 2
        tone = rng.choice([REFL_HOT, REFL_HOT, REFL_WARM, REFL_CREAM])
        for x in range(x0, x0 + ln):
            px_set(px, x, y, tone)

        # Occasional offset companion (water chop)
        if rng.random() < 0.3:
            off  = rng.randint(-4, 4)
            ln2  = rng.randint(1, 4)
            for x in range(x0 + off, x0 + off + ln2):
                px_set(px, x, y, REFL_WARM)


def boats_layer(px, rng):
    """Near boat center-left, far boat further left."""
    # Near boat
    ny = 69
    for x in range(33, 56):
        px_set(px, x, ny, BOAT)
        if x < 54:
            px_set(px, x, ny + 1, BOAT)
    # Figures
    for y in range(ny - 9, ny):
        px_set(px, 41, y, BOAT)
        px_set(px, 42, y, BOAT)
    for y in range(ny - 6, ny):
        px_set(px, 49, y, BOAT)

    # Far boat
    fy = 57
    for x in range(11, 26):
        if rng.random() < 0.8:
            px_set(px, x, fy, BOAT)
    for y in range(fy - 8, fy):
        px_set(px, 17, y, BOAT)


def main():
    rng = random.Random(42)
    img, px = new_canvas()

    sky_layer(px, rng)
    water_layer(px, rng)
    harbor_ghosts(px, rng)
    sun_disc(px, rng)
    reflection(px, rng)
    boats_layer(px, rng)

    out_path = os.path.join(OUT, "attempt_02.png")
    img.save(out_path)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
