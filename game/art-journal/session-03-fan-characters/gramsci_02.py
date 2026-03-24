#!/usr/bin/env python3
"""
Gramsci in EarthBound, Attempt 02

Problems with 01:
- Hunch not reading — he looks like he's standing, not hunched over notebooks
- Hair too thin — reads as almost bald, losing the silhouette
- No lamp — EarthBound interiors always have warm point-light on desk
- Torso too narrow and vertical, needs width + forward lean

Fix: rebuild the character with explicit seated-lean. Head closer to desk.
Add body that reads as "stooped over work." Fuller hair. Desk lamp.
"""
from PIL import Image
import os

OUT = os.path.dirname(os.path.abspath(__file__))
img = Image.open(os.path.join(OUT, "gramsci_01.png"))
# Descale back to working resolution
img = img.resize((160, 120), Image.NEAREST)
px = img.load()
W, H = 160, 120

SUIT_D  = (44, 44, 60)
SUIT_M  = (68, 68, 84)
SUIT_L  = (92, 92, 108)
SKIN    = (196, 148, 100)
HAIR    = (34, 26, 14)
GLASS   = (28, 28, 44)
SHIRT   = (228, 220, 202)
INK     = (44, 44, 76)
WALL_A  = (240, 224, 184)
WALL_B  = (220, 204, 164)
DESK_L  = (204, 144, 64)
DESK_M  = (168, 112, 48)
DESK_D  = (120, 72, 28)
NB_PAGE = (248, 240, 208)
NB_COVER= (212, 196, 152)
NB_LINE = (220, 210, 185)

# Lamp colors
LAMP_BASE  = (100, 72, 32)   # dark wood base
LAMP_NECK  = (80, 60, 28)    # neck
LAMP_SHADE = (220, 168, 48)  # warm brass shade
LAMP_GLOW  = (255, 240, 180) # inner glow
LAMP_LIGHT = (255, 248, 210) # pool of light on desk

def p(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        px[x, y] = c

def rect(x0, y0, x1, y1, c):
    for y in range(y0, y1):
        for x in range(x0, x1):
            p(x, y, c)

DESK_TOP_Y = 70
CX = 80

# ── Erase the old character completely ────────────────────────────────────
# Clear the character area back to wall/desk colors
for y in range(20, DESK_TOP_Y + 4):
    for x in range(CX - 14, CX + 16):
        # restore wall
        if y < 82 - 38:  # above floor
            c = WALL_A if y < 62 else WALL_B
        else:
            c = WALL_B
        p(x, y, c)

# Restore desk surface where we're clearing
rect(CX - 14, DESK_TOP_Y, CX + 16, DESK_TOP_Y + 1, DESK_L)
rect(CX - 14, DESK_TOP_Y + 1, CX + 16, DESK_TOP_Y + 4, DESK_M)

# ── Rebuild Gramsci with proper hunch ─────────────────────────────────────
# The hunch: head is LOW, close to desk. Body curves forward.
# Think of him as a C-shape: shoulders back/up, head and hands forward/down.

HEAD_Y = 40   # lower than before — close to desk level
HEAD_CX = CX + 2  # slightly right of center (leaning forward)

# Head (slightly oval — EarthBound heads are wide)
rect(HEAD_CX - 5, HEAD_Y, HEAD_CX + 6, HEAD_Y + 8, SKIN)
# Round the corners
p(HEAD_CX - 5, HEAD_Y,     WALL_B)
p(HEAD_CX + 5, HEAD_Y,     WALL_B)
p(HEAD_CX - 5, HEAD_Y + 7, WALL_B)
p(HEAD_CX + 5, HEAD_Y + 7, WALL_B)

# Hair — thicker, more presence. Gramsci had full dark hair swept back.
rect(HEAD_CX - 4, HEAD_Y - 3, HEAD_CX + 5, HEAD_Y + 2, HAIR)  # main bulk
# Side wisps
for y in range(HEAD_Y, HEAD_Y + 4):
    p(HEAD_CX - 5, y, HAIR)
    p(HEAD_CX + 5, y, HAIR)
# Some texture — slight variation
p(HEAD_CX - 3, HEAD_Y - 4, HAIR)
p(HEAD_CX,     HEAD_Y - 4, HAIR)
p(HEAD_CX + 3, HEAD_Y - 4, HAIR)
# Hair meets forehead
rect(HEAD_CX - 4, HEAD_Y, HEAD_CX + 5, HEAD_Y + 1, HAIR)

# Ears
p(HEAD_CX - 6, HEAD_Y + 3, SKIN)
p(HEAD_CX - 6, HEAD_Y + 4, SKIN)
p(HEAD_CX + 6, HEAD_Y + 3, SKIN)
p(HEAD_CX + 6, HEAD_Y + 4, SKIN)

# Eyes (looking down — slightly lower on face, downcast)
p(HEAD_CX - 2, HEAD_Y + 4, HAIR)
p(HEAD_CX + 2, HEAD_Y + 4, HAIR)

# Glasses — wire frames, characteristic
for x in range(HEAD_CX - 5, HEAD_CX - 1):
    p(x, HEAD_Y + 3, GLASS);  p(x, HEAD_Y + 6, GLASS)
p(HEAD_CX - 5, HEAD_Y + 4, GLASS);  p(HEAD_CX - 5, HEAD_Y + 5, GLASS)
p(HEAD_CX - 1, HEAD_Y + 4, GLASS);  p(HEAD_CX - 1, HEAD_Y + 5, GLASS)
for x in range(HEAD_CX + 1, HEAD_CX + 6):
    p(x, HEAD_Y + 3, GLASS);  p(x, HEAD_Y + 6, GLASS)
p(HEAD_CX + 1, HEAD_Y + 4, GLASS);  p(HEAD_CX + 1, HEAD_Y + 5, GLASS)
p(HEAD_CX + 5, HEAD_Y + 4, GLASS);  p(HEAD_CX + 5, HEAD_Y + 5, GLASS)
p(HEAD_CX, HEAD_Y + 3, GLASS)  # bridge
p(HEAD_CX - 6, HEAD_Y + 3, GLASS);  p(HEAD_CX + 6, HEAD_Y + 3, GLASS)  # arms
# Restore skin inside lenses
for y in range(HEAD_Y + 4, HEAD_Y + 6):
    for x in range(HEAD_CX - 4, HEAD_CX):
        p(x, y, SKIN)
    for x in range(HEAD_CX + 2, HEAD_CX + 5):
        p(x, y, SKIN)
# Eyes back on top
p(HEAD_CX - 2, HEAD_Y + 4, HAIR)
p(HEAD_CX + 2, HEAD_Y + 4, HAIR)

# Mustache (thick — this is important for Gramsci's look)
for x in range(HEAD_CX - 3, HEAD_CX + 4):
    p(x, HEAD_Y + 6, HAIR)
p(HEAD_CX - 2, HEAD_Y + 7, HAIR)
p(HEAD_CX + 2, HEAD_Y + 7, HAIR)

# Neck — short, angled (head is tilted down)
p(HEAD_CX - 1, HEAD_Y + 8, SKIN)
p(HEAD_CX,     HEAD_Y + 8, SKIN)
p(HEAD_CX + 1, HEAD_Y + 8, SKIN)
p(HEAD_CX,     HEAD_Y + 9, SKIN)  # just a pixel

# Shirt collar (small, visible at neck)
p(HEAD_CX - 2, HEAD_Y + 9,  SHIRT)
p(HEAD_CX + 2, HEAD_Y + 9,  SHIRT)
p(HEAD_CX - 1, HEAD_Y + 10, SHIRT)
p(HEAD_CX + 1, HEAD_Y + 10, SHIRT)

# ── Hunched body ───────────────────────────────────────────────────────────
# The key: shoulders are BEHIND the head (he's curled forward).
# Shoulder line is at HEAD_Y + 6, extends wide, then the body curves forward.
# Think of it as a rounded hump shape.

SHOULDER_Y = HEAD_Y + 6
SHOULDER_CX = CX  # shoulders slightly left of head-CX (body behind)

# Shoulder width — wide, this is where the suit reads
for y in range(SHOULDER_Y, SHOULDER_Y + 4):
    half = 9 - (y - SHOULDER_Y)
    for x in range(SHOULDER_CX - half, SHOULDER_CX + half + 2):
        c = SUIT_L if y == SHOULDER_Y else SUIT_M
        p(x, y, c)

# The "hump" of the back — body narrows as it curves down toward desk
for y in range(SHOULDER_Y + 4, DESK_TOP_Y):
    progress = (y - SHOULDER_Y - 4) / max(1, DESK_TOP_Y - SHOULDER_Y - 4)
    # Back gets narrower going down; simultaneously shifts right (leaning)
    half = int(8 - progress * 4)
    lean = int(progress * 3)
    for x in range(SHOULDER_CX - half + lean, SHOULDER_CX + half + lean + 1):
        p(x, y, SUIT_M)
    # Left edge (outer back) — darkest
    p(SHOULDER_CX - half + lean, y, SUIT_D)

# Lapels
p(SHOULDER_CX - 1, SHOULDER_Y + 4, SHIRT)
p(SHOULDER_CX + 1, SHOULDER_Y + 4, SHIRT)
p(SHOULDER_CX,     SHOULDER_Y + 5, SHIRT)

# ── Arms over desk ─────────────────────────────────────────────────────────
# Both arms extended downward onto the notebooks
# Left arm
for y in range(SHOULDER_Y + 4, DESK_TOP_Y + 1):
    p = lambda x, y, c: None  # shadow p to use local
for y in range(SHOULDER_Y + 3, DESK_TOP_Y + 1):
    lx = SHOULDER_CX - 6 - (y - SHOULDER_Y) // 3
    for x in range(lx, lx + 4):
        if 0 <= x < W:
            px[x, y] = SUIT_M
# Right arm
for y in range(SHOULDER_Y + 3, DESK_TOP_Y + 1):
    rx = SHOULDER_CX + 7 + (y - SHOULDER_Y) // 3
    for x in range(rx, rx + 4):
        if 0 <= x < W:
            px[x, y] = SUIT_M

def p(x, y, c):  # restore p
    if 0 <= x < W and 0 <= y < H:
        px[x, y] = c

# Hands on notebooks
# Left hand — ink visible
rect(52, DESK_TOP_Y - 2, 58, DESK_TOP_Y + 1, SKIN)
p(53, DESK_TOP_Y - 3, SKIN)  # extended finger (writing)
p(52, DESK_TOP_Y - 3, INK)   # ink on fingertip

# Right hand — holding edge of notebook
rect(96, DESK_TOP_Y - 2, 102, DESK_TOP_Y + 1, SKIN)
p(100, DESK_TOP_Y - 2, INK)

# ── Desk lamp (right side of desk) ────────────────────────────────────────
LX = 104  # lamp center x
# Base
rect(LX - 3, DESK_TOP_Y, LX + 3, DESK_TOP_Y + 2, LAMP_BASE)
# Neck (thin, slightly curved)
for y in range(DESK_TOP_Y - 8, DESK_TOP_Y):
    offset = (DESK_TOP_Y - y) // 5
    p(LX + offset, y, LAMP_NECK)
    p(LX + offset + 1, y, LAMP_NECK)
# Shade (triangle pointing down-left)
SHADE_TIP_Y = DESK_TOP_Y - 8
for i in range(7):
    shade_y = SHADE_TIP_Y - i
    for x in range(LX - i, LX + i + 2):
        p(x, shade_y, LAMP_SHADE)
    # inner glow
    if i > 1:
        for x in range(LX - i + 1, LX + i):
            p(x, shade_y, LAMP_GLOW)

# Light pool on desk surface (warm glow under the lamp)
for x in range(96, 116):
    dist = abs(x - LX)
    if dist < 10:
        p(x, DESK_TOP_Y,     LAMP_LIGHT)
        p(x, DESK_TOP_Y + 1, LAMP_LIGHT if dist < 6 else DESK_L)
        p(x, DESK_TOP_Y + 2, DESK_L if dist < 4 else DESK_M)

# ── Wall behind lamp gets a faint warm glow ───────────────────────────────
for y in range(SHADE_TIP_Y - 6, DESK_TOP_Y):
    for x in range(LX - 4, LX + 12):
        dist_sq = (x - LX) ** 2 + (y - (SHADE_TIP_Y - 3)) ** 2
        if dist_sq < 64:
            r, g, b = px[x, y]
            p(x, y, (min(255, r + 12), min(255, g + 4), b))

# ── Save ──────────────────────────────────────────────────────────────────
img.resize((W * 4, H * 4), Image.NEAREST).save(
    os.path.join(OUT, "gramsci_02.png"))
print("done — gramsci_02.png")
