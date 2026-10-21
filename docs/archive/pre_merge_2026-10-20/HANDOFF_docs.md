
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
