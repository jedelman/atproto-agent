#!/usr/bin/env python3
"""
Session 02 — French Impressionism
Study: Claude Monet, Impression, Sunrise (1872)
       Musée Marmottan Monet, Paris. 48×63 cm.

Attempt 1: Get the color zones and the primary tension right.
  The painting is organized around one axis: everything dissolves (fog,
  harbor, masts, cranes) except the sun and its reflection on water.

  Sky and water are nearly the same value — both grey-blue/teal — unified
  by fog. The sun dominates through SATURATION, not brightness. The harbor
  ghosts are barely darker than sky.

Canvas: 128×96 (landscape, ~4:3 matching original proportions)
"""
from PIL import Image
import random, os

W, H = 128, 96
OUT = os.path.dirname(os.path.abspath(__file__))

# Palette — from direct study of the original
SKY_BASE   = (168, 172, 162)  # warm blue-grey sky ground
SKY_WARM   = (188, 150, 105)  # orange-warm streaks in sky (clouds catching light)
WATER_BASE = ( 98, 142, 136)  # cooler teal-blue water — distinctly different from sky
WATER_DARK = ( 72, 108, 103)  # darker water marks, shadow passages
FOG_GHOST  = (140, 148, 152)  # harbor shapes: barely darker, slightly bluer than sky
SUN        = (218,  52,  14)  # vivid red-orange disc — the saturated anchor
REFL_HOT   = (198,  74,  24)  # reflection core
REFL_WARM  = (186, 112,  48)  # reflection warm mid
REFL_CREAM = (220, 158,  70)  # reflection bright highlights
BOAT       = ( 22,  20,  16)  # near-black boat silhouettes

HORIZON_Y = 37   # horizon: upper ~38% sky, lower ~62% water
SUN_X     = 90   # sun: upper right, ~70% from left
SUN_Y     = 17   # sun: ~18% from top


def new_canvas():
    img = Image.new("RGB", (W, H), SKY_BASE)
    return img, img.load()


def px_set(px, x, y, tone):
    if 0 <= x < W and 0 <= y < H:
        px[x, y] = tone


def h_stroke(px, x0, x1, y, tone, rng, gap=0.08, wobble=1):
    """Horizontal stroke with slight vertical wobble and gaps."""
    for x in range(x0, x1):
        if rng.random() < gap:
            continue
        dy = rng.randint(-wobble, wobble) if wobble else 0
        px_set(px, x, y + dy, tone)


def sky_layer(px, rng):
    """
    Sky: warm blue-grey base (canvas fill) plus curved orange-warm strokes.
    Monet's sky strokes curve gently — they suggest moving atmosphere.
    Warmest upper-left where light catches; softer near horizon.
    """
    # Warm orange-grey strokes — upper half of sky, scattered
    for _ in range(22):
        y  = rng.randint(0, HORIZON_Y - 5)
        x0 = rng.randint(0, W - 30)
        ln = rng.randint(18, 55)
        h_stroke(px, x0, x0 + ln, y, SKY_WARM, rng, gap=0.18, wobble=1)

    # Very near horizon: slight lightening (fog softens the seam)
    for y in range(HORIZON_Y - 3, HORIZON_Y):
        for x in range(W):
            if rng.random() < 0.35:
                r, g, b = SKY_BASE
                px_set(px, x, y, (r + 18, g + 14, b + 10))


def water_layer(px, rng):
    """
    Water: cooler teal-blue. Horizontal marks.
    Slightly darker than sky — they're different despite fog unifying value.
    """
    # Fill water zone
    for y in range(HORIZON_Y, H):
        for x in range(W):
            t = WATER_DARK if rng.random() < 0.12 else WATER_BASE
            px_set(px, x, y, t)

    # Horizontal stroke marks — darker passages on the surface
    for _ in range(30):
        y  = rng.randint(HORIZON_Y + 3, H - 6)
        x0 = rng.randint(0, W - 15)
        ln = rng.randint(6, 24)
        h_stroke(px, x0, x0 + ln, y, WATER_DARK, rng, gap=0.2, wobble=1)


def harbor_ghosts(px, rng):
    """
    Background industrial harbor: cranes, masts, ship hulls — left half.
    These are the FOG test. They must be barely present.
    Same value as sky, only slightly darker/cooler. Gaps everywhere.
    If they read too clearly, the fog is gone.
    """
    # Vague ship hull mass — low, left, straddles horizon
    for y in range(HORIZON_Y - 6, HORIZON_Y + 4):
        for x in range(6, 50):
            if rng.random() < 0.28:
                px_set(px, x, y, FOG_GHOST)

    # Tall masts — sparse verticals through sky, left half
    for mx in [16, 26, 36, 44]:
        top_y = rng.randint(3, 12)
        for y in range(top_y, HORIZON_Y + 3):
            if rng.random() < 0.68:   # gaps = fog eating the mast
                px_set(px, mx, y, FOG_GHOST)
            if rng.random() < 0.25:
                px_set(px, mx + 1, y, FOG_GHOST)

    # Crane/derrick structure — slightly right of masts
    for y in range(HORIZON_Y - 14, HORIZON_Y):
        for x in range(52, 64):
            if rng.random() < 0.16:
                px_set(px, x, y, FOG_GHOST)


def sun_disc(px, rng):
    """Small vivid disc, upper right. The saturated anchor."""
    r = 4
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r:
                px_set(px, SUN_X + dx, SUN_Y + dy, SUN)
    # Soft warm glow at edge
    for dy in range(-(r + 2), r + 3):
        for dx in range(-(r + 2), r + 3):
            d2 = dx * dx + dy * dy
            if r * r < d2 <= (r + 2) ** 2:
                if rng.random() < 0.45:
                    px_set(px, SUN_X + dx, SUN_Y + dy, SKY_WARM)


def reflection(px, rng):
    """
    Broken orange strokes on water, from just below horizon toward foreground.
    The reflection drifts slightly — water surface is moving.
    Each row: a short horizontal stroke, intermittent, slightly offset.
    These are bold. This is where Monet didn't hold back.
    """
    rx = SUN_X - 3  # reflection starts slightly left of sun (perspective)
    for y in range(HORIZON_Y + 1, H - 8):
        rx += rng.randint(-1, 1)
        rx = max(68, min(rx, 102))

        if rng.random() < 0.22:  # gap row — water breaks
            continue

        ln   = rng.randint(3, 9)
        x0   = rx - ln // 2
        tone = rng.choice([REFL_HOT, REFL_HOT, REFL_WARM, REFL_CREAM])
        for x in range(x0, x0 + ln):
            px_set(px, x, y, tone)

        # Occasional offset companion stroke
        if rng.random() < 0.38:
            off = rng.randint(-5, 5)
            ln2 = rng.randint(2, 5)
            for x in range(x0 + off, x0 + off + ln2):
                px_set(px, x, y, REFL_WARM)


def boats_layer(px, rng):
    """
    Two rowboats. Near-black. Few marks — confident, not fussy.
    Near boat: center-left foreground, two figures.
    Far boat: further left, smaller, higher up.
    """
    # Near boat — hull
    ny = 68
    for x in range(34, 58):
        px_set(px, x, ny, BOAT)
        if x < 56:
            px_set(px, x, ny + 1, BOAT)
    # Two figures — dark vertical smudges
    for y in range(ny - 9, ny):
        px_set(px, 42, y, BOAT)
        px_set(px, 43, y, BOAT)
    for y in range(ny - 7, ny):
        px_set(px, 50, y, BOAT)

    # Far boat — smaller, slightly upper-left
    fy = 57
    for x in range(12, 28):
        if rng.random() < 0.82:
            px_set(px, x, fy, BOAT)
    # Mast on far boat
    for y in range(fy - 9, fy):
        px_set(px, 18, y, BOAT)


def main():
    rng = random.Random(42)
    img, px = new_canvas()

    sky_layer(px, rng)
    water_layer(px, rng)
    harbor_ghosts(px, rng)
    sun_disc(px, rng)
    reflection(px, rng)
    boats_layer(px, rng)

    out_path = os.path.join(OUT, "attempt_01.png")
    img.save(out_path)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
