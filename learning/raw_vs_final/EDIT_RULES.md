# EDIT_RULES: how Omar turns raw generations into posted reels

Source: 35 CapCut drafts matched to 39 posted reels (25 high-confidence, 8 medium, 6 reconstructed from frames), 286 clip rows in `pairs.csv`, every value read from `draft_info.json` (source_timerange, target_timerange, speed, volume, scale, text and audio materials). Built 2026-10-19 (PT). Each rule below can be checked against a CapCut draft or an export.
Evidence key: n = number of clip segments or drafts; "W" = winners (the 4.6M, 687K, 241K and 153K drafts).

## A. Trims and in/out points
1. **No raw clip is used whole.** The median clip keeps **35%** of the raw (p10 18%, p90 77%). A 4.07 s Seedance gen becomes about 1.5 s on the timeline. *Check: kept_frac ≤ 0.8 for at least 90% of clips.*
2. **Split-and-skip inside one clip** (28 of 33 drafts). He cuts the same raw into 2–3 pieces and deletes a middle chunk (median skipped gap **0.4 s**, p90 1.35 s), which turns one generation into two "angles" with a jump cut. In the 4.6M reel, 5 of 7 raws were used this way. *Check: same raw appears ≥2 times with src gap > 0.2 s.*
3. **First shot:** median head trim is only **0.3 s**, and 40% start at 0.0. The hook keeps the generated opening because the start frame was approved. **Every later shot** gets a median **1.05 s** head trim, so the cut skips the gen's slow start. *Check: clips 2+ have src_in ≥ 0.5 s.*
4. **Tail trims are almost universal** (79% of clips lose >0.1 s at the end, median 1.23 s). He cuts out the generation's end drift and settle.
5. **Shot length:** median **1.5 s** on the timeline (p10 0.86 s, p90 3.2 s). 23% of shots are ≤1 s and only 12% are >3 s. Winners average **1.3–1.85 s** per shot. *Check: avg shot ≤ 2.0 s; no shot > 3.3 s except the hook.*
6. **Problem/hook section is 1.5–4.1 s** (the first card's end in 3-card reels: 4.07, 3.13, 2.03, 4.1, 2.73, 2.7, 2.17 s). *Check: problem card ends ≤ 4.2 s.*
7. **Total length is 12–17 s** (median 12.8 s; winners 16–17 s, the long end, with 9–13 shots). Shot count, not length, is what grows.
8. **Clip order mostly follows generation order**. Out-of-order reuse of an earlier moment happened in only 3 of 99 split pairs, so the story is shot in sequence and only tightened.

## B. Speed
9. **Speed is 1.0x for 90% of clips.** When it changes, it's a **speed-up of 1.2–1.5x** (median 1.3x, max 2.0x) on an action beat such as pulling the robe on or opening the box. The 687K reel sped up 3 of 10 clips (1.2x and 1.5x). He never slows a clip down (one 0.8x across all drafts). *Check: no speed < 1 except deliberate slow-motion afters.*

## C. Cards (on-screen text)
10. **Font is fixed:** CapCut system font, **size 15, stroke 0.09–0.10 black on white fill**. Scale is 1.0 (0.67–0.9 for long 2-line POV captions). Vertical position is **ty 0.53–0.72**, so cards sit in the upper-middle and never at the bottom. *Check those exact values.*
11. **The 3-card structure goes with higher views** (r = +0.34 with log views; the strongest single feature). The pattern is "[Problem/Concept/Christmas 2025] + 1 emoji" for **2–4 s**, then **"Vs..."** (optionally ⏳/⏰) holding through the whole build, then "[Solution/Result/Christmas 2026] 🤩+1" for the **last 3.1–4.2 s**. This is the format of the #2 4.6M and #6 687K reels.
12. **Each card has one or two emojis at the end**, never in the middle. The emoji vocabulary splits by beat: the problem gets 🤮 🤢 😬 🤕 🤒; the payoff gets 🤩 😻 ✨ 🎄 ❄️.
13. **The single-card POV/"DON'T show this to a Christmas-aholic" format failed 3 out of 3 times** (9K, 457, 33). Single-card POVs only did OK (61–63K) on BrickHood and Merry Carrier. *Rule: default to the 3-card structure; single-card POV only for a proven page/product.*
14. When there are two problem scenes there are two cards ("Christmas 2024.. 😬" 0–2.03 s, then "And Christmas 2025.. 🤕" 2.03–4.27 s); otherwise one (Omar's 10-19 instruction matches the 153K draft `0922`).

## D. Song and in-point
15. **One licensed Christmas song, cut in at a recognizable lyric, not at 0:00.** Winner in-points: Mariah "All I Want…" at **42.4 s / 49–53 s**, Bublé "It's Beginning to Look…" at **31.3–32.6 s**, Wham "Last Christmas" at **170–171 s**. Low performers start the song at its intro (Dean Martin at 0.9 s three times: 5.3K, 2.7K, 457; Wham at 0.3 s: 33). Song in-point correlates +0.26 with log views. *Check: song src_start ≥ 15 s unless the intro itself is the hook.*
16. Holly Jolly is the one exception that works from about 0.1–2.5 s (63K and 62K Merry Carrier).
17. **The raw Seedance audio is usually kept** (volume 1.0 on 89% of clips). It gets muted (volume 0) on payoff/afters shots where SFX would fight the song (the 4.6M muted its 3 afters shots), and boosted to 2–5.8x on a key diegetic moment (the 687K boosted the reveal clips to 1.96x and 4.16x). He sometimes ducks the music to 0.29–0.8. *This contradicts the engine default of "generate silent". Use: generate with natural audio, mute only the afters.*

## E. Zooms, crops and overlays
18. **No zoom, crop or reposition on the video track.** Every matched clip has scale 1.0, transform 0,0 and a full crop. He fixes framing in the start frame, not in the edit. *Check: scale == 1.0.*
19. Overlays are rare: a PNG ring or emoji on an upper track (the GrinchMelt 6.3K draft) and an optional second text card at ty ≈ −0.19 to −0.30 (lower third) for a CTA ("Link below 🔗", "Comment 'MASK'"). Neither appears in the top performers.

## F. Reuse and rejection
20. **Winning raws get re-cut into new reels.** The two 1.4M HeatedJammies reels share 3 of their raws (aa03060d, 3e6bcbbd, c0ede3c3) in a different order with different trims. Merry Glow variants (`0924`, `0924 (1)` and `0924 (3)`) re-import the finished 153K/98K export ("stripped use for variants.mp4") and only change cards and song. The variants then got **64K, 84K and 1.2K**, so the card and song swap alone can matter by 50x.
21. MerryFire/JollyGlow project clips (02_unbox_tray, 03_pour_light, 04_fuel, 05_ignite, 04_snacks_cinematic) are each reused in 2–3 different posted reels.
22. **Rejection is low once the start frame is right.** Inside each winning draft's generation window, the 4.6M used **7 of 7** gens, the 687K **7 of 8** and the 153K **6 of 7**. Wide windows show more discards (15 of 76 around the 241K). This is a lower bound, because Omar deletes rejects from Downloads (`rejected_clips.csv`).

## G. Models seen in winning raws
23. Raws are **seedance_2_5** (hook and new scenes) and **cinematic_video_editor** (Higgsfield edit/restyle of an existing clip: the 4.6M's afters clips 5–11 and the 687K's last 3 clips). 4 s, 1080×1920, exported at 2160×3840.

## 10 most important rules (for the engine's linter)
1. Keep only 20–80% of each raw (median 35%). Head-trim later clips by about 1 s and tail-trim about 1.2 s; keep the hook's opening.
2. Split one generation into 2–3 pieces and drop a 0.3–1.3 s middle chunk (fake second angle).
3. Average shot is 1.3–1.85 s, with no non-hook shot over 3.3 s and 9–13 shots in a 16–17 s reel.
4. Use 3 cards: problem (2–4 s) → "Vs..." (holds through the build) → solution (last 3–4 s), with an emoji at the end of each.
5. Card style: system font, size 15, stroke 0.09, white with black outline, ty 0.53–0.72. No bottom captions.
6. One famous Christmas song entering at a lyric/chorus (Mariah 42–53 s, Bublé 31–33 s, Wham 170 s), never from the intro (Dean Martin at 0.9 s lost 3 of 3).
7. Keep the gen's natural audio, mute it on the afters, and boost the key diegetic beat.
8. Speed is 1.0x by default, with 1.2–1.5x only on action beats and never slow-mo on story shots.
9. No zoom or crop in the edit (scale 1.0). Framing is fixed in the start frame.
10. Re-cut winners: reuse proven raws or the stripped export with new cards and song for variants. Drop the "DON'T show this to a Christmas-aholic" single-card format.

## Engine wiring (2026-10-19 PT): `engine/hookforge/edit_rules.py`
These are the editor defaults (`edit_rules.D`, `default_timeline(gens)`) and the linter (`edit_rules.lint(plan)`). The linter runs in planner.plan (`plan["edit_defaults"]`, `plan["edit_lint"]`) and recreate_mode.check (src=edit_rules).
- **Defaults:**
  - Head-trim 1.05 s and tail-trim 1.2 s on every clip after the first; the first clip keeps its opening.
  - Split every later gen into 2 pieces (up to 3) and drop 0.4 s from the middle.
  - Median shot 1.5 s, max non-hook shot 3.3 s, target 16–17 s with 9–13 shots.
  - 3 cards: problem → "Vs..." → solution.
  - The song enters at its famous lyric. ER15 warns on an in-point under 15 s; Holly Jolly is the exception.
  - Speed 1.0x, 1.2x (up to 1.5x) on action beats. No zoom: scale 1.0.
- **Severity:**
  - **FIX (blocks):** zoom/crop, slow-mo story shot, generate_audio off.
  - **WARN (logged):** length, shot count, median, head trims, splits, cards, song in-point.
- **Audio (D63, Omar decided 2026-10-19 PT):**
  - Keep the natural clip sound: generate_audio=True, clip volume 1.0.
  - Boost the key real sound 2–4x (`shot.audio_gain`); ER17 warns when nothing is boosted.
  - Fake SFX are banned (LG3 + qa.audio_check).
  - Rule 17 is now in force, without muting the afters by default.
- **Tests:** engine/tests/test_edit_rules.py.

## C-HOOK1 (D67) Short proven hook formats > long POV sentences
On-screen hook must be about 8 words or fewer and on screen from frame 0. Prefer Omar's "Don't show this to a ____" + 1–2 iOS emoji. Own evidence (performance_all.csv): 14 reels, peak 183K "DONT show this to your Grandma ❄️😳", 112K/98K/97K/88K "...your mom" (HeatedJammies FB), 9K IG "Christmas-aholic", 3.3K/2.7K IG "skier". Long POV sentences (more than 8 words) are penalized in audience_fit.check_text. Omar rejected "POV: ur wife got this for your truck so you stop arguing politics at Thanksgiving 😂🤝".
