#!/usr/bin/env python3
"""
Session 02 — French Impressionism
Study: Claude Monet, Impression, Sunrise (1872)

Attempt 3: Sky palette and movement. Tighter reflection.

  Attempt 2 improved: fog is working, horizon soft, reflection reads as marks.
  Remaining problems:
  - Sky base too warm/brown — Monet's sky is cool grey-blue; warmth comes
    from specific streaks over a cooler ground, not a warm ground itself
  - Sky static — Monet's strokes curve and layer, suggesting moving light
  - Water-sky gap still too wide in value
  - Reflection column drifts — should be tighter and more directional

  Key insight from looking again: sky and water in Monet are almost the SAME
  value. The difference is hue: sky is slightly warm (orange-grey), water is
  slightly cool (blue-teal). They're the same darkness. The fog unifies value;
  hue does the distinguishing.
"""
from PIL import Image
import random, math, os

W, H = 128, 96
OUT = os.path.dirname(os.path.abspath(__file__))

# Palette — revised again
# Sky: cooler grey-blue base; warmth from stroke layers over it
SKY_BASE   = (155, 162, 162)  # cool grey-blue — Monet's foggy morning
SKY_WARM_A = (190, 155, 108)  # orange-warm streaks, upper sky
SKY_WARM_B = (175, 142,  98)  # darker warm streaks
SKY_HAZE   = (170, 172, 164)  # soft haze near horizon (sky lightens)

# Water: same value as sky, but cooler/more teal
WATER_BASE = (130, 158, 152)  # matched value to sky but distinctly teal
WATER_MID  = (105, 136, 130)  # mid-tone water strokes
WATER_DARK = ( 80, 110, 105)  # deep dark strokes

FOG_GHOST  = (148, 154, 158)  # harbor: barely darker, barely cooler

SUN        = (225,  48,  10)  # vivid red-orange
REFL_HOT   = (202,  70,  18)  # reflection core
REFL_WARM  = (190, 108,  42)  # reflection warm
REFL_CREAM = (225, 152,  60)  # reflection bright
BOAT       = ( 18,  16,  12)  # near-black

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


def curved_stroke(px, x0, y, length, tone, rng, gap=0.1, curve=0.3):
    """
    A single brushstroke that curves gently as it extends.
    Curve direction is random — simulates Monet's looping sky marks.
    """
    cy = float(y)
    direction = rng.choice([-1, 1])
    for i in range(length):
        cx = x0 + i
        cy += direction * curve * math.sin(i / max(length, 1) * math.pi)
        if rng.random() >= gap:
            px_set(px, int(cx), int(cy), tone)


def sky_layer(px, rng):
    """
    Cooler grey-blue base. Active curved warm strokes layered over it.
    Upper third: most active, most warm. Near horizon: hazy, quieter.
    """
    # Cool gradient: very slight darkening top to bottom in sky
    for y in range(0, HORIZON_Y):
        t = y / HORIZON_Y
        row = blend(SKY_BASE, SKY_HAZE, t * 0.7)
        for x in range(W):
            px_set(px, x, y, row)

    # Warm curved strokes — active in upper half
    for _ in range(30):
        y  = rng.randint(0, HORIZON_Y - 4)
        x0 = rng.randint(-10, W - 20)
        ln = rng.randint(20, 65)
        tone = rng.choice([SKY_WARM_A, SKY_WARM_A, SKY_WARM_B])
        # Density higher away from horizon
        density = 0.85 - (y / HORIZON_Y) * 0.45
        if rng.random() < density:
            curved_stroke(px, x0, y, ln, tone, rng, gap=0.14,
                          curve=rng.uniform(0.15, 0.5))


def water_layer(px, rng):
    """
    Teal-blue water, same value as sky. Gradient darker toward bottom.
    Soft blend zone at horizon — sky and water meet without a hard line.
    """
    # Gradient from horizon (sky-value) to bottom (darker water)
    for y in range(HORIZON_Y, H):
        t = (y - HORIZON_Y) / (H - HORIZON_Y)
        row = blend(SKY_HAZE, WATER_BASE, t)
        for x in range(W):
            px_set(px, x, y, row)

    # Horizontal stroke texture
    for _ in range(40):
        y  = rng.randint(HORIZON_Y + 3, H - 4)
        x0 = rng.randint(0, W - 10)
        ln = rng.randint(4, 22)
        tone = rng.choice([WATER_MID, WATER_MID, WATER_DARK])
        for x in range(x0, x0 + ln):
            if rng.random() < 0.85:
                px_set(px, x, y, tone)

    # Soften seam: overwrite the horizon band with blended values
    for y in range(HORIZON_Y - 3, HORIZON_Y + 6):
        for x in range(W):
            t = (y - (HORIZON_Y - 3)) / 9
            tone = blend(SKY_HAZE, WATER_BASE, t * 0.65)
            if rng.random() < 0.55:
                px_set(px, x, y, tone)


def harbor_ghosts(px, rng):
    """Same as before but slightly more dissolved."""
    for y in range(HORIZON_Y - 6, HORIZON_Y + 2):
        for x in range(4, 46):
            if rng.random() < 0.2:
                px_set(px, x, y, FOG_GHOST)

    for mx in [14, 24, 33, 42]:
        top_y = rng.randint(3, 10)
        for y in range(top_y, HORIZON_Y + 2):
            if rng.random() < 0.62:
                px_set(px, mx, y, FOG_GHOST)
            if rng.random() < 0.18:
                px_set(px, mx + 1, y, FOG_GHOST)

    for y in range(HORIZON_Y - 10, HORIZON_Y):
        for x in range(48, 58):
            if rng.random() < 0.12:
                px_set(px, x, y, FOG_GHOST)


def sun_disc(px, rng):
    r = 3
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r:
                px_set(px, SUN_X + dx, SUN_Y + dy, SUN)
    # Glow
    for dy in range(-(r + 2), r + 3):
        for dx in range(-(r + 2), r + 3):
            d2 = dx * dx + dy * dy
            if r * r < d2 <= (r + 2) ** 2:
                if rng.random() < 0.38:
                    px_set(px, SUN_X + dx, SUN_Y + dy, SKY_WARM_A)


def reflection(px, rng):
    """
    Tighter column. Anchor x is fixed; drift is minimal.
    Marks are shorter near horizon, slightly longer mid-water.
    """
    anchor = SUN_X - 3   # fixed reference — reflection is directional
    rx = float(anchor)
    for y in range(HORIZON_Y + 1, H - 12):
        # Minimal drift
        rx += rng.gauss(0, 0.4)
        rx = max(anchor - 6, min(rx, anchor + 6))

        if rng.random() < 0.25:
            continue

        t  = (y - HORIZON_Y) / (H - 12 - HORIZON_Y)
        ln = rng.randint(2, max(3, int(3 + t * 4)))
        x0 = int(rx) - ln // 2
        tone = rng.choices(
            [REFL_HOT, REFL_WARM, REFL_CREAM],
            weights=[0.5, 0.35, 0.15]
        )[0]
        for x in range(x0, x0 + ln):
            px_set(px, x, y, tone)

        if rng.random() < 0.25:
            off = rng.randint(-3, 3)
            for x in range(x0 + off, x0 + off + rng.randint(1, 3)):
                px_set(px, x, y, REFL_WARM)


def boats_layer(px, rng):
    ny = 69
    for x in range(33, 55):
        px_set(px, x, ny, BOAT)
        if x < 53:
            px_set(px, x, ny + 1, BOAT)
    for y in range(ny - 9, ny):
        px_set(px, 41, y, BOAT)
        px_set(px, 42, y, BOAT)
    for y in range(ny - 6, ny):
        px_set(px, 49, y, BOAT)

    fy = 57
    for x in range(10, 25):
        if rng.random() < 0.78:
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

    out_path = os.path.join(OUT, "attempt_03.png")
    img.save(out_path)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
