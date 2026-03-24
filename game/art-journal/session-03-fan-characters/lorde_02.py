#!/usr/bin/env python3
"""
Audre Lorde in EarthBound / Magicant, Attempt 02

Fixes from 01:
- Face reads dark against pink sky background — warm the skin, add cheek-light
- Skirt/floor connection unclear — anchor her with a small cushion under her
- Papers partially overlapping with background water strip — lift table slightly
- Add a tiny more detail to hair highlight for visual richness
"""
from PIL import Image
import os

OUT = os.path.dirname(os.path.abspath(__file__))
img = Image.open(os.path.join(OUT, "lorde_01.png"))
img = img.resize((160, 120), Image.NEAREST)
px = img.load()
W, H = 160, 120

SKY_B    = (232, 176, 196)
TILE_A   = (240, 184, 200)
TILE_B   = (220, 164, 180)
TILE_G   = (248, 220, 228)
SKIN     = (136, 84, 56)
SKIN_D   = (100, 60, 36)
SKIN_H   = (168, 108, 72)
SKIN_HL  = (192, 132, 92)   # extra bright highlight for pop
HAIR     = (28, 20, 16)
HAIR_H   = (60, 44, 32)
BLOUSE_L = (224, 168, 64)
BLOUSE_M = (192, 136, 40)
BLOUSE_D = (152, 104, 24)
SKIRT_M  = (60, 40, 80)
SKIRT_D  = (40, 24, 56)
SKIRT_L  = (80, 56, 104)
PAPER_L  = (255, 248, 224)
INK      = (36, 28, 44)
TABLE_L  = (232, 196, 136)
TABLE_M  = (200, 160, 96)

FLOOR_Y = H - 32
TABLE_Y = FLOOR_Y - 12

def p(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        px[x, y] = c

def rect(x0, y0, x1, y1, c):
    for y in range(y0, y1):
        for x in range(x0, x1):
            p(x, y, c)

CX = 78
HEAD_Y = TABLE_Y - 30

# ── Fix 1: Warm up the face — add skin highlights to pop against pink sky ──
# The forehead and cheek areas should catch the ambient pink light
# but the face needs more contrast to read

# Warm highlight on right cheek (Magicant ambient is warm-pink)
p(CX + 3, HEAD_Y + 5, SKIN_HL)
p(CX + 3, HEAD_Y + 6, SKIN_HL)
p(CX + 3, HEAD_Y + 7, SKIN_H)

# Forehead highlight
p(CX,     HEAD_Y + 2, SKIN_H)
p(CX + 1, HEAD_Y + 2, SKIN_H)
p(CX + 2, HEAD_Y + 2, SKIN_H)

# Cheekbones — add subtle definition
p(CX + 2, HEAD_Y + 6, SKIN_H)

# Deepen the shadow side for contrast
p(CX - 4, HEAD_Y + 4, SKIN_D)
p(CX - 4, HEAD_Y + 5, SKIN_D)
p(CX - 4, HEAD_Y + 6, SKIN_D)
p(CX - 4, HEAD_Y + 7, SKIN_D)
p(CX - 3, HEAD_Y + 8, SKIN_D)

# ── Fix 2: Hair highlight — slightly more visible texture ─────────────────
# Add a few more HAIR_H pixels at the crown (catching ambient light)
p(CX + 2, HEAD_Y - 4, HAIR_H)
p(CX + 3, HEAD_Y - 4, HAIR_H)
p(CX + 3, HEAD_Y - 3, HAIR_H)
p(CX + 4, HEAD_Y - 3, HAIR_H)
p(CX + 4, HEAD_Y - 2, HAIR_H)
# Also a subtle outline pixel to separate hair from sky at top
for dx in range(-7, 8):
    y_edge = HEAD_Y - 8 + abs(dx) // 2  # approximate top of afro
    if 0 <= CX + dx < W and 0 <= y_edge < H:
        if px[CX + dx, y_edge] == HAIR:
            pass  # already dark, good

# ── Fix 3: Sitting cushion / zafu under her ───────────────────────────────
# A small round cushion visible at floor level grounds her presence
CUSHION_Y = FLOOR_Y - 4
CUSHION_C = (184, 100, 120)   # deep rose cushion
CUSHION_D = (148, 72, 88)     # cushion shadow

for y in range(CUSHION_Y, FLOOR_Y + 1):
    half = 6 - (y - CUSHION_Y) // 2
    for x in range(CX - half, CX + half + 1):
        if px[x, y] in [SKIRT_M, SKIRT_D, SKIRT_L, TILE_A, TILE_B, TILE_G]:
            c = CUSHION_C if y == CUSHION_Y else CUSHION_D
            p(x, y, c)

# ── Fix 4: Papers — patch any that overlapped with water strip ───────────
# The water strip is at y range [FLOOR_Y-20, FLOOR_Y-12] in 160px space
# Table surface papers are at y=[TABLE_Y-9, TABLE_Y+3] = [67, 79] at 1x
# TABLE_Y = FLOOR_Y - 12 = 76, so papers are y=67..79
# Water strip ends at FLOOR_Y-12 = 76 (same as TABLE_Y)
# So the papers may overlap right at the bank line — repaint the center paper

# Confirm center paper is fully above table and water
NB_X = 64
NB_Y = TABLE_Y - 6
rect(NB_X, NB_Y, NB_X + 36, TABLE_Y + 3, PAPER_L)
# Poem lines
for ly in range(NB_Y + 1, TABLE_Y + 2, 2):
    for x in range(NB_X + 2, NB_X + 34, 3):
        p(x, ly, INK)
        p(x + 1, ly, INK)
# Restore table surface underneath paper
for y in range(TABLE_Y, TABLE_Y + 3):
    for x in range(NB_X, NB_X + 36):
        if px[x, y] == PAPER_L:
            pass  # paper on top is fine

# ── Fix 5: Table top — make sure it reads as a surface, not a line ────────
# Repaint the table surface edge in case paper overlap muddied it
rect(44, TABLE_Y, 116, TABLE_Y + 1, TABLE_L)
# Restore papers on top of that
rect(NB_X, TABLE_Y - 6, NB_X + 36, TABLE_Y + 3, PAPER_L)
for ly in range(TABLE_Y - 5, TABLE_Y + 2, 2):
    for x in range(NB_X + 2, NB_X + 34, 3):
        p(x, ly, INK)
        p(x + 1, ly, INK)

# Re-place flowers on top of the table
FX = 46
FY = TABLE_Y - 8
for i in range(4):
    p(FX + i, FY, (255, 160, 176))
    p(FX + i, FY + 2, (240, 80, 100))
p(FX + 1, FY + 1, (240, 192, 48))
p(FX + 2, FY + 1, (240, 192, 48))
p(FX + 1, FY + 3, (80, 136, 64))

FX2 = 108
FY2 = TABLE_Y - 6
p(FX2, FY2, (248, 220, 80));  p(FX2 + 2, FY2, (248, 220, 80))
p(FX2 + 1, FY2 - 1, (248, 220, 80)); p(FX2 + 1, FY2 + 1, (248, 220, 80))
p(FX2 + 1, FY2, (240, 192, 48))
p(FX2 + 1, FY2 + 2, (80, 136, 64))

# ── Save ──────────────────────────────────────────────────────────────────
img.resize((W * 4, H * 4), Image.NEAREST).save(
    os.path.join(OUT, "lorde_02.png"))
print("done — lorde_02.png")
