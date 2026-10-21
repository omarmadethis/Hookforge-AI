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
