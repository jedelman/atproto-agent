#!/usr/bin/env python3
"""
Session 01 — Ink Wash Painting
Study: Sesshu Toyo, Haboku-sansui (1495)
Attempt 3: Build cliff from nested density regions, not discrete marks.
           The form emerges from where the ink concentrates.
           Mist as directional horizontal haze, not scattered static.
"""
from PIL import Image, ImageFilter
import math, random, os

W, H = 128, 512
OUT = os.path.dirname(os.path.abspath(__file__))
RNG = random.Random(7)

PAPER = (245, 238, 218)
MIST  = (228, 220, 202)
LIGHT = (188, 175, 150)
MID   = (125, 110,  84)
DARK  = ( 60,  48,  28)
BLACK = ( 16,  10,   2)

TONES = [BLACK, DARK, MID, LIGHT, MIST, PAPER]


def new_canvas():
    img = Image.new("RGB", (W, H), PAPER)
    return img, img.load()


def ink_density(cx, cy, rx, ry, angle, x, y):
    """Return 0..1 density value at (x,y) for a tilted ellipse mass."""
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    dx, dy = x - cx, y - cy
    lx =  dx * cos_a + dy * sin_a
    ly = -dx * sin_a + dy * cos_a
    return math.hypot(lx / rx, ly / ry)


def paint_mass(px, regions, tone, rng, wetness=0.65, noise=0.15):
    """
    Paint a tone wherever the combined density of all regions is within threshold.
    Regions: list of (cx, cy, rx, ry, angle, threshold).
    Pixels must be inside ANY region's threshold to be painted.
    wetness: probability of painting at the edge zone.
    noise: random density perturbation.
    """
    # Bounding box
    xs = [r[0] - r[2] - 4 for r in regions] + [r[0] + r[2] + 4 for r in regions]
    ys = [r[1] - r[3] - 4 for r in regions] + [r[1] + r[3] + 4 for r in regions]
    x0, x1 = max(0, min(xs)), min(W, max(xs))
    y0, y1 = max(0, min(ys)), min(H, max(ys))

    for y in range(y0, y1):
        for x in range(x0, x1):
            # Find minimum density across all regions (inside = d < threshold)
            best = min(
                ink_density(r[0], r[1], r[2], r[3], r[4], x, y) / r[5]
                for r in regions
            )
            if best < 1.0:
                # Core: always paint. Edge zone: probabilistic.
                edge_zone = best > 0.65
                perturb = rng.gauss(0, noise)
                effective = best + perturb
                if effective < 0.65 or (edge_zone and rng.random() < wetness * (1 - best)):
                    px[x, y] = tone


def ink_line(px, pts, tone, width, rng, dry=False, dry_prob=0.25):
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        steps = max(abs(x2 - x1), abs(y2 - y1), 1)
        for j in range(steps + 1):
            if dry and rng.random() < dry_prob:
                continue
            t = j / steps
            x = int(x1 + (x2 - x1) * t)
            y = int(y1 + (y2 - y1) * t)
            for w in range(width):
                if 0 <= x + w < W and 0 <= y < H:
                    px[x + w, y] = tone


def haze(px, y0, y1, tone, rng, density, x0=0, x1=W):
    """Directional mist: horizontal bands of sparse marks."""
    for y in range(y0, y1):
        # Each scanline is either hazy or clear
        if rng.random() > density * 1.5:
            continue
        x = x0
        while x < x1:
            run = rng.randint(2, 8)
            gap = rng.randint(3, 12)
            for rx in range(run):
                if x + rx < x1:
                    px[x + rx, y] = tone
            x += run + gap


def compose(px, rng):

    # ── INSCRIPTION — vertical columns, right side ─────────────────────────
    col_xs = [110, 103, 96, 89, 82]
    for cx in col_xs:
        y = 7
        while y < 54:
            ch = rng.randint(5, 9)
            # Vertical stroke
            ink_line(px, [(cx, y), (cx + rng.randint(-1,1), y + ch)], DARK, 1, rng)
            # Occasional horizontal cross-stroke
            if rng.random() < 0.5:
                mx = cx + rng.randint(-3, 3)
                ink_line(px, [(mx, y + ch//2), (mx + rng.randint(-3,3), y + ch//2)], DARK, 1, rng)
            y += ch + rng.randint(2, 5)

    # ── DISTANT MOUNTAIN — very faint, behind cliff ────────────────────────
    dist_regions = [
        (48, 120, 30, 45, math.radians(-20), 1.0),  # broad, low threshold
    ]
    paint_mass(px, dist_regions, MIST, rng, wetness=0.4, noise=0.25)

    # ── MAIN CLIFF — nested density regions, light→dark ───────────────────
    # The cliff's general form: taller than wide, leans slightly left
    # All regions share the same basic zone, varied in size — creates concentration

    axis = math.radians(-30)  # main axis tilt

    # Layer 1: light — defines the full cliff envelope
    cliff_light = [
        (44, 148, 28, 52, axis, 1.0),
    ]
    paint_mass(px, cliff_light, LIGHT, rng, wetness=0.55, noise=0.18)

    # Layer 2: mid — concentrates in the lower 2/3 of the cliff
    cliff_mid = [
        (42, 158, 20, 38, axis, 1.0),
        (38, 142, 14, 22, axis, 1.0),
    ]
    paint_mass(px, cliff_mid, MID, rng, wetness=0.68, noise=0.14)

    # Layer 3: dark — pools in the heart of the cliff, slightly off-center
    cliff_dark = [
        (40, 162, 12, 22, axis, 1.0),
        (36, 146, 8, 14, axis, 1.0),
    ]
    paint_mass(px, cliff_dark, DARK, rng, wetness=0.78, noise=0.10)

    # Layer 4: black — the densest ink moment, small core
    cliff_black = [
        (39, 165, 6, 10, axis, 1.0),
    ]
    paint_mass(px, cliff_black, BLACK, rng, wetness=0.85, noise=0.08)

    # ── TREES — summit of cliff ─────────────────────────────────────────────
    summits = [(38, 95), (46, 90), (32, 101)]
    for tx, ty in summits:
        h = rng.randint(16, 24)
        # Trunk — one continuous mark
        ctrl = [(tx, ty), (tx + rng.randint(-1, 2), ty - h//2),
                (tx + rng.randint(-2, 1), ty - h)]
        ink_line(px, ctrl, BLACK, 1, rng)
        # Branches — dry brush
        for _ in range(rng.randint(2, 4)):
            by = ty - rng.randint(h//4, h - 2)
            blen = rng.randint(5, 10)
            sign = rng.choice((-1, 1))
            ink_line(px, [(tx, by), (tx + sign * blen, by - rng.randint(2, 5))],
                     BLACK, 1, rng, dry=True, dry_prob=0.2)

    # ── WATER EDGE — where cliff base meets water ──────────────────────────
    for _ in range(4):
        wy = rng.randint(196, 208)
        wx = rng.randint(20, 44)
        ink_line(px, [(wx, wy), (wx + rng.randint(8, 16), wy + rng.randint(-1, 1))],
                 LIGHT, 1, rng, dry=True)

    # ── MIST — between zones, horizontal haze ──────────────────────────────
    haze(px, 215, 268, MIST, rng, density=0.18)

    # ── NEAR SHORE — smaller, lower on scroll ─────────────────────────────
    shore_axis = math.radians(-15)
    shore_light = [(54, 320, 16, 28, shore_axis, 1.0)]
    paint_mass(px, shore_light, LIGHT, rng, wetness=0.5, noise=0.20)
    shore_mid = [(52, 326, 10, 18, shore_axis, 1.0)]
    paint_mass(px, shore_mid, MID, rng, wetness=0.65, noise=0.14)
    shore_dark = [(50, 330, 6, 10, shore_axis, 1.0)]
    paint_mass(px, shore_dark, DARK, rng, wetness=0.75, noise=0.10)

    # Shore tree
    ink_line(px, [(52, 305), (51, 292), (52, 280)], BLACK, 1, rng)
    ink_line(px, [(52, 295), (44, 290)], BLACK, 1, rng, dry=True)
    ink_line(px, [(52, 288), (59, 284)], BLACK, 1, rng, dry=True)

    # ── BOAT ── sparse marks ──────────────────────────────────────────────
    ink_line(px, [(42, 416), (50, 418), (60, 416)], DARK, 1, rng)
    ink_line(px, [(51, 411), (51, 418)], BLACK, 1, rng)

    # ── WATER MARKS ── very sparse, open water ───────────────────────────
    for _ in range(6):
        wy = rng.randint(432, 502)
        wx = rng.randint(6, 75)
        wlen = rng.randint(5, 16)
        ink_line(px, [(wx, wy), (wx + wlen, wy)], LIGHT, 1, rng, dry=True)


def main():
    img, px = new_canvas()
    compose(px, RNG)
    out_path = os.path.join(OUT, "attempt_03.png")
    img.save(out_path)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
