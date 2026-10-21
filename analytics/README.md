# Hookforge analytics (Phase E)

A self-contained, regenerable dashboard built from one command. Every number traces to a file on
disk, and the Provenance panel at the bottom of the dashboard lists each input file with its row
count and modification time.

```bash
python analytics/build_dashboard.py            # -> analytics/dashboard.html  (+ PNGs in analytics/screenshots/)
python analytics/build_dashboard.py --public   # -> analytics/dashboard_public.html (for the shareable repo)
python analytics/build_dashboard.py --no-png   # skip PNG export (PNG needs kaleido + Chrome)
python analytics/tests/test_ingest.py          # ingest smoke test (synthetic TEST rows, temp dir only)
```
Requires Python 3.10+, pandas, numpy, scipy and plotly (`pip install plotly`; add `kaleido` for PNGs).
The HTML embeds plotly.js (about 5 MB), so it opens offline and can be emailed as-is. A build takes about 30 s.

## Adding a page's Insights (e.g. HeatedJammies), one command
1. In Meta Business Suite, go to Insights → Content → Reels, set the date range, and Export → CSV.
   The browser-scraped tables the team made also work.
2. Run:
```bash
python analytics/ingest_insights.py --page "HeatedJammies" --code HJ ~/Downloads/export.csv && python analytics/build_dashboard.py
```
- Columns are matched by alias (Business Suite names such as `Publish time`, `3-second video views`,
  `Average Seconds viewed`, `Link clicks`, and the team's `date_2026`, `3s_views`, `avg_watch_time "7s"`, ...).
  Values like `1,029`, `4.6M`, `59%`, `1h 36m` and `0:05` are parsed. Nothing is estimated, so a missing column stays empty.
- **Page/account ID columns are dropped** (scrub rule).
- Re-ingesting is safe. Rows are keyed by post ID (or reel URL, else posting minute), newer exports overwrite older
  numbers for the same reel, and new reels are appended. Output: `analytics/data/insights/<CODE>.csv`.
- Per-reel retention tables (avg % watched, completion, biggest drop-off) attach with `--retention`.
  They match by post ID or URL, else by exact view count.
- Export times are taken as PT. Use `--tz-offset-hours` if an export was made in another zone.
- A page that isn't in the corpus/DB yet still appears in the timeline and page table, marked
  "[Insights only]", and in the retention panel. Once the corpus/DB builder picks it up it joins every leaderboard.
- `python analytics/ingest_insights.py --seed-existing` rebuilds the 5 page files from the team's existing captures
  (Merry Glow, Brick Hood, Merry Carrier, Merry Glows, MerryFires).

## Data sources and loader order
`hf_load.load_reels()` uses the first source that exists. The dashboard header shows which one it used and warns when it isn't the DB.
1. `hookforge/data/hookforge.db`, table `reels` (teammate DB). Column names are adapted by alias
   (`views/plays`, `posted_pt/posted`, `format`, `hook_family`, `page_code`, `source`).
2. `hookforge/private/corpus/corpus.csv` (Phase A corpus, built by engine/backtest/corpus.py). Library rows have no views and are excluded.
3. `hookforge/engine/backtest/data/corpus_public.csv` (the shareable corpus written by corpus.py; the legacy path `analytics/data/reels.csv` is also accepted).
4. `team/hooks/hook_features.csv` (raw fallback).

Enrichments are joined by reel-ID suffix, else by a unique (page, views ±2) match. The join counts appear in Provenance.
- First-frame features: `team/hooks/hook_features.csv`
- Adjusted feature effects: `team/hooks/feature_screen_census.csv`
- Shot timing: `team/body/reels_summary.csv`, `team/body/shots.csv`
- Insights: `analytics/data/insights/*.csv`
- IG Insights: `team/instagram/merryjammies_ig_reels.md`
- Shopify aggregates (no customer data): `team/shopify/{daily,hourly_pt,family_estimates,reel_alloc}.csv`, `merryglow/…`, `brickhood/…`
- Experiments: `learning/experiments.csv`, else the example schema

## Panels
| Panel | What it answers | Statistics |
|---|---|---|
| What to make next | Which formats to exploit or explore, per category, plus production guardrails | Fixed tier rules (below), Wilson CIs, Fisher p |
| Per-page & per-product | Views over time per page/product; freshness decay vs product age | Bootstrap median CI, Wilson hit rate, Spearman + permutation p |
| Views vs shares vs profile visits vs sales /1K | Store outcomes over time; orders/1K per reel and per hook family; engagement per 1K | Allocation intervals from the Shopify workstream |
| Hook family leaderboard | FB own reels by hook family | Median (90% bootstrap CI) + hit rate (Wilson 95%), grey when n<5 |
| Format leaderboard | FB own reels by format (taxonomy F01–F19), plus how many external organic reels reached ≥1M | Same as above |
| First-frame features | Adjusted multipliers (team model, read not refitted) + raw scatter | Within-page permutation ρ |
| Shot timing | Length, shots, average shot, first cut, payoff shot, tempo vs views; shot durations by role, hits vs non-hits | Within-page ρ |
| Retention | Avg watch and 3-s rate vs views per page; benchmarks for hits vs non-hits; top-reel detail | Within-page ρ (pooled is misleading, per hooks REPORT §6) |
| Posting hour | 3-hour bins (PT) of views and hit rate; night vs day; when buyers check out | Wilson, Fisher |
| Experiment tracker | Reads `learning/experiments.csv`; variant/control ratio; innovation share vs the 20% target | – |
| Provenance & cross-checks | Every input file; totals recomputed against the reports | PASS/MISMATCH table |

**Definitions:**
- **Hit:** ≥50,000 views (`engine/hookforge/config.py:HIT_ABS_VIEWS`).
- **Leaderboards are FB-only.** IG is kept for cross-platform pairs, as in the hooks report, because many IG files are re-posts.
- **"What to make next" tiers:**
  - EXPLOIT: own n≥3 and Wilson lower bound ≥15%.
  - EXPLORE: ≥2 external organic reels ≥1M and own n<3. These fill the 20% innovation budget.
  - AVOID as lead: own n≥3 with 0 hits.
  - WATCH: everything else with n≥3.
  - INSUFFICIENT DATA: the rest.
- Every rule is printed on the panel.

**Honesty rules built in:**
- Every chart and table shows n, and groups with n<5 are greyed.
- External reels are labelled as survivorship ("proof of reach, not a hit rate").
- Per-reel sales are labelled as allocations.
- Experiment example rows have no outcomes and are excluded from the stats.
- RNG seed 7 makes bootstrap and permutation results reproducible.

## Cross-checks (recomputed on every build → `data/crosschecks.csv`)
Results of the 2026-10-18 build:

| Check | Computed | Report | Result |
|---|---|---|---|
| Merry Glow orders | 33 | 33 (merryglow_REPORT) | PASS |
| Merry Glow net sales | $3,224.61 | $3,225 | PASS |
| Merry Glow sessions | 14,039 | 14,039 | PASS |
| Brick Hood orders | 22 | 22 (brickhood_REPORT) | PASS |
| Brick Hood net sales | $911.74 | $912 | PASS |
| Brick Hood sessions (raw ShopifyQL daily, store TZ) | 958 | 958 | PASS |
| Brick Hood sessions in `brickhood/daily_pt.csv` | 920 | 958 | INFO: known gap, see below |
| Merry Jammies orders (sales analytics) | 948 | 948 (950 per GraphQL; 6 cancelled, 10 refunded) | PASS |
| Merry Jammies net sales | $91,671.94 | $91,672 | PASS |
| Merry Jammies sessions | 126,309 | 126,309 (summary_numbers.json) | PASS |
| IG Ddii6mOKO2G plays / shares | 4,626,610 / 15,140 | same (IG note) | PASS |
| IG DdK34IiqRx4 profile visits | 2,676 | 2,676 | PASS |
| IG reels with full Insights | 6 | 6 | PASS |
| Own reels in corpus | 78 | 78 (hooks REPORT) | PASS (75 have views; the 3 Purrventure reels have none) |

**Known definition differences:**
1. **Brick Hood PT-hourly sessions (920 vs 958).** `brickhood/analyze.py` blanks hourly sessions after Oct 8 16:00 PT and
   before Sep 26 17:00 PT (lines 16–18), so the PT daily file sums to 920. The 958 total comes from the raw ShopifyQL
   daily file in store timezone, and that is what the cross-check uses. The store-outcome chart uses the PT file, so its Brick Hood session line stops at Oct 8.
2. **Corpus IG note (for the corpus owner).** `engine/backtest/corpus.py:_ig_insights()` doesn't attach shares or profile visits.
   The 6 big IG reels (Sep 7–20) aren't among the 12 IG reels in the corpus. This module parses the note directly instead.

## Files
```
analytics/
  build_dashboard.py      one-command build (all panels)
  hf_load.py              adaptive loaders + provenance log
  hf_stats.py             Wilson, bootstrap median, (within-group) permutation Spearman, Fisher
  ingest_insights.py      Insights CSV -> data/insights/<CODE>.csv
  schemas/experiments.schema.md, experiments.example.csv   (EXAMPLE rows, is_example=1)
  tests/test_ingest.py, fixture_business_suite_TEST.csv    (synthetic TEST rows)
  data/insights/          ingested Insights (gitignored: URLs/captions)
  data/crosschecks.csv    last build's checks (private), crosschecks_public.csv
  dashboard.html          private build (gitignored)
  dashboard_public.html   shareable build: no absolute sales/orders/sessions, page codes instead of names
  screenshots/*.png       key charts (format, first_frame, retention, hook_family, timeline)
```

## Next steps (for whoever continues)
- When `data/hookforge.db` lands, rebuild. If its `reels` table uses other column names, add them to `hf_load.ALIASES`.
- When the learning loop writes `learning/experiments.csv` (schema in `schemas/experiments.schema.md`), the tracker fills in automatically.
- After HeatedJammies Insights are ingested, the HJ retention benchmarks appear. Consider adding page-relative hits (e.g. ≥3× the page median) for new pages.
- Daily routine: export Insights → `ingest_insights.py` → `build_dashboard.py`.
