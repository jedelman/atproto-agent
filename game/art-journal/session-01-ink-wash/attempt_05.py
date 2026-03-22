#!/usr/bin/env python3
"""
Session 01 — Ink Wash Painting
Study: Sesshū Tōyō, Haboku-sansui (1495)
       After studying Wulong, Chongqing karst gorge.

Attempt 5: Informed by nature.
  - Cliff faces are VERTICAL WALLS, not tilted masses
  - Horizontal stratification within the rock
  - Trees grow from crevices at multiple heights, not from summit
  - Sky gap (paper) between two flanking cliff walls — bilateral composition
  - Human structure at gorge floor, tiny
  - Deep shadow at base

Visualization pass first: sketch composition in buffer, then commit.
"""
from PIL import Image
import math, random, os

W, H = 128, 512
OUT = os.path.dirname(os.path.abspath(__file__))

PAPER = (245, 238, 218)
MIST  = (228, 220, 202)
LIGHT = (192, 180, 156)
MID   = (130, 115,  88)
DARK  = ( 58,  46,  26)
BLACK = ( 16,  10,   2)

TONES = [BLACK, DARK, MID, LIGHT, MIST, PAPER]


def new_canvas(fill=PAPER):
    img = Image.new("RGB", (W, H), fill)
    return img, img.load()


# ── Primitives ────────────────────────────────────────────────────────────────

def set_px(px, x, y, tone):
    if 0 <= x < W and 0 <= y < H:
        px[x, y] = tone


def ink_line(px, pts, tone, width=1, rng=None, dry=False, dry_prob=0.22):
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        steps = max(abs(x2 - x1), abs(y2 - y1), 1)
        for j in range(steps + 1):
            if dry and rng and rng.random() < dry_prob:
                continue
            t = j / steps
            x = int(x1 + (x2 - x1) * t)
            y = int(y1 + (y2 - y1) * t)
            for w in range(width):
                set_px(px, x + w, y, tone)
                set_px(px, x, y + w, tone)


def striation(px, x0, x1, y, tone, rng, gap_prob=0.15):
    """Single horizontal stratification line across a cliff face segment."""
    x = x0
    while x < x1:
        if rng.random() < gap_prob:
            x += rng.randint(2, 6)
            continue
        run = rng.randint(3, 9)
        for rx in range(run):
            set_px(px, x + rx, y, tone)
        x += run + rng.randint(0, 3)


def cliff_wall(px, x0, x1, y0, y1, rng,
               base_tone=LIGHT, stria_tone=MID, shadow_tone=DARK,
               shadow_side='left', turbulence=0.12):
    """
    Paint a vertical cliff wall between x0..x1, y0..y1.
    - Base wash across the face
    - Horizontal striations (geological strata)
    - Shadow on one side (where wall recedes)
    - Irregular outer edge
    """
    # Outer edge turbulence per scanline
    for y in range(y0, y1):
        # Determine actual left/right edge with turbulence
        jitter_l = int(rng.gauss(0, turbulence * (x1 - x0)))
        jitter_r = int(rng.gauss(0, turbulence * (x1 - x0)))
        xl = max(x0, x0 + jitter_l) if shadow_side == 'right' else x0
        xr = min(x1, x1 + jitter_r) if shadow_side == 'left' else x1

        for x in range(xl, xr):
            # Base tone across face
            t = base_tone
            # Shadow deepens toward shadow_side
            if shadow_side == 'left':
                frac = (x - xl) / max(xr - xl, 1)
                if frac < 0.25:
                    t = shadow_tone
                elif frac < 0.5:
                    t = stria_tone
            else:
                frac = (xr - x) / max(xr - xl, 1)
                if frac < 0.25:
                    t = shadow_tone
                elif frac < 0.5:
                    t = stria_tone
            set_px(px, x, y, t)

    # Horizontal striations across the face
    stria_ys = []
    y = y0 + rng.randint(8, 16)
    while y < y1 - 4:
        stria_ys.append(y)
        y += rng.randint(10, 22)

    for sy in stria_ys:
        # Striation spans part of the wall — irregular
        sx0 = x0 + rng.randint(0, (x1 - x0) // 4)
        sx1 = x1 - rng.randint(0, (x1 - x0) // 4)
        striation(px, sx0, sx1, sy, stria_tone, rng)
        # Second line close by — doubling gives weight
        if rng.random() < 0.5:
            striation(px, sx0 + rng.randint(-2,2), sx1 + rng.randint(-2,2),
                      sy + 1, shadow_tone, rng, gap_prob=0.3)

    # Base shadow — darkest at gorge floor
    shadow_depth = min(40, (y1 - y0) // 3)
    for y in range(y1 - shadow_depth, y1):
        alpha = (y - (y1 - shadow_depth)) / shadow_depth
        t = DARK if alpha > 0.5 else MID
        for x in range(x0, x1):
            set_px(px, x, y, t)


def crevice_tree(px, x, y, rng, lean=0):
    """
    Tree growing from a cliff face — sparse, gnarled.
    lean: -1 left, 0 vertical, 1 right. Grows outward from cliff.
    """
    h = rng.randint(12, 20)
    # Trunk leans outward from cliff face
    trunk = [
        (x, y),
        (x + lean * rng.randint(1, 3), y - h // 2),
        (x + lean * rng.randint(2, 5), y - h),
    ]
    ink_line(px, trunk, BLACK, 1, rng)
    # Branches — sparse, reach toward empty space
    for _ in range(rng.randint(2, 4)):
        by = y - rng.randint(h // 3, h - 2)
        bx_tip = x + lean * rng.randint(3, 10) + rng.randint(-3, 3)
        ink_line(px, [(x + lean * 2, by), (bx_tip, by - rng.randint(1, 5))],
                 BLACK, 1, rng, dry=True)


def inscription(px, rng, x_start=82, y_start=8, cols=5):
    """Vertical inscription columns, right side."""
    for col in range(cols):
        cx = x_start + col * 8
        if cx >= W:
            break
        y = y_start
        while y < 55:
            ch = rng.randint(5, 10)
            ink_line(px, [(cx, y), (cx + rng.randint(-1, 1), y + ch)], DARK, 1, rng)
            if rng.random() < 0.45:
                ink_line(px, [(cx - rng.randint(1,3), y + ch//2),
                              (cx + rng.randint(1,3), y + ch//2)], DARK, 1, rng)
            y += ch + rng.randint(2, 5)


# ── Visualization (buffer sketch) ────────────────────────────────────────────

def visualize_composition(rng):
    """
    Quick compositional sketch — flat blocks, no texture.
    Use this to verify the layout before rendering.
    """
    img, px = new_canvas()

    # Left cliff: x 0..38, y 60..380
    for y in range(60, 380):
        for x in range(0, 38):
            px[x, y] = MID

    # Right cliff: x 90..128, y 80..420
    for y in range(80, 420):
        for x in range(90, W):
            px[x, y] = MID

    # Sky gap: paper (already)
    # Gorge floor: dark, y 350..512
    for y in range(360, H):
        for x in range(20, 108):
            if x < 38 or x > 90:
                px[x, y] = DARK
            else:
                px[x, y] = DARK

    # Structure at floor
    for y in range(400, 420):
        for x in range(50, 78):
            px[x, y] = BLACK

    img.save(os.path.join(OUT, "attempt_05_viz.png"))
    print("  composition viz saved")
    return img


# ── Final composition ─────────────────────────────────────────────────────────

def compose(px, rng):

    # Inscription — top right
    inscription(px, rng, x_start=80, y_start=6, cols=5)

    # ── LEFT CLIFF WALL ───────────────────────────────────────────────────
    # Dominates left side. Face visible on right edge (shadow left).
    # Top: emerges from mist around y=58. Bottom: extends to y=390.
    # Width: 0..42, with irregular right edge.

    cliff_wall(px, 0, 40, 58, 390, rng,
               base_tone=LIGHT, stria_tone=MID, shadow_tone=DARK,
               shadow_side='left', turbulence=0.08)

    # Left cliff: darker mass near base
    for y in range(330, 390):
        for x in range(0, 40):
            if rng.random() < 0.7:
                set_px(px, x, y, DARK)

    # Trees on LEFT cliff face — leaning RIGHT into the gap
    crevice_tree(px, 38, 130, rng, lean=1)
    crevice_tree(px, 36, 190, rng, lean=1)
    crevice_tree(px, 40, 260, rng, lean=1)

    # ── RIGHT CLIFF WALL ──────────────────────────────────────────────────
    # Recedes into background slightly. Top: y=72. Bottom: y=430.
    # Width: 86..128, shadow on right edge.

    cliff_wall(px, 86, W, 72, 430, rng,
               base_tone=MID, stria_tone=DARK, shadow_tone=BLACK,
               shadow_side='right', turbulence=0.06)

    # Right cliff: darker overall (in shadow relative to left)
    for y in range(350, 430):
        for x in range(86, W):
            if rng.random() < 0.65:
                set_px(px, x, y, DARK)

    # Trees on RIGHT cliff face — leaning LEFT into the gap
    crevice_tree(px, 88, 155, rng, lean=-1)
    crevice_tree(px, 90, 240, rng, lean=-1)

    # ── SKY GAP ────────────────────────────────────────────────────────────
    # Already paper color. Add very faint mist at the horizon where
    # the gap narrows and the gorge floor disappears into haze.
    for y in range(340, 380):
        for x in range(40, 86):
            if rng.random() < 0.06:
                set_px(px, x, y, MIST)

    # ── GORGE FLOOR ────────────────────────────────────────────────────────
    # Deep shadow. A small pavilion structure, barely visible.
    for y in range(390, H):
        for x in range(38, 90):
            t = BLACK if y > 430 else DARK
            if rng.random() < 0.85:
                set_px(px, x, y, t)

    # Pavilion — a few marks suggesting a roof line
    # Roof ridge marks: two short horizontal strokes at slightly different heights
    for rx in range(48, 72):
        set_px(px, rx, 400, BLACK)
    for rx in range(52, 68):
        set_px(px, rx, 396, BLACK)
    # Vertical supports
    for ry in range(400, 415):
        set_px(px, 52, ry, BLACK)
        set_px(px, 67, ry, BLACK)

    # ── PATH / WATER GLEAM ─────────────────────────────────────────────────
    # Very faint reflective marks on the gorge floor path
    for _ in range(4):
        wy = rng.randint(445, 495)
        wx = rng.randint(44, 80)
        ink_line(px, [(wx, wy), (wx + rng.randint(4, 12), wy)], MID, 1, rng)

    # ── CLIFF TOP MIST ─────────────────────────────────────────────────────
    # Where the cliff tops fade into sky — a few haze marks
    for y in range(58, 78):
        for x in range(0, 42):
            if rng.random() < (78 - y) / 20 * 0.7:
                set_px(px, x, y, MIST)

    for y in range(72, 90):
        for x in range(84, W):
            if rng.random() < (90 - y) / 18 * 0.6:
                set_px(px, x, y, MIST)


def main():
    rng = random.Random(17)

    # Step 1: visualization sketch
    print("Visualizing composition...")
    visualize_composition(rng)

    # Step 2: final render
    print("Rendering final...")
    rng2 = random.Random(17)
    img, px = new_canvas()
    compose(px, rng2)
    out_path = os.path.join(OUT, "attempt_05.png")
    img.save(out_path)
    print(f"  {out_path}")


if __name__ == "__main__":
    main()
