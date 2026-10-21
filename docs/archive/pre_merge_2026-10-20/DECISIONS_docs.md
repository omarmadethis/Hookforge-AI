
## D59 — First live test switched to MerryGlow then-vs-now (Omar, Mon 19 Oct 2026 07:04 London)
- **Format:** F04, chosen from own data: 8 reels, median 71K, best 153K, against F01's 2 reels.
- **New engine pieces:** a MerryGlow F04 world (tangled-lights short-out disaster, family of five + dog), an unbranded BOX shot, and a pixel-LED product look.
- **4-card timing:** then-vs-now plans that carry 4 own cards now time them like MG-01: then1 | then2 (internal hook cut) | Vs.. (product shots) | now (from the lights-on reveal).
- **Music scoring fix:** proven-on-product views now count on a log scale, so a 2× own-views gap beats the 0.1 region prior. Last Christmas (153K on MG) now wins over Mariah (70K). No other dry-run pick changed.
- **Product reference:** a cropped, text-free frame from own MG-01.
- **Cost:** 174 credits (get_cost), cap 244.5. See FIRST_LIVE_RUN.md.
- **Live status:** still DISABLED.

## D54 — hookforge.db is the default reels source after review (Omar task 1, 2026-10-18 10:35 PM PT)
`engine/hookforge/reels_db.py` merges data/hookforge.db (read-only, `mode=ro`) **corpus-first**:
- Identity fields (key, page, product, hook_text, posted_pt, format, views) keep the corpus values.
- DB-only columns are added. DB values only fill corpus gaps.
- Externals are mapped by reel id.

`review()` writes learning/db_review.json. It passed for db_sig 1792387118:1970176:
- own coverage 78/78
- views within 2% 82/82
- unique uid
- posted time within 5 min 1.0

The DB is the default only while that review matches the current DB file (mtime:size). Set `HOOKFORGE_USE_DB=0` to force the corpus.

The dashboard, learn.update, posting_time, backtest and model now read through load_reels. Any merge error falls back to the corpus with a stderr note.

The views model was retrained on the DB source. LOO B3 spearman 0.236 vs 0.233 on the corpus; still ADVISORY (D35).

DB issues for the features worker are listed in docs/FEATURES_HANDSHAKE.md. We coordinate through files, never by editing data/features.

## D55 — Public dashboard: no product/brand names, no hook text (Omar task 3)
analytics/public_scrub.py rewrites the public build:
- product → category label (e.g. "Wearable gift", "Decor (fire)")
- page → "Page N"
- hook_text → "<format> · <hook type>"
- every free-text column blanked
- engine panels lose the brief, hook text and rule evidence

A last-line audit runs over the finished HTML:
- deny-list of brand, product and page names → "[redacted]"
- store names → Store A/B/C
- every corpus hook text → "[hook text]"
- reel ids → "[reel]"

The build asserts 0 remaining (analytics/data/public_audit.json).

## D56 — vision_judge is the D33 absurd-failure judge (Omar task 4)
engine/hookforge/vision_judge.py (qa.judge_raw_gen; runner.judge) decides automatically per raw generation. It uses:
- CLIP fidelity against banks built from Omar's own reels: own-product, best other product, scene
- contact-sheet pixel checks: blank, frozen
- raw_gen_checks: 9:16, packed hard cut, OCR

Thresholds are calibrated leave-one-reel-out per product: 0/78 genuine own reels are judged "certain" (learning/vision/CALIBRATION.md).

Certain (≥0.9) only for product_missing, wrong_product, scene_unrelated, hook_unusable (blank/frozen), wrong_aspect_ratio and hard_cut_missing_or_broken. Inside the genuine range, confidence is scaled below 0.9, so the clip ships and is logged.

Mangled limbs, product deformed and wrong colour are capped at 0.6, so they are never auto re-rolled. Still max 1 re-roll per shot (D33).

## D57 — Live Higgsfield path built behind an approval gate, DISABLED (Omar task 5)
runner.py has the live state machine: start_run → next_call → record_cost / record_submit / record_result → judge.

The engine never calls the network. next_call hands the agent the exact MCP call:
- always the get_cost preflight first, then the paid call
- the gate is re-checked on every call

The gate requires all of:
- `config.LIVE["enabled"]`, which is False
- live=True
- learning/approvals/<run_id>.json with approved_by Omar, the plan sha256, gen ids, account, credit_cap ≥ total, not expired, not consumed (single use)

It refuses when a quote differs from the plan by more than 0.5 credit, when the spend would pass the cap, or when it would resubmit after a timeout.

Prices were confirmed by get_cost, which submits nothing (new-account):
- Seedance 2.5 1080p 4 s = 64, 720p 4 s = 28, 1080p 5 s = 80
- GPT Image 2 2k high = 6.5

Tests: engine/tests/test_live_gate.py, 20/20. First run: FIRST_LIVE_RUN.md.

## D58 — Mug: proof shot, own hook, niche-proven caption (Omar task 2)
- GrinchMelt mug PROOF: real-time melt close-up.
- F01 adaptation: static eye-level, mug at 40% of frame, whispered 3-2-1.
- Hook "When the nights get colder, this comes back out 🤍" (EXT-10, 7.3M, 1 emoji); alt "Hot cocoa just got an upgrade ☕😳".
- When a product has no proven caption, the planner uses a caption proven on a sibling product of the same page ("niche-proven", e.g. robe "Get yours👉{url}", 6.6M) before the format default. logic_check passes.
- The mug is in the dry-run set and test_core_path.
- Race-targeted hooks are excluded in the planner and as a plan_checks FIX (parent steering 10:50 PM PT). Neutral recipient framing only.

## D52 - Covered-reveal hooks are allowed (Omar override, 2026-10-18 9:55 PM PT)
The psych codebook's PS02 ("gap without cue": product under a cloth/tray at 0 s, 0/5 hits) proposed blocking covered hooks or
restricting them to experiment slots. Omar: covered-reveal hooks are GOOD and our coded data is missing their winners.
Decision: NO block and NO experiment-only restriction. Covered-reveal (F05 / cloth / tray) stays a normal, allowed hook.
The psych scorer reports PS02 but never penalises it. Revisit when the style team sends the re-coded covered-hook reels.

## D42 — Generation failure memory: WIRED (Omar go-ahead 2026-10-18 10:00 PM PT; supersedes "deferred")
engine/hookforge/gen_failures.py + learning/gen_failures/{ledger,pairs,rules,failure_rate}.csv. Backfill from the Higgsfield
generation export (1,136 attempts: 375 ok, 27 nsfw, 11 ip, 10 param, 88 preset notices, 4 credits, 513 batch rows with unknown
per-job status). 53 failed→working pairs (minimal word diff, same session/project + model family, ≤6 h, prompt sim ≥0.5).
Rules: param (deterministic API errors) + curated (from confirmed fixes) + auto word rules. Auto word rules start as
'candidate' (stored, not linted) and promote only with ≥2 fix pairs, ≥3 blocked prompts and ≥2.5× lift vs ok prompts.
The linter (runner.preflight) runs on every video, still and recreate prompt before any generation; promoted hits are FIX,
hypotheses INFO. runner.submit() never submits in this build. Misgens enter the ledger from qa.reroll_decision (certain
absurd failures) or log_attempt(); the backfill cannot see misgens (75 'resubmitted within 30 min' candidates flagged only).
Finding: 'grinch' alone is NOT a block trigger (1/21 blocked vs 1/63 ok seedance; d7bf7598 recreate completed).
## D44 addendum — structural provenance detector (2026-10-18 ~10:20 PM PT)
preflight.provenance() matched any b"c2pa" bytes, which false-positives on compressed video (TikTok proxy fixture had one
random 'c2pa' and no manifest). Now: C2PA uuid box (d8fec3d6-…) or a JUMBF jumb/jumd box labelled c2pa, plus IPTC
DigitalSourceType / trainedAlgorithmicMedia. tests/test_c2pa_strip.py builds a fixture with a C2PA uuid box + AI XMP,
asserts final_checks BLOCKs it and that autoedit.clean_export removes everything. Every dry run also runs the animatic
through clean_export + the final provenance assert (export_test_clean.mp4).
## D53 — Covered-reveal hook options + advisory PS02 (style re-code, 2026-10-18 10:09 PM PT)
Re-code (style/covered_hooks.csv, covered_stats.json): covered reveals 5/16 at ≥50K incl. HJ-02 2.7M; robe-only 5/11 vs 21/48
(45% vs 44%, Fisher p=1.0). Split: product cue visible at 0 s 5/10 wins (median 63K) vs fully hidden/mismatched 0/6 (median 3K);
all 5 wins reveal ≤3.0 s. Engine: psych.ps02() is ADVISORY (never blocks): covered AND own cue visible at 0 s (colour/texture/face
around the tray/tin, or a drape in the product's fabric/colour) AND reveal ≤3.0 s; tray/tin versions also need 35–60% of the
frame in a still, eye-level medium shot. Hook options (worlds.ADAPTATIONS keyed (format, product, option)):
robe covered_reveal (F05 text over the tray/tin visual; refs HJ-02/HJ-05/HJ-14; tin cover variants), robe covered_drape
(F03 store drape in the robe's own fur; refs MJIG-17/HJ-10), fire pit + ski mask covered_glow (F01, glow under cloth) as
INNOVATION-SLOT only (experiment_only forces slot=experiment). Briefs: "covered reveal…", "store drape unveil…", "glow under cloth…".
Side fixes: robe store_look no longer names Target/Walmart (GF-C1 linter caught it in F03 prompts); a verbatim own proven hook
with 3 emojis (HJ-10 "Grinch X Target 😂🎁❄️") is WARN, not FIX. style/ and psychology/ files were read, not edited.

## D60: Unlit start frames for pre-reveal shots, plus the B3 redo (Omar, 2026-10-19 7:20 AM PT / 3:20 PM BST)
- **Bug (mg-tvn-001 B1).** prompts.body_still appended the lit `product_look` to every body start frame. B1 (BOX/INSTALL) therefore opened on a tree already showing the snowman/train picture, which spoiled the reveal before ACT. The B1 clip is in the final edit, so this AI tell is in it too.
- **Fix.** planner.py now passes `unlit=True` for every body gen whose first shot comes before the first LIT*/payoff shot. This applies to activation products only (those with `activation_result`). For those gens, prompts.body_still describes "the {product} ... still switched OFF: dark, no colours, pictures or glow yet". Verified on MerryGlow F04: B1 and B2 are OFF, B3 is lit. test_live_gate 20/20 and test_core_path pass, test_c2pa_strip passes.
- **B3 redo.** Run mg-tvn-001-b3 (approval "Redo B3 with adults in front, cap 34.5 credits"): 1 start frame (6.5) plus 1 Seedance 720p clip (28), spent 34.5 exactly. The new prompts put two adults in normal sweaters in the foreground, keep the children small and behind them (never central, never close-up), and keep everyone fully clothed. The word "kids" is avoided.
  - GF-C6 fires on the old B3 prompt and not on the new one.
  - The clip was not blocked. Supporting evidence for GF-C6 (still a hypothesis).
- **gen_failures.backfill().** It now keeps live rows ("lv*" ids). They had been wiped once, and the 16 mg-tvn-001 rows were restored from run.json.

## D61: POST-MORTEM of mg-tvn-001, and RECREATE as the default mode (Omar, 2026-10-19 ~8:00 AM PT / 4:00 PM BST)
Omar's verdict: "horrible and unusable. We lost the plot."

### What went wrong, and why
1. **Scene 1 had the family sitting robotically, staring at the camera.** The F04 template still said "five family members in sweaters on the couch" with no actions, and nothing checked whether the people were doing anything believable.
2. **Cards: "Christmas 2024" + "And Christmas 2025" over ONE problem scene.** We copied MG-01's card text, but MG-01 has two problem scenes.
3. **A loud generated "YAY".** The prompts asked for "Natural sound only: click, gasps, kids cheering" with generate_audio=True.
4. **Noto emoji** instead of Apple iOS emoji.
5. **The install scene was nothing like ours.** It was generic hands placing lights; ours is a guy on a ladder dropping the MerryGlow on the tip and the rings slowly unfolding around the tree.
6. **Static afters that look alike.** "Bursts into colour" and "hero wide" never said what animates.
7. **Root cause: we planned from a format template instead of recreating our own posted winner.** "We're literally just trying to recreate slightly different original versions of our videos that already exist."
8. **No LOGIC step on prompts.**
9. **CapCut text was off.** The text material matched Omar's, but card scale was 0.88/1.2 instead of 1.0, y was 0.62, and the box render's weight and stroke were off.

### Changes
- **RECREATE is the default mode.**
  - planner.plan dispatches to recreate_mode.build whenever refs/recreate/<product>.json exists; the format-template planner needs mode="original".
  - The spec holds the shot list extracted from the actual videos (timing, action, camera, blocking, product behaviour, per-after animation) and the cards and song from Omar's CapCut draft.
  - Prompts restate the beats of the verified MG-01 prompts (82e418f4, 2d4f23c9, 4dabfa47, c7888523). Only the 20 % innovation slot (cast, decor, after designs) may change.
  - MerryGlow spec v1 = OMAR_REF (draft 0924 (2)) structure + MG-01 beats, using the asset library's box, lit tree and ladder frames.
- **LOGIC step (logic.py).**
  - Lint rules LG1 (camera stare), LG2 (unmotivated people), LG3 (voices/cheering/SFX), LG4 (afters must animate and differ), LG6 (card count).
  - Vision checks:
    - **person_facing_camera** (YuNet frontal faces ≥ 1 s): flags tvn H and B1, and also OMAR_REF 0.5–2.75 s — the frozen smile his analysis already flagged.
    - **static_lights** (bright-pixel motion < 3.0): flags tvn B2 (1.46) and B3 (2.51). It also flags MG-01's own snowman shot (0.08), so the bar is now stricter than that reel.
    - **afters_not_distinct.**
- **Cards.**
  - textcards.py: one then-card per problem scene (check_cards), Apple emoji PNG overlays (160 px iamcal img-apple-160, cached in assets/emoji_apple/; fallback Apple TTF 96 px strike).
  - Box font recalibrated to Omar's reel (Montserrat wght 560, stroke 0.091·px, y 0.576–0.582).
  - CapCut: scale 1.0, y 0.582, stroke width 0.09 (= UI 45). See out/dryrun/mg_recreate_mg01/CAPCUT_TEXT_FIX.md.
- **Audio.** LIVE.video.generate_audio=False; prompts.finish() swaps any audio line for "Silent clip: no dialogue, no voices, no sound effects, no music"; autoedit.final_cmd drops clip audio (silent track); CapCut clip volume 0. The only audio is the licensed song added in CapCut.
- **Failure memory.** GF-Q1..Q9 are promoted rules (FIX in pre-flight); the old mg-tvn-001 prompts now fail on Q3/Q5/Q6. There are 9 `omar_reject` ledger rows for mg-tvn-001.
- **Tests.** tests/test_recreate_logic.py (11 checks) passes; test_live_gate 20/20, test_core_path and test_c2pa_strip still pass.

## D62: Mandatory AUDIENCE-FIT stage (Omar, 2026-10-19 ~2:00 PM PT)
Omar: "song matching, emoji matching, caption matching it all needs to fit in that audience/niche always. this isnt amateur hour." Also: "never ever use phonk", "use proof of concept as well".

### POST-MORTEM: phonk picked for TrumpGlow
- **What happened.** The first TrumpGlow plan proposed phonk because the Hello Kitty reference reels used it. TrumpGlow buyers are US Trump supporters, mainly on Facebook, and phonk pulls non-US audiences.
- **Root cause.** The song was copied from the reference format instead of being picked for the buyer. Nothing in the engine checked song, emoji or caption against the audience, and nothing required proof.
- **Rules.** GF-AF1 (phonk / reference-song copying), GF-AF2 (emoji set + Apple iOS render only), GF-AF3 (caption and card proof + voice) are promoted in learning/gen_failures/rules.csv.

### Changes
- **Profiles.** audience/<slug>.yaml for merryglow, grinch_robe, merryfire, brickhood, minionmask, grinchmelt, jollyglow, purrventure and patriotglow (alias trumpglow). Each covers buyers, main platform, markets, tone, allowed and banned genres, the emoji set with its niche meaning, slang, caption voice, caption_proof patterns with evidence, and bans. audience/_global.yaml holds the global bans: phonk (and slowed / funk / drift variants), Android/Noto/Twemoji render, UK spellings.
- **engine/hookforge/audience_fit.py.**
  - check_song: global and genre bans, allowed genre, evidence (URL or own:/omar:/ref:/ext: reference), in-point and tier are all required.
  - song_rank: tier a = proven on the same or similar product, b = trending with the buyers, c = reference format.
  - check_emoji: profile set, Apple render only.
  - check_text: bans, US spelling, caption_proof or a proven hook source, plus a voice/slang score.
  - check_plan logs every row to learning/audience_fit_log.csv.
- **Linter and gate.**
  - planner.plan adds plan["audience_fit"] and AUDIENCE-FIT lines in prompt_checks.
  - recreate_mode.check adds AF1/AF2/AF3 FIX rows, so a failure fails plan checks.
  - runner.check_gate refuses any live run whose plan fails AUDIENCE-FIT.
- **TrumpGlow song slot.** audience_fit.song_slot("patriotglow") parses research/trumpglow/SONGS.md (the research is not duplicated here).
  - Result: Free Bird (tier a, Omar-confirmed, in ~4:57) > Y.M.C.A. (tier b, 2 URLs, in 0:00).
  - Kid Rock, Toby Keith and Aldean FAIL for no evidence URL until the FB Ad Library pass fills them in.
  - Output: out/dryrun/trumpglow_A/AUDIENCE_FIT.json.
- **Tests.** engine/tests/test_audience_fit.py (19 checks).
- **Edit defaults (same day, parent steering).** learning/raw_vs_final/EDIT_RULES.md is now engine defaults and lint (engine/hookforge/edit_rules.py, rules ER2/3/5/7/9/11/15/17/18).
  - FIX: zoom, slow-mo story shots, unmuted generated audio.
  - WARN: the other targets.
  - Generated audio stays muted until Omar decides.

## D63: Natural clip sound replaces "mute generated audio"; song in-point evidence (Omar, 2026-10-19 ~2:08 PM PT)
This supersedes the D61 audio policy.

### Audio
- **Keep:** real voices, some cheering, gasps, environment and action sounds (scissors, doors, tape, sparks). Boost the key real sound 2–4x, as in Omar's edits (`shot.audio_gain` → autoedit volume filter and CapCut segment volume).
- **Ban:** whooshes, cartoon sounds, an inserted "YAY", added SFX/music, and stray sounds that don't match the action.
- **Prompt line:** "Silent clip" → "Natural ambient sound only: real voices and action sounds that match what happens on screen, no added sound effects, no music." (prompts.silent / recreate_mode.SILENT).
- **Settings:** config LIVE.video.generate_audio=True; clip_audio_volume 1.0; autoedit.final_cmd keeps clip audio.
- **Checks:**
  - LG3 is rewritten to flag fake sounds and a missing natural-ambient line; real cheering and gasps are allowed.
  - GF-Q3 is re-triggered on yay/whoosh/boing/cartoon/SFX.
  - New qa.audio_check(clip, prompt, transcript): no audio stream or silence = FAIL, fake SFX in the prompt or transcript = FAIL, 0 dB clipping = WARN. A listen pass by the watch judge is still needed for stray sounds.

### Song in-point
- check_song now also needs `in_point_evidence`: the section people actually use on similar videos, from the TikTok/IG audio page's popular clip or the most-used start in reference reels or own drafts. A song without it FAILS.
- Library songs get evidence from the most-used CapCut offset across ≥2 own drafts.
- TrumpGlow:
  - Free Bird enters at 15.0 s on the CapCut file (11 own drafts).
  - Y.M.C.A. now FAILS: there's no in-point evidence until an IG/TikTok audio-page check.
