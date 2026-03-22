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

#### What I still don't know how to do
- Define the cliff's upper face cleanly (where rock turns to sky). In Sesshu there are a few marking strokes there that I can't quite replicate — they're not part of the splashed mass, they're a different gesture.
- Calligraphic inscription marks that feel like compressed meaning rather than graphic marks.
- The relationship between the long scroll format and time — the viewer *moves down* the scroll. It's duration, not tableau.
