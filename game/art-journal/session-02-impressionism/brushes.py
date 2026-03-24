"""
Brush library for pixel painting.
Each brush is a function that takes (px, W, H, rng) plus placement args
and paints directly onto px.
"""
import math, random


def dab(px, W, H, x, y, tone, r=3, density=0.7, rng=None):
    """Small loaded-brush touch. Circular cluster, uneven fill."""
    rng = rng or random.Random()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx*dx + dy*dy <= r*r:
                if rng.random() < density:
                    cx, cy = x + dx, y + dy
                    if 0 <= cx < W and 0 <= cy < H:
                        px[cx, cy] = tone


def sweep(px, W, H, x0, y, length, tone, width=1, curve=0.3,
          gap=0.10, rng=None, clip_y=None):
    """
    Curved horizontal sweep. Monet's sky stroke.
    curve: amplitude of the arc. direction: random.
    clip_y: (y_min, y_max) to keep stroke within a band.
    """
    rng = rng or random.Random()
    direction = rng.choice([-1, 1])
    cy = float(y)
    for i in range(length):
        cy += direction * curve * math.sin(i / max(length, 1) * math.pi)
        cx = x0 + i
        iy = int(cy)
        if clip_y and not (clip_y[0] <= iy < clip_y[1]):
            continue
        if 0 <= cx < W and 0 <= iy < H:
            if rng.random() >= gap:
                for w in range(width):
                    if 0 <= iy + w < H:
                        px[cx, iy + w] = tone


def dry(px, W, H, x0, y, length, tone, gap=0.35, drift=0.5, rng=None,
        clip_y=None):
    """
    Dry brush — heavy gap, slight vertical drift. Scratchy texture.
    Good for broken water surface and rough atmospheric marks.
    """
    rng = rng or random.Random()
    cy = float(y)
    for i in range(length):
        cy += rng.uniform(-drift, drift)
        cx = x0 + i
        iy = int(cy)
        if clip_y and not (clip_y[0] <= iy < clip_y[1]):
            continue
        if 0 <= cx < W and 0 <= iy < H:
            if rng.random() >= gap:
                px[cx, iy] = tone


def flat(px, W, H, x0, x1, y, tone, gap=0.05, rng=None):
    """
    Flat horizontal mark — loaded brush, nearly solid.
    Good for water surface bands and horizon edge.
    """
    rng = rng or random.Random()
    for x in range(x0, x1):
        if 0 <= x < W and 0 <= y < H:
            if rng.random() >= gap:
                px[x, y] = tone


def smear(px, W, H, x0, x1, y0, y1, direction='h', strength=0.4, rng=None):
    """
    Smear existing pixels — blend neighbors.
    direction 'h': horizontal smear (good for reflections, water).
    direction 'v': vertical smear (good for mist, dissolve effects).
    """
    rng = rng or random.Random()
    if direction == 'h':
        for y in range(y0, y1):
            for x in range(x0 + 1, x1):
                if rng.random() < strength:
                    if 0 <= x < W and 0 <= y < H and 0 <= x-1 < W:
                        c0, c1 = px[x-1, y], px[x, y]
                        px[x, y] = tuple((c0[i] + c1[i]) // 2 for i in range(3))
    else:
        for x in range(x0, x1):
            for y in range(y0 + 1, y1):
                if rng.random() < strength:
                    if 0 <= x < W and 0 <= y < H and 0 <= y-1 < H:
                        c0, c1 = px[x, y-1], px[x, y]
                        px[x, y] = tuple((c0[i] + c1[i]) // 2 for i in range(3))


def scatter(px, W, H, x0, x1, y0, y1, tone, density=0.15, rng=None):
    """
    Random scatter of single pixels in a region. Good for atmospheric grain,
    mist, distant texture.
    """
    rng = rng or random.Random()
    for y in range(y0, y1):
        for x in range(x0, x1):
            if rng.random() < density:
                px[x, y] = tone
