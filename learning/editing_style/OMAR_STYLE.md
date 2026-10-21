# OMAR_STYLE: how Omar edits in CapCut (built 2026-10-19 PT)

Source: 105 of his CapCut drafts (`draft_info.json`), from the read-only box mirror of `~/Movies/CapCut/User Data/Projects/com.lveditor.draft`, with `1018 (4)` re-copied fresh today. Drafts that only wrap Hookforge renders (trumpglow_/jollyglow_/HF_TEST) are left out. 40 drafts are joined to posted-reel views (private/edits/edits.csv + raw_vs_final/draft_features.csv); 17 have ≥50K views. Each draft is weighted by log10(views)−2, and unjoined drafts count like 1K views. Numbers are weighted medians with p10–p90 ranges. Timing and speed use the 82 drafts with ≥3 shots (1–2-shot drafts are pre-cut exports). Script: `extract.py` → `stats.json` (all numbers), `style.json` (engine defaults), `shots.csv`, `cards.csv`.

## Timing
- Total length: all 13.1 (p10–p90 11.3–16.833, n=82) s; **top performers 12.567 (p10–p90 11.3–16.833, n=14) s**. Our old 16–17 s default was too long.
- Shots per video: 7 (p10–p90 5–11, n=82).
- **Opener (first shot): 2.367 (p10–p90 1.5–4.833, n=14) s for top reels**. Hard ceiling in style.json is 4.1 s (the TrumpGlow B peel at 3.6 s and C at 4.1 s are at or over his p90).
- Shot length by role (s): before/problem 1.233 (p10–p90 0.667–2.333, n=137); reveal 2.233 (p10–p90 1.233–3.4, n=28) (the one longer beat); afters 1.267 (p10–p90 0.8–1.833, n=32); other body shots 1.467 (p10–p90 0.867–3.2, n=329).
- Ending shot: 1.733 (p10–p90 1.067–3.5, n=82) s.
- Roles come from card windows: hook = first shot, before = up to the last card, reveal = first shot under the last card, afters = the rest.

## Speed
- 11 % of shots are sped up, in 50 % of drafts. Values: 1.3 (p10–p90 1.1–1.8, n=67). Most common: 1.2x ×15, 1.5x ×10, 1.3x ×10, 1.1x ×9, 1.6x ×4, 1.4x ×4, 2.0x ×3, 1.15x ×3.
- By role: hooks 16/82 sped (most often 1.2x), befores 21/137, reveals and afters almost never.
- No ramps or curves (speed mode 0 only). Slow-mo is essentially never used on story shots (0.8x shows up once, on a hook).
- **Rule:** when a spoken hook is too long, speed the whole hook up (1.1 → 1.15 → 1.2 → 1.3 → 1.5) instead of cutting a word.

## Cuts
- Transitions: 0 in 105 drafts. Hard cuts only, no zooms, essentially no overlays.
- 67 % of shots are head-trimmed (median 0.9 s). He cuts into the motion instead of starting on frame 0, which is the cut-on-action proxy (frame-level action detection is not measured).
- Colour adjust (brightness/HSL) is used in 18 % of drafts.

## Text
- Font: CapCut system `en.ttf` on all 148 cards. Size 15, white fill, black stroke 0.09, line_max_width 0.82. No templates, animations or backgrounds.
- Card scale 0.919 (p10–p90 0.723–1.0, n=148), i.e. em ≈ 7.4 % of frame width. Centre at 0.2 (p10–p90 0.152–0.237, n=148) of height from the top (upper fifth).
- **Rows: 98.6 % of cards are ≤2 rows**, broken by hand with ⏎. The few 3-row cards are older drafts. Characters per line: median 18.0, max ~24. Total characters median 22.0 (p90 44).
- Timing: the first card is on at 0.0 s in 99 % of drafts. Card changes sit on a cut 83 % of the time. 38 % of cards stay up for the whole video (single-hook format). In 3-card formats, cards last 3.967 (p10–p90 2.5–9.7, n=92) s, and the last card holds to the end.
- Emoji: 1 per card (max 2 in practice), placed at the end of the card in 93 % of cards. "Vs..." cards often have one timing emoji (⏳/⏱️).

## Audio
- Song on 79 % of drafts. It starts at 0.0 s on the timeline (median), cut in at its famous line (in-point median 21.6 s; Holly Jolly from ~0.1 s). The song runs to the end of the video in 86 % of drafts.
- **No fades (0 of 97) and no volume keyframes or ducking (0).**
- Song gain is usually 1.0 (0 dB). He pulls it down (to 0.29–0.8) when a hook has dialogue.
- Clip sound is kept at 1.0 and muted on 14 % of shots. **Dialogue and countdown shots get boosted**: 8 % of shots, median ×2.954 (≈+9 dB), mostly hooks and befores. On average the boosted clip ends up ≈+14 dB over the song's gain.
- Measured loudness on the raws we have (same songs): speech sits **+4 to +10.6 LU over the music**. The 1011 Walmart countdown hook (the closest match to Jolly Glow) is +7.7 to +10.6 LU. Engine target: **+8 LU**.

## Endings
- He ends on an after or the reveal, never on an end card. The last card covers the end in 99 % of drafts. No on-screen link or CTA.

## Top drafts (views-joined)
| draft | views | s | shots | opener | speeds | cards | song @ in-point |
|---|---|---|---|---|---|---|---|
| 0920 (1) | 4,626,729 | 17.03 | 13 | 1.5 | – | The problem 🤒❄️ / Vs...  / The solution 🤩💆🏼‍♀️ | Mariah Carey - All I Want for Christmas  @42.4s |
| 0913 (1) | 686,895 | 16.3 | 10 | 3.13 | [1.2, 1.5, 1.5] | The concept 🤮 / Vs... / The result 🤩❄️ | Michael Bublé - It's Beginning To Look  @32.4s |
| 0922 | 152,878 | 12.23 | 7 | 2.03 | [1.4] | Christmas 2024.. 😬 / And Christmas 2025.. 🤕 / Vs... ⏳ / Christmas 2026 🤩🎄 | Wham! - Last Christmas (Official Video). @171.2s |
| 0923 | 152,878 | 12.07 | 1 | 12.07 | – | – | – |
| 0920 | 97,955 | 12.57 | 7 | 3.77 | – | – | – |
| 0910 | 91,000 | 16.83 | 9 | 3.17 | – | "The perfect gift  ⏎ doesn't exi-" 😳☃️ | Mariah Carey - All I Want for Christmas  @53.2s |
| 0924 (3) | 84,377 | 13.43 | 3 | 9.83 | – | Christmas last year.. 😬 / Vs... ⏱️ / Christmas in 2026 😻 | Wham! - Last Christmas (Official Video). @170.2s |
| 0920 (2) | 70,437 | 12.8 | 11 | 0.87 | [1.6, 1.6, 1.6, 1.3, 1.2] | Christmas trees ⏎ in 1968 👴🤦‍♂️ / Vs... ⏳ / Christmas trees ⏎ in 2026 🤩🎄 | Mariah Carey - All I Want for Christmas  @49.7s |
| 1007 | 67,731 | 14.47 | 11 | 2.8 | – | Christmas last year.. 🤕 / Vs... ⏳ / Christmas this year 😻✨ | Michael Bublé - It's Beginning To Look  @32.6s |
| 0924 (1) | 64,542 | 13.43 | 1 | 13.43 | – | Christmas in 2025.. 🤮 / Vs... ⏳ / Christmas in 2026 😻🎄 | Michael Bublé - It's Beginning To Look  @31.3s |
| 1010 | 63,320 | 12.1 | 7 | 2.17 | [1.15, 1.15] | POV: the whole street is  ⏎ JEALOUS of your house.. 🤭🏠 | Michael Bublé - Holly Jolly Christmas [ @0.1s |
| 1009 (4) | 62,992 | 11.3 | 7 | 2.37 | – | POV: Christmas movie night ⏎ will never be the same 🥹❄️ | Wham! - Last Christmas (Official Video). @0.4s |

## What the engine does with this (D74)
- `engine/hookforge/omar_style.py` loads `style.json` and provides:
  - `hook_speed()` to fit a hook by speeding it up, never cutting.
  - `card_layout()` for at most 2 rows, shrinking the card scale.
  - `dialogue_gain_db()` to put speech at +8 LU over the song (clip gain capped at +20 dB, after which the song is lowered instead).
  - `compare()` / `timeline_from_final()` for the edit-vs-Omar score from 0 to 100. A hard-rule miss (3 rows, on-screen link, late song, buried voices, slow-mo, hook speed out of range) BLOCKs.
- `songlay.lay_song(..., dialogue=[(t0,t1)])` sets clip gain from Omar's style. Clips with no dialogue stay at 0 dB with no ducking. The function returns `dialogue_minus_music_lu`.
- `edit_rules.D` uses Omar's target length, shot count and median shot length, and exposes `edit_rules.hook_fit`.
- `qa.final_checks(..., cards=, dialogue_minus_music_lu=)` adds `edit_vs_omar` to the preflight report.

Caveats: line counts come from his manual line breaks (wrap is only estimated). "Cut-on-action" is a head-trim proxy. Dialogue LU is measured on 5 shots from 3 drafts, because most raws are on the Mac only. Only 40 of 105 drafts are joined to views.
