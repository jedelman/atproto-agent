#!/usr/bin/env python3
"""
Fanon in Chrono Trigger, Attempt 02

Fixes from 01:
- Notebook buried behind desk edge — raise it to read above surface
- Bottom-left silhouette reads as debris — rework as huddled seated person
- Head corners too boxy — CT style needs more roundness
- Add a few more writing implements on desk surface (small detail richness)
"""
from PIL import Image
import os

OUT = os.path.dirname(os.path.abspath(__file__))
img = Image.open(os.path.join(OUT, "fanon_01.png"))
img = img.resize((160, 120), Image.NEAREST)
px = img.load()
W, H = 160, 120

DOME_MID   = (44, 56, 72)
DOME_DARK  = (28, 36, 52)
DOME_RUST  = (80, 52, 28)
RUST_L     = (108, 72, 36)
CRATE_L    = (96, 72, 40)
CRATE_M    = (72, 52, 28)
CRATE_D    = (48, 32, 12)
STEEL_L    = (80, 96, 112)
STEEL_D    = (52, 64, 76)
SKIN       = (168, 112, 72)
SKIN_D     = (128, 84, 52)
SKIN_H     = (196, 136, 88)
HAIR       = (24, 20, 16)
HAIR_H     = (48, 40, 28)
FATIGUE_L  = (88, 100, 64)
FATIGUE_M  = (64, 76, 48)
FATIGUE_D  = (44, 56, 32)
FATIGUE_DK = (32, 40, 24)
NB_COVER   = (96, 64, 32)
NB_PAGE    = (232, 220, 192)
NB_LINE    = (200, 188, 160)
INK        = (24, 24, 36)
STETH_T    = (100, 88, 60)

FLOOR_Y = H - 30
DESK_TOP_Y = FLOOR_Y - 22

def p(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        px[x, y] = c

def rect(x0, y0, x1, y1, c):
    for y in range(y0, y1):
        for x in range(x0, x1):
            p(x, y, c)

CX = 80
HEAD_Y = DESK_TOP_Y - 30

# ── Fix 1: Round the head corners more (CT style) ─────────────────────────
# Current head: rect(CX-6, HEAD_Y, CX+6, HEAD_Y+12, SKIN)
# CT heads are wider and round. Set corners to background.
# Top corners
p(CX - 6, HEAD_Y,      DOME_MID)
p(CX - 5, HEAD_Y,      DOME_MID)   # extra corner pixel
p(CX + 5, HEAD_Y,      DOME_MID)
p(CX + 4, HEAD_Y,      DOME_MID)   # extra corner pixel
# Bottom corners
p(CX - 6, HEAD_Y + 11, DOME_MID)
p(CX - 5, HEAD_Y + 11, DOME_MID)
p(CX + 5, HEAD_Y + 11, DOME_MID)
p(CX + 4, HEAD_Y + 11, DOME_MID)
# Restore any skin lost at these boundary pixels to DOME_MID
# (CT characters blend softly into environment at edges)

# ── Fix 2: Notebook raised so it reads above desk surface ─────────────────
# Clear old notebook position
NB_X_OLD = 74
NB_Y_OLD = DESK_TOP_Y - 5
for y in range(NB_Y_OLD - 1, DESK_TOP_Y + 3):
    for x in range(NB_X_OLD - 1, NB_X_OLD + 19):
        if px[x, y] in [NB_COVER, NB_PAGE, NB_LINE, INK]:
            # Restore desk or atmosphere color
            if y >= DESK_TOP_Y:
                p(x, y, CRATE_L if y == DESK_TOP_Y or y == DESK_TOP_Y + 1 else CRATE_M)
            else:
                # Leave as-is (might be body/arm pixels)
                pass

# Redraw notebook higher — centered under his writing hand
NB_X = 68
NB_Y = DESK_TOP_Y - 9   # raised: top of notebook visible above desk edge
NB_W = 18
NB_H = DESK_TOP_Y - NB_Y + 2

# Open notebook spread
rect(NB_X, NB_Y + 2, NB_X + NB_W, DESK_TOP_Y + 2, NB_COVER)   # cover base
rect(NB_X + 1, NB_Y, NB_X + NB_W - 1, DESK_TOP_Y + 1, NB_PAGE)  # pages
# Left page lines
for ly in range(NB_Y + 1, DESK_TOP_Y + 1, 2):
    for x in range(NB_X + 2, NB_X + 8):
        p(x, ly, NB_LINE)
# Right page lines + writing
for ly in range(NB_Y + 1, DESK_TOP_Y + 1, 2):
    for x in range(NB_X + 11, NB_X + NB_W - 1):
        p(x, ly, NB_LINE)
# Some ink words on right page (short strokes)
for ly in range(NB_Y + 2, DESK_TOP_Y, 3):
    for x in range(NB_X + 11, NB_X + 17, 3):
        p(x, ly, INK)
        p(x + 1, ly, INK)
# Spine crease
for y in range(NB_Y, DESK_TOP_Y + 2):
    p(NB_X + 9, y, NB_COVER)

# ── Fix 3: Pencil / stylus visible on desk surface ────────────────────────
# Small pen lying on desk to the right of notebook
PEN_Y = DESK_TOP_Y + 1
for x in range(NB_X + NB_W + 2, NB_X + NB_W + 10):
    p(x, PEN_Y, (120, 96, 48))   # pen barrel (brass-ish)
p(NB_X + NB_W + 10, PEN_Y, INK)  # nib
p(NB_X + NB_W + 1,  PEN_Y, (140, 100, 48))  # end cap

# ── Fix 4: Survivor silhouette — rework as huddled person ─────────────────
# Clear old silhouette area (lower left)
for y in range(FLOOR_Y - 20, FLOOR_Y + 1):
    for x in range(26, 48):
        if px[x, y] in [DOME_RUST, RUST_L]:
            r, g, b = px[x, y]
            # Check if it's floor
            if y >= FLOOR_Y - 2:
                c_new = STEEL_L if ((x // 8) + (y // 6)) % 2 == 0 else STEEL_D
            else:
                # Restore to lit dome color (lamp warms this area)
                c_new = (52, 56, 52)  # darkened-warm (lamp falloff)
            p(x, y, c_new)

# Redraw: a seated figure huddled against left wall
# Silhouette: dark, very simple, reading as human — knees up, arms around knees
SIL_X = 32
SIL_FLOOR = FLOOR_Y - 1
SIL_COLOR = (48, 44, 36)   # dark, slightly warm (lamp reaching them faintly)
SIL_DARK  = (32, 28, 24)

# Knees drawn up (the classic "huddled in shelter" pose)
# Legs/knees
rect(SIL_X - 3, SIL_FLOOR - 6, SIL_X + 4, SIL_FLOOR - 4, SIL_COLOR)
rect(SIL_X - 4, SIL_FLOOR - 4, SIL_X + 5, SIL_FLOOR - 1, SIL_DARK)  # feet/lower body
# Torso hunched over knees
rect(SIL_X - 2, SIL_FLOOR - 14, SIL_X + 3, SIL_FLOOR - 6, SIL_COLOR)
# Head resting on knees / arms
p(SIL_X - 1, SIL_FLOOR - 16, SIL_COLOR)
p(SIL_X,     SIL_FLOOR - 16, SIL_COLOR)
p(SIL_X + 1, SIL_FLOOR - 16, SIL_COLOR)
p(SIL_X - 1, SIL_FLOOR - 15, SIL_COLOR)
p(SIL_X,     SIL_FLOOR - 15, SIL_COLOR)
p(SIL_X + 1, SIL_FLOOR - 15, SIL_COLOR)

# Arms wrapped around knees
p(SIL_X - 3, SIL_FLOOR - 10, SIL_COLOR)
p(SIL_X - 3, SIL_FLOOR - 9,  SIL_COLOR)
p(SIL_X + 3, SIL_FLOOR - 10, SIL_COLOR)
p(SIL_X + 3, SIL_FLOOR - 9,  SIL_COLOR)

# Faint warm tint from lamp reaching this corner
for y in range(SIL_FLOOR - 16, SIL_FLOOR + 1):
    for x in range(SIL_X - 4, SIL_X + 6):
        r, g, b = px[x, y]
        if (r, g, b) not in [(0, 0, 0)]:  # don't touch pure black
            p(x, y, (min(255, r + 6), min(255, g + 3), b))

# ── Save ──────────────────────────────────────────────────────────────────
img.resize((W * 4, H * 4), Image.NEAREST).save(
    os.path.join(OUT, "fanon_02.png"))
print("done — fanon_02.png")
