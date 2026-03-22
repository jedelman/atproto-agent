#!/usr/bin/env python3
"""
Gilt-City Ground Tileset — Void's Folly
Generates 128x128 SNES-era floor tiles.
Cracks and dither are stochastic (seeded for reproducibility).
"""
from PIL import Image
import math, random, os

SIZE = 128
OUT = os.path.dirname(os.path.abspath(__file__))

# Seeded RNG — change seed to explore different crack shapes
RNG = random.Random(7)

# --- Gilt-City palette ---
G_HIGHLIGHT = (240, 248, 255)
G_BASE      = (184, 220, 240)
G_MID       = (144, 192, 224)
G_DEEP      = (104, 152, 200)
G_SHADOW    = ( 56,  80, 144)
G_VOID      = ( 24,  32,  64)
GOLD_LIGHT  = (240, 208,  96)
GOLD_BASE   = (200, 146,  42)
GOLD_DARK   = (122,  80,  24)
CRACK       = ( 16,  24,  40)
CRACK_EDGE  = (200, 228, 248)


def new_tile(fill=G_BASE):
    img = Image.new("RGB", (SIZE, SIZE), fill)
    return img, img.load()


# ── Dither ────────────────────────────────────────────────────────────────────

def add_dither_texture(px, base=G_BASE, max_density=0.10, seed=None):
    """
    Sparse stochastic dither, lower-right quadrant.
    Density ramps up gradually from the quadrant edge to avoid a hard boundary.
    """
    rng = random.Random(seed or 99)
    x0 = SIZE // 2 + 4
    y0 = SIZE // 2 + 4
    ramp = SIZE // 4  # pixels over which density rises from 0 to max

    for y in range(y0, SIZE - 4):
        for x in range(x0, SIZE - 4):
            if px[x, y] != base:
                continue
            # Density ramps with distance from quadrant origin
            t = min(1.0, min(x - x0, y - y0) / ramp)
            density = max_density * t
            r = rng.random()
            if r < density * 0.6:
                px[x, y] = G_MID
            elif r < density:
                px[x, y] = G_DEEP


# ── Specular ──────────────────────────────────────────────────────────────────

def add_specular(px):
    """Diagonal specular streak, upper-left quadrant."""
    for i in range(6, 28):
        px[i, i - 4] = G_HIGHLIGHT
        px[i + 1, i - 4] = G_HIGHLIGHT
    for i in range(8, 26):
        if px[i - 2, i - 4] == G_BASE:
            px[i - 2, i - 4] = G_MID
        if px[i + 3, i - 3] == G_BASE:
            px[i + 3, i - 3] = G_MID
    for dx in range(-1, 3):
        for dy in range(-1, 3):
            px[10 + dx, 6 + dy] = G_HIGHLIGHT


# ── Panel seams ───────────────────────────────────────────────────────────────

def add_panel_seams(px, base=G_BASE):
    mid = SIZE // 2
    for i in range(2, SIZE - 2):
        for offset in (0, 1):
            if px[i, mid - 1 + offset] == base:
                px[i, mid - 1 + offset] = G_MID
            if px[mid - 1 + offset, i] == base:
                px[mid - 1 + offset, i] = G_MID
    for dx in range(-1, 3):
        for dy in range(-1, 3):
            px[mid - 1 + dx, mid - 1 + dy] = G_DEEP


# ── Depth edge ────────────────────────────────────────────────────────────────

def add_depth_edge(px):
    for i in range(SIZE):
        px[i, SIZE - 1] = G_VOID
        px[i, SIZE - 2] = G_SHADOW
        px[i, SIZE - 3] = G_DEEP
        px[SIZE - 1, i] = G_VOID
        px[SIZE - 2, i] = G_SHADOW
        px[SIZE - 3, i] = G_DEEP
        px[i, 0] = G_HIGHLIGHT
        px[i, 1] = G_BASE
        px[0, i] = G_HIGHLIGHT
        px[1, i] = G_BASE


# ── Stochastic crack walk ─────────────────────────────────────────────────────

def crack_walk(px, x, y, angle, steps, width=2, branch_prob=0.12,
               jitter=0.18, base_colors=None, rng=None, depth=0):
    """
    Walk a crack from (x, y) in direction `angle` for `steps` pixels.
    Jitters direction each step, branches randomly at 30-60° offsets.
    Max recursion depth = 2 (main → branch → sub-branch).
    """
    if base_colors is None:
        base_colors = (G_BASE, G_MID, G_DEEP)
    if rng is None:
        rng = RNG

    cx, cy = float(x), float(y)
    dx = math.cos(angle)
    dy = math.sin(angle)

    for step in range(steps):
        # Jitter direction
        dx += rng.uniform(-jitter, jitter)
        dy += rng.uniform(-jitter, jitter)
        mag = math.hypot(dx, dy)
        dx /= mag
        dy /= mag

        ix, iy = int(cx), int(cy)

        # Draw crack pixels (width × 1)
        for w in range(width):
            for wx, wy in ((ix + w, iy), (ix, iy + w)):
                if 0 <= wx < SIZE and 0 <= wy < SIZE:
                    px[wx, wy] = CRACK

        # Catch-light on upper-left edge of crack
        for ex, ey in ((ix - 1, iy), (ix, iy - 1)):
            if 0 <= ex < SIZE and 0 <= ey < SIZE and px[ex, ey] in base_colors:
                px[ex, ey] = CRACK_EDGE

        # Chance to branch
        if depth < 2 and step > steps // 5 and rng.random() < branch_prob:
            sign = rng.choice((-1, 1))
            branch_angle = angle + sign * rng.uniform(math.pi / 6, math.pi / 2.5)
            branch_steps = int(steps * rng.uniform(0.25, 0.55))
            crack_walk(px, ix, iy, branch_angle, branch_steps,
                       width=max(1, width - 1), branch_prob=branch_prob * 0.5,
                       jitter=jitter * 1.3, base_colors=base_colors,
                       rng=rng, depth=depth + 1)

        cx += dx
        cy += dy

        # Stop if we walk off the tile
        if not (0 <= int(cx) < SIZE and 0 <= int(cy) < SIZE):
            break


# ── Turkish weaver reductive pass ────────────────────────────────────────────

def reductive_pass(img):
    """
    At every harsh color boundary, insert the defined intermediate color.
    Reads from a snapshot so changes don't cascade.
    CRACK_EDGE (catch-light) pixels are never overwritten.
    """
    w, h = img.size
    snap = [img.getpixel((x, y)) for y in range(h) for x in range(w)]

    def s(x, y):
        return snap[y * w + x]

    px = img.load()
    PROTECTED = {CRACK_EDGE}

    # (pixel_color, neighbor_color) → recolor pixel to this intermediate
    # Order matters: first matching rule wins per pixel.
    rules = [
        # Crack shadow halo: glass pixels adjacent to crack darken on the non-catch-light side
        (G_BASE,      CRACK,      G_DEEP),
        (G_MID,       CRACK,      G_SHADOW),
        (G_HIGHLIGHT, CRACK,      G_MID),
        # Gold vein sides: dark glass softens into amber
        (G_DEEP,      GOLD_BASE,  GOLD_DARK),
        (G_SHADOW,    GOLD_BASE,  GOLD_DARK),
        (G_DEEP,      GOLD_LIGHT, GOLD_BASE),
        (G_SHADOW,    GOLD_LIGHT, GOLD_DARK),
        # Specular falloff: base adjacent to highlight gets mid
        (G_BASE,      G_HIGHLIGHT, G_MID),
        # Deep shadow softens into void
        (G_DEEP,      G_VOID,     G_SHADOW),
    ]

    neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for y in range(h):
        for x in range(w):
            c = s(x, y)
            if c in PROTECTED:
                continue
            for dx, dy in neighbors:
                nx, ny = x + dx, y + dy
                if not (0 <= nx < w and 0 <= ny < h):
                    continue
                n = s(nx, ny)
                for pixel_col, neighbor_col, new_col in rules:
                    if c == pixel_col and n == neighbor_col:
                        px[x, y] = new_col
                        break
                else:
                    continue
                break  # first rule match wins; move to next pixel


# ── Tiles ─────────────────────────────────────────────────────────────────────

def make_polished_glass_floor():
    img, px = new_tile(G_BASE)
    add_specular(px)
    add_panel_seams(px)
    add_dither_texture(px, seed=11)
    add_depth_edge(px)
    reductive_pass(img)
    img.save(os.path.join(OUT, "floor_glass_polished.png"))
    print("  floor_glass_polished.png")


def make_cracked_glass_floor():
    img, px = new_tile(G_BASE)
    add_specular(px)
    add_panel_seams(px)
    add_dither_texture(px, seed=22)

    rng = random.Random(42)

    # Main crack: from upper-center, walks toward lower-right
    crack_walk(px, 38, 12, angle=math.radians(105), steps=90,
               width=2, branch_prob=0.14, jitter=0.15, rng=rng)

    # Secondary crack: lower-left panel, shorter
    crack_walk(px, 18, 82, angle=math.radians(75), steps=40,
               width=1, branch_prob=0.10, jitter=0.20, rng=rng)

    add_depth_edge(px)
    reductive_pass(img)
    img.save(os.path.join(OUT, "floor_glass_cracked.png"))
    print("  floor_glass_cracked.png")


def make_gold_veined_floor():
    img, px = new_tile(G_SHADOW)

    # Lighter interior
    for y in range(4, SIZE - 4):
        for x in range(4, SIZE - 4):
            px[x, y] = G_DEEP

    # Stochastic dither over lower half
    rng_d = random.Random(55)
    for y in range(SIZE // 2, SIZE - 4):
        for x in range(4, SIZE - 4):
            if px[x, y] == G_DEEP and rng_d.random() < 0.12:
                px[x, y] = G_SHADOW

    base_colors = (G_SHADOW, G_DEEP)

    rng = random.Random(77)

    # Main vein: lower-left to upper-right diagonal
    crack_walk(px, 8, 110, angle=math.radians(-52), steps=115,
               width=2, branch_prob=0.09, jitter=0.10,
               base_colors=base_colors, rng=rng)

    # Crossing vein: upper-left to lower-right
    crack_walk(px, 14, 16, angle=math.radians(52), steps=80,
               width=2, branch_prob=0.08, jitter=0.10,
               base_colors=base_colors, rng=rng)

    # Recolor CRACK → GOLD_BASE for veins, CRACK_EDGE → GOLD_LIGHT
    for y in range(SIZE):
        for x in range(SIZE):
            if px[x, y] == CRACK:
                px[x, y] = GOLD_BASE
            elif px[x, y] == CRACK_EDGE:
                px[x, y] = GOLD_LIGHT

    # Void border
    for i in range(SIZE):
        for w in range(3):
            px[i, w] = G_VOID
            px[w, i] = G_VOID
            px[i, SIZE - 1 - w] = G_VOID
            px[SIZE - 1 - w, i] = G_VOID

    reductive_pass(img)
    img.save(os.path.join(OUT, "floor_gold_veined.png"))
    print("  floor_gold_veined.png")


def make_hairline_floor():
    img, px = new_tile(G_BASE)
    add_specular(px)
    add_panel_seams(px)
    add_dither_texture(px, seed=33)

    rng = random.Random(13)

    # Single hairline — 1px wide, low branch probability
    crack_walk(px, 44, 18, angle=math.radians(108), steps=75,
               width=1, branch_prob=0.04, jitter=0.12, rng=rng)

    add_depth_edge(px)
    reductive_pass(img)
    img.save(os.path.join(OUT, "floor_glass_hairline.png"))
    print("  floor_glass_hairline.png")


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Generating Gilt-City floor tiles (128x128) →")
    make_polished_glass_floor()
    make_cracked_glass_floor()
    make_gold_veined_floor()
    make_hairline_floor()
    print(f"\nDone. Output: {OUT}/")
