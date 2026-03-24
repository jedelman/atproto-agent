#!/usr/bin/env python3
"""
Session 02 — French Impressionism
Study: Claude Monet, Impression, Sunrise (1872)

Attempt 4: Fix the water. Stop over-stroking it.

  Attempt 3 diagnosis:
  - Dark water strokes clustered, creating banding and a dark halo around
    the reflection. The reflection should sit on open teal-grey water,
    not in a shadow.
  - Sky warm strokes still too timid — Monet's sky is aggressively warm
    in places; I'm holding back.
  - Horizon still seams — extend the blend zone further both ways.
  - Harbor ghost masts too solid.

  Key correction: the water in Impression Sunrise is LIGHTER than I've been
  painting it. The fog fills the water too — it's not a dark teal sea, it's
  a pale misty surface. The darkness comes from specific stroke marks, not
  from a dark base.
"""
from PIL import Image
import random, math, os

W, H = 128, 96
OUT = os.path.dirname(os.path.abspath(__file__))

SKY_BASE   = (155, 162, 160)  # cool grey-blue
SKY_WARM_A = (195, 158, 108)  # orange-warm, bold
SKY_WARM_B = (178, 140,  92)  # deeper warm
SKY_HAZE   = (168, 172, 166)  # horizon haze

# Water: lighter this time — fog fills it
WATER_BASE = (148, 168, 162)  # pale teal-grey, close to sky value
WATER_MID  = (118, 144, 138)  # mid strokes — sparse
WATER_DARK = ( 88, 114, 108)  # darkest marks — very few

FOG_GHOST  = (150, 156, 160)  # harbor ghosts — nearly identical to sky

SUN        = (228,  46,   8)
REFL_HOT   = (204,  68,  16)
REFL_WARM  = (192, 108,  40)
REFL_CREAM = (228, 150,  55)
BOAT       = ( 18,  15,  11)

HORIZON_Y  = 38
SUN_X, SUN_Y = 90, 17


def new_canvas():
    img = Image.new("RGB", (W, H), SKY_BASE)
    return img, img.load()


def px_set(px, x, y, tone):
    if 0 <= x < W and 0 <= y < H:
        px[x, y] = tone


def blend(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def curved_stroke(px, x0, y, length, tone, rng, gap=0.12, curve=0.3):
    cy = float(y)
    direction = rng.choice([-1, 1])
    for i in range(length):
        cy += direction * curve * math.sin(i / max(length, 1) * math.pi)
        if rng.random() >= gap:
            px_set(px, x0 + i, int(cy), tone)


def sky_layer(px, rng):
    """
    Cool grey base. Bold warm curved strokes — don't hold back.
    Upper sky: warmest and most active.
    Near horizon: lightens to haze.
    """
    # Cool-to-haze gradient in sky
    for y in range(0, HORIZON_Y):
        t = y / HORIZON_Y
        for x in range(W):
            px_set(px, x, y, blend(SKY_BASE, SKY_HAZE, t * 0.6))

    # Warm strokes — bold and numerous, especially upper sky
    for _ in range(36):
        y  = rng.randint(0, HORIZON_Y - 3)
        x0 = rng.randint(-15, W - 15)
        ln = rng.randint(22, 70)
        tone = rng.choice([SKY_WARM_A, SKY_WARM_A, SKY_WARM_B])
        # Probability weighted away from horizon (more active at top)
        if rng.random() < (1.0 - y / HORIZON_Y * 0.4):
            curved_stroke(px, x0, y, ln, tone, rng,
                          gap=0.12, curve=rng.uniform(0.1, 0.45))


def water_layer(px, rng):
    """
    Pale teal-grey water. LIGHTER than previous attempts.
    Fog fills the water just as it fills the sky.
    A few sparse dark strokes for surface texture — not many.
    Wide soft blend zone at horizon.
    """
    # Gradient: sky haze at horizon → pale water base lower
    for y in range(HORIZON_Y, H):
        t = (y - HORIZON_Y) / (H - HORIZON_Y)
        for x in range(W):
            px_set(px, x, y, blend(SKY_HAZE, WATER_BASE, t * 0.8))

    # Sparse horizontal strokes — surface texture, not dark banding
    for _ in range(20):   # half as many as before
        y  = rng.randint(HORIZON_Y + 6, H - 4)
        x0 = rng.randint(0, W - 8)
        ln = rng.randint(4, 16)
        tone = rng.choice([WATER_MID, WATER_MID, WATER_DARK])
        for x in range(x0, x0 + ln):
            if rng.random() < 0.8:
                px_set(px, x, y, tone)

    # Wide horizon blend — sky and water dissolve into each other
    blend_start = HORIZON_Y - 5
    blend_end   = HORIZON_Y + 9
    for y in range(blend_start, blend_end):
        t = (y - blend_start) / (blend_end - blend_start)
        for x in range(W):
            tone = blend(SKY_HAZE, WATER_BASE, t * 0.7)
            # Don't overwrite every pixel — let some underlying show
            if rng.random() < 0.7:
                px_set(px, x, y, tone)


def harbor_ghosts(px, rng):
    """
    Maximally dissolved. These should be impressions, not marks.
    Use a tone almost indistinguishable from sky.
    """
    for y in range(HORIZON_Y - 7, HORIZON_Y + 2):
        for x in range(4, 46):
            if rng.random() < 0.16:   # reduced from 0.2
                px_set(px, x, y, FOG_GHOST)

    for mx in [14, 24, 33, 42]:
        top_y = rng.randint(4, 12)
        for y in range(top_y, HORIZON_Y + 2):
            if rng.random() < 0.52:   # reduced from 0.62
                px_set(px, mx, y, FOG_GHOST)

    for y in range(HORIZON_Y - 10, HORIZON_Y):
        for x in range(48, 56):
            if rng.random() < 0.10:
                px_set(px, x, y, FOG_GHOST)


def sun_disc(px, rng):
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
                    px_set(px, SUN_X + dx, SUN_Y + dy, SKY_WARM_A)


def reflection(px, rng):
    """
    Tight column. No dark zone around it — pale water base means the
    orange marks pop on their own without dark shadow contrast.
    Marks widen slightly toward foreground.
    """
    anchor = SUN_X - 3
    rx = float(anchor)
    for y in range(HORIZON_Y + 1, H - 14):
        rx += rng.gauss(0, 0.35)
        rx = max(anchor - 5, min(rx, anchor + 5))

        if rng.random() < 0.24:
            continue

        t  = (y - HORIZON_Y) / (H - 14 - HORIZON_Y)
        ln = rng.randint(2, max(3, int(3 + t * 5)))
        x0 = int(rx) - ln // 2
        tone = rng.choices(
            [REFL_HOT, REFL_WARM, REFL_CREAM],
            weights=[0.5, 0.35, 0.15]
        )[0]
        for x in range(x0, x0 + ln):
            px_set(px, x, y, tone)

        if rng.random() < 0.28:
            off = rng.randint(-4, 4)
            ln2 = rng.randint(1, 3)
            for x in range(x0 + off, x0 + off + ln2):
                px_set(px, x, y, REFL_WARM)


def boats_layer(px, rng):
    ny = 68
    for x in range(32, 55):
        px_set(px, x, ny, BOAT)
        if x < 53:
            px_set(px, x, ny + 1, BOAT)
    for y in range(ny - 9, ny):
        px_set(px, 40, y, BOAT)
        px_set(px, 41, y, BOAT)
    for y in range(ny - 6, ny):
        px_set(px, 48, y, BOAT)

    fy = 57
    for x in range(10, 24):
        if rng.random() < 0.76:
            px_set(px, x, fy, BOAT)
    for y in range(fy - 8, fy):
        px_set(px, 16, y, BOAT)


def main():
    rng = random.Random(42)
    img, px = new_canvas()

    sky_layer(px, rng)
    water_layer(px, rng)
    harbor_ghosts(px, rng)
    sun_disc(px, rng)
    reflection(px, rng)
    boats_layer(px, rng)

    out_path = os.path.join(OUT, "attempt_04.png")
    img.save(out_path)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
