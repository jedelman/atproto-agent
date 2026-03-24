#!/usr/bin/env python3
"""
Session 03 — Fan Characters
Elinor Ostrom in A Link to the Past, Attempt 02

Fixes from 01:
- Face too small/unreadable — enlarge head slightly, bold the eyes and smile
- Center bookcase below books reads as dark alcove — fill backing with wall color
- Left arm indistinguishable from robe body — add definition with darker edge
- Right arm angle: tighten the scroll-hold gesture so it reads as "actively reading"
"""
from PIL import Image
import os

OUT = os.path.dirname(os.path.abspath(__file__))
img = Image.open(os.path.join(OUT, "ostrom_01.png"))
img = img.resize((160, 120), Image.NEAREST)
px = img.load()
W, H = 160, 120

# Palette (same as 01)
WALL_L   = (224, 212, 176)
WALL_D   = (196, 180, 144)
STONE_D  = (128, 112, 84)
WOOD_L   = (176, 128, 72)
WOOD_M   = (136, 96, 48)
WOOD_D   = (96, 64, 24)
FLOOR_L  = (216, 200, 160)
FLOOR_D  = (184, 168, 128)
ROBE_L   = (212, 168, 80)
ROBE_M   = (180, 136, 56)
ROBE_D   = (136, 100, 32)
ROBE_DK  = (100, 72, 20)
SKIN     = (220, 172, 120)
SKIN_D   = (188, 144, 96)
HAIR_L   = (204, 196, 176)
HAIR_M   = (164, 156, 140)
HAIR_D   = (120, 112, 100)
SCROLL_L = (240, 224, 176)
SCROLL_M = (208, 192, 144)
SCROLL_D = (176, 160, 112)
SCROLL_R = (160, 120, 64)

def p(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        px[x, y] = c

def rect(x0, y0, x1, y1, c):
    for y in range(y0, y1):
        for x in range(x0, x1):
            p(x, y, c)

FLOOR_Y = H - 36
CX = 76

# ── Fix 1: Center bookcase backing — replace dark stone with wall color ────
# The center bookcase occupies x=56..104, y=0..28
# Below the books (y=4..28) the STONE_D backing reads as dark alcove
# Patch: fill the non-book, non-shelf areas with WALL_L
for y in range(4, 28):
    for x in range(57, 103):
        if px[x, y] == STONE_D:
            p(x, y, WALL_D)

# ── Fix 2: Face — bolder features ─────────────────────────────────────────
HEAD_Y = 38

# Enlarge head slightly (was CX-5..CX+5, CX=76)
# Already sized at 10px wide — keep size, improve feature contrast
# Warm up the skin a touch (current SKIN is already warm, keep it)

# Eyes — make them 2px tall instead of 1px dots
p(CX - 1, HEAD_Y + 4, (32, 24, 16))
p(CX - 1, HEAD_Y + 5, (32, 24, 16))  # extra row
p(CX + 2, HEAD_Y + 4, (32, 24, 16))
p(CX + 2, HEAD_Y + 5, (32, 24, 16))  # extra row

# Eyebrows (subtle — silver, slightly darker than hair)
p(CX - 2, HEAD_Y + 3, HAIR_D)
p(CX - 1, HEAD_Y + 3, HAIR_D)
p(CX + 1, HEAD_Y + 3, HAIR_D)
p(CX + 2, HEAD_Y + 3, HAIR_D)

# Smile — a touch warmer/more defined
p(CX - 2, HEAD_Y + 7, SKIN_D)
p(CX - 1, HEAD_Y + 7, (160, 120, 96))   # slightly darker mouth center
p(CX,     HEAD_Y + 7, SKIN_D)
p(CX + 1, HEAD_Y + 7, SKIN_D)
# Smile lift at corners
p(CX - 2, HEAD_Y + 8, SKIN_D)
p(CX + 1, HEAD_Y + 8, SKIN_D)

# Nose suggestion (ALttP characters sometimes have a small dot)
p(CX,     HEAD_Y + 6, SKIN_D)

# ── Fix 3: Left arm definition ─────────────────────────────────────────────
# Left arm runs along CX-6, CX-7 from ROBE_Y to ROBE_Y+18
ROBE_Y = HEAD_Y + 12   # = 50

# Darken the outermost edge of the left arm to separate it from the robe body
for y in range(ROBE_Y, ROBE_Y + 18):
    # Check if there's robe color at CX-7
    if px[CX - 7, y] == ROBE_D:
        p(CX - 7, y, ROBE_DK)
    # Add a shadow pixel one step further out if inside bounds
    p(CX - 8, y, ROBE_DK) if px[CX - 8, y] in [ROBE_D, ROBE_M, ROBE_L] else None

# ── Fix 4: Right arm — tighten scroll-hold angle ─────────────────────────
# Current right arm drifts too far right. Tighten it so it reads as
# "holding scroll at body side" rather than extended outward.
# ARM_Y = ROBE_Y + 4 = 54

ARM_Y = ROBE_Y + 4
# Clear the old arm pixels in that region
for y in range(ARM_Y, ARM_Y + 12):
    offset = (y - ARM_Y) // 3
    # Clear both old arm pixel positions
    for dx in [7 + offset, 8 + offset]:
        if 0 <= CX + dx < W:
            # Replace with robe body color if it's arm color
            if px[CX + dx, y] in [ROBE_M, ROBE_L]:
                p(CX + dx, y, WALL_L)

# Redraw tighter arm — less outward drift
for y in range(ARM_Y, ARM_Y + 12):
    offset = (y - ARM_Y) // 5   # slower drift = arm stays closer to body
    p(CX + 6 + offset, y, ROBE_M)
    p(CX + 7 + offset, y, ROBE_M)

# Move scroll closer in accordingly
# Clear old scroll area
SX_OLD = CX + 12
SY = ARM_Y + 8

# Recalculate scroll position based on tighter arm
SX = CX + 9   # moved in from 12 to 9

# Clear old scroll pixels
for y_c in range(SY - 10, SY + 19):
    for x_c in range(SX_OLD - 4, SX_OLD + 7):
        if px[x_c, y_c] in [SCROLL_R, SCROLL_M, SCROLL_L, SCROLL_D]:
            p(x_c, y_c, WALL_L)

# Redraw scroll at new position
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

# ── Repair any wall pixels accidentally painted into the robe body ──────
# Walk the robe area and patch stray WALL_L back
for y in range(ROBE_Y, FLOOR_Y + 2):
    progress = (y - ROBE_Y) / max(1, FLOOR_Y - ROBE_Y)
    half = int(5 + progress * 8)
    # Only patch pixels that are now WALL_L but inside the robe boundary
    for x in range(CX - half + 1, CX + half):
        if px[x, y] == WALL_L and y > ROBE_Y + 4:
            # If surrounded by robe pixels, it's a stray patch
            neighbors = [px[x-1, y], px[x+1, y], px[x, y-1], px[x, y+1]]
            robe_neighbors = sum(1 for c in neighbors if c in [ROBE_L, ROBE_M, ROBE_D, ROBE_DK])
            if robe_neighbors >= 2:
                p(x, y, ROBE_M)

# ── Save ──────────────────────────────────────────────────────────────────
img.resize((W * 4, H * 4), Image.NEAREST).save(
    os.path.join(OUT, "ostrom_02.png"))
print("done — ostrom_02.png")
