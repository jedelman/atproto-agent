#!/usr/bin/env python3
"""
Session 03 — Fan Characters
Audre Lorde in EarthBound, Attempt 01

Setting: Magicant — Ness's inner world. Pink tiles, dreamlike, the place where
your truest self lives. Audre Lorde's presence here is correct: she wrote from
the interior, named what others refused to name. "Poetry is not a luxury. It is
a vital necessity of our existence."

Her signature: natural hair (distinctive round silhouette — perfect pixel art),
deep warm brown skin, a gold/amber blouse. She's writing at a low table — not a
desk but a sitting surface, more informal, more earthbound in another sense.

EarthBound Magicant visual language:
- Pink/rose sky, warm pastel tile floor
- Dreamy spatial logic — some floating elements
- Soft saturated palette, high chroma but gentle
- Characters retain EarthBound's chunky warm-sprite style
- The Eight Melodies pond nearby (implied by water-color horizon)

EarthBound aesthetic specifics:
- 8px tile grid, checkerboard floor variation with pink/rose
- Interior and exterior blend (Magicant blurs inside/outside)
- Warm lamp light, flowers, practical magic

Canvas: 160×120 at 4x scale (640×480)
"""
from PIL import Image
import os

W, H = 160, 120
SCALE = 4
OUT = os.path.dirname(os.path.abspath(__file__))

img = Image.new('RGB', (W, H))
px = img.load()

# ── Palette: Magicant ────────────────────────────────────────────────────
SKY_A    = (248, 200, 216)   # magicant sky pink-rose
SKY_B    = (232, 176, 196)   # sky lower (slightly deeper)
CLOUD_L  = (255, 228, 236)   # cloud light
CLOUD_D  = (240, 208, 220)   # cloud shadow
TILE_A   = (240, 184, 200)   # floor tile rose-pink
TILE_B   = (220, 164, 180)   # floor tile darker pink
TILE_G   = (248, 220, 228)   # grout line / lighter tile variation
WATER_L  = (148, 196, 240)   # pond/water light (Eight Melodies horizon)
WATER_D  = (116, 164, 208)   # water deeper
WATER_G  = (196, 228, 248)   # water shimmer

# Small table (low, Japanese-style sitting)
TABLE_L  = (232, 196, 136)   # light wood
TABLE_M  = (200, 160, 96)    # mid wood
TABLE_D  = (160, 120, 60)    # shadow wood
TABLE_DK = (120, 88, 36)     # deep shadow

# Flowers
PETAL_R  = (240, 80, 100)    # deep rose petal
PETAL_L  = (255, 160, 176)   # light petal
PETAL_Y  = (248, 220, 80)    # yellow flower
CENTER   = (240, 192, 48)    # flower center
STEM     = (80, 136, 64)     # stem green
LEAF     = (96, 160, 72)     # leaf green

# Audre Lorde character
SKIN     = (136, 84, 56)     # warm dark brown skin
SKIN_D   = (100, 60, 36)     # skin shadow
SKIN_H   = (168, 108, 72)    # skin highlight
HAIR     = (28, 20, 16)      # very dark hair
HAIR_H   = (60, 44, 32)      # hair highlight
BLOUSE_L = (224, 168, 64)    # gold/amber blouse light
BLOUSE_M = (192, 136, 40)    # blouse mid
BLOUSE_D = (152, 104, 24)    # blouse shadow
SKIRT_L  = (80, 56, 104)     # deep purple skirt light
SKIRT_M  = (60, 40, 80)      # skirt mid
SKIRT_D  = (40, 24, 56)      # skirt shadow
PAPER_L  = (255, 248, 224)   # manuscript/poem paper light
PAPER_M  = (240, 232, 200)   # paper mid
PAPER_D  = (220, 212, 180)   # paper shadow
INK      = (36, 28, 44)      # ink

def p(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        px[x, y] = c

def rect(x0, y0, x1, y1, c):
    for y in range(y0, y1):
        for x in range(x0, x1):
            p(x, y, c)

FLOOR_Y = H - 32

# ── Sky (Magicant) ────────────────────────────────────────────────────────
for y in range(FLOOR_Y):
    for x in range(W):
        # Gradient sky: lighter at top, deeper toward horizon
        if y < FLOOR_Y // 2:
            p(x, y, SKY_A)
        else:
            # Blend toward horizon
            t = (y - FLOOR_Y // 2) / (FLOOR_Y // 2)
            r = int(248 - t * 16)
            g = int(200 - t * 24)
            b = int(216 - t * 20)
            p(x, y, (r, g, b))

# ── Clouds (floating, dreamy) ─────────────────────────────────────────────
def draw_cloud(cx, cy, w, h):
    for dy in range(h):
        for dx in range(w):
            dist_x = abs(dx - w // 2) / (w // 2)
            dist_y = abs(dy - h // 2) / (h // 2)
            if dist_x**2 + dist_y**2 < 0.85:
                c = CLOUD_L if dy < h // 2 else CLOUD_D
                p(cx - w // 2 + dx, cy - h // 2 + dy, c)

draw_cloud(30, 16, 24, 8)
draw_cloud(120, 10, 20, 6)
draw_cloud(70, 22, 16, 6)

# ── Pond / water on the horizon (Eight Melodies reference) ───────────────
# A strip of water visible in the far background
POND_Y = FLOOR_Y - 20
rect(0, POND_Y, W, POND_Y + 8, WATER_D)
# Shimmer
for x in range(0, W, 8):
    for y in range(POND_Y, POND_Y + 8):
        if (x // 4 + y) % 3 == 0:
            p(x, y, WATER_L)
        elif (x // 4 + y) % 7 == 0:
            p(x, y, WATER_G)
# Bank
rect(0, POND_Y - 2, W, POND_Y, STEM)   # green bank
p_row = POND_Y - 3
for x in range(0, W):
    if x % 4 == 0:
        p(x, p_row, LEAF)

# ── Floor tiles (Magicant rose-pink checkerboard) ─────────────────────────
for y in range(FLOOR_Y, H):
    for x in range(W):
        if ((x // 8) + (y // 8)) % 2 == 0:
            p(x, y, TILE_A)
        else:
            p(x, y, TILE_B)
# Grout lines
for x in range(0, W, 8):
    for y in range(FLOOR_Y, H):
        p(x, y, TILE_G)
for y in range(FLOOR_Y, H, 8):
    for x in range(W):
        p(x, y, TILE_G)

# ── Low writing table ─────────────────────────────────────────────────────
TABLE_X0 = 44
TABLE_X1 = 116
TABLE_Y  = FLOOR_Y - 12

rect(TABLE_X0, TABLE_Y, TABLE_X1, TABLE_Y + 2, TABLE_L)     # surface highlight
rect(TABLE_X0, TABLE_Y + 2, TABLE_X1, TABLE_Y + 6, TABLE_M) # surface
rect(TABLE_X0, TABLE_Y + 6, TABLE_X1, TABLE_Y + 10, TABLE_D) # face
# Table legs (short — low table)
rect(TABLE_X0 + 2, TABLE_Y + 10, TABLE_X0 + 6, FLOOR_Y, TABLE_DK)
rect(TABLE_X1 - 6, TABLE_Y + 10, TABLE_X1 - 2, FLOOR_Y, TABLE_DK)
# Shadow under table on floor
for x in range(TABLE_X0 + 4, TABLE_X1 - 4):
    r, g, b = px[x, FLOOR_Y]
    p(x, FLOOR_Y, (int(r * 0.90), int(g * 0.90), int(b * 0.90)))

# ── Papers on table — open manuscript / poem ──────────────────────────────
# Several sheets, slightly scattered
# Left sheet (partially under center)
rect(50, TABLE_Y - 4, 74, TABLE_Y + 2, PAPER_M)
rect(50, TABLE_Y - 4, 74, TABLE_Y, PAPER_L)
# Lines on left sheet
for ly in range(TABLE_Y - 3, TABLE_Y, 2):
    for x in range(52, 72, 3):
        p(x, ly, INK)
        p(x + 1, ly, INK)
# Center sheet (active — writing in progress)
rect(64, TABLE_Y - 6, 100, TABLE_Y + 3, PAPER_L)
# Poem text — actual pixel-line writing
for ly in range(TABLE_Y - 5, TABLE_Y + 2, 2):
    for x in range(66, 98, 3):
        p(x, ly, INK)
        p(x + 1, ly, INK)
# Right paper
rect(92, TABLE_Y - 3, 112, TABLE_Y + 2, PAPER_M)

# ── Flowers on the table corner ───────────────────────────────────────────
FX = 46
FY = TABLE_Y - 8
# Rose bloom
for i in range(4):
    p(FX + i, FY, PETAL_L)
    p(FX + i, FY + 2, PETAL_R)
p(FX, FY + 1, PETAL_R);  p(FX + 3, FY + 1, PETAL_R)
p(FX + 1, FY + 1, PETAL_L);  p(FX + 2, FY + 1, PETAL_L)
# Center
p(FX + 1, FY + 1, CENTER)
p(FX + 2, FY + 1, CENTER)
# Stem
p(FX + 1, FY + 3, STEM)
p(FX + 1, FY + 4, STEM)
p(FX + 2, FY + 4, LEAF)  # small leaf

# Another small flower (yellow)
FX2 = 108
FY2 = TABLE_Y - 6
p(FX2, FY2, PETAL_Y);  p(FX2 + 2, FY2, PETAL_Y)
p(FX2 + 1, FY2 - 1, PETAL_Y); p(FX2 + 1, FY2 + 1, PETAL_Y)
p(FX2 + 1, FY2, CENTER)
p(FX2 + 1, FY2 + 2, STEM);  p(FX2 + 1, FY2 + 3, STEM)

# ── Audre Lorde ───────────────────────────────────────────────────────────
# Seated on floor at low table, cross-legged, leaning slightly forward
# This reads as "in her element" — not at a desk but at her own level

CX = 78
HEAD_Y = TABLE_Y - 30

# Head (EarthBound: slightly wide, warm)
rect(CX - 5, HEAD_Y, CX + 5, HEAD_Y + 10, SKIN)
# Round corners (EarthBound has soft sprites)
p(CX - 5, HEAD_Y,      SKY_B)
p(CX + 4, HEAD_Y,      SKY_B)
p(CX - 5, HEAD_Y + 9,  TILE_A)
p(CX + 4, HEAD_Y + 9,  TILE_A)

# Skin shading
for y in range(HEAD_Y + 1, HEAD_Y + 9):
    p(CX + 4, y, SKIN_H)   # right highlight
    p(CX - 4, y, SKIN_D)   # left shadow

# ── Natural hair — the key silhouette ─────────────────────────────────────
# Round, full afro: extends above and around head
# This is the visual signature — distinct round mass
HAIR_CX = CX
HAIR_CY = HEAD_Y + 1  # center of hair mass

for dy in range(-9, 4):
    for dx in range(-8, 9):
        # Ellipse: slightly wider than tall, natural shape
        if (dx / 8.0) ** 2 + (dy / 6.5) ** 2 < 1.0:
            hy = HAIR_CY + dy
            hx = HAIR_CX + dx
            # Don't overwrite face skin below HEAD_Y+2
            if hy < HEAD_Y + 2 or hx < CX - 5 or hx > CX + 4:
                c = HAIR_H if dy < -4 and dx > 0 else HAIR
                p(hx, hy, c)

# Face features
# Eyes (EarthBound = simple dots but warm)
p(CX - 2, HEAD_Y + 5, (28, 20, 16))
p(CX + 1, HEAD_Y + 5, (28, 20, 16))
# Whites
p(CX - 1, HEAD_Y + 5, (220, 192, 164))   # warm white
p(CX + 2, HEAD_Y + 5, (220, 192, 164))
# Eyebrows
p(CX - 3, HEAD_Y + 4, HAIR)
p(CX - 2, HEAD_Y + 4, HAIR)
p(CX,     HEAD_Y + 4, HAIR)
p(CX + 1, HEAD_Y + 4, HAIR)

# Nose
p(CX - 1, HEAD_Y + 6, SKIN_D)
p(CX,     HEAD_Y + 6, SKIN_D)
p(CX + 1, HEAD_Y + 6, SKIN_D)

# Mouth — gentle, warm, the suggestion of words about to come
p(CX - 2, HEAD_Y + 8, SKIN_D)
p(CX - 1, HEAD_Y + 8, (112, 68, 48))   # lip
p(CX,     HEAD_Y + 8, (112, 68, 48))
p(CX + 1, HEAD_Y + 8, (112, 68, 48))
p(CX + 2, HEAD_Y + 8, SKIN_D)

# Earrings (she wore statement earrings — a tiny gold pixel)
p(CX - 6, HEAD_Y + 5, (220, 180, 40))   # gold earring left
p(CX + 5, HEAD_Y + 5, (220, 180, 40))   # gold earring right

# Neck
rect(CX - 1, HEAD_Y + 10, CX + 2, HEAD_Y + 13, SKIN)

# ── Gold/amber blouse ─────────────────────────────────────────────────────
TORSO_Y = HEAD_Y + 12

# Blouse — loose, flowing, warm gold
for y in range(TORSO_Y, TABLE_Y + 2):
    progress = (y - TORSO_Y) / max(1, TABLE_Y - TORSO_Y)
    half = int(7 + progress * 4)
    for x in range(CX - half, CX + half + 1):
        if x == CX - half:
            c = BLOUSE_D
        elif x < CX - 2:
            c = BLOUSE_M
        elif x > CX + half - 2:
            c = BLOUSE_L   # right-side catch-light
        else:
            c = BLOUSE_M
        p(x, y, c)

# Collar detail — scoop neck
p(CX - 2, TORSO_Y, BLOUSE_D)
p(CX + 1, TORSO_Y, BLOUSE_D)
p(CX - 1, TORSO_Y + 1, BLOUSE_D)
p(CX,     TORSO_Y + 1, BLOUSE_D)

# ── Arms ──────────────────────────────────────────────────────────────────
# Both arms extended forward to the low table (she's leaning in, writing)
ARM_Y = TORSO_Y + 5

for y in range(ARM_Y, TABLE_Y + 1):
    progress = (y - ARM_Y) / max(1, TABLE_Y - ARM_Y)
    # Left arm — extends left toward paper
    lx = CX - 8 - int(progress * 6)
    p(lx,     y, BLOUSE_D)
    p(lx + 1, y, BLOUSE_M)
    p(lx + 2, y, BLOUSE_M)
    # Right arm — extends right toward paper
    rx = CX + 8 + int(progress * 4)
    p(rx - 2, y, BLOUSE_M)
    p(rx - 1, y, BLOUSE_M)
    p(rx,     y, BLOUSE_L)

# Hands on paper
rect(CX - 16, TABLE_Y - 2, CX - 11, TABLE_Y + 1, SKIN)
p(CX - 16, TABLE_Y - 3, SKIN)   # writing finger
p(CX - 16, TABLE_Y - 3, INK)    # ink
rect(CX + 11, TABLE_Y - 2, CX + 16, TABLE_Y + 1, SKIN_H)

# ── Seated cross-legged (lower body, at floor level) ──────────────────────
# Seated silhouette at the base: purple skirt pooling on the floor
SEAT_Y = TABLE_Y + 2

# Cross-legged: skirt spreads horizontally at floor level
for y in range(SEAT_Y, FLOOR_Y + 1):
    progress = (y - SEAT_Y) / max(1, FLOOR_Y - SEAT_Y)
    half = int(8 + progress * 6)
    for x in range(CX - half, CX + half + 1):
        if x == CX - half or x == CX + half:
            c = SKIRT_D
        elif x < CX:
            c = SKIRT_M
        else:
            c = SKIRT_L
        p(x, y, c)

# ── Pen in hand / visible ─────────────────────────────────────────────────
for y in range(TABLE_Y - 6, TABLE_Y - 1):
    p(CX - 15, y, (160, 120, 48))   # golden pen barrel
p(CX - 15, TABLE_Y - 7, INK)   # nib

# ── Shadow under Lorde ────────────────────────────────────────────────────
for x in range(CX - 14, CX + 16):
    r, g, b = px[x, FLOOR_Y]
    p(x, FLOOR_Y, (int(r * 0.88), int(g * 0.88), int(b * 0.88)))

# ── Save ──────────────────────────────────────────────────────────────────
img.resize((W * SCALE, H * SCALE), Image.NEAREST).save(
    os.path.join(OUT, "lorde_01.png"))
print("done — lorde_01.png")
