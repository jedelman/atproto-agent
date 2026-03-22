#!/usr/bin/env python3
"""
Session 01 — Ink Wash Painting
Study: Sesshu Toyo, Haboku-sansui (1495)
Attempt 2: Lead with directional energy, not placement.
           No outline edges — let mass define itself.
           Fewer marks. Trust the empty space more.
"""
from PIL import Image
import math, random, os

W, H = 128, 512
OUT = os.path.dirname(os.path.abspath(__file__))
RNG = random.Random(3)

PAPER = (245, 238, 218)
MIST  = (228, 220, 202)
LIGHT = (185, 172, 148)
MID   = (122, 108,  82)
DARK  = ( 58,  48,  28)
BLACK = ( 16,  10,   2)


def new_canvas():
    img = Image.new("RGB", (W, H), PAPER)
    return img, img.load()


def directed_splat(px, cx, cy, rx, ry, angle, tone, rng, wetness=0.65):
    """
    Elliptical splat with a directional axis.
    rx, ry: radii along and perpendicular to angle.
    Simulates a loaded brush dragged in a direction.
    """
    tones = [BLACK, DARK, MID, LIGHT, MIST, PAPER]
    try:
        t_idx = tones.index(tone)
    except ValueError:
        t_idx = 2

    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    max_r = max(rx, ry)

    for dy in range(-max_r - 2, max_r + 3):
        for dx in range(-max_r - 2, max_r + 3):
            # Rotate to ellipse frame
            lx =  dx * cos_a + dy * sin_a
            ly = -dx * sin_a + dy * cos_a
            d = math.hypot(lx / rx, ly / ry)
            if d > 1.0:
                continue

            x, y = cx + dx, cy + dy
            if not (0 <= x < W and 0 <= y < H):
                continue

            # Wetness irregularity at edges
            if d > 0.6 and rng.random() > wetness:
                continue

            # Tone falloff from center
            falloff = d
            idx = t_idx + int(falloff * 1.8)
            idx = min(idx, len(tones) - 1)
            px[x, y] = tones[idx]


def ink_line(px, pts, tone, width, rng, dry=False):
    """
    Draw a brushstroke through a list of (x,y) waypoints.
    dry=True adds flying-white gaps (brush running thin).
    """
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        steps = max(abs(x2 - x1), abs(y2 - y1), 1)
        for j in range(steps + 1):
            t = j / steps
            x = int(x1 + (x2 - x1) * t)
            y = int(y1 + (y2 - y1) * t)
            if dry and rng.random() < 0.3:
                continue  # flying white gap
            for w in range(width):
                if 0 <= x + w < W and 0 <= y < H:
                    px[x + w, y] = tone
                if 0 <= x < W and 0 <= y + w < H:
                    px[x, y + w] = tone


def light_wash(px, x0, y0, x1, y1, tone, rng, density):
    for y in range(y0, y1):
        for x in range(x0, x1):
            if rng.random() < density:
                # irregular edge: lower density near borders
                edge = min(x - x0, x1 - x, y - y0, y1 - y, 8) / 8
                if rng.random() < edge:
                    px[x, y] = tone


def compose(px, rng):

    # ── INSCRIPTION ────────────────────────────────────────────────────────
    # Five columns of vertical marks (Chinese/Japanese calligraphy reads top→down)
    col_xs = [88, 96, 104, 80, 112]
    for cx in col_xs:
        y = 8
        while y < 52:
            char_h = rng.randint(6, 10)
            # character body — a few quick marks
            ink_line(px, [(cx, y), (cx + rng.randint(-2, 2), y + char_h)],
                     DARK, 1, rng)
            y += char_h + rng.randint(2, 4)

    # ── DISTANT MOUNTAIN ── very faint, behind everything ─────────────────
    light_wash(px, 24, 75, 88, 155, MIST, rng, density=0.30)

    # ── MAIN CLIFF ── directional: mass leans upper-left ─────────────────
    # The cliff's axis runs roughly from lower-right to upper-left
    # Layer from lightest to darkest (wet-on-wet: lighter first)

    # Base wash — broad, low density
    light_wash(px, 18, 95, 78, 200, LIGHT, rng, density=0.22)

    # Mid-tone forms — directed ellipses along the cliff's axis
    cliff_axis = math.radians(-35)  # leaning upper-left
    for cx, cy, rx, ry in [
        (46, 170, 22, 12),
        (40, 148, 18, 10),
        (50, 128, 16, 9),
        (44, 190, 14, 8),
        (38, 158, 12, 7),
    ]:
        directed_splat(px, cx, cy, rx, ry, cliff_axis, MID, rng, wetness=0.6)

    # Dark wet-on-wet splashes over the mid-tone
    for cx, cy, rx, ry in [
        (44, 160, 14, 7),
        (38, 142, 12, 6),
        (50, 175, 10, 6),
        (42, 128, 9, 5),
    ]:
        directed_splat(px, cx, cy, rx, ry, cliff_axis, DARK, rng, wetness=0.72)

    # Black accent — densest ink, heart of the cliff
    for cx, cy, rx, ry in [
        (42, 155, 7, 4),
        (36, 140, 5, 3),
    ]:
        directed_splat(px, cx, cy, rx, ry, cliff_axis, BLACK, rng, wetness=0.85)

    # ── TREES ── few, irregular, at cliff summit ───────────────────────────
    tree_positions = [(40, 97), (48, 92), (35, 103)]
    for tx, ty in tree_positions:
        h = rng.randint(14, 22)
        # Trunk — slightly curved
        trunk = [(tx, ty), (tx + rng.randint(-1, 1), ty - h // 2),
                 (tx + rng.randint(-2, 2), ty - h)]
        ink_line(px, trunk, BLACK, 1, rng, dry=False)
        # 2-3 branches — sparse
        for _ in range(rng.randint(2, 3)):
            by = ty - rng.randint(h // 3, h)
            bx_end = tx + rng.randint(-8, 8)
            ink_line(px, [(tx, by), (bx_end, by - rng.randint(3, 7))],
                     BLACK, 1, rng, dry=True)

    # ── WATER EDGE ── where cliff meets water below ───────────────────────
    # A few horizontal marks defining the waterline at cliff base
    for _ in range(3):
        wy = rng.randint(196, 205)
        wx = rng.randint(22, 50)
        ink_line(px, [(wx, wy), (wx + rng.randint(6, 14), wy)], LIGHT, 1, rng)

    # ── MIST ZONE ── the transition between cliff and near shore ──────────
    light_wash(px, 0, 210, W, 270, MIST, rng, density=0.06)

    # ── NEAR SHORE ── smaller, lower energy than main cliff ──────────────
    shore_axis = math.radians(-20)
    for cx, cy, rx, ry in [
        (52, 320, 14, 7),
        (44, 335, 11, 6),
        (58, 310, 9, 5),
    ]:
        directed_splat(px, cx, cy, rx, ry, shore_axis, MID, rng, wetness=0.55)

    for cx, cy, rx, ry in [
        (50, 325, 8, 4),
    ]:
        directed_splat(px, cx, cy, rx, ry, shore_axis, DARK, rng, wetness=0.7)

    # Shore tree — single, spare
    ink_line(px, [(52, 305), (51, 285)], BLACK, 1, rng)
    ink_line(px, [(51, 293), (44, 288)], BLACK, 1, rng, dry=True)

    # ── BOAT ── minimal, open water zone ──────────────────────────────────
    # Hull: a single curved mark. Mast: one vertical.
    ink_line(px, [(44, 415), (50, 417), (58, 416)], DARK, 1, rng, dry=False)
    ink_line(px, [(51, 410), (51, 417)], BLACK, 1, rng)

    # ── WATER MARKS ── very sparse horizontal strokes, lower scroll ───────
    for _ in range(5):
        wy = rng.randint(428, 498)
        wx = rng.randint(8, 70)
        wlen = rng.randint(6, 18)
        ink_line(px, [(wx, wy), (wx + wlen, wy + rng.randint(-1, 1))],
                 LIGHT, 1, rng, dry=True)


def main():
    img, px = new_canvas()
    compose(px, RNG)
    out_path = os.path.join(OUT, "attempt_02.png")
    img.save(out_path)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
