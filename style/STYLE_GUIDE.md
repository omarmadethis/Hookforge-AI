# Hookforge style guide: CapCut text, edit and audio forensics (2026-10-18 PT)
Source: all 110 team CapCut drafts (CapCut 9.4.1). That's 148 text elements in 89 drafts (21 drafts have no text layer), 646 video segments, 171 audio segments and 20 adjustment layers. 35 drafts join to posted reels. Every field is extracted per element in `text_styles.csv` and per segment in `segments.csv` (`extract_capcut_style.py`); aggregates are in `style_stats.json` (`style_stats.py`).

## 1. The default text spec (team uses it on 136/148 = 92% of cards)
| property | value | CapCut field |
|---|---|---|
| Font | CapCut **System font** (`SystemFont/en.ttf`, font_id empty) on 148/148. Box render equivalent: **Montserrat Medium** (OFL), verified below | `styles[0].font.path` |
| Font size | **15** on 148/148. Size is set with the segment **scale**: median **0.93** for all cards, **0.88** for the hook card (IQR 0.77–1.00) | `size`, `clip.scale` |
| Fill | **#FFFFFF** on 147/148 | `fill.solid.color` |
| Stroke | **black #000000, width 0.09** on 136/148 (8 none, 2 at 0.10, 2 at 0.06) | `strokes[0]` / `border_width` |
| Shadow | none (148/148) | `has_shadow=false` |
| Background box | none (147/148; one black-on-white rounded box, unposted) | `background_style=0` |
| Letter / line spacing | 0.0 / 0.02 | |
| Alignment | centre (`alignment=1`), auto-wrap at 0.82 of canvas width | `line_max_width` |
| Bold / italic / underline | none (the font weight alone gives the look) | |
| Text template, effects, animation in/out | **none** (0/148: no templates, no presets, no in/out animations) | |
| Position | x centred (141/148). **Block centre 19.9% from the top** (median `transform.y` 0.60, IQR 17.1–21.9%). Hook card 19.6% | `clip.transform` |
| Rotation, keyframes | 0 / none | |
| Layers at once | 1 (144/148; 4 short overlaps at card switches) | |
| Lines | 1 line on 53%, 2 lines on 45%. The hook card is 2 lines on 66%. Median 17 characters per line, p90 25; hook card median 20, max ≈26–28 (BrickHood quotes) | `\n` in text |
| Words | hook card median 6 words, p10–p90 2–8 | |
| Emojis | 92% of cards end with 1–2 emojis after a space (see `emojis.md`) | |
| Timing | the hook card starts at 0.00 s. 63% of drafts use one persistent card (median 11.6 s). Multi-card drafts switch cards exactly on body cuts | |

**Pixel spec for the auto-edit (any frame width W):** font_px = 0.00557 × 15 × scale × W, which is **0.0777·W at scale 0.93** (≈84 px on a 1080 canvas, 168 px at 2160). stroke_px ≈ 0.086 × font_px (**≈7 px at 1080**). The text block centre sits at y = (1 − transform_y)/2 · H, which is **≈19% of H**. Wrap at 82% of W.
Machine form: `capcut_text_preset.json` (CapCut material fields for the exporter + render constants). Renderer: `render_text.py` (`render_card(text, W, H, scale, y)` → RGBA layer, colour emoji supported; composite with ffmpeg `overlay`). ffmpeg `drawtext` can't draw colour emoji, so the preset gives a drawtext fallback for text-only cards.

## 2. Variants by format / product (n = cards)
- **Then-vs-now (F04, n=22, 3.1 cards/reel):** the era cards switch exactly on body cuts. "Christmas 2024.. 😬" → "And Christmas 2025.. 🤕" → **"Vs... ⏳" at scale 1.21** (the bridge card is the largest text in the corpus) → "Christmas 2026 🤩🎄", which drops to 22% from the top (y 0.55) so it clears the lit product. Short single-line era cards stay at scale 1.0.
- **Problem/solution and concept-vs-result (F18/F19, n=9):** 3 cards ("The idea 🤮" → "Vs..." → "The result 😻"), scale 1.0, 14–21% from the top.
- **Don't-show (F05, n=11) and POV (F01/F12/F13):** one persistent 2-line card, scale 0.72–0.90 depending on length, 13–20% from the top.
- **BrickHood quote hooks (F16, n=7):** long 2-line quotes ("Send this to someone you'd / absolutely wear this with" 😂) are set at **scale 0.72–0.79** so 27–28 characters fit in 82% width.
- **On-screen CTA / JK cards:** these sit **lower, at 59–60% from the top** ("Say "MASK" if / you'd get one 😭", last ~3 s; BrickHood) and at 75% for "Just kidding, we / make them 🤭". So the end card moves to the lower-middle and doesn't replace the hook position.
- **By page (median scale, % from top):** MG 1.00 / 21.8 · MJIG 1.00 / 16.6 · HJ 0.98 / 20.9 · MC 0.91 / 14.6 · MGS 0.87 / 18.1 · BH 0.78 / 18.3 · MF 0.72 / 19.4. Scale follows text length, not the page.
- **Outliers (don't copy):** 8 no-stroke cards, 1 black text on white, 2 cards placed 31% from the top. None of them are on a 50K+ reel.

## 3. Winners (≥50K, n=13 reels) vs flops (<10K, n=16): text styling
| hook card | winners | flops |
|---|---|---|
| stroke 0.09 white/black | 92% | 94% |
| scale (median) | 0.88 (IQR 0.85–0.91) | 0.92 (0.77–1.00) |
| % from top (median) | 18.9 (IQR 18.2–20.2) | 18.9 (16.5–21.0) |
| words (median) | **5** | **7** |
| 2+ lines | **69%** | **81%** |
| emojis per hook | 1.54 | 1.62 |
| cards per reel | 1.85 | 1.56 |
| hook card duration | 11.3 s | 12.2 s |
| quoted text ("…") | 23% | 12% |
| contains ".." | 46% | 31% |

**Conclusion:** the visual style is a constant (one house style), so it can't explain views. The small differences that lean toward winners are slightly **shorter hooks (5 vs 7 words)**, more ".." trailing and more multi-card progression. They're all within noise at this n (Mann-Whitney not significant). The engine should hold the style fixed at the house spec and spend its variation on hook wording, format and shot grammar.

## 4. Video edit defaults (646 video segments)
- **Transitions: 0/646. Keyframes or zoom animation: 0. Crop: 0. Reverse: 0.** Only straight cuts.
- **Speed:** 1.0× on 89.5% of segments. Speed-ups are on 10.5%: 1.2× (16), 1.3× (10), 1.5× (10), 1.1× (9), 1.4–2.0× (11); slow-downs 0.8× on 3. Speed-ups land on body action clips (unboxing, pouring) to hit the ~1.4 s shot rhythm.
- **Scale:** 1.0 on 636/646. 9 segments are re-framed: 2.9–3.0× zoom-ins on a detail, or 0.2× picture-in-picture on FaceTime hooks.
- **Clip audio:** kept at 1.0 on 79%, muted on 13% (song-only beats), boosted 1.3–3.4× on 8% (named SFX moments such as an ignition whoosh or a "ring" doorbell).
- **Colour:** an optional whole-timeline adjustment layer in 18/110 drafts. The typical recipe is brightness +0.02, saturation +0.08, **temperature −0.08 to −0.28 (cooler)**, tone −0.08, light_sensation +0.06–0.08. No LUT filters.
- **Canvas** 1080×1920 (a few 1074–1080×1912–1928 from the source); export 2160×3840.

## 5. Audio tracks (171 segments)
No fades on any audio segment (0/171). Song volume median 1.0 (Bublé Holly Jolly 0.9; some 2.0–2.6 boosts). In-points (median seconds into the source file):

| song (file) | n | in-point |
|---|---|---|
| Wham! Last Christmas | 17 | **170.5 s (2:50)** |
| Bublé, It's Beginning To Look… | 15 | **32.4 s** |
| Free Bird | 14 | **15.0 s** |
| Mariah AIWFCIY (Make My Wish edition) | 12 | **49.6 s** |
| Bublé Holly Jolly | 12 | **0.1 s** |
| Boombastic (incl. TikTok Sting remix, n=2 at 21.9 s) | 8+2 | **21.6 s** |
| Dean Martin Let It Snow | 5 | 0.9 s |
| Nat King Cole Chestnuts | 5 | 14.2 s |
| Home Alone "Somewhere in my memory" | 5 | 104.0 s |

## 6. Verification
- **Extraction (hand check):** 16 random text rows (11%) re-read from the independent `Timelines/<uuid>/draft_info.json` copy. **16/16 match** on text, y, scale, start time, size and stroke (`verification_textrows.csv`).
- **Font:** rendered 7 candidate fonts against the posted 152.9K frame ("Christmas 2024.."). Montserrat Medium matches the glyph shapes (double-storey a, 2 and 4) and the height/width ratio (0.0926 vs 0.0902 measured). Poppins has a single-storey a; TikTok Sans is taller (0.105).
- **Size and position fit:** a template-matching fit on 12 posted reels gives a median size factor of 1.00 (strong matches 0.96–1.02) and a vertical offset of 0.00. Side-by-side renders (`_work/verify_*.png`) on MGS-07, MJIG-09 and MG-06 match line breaks, size, centre and stroke by eye. **Known residual:** CapCut on Mac draws Apple Color Emoji, and the box uses Noto Color Emoji (same size and slot, different art).
- **Draft ≠ posted text** on HJ-13 and HJ-15: those joined drafts are pre-post variants.

## 7. What the engine should apply
1. Every text card uses `capcut_text_preset.json` `default`. Pick the scale from length: ≤17 chars/line → 1.0; 18–22 → 0.88; 23–28 → 0.72–0.80. The bridge "Vs..." card → 1.2.
2. The hook card goes at y 0.62. Payoff cards may go to y 0.55. End CTA or JK cards go to y −0.2 (60% from top).
3. No animations, templates, shadows, boxes or transitions. Speed 1.0, with 1.2–1.5× only on long action clips.
4. Music at the table in-points, no fades. Clip audio at 1.0, muted under song-only beats.
