#!/usr/bin/env python3
"""
Session 03 — Fan Characters
Elinor Ostrom in A Link to the Past, Attempt 01

Setting: Kakariko Village library — the book-filled house already in the game.
Ostrom as a scholar-sage: ochre robes, practical, older, carrying a scroll.
She wrote the books about the Imprisoning War that Link reads. Still writing.

ALttP visual language:
- 3/4 overhead perspective (structures show their side/back at reduced height)
- Characters read in silhouette — Link's purple hair, her ochre warmth
- 15 colors + transparency per sprite
- The world uses limited palettes with high contrast per area
- Kakariko: warm stone tones, brown wood, some greens

Canvas: 160×120 at 4x scale (640×480)
"""
from PIL import Image
import os

W, H = 160, 120
SCALE = 4
OUT = os.path.dirname(os.path.abspath(__file__))

img = Image.new('RGB', (W, H))
px = img.load()

# ── ALttP Kakariko palette ────────────────────────────────────────────────
STONE_L  = (200, 184, 152)   # light stone floor/wall
STONE_M  = (168, 152, 120)   # mid stone
STONE_D  = (128, 112, 84)    # dark stone / shadow
WOOD_L   = (176, 128, 72)    # light wood (shelf face)
WOOD_M   = (136, 96, 48)     # mid wood
WOOD_D   = (96, 64, 24)      # dark wood / shadow
BOOK_R   = (192, 56, 40)     # red spine
BOOK_B   = (56, 88, 160)     # blue spine
BOOK_G   = (64, 120, 64)     # green spine
BOOK_T   = (184, 152, 96)    # tan spine
BOOK_P   = (128, 64, 128)    # purple spine
BOOK_DK  = (80, 48, 96)      # dark spine (old tome)
FLOOR_L  = (216, 200, 160)   # flagstone floor light
FLOOR_D  = (184, 168, 128)   # flagstone floor dark
WALL_L   = (224, 212, 176)   # wall light
WALL_D   = (196, 180, 144)   # wall shadow
RUG_A    = (160, 64, 48)     # rug red
RUG_B    = (128, 48, 32)     # rug dark red
RUG_TRIM = (212, 160, 48)    # rug gold trim

# Ostrom character — ochre/warm earth tones
ROBE_L   = (212, 168, 80)    # ochre robe highlight
ROBE_M   = (180, 136, 56)    # ochre robe mid
ROBE_D   = (136, 100, 32)    # ochre robe shadow
ROBE_DK  = (100, 72, 20)     # robe deepest shadow
SKIN     = (220, 172, 120)   # warm skin (lighter than Gramsci — older, different tone)
SKIN_D   = (188, 144, 96)    # skin shadow
HAIR_L   = (204, 196, 176)   # silver-white hair light
HAIR_M   = (164, 156, 140)   # silver hair mid
HAIR_D   = (120, 112, 100)   # silver hair shadow
SCROLL_L = (240, 224, 176)   # scroll parchment light
SCROLL_M = (208, 192, 144)   # scroll parchment mid
SCROLL_D = (176, 160, 112)   # scroll shadow
SCROLL_R = (160, 120, 64)    # scroll rod

def p(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        px[x, y] = c

def rect(x0, y0, x1, y1, c):
    for y in range(y0, y1):
        for x in range(x0, x1):
            p(x, y, c)

FLOOR_Y = H - 36

# ── Floor (flagstone pattern) ──────────────────────────────────────────────
for y in range(FLOOR_Y, H):
    for x in range(W):
        # irregular flagstone — larger pattern than EarthBound's tiles
        tile_x = x // 12
        tile_y = y // 10
        # offset alternating rows
        if tile_y % 2 == 0:
            tx = tile_x
        else:
            tx = tile_x + 1
        p(x, y, FLOOR_L if tx % 2 == 0 else FLOOR_D)

# Flagstone grout lines
for y in range(FLOOR_Y, H, 10):
    for x in range(W):
        p(x, y, STONE_D)
for x in range(0, W, 12):
    for y in range(FLOOR_Y, H):
        row = (y - FLOOR_Y) // 10
        if row % 2 == 0:
            p(x, y, STONE_D)
        else:
            p(x + 6 if x + 6 < W else x, y, STONE_D)

# ── Small rug in front of the reading area ────────────────────────────────
RUG_X0, RUG_Y0, RUG_X1, RUG_Y1 = 52, FLOOR_Y + 4, 108, FLOOR_Y + 22
rect(RUG_X0, RUG_Y0, RUG_X1, RUG_Y1, RUG_A)
# Pattern — simple diamond
for y in range(RUG_Y0, RUG_Y1):
    for x in range(RUG_X0, RUG_X1):
        # diamond pattern
        cx_d = (RUG_X0 + RUG_X1) // 2
        cy_d = (RUG_Y0 + RUG_Y1) // 2
        if abs(x - cx_d) + abs(y - cy_d) == 10:
            p(x, y, RUG_TRIM)
        elif abs(x - cx_d) + abs(y - cy_d) < 4:
            p(x, y, RUG_TRIM)
        elif abs(x - cx_d) % 8 == 0 or abs(y - cy_d) % 6 == 0:
            p(x, y, RUG_B)
# Rug border
for x in range(RUG_X0, RUG_X1):
    p(x, RUG_Y0, RUG_TRIM);  p(x, RUG_Y1 - 1, RUG_TRIM)
for y in range(RUG_Y0, RUG_Y1):
    p(RUG_X0, y, RUG_TRIM);  p(RUG_X1 - 1, y, RUG_TRIM)

# ── Wall ──────────────────────────────────────────────────────────────────
for y in range(FLOOR_Y):
    for x in range(W):
        p(x, y, WALL_L if y < FLOOR_Y - 16 else WALL_D)

# ── Bookshelves (ALttP style — lower, more solid-looking) ──────────────────
def draw_shelf_alttp(x0, x1, y0, y1):
    """ALttP shelves: stone/wood construction, heavier look than EarthBound"""
    # Back (dark stone)
    rect(x0, y0, x1, y1, STONE_D)
    # Shelf boards — thicker, ALttP style
    for by in range(y0 + 12, y1, 18):
        rect(x0, by, x1, by + 4, WOOD_M)
        rect(x0, by, x1, by + 1, WOOD_L)  # top edge highlight
        rect(x0, by + 3, x1, by + 4, WOOD_D)  # bottom shadow
    # Books
    book_colors = [BOOK_R, BOOK_DK, BOOK_B, BOOK_T, BOOK_G, BOOK_P, BOOK_T, BOOK_B]
    bw = max(3, (x1 - x0) // len(book_colors))
    for by in range(y0, y1 - 18, 18):
        for i, bc in enumerate(book_colors):
            bx0 = x0 + i * bw
            bx1 = min(bx0 + bw - 1, x1 - 1)
            rect(bx0, by + 4, bx1, by + 12, bc)
    # Right edge trim
    for y in range(y0, y1):
        p(x1 - 1, y, WOOD_L)
    # Left edge shadow
    for y in range(y0, y1):
        p(x0, y, STONE_D)

draw_shelf_alttp(0, 28, 0, FLOOR_Y)
draw_shelf_alttp(W - 28, W, 0, FLOOR_Y)

# Center bookcase on back wall (between shelves)
draw_shelf_alttp(56, 104, 0, 28)
# Stone top/sides of center case
rect(54, 0, 106, 4, STONE_M)

# ── Ostrom ────────────────────────────────────────────────────────────────
# ALttP perspective: characters face the viewer at a slight 3/4 angle
# She's standing near center, slightly left, facing right-ish
CX = 76
HEAD_Y = 38

# Head (rounder than EarthBound, ALttP has slightly larger heads relative to body)
rect(CX - 5, HEAD_Y, CX + 5, HEAD_Y + 10, SKIN)
# Slight shading — left side
for y in range(HEAD_Y, HEAD_Y + 10):
    p(CX - 5, y, SKIN_D)
    p(CX - 4, y, SKIN_D)

# Silver hair — tied up in a practical bun
# Bun at top
rect(CX - 3, HEAD_Y - 5, CX + 4, HEAD_Y + 1, HAIR_M)
p(CX - 3, HEAD_Y - 5, HAIR_L);  p(CX + 3, HEAD_Y - 5, HAIR_L)
# Bun knot
rect(CX, HEAD_Y - 6, CX + 2, HEAD_Y - 3, HAIR_D)
# Side hair (coming down to ears)
for y in range(HEAD_Y + 1, HEAD_Y + 6):
    p(CX - 5, y, HAIR_M)
    p(CX + 5, y, HAIR_M)
# A few silver wisps
p(CX - 4, HEAD_Y - 1, HAIR_L)
p(CX + 4, HEAD_Y - 1, HAIR_L)

# Face — older, kind expression
# Eyes (ALttP eyes are simple dots)
p(CX - 1, HEAD_Y + 4, (32, 24, 16))
p(CX + 2, HEAD_Y + 4, (32, 24, 16))
# Small wrinkles / lines beside eyes
p(CX + 4, HEAD_Y + 4, SKIN_D)
p(CX - 4, HEAD_Y + 5, SKIN_D)
# Slight smile
p(CX - 1, HEAD_Y + 7, SKIN_D)
p(CX,     HEAD_Y + 7, SKIN_D)
p(CX + 1, HEAD_Y + 7, SKIN_D)

# Neck
rect(CX - 1, HEAD_Y + 10, CX + 2, HEAD_Y + 13, SKIN)

# ── Ochre robe — her defining visual feature ──────────────────────────────
# Body (wider and more substantial — ALttP characters have broader bases)
ROBE_Y = HEAD_Y + 12

for y in range(ROBE_Y, FLOOR_Y + 2):
    progress = (y - ROBE_Y) / max(1, FLOOR_Y - ROBE_Y)
    half = int(5 + progress * 8)  # robe widens toward hem
    for x in range(CX - half, CX + half + 1):
        # Shading: left side darker, right lighter
        if x == CX - half:
            c = ROBE_DK
        elif x < CX:
            c = ROBE_D
        elif x > CX + half - 2:
            c = ROBE_L
        else:
            c = ROBE_M
        p(x, y, c)
    # Robe hem detail — small decorative edge at bottom
    if y > FLOOR_Y - 4:
        p(CX - half, y, ROBE_D)
        p(CX + half, y, ROBE_D)

# Collar — simple V neck showing robe opening
p(CX - 1, ROBE_Y,     ROBE_DK)
p(CX + 1, ROBE_Y,     ROBE_DK)
p(CX,     ROBE_Y + 1, ROBE_DK)

# Belt/sash (darker band around waist)
SASH_Y = ROBE_Y + 14
for x in range(CX - 8, CX + 9):
    if px[x, SASH_Y] == ROBE_M or px[x, SASH_Y] == ROBE_L:
        p(x, SASH_Y,     ROBE_D)
        p(x, SASH_Y + 1, ROBE_D)
        p(x, SASH_Y + 2, ROBE_M)

# ── Arms and scroll ───────────────────────────────────────────────────────
# Left arm (at side, hanging)
for y in range(ROBE_Y, ROBE_Y + 18):
    p(CX - 6, y, ROBE_D)
    p(CX - 7, y, ROBE_D)
# Left hand
rect(CX - 8, ROBE_Y + 18, CX - 5, ROBE_Y + 22, SKIN_D)

# Right arm — holding a scroll outward
ARM_Y = ROBE_Y + 4
for y in range(ARM_Y, ARM_Y + 12):
    offset = (y - ARM_Y) // 3
    p(CX + 7 + offset, y, ROBE_M)
    p(CX + 8 + offset, y, ROBE_M)

# Scroll (held in right hand, partially unrolled)
SX = CX + 12
SY = ARM_Y + 8
# Scroll rod top
rect(SX, SY - 8, SX + 2, SY, SCROLL_R)
# Scroll roll at top
for x in range(SX - 2, SX + 4):
    p(x, SY - 9, SCROLL_M)
    p(x, SY - 10, SCROLL_L)
# Unrolled portion hanging down
rect(SX - 3, SY, SX + 5, SY + 16, SCROLL_M)
# Parchment lines (text)
for ly in range(SY + 2, SY + 15, 2):
    for x in range(SX - 2, SX + 4):
        p(x, ly, SCROLL_L)
# Curled bottom edge
for x in range(SX - 2, SX + 5):
    p(x, SY + 16, SCROLL_D)
# Bottom rod
rect(SX - 1, SY + 16, SX + 4, SY + 18, SCROLL_R)

# ── Small reading stand / lectern at her side ────────────────────────────
STAND_X = CX - 24
STAND_Y = FLOOR_Y - 16
rect(STAND_X, STAND_Y, STAND_X + 16, STAND_Y + 2, WOOD_L)   # top surface
rect(STAND_X, STAND_Y + 2, STAND_X + 16, FLOOR_Y, WOOD_M)   # body
rect(STAND_X + 2, FLOOR_Y - 2, STAND_X + 14, FLOOR_Y, WOOD_D) # base
# Open book on the lectern
rect(STAND_X + 1, STAND_Y - 3, STAND_X + 15, STAND_Y, SCROLL_M)
p(STAND_X + 8, STAND_Y - 3, SCROLL_D)  # center spine
for x in range(STAND_X + 2, STAND_X + 8):
    p(x, STAND_Y - 2, SCROLL_L)
for x in range(STAND_X + 9, STAND_X + 14):
    p(x, STAND_Y - 2, SCROLL_L)

# ── Shadow under Ostrom (grounds the character) ───────────────────────────
for x in range(CX - 10, CX + 14):
    dist = abs(x - CX)
    if dist < 12:
        r, g, b = px[x, FLOOR_Y]
        p(x, FLOOR_Y, (int(r * 0.82), int(g * 0.82), int(b * 0.82)))

# ── Save ──────────────────────────────────────────────────────────────────
img.resize((W * SCALE, H * SCALE), Image.NEAREST).save(
    os.path.join(OUT, "ostrom_01.png"))
print("done — ostrom_01.png")
