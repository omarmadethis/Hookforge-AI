# Hookforge GAP AUDIT (gap hunter): what nobody has asked for yet
2026-10-18, ~9:40 PM PT. Scope: the whole pipeline, from a one-line order to the posted video to learning from results.
**Ranking:** production path first (parent steering at 9:25 PM PT), then impact × effort. Impact and effort are scored 1–5, and the score is impact²/effort.
**Rules followed:** no Higgsfield spend, no posting, read-only on FB/IG/Shopify, no PII, no messages sent. Box work was kept light because the production engine has priority.

Status key: **CLOSED** = installed or prototyped by me · **HAND** = recommended owner · **OMAR** = needs Omar

## Summary: top 10
| # | Gap (stage) | Impact | Effort | Status | Owner |
|---|---|---|---|---|---|
| G1 | No automated absurd-failure QA: no vision pass, no product-fidelity check, no hard-cut verification on packed gens (QA) | 5 | 2 | CLOSED (prototype tools) → HAND | architect (qa.py) |
| G2 | No originality / duplicate-risk gate for recreations, Ad Multiplier variants, cross-page reposts (QA, distribution) | 5 | 2 | CLOSED (Meta PDQ installed + checker) → HAND | architect |
| G3 | AI-provenance metadata and Meta's AI-disclosure rule aren't handled at all (posting, compliance) | 5 | 1 | evidence gathered → OMAR decision | Omar + architect |
| G4 | One hook and no cover per video, and no use of the native A/B tools (FB caption/thumbnail test, IG Trial Reels) (script, posting, learning) | 5 | 2 | HAND | architect (planner) + style/psych |
| G5 | No seasonality/calendar logic for Q4 (Black Friday, shipping cutoff, post-Christmas pivot). The 14-day freshness rule also throws away last year's Q4 analogs (planning, references) | 5 | 2 | CLOSED (calendar JSON) → HAND | architect + research |
| G6 | Engagement-bait and caption/hashtag rules are incomplete (captions/CTA) | 4 | 1 | HAND | architect (linter) + style/psych |
| G7 | Per-reel sales are allocations, not attribution (analytics) | 4 | 1 | HAND (no access needed) | architect (caption builder) + analytics |
| G8 | No final-render preflight: loudness (D7), aspect, text safe zones, burned-in text check (export QA) | 4 | 1 | CLOSED (preflight.py) → HAND | architect |
| G9 | No product fatigue / lifecycle trigger (format choice, learning) | 4 | 2 | CLOSED (ruptures installed) → HAND | architect Phase E + analytics |
| G10 | Cost actuals, job failure recovery and resumable runs are missing for 5/day autonomy (generation ops) | 4 | 3 | HAND | architect Phase F |

---
## Production path (order → finished video)

### G1. Absurd-failure QA (vision pass + product fidelity + hard-cut check). Score 12.5
- **Evidence:**
  - D33 defines the auto re-roll triggers: product missing, deformed or wrong colour; mangled person; unrelated scene; broken hard cut. `engine/hookforge/qa.py` doesn't exist yet (HANDOFF lists it as NEXT).
  - PySceneDetect is installed but not wired in. The capability audit records that the ad-hoc `scene>0.25` detector missed the inner cuts behind the Oct 2 Ad Multiplier failure (~368 credits).
  - No check compares generated frames with the real product photos, although they're on the box (`/workspace/products/images/<product>/`, 6 products).
- **Fix:**
  1. `tools/preflight/preflight.py` makes a timestamped **contact sheet** (a frame every 0.5 s). The agent's own vision reviews it against a fixed D33 rubric: hands/limbs, product present and on-model, colour, scene logic, US flag, top display unit lit. It returns `{shot, failure, confidence}`. Only ≥0.9 absurd failures re-roll.
  2. `tools/preflight/product_fidelity.py` computes a CLIP similarity per 0.5 s between frames and the product reference photos, using open_clip ViT-B-32, which is already cached (no download). Low-score shots go to the top of the vision pass. It isn't a BLOCK until it's calibrated on our own reels.
  3. Hard cut: run PySceneDetect `AdaptiveDetector` on every packed gen and assert exactly one cut in 1.5–2.5 s (D2/D20) before the clip enters the edit.
- **Tools:** PySceneDetect 0.7.2 (installed), open_clip (installed, weights cached), agent vision via Read on the PNG. MediaPipe Hands was considered and skipped: hand *detection* doesn't detect *mangled* hands reliably, so the vision rubric is the honest tool.
- **Status:** CLOSED as a prototype (scripts syntax-checked; the full validation run was stopped when CPU was handed to the engine). **HAND → architect:** call these from qa.py, then calibrate the fidelity thresholds on the BH/MG/HJ own reels vs. other-product reels (about 5 min of CPU when the box is free).

### G2. Originality / duplicate-risk gate. Score 12.5
- **Evidence:**
  - Meta, July 14 2025 (creators.facebook.com/blog/combating-unoriginal-content; TechCrunch, The Verge): "When Facebook detects duplicate videos, it will reduce the distribution of the copies". Repeat offenders lose distribution page-wide.
  - Own data: a repost of the 6.6M robe reel did 2.2K (formats/INDEX.md).
  - Omar's rule R22 (variants change enough to avoid duplicate detection) has no measurement behind it.
  - The same file is cross-posted across pages (FB/IG pairs in the corpus).
- **Fix:**
  - `tools/preflight/originality.py` re-implements Meta's published video matching (vPDQ = PDQ per frame, Hamming ≤31, quality ≥50) with **Meta's own open-source PDQ** (`pdqhash`, facebook/ThreatExchange). It reports % of frames matched in both directions.
  - Gate (PROPOSED, PD-G2): a variant, recreate or cross-page repost must score **≤20 %** frame match against the source and our last 60 days of posts. 20–80 % gets a FIX ("change angle, background or character in more shots"). ≥80 % gets a BLOCK. Calibrate on our Ad Multiplier variants: the 64K vs 2.1K vs 1.2K variants (D21) are a ready-made test set.
  - Also hash horizontal flips (`pdqhash.compute_dihedral`). Mirroring isn't originality.
- **Status:** CLOSED as a prototype. `pdqhash` 0.2.8 is built and installed (needed apt `g++` and `python3-dev`, which is small); `ruptures` and `rapidfuzz` are also installed. Validation was stopped by the CPU handover. The test is ready in `/tmp/orig_test.py`: original vs. crop/saturation variant vs. mirror vs. same-product vs. unrelated. **HAND → architect** (QA gate) and the **features DB**, which can store PDQ hashes per reel_key so the "last 60 days" comparison is instant.

### G3. AI-provenance metadata and Meta's disclosure rule. Score 25 (cheap, high stakes), needs OMAR
- **Evidence (measured on the box tonight):**
  - **485 of 508 raw Higgsfield clips** in `/workspace/hf_match/hf_videos` contain a C2PA manifest (`c2pa.claim`, `c2pa.signature`, `digitalSourceType`, `softwareAgent` assertions). Only a run of Oct 7–17 files lacks one.
  - **8 of 60** non-hf finished/library MP4s also still carry C2PA. Some exports keep it; most CapCut re-encodes drop it.
  - Meta (Transparency/newsroom, PAI case study): Meta reads C2PA and IPTC signals to apply the "AI info" label. It **requires** people to use the disclosure tool for organic photorealistic AI video, and "may apply penalties" if they don't.
  - TikTok also auto-labels C2PA content. That matters if cross-posting starts.
- **Gap:** Hookforge has no policy, no per-video record of whether the final file carries provenance, and no record of whether a post got the label. So we can't measure label vs. reach, and we can't show compliance.
- **Fix:**
  - `preflight.py` now reports `provenance{c2pa, iptc_digital_source_type, trained_algorithmic_media}` for every final.
  - The post ledger gets an `ai_label` field (none / auto / self-disclosed).
  - I do **not** recommend stripping metadata to avoid labels: it's against Meta's stated rule and risks page-level penalties.
- **OMAR (one decision):** What is your AI-disclosure policy for posts (self-disclose / don't)? We'll then log label status and measure its effect on reach.

### G4. Hook variants, cover frames and the native A/B tools. Score 12.5
- **Evidence:**
  - `planner._pick_hook()` returns a single hook (the first proven line). No cover/thumbnail is produced (`capcut_export` blanks covers).
  - Facebook's Professional Dashboard lets creators test **up to 4 captions or thumbnails** on a Reel, auto-promotes the winner, and shows a **retention graph and distribution score** (Meta, Nov 2023, ppc.land summary). Availability can vary by account.
  - Instagram **Trial Reels** show a reel to non-followers first and can auto-graduate (Mosseri recommends them for testing).
  - Mosseri's top Reels signals are watch time, likes per reach and **sends per reach** (sends weigh more for non-follower reach).
- **Fix:**
  - The planner emits 3–4 ranked hook texts (proven line + format formula variants + 1 experiment) and 2–4 cover frames: product-fidelity high, hook text legible, face or reaction if present.
  - The posting checklist says: "FB: run caption/thumbnail test with these 4; IG: post experiment slots as Trial Reels".
  - The learning ledger stores which variant won. This turns the 20 % innovation budget into cheap, controlled hook tests that cost **0 extra credits**: the video stays the same and only the text and cover change.
- **HAND → architect** (planner/edit render with N text variants) and **style/psych** (variant hook writing within the proven formulas). Omar's team must tick the test box when posting (manual posting stays, per D9).

### G5. Seasonality calendar and a seasonal-analog evidence tier. Score 12.5
- **Evidence:**
  - Own posts span 2026-09-04 → 10-12, so **zero own Q4 data**. The planner has no date awareness: songs, gift hooks and urgency are the same in October and on Dec 26.
  - The D34 inclusion rules (14d_1m / 90d_20m) exclude **last year's Nov–Dec mega-viral reels**, which are the only real evidence for the Q4 peak.
  - USPS 2026 cutoffs: Ground Advantage Dec 17, Priority Dec 18, Express Dec 19. BFCM is Nov 26–30.
  - Dropship transit time isn't in any product profile, so "arrives before Christmas" claims can't be checked.
- **Fix:**
  - `tools/preflight/season_calendar_2026.json` (CLOSED): events, phases (pre-season → BFCM → peak gift → post-cutoff → post-Christmas), the levers per phase, and a gift-cutoff rule that **forbids delivery claims when ship days are unknown**.
  - PROPOSED **PD-G5:** a new reference tier `ly_season` holds 1M+ reels from the same calendar window last year (±21 days). It's weighted as a prior (e.g. 0.5, never above own data) and used only for phase-specific format and music choices.
- **HAND → architect:** the planner reads the calendar; product profiles get `processing_days` and `ship_days` (from the Shopify delivery profile, read-only). **HAND → research:** build `ly_season` from Nov 1 2025 to Jan 10 2026.

### G6. Engagement-bait and caption/hashtag rules. Score 16
- **Evidence:**
  - Meta's Content Distribution Guidelines demote posts that explicitly ask for likes, shares, comments, tags or votes. `config.BANNED_CTA_WORDS` covers comment, tag, vote and like-if, but **"Send this to…"** sits in F16 and in BH hooks (BH 61.1K "Send this to someone you'd absolutely w…").
  - That's proven in our data and matches IG's sends signal, but it's the share-bait pattern on FB.
  - Hashtags: Instagram capped captions at **5 hashtags** (Dec 18 2025), and Mosseri says hashtags "don't increase your reach".
  - Own data agrees: within HJ, hashtag count (3 vs 4) vs views is Spearman −0.06, p=0.74. The between-page pattern is just page habit (MGS 0 tags, MG 1, HJ 3–4).
- **Fix (PROPOSED PD-G6):**
  - The caption linter enforces ≤5 targeted hashtags, no generic tags (#fyp #reels #explore #viral), and SAY not COMMENT (D5).
  - Keep "Send this to…" (proven) but tag it `share_cta`, track FB vs IG separately, and run 1 experiment pair per month without it.
  - No first-comment strategy: there's no evidence in our data, so it isn't added.
- **HAND → architect** (linter in prompts/check) and **style/psych** (wording that earns sends without commanding them, e.g. recipient-identity hooks).

### G8. Final-render preflight. Score 16
- **Evidence:**
  - D7 (−14 LUFS, TP ≤ −1 dBTP, 2160×3840) is a rule with no check on the finished file.
  - The D30 text position (~19 % from top) sits next to Meta's Reels safe zone (top 14 % / bottom 35 % / sides 6 %, Meta Reels ads guide). Organic UI is lighter, so these are warnings.
  - Generations must have no burned text (D14).
- **Fix:** `preflight.py` checks ebur128 loudness and true peak, the aspect ratio, RapidOCR (PaddleOCR models on ONNX, already installed) text boxes against the safe zones, plus provenance and the contact sheet. Running the same OCR on raw gens catches burned-in text or captions before the edit.
- **Status:** CLOSED as a prototype → **HAND → architect** (run in qa.py on every gen and final). **style/psych** should set the organic safe band from our winners' measured text boxes.

### G10. Cost actuals and failure recovery. Score 5.3
- **Evidence:** the planner prints *estimated* credits only. There's no ledger of actual credits per job, no retry/backoff on failed or queued Higgsfield jobs, and no idempotent `runs/<id>` resume. At 5/day/product, failures will be daily.
- **Fix:**
  - Run state machine: planned → gens_submitted → gens_done → qa → edit → preflight → ready.
  - Every Higgsfield job id, its status and its actual credits go to `learning/ledger.jsonl`.
  - Max 1 auto re-roll (D33), then park with a reason.
  - Daily cost per video and per winner (credits per 50K-view hit) on the dashboard.
- **HAND → architect Phase F** (automation design).

## Learning, analytics and distribution

### G7. Per-reel attribution instead of allocations. Score 16
- **Evidence:** the analytics README labels per-reel sales as allocations. D6 says links aren't a ranking lever, but they're the only way to attribute orders.
- **Fix (PROPOSED PD-G7):** every caption or keyword-DM link carries `?utm_source=fb|ig&utm_medium=reel&utm_campaign=<product>&utm_content=<reel_key>`. Shopify reports sessions and orders by UTM (read-only query), which gives orders/1K per reel and per hook.
- **HAND → architect** (caption builder) + **analytics** (ShopifyQL by utm_content).
- **Optional OMAR (1 line):** which tool answers the SAY "<KEYWORD>" comments (ManyChat or similar)? If it's a DM tool, the UTM goes in the DM link.

### G9. Product fatigue / lifecycle trigger. Score 8
- **Evidence:** the analytics panel plots freshness decay against product age but nothing acts on it. The HJ robe went from 6.6M/2.7M early to a much lower median later (corpus).
- **Fix:**
  - Per product × page: change-point detection on log-views over posts (`ruptures`, PELT; installed).
  - Alert when the last 5-post median is below 30 % of the product's best-10 median (PROPOSED).
  - The planner then shifts to `same-product-new-audience` and new formats, or flags the product for a refresh.
- **HAND → architect Phase E + analytics.**

### G11. Retention and page-relative labels (extends audit ask #1). Score 8
- FB now exposes a **distribution score** (each reel compared with the page's other reels) and a retention graph per reel. A page-relative label directly addresses D35's finding that the page prior (AUC 0.86) beats every creative model.
- Add both to the Insights scrape.
- **HAND → analytics.** OMAR: already asked (HJ Insights access).

### G12. Multi-page distribution and cross-posting rules. Score 6
- The same edit posted on several pages and platforms faces G2 duplicate risk, and TikTok adds C2PA labels.
- **Fix:** the distribution planner assigns one *visually distinct* variant per page (G2 score ≤20 % between pages), staggers posting times per `posting_windows.json`, and keeps the TikTok decision with Omar (out of scope until then).
- **HAND → architect Phase F.**

### G13. Account-health monitoring. Score 6
- Meta added penalty-risk status in the Page/professional Support home (July 2025) and IG Account Status. A restricted page silently kills reach and poisons the model.
- **Fix:** a weekly read-only check through the box browser (pages where the box already has admin) → `analytics/data/account_health.csv`. The model excludes restricted windows.
- **HAND → analytics.**

### G14. Music rights and mute risk. Score 4.5
- Business pages have a restricted music library (D13). A track added in CapCut can be muted or blocked after upload.
- **Fix:** after posting, check whether audio is muted (Insights or a visual check); `music_library.csv` gets `mute_incidents`.
- **HAND → architect** (music.py) + **analytics.**

### G15. Experiment statistics. Score 6
- Views are heavy-tailed, and the page burst dominates them.
- **Fix:** compare variants on page-relative log-views or distribution score at a fixed 72 h age, with a Mann-Whitney test or a Bayesian log-normal comparison. Paired designs come free from the G4 FB/IG native tests.
- **HAND → architect Phase E.**

### G16. Competitor monitoring and product screening. Score 5
- The research library is refreshed by hand.
- **Fix:**
  - A scheduled weekly refresh plus a competitor-page watchlist with view velocity.
  - Product screening from public, widely used sources: TikTok Creative Center (top products, songs, hashtags) and the Meta Ad Library (public web, competitors running ads on our products).
  - Competitor captions get OCR'd with the same RapidOCR as G8.
- **HAND → research.**

### G17. Handoff and repo. Score 4
- The git repo isn't pushed (the remote choice is pending). Store backups exist.
- **HAND → architect Phase F** (already planned). Nothing new.

## Already closed tonight (box changes)
- **Installed:**
  - `pdqhash` 0.2.8 (Meta PDQ; built from source after `apt install g++ python3-dev`)
  - `ruptures` 1.1.10
  - `rapidfuzz` 3.14.6 (hook-text near-duplicate matching for G2/G4)
  - All `pip --user`, nice 19.
- **New files:**
  - `tools/preflight/` holds `_frames.py`, `originality.py`, `preflight.py`, `product_fidelity.py` and `season_calendar_2026.json`
  - this doc
- **Considered and skipped (load, or redundant):**
  - vPDQ/TMK C++ (PDQ-per-frame is equivalent for our use)
  - MediaPipe hands
  - DINOv2 or SigLIP downloads (CLIP B/32 is already cached; revisit if fidelity calibration is weak)
  - pyloudnorm (ffmpeg ebur128 is the same standard)
  - WhisperX (faster-whisper word timestamps already)

## Omar asks (true minimum)
1. **AI disclosure policy** (G3): self-disclose AI on posts, yes or no? It's a compliance decision; we'll log and measure either way.
2. *(Optional)* Which tool replies to SAY "<KEYWORD>" comments? This is for G7 attribution only.
3. Still open from the capability audit: HJ Insights access (G11).

---
## Autonomy status re-audit (2026-10-20 ~9:45 AM PT, D84, checked against the code)
Note: G3's "don't strip metadata" recommendation is SUPERSEDED by Omar (F87 "never ever a trace"): deliver.py strips everything.
| Capability | Status | Evidence in code | What's left |
|---|---|---|---|
| Plan → gates → quote | DONE | planner.plan + gates.run_all G1–G22 | POC defaults for products other than PurrVenture |
| Reference library + ref gate | DONE / PARTIAL | refs_lib.py, ref_gate.py, refs/*/manifest.json | approved cast missing for 10 of 11 slugs; TrumpGlow has no clean product photo |
| Generation runner | PARTIAL | runner.start_run/next_call/record_* | job polling with timeout + backoff, stuck-job recovery, nightly resume |
| Job recovery | PARTIAL | run.json cursor + 1 auto re-roll (D33) | crash-safe resume daemon, parking with reason, alerting |
| Frame / final QA | DONE | frame_qa, qa.final_checks(_variants), ai_look | calibrate product-fidelity thresholds |
| Edit (autoedit) | DONE | autoedit, songlay, omar_style | song fetch per new song (mambo_no_5 not fetched/verified yet) |
| CapCut write-back (learn from Omar's edits) | PARTIAL | capcut_export (write), backtest/capcut_drafts (batch read) | diff Omar's edited draft vs ours → new rules automatically |
| Zero-metadata delivery | DONE | deliver.stage/verify_staged | – |
| Drive delivery + auto-trash superseded | PARTIAL | drive_layout.json, deliver | 403 on files the app didn't create (Omar trashes those) |
| Posting | PARTIAL | publish.py (Buffer draft payloads, approval-only) | Omar links FB/IG in Buffer; public direct video host; Omar's approval per post |
| 5/day scheduler | MISSING | learn.schedule builds a day on demand; automation/ empty | cron/daemon: plan → approve → generate → edit → queue, with budget cap per day |
| Results feed | PARTIAL | results_feed.py (CSV inbox / META_TOKEN) | data source: Business Suite exports or a token Omar sets in the shell |
| A/B testing | PARTIAL | hook_variants, covers, variants.py | log which variant won; FB caption test / IG Trial Reels toggled by hand |
| Attribution | PARTIAL | tracked_links.py, sales_attribution.py | UTM links in live captions (blocked on product URLs, e.g. PatriotsGlow), Shopify UTM query runs |
| Learning loop (bandit/rules update) | PARTIAL | learn.update, arms.csv, rules_learned.csv | needs results data to move |
| Competitor / viral scan | PARTIAL | Viral Research daily scan (teammate) | spec finalisation pending on their side |
