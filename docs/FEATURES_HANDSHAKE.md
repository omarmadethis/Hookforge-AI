# data/features <-> engine handshake (written by the engine lead, 2026-10-18 ~10:50 PM PT)

The features worker owns data/features/ and data/hookforge.db. The engine never writes there and never stops its jobs.

## How the engine reads the DB
- `engine/hookforge/reels_db.py` opens `data/hookforge.db` read-only (`sqlite ... mode=ro`). A failed or locked read falls back to private/corpus/corpus.csv.
- `python3 -m hookforge.reels_db` (run by `learning/update.py`) reviews the DB against the corpus and writes `learning/db_review.json`.
  The DB becomes the default source only while the latest review passed for the file on disk (same mtime and size). Every rewrite of the DB triggers a re-review on the next update run.
- Merge policy: identity fields (key, page, page_code, product, category, hook_text, format, views, posted_pt) keep the corpus values. DB measured features are added as new columns, and DB values fill corpus gaps but never overwrite them. The DB hook_family is kept as `hook_family_db` (it uses the features codebook).
- Review checks: required columns, all 78 own reels present, views within 2% (82/82), unique uid, posted time within 5 min (78/78 with both), externals mapped by reel id from the corpus url/file (72/72).

## Issues found in the DB (for the features worker; nothing blocks)
1. `format_ref` is empty for all labelled rows, so format comes from the corpus overlay.
2. `corpus_key` is empty for the 72 externals. The engine maps them by reel id, but filling corpus_key (EXT-01..72) would be cleaner.
3. `page_code` is NaN for externals (the corpus uses EXT).
4. `page` holds a reel shortcode instead of the page name for 2 merryglow IG rows (e.g. 'DegGRHtMucS'; the corpus has merryglow.official).
5. `schema_version` is empty.
6. `category` is finer-grained than the corpus (accessory_skimask vs accessory). That's fine: the engine keeps the corpus category.

## Features worker response (2026-10-18 ~11:50 PM PT)
Layout unchanged: same file (data/hookforge.db), same tables (reels, text_events, cuts, per_second, codebook), same uid scheme; columns only added. A no-write dry run of `reels_db.review()` against the rebuilt DB passed all checks.
- Fixed #2/#3: externals and VR rows now carry corpus_key (EXT-01..72, VR-01..07) and page_code EXT, mapped by platform reel id against private/corpus/corpus.csv.
- Fixed #4: VR rows whose page held a shortcode take the corpus page name (merryglow.official).
- Fixed #5: `schema_version` = `features-2026-10-18b` on every row (bumped whenever columns or tables change).
- #1 (format_ref) is still open: the features DB has no format labels; keep the corpus overlay.
- New rows: 21 merry.jammies IG reels (`dup_note` starts `ig_extra`; metrics from audience/ig_reel_audience.csv). Six of them map to corpus rows by shortcode; the other 15 have no corpus_key, so merged() appends them as db_row=True, corpus_row=False. Reference library: 169 rows (source `reference`, not in LABELLED).
- New columns: cc_* (CapCut primary joins; HJ-13/MJIG-04 unjoined), covered_* (style/covered_hooks.csv), platform_audio_label, audio_id_confidence. See data/features/SCHEMA.md "Side joins".
