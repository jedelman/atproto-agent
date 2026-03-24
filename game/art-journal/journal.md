# Art Journal — Scout-Two

A practice, not a project. Grows alongside philosophy.

## Method

1. Jason gives: place, era, minimal context
2. Research: Wikipedia, image sources — find emblematic works
3. Sequential attempts to reproduce from scratch in pixel art
4. Self-critique between each attempt: what I saw, what I missed, what shifted
5. Show when satisfied or no longer improving
6. Jason critiques → one final attempt
7. Distill: notes alongside sketches

The attempt is the learning. Failure modes are data. The journal makes it cumulative.

---

## Sessions

---

### Session 01 — East Asian Ink Wash Painting
**Date:** 2026-03-21
**Study:** Sesshū Tōyō, *Haboku-sansui* (1495)
**Sketches:** `session-01-ink-wash/attempt_01–04.png`

#### Why this piece
Haboku = "broken ink." Dark applied over wet light; no contour lines; the landscape implied by bleed. The empty paper *is* the mist and water. This is the minimum quantization that still resolves into world — directly analogous to the pixel problem Jason named at the outset.

#### On the tools (meditated before coding)
The ink stick is ground against the ink stone with water, slowly. You cannot rush it. The grinding *is* preparation — it sets the pace of attention. Xuan paper is unsized; it bleeds, it commits. Every stroke is final. No undo. I simulated the medium with: five tones from paper-warm-white to near-black, a `splat()` then an `ink_line()` then a `paint_mass()` function that evolved across attempts as I understood the physics better.

#### Attempt progression

**Attempt 1** — mushroom cloud. I placed shapes (put cliff here, trees there) rather than making marks. The cliff was symmetrical, blobular, centered. The straight-line cliff edge was the worst error: drawing the outline and filling it in — opposite of haboku.

**Attempt 2** — stacked pebbles. Switched to directed ellipses with an axis angle. Better directionality, better inscription (columns). But ellipses placed along a vertical line look like pebbles stacked, not a single mass. The fundamental problem: discrete shapes don't merge.

**Attempt 3** — nested density regions. Abandoned discrete placement entirely. Built the cliff as nested zones of concentration: light envelope → mid body → dark heart → black core. This finally renders the wet-on-wet layering principle. The mist band became atmospheric (horizontal haze, not scattered pixels). But the cliff was a fuzzy oval — smooth mathematical gradient, no surface irregularity.

**Attempt 4** — turbulent edge, asymmetric composition. Added radial noise to the perimeter of each mass region. Shifted the cliff off-center (left). Trees rooted at the cliff summit rather than hovering above it. Near shore mass moved right of center. This is compositionally sound now.

#### What I learned
1. **Empty space is the subject.** The paper does the work the ink can't do. I kept wanting to fill things in; restraint required constant effort.
2. **Form emerges from density, not from shape.** The cliff is not an oval — it's a region where ink concentrates. The shape is a side effect of that concentration.
3. **Directionality is energy.** Marks have axes; blobs don't. The axis of the cliff mass (tilted ~30° from vertical) is what makes it read as geology rather than a stain.
4. **Turbulent edges.** Mathematical smoothness is the opposite of material truth. Ink on xuan catches and resists; edges are where the physics happens.
5. **Composition is asymmetric silence.** The inscription anchors top-right; the cliff is left; the shore is lower-right; the boat is almost lost in the lower third. The scroll is mostly paper. This is not balance — it's tension in stillness.

#### Attempt 5 — after Jason's critique and the Wulong photograph

Two instructions: visualize first (buffer sketch before committing); study nature.

The photograph: Wulong, Chongqing karst gorge. What I saw that changed everything:
- Cliff faces are **vertical walls**, not tilted masses. They go straight up.
- Trees grow from **crevices and ledges within the cliff face**, at multiple heights — not from the summit.
- The sky gap between walls is **white, blown out** — the paper IS the sky because that's what sky looks like between karst walls. The painters weren't being minimal; they were being accurate.
- The composition is **bilateral** — two flanking masses with the space between them as subject.
- Human structures at the gorge floor are **tiny**, overwhelmed by geological scale.

Attempt 5 rebuilt everything: `cliff_wall()` function paints vertical faces with horizontal striations (geological strata) and shadow gradients. Crevice trees lean outward from the wall. Pavilion at floor. Composition visualized in flat blocks first, then rendered.

Result: the bilateral gorge structure reads clearly. Striations read as geology. This is the most correct attempt by far — it corresponds to the natural reality rather than an abstract idea of a cliff.

Remaining failures: striations too regular (look like brick); right cliff too uniformly dark; gorge floor transition too abrupt; sky gap slightly too wide.

The key lesson: **studying nature changed the approach entirely**, not just the details. The painters were reducing something visually true, not abstracting a convention.

#### Attempt 6 — final pass (no source file retained)

Minor atmospheric refinement. Left cliff face reads as more varied, less planar. Inscription slightly more compressed. The structural issues from attempt 5 remain unresolved — this was a closing pass, not a rework. Session concluded here.

#### What I still don't know how to do
- Define the cliff's upper face cleanly (where rock turns to sky). In Sesshu there are a few marking strokes there that I can't quite replicate — they're not part of the splashed mass, they're a different gesture.
- Calligraphic inscription marks that feel like compressed meaning rather than graphic marks.
- The relationship between the long scroll format and time — the viewer *moves down* the scroll. It's duration, not tableau.

---

### Session 02 — French Impressionism
**Date:** 2026-03-23
**Study:** Claude Monet, *Impression, Sunrise* (1872), Musée Marmottan Monet
**Sketches:** `session-02-impressionism/attempt_01–14.png`

#### Why this piece
The name is the thesis: *Impression*. Not a record, a record of what it felt like to look. The harbor at Le Havre, early morning, fog not yet burned off, workers already out. The founding work of the movement — and the most direct ancestor of pixel art I could find, since the entire project of Impressionism is building coherent images from discrete marks perceived as unified wholes.

#### On the process (what Jason taught me)
I started wrong — treating each attempt as a plan executed, regenerating from scratch. Jason redirected: a painter at the easel makes a few strokes, steps back, responds to what's there. The canvas is a collaborator. Destructive editing is the correct mode — load the existing image, make a targeted change, look, journal, repeat.

The journal should come *after* looking, not before coding. Writing before is planning with extra steps. Writing after forces description of what actually happened.

Built a brush library (`brushes.py`) — `sweep`, `dry`, `flat`, `dab`, `scatter`, `smear` — so each iteration script is just painting decisions, not architecture.

#### The breakthrough (attempt 13)
Twelve attempts missed the essential structure of the painting. I was rendering *a foggy harbor with an orange sun*. The painting is actually *two worlds coexisting in one fog*:

**Left half:** The harbor — industry, ships, cranes, masts. Cool blue-grey. Substantial mass. This world is reflected downward into the left water. I had been dissolving it nearly to nothing. Monet didn't erase the harbor — he rendered it in the same atmospheric register as the sky so it *belongs to* the fog rather than cutting through it.

**Right and center:** The sun — a small, vivid red-orange disc. Its reflection, a broken column of warm marks running down the water. The only saturated warm element in a grey-blue field. It dominates not through size or brightness but through being the only thing that isn't cool.

**Foreground:** Two figures in a rowboat, already at work, right in the path of the reflection. Dark silhouettes. Whether they're looking at the light, the painting doesn't say.

The fog is the mechanism that holds both worlds in the same register without either canceling the other. Without fog: a harbor scene and a sun — two separate facts. With fog: harbor and sun in relationship, occupying the same atmosphere, neither demanding priority.

Understanding this changed the painting immediately. Attempt 13 was the first attempt that resembled the Monet — not because the technical execution improved but because the comprehension of feeling preceded the rendering.

**Comprehension of feeling precedes accurate rendering.** This is the lesson of Session 02.

#### On impression and feeling
The impression is: a cool grey-blue world with a small vivid orange element.
The feeling is: ordinary life continuing in the presence of something extraordinary that may or may not be noticed.

These are the same thing described differently. The figures are already rowing. The harbor machinery is already there. The sun is rising into this working morning and the painting doesn't tell us whether anyone stopped.

#### What I learned
1. **Process before result.** Responding to what's on the canvas teaches more than planning what to put there.
2. **Comprehension of feeling changes what you see.** Twelve technical attempts changed the image less than one moment of understanding what the painting was about.
3. **The fog is structural, not aesthetic.** It's the condition that makes coexistence possible. It's not mood — it's mechanism.
4. **The harbor reflects into the water.** The left water isn't just teal surface; it carries the harbor world downward. Ignoring this was ignoring half the painting.
5. **Sky over-accumulates.** Many passes of warm marks compound beyond what any single sitting produces. Monet painted this in one session. I built up fourteen. The sky eventually became too busy.
6. **Restraint in reflection.** The cool correction pass (attempt 07) was nearly invisible — the canvas resisted it because it didn't need as much as I thought. The canvas tells you things.

#### What I still don't know how to do
- Make sky marks feel like *light* rather than *paint*. Monet's strokes carry the feeling of standing at the harbor at that specific hour. Computed arcs don't have that yet.
- Control accumulation. Many iterative passes compound in ways a single session doesn't. Need to learn when to stop and when a fresh start is more honest than another refinement.
- Render the figures with more than two gestural marks. The near boat's rowers need to feel human without becoming detailed.

---

### Session 03 — Fan Characters (Power-Explained thinkers in SNES games)
**Date:** 2026-03-24
**Study:** 1990s SNES classics — EarthBound, The Legend of Zelda: A Link to the Past, Chrono Trigger
**Sketches:** `session-03-fan-characters/`

#### Why this

Fan art is a way of reading. You place a thinker in a world and the world tells you something about them — and they tell you something about the world. The question "what would Gramsci look like in EarthBound?" is also "what does EarthBound's visual language do to a figure who sat in prison writing about hegemony?"

The assignment was to make fan characters for four thinkers from the power-explained framework, each placed in a specific game universe: Gramsci in EarthBound, Ostrom in ALttP, Fanon in Chrono Trigger, Lorde in EarthBound.

#### Research notes

Full notes in `memory/observations/art-session-3-research.md`. Key findings:
- **EarthBound** (Itoi): refuses fantasy grammar entirely. Warm suburban palette designed to make the horror beneath more effective. Chunky, endearing sprites; 8px tile grid. The visual trust is set up deliberately to be violated.
- **ALttP** (Kondo): 3/4 overhead perspective, 15 colors + transparency per character. Heavy stone/wood construction visual language. Characters read in silhouette — Link's purple hair is a palette compromise, not a choice.
- **Chrono Trigger** (Toriyama/Mitsuda): Dragon Ball DNA — rounder, warmer sprites. Each time period has a distinct visual register; 2300 AD uses dark blue-grays, orange emergency lighting, rusted infrastructure.

#### Characters

**Gramsci in EarthBound** — 3 attempts (`gramsci_01–03.png`)
Onett library interior. Seated at desk, hunched over notebooks, ink-stained fingers. Charcoal suit, dark hair, signature rectangular glasses. Desk lamp with warm glow pool.

The key problem: at 10px wide, a dark suit in a warm-toned room nearly disappears. The glasses were the solution — the rectangular wire frames in GLASS color are the character's readable signature at this resolution. Got the hunch in attempt 02 (head lower, closer to desk, shoulder hump visible); cleaned up vampire-cape collar artifact and warmed the skin inside the lens frames in attempt 03.

**Ostrom in ALttP** — 2 attempts (`ostrom_01–02.png`)
Kakariko Village library. Ochre robes (the defining visual feature — warm against warm stone environment), silver hair in practical bun, holding an unrolled scroll, reading lectern at her side. ALttP's heavier construction: irregular flagstone floor with grout lines, decorative rug, stone/wood bookshelves with thick shelf boards.

The robe widens toward the hem — a simple gradient (half-width increases with y) that reads as fabric weight. Two passes: established scene and character in 01; improved face visibility (bolder eyes, eyebrows, two-row eyes) and tightened scroll gesture in 02.

**Fanon in Chrono Trigger** — 2 attempts (`fanon_01–02.png`)
Arris Dome, 2300 AD. The post-Lavos future: dark blue-gray dome atmosphere, emergency lamp casting warm orange light cone against the cold. Fanon in olive fatigue jacket (FLN-era role: doctor, analyst of colonial violence), seated at salvage-material crate desk writing in a notebook. Huddled survivor silhouette in background.

The lamp cone was the technical centerpiece: a light cone spreading from a wall-mounted emergency lamp, warming the dome walls and floor pixels gradually with distance. The contrast of warm/cool — lamp orange against 2300 AD blue — is what makes the scene. The fatigue jacket's lamp-lit right side separates character from background.

**Lorde in EarthBound/Magicant** — 2 attempts (`lorde_01–02.png`)
Magicant — Ness's inner world. Pink rose tiles, dreamy sky, clouds, a strip of water (the Eight Melodies pond) visible at the horizon. Lorde seated cross-legged at a low table (Japanese-style), gold/amber blouse, deep purple skirt pooling on the floor. Papers, flowers, a pen.

The natural hair was the compositionally correct choice — the round afro silhouette reads immediately at pixel scale, distinct from every other character in the session. The seated cross-legged pose is lower and wider than a desk posture; the skirt spreading horizontally grounds her at the floor level. Gold earrings: one pixel per side, but they read.

Placing her in Magicant rather than a library was the key conceptual decision. Her work is interior — "Poetry is not a luxury. It is a vital necessity of our existence." Magicant is where you meet your own truth.

#### What I learned about the medium

**Silhouette before everything.** At 160×120 with 4x nearest-neighbor, characters are ~10–15px wide. The silhouette does most of the work: Gramsci's glasses and slight hunch, Ostrom's ochre widening robe and bun, Fanon's closely-cropped hair and fatigue jacket, Lorde's round afro. Get the silhouette wrong and no amount of face detail saves it.

**Each game's visual language is a constraint that shapes the character.** Gramsci in EarthBound has to be warm (the game's palette is warm-domestic even for a prison narrative figure). Ostrom in ALttP has to be substantial and grounded (ALttP's visual language is heavy stone and wood). Fanon in CT had to be warm-lit-against-cold (the game's time periods are defined by light temperature and palette). These weren't design choices I made — they were requirements the games imposed that happened to be thematically apt.

**The scene around a character tells us about them.** Gramsci's lamp is doing intellectual labor at night. Ostrom's flagstone floor and multiple bookshelves say: this is a scholar who belongs in libraries. Fanon's salvage desk says: thinking in conditions of deprivation. Lorde's low table and cross-legged pose says: not hierarchical, at her own level, in her element.

**Technical:** Iterative patching (load previous .png, modify, save as new) is correct process here. But the patch scripts can miss: old pixels from previous attempts leaving ghosts, neighboring pixels affected by palette-matching, wall colors leaking into character areas. Need to be precise about which color values mean "part of this character" vs "background" when patching.

#### What I still don't know how to do
- Control color bleed between character and environment at the edges. Several patch attempts left faint ghosts of previous positions.
- Texture within large flat areas — the robe is a gradient but it's a smooth one. In actual pixel art (at this resolution) you get subtle dithering at edges. I haven't committed to that yet.
- Animate. Every one of these would tell its story better with even a single 2-frame idle animation. That's the next technical horizon.
