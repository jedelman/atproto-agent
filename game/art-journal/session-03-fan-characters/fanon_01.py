#!/usr/bin/env python3
"""
Session 03 — Fan Characters
Frantz Fanon in Chrono Trigger, Attempt 01

Setting: Arris Dome, 2300 AD. The last surviving humans, living in underground
shelter domes. Emergency lighting, rusted infrastructure, desperate hope.

Fanon is seated at salvage materials (wooden crate desk), writing in a notebook
by the light of an emergency lamp. He's in his FLN-era role: doctor and analyst
of colonial violence, building theory from the wreckage.

CT visual language:
- Toriyama's Dragon Ball DNA: rounder heads, warmer character style
- Sprites ~32×48px region, larger than FFVI, facial expressions readable in combat
- 2300 AD palette: dark blue-grays, orange emergency lighting, orange-rust metal
- Strong contrast: warm light source against cold dark environment
- Characters read round and chunky against angular/mechanical backgrounds

Canvas: 160×120 at 4x scale (640×480)
"""
from PIL import Image
import os

W, H = 160, 120
SCALE = 4
OUT = os.path.dirname(os.path.abspath(__file__))

img = Image.new('RGB', (W, H))
px = img.load()

# ── Palette: 2300 AD Arris Dome ───────────────────────────────────────────
DOME_DARK  = (28, 36, 52)    # dark dome wall / background
DOME_MID   = (44, 56, 72)    # dome wall mid
DOME_LIGHT = (60, 76, 96)    # dome wall lit by lamp
DOME_RUST  = (80, 52, 28)    # corroded metal panels
RUST_L     = (108, 72, 36)   # rust highlight
RUST_D     = (56, 32, 12)    # rust deep shadow
STEEL_L    = (80, 96, 112)   # steel floor light
STEEL_D    = (52, 64, 76)    # steel floor dark
CONDUIT_G  = (60, 88, 64)    # corroded green conduit/pipe
CONDUIT_D  = (36, 56, 40)    # pipe shadow
LAMP_CASE  = (96, 80, 48)    # emergency lamp housing
LAMP_GLOW  = (255, 200, 80)  # inner glow
LAMP_WARM  = (240, 160, 48)  # lamp housing illuminated
LIGHT_CAST = (88, 72, 40)    # floor lit by emergency lamp (warm on dark)
LIGHT_FADE = (52, 52, 48)    # light fading at edges
WIRE       = (40, 40, 44)    # wire/cable
BOLT       = (100, 92, 72)   # bolt/rivet

# Fanon character palette
SKIN       = (168, 112, 72)  # warm dark brown skin
SKIN_D     = (128, 84, 52)   # skin shadow
SKIN_H     = (196, 136, 88)  # skin highlight (light-lit side)
FATIGUE_L  = (88, 100, 64)   # olive fatigue jacket light
FATIGUE_M  = (64, 76, 48)    # fatigue jacket mid
FATIGUE_D  = (44, 56, 32)    # fatigue shadow (almost merges with bg)
FATIGUE_DK = (32, 40, 24)    # fatigue deepest shadow
HAIR       = (24, 20, 16)    # dark hair
HAIR_H     = (48, 40, 28)    # hair highlight (lamp-lit)
TROUSER    = (36, 44, 52)    # dark trousers (nearly dome color)
TROUSER_L  = (52, 64, 72)    # trouser highlight
NB_COVER   = (96, 64, 32)    # notebook cover (worn leather)
NB_PAGE    = (232, 220, 192) # notebook page
NB_LINE    = (200, 188, 160) # faint ruled lines
INK        = (24, 24, 36)    # ink
STETH      = (120, 108, 80)  # stethoscope (brass/worn)
STETH_T    = (100, 88, 60)   # stethoscope tubing
CRATE_L    = (96, 72, 40)    # salvage crate light
CRATE_M    = (72, 52, 28)    # crate mid
CRATE_D    = (48, 32, 12)    # crate dark

def p(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        px[x, y] = c

def rect(x0, y0, x1, y1, c):
    for y in range(y0, y1):
        for x in range(x0, x1):
            p(x, y, c)

FLOOR_Y = H - 30

# ── Background: dome interior ─────────────────────────────────────────────
for y in range(H):
    for x in range(W):
        # Base dome atmosphere — slight gradient darker at top/edges
        dist_from_center = abs(x - W // 2)
        if y < FLOOR_Y:
            if dist_from_center > 60 or y < 20:
                p(x, y, DOME_DARK)
            elif y < 40:
                p(x, y, DOME_MID)
            else:
                p(x, y, DOME_MID)
        else:
            # Steel floor
            p(x, y, STEEL_L if ((x // 8) + (y // 6)) % 2 == 0 else STEEL_D)

# Corroded metal panel sections (left wall)
for y in range(8, 60):
    for x in range(0, 24):
        if (y // 14) % 2 == 0:
            p(x, y, DOME_RUST)
        else:
            p(x, y, RUST_D)
    # Rivet line
    for y_r in range(8, 60, 14):
        for x in range(2, 22, 5):
            p(x, y_r, BOLT)

# Conduit / pipe running along left wall
for y in range(0, FLOOR_Y):
    p(24, y, CONDUIT_G)
    p(25, y, CONDUIT_D)
# Pipe junction
rect(20, 40, 30, 44, CONDUIT_G)
p(20, 41, CONDUIT_D); p(29, 41, CONDUIT_D)

# Right wall — back panel, wiring
for y in range(0, 50):
    for x in range(W - 20, W):
        p(x, y, DOME_DARK if y % 10 < 7 else DOME_MID)
for y in range(0, 50, 10):
    for x in range(W - 19, W):
        p(x, y, RUST_D)

# Wire running along right wall
for y in range(0, FLOOR_Y):
    p(W - 21, y, WIRE)

# ── Emergency lamp (right of scene, mounted on wall) ──────────────────────
LX = 128   # lamp x position
LY = 28    # lamp top y

# Bracket/mount
rect(LX - 2, LY, LX + 8, LY + 2, RUST_L)
# Lamp housing
rect(LX - 1, LY + 2, LX + 8, LY + 10, LAMP_CASE)
rect(LX,     LY + 3, LX + 7, LY + 9,  LAMP_WARM)
rect(LX + 1, LY + 4, LX + 6, LY + 8,  LAMP_GLOW)

# Light cone: warm cast spreading down-left from lamp
for y in range(LY + 10, FLOOR_Y):
    spread = (y - (LY + 10)) // 2
    x_right = min(LX + 8 + spread // 2, W - 1)
    x_left  = max(LX - 6 - spread, 30)
    for x in range(x_left, x_right + 1):
        dist = abs(x - (LX + 3)) + (y - (LY + 10)) // 3
        if dist < 18:
            # Warm the wall/floor pixels
            r, g, b = px[x, y]
            warmth = max(0, 18 - dist)
            p(x, y, (min(255, r + warmth * 4),
                     min(255, g + warmth * 2),
                     max(0,   b - warmth)))

# ── Fanon's salvage desk (stacked crates + plank) ─────────────────────────
DESK_TOP_Y = FLOOR_Y - 22

# Right crate (larger)
rect(88, DESK_TOP_Y + 6, 116, FLOOR_Y, CRATE_M)
rect(88, DESK_TOP_Y + 6, 116, DESK_TOP_Y + 8, CRATE_L)   # top edge
for y in range(DESK_TOP_Y + 8, FLOOR_Y, 1):
    p(88, y, CRATE_D); p(115, y, CRATE_L)
# Plank across crates
rect(60, DESK_TOP_Y, 116, DESK_TOP_Y + 6, CRATE_M)
rect(60, DESK_TOP_Y, 116, DESK_TOP_Y + 2, CRATE_L)

# Left support crate
rect(60, DESK_TOP_Y + 6, 80, FLOOR_Y, CRATE_D)
rect(60, DESK_TOP_Y + 6, 80, DESK_TOP_Y + 8, CRATE_M)

# Crate bands/slats
for y in [DESK_TOP_Y + 10, DESK_TOP_Y + 18]:
    rect(88, y, 116, y + 2, RUST_D)
    rect(60, y, 80, y + 2, RUST_D)

# ── Notebook on desk ──────────────────────────────────────────────────────
NB_X = 74
NB_Y = DESK_TOP_Y - 5
rect(NB_X, NB_Y + 1, NB_X + 18, DESK_TOP_Y + 2, NB_COVER)
rect(NB_X + 1, NB_Y, NB_X + 17, DESK_TOP_Y + 1, NB_PAGE)
# Ruled lines
for ly in range(NB_Y + 1, DESK_TOP_Y + 1, 2):
    for x in range(NB_X + 2, NB_X + 16):
        p(x, ly, NB_LINE)
# Center spine
for y in range(NB_Y, DESK_TOP_Y + 2):
    p(NB_X + 9, y, NB_COVER)
# Some writing on right page
for ly in range(NB_Y + 2, DESK_TOP_Y + 1, 2):
    for x in range(NB_X + 10, NB_X + 16, 2):
        p(x, ly, INK)

# ── Frantz Fanon ──────────────────────────────────────────────────────────
# Seated, bent slightly forward over the notebook
# CT style: rounder head, warm chunky feel
CX = 80
HEAD_Y = DESK_TOP_Y - 30   # seated, close to desk

# Head (CT heads are wider, rounder)
rect(CX - 6, HEAD_Y, CX + 6, HEAD_Y + 12, SKIN)
# Round the corners (CT's more organic shapes)
p(CX - 6, HEAD_Y,      DOME_MID)
p(CX + 5, HEAD_Y,      DOME_MID)
p(CX - 6, HEAD_Y + 11, DOME_MID)
p(CX + 5, HEAD_Y + 11, DOME_MID)
# Highlight from lamp (left side catches warm light)
for y in range(HEAD_Y + 1, HEAD_Y + 10):
    p(CX + 4, y, SKIN_H)
    p(CX + 5, y, SKIN_H)
# Shadow right side
for y in range(HEAD_Y + 1, HEAD_Y + 10):
    p(CX - 5, y, SKIN_D)
    p(CX - 6, y, SKIN_D)

# Hair — short, close-cropped (Fanon's appearance in 1950s photos)
rect(CX - 5, HEAD_Y, CX + 5, HEAD_Y + 3, HAIR)
# Lamp highlight on hair
p(CX + 3, HEAD_Y,     HAIR_H)
p(CX + 4, HEAD_Y,     HAIR_H)
p(CX + 4, HEAD_Y + 1, HAIR_H)

# Ears
p(CX - 7, HEAD_Y + 4, SKIN)
p(CX - 7, HEAD_Y + 5, SKIN)
p(CX + 6, HEAD_Y + 4, SKIN_H)
p(CX + 6, HEAD_Y + 5, SKIN_H)

# Eyes — looking down at notebook (downcast, focused)
# CT eyes have more expression than EarthBound's dots
# Left eye (in shadow)
p(CX - 3, HEAD_Y + 5, HAIR)
p(CX - 2, HEAD_Y + 5, HAIR)
# Right eye (lit)
p(CX + 1, HEAD_Y + 5, HAIR)
p(CX + 2, HEAD_Y + 5, HAIR)
# Eye whites (lit side)
p(CX + 3, HEAD_Y + 5, (220, 200, 168))  # slightly warm white
# Slight furrowed brow — concentration
p(CX - 2, HEAD_Y + 4, SKIN_D)
p(CX + 1, HEAD_Y + 4, SKIN_D)

# Nose
p(CX - 1, HEAD_Y + 7, SKIN_D)
p(CX,     HEAD_Y + 7, SKIN_D)

# Mouth — set, focused, slight tension
p(CX - 2, HEAD_Y + 9, SKIN_D)
p(CX - 1, HEAD_Y + 9, (120, 80, 56))   # lips
p(CX,     HEAD_Y + 9, (120, 80, 56))
p(CX + 1, HEAD_Y + 9, SKIN_D)

# Neck
rect(CX - 1, HEAD_Y + 12, CX + 2, HEAD_Y + 14, SKIN)

# ── Fatigue jacket ────────────────────────────────────────────────────────
# Slightly forward lean (seated over desk)
TORSO_Y = HEAD_Y + 13

# Collar / shirt beneath (lighter hint of undershirt)
p(CX - 1, TORSO_Y, (180, 160, 120))
p(CX + 1, TORSO_Y, (180, 160, 120))
p(CX,     TORSO_Y + 1, (160, 140, 100))  # V

# Torso — jacket widens slightly, leans forward
for y in range(TORSO_Y + 1, DESK_TOP_Y + 3):
    progress = (y - TORSO_Y) / max(1, DESK_TOP_Y - TORSO_Y)
    half = int(6 + progress * 3)
    lean = int(progress * 2)  # slight forward lean
    for x in range(CX - half + lean, CX + half + lean + 1):
        if x == CX - half + lean:
            c = FATIGUE_DK
        elif x < CX:
            c = FATIGUE_D
        elif x > CX + half + lean - 2:
            c = FATIGUE_L   # lamp-lit right side
        else:
            c = FATIGUE_M
        p(x, y, c)

# Pocket detail (left breast pocket, signature of fatigue jacket)
POCKET_Y = TORSO_Y + 6
p(CX - 3, POCKET_Y,     FATIGUE_D)
p(CX - 2, POCKET_Y,     FATIGUE_D)
p(CX - 1, POCKET_Y,     FATIGUE_D)
p(CX - 3, POCKET_Y + 1, FATIGUE_D)
p(CX - 1, POCKET_Y + 1, FATIGUE_D)
p(CX - 3, POCKET_Y + 2, FATIGUE_D)
p(CX - 2, POCKET_Y + 2, FATIGUE_D)
p(CX - 1, POCKET_Y + 2, FATIGUE_D)
# Pen in pocket
p(CX - 2, POCKET_Y + 1, INK)

# ── Left arm — reaching toward notebook ───────────────────────────────────
ARM_L_Y = TORSO_Y + 4
for y in range(ARM_L_Y, DESK_TOP_Y + 1):
    progress = (y - ARM_L_Y) / max(1, DESK_TOP_Y - ARM_L_Y)
    lx = CX - 7 - int(progress * 4)   # extends left toward notebook
    p(lx,     y, FATIGUE_M)
    p(lx + 1, y, FATIGUE_M)
    p(lx + 2, y, FATIGUE_M)
    p(lx - 1, y, FATIGUE_DK)  # outer edge shadow

# Left hand — writing
rect(CX - 13, DESK_TOP_Y - 2, CX - 8, DESK_TOP_Y + 1, SKIN)
p(CX - 13, DESK_TOP_Y - 3, SKIN)  # extended writing finger
p(CX - 13, DESK_TOP_Y - 3, INK)   # ink on fingertip (he's writing)

# ── Right arm — resting on desk edge, holding notebook open ──────────────
ARM_R_Y = TORSO_Y + 6
for y in range(ARM_R_Y, DESK_TOP_Y + 1):
    progress = (y - ARM_R_Y) / max(1, DESK_TOP_Y - ARM_R_Y)
    rx = CX + 8 + int(progress * 2)
    p(rx,     y, FATIGUE_L)   # lamp-lit right arm
    p(rx + 1, y, FATIGUE_L)
    p(rx + 2, y, FATIGUE_M)

# Right hand on notebook edge
rect(CX + 10, DESK_TOP_Y - 1, CX + 16, DESK_TOP_Y + 1, SKIN_H)

# ── Stethoscope (hanging from neck / draped over shoulder) ────────────────
# Just a suggestion: tubing drapes down from neck-right, coils near desk
ST_X = CX + 3
ST_Y = TORSO_Y + 2
# Ear piece hanging out of pocket area
for i in range(5):
    p(ST_X + i, ST_Y + i, STETH_T)
p(ST_X + 5, ST_Y + 5, STETH)  # earpiece tip

# ── Floor shadow under Fanon ───────────────────────────────────────────────
for x in range(CX - 10, CX + 14):
    r, g, b = px[x, FLOOR_Y]
    p(x, FLOOR_Y, (int(r * 0.80), int(g * 0.80), int(b * 0.80)))

# ── Distant silhouettes (other survivors in background) ────────────────────
# Two simple huddled shapes against the back wall — implies community
SILO = DOME_DARK
# Left silhouette
for y in range(FLOOR_Y - 16, FLOOR_Y):
    half = 4 - (y - (FLOOR_Y - 16)) // 5
    for x in range(32, 32 + half * 2):
        p(x, y, DOME_RUST)
p(36, FLOOR_Y - 17, DOME_RUST)  # head

# ── Save ──────────────────────────────────────────────────────────────────
img.resize((W * SCALE, H * SCALE), Image.NEAREST).save(
    os.path.join(OUT, "fanon_01.png"))
print("done — fanon_01.png")
