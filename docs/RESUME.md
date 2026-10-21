# RESUME — Hookforge (read this first)
Generated 2026-10-20 5:39 PM PT by `engine/scripts/build_resume.py` from DECISIONS, OMAR_FEEDBACK_LOG, rules_core, config and the queues. Do not hand-edit; fix the sources and rerun.

## 0. Start of every session
```
/workspace/hookforge/automation/ensure.sh          # snapshot supervisor (idempotent)
cd /workspace/hookforge/engine && PYTHONPATH=. python3 -m hookforge.regen   # calendar, concepts, weekly+lean, render queue, Buffer preflight, digest
PYTHONPATH=. python3 -m pytest -q tests   # + script tests: test_recreate_logic, test_audience_fit, test_edit_rules, test_omar_style (python3 <file>)
```
Full history: [docs/DECISIONS.md](DECISIONS.md) · [docs/HANDOFF.md](HANDOFF.md) · [learning/OMAR_FEEDBACK_LOG.md](../learning/OMAR_FEEDBACK_LOG.md) · audit: [docs/BLUEPRINT_2026-10-20.md](BLUEPRINT_2026-10-20.md) · excluded assets: [docs/MANIFEST_EXCLUDED.md](MANIFEST_EXCLUDED.md)

## 1. Hard safety constraints (Omar, standing — override everything)
- No Higgsfield credit spend without Omar's explicit approval of the exact plan and cap (approval record in learning/approvals/<run>.json; runner gate, LIVE disabled by default).
- Post nothing, send nothing: every external message/post needs a draft card and Omar's okay. Buffer = saveToDraft drafts only, mode addToQueue, never shareNow.
- FB/IG read-only (no likes, comments, posts, ads). Shopify read-only, aggregates only, no PII, don't switch stores. Gmail read-only.
- Never ask for or see passwords (Secure Form / box handoff). No tokens in files or chat. No scraping browser cookies/credentials to get around blocks. Never print presigned URLs.
- Exclude: FEMBOY child content entirely; never sexualize minors. Bank statements, Ecomstein/IMG_5172.PNG, rental applications, IDs, tax/financial docs, credentials, the LLC folder, the "vids w isaac" folder.
- No race-based casting or hooks. Cast: default women; Trump/car/patriotic products a man; cat products a woman.
- On-screen text (hooks + text cards) ≤ 8 words, NO exceptions (D149). FB post captions follow proven winners (not word-capped).
- Captions use SAY "<KEYWORD>", never "Comment" (D5/F93); the SAY rule always applies (D148).
- Hooks are 1080p (D141). Seedance 2.5 video only, GPT Image 2 stills only, no end frames (D22).
- Every file leaves the box via deliver.stage / verify_staged (D44d). Leave the shared-learning server deployment alone; don't touch the other worker's PurrVenture files unless asked.
- Report times in PT. Log every decision as a D-number in docs/DECISIONS.md.

## 2. Products
**Active (D117/D131):** `jollyglow_curtain`, `trumpglow`, `purrventure_carrier`

**Retired (FULL reference data — cuts, tags, captions, stats, sounds, hooks — no new content):** `grinch_robe`, `heatjams`, `cozyjams`, `grinchmelt_mug`, `brickhood_mask`, `minionmask`, `merryfire`, `merryglow_lights`

| active product | product URL status |
|---|---|
| jollyglow_curtain | https://grinchmelt.store/products/jollyglow-programmable-led-curtain-lights |
| trumpglow | PLACEHOLDER (blocks caption swaps) |
| purrventure_carrier | PLACEHOLDER (blocks caption swaps) |

## 3. Account and channel IDs (IDs only — no secrets; auth is host-connector OAuth)
| Buffer account | MCP namespace | org id | plan | connected |
|---|---|---|---|---|
| buffer1 | user-Buffer | 6ad7108f7a26bda7eb714973 | free (max 10 scheduled) | True |
| buffer2 | user-Buffer--buffer2 | 6ad7d4f3d9fb9bac41dd9d22 | free (max 10 scheduled) | True |
| buffer3 | None | None | free (max 10 scheduled) | False |

| page | service | account | channel id | products |
|---|---|---|---|---|
| jollyglow_fb | facebook | buffer1 | 6ad7c7b6778b240e2f6eded2 | jollyglow_curtain |
| patriotsglow_fb | facebook | buffer1 | 6ad7c63f778b240e2f6ed4e6 | trumpglow |
| purrventures_fb | facebook | buffer1 | 6ad7c63f778b240e2f6ed4e5 | purrventure_carrier |
| merryjammies_ig | instagram | buffer1 | 6ad7c950778b240e2f6f0cfd | LOCKED |
| trumpglow_fb | facebook | buffer2 | 6ad7d610778b240e2f6f8b6c | trumpglow |
| merryjammies_ig_b2 | instagram | buffer2 | 6ad7d94a778b240e2f6ffc72 | - |
| purrventures2_fb | facebook | buffer2 | 6ad7e3e8778b240e2f706dfd | purrventure_carrier |

**Higgsfield:** MCP namespaces `user-Higgsfield` (old account) and `user-Higgsfield--new-account` (live account: `user-Higgsfield--new-account`). Live runs: LIVE.enabled = `False`. Prices (get_cost): seedance_2_5 1080p 4 s = 64, 720p 4 s = 28; gpt_image_2 2k high = 6.5 / 1k high = 3.5 / 1k medium = 1.0.
Other connectors: user-Shopify / user-Shopify--brickhood (read-only), user-Gmail (read-only), user-Google-drive, user-Slack, user-Buffer / user-Buffer--buffer2.

## 4. Approval queue (learning/approval_queue — all AWAITING_OMAR_APPROVAL, nothing approved)
| id | kind | credits | recommended option | ready |
|---|---|---|---|---|
| concept_2026-10-20_jollyglow_curtain_F06 | concept_test | 200.0 | - | True |
| concept_2026-10-20_purrventure_carrier_F02 | concept_test | 200.0 | - | True |
| concept_2026-10-20_trumpglow_F09 | concept_test | 200.0 | lean_1_still | True |
| weekly_batch_2026-10-21 | weekly_batch | 1227.0 | lean_1080p_hook | True |

Archived (never re-queue): concept_2026-10-20_brickhood_mask_F01, concept_2026-10-20_brickhood_mask_F02, concept_2026-10-20_brickhood_mask_F07, concept_2026-10-20_cozyjams_F13, concept_2026-10-20_grinch_robe_F08, concept_2026-10-20_grinchmelt_mug_F02, concept_2026-10-20_heatjams_F07, concept_2026-10-20_merryfire_F02, concept_2026-10-20_merryglow_lights_F06, concept_2026-10-20_minionmask_F16, pv_P2_payoff_redo

**Approval records on file (learning/approvals):** jollyglow_321_frames, jollyglow_combo_frames, long_gens, mg-tvn-001, mg-tvn-001-b3, purrventure_3videos, purrventure_branding_v2, purrventure_p2_addshot

## 5. Open decisions for Omar
- Weekly batch 2026-10-21: approve lean 1080p-hook plan (1,227 cr) vs standard (2,600 cr), or per video.
- Daily innovation budget 175 cr < 200 cr full concept; lean (174) auto-recommended — raise budget or keep lean?
- 298.15 cr unledgered spend on the new Higgsfield account (10-20) — needs job rows; purrventure_branding_v2 spend unknown.
- trumpglow + purrventure product URLs are PLACEHOLDER (blocks traction caption swaps) — read-only Shopify lookup or Omar to supply.
- SAY "VOTE" near the midterms carries a PL5 WARN — keep the keyword or switch (e.g. SAY "USA")?
- JollyGlow captions now carry SAY "LIGHTS" (D148) — confirm wording.
- No public video host for Buffer asset URLs yet (needed before the first real draft push).
- GitHub: push once auth exists; repo should be PRIVATE (config/buffer_routing.json carries org/channel IDs, D10).

## 6. Next steps
1. Get Omar's decision on the weekly batch (lean vs standard) and today's concept; write learning/approvals/<run>.json from the chat approval (runner gate needs plan sha256 + cap).
2. Live run via runner (anchor = build_calls_lean 'anchor' 174 cr; extras = 'extra' 70.5 cr), then lean_edit.build + gate_built + reveal check per video.
3. Stage renders with deliver.stage/verify_staged, get public URLs, rerun buffer_preflight with real URLs, then publish.prepare → Omar approve → Buffer drafts.
4. Fill PLACEHOLDER product URLs; reconcile the 298.15 cr; set META_TOKEN via a Secure Form/handoff so the snapshot loop gets data.
5. Migration plan: docs/BLUEPRINT_2026-10-20.md (commit → container → read-only jobs → approvals UI → Buffer → generation).

## 7. Omar's standing decisions (verbatim table from docs/DECISIONS.md D1–D34)

| # | Date PT | Decision | Why | Evidence |
| D1 | 2026-10-18 | (AMENDED by D17: video prompts only) Every Higgsfield prompt ends with the verbatim iPhone 12 realism suffix (`config.IPHONE12_SUFFIX`); prompt builder appends/validates it | Omar standing rule | omar_decisions.md; Mac rules R02 (evolved 15 Pro Max → 15 → 12) |
| D2 | 2026-10-18 | Hook = its own 4 s Seedance 2.5 gen at 1080p; every other gen 720p, 2 shots per 4 s gen with a straight hard cut at ~2 s (1.5–2.5 allowed) | Omar standing rule; credits | omar_decisions.md 7:49 PM; Mac R07, R10 |
| D3 | 2026-10-18 | (AMENDED by D19) "Don't show this to…" allowed on decor | Omar; external 3.2M/576K/198K decor don't-show wins | omar_decisions.md; team/external §3a; viral_research #2 |
| D4 | 2026-10-18 | Real-retailer fake-store hooks keep the "JK, we make them" flip on the activation cut | Omar; legal/false-ad exposure flagged by viral research | omar_decisions.md; viral_research disagreements table |
| D5 | 2026-10-18 | CTAs say `SAY "<KEYWORD>"`, never COMMENT/tag/vote | FB engagement-bait demotion | omar_decisions.md; external §3f |
| D6 | 2026-10-18 | Link captions are a safe default, not a ranking lever; never used as a model predictor | Links added after reels took off; Meta 2-links/month risk | Omar ground truth; hooks REPORT model rules; audit R7; external §6.4 |
| D7 | 2026-10-18 | Upload 2160×3840@30, −14 LUFS, TP ≤ −1 dBTP; served 1080 vs 1440 is an *outcome* (FB AV1 ladder after watch time), so resolution of downloaded copies is excluded from QA validation and the virality model | Reverse causality | body REPORT §5 (4.8K reel from 2160×3840 source served 1080 VP9) |
| D8 | 2026-10-18 | Seedance only (no Kling); GPT Image 2 only for stills; no end frames; never regenerate without approval/budget | Omar rules | Mac R11, R12, R13, R14 |
| D9 | 2026-10-18 | No Higgsfield credit spend, no posting, no FB/IG actions without Omar's explicit approval | Standing constraint | task brief |
| D10 | 2026-10-18 | Privacy: sales $, order counts, team names/emails, page/reel/workspace IDs, customer data live only in `private/` (gitignored); shareable files use relative metrics (orders/1K views) | Repo shared with friends | task brief |
| D11 | 2026-10-18 | Formats are *hook formats* (0–4 s + text device); bodies are per-category formulas with packing baked in (`engine/hookforge/bodies.py`) | Body doesn't separate winners (p>0.1 on all metrics); hook + distribution do | body REPORT §0; hooks REPORT §1 |
| D12 | 2026-10-18 | Store hooks render a store that *looks like* Target (red) / Walmart (blue) without logos; the store name lives only in the text overlay + JK flip | Omar rule + trademark risk | Mac R20; viral_research risk note |
| D13 | 2026-10-18 | Generations always carry native ambient audio (no music); music is added in the edit (or in-app at upload) | Omar rule; business-account music library limits | Mac R05; external §6.8 |
| D14 | 2026-10-18 | Burned text: never in generations; the auto-edit renders the text layer (TikTok Sans, OFL) so the master can also be exported text-free for CapCut | Omar "never burn in captions" (R04) applies to generations; autonomy needs a text layer | Mac R04 |
| D15 | 2026-10-18 | (SUPERSEDED by D24: mandatory) US flag in background of start frames by default | Omar request (GrinchMelt, MJ, MG) | Mac R03; playbook §6 |
| D16 | 2026-10-18 | 20 % innovation budget: ≥1 of 5 daily slots per product is a tagged experiment with a hypothesis | Omar steering (explore vs exploit) | steering 2026-10-18 8:17 PM |
| D17 | 2026-10-18 | (SUPERSEDED by D32) iPhone 12 suffix goes on VIDEO prompts only. Start-frame stills (GPT Image 2) use the short positive recipe `iPhone photo of … Sharp, clean, realistic phone photo.` with NO negative words (`config.STILL_*`; prompt linter rejects suffix/negatives in stills) | Omar's GrinchMelt finding: negative suffix words made stills worse; start frames are his #1 quality lever (R01). Lead resolution of conflict C1, confirmed by parent steering | GrinchMelt-Playbook.md "winning image recipe"; Mac REPORT §5 C1; 60K+ MerryFire/JollyGlow video prompts (no suffix) are craft evidence that the opener "Handheld phone video, natural real-time speed, no slow motion" also works |
| D18 | 2026-10-18 | (RE-ROLL PART SUPERSEDED by D33; cost listing stays) No re-rolls without Omar's permission (`REROLLS_ALLOWED=0`). Every plan prints the credit cost per video (budget 100–175; variants ≤100). The QA gate flags a failed clip as a **re-roll request** (clip, reason, prompt fix, credit cost) instead of re-rolling. Playbook §15.11 "2–4 rolls per shot" is overridden | Omar's rule wins (R14, R15) | rules.csv R14 (09-28), R15 (10-03); Omar chrono "100 credits per video at the very max" |
| D19 | 2026-10-18 | "Don't show this to…" on DECOR demoted to experiment-only (innovation slot), pending Omar's call. Then-vs-now (F04) and POV (F12/F15) are the preferred decor hooks. Still Tier A on wearables | Own decor results 0/5 ≥10K | MerryFire 457 (MGS-09) / 33 / 3,084 (MF-02); MGS-05 3,048; MJIG-04 9,007 vs F04 decor 152.9K/84.4K/70.4K/67.7K/64.5K and POV 63.3K/63.0K (CapCut-joined drafts) |
| D20 | 2026-10-18 | Packing multiple shots per gen (straight hard cuts, new angle each cut) is the standard. Playbook §7.5 "one action per clip" is retired (micro-beats like a plug press may still get their own half of a packed gen) | Matches Omar's packing rule; proven in 63K/35K reels | Mac R07, R08; D2; project_reel_matches (movie-night 63K, FaceTime 35K used 2–3-shot hard-cut gens) |
| D21 | 2026-10-18 | Ad Multiplier = remake the whole video. Background and character swaps (+ Christmas background adjustments) are permitted ONLY in Ad Multiplier variant mode; everywhere else swaps are avoided (recreate = 1–2 changes) | Omar R21/R22 vs hf_match §15.8 (background swaps 26 % used vs 52 % unused) | rules.csv R21 (10-13), R06; prompt_analysis §15.8; Ad Multiplier variants of 100K+ reels: 64K / 2.1K / 1.2K (≈1 in 3) |
| D22 | 2026-10-18 | Seedance 2.5 only (no Kling, ever); GPT Image 2 only for stills (no Seedream/"sunburst"); no end frames ever | Omar rules | R11 (10-06), R12 (10-09), R13 (09-29) |
| D23 | 2026-10-18 | Always generate native audio (ambient only, named sounds, "No background music, no text, no captions"); never burn captions or music into generations; every variant gets fresh audio (never the original track) | Omar rules; shadowban risk on repeated audio | R04, R05, R06 |
| D24 | 2026-10-18 | US flags in the background of EVERY clip (mandatory, prompt linter checks). Any display: the top unit is always lit/working | Omar global rules | R03 (10-04), R16 (10-08); 35K FaceTime reel "the one at the very top is already activated" |
| D25 | 2026-10-18 | Hooks ≤5 s and every gen ≤5 s (4 s standard). Story-logic checks in QA/brief: time of day progresses, build order makes sense (fuel → ignite → snacks), relatable homes, no nonsense props, natural speed, no permanent shock face, real FaceTime UI with no whip/whoosh | Omar rules | R09, R17, R18, R19, R24, R25, R26 |
| D26 | 2026-10-18 | Stores look like Target (red) / Walmart (blue) with no logos; names live only in text overlay + JK flip (reaffirms D12) | Omar rule + trademark | R20 |
| D27 | 2026-10-18 | Race/ethnicity casting instructions and slur content are excluded from all rules and outputs. `config.sanitize_casting` strips them from every reused prompt (143 of 1,926 Mac prompts had ethnicity casting terms → 0 after sanitizing); QA blocks any output with `casting_violations` | Compliance, platform policy, legal risk | Mac REPORT §7 |
| D28 | 2026-10-18 | **FINAL (Omar, 8:32 PM PT):** recency weighting (`config.RECENCY`: full ≤14 d, exp decay τ=7 d, floor 0.05; 90+ d = weak prior) applies ONLY to EXTERNAL reels (research reference library tiers, external/competitor reels). OUR OWN data (all our pages' reels, CapCut drafts, prompts, Insights, Shopify) keeps FULL weight regardless of age. No "≥1 fresh row" requirement when our own data supports a trend rule; external-only trend rules carry a freshness label (fresh/aging/prior-only). Supersedes the earlier draft of D28 | Omar's final call via parent steering | steering 2026-10-18 8:32 PM |
| D29 | 2026-10-18 | CapCut drafts are a first-class data source (`engine/backtest/capcut_drafts.py` → `private/edits/`). Export of edit plans to CapCut uses a native writer that clones the team's own CapCut 9.4.1 draft (new_version 185) rather than pyJianYingDraft (which writes JianYing 5.9 `draft_content.json`, new_version 110) | Exact schema of the installed app; both tested on throwaway copies only | docs/CAPCUT_EXPORT.md |
| D30 | 2026-10-18 | Text overlay centre = 19 % from top (CapCut transform.y 0.62, IQR 0.56–0.66), font size 15, stroke 0.09, one persistent card for most formats; then-vs-now cards switch on the first body cut ("Vs..") and the payoff | 110 team drafts | capcut_stats.json; edits.csv text_cards |
| D31 | 2026-10-18 | Reference library tiers (schema 1.0): `index.csv` = 1M+ reels ≤14 days (recreation + trend picks use these first), `archive.csv` = older 1M+, `near_misses.csv` = 300K–1M in window. Backtester uses all tiers weighted by `recency_weight` | Freshness rule | Viral Research schema 1.0 |
| D32 | 2026-10-18 | **Omar override (supersedes D17):** EVERY prompt, both video and start-frame still, ends with the verbatim iPhone 12 suffix. A still = `iPhone photo of <scene>. Sharp, clean, realistic phone photo.` + suffix (`config.still_prompt`). The prompt builder appends it (`config.ensure_suffix`) and QA rejects any prompt without it | Omar: start frames keep the iPhone shot parameters too | steering 2026-10-18 8:35 PM |
| D33 | 2026-10-18 | **Omar override (supersedes the zero-re-roll part of D18):** an automatic re-roll is allowed ONLY for an absurd failure with confidence ≥0.9, at most 1 auto re-roll per shot. Absurd failures: product missing or deformed, wrong product or colour, mangled person or limbs, unrelated scene, hard cut missing or broken, unusable hook. Minor flaws never trigger a re-roll (background logos, odd text on displays or signage, small artifacts, slight lighting issues). Those ship and get noted in the learning log. Every re-roll is logged with reason, confidence and credit cost; the cost listing per video stays | Omar override | steering 2026-10-18 8:35 PM; `config.REROLL` |
| D34 | 2026-10-18 | External library rows carry `inclusion_rule` ∈ {`14d_1m`, `90d_20m`}. `14d_1m` rows (≤14 d, 1M+) follow `config.RECENCY`. `90d_20m` rows (≤90 d, 20M+, mega viral) are exempt from the 14-day decay and get weight `config.INCLUSION_WEIGHT["90d_20m"]` = 0.95 as proven mega-viral evidence. Own data stays at 1.0 (D28) | Omar library schema update | steering 2026-10-18 8:36 PM |
| # | Status | Decision | Why | Evidence |

Later decisions D35–D160 (incl. amendments) are sections in docs/DECISIONS.md; index:

D35 Backtest gate policy (Phase B result) — 2026-10-18, D36 Posting-time promotion uses Holm correction — 2026-10-18, D37 PRODUCT WORLD layer is core (Omar, 2026-10-18), D38 Music and captions must be proven + niche/energy matched (Om, D39 Teammate plug-ins (style/, psychology/), D40 Credit estimates (inferred), D41 Scale / originality / auto-post (disabled) / audience+voice, D42 Generation failure memory: PROPOSED, deferred until the core, D43 Gap-audit items folded into the core path (2026-10-18), D44 Strip C2PA/provenance metadata from all final exports (Omar,, D45 Members pass 2 rules MP2-1..9 folded into templates + QA; MP, D46 Audience layer light integration + posting-window conflict +, D47 (PROPOSED) — Customer-voice rules feed the engine (voice/voi, D48 (PROPOSED) — Every reel ends with a where-to-buy answer in S, D49 (PROPOSED) — PROOF beat in every body (V02) + AI-tell QA log, D50 (PROPOSED, NEEDS OMAR) — Robe and MerryFire content gates (V, D47 –D49 (voice layer, integrated as PROPOSED by voice/) + SAFET, D50 Omar override on customer-voice suggestions (Omar, 2026-10-1, D51 MerryFire safety hold REMOVED; business-risk flags dropped (, D63 FB HeatedJammies insights fed into the engine (2026-10-19 PT, D65 Autonomous song fetch on Omar's Mac + full official tracks (, D66 (2026-10-19) Song starts on frame 0, D67 (2026-10-19) Hook captions: short proven formats, max ~8 wor, D68 (2026-10-19 9:05 PM PT) No profile ban against Omar's own pr, D69 (2026-10-19 9:12 PM PT) Store-aisle ban removed for every pr, D69 (2026-10-19 ~9:30 PM PT) Omar's corrections as automatic gat, D70 (2026-10-19 9:20 PM PT) Camera gaze follows scene logic, D71 (2026-10-19 9:17 PM PT) JollyGlow video cap 400; chain after, D72 (2026-10-19 9:30 PM PT) No on-screen link CTAs; short opener, D72 (2026-10-19 ~9:35 PM PT) Image rate fix, ledger backfill, pe, D74 (2026-10-19 ~9:50 PM PT) Omar's CapCut editing style = edit, D75 (2026-10-19 ~10:15 PM PT) AI footage must look real: product, D72 Speech QA gates + voice-forward remix (Omar, 2026-10-19 ~9:3, D73 Captions max 2 rows + "everyone counts" (Omar, 2026-10-19 9:, D44b No encoder tag on any final (2026-10-19), D44c No codec fingerprint on any final (2026-10-19), D44d Never a trace: single delivery chokepoint (Omar: "there shou, D76 (2026-10-19 ~11:35 PM PT) Omar feedback log + gates G14–G19, D77 (2026-10-19 ~11:45 PM PT) Stored-fact cross-check + conflict, D78 (2026-10-20 overnight) Buffer posting pipeline - prepare onl, D79 (2026-10-20 overnight) Edit-vs-Omar audit + PurrVenture NaN, D80 (2026-10-20 ~9:20 AM PT) Reference hard gate (F88) + light g, D81 (2026-10-20 ~9:35 AM PT) Strict frame self-QA gate (F90), D84 (2026-10-20 ~9:45 AM PT) PurrVenture POC defaults, per-produ, D85 (2026-10-20 ~9:55 AM PT) SAY-not-Comment gate, cast lock per, D86 (2026-10-20 ~10:05 AM PT) #1 Results feed: per-reel performa, D87 (2026-10-20 ~10:05 AM PT) #5 Per-reel tracked links + Shopif, D88 (2026-10-20 ~10:05 AM PT) ly_season prior tier (PD-G5 → impl, D89 (2026-10-20 ~10:05 AM PT) Trump projector composite pipeline, D86 (2026-10-20 ~10:30 AM PT) SAY end card re-edit (F93), TrumpG, D82 (2026-10-20 ~10:45 AM PT) PurrVenture video run, D91 (2026-10-20 ~12:15 PM PT) Backend build: scheduler, recovery, D92 (2026-10-20 ~12:25 PM PT) ly_season curated set wired in (Vi, D93 Facebook POST caption module (fb_caption.py) - 2026-10-20, D94 (2026-10-20 ~2:25 PM PT) Buffer multi-account routing, D95 Per-page FB captions, caption-swap approval, posting windows, D96 Hourly results snapshots (read-only), D97 test_live_gate G9 fix (planner prompt, gate unchanged), D98 Product URLs via read-only Shopify, D99 (2026-10-20 ~2:40 PM PT) F96 hard gate: strip + C2PA verify, D100 PurrVenture Bengal ref replaced + CLIP ref-sanity, D101 Per-page caption variants (products on >= 2 pages), D102 Meta CSV ingest + supervised snapshot loop, D103 Publishing dashboard panel, D104 Woman cast refs tight-cropped; ref audit 0 fail (2026-10-20), D105 Higgsfield new-account media IDs (free uploads), D106 concept_lab + approval_queue (20% innovation, dry run), D107 Graph API caption edit (approval-gated), D108 PurrVenture P2 payoff redo plan, D109 Product profiles + audiences for heatjams, cozyjams, minionm, D110 Concept-lab blockers fixed in the planner (gates untouched), D111 Cross-product concept ranking, D112 Woman cast refs re-sourced from the source reels, D113 World-consistency gate (2026-10-20), D114 Political-content lint (2026-10-20), D115 End-to-end dry run, 11 products (2026-10-20), D116 HANDOFF architecture map (2026-10-20), D117 Retired products (Omar F96, 2026-10-20 3:37 PM PT), D118 Spare PurrVentures channel + duplicate-channel check, D119 Performance feedback loop (perf_feedback.py), D120 Credit ledger (credit_ledger.py), D121 Chat-approved caps + run close-out (2026-10-20 3:50 PM PT), D122 Auto-reroll planner (reroll_planner.py), D123 purrventures2_fb caption, D124 Approval digest (approval_digest.py → analytics/approval_dig, D125 Queue cleanup (2026-10-20 3:59 PM PT), D126 Automatic job-ID logging + reconciliation, D127 Weekly content calendar (content_calendar.py), D128 Crash recovery / resume, D129 Hourly unlogged-spend watch (spend_watch.py), D130 Render queue (render_queue.py), D131 Robe family retired (Omar F97, 4:09 PM PT), D132 Hook/caption variants (hook_variants.py), D133 Pipeline profiling + caches, D134 Reference miner (ref_miner.py), D135 Weekly batch (concept_lab.weekly), D136 Post-publish watcher dry run (post_watch.py), D59 First live test switched to MerryGlow then-vs-now (Omar, Mon, D54 hookforge.db is the default reels source after review (Omar, D55 Public dashboard: no product/brand names, no hook text (Omar, D56 vision_judge is the D33 absurd-failure judge (Omar task 4), D57 Live Higgsfield path built behind an approval gate, DISABLED, D58 Mug: proof shot, own hook, niche-proven caption (Omar task 2, D52 Covered-reveal hooks are allowed (Omar override, 2026-10-18, D42 Generation failure memory: WIRED (Omar go-ahead 2026-10-18 1, D44 addendum — structural provenance detector (2026-10-18 ~10:20, D53 Covered-reveal hook options + advisory PS02 (style re-code,, D60 Unlit start frames for pre-reveal shots, plus the B3 redo (O, D61 POST-MORTEM of mg-tvn-001, and RECREATE as the default mode, D62 Mandatory AUDIENCE-FIT stage (Omar, 2026-10-19 ~2:00 PM PT), D63 Natural clip sound replaces "mute generated audio"; song in-, D137 (2026-10-20 PT) PL6 group-insult lint, D138 Listing-style captions blocked, D139 Distinct caption TEXT, D140 Real still price + lean plan, D141 (2026-10-20 PT) P2 payoff redo archived for good; lean plan, D142 Near-duplicate video gate for the lean plan, D143 Daily and weekly budget logic picks lean automatically, D144 JollyGlow caption, D145 (2026-10-20 PT) Lean editor, real build, D146 JollyGlow F06 on-screen hook, D147 Payoff reveal check, D148 SAY rule on JollyGlow, D149 (2026-10-20 PT) 8-word hook rule, no exceptions, D150 Slow-reveal detection, D151 Lean dry render, trumpglow + purrventure, D152 Output cleanup, D153 (2026-10-20 PT) Buffer draft-payload preflight, D154 One-command regenerate, D155 lean_dryrun pruned, D156 (2026-10-20 PT) Stale G2 test, D157 One copy of HANDOFF and DECISIONS, D158 Retro approval records for today's chat-approved runs, D159 Snapshot supervisor ensure script, D160 GitHub-ready local commit (not pushed), D161 (2026-10-20 PT) Spend watch attribution by model, D162 (2026-10-20 PT) CI workflow, D163 (2026-10-20 PT) Asset restore plan, dry run only

## 8. Omar's rules in his words (learning/rules_core.csv)
| id | rule | status | resolution |
|---|---|---|---|
| R01 | Start frames are the #1 quality lever; must look like a genuine iPhone photo | active |  |
| R02 | Realism suffix in every prompt (evolved: iPhone 15 Pro Max -> iPhone 15 -> iPhone 12) | active | D32: suffix on EVERY prompt (video + stills); stills = 'iPhone photo of… Sharp, clean, realistic phone photo.' + suffix |
| R03 | US flags in the background of every clip | active |  |
| R04 | Never burn in captions or music; Omar adds them in CapCut | active |  |
| R05 | Always generate audio (ambient only, no music) | active |  |
| R06 | Ad Multiplier variants need their own fresh audio, never the original track (shadowban risk) | active |  |
| R07 | Combine shots: 2+ cuts of similar scenery go in ONE gen with straight hard cuts and different angles | active | D20: packing multiple shots per gen is the standard; playbook §7.5 'one action per clip' retired |
| R08 | Cuts are straight hard cuts, no fades, change angle every cut | active |  |
| R09 | Clips short: <=5s (4s typical); never 8s | active |  |
| R10 | Resolution: hook 1080p, rest 720p (briefly 'hook at 720p as well' 09-29 for BrickHood) | active |  |
| R11 | Seedance only; no Kling | active |  |
| R12 | Image model: GPT Image 2 only (not Seedream/'sunburst') | active |  |
| R13 | No end frames; generate from start frame only | active |  |
| R14 | Never regenerate without explicit permission | amended | D33: auto re-roll only on absurd failures at >=0.9 confidence (max 1/shot), logged with reason+cost; minor flaws ship + are logged |
| R15 | Always list cost; stay in budget (typ. 100-175 credits/video) | active | D18: every plan prints credits per video; budget 100-175 (variants <=100) |
| R16 | Every display: an ACTIVE working product on top (engagement) | active |  |
| R17 | Time of day must progress chronologically | active |  |
| R18 | Natural motion; no permanent shock face; not slow/robotic | active |  |
| R19 | FaceTime flip must be natural - no whip motion, no whoosh SFX, real FaceTime UI | active |  |
| R20 | Store look without logos: 'look like a Target' (red), Walmart = blue | active |  |
| R21 | Ad Multiplier = remake the WHOLE video, with Christmas background adjustments | active | D21: Ad Multiplier = whole video; background/character swaps allowed ONLY in Ad Multiplier mode |
| R22 | Reposting own winners via variants (new characters/backgrounds/outfits) to avoid Meta duplicate detection | active | D21: variant reposts via Ad Multiplier only |
| R23 | Watch AND listen to references fully before working | active |  |
| R24 | MerryFire build order: fuel pour + ignition before snacks | active |  |
| R25 | Settings must be relatable homes (no random/nonsense props) | active |  |
| R26 | Hooks need a 'wow factor' yet stay realistic; stand out from 'slop' | active |  |
| R27 | These are ORGANIC posts, not ads | active |  |
| R28 | Captions come from the Caption Bank (patterns: POV, 'perfect X doesn't exi-', 'Christmas moms. . RUN to [STORE]', 'DON'T show this to. . . ') | active |  |
| R29 | BrickHood hook = first-person POV unboxing (gondola/snowmobile), plastic wrap rip, product stays recognizable | active |  |
| R30 | Hero prop must match the reference exactly (e. g. JollyGlow light density, product shown before unfold) | active |  |
| H01 | Exclude race/ethnicity casting and slur content from every rule, prompt and output | active | D27: config.sanitize_casting + QA casting_violations block |
| H02 | 'Don't show this to…' on decor = experiment-only (MerryFire 0/3: 457/33/3K); prefer then-vs-now + POV on decor | active | D19 pending Omar |
| H03 | Hooks <=5 s; every gen <=5 s | active | D25 |

## 9. OMAR_FEEDBACK_LOG (verbatim copy of learning/OMAR_FEEDBACK_LOG.md)

# OMAR FEEDBACK LOG
Every fix or critique Omar has given (all products, all time) → rule → enforcement. Times PT. Merge-append only; never delete rows (supersede instead).
Sources: rules_core.csv (R01–R30, Mac chat history), DECISIONS.md (D1–D75, D-NOLOOP, D-NOSPLICE, D44b–d), failure_memory.csv, PLAYBOOK.md, parent chat transcript (t206–t223).
Enforcement key: gates.py G1–G19 (`gates.run_all`), qa.final_checks gates, speech_gates SG1/SG2, prompts.lint, config.*, or `manual`.

| # | Date | Omar (quote/paraphrase) | Product | Rule | Enforcement |
|---|---|---|---|---|---|
| F01 | 2026-10-01 | "the start frames are everything… if it looks like AI slop… shadow ban" | all | Start frames are the #1 quality lever; look like a genuine iPhone photo | G8 (Omar approves frames before any video) + manual |
| F02 | 2026-09-27→10-18 | "shot on iphone… no blur, nothing cinematic, no warm lighting… remember this forever"; start frames keep it too | all | iPhone 12 realism suffix on EVERY prompt (video + stills) | config.ensure_suffix + QA rejects missing suffix (D32/D35) |
| F03 | 2026-10-04 | "US flags in the background of every single clip" | all | US flag in every clip | prompts.with_flag + prompts.lint "no US flag" |
| F04 | 2026-10-08 | "NEVER BURN IN CAPTIONS" | all | No burned captions/music in generations | qa.raw_gen_checks OCR burned-text check (D43) |
| F05 | 2026-10-03 | "i already told you to always generate audio"; keep natural clip sound (real voices, cheering, gasps, environment), never fake/weird SFX | all | Native ambient audio on every gen, no music, no fake SFX | prompt builder; G6 fake-SFX BLOCK |
| F06 | 2026-09-24 | Ad Multiplier variants get own fresh audio (shadowban) | variants | Never reuse original track on variants | manual (variants.py fresh gen) |
| F07 | 2026-10-07 | "combine clips… same prompt" | all | Pack 2 shots per 4 s gen | planner (D20) + qa.packed_cut_check |
| F08 | 2026-10-07 | "straight cuts no fades, different angles" | all | Hard cuts only, new angle each cut | omar_style.compare (no fades) + packed_cut_check |
| F09 | 2026-10-10 | "8 seconds? that can be done in 5 tops" | all | Every gen ≤5 s; hook ≤5 s; Omar-approved exceptions only (JollyGlow combo garage afters 6 s, D71) | **G18** + learning/approvals/long_gens.json; D35 hook>5s BLOCK |
| F10 | 2026-09-29 | "hook is seedance 2.5 1080p, rest 720p" | all | Only hook gens 1080p | G4 |
| F11 | 2026-10-06 | "no kling what so ever… seedance only"; t206 "seedance 2.5 is the best by a landslide", no model comparisons | all | Seedance 2.5 only | **G16 (new)** |
| F12 | 2026-10-09 | "only use gpt image 2" | all | GPT Image 2.0 only for stills | **G16 (new)** |
| F13 | 2026-09-29 | "we dont need end frames ever" | all | No end frames, ever (RESOLVED 2026-10-19: rule stands; the TrumpGlow A end_image fix in failure_memory is retired) | **G16** |
| F14 | 2026-09-28 / 10-18 | no regen without permission; later: auto re-roll only on absurd failure ≥0.9, max 1 | all | Re-roll policy D33 | qa.reroll_decision |
| F15 | 2026-10-03 | "always list cost"; budgets 150/175/100 variants; JollyGlow cap 400 | all | Cost listed per output; stay under budget (default 200) | G5 quote + **G17 (new)** |
| F16 | 2026-10-08 | active working product on top of any display | all | Top unit lit | manual (prompt rule D24) |
| F17 | 2026-10-08 | time of day must make sense chronologically | all | Time progresses | qa.logic_check / manual |
| F18 | 2026-10-06 | "shocked the whole time… slow and robotic" | all | Natural motion, no permanent shock face | G13 motion + ai_look + manual |
| F19 | 2026-10-10 | FaceTime whip + whoosh unnatural; real FaceTime UI | FaceTime fmt | No whip/whoosh | G6 fake-SFX BLOCK + manual |
| F20 | 2026-10-09 | "just look like a target" | store hooks | Store look-alike, no logos | manual (D12/D26) |
| F21 | 2026-10-13 | "ad multiplier… the whole fucking video"; Christmas bg adjustments | variants | Ad Multiplier = remake whole video | manual (D21) |
| F22 | 2026-09-28 | variants changed enough to re-upload from another page | variants | ≥4 of 7 axes changed | variants.py + qa.originality_gate |
| F23 | 2026-10-03 | thoroughly listen and watch references | all | Watch+listen fully before working | manual |
| F24 | 2026-10-07 | gasoline pour + ignition before snacks | MerryFire | Build order | qa.logic_check / manual |
| F25 | 2026-10-08 | "relatable… patio/backyard of a home" | all | Relatable homes, no nonsense props | logic_check world anchors / manual |
| F26 | 2026-10-09 | hook needs wow factor; stand out from slop | all | Wow-factor hooks | manual (G7 POC) |
| F27 | 2026-10-05 | "these are all organic videos, i dont even do ads" | all | Organic posts framing | manual |
| F28 | 2026-10-08 | captions from the Caption Bank | all | Proven caption patterns | G7 POC citation |
| F29 | 2026-09-29 | gondola hook = first-person POV | BrickHood | POV unboxing hook | manual (worlds.py) |
| F30 | 2026-10-08 | lights in start frame before unfold, reproduced correctly | JollyGlow/all | Hero prop matches reference | CLIP fidelity (rank-only) + manual |
| F31 | 2026-10-18 | race-based casting excluded | all | No race/ethnicity casting | config.sanitize_casting + QA casting_violations + prompts.lint |
| F32 | 2026-10-18 | JK flip on fake-store hooks | store hooks | "JK, we make them" flip | manual |
| F33 | 2026-10-18 | 20 % innovation; t214 test new concepts from POC on own (core rule) | all | ≥1 experiment slot; every concept cites POC | planner D16 + G7 |
| F34 | 2026-10-18 8:32 PM | recency only for external reels | research | RECENCY on external only | config.RECENCY |
| F35 | 2026-10-18 9:39 PM; 2026-10-19 (t211, t218) | "there should never ever be a trace ever"; anything generated, images included, gets AI metadata stripped | all | Strip C2PA/AI/encoder/codec traces from every delivered file (video + image) | qa.final_checks metadata BLOCK + deliver.py chokepoint (D44–D44d) |
| F36 | 2026-10-18 9:48/9:50 PM | drop voice-layer suggestions except AI-doubt proof; drop safety holds | all | PROOF shot per video only | QA FIX on missing PROOF (D49/D50/D51) |
| F37 | 2026-10-19 | v3 AC/DC silent lead-in; song from frame 0 | all | Song starts at t=0 at proven in-point | G1 + songlay.song_start_check |
| F38 | 2026-10-19 | B "POV…Thanksgiving" too long, not catchy | TrumpGlow | Hooks ≤8 words, proven formats | G2 |
| F39 | 2026-10-19 9:05 PM | store-aisle ban and 😳/🎅 block "stupid" | all | No ban against own proven data | G3 proof_guard |
| F40 | 2026-10-19 | no phonk; iOS emoji only; real ambient only | all | Bans | G6 |
| F41 | 2026-10-19 | show start frames first | all | Frames approved before video | G8 |
| F42 | 2026-10-19 | shared enterprise workspace; only our job ids | all | Spend from our ledger only | G5 our_spend |
| F43 | 2026-10-19 9:20 PM | staged scenes may look at camera; organic not | all | Gaze follows scene logic | G9 + logic LG1 |
| F44 | 2026-10-19 9:17 PM | JollyGlow cap 400; chain afters in one clip | JollyGlow | Chain 2–3 afters per clip | manual (planner) + G17 budget field |
| F45 | 2026-10-19 9:25 PM | no "Get yours"/URL on screen; comment CTA OK | all | Link in caption/bio only | G10 |
| F46 | 2026-10-19 | B 3M peel "way too slow, long and boring" | TrumpGlow | Opener/peel fast, ~2 s, speed up 1.5–2x (WINS over F49) ; PurrVenture backyard-cam opener ~4 s allowed (t219) | G11 (WARN) |
| F47 | 2026-10-19 | chip-glint showcase shot | TrumpGlow | Action over showcase | G12 |
| F48 | 2026-10-19 | (failure_memory) no cut between door opening and reveal | TrumpGlow | Reveal continuous from trigger | manual |
| F49 | 2026-10-19 | (failure_memory) peel too fast at 1.2x | TrumpGlow | SUPERSEDED by F46 (newer note wins: fast, ~2 s) | — |
| F50 | 2026-10-19 | "make editing on POINT, as good as me" | all | Edit within Omar CapCut ranges | omar_style.compare in qa.final_checks |
| F51 | 2026-10-19 | hook too long → speed up, never cut; never cut dialogue | all | Hook speed 1.0–1.5x; dialogue complete | omar_style hard miss + SG1 |
| F52 | 2026-10-19 | voices buried under song | JollyGlow | Speech ≥6 dB over music (+8 LU) | SG2 + omar_style |
| F53 | 2026-10-19 9:37 PM | captions max 2 rows; everyone counts together | all | ≤2 rows; countdown spoken by all groups | CAP2 caption_lines_gate + logic LG7 |
| F54 | 2026-10-19 | iOS emoji; CapCut preset size 15 stroke 0.09, y≈0.20 | all | Text style | omar_style.compare / plugins capcut_text_preset |
| F55 | 2026-10-19 | TrumpGlow A first close-up "repeats" | all | Never loop/repeat footage | qa.final_checks repeat_detect |
| F56 | 2026-10-19 | jump cut inside one take | all | No same-take splice | qa.final_checks splice_detect (needs timeline) |
| F57 | 2026-10-19 t206 | do it all yourself; realistic product shots, real footage reveals | all | Realism stack (refs, grade, simple motion, AI-look QA) | G13 + ai_look in final_checks |
| F58 | earlier (grade note) | "do not make the video grainy or sharp in any way" | all | iPhone grade subtle; off if Omar objects | manual (plan.grade) |
| F59 | 2026-10-19 | US market | all | US English/US cues | prompts US cues (D46); P-AUD-5 still PROPOSED → manual |
| F60 | 2026-10-19 t207/t208 | organize Drive per product, clear names; trash rejected old variants | all | Delivery layout + replace-not-stack | deliver.py/drive_layout.json + manual |
| F61 | 2026-10-19 t214/t217 | study competitor harder; get Instagram viewed; follow proof (~4 s opener for PurrVenture) | PurrVenture | Competitor proof drives format | G7 + manual |
| F62 | 2026-10-19 t220 | A ACDC weird cut still there after Free Bird was fixed | TrumpGlow | Same-take splice gate runs on EVERY song variant with its own timeline | qa.final_checks BLOCKs when no timeline is passed + qa.final_checks_variants() |
| F63 | 2026-10-19 t220 | clip "lingers wayyy too long for how uninteresting it is" | TrumpGlow/all | Non-key shots ≤~2.2 s (WARN >2.5, BLOCK >3.2) | **G15 (new)** |
| F64 | 2026-10-19 t220 | "Vs. part… should only come during the mid. never in the first" | all | Vs only in mid card | **G14 (new)** |
| F65 | 2026-10-19 t220 | pensive 😔 over 💔, pair with 🇺🇸 | TrumpGlow/all | Sad beat = 😔 + second emoji | **G19 (new, WARN)** |
| F66 | 2026-10-19 t221–223 | take note of every fix to improve Hookforge | all | Every fix → this log + gate/test | process (this file) |
| F67 | playbook | never engagement-bait questions or comfort adjectives | all | Caption bans | audience_fit caption score / manual |
| F68 | playbook | keep change list 1–2 items + "Remove the caption" in recreates | recreate | Recreate = 1–2 changes | recreate.check (D45) |
| F69 | playbook | product/lining colour and box brand never drift | all | Product consistency | CLIP fidelity + consistency line + manual |
| F70 | stored fact | song section must be the part people actually use | all | In-point = proven offset (own CapCut / verified ref), never an arbitrary section | G1 (in-point required) + G7 |
| F71 | stored fact | afters animated on the product and differ from each other | decor | Every after animates; no repeated after design | **G20 (new)** |
| F72 | stored fact | every element (song, start point, cards, shots) POC-backed; unproven excluded | all | No unproven element in core slots | G7 BLOCK + D38 (unproven = experiment slot only) |
| F73 | stored fact | core job: recreate slightly different originals of his winners shot for shot, not invent scenes | all | Recreate mode default, 1–2 changes, per-shot ref cites | recreate.check + G7 per-shot refs; manual |
| F74 | stored fact | every prompt needs a logic step (no family staring blankly at the camera) | all | Logic check per prompt | qa.logic_check + G9/LG1 |
| F75 | stored fact | one caption per problem scene, then "Vs...", then "Christmas 2026" on the afters | then-vs-now | Card order problem(s) → Vs → Christmas 2026 | **G21 (new)** + G14 |
| F76 | stored fact | song, emoji, caption matched to audience/niche; proven songs first, then trends | all | Niche/energy match; rank own proof > trend > other | D38 music + poc_library.rank_songs + audience_fit + G3 |
| F77 | stored fact | exact original song recording, never a substitute | all | Official recording verified xcorr ≥0.9 vs preview; no covers/remixes | G1 (verified) + fetch_song filters |
| F78 | stored fact | always send a proven-converting caption with each video | all | Post caption present, POC-cited | **G22 (new)** |
| F79 | stored fact | track posting-time patterns | all | Posting-time stats per page | learning/rules_learned.csv PT-*, posting_windows.json; manual |
| F80 | stored fact | prefer free tools | all | Free/open tools first | manual |
| F81 | 2026-10-19 | "the 2nd scene where he's just showcasing the pin… could've made it more engaging (toss it like a coin / put it on the device)" | TrumpGlow B | Product shots need action on the product, never just held up | G12 showcase (plan) + manual frame review |
| F82 | 2026-10-19 | voices audible under the music (countdown, crowd) | Jolly Glow | Dialogue sits about +8 LU over the song | songlay.lay_song(dialogue=…) + omar_style compare (D74) |
| F83 | 2026-10-19 | everyone in the shot says "3-2-1" together | Jolly Glow 3-2-1 | All on-screen people take part in the countdown | speech_gates SG1/SG2 + manual |
| F84 | 2026-10-19 23:22 | "the weird cut is STILL in the ACDC v6" | TrumpGlow A | Cause: G5 ended on a static logo close-up and the next shot (G3) opened on the same framing, so it read as the scene repeating. A cut must change framing, and song variants must share one identical video | qa.final_checks → pacing.near_duplicate_cuts (BLOCK) + qa.final_checks_variants → pacing.variants_identical |
| F85 | 2026-10-19 23:22 | "that clip now lingers way too long for how uninteresting it is" | TrumpGlow A | Non-reveal shots stay under Omar's p90 hold for their role (style.json timing.hold_p90_s: after 1.82 s, before 2.41 s, ending 3.5 s, opener 4.1 s). Only the reveal (or a proven shot) gets the long beat. Trim, or speed up to at most 1.5x; never loop | qa.final_checks → pacing.hold_violations (BLOCK) + G15 |
| F86 | 2026-10-19 23:30 | "😔 was a suggestion, not a hard rule" (correction to F-😔) | TrumpGlow C | Choose the sad/problem-card emoji by POC; pair it. C card 1 = "His last day on my truck.. ❤️🇺🇸", from POC-0255 (Lumi Door "His last day with us.. VS... ❤️", 2.4M, the reference C copies) | G19 POC check (WARN only, never forces 😔) + G14 (Vs never on card 1, BLOCK via qa.final_checks(card_texts=…)) |
| F87 | 2026-10-19 22:18 | "there should never ever be a trace ever" | all | Every file leaves the box only through deliver.stage() + verify_staged() (whitelist metadata + byte scan, no override) | deliver.py + qa.final_checks deliver scan (D44d) |
| F88 | 2026-10-20 9:17 AM | annoyed that PurrVenture v1 start frames were generated without references (ball shape + cat drifted in 7 of 12) | all | NO image or video generation without product AND cast reference images attached (Higgsfield media ids in medias); only exception is a shot whose prompt explicitly says "no product anywhere in frame" / "no people + no cat" | **HARD GATE** engine/hookforge/ref_gate.py, enforced in runner.build_calls/start_run/next_call (no override); test engine/tests/test_ref_gate.py; refs in refs/<product>/ + higgsfield_new_account_media_ids.json |
| F89 | 2026-10-20 9:17 AM | iPhone grade must show no visible grain or sharpening (restates F58) | all | Default grade = "light" (tone only: no noise, no unsharp, softer vignette) | iphone_grade.STRENGTH["light"] default |
| F90 | 2026-10-20 9:27 AM | "cat phasing through the ball" in 2 frames - "these should be caught before he sees anything" | all | Every frame passes a strict full-resolution self-QA before Omar sees it: physics (no clipping/phasing, cat fully inside the zipped ball or fully outside, nothing through the mesh, correct ground contact), cat = ref, product = ref, cast/outfit = ref, flag tiny, gaze, no AI tells. Max 2 regen attempts per frame within cap | **HARD GATE** engine/hookforge/frame_qa.py (record per-frame checklist + reasons; build_sheet refuses unless all pass, re-checks file hash); test engine/tests/test_frame_qa.py |
| F91 | 2026-10-20 (t233) | PurrVenture defaults kept picking Christmas songs / 'Get yours' / unproven emoji | PurrVenture | Per-product POC defaults: song by proof (Mambo No. 5 / Be My Baby), comment CTA 'Comment "PURR"', emoji from the competitor's proven cards | config/poc_defaults.json + product_poc.apply + audience-fit AF1/AF2/AF3 + G10/G19/G22 |
| F92 | 2026-10-20 9:17 AM (t230) | refs should have been loaded from the start | all | Every product has a ref library with manifest (product + cast) auto-attached to every plan | refs_lib.attach in planner.d75 + tests/test_ref_manifests.py + ref_gate (F88) |
| F93 | 2026-10-20 ~9:47 AM | FB captions use 'SAY ...', never 'Comment ...' | all | Every caption/card/hook variant uses SAY "<KEYWORD>"; 'Comment' is refused. PurrVenture caption = SAY "PURR" if you want one! 🐈 | **G23 (new, BLOCK)** gates.g23_say_not_comment + publish._caption_checks refusal + config.BANNED_CTA_WORDS; test tests/test_ref_manifests.py::test_g23_say_not_comment |
| F94 | 2026-10-20 ~9:50 AM | lock each product's cast from the avatars in its proven/top videos; default women, buyer logic wins (Trump/car/patriotic = man, cat = woman) | all | Cast per product locked in refs_lib.CAST + refs/<slug>/cast/cast_*_top.png (frames from the top own reel, caption band cropped, metadata stripped); PurrVenture cast switched to the woman | refs_lib.CAST + manifest.approved_cast + ref_gate (F88) needs a cast ref |
| F95 | 2026-10-20 ~9:47 AM | asked before for a clean TrumpGlow product photo | TrumpGlow | Product hero ref must exist for every product before generation (carbon-fiber projector, Trump/flag projection, rally background, no NFL logos) | refs/trumpglow/product/ + frame_qa.json + manifest |
| F96 | 2026-10-20 ~3:37 PM | brickhood, merryglow lights, merryfire, grinchmelt mug and minionmask are OLD/retired; keep all their cuts, tags/hashtags, captions, stats, sounds and hooks as full reference data for active products; no new content for them | 5 retired | **D117**: config/products.json `active` flag + hookforge/products.py; excluded from concept_lab/rank, e2e, Buffer routing (routing.route raises Retired) and missing-channel warnings; 7 queue items status RETIRED; corpus untouched; perf_feedback uses their stats as the pooled prior |
| F97 | 2026-10-20 ~4:09 PM | grinch_robe, heatjams and cozyjams are also retired; active = jollyglow_curtain, trumpglow, purrventure_carrier only; retired stay as full reference data | robe family | **D131**: products.json inactive; routing removed (merryjammies_ig_b2 idle); 3 queue items RETIRED → _archive; calendar cadence redistributed to the 5 remaining pages; heatjams URL question moot |

