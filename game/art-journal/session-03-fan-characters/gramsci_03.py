#!/usr/bin/env python3
"""
Gramsci in EarthBound, Attempt 03

Fixes:
- Collar pixels at shoulders read as vampire cape — remove, relocate to neck V
- Face slightly dark behind glasses — warm the skin inside the lens frames
- Clean up arm edges
- Add a faint shadow under the desk (grounds him in the room)
"""
from PIL import Image
import os

OUT = os.path.dirname(os.path.abspath(__file__))
img = Image.open(os.path.join(OUT, "gramsci_02.png"))
img = img.resize((160, 120), Image.NEAREST)
px = img.load()
W, H = 160, 120

SKIN    = (196, 148, 100)
SKIN_W  = (210, 165, 115)   # slightly warmer/lighter skin for face interior
HAIR    = (34, 26, 14)
GLASS   = (28, 28, 44)
SHIRT   = (228, 220, 202)
SUIT_D  = (44, 44, 60)
SUIT_M  = (68, 68, 84)
SUIT_L  = (92, 92, 108)
WALL_B  = (220, 204, 164)
DESK_M  = (168, 112, 48)
FLOOR_A = (200, 184, 148)
FLOOR_B = (180, 164, 130)
SHADOW  = (160, 148, 120)   # desk drop shadow on floor

def p(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        px[x, y] = c

# ── Fix: remove the vampire-cape collar pixels at shoulders ───────────────
# Those SHIRT-colored pixels at SHOULDER_Y+4 and SHOULDER_Y+5 (around y=51-52)
# Shoulder center is CX=80, shoulder_y = HEAD_Y+6 = 46, so shoulder+4 = 50
SHOULDER_Y = 46
for y in range(SHOULDER_Y + 3, SHOULDER_Y + 7):
    for x in range(72, 90):
        if px[x, y] == SHIRT:
            p(x, y, SUIT_M)  # replace with suit

# ── Fix: warm the skin inside the glasses frames ──────────────────────────
# The lens frames are at HEAD_CX=82, HEAD_Y=40
HEAD_CX = 82
HEAD_Y  = 40
# Left lens interior: x range(78, 82), y range(HEAD_Y+4, HEAD_Y+6)
for y in range(HEAD_Y + 4, HEAD_Y + 6):
    for x in range(HEAD_CX - 4, HEAD_CX):
        if px[x, y] == SKIN:
            p(x, y, SKIN_W)
# Right lens interior
for y in range(HEAD_Y + 4, HEAD_Y + 6):
    for x in range(HEAD_CX + 2, HEAD_CX + 5):
        if px[x, y] == SKIN:
            p(x, y, SKIN_W)

# ── Add proper shirt V at neck (replaces the high collar pixels) ──────────
# The V should be at the top of the torso, below the neck
V_Y = HEAD_Y + 10
p(HEAD_CX - 2, V_Y,     SHIRT)
p(HEAD_CX + 2, V_Y,     SHIRT)
p(HEAD_CX - 1, V_Y + 1, SHIRT)
p(HEAD_CX + 1, V_Y + 1, SHIRT)
p(HEAD_CX,     V_Y + 2, SHIRT)  # V-tip

# ── Slight arm cleanup — soften the blobby edges ──────────────────────────
# Left arm region: roughly x=58-68, y=50-70
# Just darken the very outer pixel of each arm row for definition
for y in range(SHOULDER_Y + 4, 70):
    # Find leftmost suit pixel in this row
    for x in range(50, 75):
        if px[x, y] == SUIT_M:
            p(x, y, SUIT_D)  # darken outer edge
            break
    # Find rightmost suit on right arm
    for x in range(100, 75, -1):
        if px[x, y] == SUIT_M:
            p(x, y, SUIT_D)
            break

# ── Drop shadow under desk onto floor ────────────────────────────────────
# A soft dark band just below the desk front face
DESK_BOT = 82
for x in range(44, 116):
    dist = abs(x - 80)
    intensity = max(0, 1.0 - dist / 40.0)
    if intensity > 0.2:
        r, g, b = px[x, DESK_BOT]
        p(x, DESK_BOT,     (int(r * 0.85), int(g * 0.85), int(b * 0.85)))
        p(x, DESK_BOT + 1, (int(r * 0.92), int(g * 0.92), int(b * 0.92)))

# ── Save ──────────────────────────────────────────────────────────────────
img.resize((160 * 4, 120 * 4), Image.NEAREST).save(
    os.path.join(OUT, "gramsci_03.png"))
print("done — gramsci_03.png")
