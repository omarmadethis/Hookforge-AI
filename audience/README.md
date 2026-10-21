# audience/: Hookforge audience-targeting layer
Goal: steer each video's organic distribution toward **tier-1 / high-converting markets** (US first) and away from **non-target regions**, using only data-backed, PoC-tested levers. Owner: audience workstream (Grok Bot executor). Created 2026-10-18 PT.

## Read in this order
1. `LEVERS.md`: what Meta documents about how Reels pick audiences, the 10 levers ranked by evidence, the own-Shopify business case, sources [S1–S17].
2. `data/country_tiers.csv`: country ranking and tiers (external CR/AOV/PPP + own Shopify rates with Wilson CIs).
3. `audience_rules.csv`: rules in `learning/rules_core.csv` format, `status` ∈ proven / supported / hypothesis.
4. `lexicon.csv`: 54 entries (recipient slot fills, US retail, holidays, units/spelling, register, and words to avoid), US/UK-IE/AU-NZ/CA variants, corpus counts, `reach_evidence` (grounded / seen / not_in_corpus) vs `geo_status` (all hypothesis).
5. `audio_regions.md`: US vs UK chart evidence per song, weekly US-trending procedure, proposed `region_skew` column for the music library.
6. `visual_cues.md`: prompt snippets (flags, US homes, US outlets/plates/units, US retail look, Q4 US calendar, presenter), compatible with the iPhone 12 suffix (D32), D24/D26/D27/D37.
7. `EXPERIMENTS.md` + `experiments_proposed.csv`: A/B pairs EXP-AUD-01..08, metrics, power, decision rules, the advisory tier-1 score.

## Key findings (2026-10-18)
- **Proven (own data):** US sessions convert ~10× better than non-target regions (0.51 % vs 0.05 %, non-overlapping 95 % CIs; MG+BH stores, 14.2K sessions). US = 46 % of sessions but 64 % of orders. Other tier-1 markets convert at 0.36–0.46 %.
- **Documented by Meta:** IG Reels uses "how much time viewers from your country spent on this reel" as an engagement feature, so early watch-time by country compounds. FB Pages have a hard **country restriction** setting. IG **Collabs** seed a reel to both accounts' followers.
- **Supported (n=1):** a US creator (Jordan Stallion, ~300K Grinch robe IG reel) produced an excellent US audience while almost all other IG reels did not.
- **Hypothesis (to test):** posting window (US evening vs current night-PT window, which hits Europe's morning), US-skewed audio (Last Christmas is UK #1 / US #4), US-only text cues, extra visual cues, AI US-style presenter.

## Tools (all light; run with `nice -n 19` from `hookforge/`)
| script | does | output |
|---|---|---|
| `tools/text_corpus.py` | hook text + caption + CapCut text from library, external, own, drafts, caption bank | `data/text_corpus.csv` (416 rows) |
| `tools/lexicon_counts.py` | counts ~80 candidate terms (rows, own ≥50K, ext ≥1M, best views, examples) | `data/lexicon_counts.csv` |
| `tools/build_lexicon.py` | curated lexicon + counts | `lexicon.csv` |
| `tools/country_tiers.py` | ranks countries, assigns tiers, own CR by tier | `data/country_tiers.csv` |
| `tools/us_share_drivers.py` | high-US vs low-US reel comparison (Fisher, Spearman+perm), joins corpus + prompts_ledger + `data/reel_cues.csv` | `US_SHARE_ANALYSIS.md`, `data/us_share_features.csv` |
| `tools/tier1_score.py` | advisory 0–100 tier-1 score for a plan (never blocks, D35) | JSON |

## Data and privacy
- Shopify: read-only ShopifyQL aggregates (sessions by `session_country`, orders/net sales/AOV by `billing_country`). Absolute counts and $ live in `private/audience/` (D10). `data/shopify_country_relative.csv` holds shares and rates only. No customer data was pulled.
- Merry Jammies store (largest) is NOT included: the Shopify connector is attached to Merry Glow and Brick Hood; switching would revoke the current token, so we didn't.
- `ig_reel_audience.csv` comes from a separate browser task. When it lands, run `us_share_drivers.py`.
- Language rule: markets are named neutrally ("tier-1 / high-converting", "non-target regions") in every file.

## Integration points (proposals; owners decide)
- Architect: `backtest.run()` adds `audience.tier1_score` as INFO. The prompt builder may insert `visual_cues.md` snippets inside the scene text. The overlay linter WARNs on AV-list words on US-primary posts.
- Learning: add `pct_us, pct_tier1, tier1_sessions_48h` to `learning/experiments.csv` and the ledger `insights` event.
- Music: add `region_skew, us_chart_evidence, ig_us_trending_date` to `learning/music_library.csv`.
- Analytics: an "Audience geography" panel once per-reel country data exists.
