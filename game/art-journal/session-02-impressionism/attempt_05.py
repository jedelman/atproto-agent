#!/usr/bin/env python3
"""
Session 02 — French Impressionism
Study: Claude Monet, Impression, Sunrise (1872)

Attempt 5: Larger canvas (256×192). Fix water banding.

  Canvas: 256×192 (~4:3, matching original 63×48cm proportions)

  Water banding diagnosis: short strokes + sparse fill + fixed seed
  → clustering into vertical artifacts. Fix: render water as SCANLINE
  passes — each row gets its own horizontal marks from left to right,
  with smooth gaps and color variation. More like actual horizontal
  brushstrokes than scattered dots.

  Also: with more pixels, brushwork can actually read as marks.
  The sky strokes can now carry visual weight.
"""
from PIL import Image
import random, math, os

W, H = 256, 192
OUT = os.path.dirname(os.path.abspath(__file__))

SKY_BASE   = (155, 162, 160)
SKY_WARM_A = (196, 158, 106)
SKY_WARM_B = (178, 138,  88)
SKY_HAZE   = (168, 173, 166)

WATER_BASE = (148, 168, 162)
WATER_MID  = (120, 146, 140)
WATER_DARK = ( 90, 116, 110)

FOG_GHOST  = (150, 156, 160)

SUN        = (228,  46,   8)
REFL_HOT   = (206,  68,  16)
REFL_WARM  = (194, 108,  40)
REFL_CREAM = (230, 150,  52)
BOAT       = ( 18,  14,  10)

HORIZON_Y  = 76   # ~40% from top in 192px
SUN_X      = 182  # ~71% from left in 256px
SUN_Y      = 34   # ~18% from top


def new_canvas():
    img = Image.new("RGB", (W, H), SKY_BASE)
    return img, img.load()


def px_set(px, x, y, tone):
    if 0 <= x < W and 0 <= y < H:
        px[x, y] = tone


def blend(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def curved_stroke(px, x0, y, length, tone, rng, gap=0.12, curve=0.4):
    cy = float(y)
    direction = rng.choice([-1, 1])
    for i in range(length):
        cy += direction * curve * math.sin(i / max(length, 1) * math.pi)
        if rng.random() >= gap:
            px_set(px, x0 + i, int(cy), tone)


def sky_layer(px, rng):
    # Cool gradient base
    for y in range(0, HORIZON_Y):
        t = y / HORIZON_Y
        for x in range(W):
            px_set(px, x, y, blend(SKY_BASE, SKY_HAZE, t * 0.6))

    # Bold warm curved strokes — Monet didn't hold back in this sky
    for _ in range(55):
        y  = rng.randint(0, HORIZON_Y - 5)
        x0 = rng.randint(-20, W - 30)
        ln = rng.randint(40, 130)
        tone = rng.choice([SKY_WARM_A, SKY_WARM_A, SKY_WARM_B])
        if rng.random() < (1.0 - y / HORIZON_Y * 0.35):
            curved_stroke(px, x0, y, ln, tone, rng,
                          gap=0.12, curve=rng.uniform(0.15, 0.55))


def water_scanlines(px, rng):
    """
    Water rendered as scanline passes — each row is a full horizontal
    sweep with color variation. No short scattered strokes.
    The result: smooth horizontal banding at row level, not pixel clusters.
    """
    # Gradient base
    for y in range(HORIZON_Y, H):
        t = (y - HORIZON_Y) / (H - HORIZON_Y)
        for x in range(W):
            px_set(px, x, y, blend(SKY_HAZE, WATER_BASE, t * 0.85))

    # Horizontal stroke marks — each mark is a full scanline segment
    # rendered as a continuous run, leaving gaps between runs (not within)
    for y in range(HORIZON_Y + 8, H - 6):
        if rng.random() < 0.45:  # ~half of rows get a stroke mark
            # Pick tone for this row's mark
            tone = rng.choice([WATER_MID, WATER_MID, WATER_DARK])
            # One or two runs across the row, with gaps
            x = rng.randint(0, W // 3)
            while x < W:
                run = rng.randint(8, 40)
                gap = rng.randint(6, 35)
                for rx in range(x, min(x + run, W)):
                    # Slight color variation within the run
                    t = rx / W
                    c = blend(tone, WATER_MID, t * 0.3)
                    px_set(px, rx, y, c)
                x += run + gap

    # Wide soft horizon blend
    blend_start = HORIZON_Y - 8
    blend_end   = HORIZON_Y + 14
    span = blend_end - blend_start
    for y in range(blend_start, blend_end):
        t = (y - blend_start) / span
        for x in range(W):
            tone = blend(SKY_HAZE, WATER_BASE, t * 0.65)
            if rng.random() < 0.65:
                px_set(px, x, y, tone)


def harbor_ghosts(px, rng):
    """
    Background harbor: barely present. Scale up for larger canvas.
    """
    # Hull suggestion at horizon
    for y in range(HORIZON_Y - 12, HORIZON_Y + 4):
        for x in range(8, 94):
            if rng.random() < 0.14:
                px_set(px, x, y, FOG_GHOST)

    # Tall masts — 4 of them, left side
    for mx in [28, 48, 68, 86]:
        top_y = rng.randint(6, 22)
        for y in range(top_y, HORIZON_Y + 3):
            if rng.random() < 0.55:
                px_set(px, mx, y, FOG_GHOST)
            if rng.random() < 0.22:
                px_set(px, mx + 1, y, FOG_GHOST)

    # Crane structure
    for y in range(HORIZON_Y - 22, HORIZON_Y):
        for x in range(98, 118):
            if rng.random() < 0.10:
                px_set(px, x, y, FOG_GHOST)


def sun_disc(px, rng):
    r = 7   # scaled for larger canvas (was 3 in 128px)
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r:
                px_set(px, SUN_X + dx, SUN_Y + dy, SUN)
    # Glow
    for dy in range(-(r + 4), r + 5):
        for dx in range(-(r + 4), r + 5):
            d2 = dx * dx + dy * dy
            if r * r < d2 <= (r + 4) ** 2:
                if rng.random() < 0.35:
                    px_set(px, SUN_X + dx, SUN_Y + dy, SKY_WARM_A)


def reflection(px, rng):
    """
    Scaled for larger canvas. Tight column of broken marks from
    just below horizon to near foreground.
    """
    anchor = SUN_X - 6
    rx = float(anchor)
    for y in range(HORIZON_Y + 1, H - 24):
        rx += rng.gauss(0, 0.5)
        rx = max(anchor - 10, min(rx, anchor + 10))

        if rng.random() < 0.22:
            continue

        t  = (y - HORIZON_Y) / (H - 24 - HORIZON_Y)
        ln = rng.randint(3, max(5, int(5 + t * 10)))
        x0 = int(rx) - ln // 2
        tone = rng.choices(
            [REFL_HOT, REFL_WARM, REFL_CREAM],
            weights=[0.5, 0.35, 0.15]
        )[0]
        for x in range(x0, x0 + ln):
            px_set(px, x, y, tone)

        if rng.random() < 0.28:
            off = rng.randint(-7, 7)
            ln2 = rng.randint(2, 6)
            for x in range(x0 + off, x0 + off + ln2):
                px_set(px, x, y, REFL_WARM)


def boats_layer(px, rng):
    # Near boat — center-left, lower third
    ny = 136
    for x in range(64, 110):
        px_set(px, x, ny, BOAT)
        if x < 108:
            px_set(px, x, ny + 1, BOAT)
            px_set(px, x, ny + 2, BOAT)
    # Two figures
    for y in range(ny - 18, ny):
        px_set(px, 80, y, BOAT)
        px_set(px, 81, y, BOAT)
        px_set(px, 82, y, BOAT)
    for y in range(ny - 13, ny):
        px_set(px, 96, y, BOAT)
        px_set(px, 97, y, BOAT)
    # Oar suggestion
    for y in range(ny - 4, ny + 6):
        px_set(px, 106, y, BOAT)

    # Far boat — smaller, left, higher
    fy = 113
    for x in range(20, 50):
        if rng.random() < 0.78:
            px_set(px, x, fy, BOAT)
    # Mast on far boat
    for y in range(fy - 16, fy):
        px_set(px, 32, y, BOAT)
        if rng.random() < 0.4:
            px_set(px, 33, y, BOAT)


def main():
    rng = random.Random(42)
    img, px = new_canvas()

    sky_layer(px, rng)
    water_scanlines(px, rng)
    harbor_ghosts(px, rng)
    sun_disc(px, rng)
    reflection(px, rng)
    boats_layer(px, rng)

    out_path = os.path.join(OUT, "attempt_05.png")
    img.save(out_path)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
