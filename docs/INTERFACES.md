# Hookforge interfaces (schemas every workstream writes to)
Owner: lead architect. Version 1 · 2026-10-18 PT. Change a schema only by editing this file + DECISIONS.md.

Join key everywhere: **`reel_key`** (stable, anonymised, e.g. `HJ-01` = HeatedJammies FB reel with the most views,
`MG-03`, `EXT-17`, `VR-02`, `REF-041`, `LIB-120`, `MAC-0007`). The mapping `reel_key -> platform reel id / URL / page`
lives ONLY in `private/` (gitignored). Engine code (`engine/backtest/corpus.py`) already assigns these keys; teammates
must reuse them (read `private/corpus/corpus.csv`, column `key`) instead of inventing new ones.

Canonical vocabularies (import, don't copy): `engine/hookforge/taxonomy.py`
- `format_id` in F01..F19, F99 (`FORMATS`, `FORMAT_TITLES`, `format_of(hook_family, archetype, hook_text, vo321)`).
- `category` in wearable_gift, decor_light, decor_fire, decor_mug, accessory, pet, gadget, home, other (`norm_category`).
- psychology flags (0/1): `PSYCH` = curiosity_gap, forbidden, recipient, identity_callout, store_surprise, jk_twist,
  social_proof, gift_framing, humor, transformation, envy, urgency, countdown, cozy_payoff, squad (`code_psych(...)`).

---
## 1. Feature DB (Phase A teammate) -> `data/hookforge.db` (SQLite) + `data/features/*.csv`
### table `reels` (one row per reel/video)
| column | type | notes |
|---|---|---|
| reel_key | TEXT PK | see above |
| source | TEXT | own, external, viral_research, reference_library, library, mac |
| platform | TEXT | FB, IG, TikTok |
| page_code | TEXT | HJ, MG, MGS, MF, MC, BH, PV, MJIG, EXT, LIB, MAC (no page IDs) |
| category, format_id, hook_family, opening_archetype | TEXT | vocab above |
| product | TEXT | generic product noun |
| hook_text | TEXT | exact on-screen text at 0 s; multi-card joined with ` → ` |
| posted_pt | TEXT | `YYYY-MM-DD HH:MM` PT |
| page_day, product_day | REAL | days since page / product first post |
| views | REAL | FB grid/Insights views, IG plays, TikTok playCount (platform not comparable!) |
| three_sec_rate, avg_watch_s, avg_watch_pct, completion, dropoff_s | REAL | Insights (NULL if unknown) |
| shares, likes, comments, saves, profile_visits, reach | REAL | where available |
| orders_per_1k, sessions_per_1k, net_per_1k | REAL | relative sales only (no absolute $ / order counts) |
| paid_flag | INT | 1 if TikTok ad/Spark flag or known boost |
| file_relpath | TEXT | path relative to /workspace (private) |
| psych flags | INT | one column per `PSYCH` entry |
| coder | TEXT | `rule` (code_psych) or `human:<initials>`; human codes go in extra cols suffixed `_h` |
### table `measures` (engine extractor output, one row per reel_key)
Produced ONLY by `engine/hookforge/measure.py` (same code runs on new drafts, so backtest compares like with like).
Columns: duration, width, height, fps, n_shots, first_cut, cuts (JSON list s), cut_fracs, last_shot_start_frac,
last_shot_s, max_shot_s, avg_shot_s, motion_0_1, motion_1_3, bright_0, contrast_0, sat_0, colorful_0, warmth_0,
audio_start_s, lufs, true_peak, end_drop_db, text0_n_words, text0_center_y_frac, text0_height_frac, text0_n_lines,
text_change_times (JSON), product_share_0, product_prob_0. Cache: `private/cache/measure/*.json`.
Teammates may ADD measured columns in `data/features/<name>.csv` keyed by reel_key; never overwrite engine columns.

## 2. Reference library (Viral Research bot) -> `/workspace/research/reference_library/`
`index.csv` columns (already in use): id, url, platform, views, likes, shares, comments, post_date, checked_date,
page_handle, page_followers, product, product_category, format, on_screen_hook_text, length_seconds, audio, is_paid,
ai_label, caption, video_file, notes. Requested additions: `format_id` (taxonomy), `hook_family`, `category`.
Sidecar JSON `videos/<id>.json`: same fields + `shot_cuts_s`, `text_cards` [{t_start,t_end,text}], `transcript`.
Corpus ingests it automatically (`corpus.reference_library()`), keys `REF-###` in index order (append-only!).

## 3. Format library (Phase C teammate) -> `formats/`
- Human spec: `formats/F##_<slug>.md` (template in this section).
- Machine spec read by the engine: `formats/formats.json` = list of objects:
```json
{"format_id":"F02","slug":"fake_store_pallet","title":"...","tier":"A|B|C",
 "categories":["wearable_gift","pet"],"body_override":null,
 "evidence":[{"reel_key":"HJ-04","views":1400000,"note":"Grinch X Target, pallet push-in"}],
 "hook_formulas":["{character} X {store} 😳🎄❄️"],
 "hook_lines":[{"text":"Grinch X Target 😳🎄❄️","tag":"P","source":"HJ-04"}],
 "text_cards":[{"t_start":0,"t_end":"activation","text":"{hook}"},{"t_start":"activation","t_end":"end","text":"JK, We make them🎅🎄"}],
 "hook_prompt_recreate":"Recreate <<<video_1>>> 1:1 ...","hook_prompt_original":"...","startframe_prompt":"...",
 "body_shot_overrides":{"HOOK":"..."},"music":[{"song":"...","section_s":0}],
 "captions":["Get yours👉{url}"],"say_keywords":["COZY"],"variants":{"exploit":[],"explore":[]},
 "kill_rule":"...","psych":["store_surprise","jk_twist"]}
```
Rules the engine enforces regardless of the spec: iPhone 12 suffix last, hook = own 4 s 1080p gen, body = 720p packed
2 shots/4 s with hard cut, SAY not COMMENT, no burned text in generations. Slots: {product} {product_look} {brand}
{recipient} {recipient_plural} {audience} {store} {store_look} {room} {feature_1} {feature_2} {activation_action}
{activation_result} {payoff_scene} {disaster} {era_year} {occasion} {character} {keyword} {url}.
If `formats/formats.json` is absent the engine uses `engine/hookforge/format_defaults.py`.

## 4. Analytics (Phase E teammate) -> `analytics/`
Reads `data/hookforge.db` + `learning/ledger.jsonl` + `learning/state.json`. Writes `analytics/dashboard/index.html`
and PNGs. Must not write outside `analytics/`.

## 5. Learning ledger (lead) -> `learning/ledger.jsonl` (append-only, one JSON per event)
`{"ts":"ISO PT","event":"generation|take_review|edit|qa|backtest|post|insights","run_id":"...","video_id":"...",
 "product":"...","format_id":"F02","hook_text":"...","prompt_pattern":"T7|T1|...","model":"seedance_2_5","res":"720p",
 "usable":true,"notes":"...","qa_score":87,"bt_pred_band":"20-80K","views":12345,"three_sec_rate":0.41,
 "avg_watch_s":7,"shares":0,"profile_visits":0,"orders_per_1k":null,"experiment_id":null}`

## 6. Mac mining (executor) -> `/workspace/team/mac/`
`out/rules.csv` (id, rule, verbatim_quote, date_PT, source_session_or_file, scope, evolution_or_superseded_by,
playbook_conflict_or_note), `out/prompts.csv`, `out/mac_videos.csv`, `REPORT.md`. Mac finished videos enter the
corpus as source=`mac`, keys `MAC-####` (by `idx`).

## 7. Run artefacts (engine) -> `runs/<run_id>/` (gitignored)
`plan.json` (brief → plan), `prompts.json`, `edit_plan.json`, `final.mp4`, `qa.json`, `backtest.json`, `caption.txt`.


## Added 2026-10-18 (v1.1)
### Recency / freshness (D28 FINAL): every evidence row carries `post_date` + `source`
- `weight = hookforge.config.recency_weight(age_days, source)`.
  - Own sources (`own, capcut, prompt, insights, shopify, library`) are always 1.0.
  - External sources (`external, research, reference tiers`) get 1.0 for ≤14 d, exp decay τ=7 d, floor 0.05 (90+ d = weak prior).
- The single knob is `config.RECENCY`.
- Trend rules supported by own data need no fresh row. External-only rules carry `freshness ∈ {fresh, aging, prior-only}`.

### Reference library tiers (Viral Research schema 1.0, D31)

- **`inclusion_rule` (D34)** sits on every library row and sidecar. `14d_1m` = last 14 days, 1M+ views, weighted by `config.RECENCY`. `90d_20m` = last 90 days, 20M+ views (mega viral), exempt from decay with weight `config.INCLUSION_WEIGHT["90d_20m"]` (0.95). Call `recency_weight(age, source, inclusion_rule=row.inclusion_rule)`.
| file | contents | used by |
|---|---|---|
| `research/reference_library/index.csv` | 1M+ reels posted ≤14 days ago (fresh, small n) | **reference selector**: recreation + trend picks come from here first |
| `research/reference_library/archive.csv` | older 1M+ reels | backtester (recency-weighted); selector fallback, labelled "aging/prior" |
| `research/reference_library/near_misses.csv` | 300K–1M reels in the 14-day window | backtester (recency-weighted) + contrast set |
Reference keys stay `REF-###` across tiers. A reel moving index → archive keeps its key.

### CapCut edits (D29): `private/edits/` (private: file names and paths)
- `edits.csv`, one row per draft: `draft, created, updated, duration, width, height, fps, n_shots, first_cut, cuts (json s), cut_fracs, last_shot_start_frac, n_hf_clips, hf_clips, speed_changes, text_cards (json [{t,dur,text,y,size}]), hook_text, n_text, text_change_times, text_y, text_size, song, song_offset_s, song_t_start, clip_audio_volume, reel_key (primary join), join_score, days_to_post, primary, variant_of, views`
- `edit_segments.csv`: one row per segment (video/text/audio) with timeline + source times.
- `edit_clips.csv`: placed clip → `gen_id` → model/resolution/prompt (generation logs).
- Public aggregate: `engine/backtest/data/capcut_stats.json`.

### Evidence from the Mac (D17–D27)
- `private/evidence/prompts_ledger.csv`: 1,926 prompts, casting-sanitized. Columns: `gen_id, reel_key, join_source (capcut|mac), used_in_posted, views, post_date, gen_date, has_suffix, packed, us_flag, scope=craft`.
- `learning/rules_core.csv`: Omar's rules verbatim plus `status, hookforge_resolution, freshness_scope`. The production run reads this before anything else.

### CapCut export plan block (edit_plan.json → `capcut`)
See the `engine/hookforge/capcut_export.py` docstring (`shots[], texts[], music{file, offset}, media_root_map`).
