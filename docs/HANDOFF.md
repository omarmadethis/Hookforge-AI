# Hookforge v3: HANDOFF (read this first)
Last updated: 2026-10-18 8:32 PM PT · Owner: lead architect (Grok Bot executor). This document is meant to let any AI or engineer continue the build mid-way.

## Mission
Omar sends one line ("make a 3-2-1 video for X", "make X type of video for X"). Hookforge returns a finished, maximally viral reel: brief → format pick → start-frame and packed-generation prompts → auto-edit → QA gate → backtest gate. After that, it runs autonomously at 5 videos/day per product with a 20 % experiment budget, and it learns from every generation and posted result. Bar: clearly better than the team's current output. Every rule cites reels and data.

## Authority order (when sources conflict)
1. Omar's explicit decisions (`/workspace/team/omar_decisions.md`, DECISIONS D1–D16 + D17–D31)
2. Omar's own rules in his words (`learning/rules_core.csv`, verified 30/30 against his transcripts)
3. Measured data (corpus, Insights, Shopify, CapCut drafts), recency-weighted for trends (D28)
4. Team reports, playbook v2, hf_match prompt analysis
5. External/competitor evidence

## Hard rules (enforced in code: `engine/hookforge/config.py`)
- Seedance 2.5 only for video and GPT Image 2 only for stills. No Kling, no end frames (D22).
- The hook is its own 1080p gen. Every other gen is 720p and packs 2 shots with a straight hard cut at about 2 s. All gens are ≤5 s, 4 s standard. Hooks are ≤5 s (D2, D20, D25).
- EVERY prompt (video and still) ends with the verbatim iPhone 12 suffix. Stills use `iPhone photo of … Sharp, clean, realistic phone photo.` + suffix (D32, supersedes D17).
- Always generate native ambient audio. Never burn captions or music into generations. Variants get fresh audio (D23).
- US flags in every clip. The top unit of any display is lit or working. Stores look like Target/Walmart with no logos. The JK flip stays on fake-retailer hooks (D24, D26, D4).
- Auto re-roll ONLY for absurd failures at ≥0.9 confidence, max 1 per shot: product missing/deformed/wrong, wrong colour, mangled person, unrelated scene, broken hard cut, unusable hook. Minor flaws ship and are logged. Every re-roll is logged with reason and cost. Print credits per video (100–175; variants ≤100) (D33, D18).
- No Higgsfield spend, posting or FB/IG actions without Omar's explicit approval (D9).
- CTA wording is `SAY "<KEYWORD>"`, never COMMENT (D5).
- Ad Multiplier means the whole video. Background and character swaps happen only in Ad Multiplier mode (D21).
- No race/ethnicity casting and no slurs: `sanitize_casting` + a QA block (D27).
- "Don't show this to…" on decor is experiment-only; prefer then-vs-now and POV on decor (D19, pending Omar).

## Freshness (D28 FINAL): one knob, `config.RECENCY`
- **Own data never decays.** Our own reels (all pages), CapCut drafts, prompts, Insights and Shopify all keep full weight regardless of age.
- **External reels are recency-weighted.** This covers the research library tiers and external/competitor reels: full weight for ≤14 days, then exponential decay (τ=7 d), with a 0.05 floor (90+ days = weak prior). Call `recency_weight(age, source)`.
- **No freshness requirement when own data supports a trend.** A trend rule backed by our own data needs no fresh row. Only rules backed solely by external reels carry a fresh/aging/prior-only label.

## Reference library tiers (D31)

- **`inclusion_rule` (D34)** sits on every library row and sidecar. `14d_1m` = last 14 days, 1M+ views, weighted by `config.RECENCY`. `90d_20m` = last 90 days, 20M+ views (mega viral), exempt from decay with weight `config.INCLUSION_WEIGHT["90d_20m"]` (0.95). Call `recency_weight(age, source, inclusion_rule=row.inclusion_rule)`.
- `research/reference_library/index.csv` holds 1M+ reels from the last 14 days. The selector prefers these for recreation and trend picks.
- `archive.csv` holds older 1M+ reels. `near_misses.csv` holds 300K–1M reels inside the window.
- The backtester uses all tiers, recency-weighted.

## Architecture map (re-audited against the code 2026-10-20 ~9:45 AM PT, D84)
| path | what | status |
|---|---|---|
| `engine/hookforge/config.py` | constants, standing rules, D32 suffix, casting sanitizer | done |
| `engine/hookforge/planner.py` + `product_poc.py` | brief → plan; per-product POC defaults (config/poc_defaults.json) | done (POC defaults only for PurrVenture so far) |
| `engine/hookforge/gates.py` | G1–G22 plan gates, quote, spend ledger | done |
| `engine/hookforge/qa.py`, `pacing.py`, `splice_detect.py`, `repeat_detect.py`, `frame_qa.py` | final/variant checks, pacing, splice, repeat, frame self-QA | done |
| `engine/hookforge/ref_gate.py` + `refs_lib.py` | F88 hard ref gate; per-product ref library refs/<slug>/manifest.json, auto-attached in planner.d75 | done; cast missing for every product except PurrVenture |
| `engine/hookforge/runner.py` | live order runner: approval + credit cap, call cursor, cost/ledger, 1 auto re-roll | partial: resumable via run.json cursor; no job polling/timeout/backoff daemon |
| `engine/hookforge/autoedit.py`, `songlay.py`, `iphone_grade.py`, `omar_style.py` | edit, song from frame 0, grade, compare vs Omar CapCut stats | done |
| `engine/hookforge/deliver.py` | zero-metadata whitelist stage/verify (only exit path) | done |
| `engine/hookforge/capcut_export.py` | plan → editable CapCut draft | partial: write only; Omar-edit read-back = `engine/backtest/capcut_drafts.py` batch, not a loop |
| `engine/hookforge/publish.py` + `posting.py` | Buffer payload prep, Omar-approval-only | partial: no public video host; auto-post disabled (D41/D78) |
| `engine/hookforge/results_feed.py`, `sales_attribution.py`, `tracked_links.py` | results feed (CSV inbox / META_TOKEN), UTM links, Shopify UTM sales | partial: code done; no data flowing (no exports / token / UTM in live captions) |
| `engine/hookforge/learn.py` | arms, 5/day schedule, experiments, update | partial: plans a day on demand; no scheduler (automation/ empty, no cron) |
| `engine/hookforge/variants.py`, planner hook_variants/covers | A/B variants (FB caption/thumbnail test, IG Trial Reels) | partial: variants produced; tests run by hand, winners not logged automatically |
| `engine/backtest/*` | corpus, CapCut drafts, backtester + model | done |
| `analytics/` | dashboard, insights ingest | done (stale data) |
| `automation/` | 5/day runner | MISSING (empty folder) |

## How to run (from `engine/`)
```
python3 -m backtest.corpus            # rebuild corpus (private + public)
python3 -m backtest.measure_corpus --procs 3   # measure all videos (cached by file hash)
python3 -m backtest.capcut_drafts     # CapCut drafts → private/edits/*.csv + data/capcut_stats.json
python3 -m backtest.mac_evidence      # Mac prompts/rules → private/evidence + learning/rules_core.csv
```
Deps: `requirements.txt`, ffmpeg. pyJianYingDraft lives only in `/workspace/.venvs/capcut` (used as a validator).

## Key data findings so far (CapCut drafts, n=110; 35 joined to posted reels)
- Edit rhythm does NOT separate winners from flops. Post-hook shot median is 1.38 s for winners and 1.44 s for flops. First cut is 2.37 s vs 2.70 s and length 12.2 s vs 13.0 s, both weak. Hook/format and distribution are the levers (consistent with the body REPORT).
- Text sits 19 % from the top, size 15, one persistent card. Then-vs-now switches "Vs.." on the first body cut.
- Song sections (draft medians):
  - Last Christmas MV 170.2 s (≈2:50)
  - Mariah AIWFCIY Make-My-Wish edit 49.6 s
  - Bublé ITBTLALC 31.6 s
  - Holly Jolly 0.1 s
  - Let It Snow MV 0.87 s
  - Boombastic 21.6 s
  - Free Bird ≈14 s
- 38 % of drafts use a speed change.

## Known weaknesses / open questions
- HJ Insights retention is missing (audit ask #1). The model is trained on views, which are mostly luck plus page burst.
- Only 18 of 203 draft hf clips have prompts in local logs. Read-only Higgsfield prompt lookup could fill more.
- Omar to confirm: D19 (decor don't-show), the D28 scope, and the CapCut Mac open test.
- The box is shared and heavily loaded, so measurement is slow.

## Checkpoints
`BUILD_LOG.md` (phase log), `CHANGELOG.md`, `DECISIONS.md`, `docs/REVIEWS.md`, `docs/INTERFACES.md`, `docs/CAPCUT_EXPORT.md`. Mirror: `/cursor/stores/store-17dde83b-…/hookforge_backup/`.


## Phase B status (2026-10-18)
- Run: `cd engine && python3 -m backtest.model` (background, about 3 min on the loaded box) → engine/backtest/data/validation.json. `python3 -m backtest.backtest` → kNN validation. `backtest.run(feat)` → per-video report/verdict.
- Gate policy D35: band is informational; BLOCK on hard rules; FIX on deviations.
- Posting time: `python3 -m analysis.posting_time` after every new post (learning loop hook TODO in learning/update.py) → learning/posting_windows.json + rules_learned.csv (Holm, D36). Scheduler: best window per page, 20% explore slots.
- CapCut test draft for Omar: out/capcut_test/HF_TEST_01/ (+ .tgz, README) → copy to /Users/omar/Movies/CapCut/User Data/Projects/com.lveditor.draft/HF_TEST_01

## Phase D — production engine (2026-10-18, core path verified on dry runs)
**One-liner:** `cd engine && python3 -m hookforge.pipeline "3-2-1 video for the Grinch robe"` → out/dryrun/<slug>/ {PLAN.md, plan.json, animatic.mp4, covers/, preflight/, media_qa.json, capcut/DRY_*/}. Add `--force` to override a REJECT (experiment only) and `--no-render` to skip ffmpeg.
**Path:** planner.parse_brief → profiles.load (product world, D37) → fit.assess (REJECT/WARN plus why-this-format; own track record first) → worlds.ADAPTATIONS (format re-staged in the world) → body packing (bodies.py; 1080p hook + 3×720p packed gens, HARD CUT ~2 s) → prompts.py (iPhone 12 suffix on EVERY prompt, US flag, casting sanitiser, placeholder check) → hook + CapCut card texts from the own winner's draft → hook_variants (3–4) + covers (2–4) → music.select (proven + niche/energy, profile bans/preferences, D38) → proven caption → season phase + delivery-claim guard → posting windows → credits (174/175, D40) → qa.plan_checks + qa.logic_check (world) → backtest gate (D35) → CapCut draft + animatic + media QA.
**Media QA for live runs:** qa.raw_gen_checks(clip, product_img_dir) per gen (contact sheet, OCR, packed-cut assert, CLIP fidelity) → qa.reroll_decision (D33, logged to learning/reroll_log.csv) → autoedit.final_cmd → qa.final_checks (D7 loudness, 2160×3840, safe zones, C2PA report-only) → qa.originality_gate for recreations/variants.
**Product worlds:** engine/hookforge/worlds.py (curated) + `python3 -m hookforge.profiles` (evidence) → product_profiles/*.json. To add a product, add a WORLDS entry (settings, energy, forbidden settings, copy_forbidden, music bans/preferences, processing/ship days) and rebuild.
**Music:** `python3 -m hookforge.music` → learning/music_library.csv.
**Plug-ins:** plugins.py (style/, psychology/, audience/, voice/). It currently uses style/capcut_text_preset.json (draft); the rest falls back to defaults.
**Learning (E, started):** learning/update.py re-derives corpus → edits → posting_time → music → profiles → arms (+ model/dashboard). `learning/update.py schedule <product>` = 4 core (Thompson) + 1 experiment slot with posting windows.
**Deferred by Omar's priority:** failure memory (D42), page registry/variants/auto-post wiring beyond stubs (D41), ops stubs, dashboard panels, public package (tools/package_public.py written, not run).
**Known limits:** model is weak (D35); credits inferred (D40); animatic uses the evidence reel as mock footage (its own burned text shows underneath; emojis stripped in preview only); processing/ship days unknown, so no delivery claims; PDQ/fidelity thresholds are PROPOSED; Brick Hood 3-2-1 is a transfer (no own proof), so it goes in an experiment slot.

## Audience-targeting layer (audience/, 2026-10-18 ~9:40 PM PT)
- Start at `audience/README.md`. Rules are in `audience/audience_rules.csv` (rules_core format; proven / supported / hypothesis). Proposals are P-AUD-1..8 in DECISIONS.md.
- **Proven:** US converts ~10× better per session than non-target regions (own Shopify). **Documented:** the IG per-country engagement signal, FB Page country restriction and IG Collabs. **Supported (n=1):** a US creator drives US audience. Everything else is a hypothesis with an A/B plan in `audience/EXPERIMENTS.md`.
- Next step once `audience/ig_reel_audience.csv` exists: `nice -n 19 python3 audience/tools/us_share_drivers.py`. Then fold the results into audience_rules.csv A03–A08 and re-prioritize EXP-AUD-*.
- Integration proposals (not yet wired): tier1_score as backtest INFO; visual_cues snippets in the prompt builder; overlay linter WARN on the AV-list; `region_skew` column in music_library; `pct_us/pct_tier1` in experiments.csv and the ledger.

## Customer-voice layer (`voice/`, 2026-10-18 PT)
- Read `voice/README.md`, then `voice/INSIGHTS.md` (§0 = critical business alerts: robe fulfilment mismatch, MerryFire vs the CPSC liquid-fuel alert, duplicated testimonials, AI call-outs).
- Data: `voice/comments.csv` (8,475 de-identified competitor comments, 47 videos), `voice/support_themes.csv` (Gmail support inbox aggregated, 164 customer threads), `voice/engagement_correlation.csv`.
- Engine hook: `voice/voice_rules.csv` (V01–V16, rules_core format + `engine_slot`). D47–D50 are PROPOSED.
- Next: run `voice/browser_queue.csv` (115 rows: 72 own reels by views, 5 competitor reels, 38 discovery searches; READ ONLY; capture spec in README), drop the captures in `voice/inbox/`, then `python3 voice/pipeline.py && python3 voice/report.py`.
- Re-run: `voice/README.md` § Run. Blocked from the box: YouTube, Reddit.

### Phase D additions after 21:30 PT (D44–D49)
- **Final export (D44, Omar):** `autoedit.clean_export(src, out)` re-encodes with all metadata/C2PA stripped and asserts preflight.provenance is clean. qa.final_checks BLOCKs if provenance remains. Tested on a real HF clip: c2pa/IPTC/trainedAlgorithmicMedia True → all False.
- **Recreate workhorse (D45):** recreate.p1 = the d7bf7598 family (165K). recreate.check enforces MP2-5/6/7. ONE roll by default (D33 wins over MP2-1). The robe plans carry it as `gens[0].alt_recreate`.
- **Audience (D46):** tier-1 advisory score in the backtest report; US cue snippets in prompts (world-filtered); region_skew in music_library; explicit PT everywhere (the box clock is BST).
- **Voice (D50 supersedes D47–D48):** voice rules are reference data only; NO end card; KEEP the D49 AI-doubt PROOF shot + AI-tells log.
- **Safety hold removed (D51, Omar 21:50):** MerryFire world/body restored (pour + ignition, indoor). There are no claims blocks in the engine. Only the D49 AI-doubt proof shot + AI-tells log remain from the voice layer.
- **Packed-cut assert validation** (engine/backtest/data/packed_cut_validation.json): 13/15 ledger-packed Seedance clips pass (87%). 5/15 "unpacked" clips also show exactly one cut in 1.5–2.5 s, so the packed flag in the ledger is incomplete or the detector has false positives. Calibrate before letting it auto-re-roll.

---
## Merged 2026-10-20 5:22 PM PT: sections that existed only in the old docs/HANDOFF.md copy (verbatim)

### Style/psych layer (2026-10-18 ~10 PM PT)
style.py (hard: Brick Hood hook setting; FIX: hands-on/face-to-camera, emoji count), psych.py (advisory), render_text cards in animatics, STYLE_GUIDE §5 song in-points. D52: covered-reveal hooks allowed - waiting on the style team's re-coded covered-hook reels before PS02 numbers mean anything. Join fixes: HJ-13 and MJIG-04 unjoined (backtest model features for those reels changed; retrain model before next report).

### 2026-10-18 ~11:00 PM PT
D54–D58 are done. New files:
- engine/hookforge/reels_db.py, vision_judge.py
- analytics/public_scrub.py
- engine/tests/test_live_gate.py
- FIRST_LIVE_RUN.md
- learning/vision/ (banks + calibration; private)

Live is disabled: `config.LIVE['enabled'] = False`, and there are no approval files.

Re-run the vision calibration with `python3 -c "from hookforge import vision_judge as V; V.calibrate()"`. It needs the features proxies, which are read-only.

### 2026-10-18 ~10:40 PM PT
Run: `cd engine && python3 -m tests.test_core_path` and `python3 -m tests.test_c2pa_strip`; `python3 learning/update.py` (loop + dashboard); `python3 learning/update.py day <product>` (next-day package, out/daily/). Dry runs: out/dryrun/ (9 briefs incl. 4 covered-reveal). Open: data/features hookforge.db schema adapter; live runner submission (intentionally absent); posting backend disabled; D33 vision judge; mug F01 has no PROOF shot and a 4-emoji fallback hook (mug not in the dry-run set).

## Final-export hygiene (2026-10-19)
- Every final ends in `autoedit.clean_export`. Any later fix (audio re-level etc.) must use `autoedit.relevel_audio` / `autoedit.clean_remux`.
- `qa.final_checks(path, timeline=...)` BLOCKs: repeated/looped footage (repeat_detect), jump cuts inside one take (splice_detect, needs timeline), and any Encoder/Lavf/Lavc/libx26x/C2PA metadata.

## Delivery chokepoint — deliver.py (D44d, 2026-10-19). MANDATORY
- Every file that leaves the box (Drive UploadFile, CopyFromBox, attachments) goes through `engine/hookforge/deliver.py` first:
  `p = deliver.stage(src, "<Drive name>")`, then `deliver.verify_staged(p)`, then upload **only** `p`, which lives in `out/deliver/`.
  CLI: `cd engine && python3 -m hookforge.deliver <file> "<name>"` (exit 2 = REFUSED).
- The scan uses a whitelist: exiftool -a -G1 -ee fields, the MP4 box tree, PNG chunks and JPEG segments. It also scans the raw bytes for
  c2pa/jumbf/Lavf/Lavc/x264/x265/ffmpeg/Higgsfield/Seedance/OpenAI/XMP/AI-generator strings. Anything outside the whitelist is refused. There is no override flag.
- stage() auto-sanitizes: lossless remux plus blanking of the encoder SEI/Lavc banners for video, and a pixel-only rewrite for PNG/JPG. The result must still pass the scan.
- Raw start frames (Higgsfield PNGs) carry C2PA plus `Hf-job-id`. They can only leave through stage(), which rewrites them pixel-only.
- qa.final_checks runs the same scan as a BLOCK. Tests: engine/tests/test_deliver.py.

## Architecture map (auto-generated, D116 — 2026-10-20)

Flow: `concept_lab.daily` → `planner` (profile from `profiles`/`worlds`) → `fit.assess` → `gates.run_all` (G1–G25; G24 world, G25 `political_lint`) → `runner.preflight`/`build_calls` (quote = credits) → `approval_queue` (learning/approval_queue) → [Omar approves; spend] → CapCut draft → caption (`fb_caption`/`caption_variants`) → `routing.route` (config/buffer_routing.json) → `publish.build_payload` (draft only). `e2e_dryrun.run` exercises this whole chain without spending or calling Buffer. Files leave the box only through `deliver.stage`/`verify_staged`.

| Module | Purpose | Public functions | Internal deps |
|---|---|---|---|
| `credit_ledger` | D120 credit ledger vs Omar-approved caps; precheck before each runner call | spent, daily, status, precheck, backfill | gates |
| `perf_feedback` | D119 Buffer/Meta stats → ab_log → per-product hook/caption/song weights | ingest, reweight, weight, from_buffer, from_meta | products, ab_log |
| `products` | D117 active/retired registry (config/products.json) | active, is_active, retired, require_active | - |
| `reroll_planner` | D122 cheapest fix for AI-look warnings (retrim/take swap/frame swap/reroll) → approval queue | propose, from_review, queue, locate | ai_look, approval_queue, runner |
| `approval_digest` | D124 one-page HTML digest of pending approvals with cost + Yes/No | build, pending_items | approval_queue, products, credit_ledger |
| `content_calendar` | D127 weekly per-page drafts calendar (cadence, rotation, midterms ramp, account caps) | week, weight | routing, products, approval_queue, e2e_dryrun |
| `spend_watch` | D129 hourly read-only unlogged-spend flag file | check, parse | credit_ledger |
| `render_queue` | D130 bind each calendar slot to an approved video or flag NEEDS_VIDEO | build, schedulable | publish, deliver, approval_queue |
| `hook_variants` | D132 3 hooks + 3 captions per concept, <= 8 words, gated | run, for_concept, gate, candidates | products, approval_queue, political_lint, worlds |
| `ref_miner` | D134 cross-product transfer ranking of hooks/sounds/hashtags/cuts → rank boost | build, boost, hooks, sounds, hashtags, cuts | products, worlds, political_lint |
| `post_watch` | D136 post-publish caption-swap watcher (dry run) | dry_run, current_pages | fb_caption, routing, products |
| `ab_log` | D91 #4 A/B VARIANT LOG tied to results_feed (learning/results/outcomes.csv, keyed by video_id) and sales_attribution | log_variant, results | - |
| `ai_look` | D75 AI-look QA reviewer. Samples frames per shot and scores AI artifacts 0..1: | frames, text_gibberish, temporal_break, skin_texture, review_shot, review | - |
| `approval_queue` | D106 approval queue for GENERATION plans (concepts, redos). Items live in learning/approval_queue/<id>.json with | queue, pending | - |
| `asr` | Word-level ASR helper (faster-whisper, decoded via ffmpeg to avoid the av version clash). | pcm, words | - |
| `audience_fit` | D62 AUDIENCE-FIT stage (Omar 2026-10-19: "song matching, emoji matching, caption matching it all needs to fit in that | glob_rules, slugs, slug_for, load, check_song, song_rank | - |
| `autoedit` | ffmpeg auto-edit. animatic(): mock edit from existing clips (no generation) with shot labels + text cards at the | animatic_cmd, final_cmd, clean_export_cmd, clean_export, clean_remux, relevel_audio | - |
| `bodies` | Body formulas per product category, with Omar's packing rule baked in. | body_for, validate_body | - |
| `capcut_export` | Export a Hookforge edit plan as an editable CapCut (Mac, desktop 9.x) draft project. | export, verify | - |
| `capcut_learn` | D91 #3 CAPCUT LEARNING LOOP: diff Omar's edited CapCut draft against the draft we exported, log the differences, | read, diff, learned | - |
| `caption_variants` | D101 per-page caption variants for products routed to >= 2 pages (routing.py). Every variant is POC-backed: | candidates, build, for_page | - |
| `concept_lab` | D106 autonomous concept testing (DRY RUN). Daily: one NEW concept per product = the 20 % innovation slot | candidates, propose, daily, poc_strength, season_fit, page_gap | - |
| `config` | Hookforge v3 constants. Standing decisions live here so every module enforces them. | still_prompt, ensure_suffix, recency_weight, freshness_label, sanitize_casting, casting_violations | - |
| `cues` | US/tier-1 visual cue snippets from audience/visual_cues.md (hypothesis-level geo effect; EXP-AUD-07). | snippets, for_world | - |
| `deliver` | D44d - the ONLY way a file may leave the box (Drive upload, CopyFromBox, attachments). | c2pa_manifests, scan, sanitize, stage, verify_staged, preview | autoedit |
| `e2e_dryrun` | D115 end-to-end DRY RUN for every product: concept -> plan -> gates -> quote -> CapCut draft -> post caption -> | capcut, caption_for, run_product, run | - |
| `edit_rules` | Editor defaults + linter from learning/raw_vs_final/EDIT_RULES.md (35 Omar CapCut drafts vs 39 posted reels). | default_timeline, lint | - |
| `fb_caption` | D93 - Facebook POST caption module (the post text, NOT the on-screen text). | product_key, classify, split_caption, pattern_of, build_library, product_url | - |
| `fit` | Product x format fit (D37). Every plan passes through assess(); the brief parser warns on WEAK and refuses REJECT | assess, rank | - |
| `format_defaults` | Built-in machine format specs (engine fallback). formats/formats.json (format-library workstream) overrides | get | - |
| `frame_qa` | F90 / D81 strict frame self-QA (Omar 2026-10-20 9:27 AM: "these should be caught before he sees anything"). | load, record, require_all_pass, build_sheet | - |
| `gates` | - | R, words, g1_song, g2_hook, g3_profiles, is_hook_gen | - |
| `gen_failures` | Generation failure memory (D42, wired 2026-10-18 ~10:10 PM PT; Omar's 10:00 PM go-ahead). | classify, backfill, learn_rules, rules, lint, log_attempt | - |
| `graph_caption` | D107 Graph API caption edit for a PUBLISHED FB reel (Buffer cannot edit sent posts). APPROVAL-GATED. | plan, execute | - |
| `iphone_grade` | D75 iPhone-texture grade: applied to AI shots ONLY (never real footage, never text cards), kept subtle. | vf, should_grade, grade, before_after | - |
| `learn` | Learning loop (Phase E). update() re-derives everything after new posts / drafts / gens: | arms, schedule, build_day, evaluate_experiments, experiments_status, update | - |
| `logic` | LOGIC step (D61, Omar 2026-10-19 post-mortem of mg-tvn-001): every prompt must pass a believability check | camera_allowed, lint_prompt, designs, lint_plan, facing_camera, cuts | - |
| `ly_season` | ly_season (PD-G5 -> D88): last season's holiday benchmark tier, Nov 1 2025 - Jan 10 2026, 1M+ views. | phase_of, build, prior, blend, load, song_in_point | - |
| `measure` | Measure everything Hookforge can measure on an mp4 (used by QA + backtest). | probe, frames_lowres, detect_cuts, motion_stats, image_stats, audio_stats | - |
| `motion_rules` | D75 motion rules: AI shots look real when the motion is SHORT and SIMPLE (one subject, one action, <=4-6 s, slow camera). | shot_texts, count_actions, lint, simplify_motion | - |
| `music` | Music library (D38): every song must be PROVEN and match niche + energy. | canon, build, load, select | - |
| `omar_style` | D74 OMAR STYLE: edit defaults + "edit vs Omar" QA, learned from his CapCut drafts (learning/editing_style/style.json, | style, hook_speed, card_layout, dialogue_gain_db, compare, timeline_from_final | - |
| `order` | D69 ONE-COMMAND ORDER -> PACKAGE runner.  python3 -m hookforge.order "<one-line order>" [--run-id ID] | research, stage_of, run | - |
| `pacing` | Pacing / timeline gates (Omar 2026-10-19 t2xx: 'that clip lingers way too long for how uninteresting it is'). | p90, infer_roles, hold_violations, near_duplicate_cuts, video_hash, variants_identical | - |
| `pages` | Page registry (D41). private/pages.json (real, gitignored) - public example at config/pages.example.json. | bootstrap, load, pages_for, buffer_pages | - |
| `pipeline` | One-line brief -> plan -> QA (incl. logic check) -> backtest gate -> animatic + CapCut draft (dry run, no generation). | slug, gate_features, md, run | - |
| `planner` | Brief -> plan (Phase D). parse_brief() resolves product + format; plan() builds the full production plan: | parse_brief, hook_variants, cover_frames, plan, d75 | - |
| `plugins` | Plug-in layer for teammate workstreams (D39). Each loader returns the teammate file when it exists AND passes | text_preset, emojis, shot_grammar, psych_codebook, provenance, audience | - |
| `poc_library` | D69 POC LIBRARY: searchable index of proven hooks, songs (with in-points), formats and captions, each with views + source. | strength, fmt_of, build, trend_songs, alive, rank_songs | - |
| `political_lint` | D114 political-content safety lint (G25) for political products (trumpglow / patriotglow / trumpglow_projector). | texts, lint_text, check | - |
| `posting` | Auto-posting interface (D41) - DISABLED. Nothing in this module posts. enqueue() writes a scheduled row to | backend, enqueue | - |
| `product_poc` | D84 per-product POC defaults (config/poc_defaults.json). prepare() runs before the planner: syncs the product | load, prepare, apply | - |
| `product_refs` | D75 product-reference module: photoreal product reference shots via GPT Image 2.0 (1 credit/image) FROM the product's own | store_photos, ref_prompt, plan_refs, register, refs_for, attach_to_gen | - |
| `profiles` | Product profiles (D37). build() writes product_profiles/<product>.json = worlds.WORLDS (curated world: settings, | build, load, resolve | - |
| `prompts` | Prompt builder (D32/D33). Fills format + world-adaptation templates with the product profile, packs body shots | fill, with_flag, with_cues, finish, silent, still | - |
| `proof_guard` | D68 proof guard: an audience/product profile may not ban a format/setting or emoji that has proven performance | corpus_products, emoji_proof, setting_proof, niche_categories, omar_banned, audit | - |
| `psych` | Psych codebook scorer (psychology/psych_codebook.csv, PS01-PS19). ADVISORY per D35. PS02 (covered reveal) is an advisory cue/timing check, never a block (D52; style re-code 22:09 PT). | callout_primary, ps02, score | - |
| `publish` | D78 - Buffer posting pipeline (PREPARE ONLY). Nothing here calls Buffer or any network. | build_payload, prepare, prepare_fb, prepare_fb_all, approve_swap, swap_action | - |
| `pv_p2_redo` | D108 PurrVenture P2 payoff redo PLAN (no generation). Payoff shot only: cream Bengal rolling in the black mesh ball, | plan, queue | - |
| `qa` | QA gate (Phase D): plan checks, LOGIC CHECK (product world, D37), music/caption proof (D38), rendered-edit checks, | logic_check, plan_checks, probe, detect_cuts, edit_checks, reroll_decision | ai_look, deliver, find_repeats, find_same_take_splices, gates, omar_style, pacing, repeat_detect, song_start_check, songlay, splice_detect |
| `real_footage` | D75 real-footage reveal shots from /workspace/research/product_footage/<product>/ (supplier clips pulled by Viral Research). | probe, clips, reveal_shot, use_real_reveal, folder, manifest | - |
| `recovery` | D91 #2 RECOVERY for live runs (out/live/<run_id>/run.json). Never resubmits a job that may still be running. | scan, record_refund, retry, resume | - |
| `recreate` | Recreate templates + rules from the members pass 2 (MP2-1..9, docs/evidence_members_pass2.md). | p1, variants, check | - |
| `recreate_mode` | RECREATE mode (D61, the default since Omar's mg-tvn-001 post-mortem, 2026-10-19): | load_spec, merryglow_gens, build, check, plan_sha, side_by_side | - |
| `reels_db` | Shared reel loader over data/hookforge.db (features workstream, owner: data/features worker) + the Phase A corpus. | read_db, merged, load_reels, review, db_is_default | - |
| `ref_gate` | F88 / D80 HARD GATE (Omar 2026-10-20): no image or video generation without product AND cast reference images attached. | check | - |
| `ref_sanity` | D100 ref-sanity: a reference image must actually CONTAIN its subject (CLIP ViT-B-32 laion2b, local cache, no network). | check, label_for, audit | - |
| `refs_lib` | D84 per-product reference library: refs/<slug>/manifest.json (+ clean product/cast copies). | build, build_all, manifest, refs_for, attach | - |
| `repeat_detect` | Detect looped / repeated footage: a frame that matches an earlier NON-adjacent frame | find_repeats | - |
| `results_feed` | #1 RESULTS FEED (D86): per-reel performance -> learning loop. | read_csv_export, parse_fb, parse_ig, fetch_graph, write_snapshot, load_snapshots | - |
| `routing` | D94 Buffer multi-account routing (config/buffer_routing.json). Pure planning: no network, no posting. | cfg, page, page_by_channel, capacity, assert_routable, route | - |
| `runner` | Generation runner front door. EVERY generation goes through this module: the D42 pre-flight linter runs first, then the live path, | preflight, plan_sha, build_calls, check_gate, approval_template, submit | - |
| `sales_attribution` | #5 SALES ATTRIBUTION (D87). READ-ONLY ShopifyQL aggregates only (no orders, no customers, no PII). | check_query, load_attribution, coverage | - |
| `scheduler` | D91 #1 SCHEDULER: at most 5 generation jobs per PT day, inside the credit caps. QUEUE + DISPATCH CHECK ONLY. | plan_cost, spent_on, enqueue, dispatchable, mark | - |
| `season` | Season calendar (gap G5): phase + levers for the posting date, gift cutoff per product, and the delivery-claim guard. | gift_cutoff, phase, claim_problems | - |
| `snapshot_scheduler` | D96 hourly results snapshots for the 10K/hour caption-swap trigger (fb_caption.SWAP_HOUR_GAIN). READ-ONLY. | tick, loop, ensure_running | - |
| `songlay` | D64 SONG LAY-IN (Omar 2026-10-19: "final exports always include the chosen song at its proven in-point"). | songs, find_in_point, lay_song, ensure_song, lay_song, onset_s | - |
| `speech_gates` | D72 speech QA gates (Omar 2026-10-19 9:34 PM PT). | dialogue_complete, audibility | - |
| `splice_detect` | Gate 2: jump cut inside one take = two ADJACENT timeline segments from the same source clip id, | find_same_take_splices | - |
| `style` | Style layer (style/ workstream, accepted 2026-10-18): text scale by line length, emoji rules, shot-grammar checks. | text_scale, emoji_rules, emoji_problems, ensure_hands_on, shot_problems | - |
| `taxonomy` | Format taxonomy + psychology coding. One mapping used everywhere (corpus, backtest, briefs, learning). | format_of, code_psych, norm_category | - |
| `telemetry` | Shared-learning client (DISABLED by default). See docs/SHARED_LEARNING_PLAN.md. | client_id, scrub_text, build_event, send | - |
| `textcards` | Hookforge text cards with Apple iOS emoji (D61, Omar 2026-10-19: "emojis must be Apple iOS emojis"). | apple_png, render_card, cards_for, check_cards, card_lines, fit_card | - |
| `tracked_links` | #5 per-reel tracked links (D87). utm_source=fb|ig, utm_medium=social, utm_campaign=<product>, utm_content=<video_id>. | tracked_url, fill_caption | - |
| `variants` | Per-page originality (D41). One master plan -> N page variants that are original enough to avoid Meta's | similarity, make_variants, file_hash | - |
| `vision_judge` | D33 absurd-failure JUDGE (Omar 2026-10-18 10:35 PM PT: "use your own vision QA (CLIP fidelity plus contact-sheet checks) as the | build_refs, signals, pixel_checks, calibrate, per_product, recalibrate | - |
| `worlds` | PRODUCT WORLD layer (D37, Omar 2026-10-18): hand-curated world facts per product, from Omar's transcripts | world_forbidden, world_conflicts | - |

Active products (D131): jollyglow_curtain, trumpglow, purrventure_carrier. Retired (full reference corpus, no new content): grinch_robe, heatjams, cozyjams, brickhood_mask, merryglow_lights, merryfire, grinchmelt_mug, minionmask.
Feedback + spend: published post stats → `perf_feedback.ingest` → `reweight` → weights used by rank/captions/music. Every Higgsfield call → `credit_ledger.precheck` (in runner.next_call) → `gates.ledger_add`.

Caps: config/credit_caps.json (chat-approved, incl. group caps); closed runs refuse new spend. Digest: `python3 -m hookforge.approval_digest` → analytics/approval_digest.html.

Spend logging: all Higgsfield submits go through `credit_ledger.log_job` (runner does it); `credit_ledger.reconcile` checks the Higgsfield transactions feed for spend outside the runner. Runs survive crashes: atomic run.json, in-flight submit marker, `recovery.resume`.

Calendar → render_queue (no slot schedulable without its approved video). Hourly spend watch: docs/HOURLY_SPEND_WATCH.md. Caches: audience YAML, gen_failures rules, placeholder slates (.cache/slates).

Weekly: `concept_lab.weekly()` → fewest videos for all calendar slots, quoted, one weekly_batch queue item.

Open items: trumpglow + purrventure product URLs are PLACEHOLDER (blocks caption swaps); 298 cr of unledgered new-account spend today (D126);  SAY "VOTE" PL5 warning near midterms; branding v2 spend not in the ledger.

---
## Merged 2026-10-20: sections that existed only in the old engine/HANDOFF.md copy (verbatim, newest)

### 2026-10-20 batch (D137–D140)
PL6 lint, listing block, distinct caption text, real still price (200/video), lean_plan.py (1,227 / 759 vs 2,600 standard). Open items: 175 innovation budget < 200/concept (Omar's call); 298.15 cr of unlogged spend; trumpglow and purrventure product URLs are placeholders; SAY "VOTE" PL5 warning.
### 2026-10-20 batch (D141–D144)
P2 redo stays archived. Lean plan is 1080p-only at 1,227 credits with the near-duplicate edit gate (worst 40%). Daily and weekly logic auto-recommend lean. JollyGlow caption swapped. Runner support for lean edits (body trims and order) is still needed before a live run.
### 2026-10-20 batch (D145–D148)
Lean editor is real: lean_edit plus runner.build_calls_lean and runner.assemble_lean, tested on the local JollyGlow clips (out/lean_test). JollyGlow F06 hook = "POV: the whole street is JEALOUS of your house..". Reveal check at 1.5 s. SAY "LIGHTS" on every JollyGlow caption.
Caveat: the reveal detector finds hard cuts and flashes. Steady "after" footage returns None and gets flagged for a human look.
### 2026-10-20 batch (D149–D152)
8-word hook hard rule with no exceptions. Slow-reveal ramp detector. scripts/lean_dry_render.py (trumpglow + purrventure pass). Box cleanup logged in out/CLEANUP_2026-10-20.txt.
### 2026-10-20 batch (D153–D155)
- One command: `cd engine && PYTHONPATH=. python3 -m hookforge.regen`.
- Buffer preflight results: learning/buffer_preflight/<week>.json (20/20 pass the schema).
- Lean dry-render summary: docs/LEAN_DRY_RENDER_2026-10-20.md.

### 2026-10-20 5:30 PM PT (D156–D160)
- Start here: docs/RESUME.md (generated), then run automation/ensure.sh and `python3 -m hookforge.regen`.
- HANDOFF and DECISIONS live only in docs/.
- Retro approval records: purrventure_3videos, purrventure_branding_v2, purrventure_p2_addshot.
- Local git commit is in place. Not pushed: waiting for GitHub auth, and the repo should be private.
- D161: the spend watch flags only Hookforge-model spend that the ledger doesn't cover. External spend is reported per model.
- D162: CI is .github/workflows/test.yml, which runs `pytest -m "not needs_data"`.
- D163: `python3 automation/restore_assets.py [--drive-index idx.json]` writes a dry-run restore plan only.
