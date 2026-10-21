# BUILD_LOG (phase checkpoints, PT; '~' = approximate)
## 2026-10-18
- 19:50 Phase A started: repo skeleton, config, taxonomy, bodies, measure, corpus (512 videos) → measure_corpus launched.
- ~20:10 CapCut drafts made first-class: 110/110 parsed; 35 primary joins to posted reels; 646 placed clips; text/music/cut stats → D29/D30.
- 20:25 measure_corpus restarted (library rows: first-frame OCR only, no CLIP) because the shared box is at load ~40.
- ~20:27 CapCut export evaluated: pyJianYingDraft (JianYing 5.9 format) vs native clone writer (CapCut 9.4.1 format). Native chosen; both tested on throwaway copies.
- ~20:22 format_defaults F01–F19 written (engine fallback).
- 20:31 Mac mining reviewed (rules 30/30 verified; prompts sanitized 143→0 casting terms; CapCut adds 14 clip→reel links); D17–D31 logged; recency weighting in config; rules_core.csv.
- NEXT: backtester + virality model (LOO/holdout, with CapCut features and recency weights), then the production engine.

## 2026-10-18 ~21:00 PT — Phase B complete
model.py (ridge, LOO + temporal holdout), backtest.py (kNN neighbours, deviation checks, band, verdict), posting_time.py (Holm-corrected). Results in engine/backtest/data/validation.json. D35/D36 logged. Formats/analytics reviews logged. Next: Phase D.

## 2026-10-18 ~21:40 PT: Gap audit (gap hunter)
docs/GAP_AUDIT.md: 17 ranked gaps (production path first). Prototypes in tools/preflight/ (originality via Meta PDQ, preflight contact sheet/OCR safe zones/loudness/C2PA, product fidelity via cached CLIP, Q4 2026 calendar). Installed pdqhash (apt g++ + python3-dev), ruptures, rapidfuzz. Found that 485/508 raw Higgsfield clips carry C2PA AI-provenance manifests (Meta AI-info label input), so Omar needs to make a disclosure decision. Validation runs were deferred because CPU went to the production engine. Proposed PD-G2/G5/G6/G7 in DECISIONS.md.

## 2026-10-18 ~21:40 PT — Phase D progress: core path working, 3 dry runs complete
The brief → plan → QA → gate → animatic + CapCut draft path runs end to end. Pieces: product_profiles (7 products; world, energy, proven formats/music/captions), fit picker (REJECT/WARN plus why-this-format), world adaptations, the prompt builder (iPhone 12 suffix on every prompt, US flag, casting sanitiser, packed HARD CUT gens), proven music (music_library.csv), proven captions, posting windows, credit estimate (174/175), QA plan checks + logic check, the D35 backtest gate, ffmpeg animatic and CapCut draft.
Output in out/dryrun/: Grinch robe 3-2-1 (F01 STRONG), MerryFire then-vs-now (F04 STRONG), Brick Hood friend dare on the slopes with the Boombastic TikTok remix (F16 STRONG), Brick Hood 3-2-1 on the slope (F01 OK, transfer). Brick Hood store pallet: REJECTED (world conflict). All gates PASS, logic checks PASS, CapCut verify OK.
Next: fold in the gap-audit items (preflight, product fidelity, PySceneDetect cut assert, PDQ originality, hook/cover variants, season calendar + shipping claims, final-file checks).

## 2026-10-18 ~9:40 PM PT: Audience-targeting layer (audience/)
- Research: Meta system cards (FB Reels, IG Reels Chaining: per-country engagement feature; FB Feed Recs: current time; IG Search: country), Collabs, Trial Reels, FB Page country restrictions, AI translations. Statista/ECDB/IMF for country ranking. Billboard Holiday 100 vs UK Official Charts for audio.
- Shopify (read-only aggregates, MG + BH) by country → private/audience/ (absolute) + audience/data/shopify_country_relative.csv. US CR ~10× non-target.
- Built: LEVERS.md, data/country_tiers.csv, lexicon.csv (54 entries, 33 grounded in viral reels), audio_regions.md, visual_cues.md, EXPERIMENTS.md + experiments_proposed.csv (EXP-AUD-01..08), audience_rules.csv (A01–A12), tools/ (corpus, counts, lexicon, tiers, us_share_drivers, tier1_score). PROPOSED P-AUD-1..8 in DECISIONS.
- Waiting: audience/ig_reel_audience.csv (browser task) → run `nice -n 19 python3 audience/tools/us_share_drivers.py`.

## 2026-10-18 21:45 PT — Customer-voice layer (voice/) built
- Sources: 8,475 public TikTok comments on 47 competitor/reference videos (public comment JSON via curl_cffi; yt-dlp 2026.08 no longer extracts TikTok comments) + Gmail support inbox, read-only (298 threads scanned, 164 customer threads, aggregated, raw deleted) + public product pages and web-search review summaries.
- Blocked: YouTube (bot check on box IP; cookies refused, since that would mean using a credential), Reddit JSON (403 without OAuth), TikTok search/user listing (hangs). FB/IG → voice/browser_queue.csv (115 rows).
- Outputs: voice/comments.csv, voice_stats.json, INSIGHTS.md, voice_rules.csv (V01–V16, rules_core format + rule_type/engine_slot/evidence_n), support_themes.csv, engagement_correlation.csv.
- Critical alerts raised (INSIGHTS §0): robe fulfilment mismatch (106/164 support threads late; 16+ no controller); MerryFire vs the CPSC Dec-2024 liquid-fuel fire pit alert; duplicated testimonials across stores (FTC 16 CFR 465); viewers calling out AI.
- Corpus label error found: the EXT stonebrook.home 'portable fire pit' is a portable TV (excluded in voice/products.py).

## 2026-10-18 21:46 PT — RAM emergency: features extraction cut to 1 worker, measure_corpus paused
- data/features: stopped the ASR, OCR and build_features processes; only ONE extract stage runs now (`extract.py --stage base`, nice 19, 1 worker, ~0.5 GB). OCR and ASR will run strictly one after another once base finishes. All three resume from cache/, so nothing is lost.
- backtest.measure_corpus (--procs 3, ~3.4 GB across 3 workers) paused: pool parent sent SIGTERM at 44 cached videos (log private/measure.log). It is cached and resumable. Restart it after the feature stages finish with: `cd engine && nohup nice -n 19 python3 -m backtest.measure_corpus --procs 1 >> ../private/measure.log 2>&1 &`
- Memory after: 5016 MB available (target ≥4 GB met).

## 2026-10-18 ~23:15 PT: Features DB takeover (features worker #2)
- State on takeover: run_sequential.sh (orchestrator) running `extract --stage ocr --sources own` (finished 22:35, 62 reels), then product own (76, 22:39), now OCR for VR/external/reference. One extract at a time, nice 19, 1 worker.
- inventory.py: + `own_ig_extra` = 21 merry.jammies IG reels missing from team/hooks (metrics from audience/ig_reel_audience.csv, videos from style/_work/covered/ig; incl. 4.6M Ddii6mOKO2G, 687K DdQw1jyKI63, 362K DdTC2suKD0l, 334K DdK34IiqRx4, 241K DdGdL41KJo4). Reference library re-read: 169 rows (54 top_recent_1m, 73 near_miss, 42 archive) + new keys platform_audio_label, audio_id_confidence. Own 78 → 99.
- build_features.side_joins: CapCut primary joins (cc_* from private/edits/edits.csv; HJ-13 and MJIG-04 unjoined per architect → cc_joined=0; 33 joins) + covered-reveal labels from style/covered_hooks.csv (covered_reveal / cue_visible / cue_score / reveal_s / grp; 18 own rows incl. MF-02 as MJIG-04's same edit). correlations.py: new columns + own_IG set. SCHEMA.md updated.
- run_followup.sh (RAM guard ≥4.5 GB before each stage): waits for run_sequential's first build, stops it before the Drive-library/Mac stages (out of scope tonight, cached/resumable), runs base→fp→ocr→asr→product for own/VR/external/reference (new IG + reference rows), rebuilds + mirrors to the store, then resumes `backtest.measure_corpus --procs 1`. Logs: data/features/logs_followup.log, logs_fu_<stage>.log, private/measure.log.
- 2026-10-19 00:31 PT: run_sequential finished OCR (VR/ext/ref 232), ASR (own+VR+ext+ref), 4 forced re-extracts, product (248) and the first build (00:29), then was stopped before the library/Mac stages. run_followup.sh (PID 879962, setsid/nohup) now runs base → fp → ocr → asr → product for the new rows → build (validate + correlations + store mirror) → measure_corpus --procs 1. progress_watch.sh mirrors each stage into data/features/PROGRESS.md. Handshake fixes (corpus_key/page_code EXT for ext+VR, VR page names, schema_version) are in build_features.side_joins and documented in docs/FEATURES_HANDSHAKE.md.
