#!/usr/bin/env python3
"""
Session 01 — Ink Wash Painting
Study: Sesshu Toyo, Haboku-sansui (1495)
Attempt 4: Edge turbulence. Off-center composition. Trees rooted in mass.
           The form must be rough where it meets empty space.
"""
from PIL import Image
import math, random, os

W, H = 128, 512
OUT = os.path.dirname(os.path.abspath(__file__))
RNG = random.Random(11)

PAPER = (245, 238, 218)
MIST  = (228, 220, 202)
LIGHT = (190, 177, 152)
MID   = (128, 112,  85)
DARK  = ( 58,  46,  26)
BLACK = ( 16,  10,   2)

TONES = [BLACK, DARK, MID, LIGHT, MIST, PAPER]


def new_canvas():
    img = Image.new("RGB", (W, H), PAPER)
    return img, img.load()


def perturbed_density(cx, cy, rx, ry, angle, x, y, rng, turbulence=0.0):
    """
    Ellipse density with radial turbulence — the edge is rough, not smooth.
    turbulence > 0 warps the ellipse boundary with noise.
    """
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    dx, dy = x - cx, y - cy
    lx =  dx * cos_a + dy * sin_a
    ly = -dx * sin_a + dy * cos_a
    base_d = math.hypot(lx / rx, ly / ry)
    if turbulence > 0:
        # Radial noise using angle as lookup
        theta = math.atan2(ly, lx)
        noise = math.sin(theta * 3.7) * 0.15 + math.sin(theta * 7.1) * 0.09
        base_d += turbulence * noise
    return base_d


def paint_mass(px, regions, tone, rng, wetness=0.65, noise=0.15, turbulence=0.3):
    xs = [r[0] - r[2] - 5 for r in regions] + [r[0] + r[2] + 5 for r in regions]
    ys = [r[1] - r[3] - 5 for r in regions] + [r[1] + r[3] + 5 for r in regions]
    x0, x1 = max(0, min(xs)), min(W, max(xs))
    y0, y1 = max(0, min(ys)), min(H, max(ys))

    for y in range(y0, y1):
        for x in range(x0, x1):
            best = min(
                perturbed_density(r[0], r[1], r[2], r[3], r[4], x, y, rng, turbulence) / r[5]
                for r in regions
            )
            perturb = rng.gauss(0, noise)
            effective = best + perturb
            if effective < 0.55:
                px[x, y] = tone
            elif effective < 1.0:
                # Edge zone: probabilistic, falls off sharply
                prob = wetness * (1.0 - effective) * 2.2
                if rng.random() < prob:
                    px[x, y] = tone


def ink_line(px, pts, tone, width, rng, dry=False, dry_prob=0.22):
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
    for y in range(y0, y1):
        if rng.random() > density * 2.0:
            continue
        x = x0 + rng.randint(0, 8)
        while x < x1:
            run = rng.randint(2, 7)
            gap = rng.randint(4, 16)
            for rx in range(run):
                if x + rx < x1:
                    px[x + rx, y] = tone
            x += run + gap


def compose(px, rng):

    # ── INSCRIPTION — right column, vertical ──────────────────────────────
    col_xs = [112, 105, 98, 91, 84]
    for cx in col_xs:
        y = 8
        while y < 55:
            ch = rng.randint(5, 10)
            ink_line(px, [(cx, y), (cx + rng.randint(-1, 1), y + ch)], DARK, 1, rng)
            if rng.random() < 0.45:
                ink_line(px, [(cx - rng.randint(1,3), y + ch//2),
                              (cx + rng.randint(1,3), y + ch//2)], DARK, 1, rng)
            # Occasional accent dot
            if rng.random() < 0.2 and y + ch + 2 < 55:
                px[cx, y + ch + 1] = BLACK
            y += ch + rng.randint(2, 5)

    # ── DISTANT MOUNTAIN — far right behind, very faint ───────────────────
    paint_mass(px,
        [(56, 118, 26, 40, math.radians(-18), 1.0)],
        MIST, rng, wetness=0.3, noise=0.30, turbulence=0.4)

    # ── MAIN CLIFF — left-of-center, asymmetric ───────────────────────────
    # Shifted left: cliff centered around x=36 (not 64)
    axis = math.radians(-28)
    cx_cliff = 36

    # Light envelope — tallest and widest
    paint_mass(px,
        [(cx_cliff, 155, 26, 56, axis, 1.0)],
        LIGHT, rng, wetness=0.52, noise=0.20, turbulence=0.35)

    # Mid layer — offset slightly downward relative to light
    paint_mass(px, [
        (cx_cliff - 2, 162, 18, 40, axis, 1.0),
        (cx_cliff + 4, 145, 12, 22, axis, 1.0),  # secondary lobe
    ], MID, rng, wetness=0.65, noise=0.15, turbulence=0.28)

    # Dark — pooling in lower-left heart of cliff
    paint_mass(px, [
        (cx_cliff - 4, 168, 11, 26, axis, 1.0),
        (cx_cliff,     152, 7,  14, axis, 1.0),
    ], DARK, rng, wetness=0.78, noise=0.10, turbulence=0.18)

    # Black core — single dense moment
    paint_mass(px,
        [(cx_cliff - 4, 172, 6, 14, axis, 1.0)],
        BLACK, rng, wetness=0.88, noise=0.08, turbulence=0.12)

    # ── TREES — growing FROM cliff top ───────────────────────────────────
    # Cliff top is approximately y=99 at cx_cliff. Trees root there.
    tree_positions = [
        (cx_cliff - 2, 100),
        (cx_cliff + 7, 96),
        (cx_cliff - 9, 106),
    ]
    for tx, ty in tree_positions:
        h = rng.randint(18, 28)
        # Trunk emerges from mass
        ctrl = [(tx, ty), (tx + rng.randint(-2, 1), ty - h//2),
                (tx + rng.randint(-1, 2), ty - h)]
        ink_line(px, ctrl, BLACK, 1, rng)
        # Branches
        for _ in range(rng.randint(2, 4)):
            by = ty - rng.randint(h//3, h - 4)
            sign = rng.choice((-1, 1))
            blen = rng.randint(6, 12)
            ink_line(px, [(tx, by), (tx + sign * blen, by - rng.randint(2, 6))],
                     BLACK, 1, rng, dry=True)

    # ── CLIFF BASE / WATER EDGE ───────────────────────────────────────────
    for _ in range(5):
        wy = rng.randint(205, 215)
        wx = rng.randint(14, 48)
        ink_line(px, [(wx, wy), (wx + rng.randint(6, 14), wy + rng.randint(-1, 1))],
                 LIGHT, 1, rng, dry=True)

    # ── MIST TRANSITION ───────────────────────────────────────────────────
    haze(px, 220, 272, MIST, rng, density=0.20)

    # ── NEAR SHORE — smaller, right of center ─────────────────────────────
    sa = math.radians(-12)
    paint_mass(px, [(68, 325, 14, 24, sa, 1.0)], LIGHT, rng, wetness=0.48, noise=0.22, turbulence=0.38)
    paint_mass(px, [(67, 331, 9, 15, sa, 1.0)],  MID,   rng, wetness=0.62, noise=0.15, turbulence=0.28)
    paint_mass(px, [(66, 336, 5, 9,  sa, 1.0)],  DARK,  rng, wetness=0.75, noise=0.10, turbulence=0.18)

    # Shore tree
    ink_line(px, [(68, 305), (67, 290), (68, 278)], BLACK, 1, rng)
    ink_line(px, [(68, 293), (60, 288)], BLACK, 1, rng, dry=True)
    ink_line(px, [(68, 287), (76, 283)], BLACK, 1, rng, dry=True)

    # ── BOAT ─────────────────────────────────────────────────────────────
    ink_line(px, [(46, 415), (56, 418), (66, 415)], DARK, 1, rng)
    ink_line(px, [(56, 410), (56, 418)], BLACK, 1, rng)

    # ── WATER MARKS ──────────────────────────────────────────────────────
    for _ in range(7):
        wy = rng.randint(434, 504)
        wx = rng.randint(4, 80)
        ink_line(px, [(wx, wy), (wx + rng.randint(6, 18), wy)],
                 LIGHT, 1, rng, dry=True)


def main():
    img, px = new_canvas()
    compose(px, RNG)
    out_path = os.path.join(OUT, "attempt_04.png")
    img.save(out_path)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
