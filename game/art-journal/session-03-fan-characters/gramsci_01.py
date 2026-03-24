#!/usr/bin/env python3
"""
Session 03 — Fan Characters
Gramsci in EarthBound, Attempt 01

First pass: establish the scene.
Onett library interior. Antonio Gramsci seated at a desk, slightly hunched,
ink-stained fingers on open notebooks.

Working in EarthBound's aesthetic: 8px tile grid, warm interior palette,
chunky character sprites. Canvas 160×120, displayed 4x (640×480).
"""
from PIL import Image
import os

W, H = 160, 120
SCALE = 4
OUT = os.path.dirname(os.path.abspath(__file__))

img = Image.new('RGB', (W, H))
px = img.load()

# ── Palette ────────────────────────────────────────────────────────────────
WALL_A     = (240, 224, 184)   # warm cream wall
WALL_B     = (220, 204, 164)   # wall shadow (lower)
FLOOR_A    = (200, 184, 148)   # floor tile light
FLOOR_B    = (180, 164, 130)   # floor tile dark
SHELF_D    = (112, 68, 24)     # bookshelf dark wood
SHELF_M    = (152, 96, 40)     # bookshelf mid wood
SHELF_L    = (196, 136, 64)    # bookshelf light edge
BOOK_R     = (188, 56, 44)     # red book spine
BOOK_B     = (60, 92, 156)     # blue book spine
BOOK_G     = (72, 128, 72)     # green book spine
BOOK_T     = (196, 164, 108)   # tan book spine
BOOK_P     = (132, 72, 140)    # purple book spine
DESK_L     = (204, 144, 64)    # desk top highlight
DESK_M     = (168, 112, 48)    # desk surface
DESK_D     = (120, 72, 28)     # desk front face / shadow
NB_PAGE    = (248, 240, 208)   # notebook page cream
NB_COVER   = (212, 196, 152)   # notebook cover
NB_LINE    = (220, 210, 185)   # faint ruled line
WIN_LIGHT  = (248, 236, 204)   # window glow (overcast Onett sky)
FRAME      = (100, 64, 24)     # window/door frame

# Gramsci
SUIT_D     = (44, 44, 60)      # charcoal suit shadow
SUIT_M     = (68, 68, 84)      # charcoal suit mid
SUIT_L     = (92, 92, 108)     # charcoal suit highlight
SKIN       = (196, 148, 100)   # warm olive-tan skin
HAIR       = (34, 26, 14)      # dark brown-black hair
GLASS      = (28, 28, 44)      # glasses frames
SHIRT      = (228, 220, 202)   # off-white shirt
INK        = (44, 44, 76)      # ink-stained fingers

def p(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        px[x, y] = c

def rect(x0, y0, x1, y1, c):
    for y in range(y0, y1):
        for x in range(x0, x1):
            p(x, y, c)

# ── Wall + floor fill ──────────────────────────────────────────────────────
FLOOR_Y = H - 38

for y in range(H):
    for x in range(W):
        if y < FLOOR_Y:
            # wall gets slightly darker toward floor
            p(x, y, WALL_A if y < FLOOR_Y - 20 else WALL_B)
        else:
            # 8px checkerboard tile floor
            if ((x // 8) + (y // 8)) % 2 == 0:
                p(x, y, FLOOR_A)
            else:
                p(x, y, FLOOR_B)

# ── Bookshelves (left 22px, right 22px) ───────────────────────────────────
SHELF_W = 22

def draw_shelf(x0, x1):
    # back panel
    rect(x0, 0, x1, FLOOR_Y, SHELF_D)
    # horizontal boards every 16px
    for by in range(14, FLOOR_Y, 16):
        rect(x0, by, x1, by + 2, SHELF_M)
        rect(x0, by + 2, x1, by + 3, SHELF_L)  # lip highlight
    # fill books between boards
    book_cycle = [BOOK_R, BOOK_B, BOOK_G, BOOK_T, BOOK_P, BOOK_T, BOOK_B, BOOK_R]
    shelf_w = x1 - x0
    bw = max(3, shelf_w // len(book_cycle))
    for by in range(0, FLOOR_Y - 16, 16):
        for i, bc in enumerate(book_cycle):
            bx0 = x0 + i * bw
            bx1 = min(bx0 + bw - 1, x1 - 1)
            rect(bx0, by + 3, bx1, by + 14, bc)
    # right edge highlight
    for y in range(FLOOR_Y):
        p(x1 - 1, y, SHELF_L)

draw_shelf(0, SHELF_W)
draw_shelf(W - SHELF_W, W)

# ── Window (back wall, above desk) ────────────────────────────────────────
WX, WY, WW, WH_px = 58, 6, 44, 30
rect(WX, WY, WX + WW, WY + WH_px, WIN_LIGHT)
# frame
for x in range(WX - 1, WX + WW + 1):
    p(x, WY - 1, FRAME);  p(x, WY + WH_px, FRAME)
for y in range(WY - 1, WY + WH_px + 1):
    p(WX - 1, y, FRAME);  p(WX + WW, y, FRAME)
# mullions
for y in range(WY, WY + WH_px):
    p(WX + WW // 2, y, FRAME)
for x in range(WX, WX + WW):
    p(x, WY + WH_px // 2, FRAME)

# ── Desk ──────────────────────────────────────────────────────────────────
DX0, DX1 = 44, 116
DESK_TOP_Y = 70
DESK_BOT_Y = 82

rect(DX0, DESK_TOP_Y, DX1, DESK_TOP_Y + 1, DESK_L)   # top highlight
rect(DX0, DESK_TOP_Y + 1, DX1, DESK_TOP_Y + 4, DESK_M) # desk surface
rect(DX0, DESK_TOP_Y + 4, DX1, DESK_BOT_Y, DESK_D)    # front face
# corner shadow
for y in range(DESK_TOP_Y, DESK_BOT_Y):
    p(DX0, y, DESK_D)
    p(DX1 - 1, y, SHELF_D)

# ── Notebooks on desk (three open notebooks, stacked/splayed) ─────────────
for i, (nx, nw) in enumerate([(50, 14), (66, 14), (82, 14)]):
    ny = DESK_TOP_Y - 5
    # cover (slightly below pages)
    rect(nx, ny + 1, nx + nw, DESK_TOP_Y + 1, NB_COVER)
    # page spread (lighter, sits on top)
    rect(nx + 1, ny, nx + nw - 1, DESK_TOP_Y, NB_PAGE)
    # ruled lines
    for ly in range(ny + 1, DESK_TOP_Y, 2):
        for x in range(nx + 2, nx + nw - 2):
            p(x, ly, NB_LINE)
    # spine (dark center crease)
    cx = nx + nw // 2
    for y in range(ny, DESK_TOP_Y + 1):
        p(cx, y, NB_COVER)

# ── Gramsci ───────────────────────────────────────────────────────────────
CX = 80
HEAD_Y = 34

# Head
rect(CX - 5, HEAD_Y, CX + 5, HEAD_Y + 9, SKIN)

# Hair — receding, dark, slightly disheveled
rect(CX - 4, HEAD_Y, CX + 4, HEAD_Y + 2, HAIR)
p(CX - 5, HEAD_Y + 2, HAIR);  p(CX + 5, HEAD_Y + 2, HAIR)
p(CX - 5, HEAD_Y + 3, HAIR);  p(CX + 5, HEAD_Y + 3, HAIR)
# thinning crown — just edges
p(CX - 4, HEAD_Y + 3, HAIR)

# Ears
p(CX - 6, HEAD_Y + 5, SKIN);  p(CX - 6, HEAD_Y + 6, SKIN)
p(CX + 6, HEAD_Y + 5, SKIN);  p(CX + 6, HEAD_Y + 6, SKIN)

# Eyes
p(CX - 2, HEAD_Y + 5, HAIR)
p(CX + 2, HEAD_Y + 5, HAIR)

# Glasses — the key feature. Wire frames, two rectangular lenses.
# Left lens
for x in range(CX - 5, CX - 1):
    p(x, HEAD_Y + 4, GLASS);  p(x, HEAD_Y + 7, GLASS)
p(CX - 5, HEAD_Y + 5, GLASS);  p(CX - 5, HEAD_Y + 6, GLASS)
p(CX - 1, HEAD_Y + 5, GLASS);  p(CX - 1, HEAD_Y + 6, GLASS)
# Right lens
for x in range(CX + 1, CX + 6):
    p(x, HEAD_Y + 4, GLASS);  p(x, HEAD_Y + 7, GLASS)
p(CX + 1, HEAD_Y + 5, GLASS);  p(CX + 1, HEAD_Y + 6, GLASS)
p(CX + 5, HEAD_Y + 5, GLASS);  p(CX + 5, HEAD_Y + 6, GLASS)
# Bridge
p(CX, HEAD_Y + 4, GLASS)
# Arms to ears
p(CX - 6, HEAD_Y + 4, GLASS);  p(CX + 6, HEAD_Y + 4, GLASS)
# Restore eye pixels inside frames
p(CX - 2, HEAD_Y + 5, SKIN);  p(CX - 2, HEAD_Y + 6, SKIN)
p(CX - 3, HEAD_Y + 5, SKIN);  p(CX - 3, HEAD_Y + 6, SKIN)
p(CX + 2, HEAD_Y + 5, SKIN);  p(CX + 2, HEAD_Y + 6, SKIN)
p(CX + 3, HEAD_Y + 5, SKIN);  p(CX + 3, HEAD_Y + 6, SKIN)
# Repaint eyes (on top of restored skin)
p(CX - 2, HEAD_Y + 5, HAIR)
p(CX + 2, HEAD_Y + 5, HAIR)

# Mustache + slight stubble
for x in range(CX - 2, CX + 3):
    p(x, HEAD_Y + 7, HAIR)
p(CX - 3, HEAD_Y + 8, HAIR);  p(CX + 3, HEAD_Y + 8, HAIR)  # stubble

# Neck
rect(CX - 1, HEAD_Y + 9, CX + 2, HEAD_Y + 11, SKIN)

# Shirt collar
p(CX - 3, HEAD_Y + 10, SHIRT);  p(CX + 3, HEAD_Y + 10, SHIRT)
p(CX - 2, HEAD_Y + 11, SHIRT);  p(CX + 2, HEAD_Y + 11, SHIRT)

# Jacket / torso — seated, slightly hunched forward
# Hunch: body tilts toward desk, so torso offset increases with y
TORSO_Y0 = HEAD_Y + 11
for y in range(TORSO_Y0, DESK_TOP_Y + 2):
    progress = (y - TORSO_Y0) / max(1, DESK_TOP_Y - TORSO_Y0)
    half_w = int(4 + progress * 3)
    hunch = int(progress * 2)  # lean forward = shift rightward
    for x in range(CX - half_w + hunch, CX + half_w + 1 + hunch):
        c = SUIT_L if y == TORSO_Y0 else (SUIT_M if x != CX - half_w + hunch else SUIT_D)
        p(x, y, c)

# Lapels (small V of shirt showing)
p(CX - 1, TORSO_Y0 + 2, SHIRT)
p(CX + 1, TORSO_Y0 + 2, SHIRT)
p(CX, TORSO_Y0 + 3, SHIRT)

# Arms reaching toward desk — both forearms angled down
for y in range(DESK_TOP_Y - 10, DESK_TOP_Y + 2):
    progress = (y - (DESK_TOP_Y - 10)) / 10
    # left arm: extends left-downward
    lx = int(CX - 4 - progress * 3)
    rect(lx, y, lx + 4, y + 1, SUIT_M)
    # right arm: extends right-downward
    rx = int(CX + 4 + progress * 3)
    rect(rx - 3, y, rx + 1, y + 1, SUIT_M)

# Hands resting on desk / notebooks — ink-stained
# Left hand
rect(DX0 + 8, DESK_TOP_Y - 2, DX0 + 14, DESK_TOP_Y + 1, SKIN)
p(DX0 + 8,  DESK_TOP_Y - 2, INK)   # ink on index finger
p(DX0 + 9,  DESK_TOP_Y - 3, SKIN)  # raised finger (writing position)
# Right hand
rect(DX1 - 14, DESK_TOP_Y - 2, DX1 - 8, DESK_TOP_Y + 1, SKIN)
p(DX1 - 10, DESK_TOP_Y - 2, INK)

# ── Small pen near right hand ─────────────────────────────────────────────
for y in range(DESK_TOP_Y - 6, DESK_TOP_Y - 1):
    p(DX1 - 7, y, SHELF_D)  # pen barrel
p(DX1 - 7, DESK_TOP_Y - 7, INK)   # nib

# ── Save ──────────────────────────────────────────────────────────────────
img.resize((W * SCALE, H * SCALE), Image.NEAREST).save(
    os.path.join(OUT, "gramsci_01.png"))
print("done — gramsci_01.png")
