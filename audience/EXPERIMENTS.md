# Audience experiments: proving which levers move views into tier-1 markets
Owner: audience workstream · created 2026-10-18 ~9:50 PM PT · machine-readable arms: `audience/experiments_proposed.csv` (schema = `learning/experiments.csv` + 3 audience columns). **Nothing here is posted or spent without Omar's explicit approval (D9).** All arms come out of the existing 20 % innovation budget (D16); no extra credits beyond normal plans.

## 1. What we measure
| metric | definition | source | status |
|---|---|---|---|
| **pct_us** (primary) | % of a reel's views/accounts reached located in the US | IG app reel insights → Audience → Top countries (the browser task writing `audience/ig_reel_audience.csv`); FB reel insights "Audience" panel in Professional dashboard / Business Suite where shown | per-reel numbers exist in-app only. **The Business Suite Reels CSV export has NO country column** (`analytics/ingest_insights.py` has no country alias). The Graph API gives country ONLY at account level: `GET /{ig-user-id}/insights?metric=reached_audience_demographics&breakdown=country&timeframe=this_week` (also `engaged_audience_demographics`; FB Page country metrics deprecated). Needs the Meta dev app (pending Omar) |
| pct_tier1 | % views from T1-PRIMARY + T1-EN + T1-WEST (`audience/data/country_tiers.csv`) | same | |
| views_24h, views_7d | guardrail: a lever that costs >30 % of views must pay back in tier-1 views | Insights | |
| tier1_views | views × pct_tier1: the number we actually want to maximize | derived | |
| tier1_sessions_48h | Shopify sessions from tier-1 countries in the 48 h after posting, minus the same-hour baseline of the previous 7 days | ShopifyQL `FROM sessions SHOW sessions GROUP BY session_country, hour` (read-only, aggregates only) | Merry Glow + Brick Hood connected; Merry Jammies store not reachable without switching connector auth |
| orders_per_1k (conversion proxy) | orders in the 48 h window / views × 1000, by billing country tier | ShopifyQL `FROM sales SHOW orders GROUP BY billing_country` | no PII pulled, ever |

## 2. Experiments (A/B pairs; one variable per pair; same product, format, page and week)
| id | lever (LEVERS.md) | control | variant | first hypothesis | priority |
|---|---|---|---|---|---|
| **EXP-AUD-02** | L2 US creator seed | our solo post | same concept as an IG **Collab** with a US-based creator (real person, disclosed partnership) | pct_us +20 pp (Jordan Stallion reel is the n=1 proof) | **1** (needs Omar: creator outreach/cost) |
| **EXP-AUD-04** | L2/L7 presenter | faceless product video (current default) | AI-generated US-style presenter (visual_cues.md "Presenter"; no ethnicity, no real likeness; AI label if prompted) holding/using the product | pct_us +10 pp; tests whether a *face/American creator vibe* matters without a real creator's follower seed. If 02 wins and 04 doesn't, the effect is the follower seed, not the face | **1** |
| **EXP-AUD-03** | L4 posting window | 22:00–03:00 PT (current night window, D36) | 14:00–20:00 PT (US evening) | pct_us +10 pp; views may drop (D36 trade-off). Decide on tier1_views, not views | **1** (free: scheduling only) |
| **EXP-AUD-01** | L1 FB Page country restriction | test page as-is for 7 days | same page, "Show only in" = T1 list, 7 days (or a twin page) | non-target views → ~0, pct_tier1 ≈ 100 %; open question: total reach | 2 (Omar must flip the setting; reversible) |
| EXP-AUD-05 | L6 text dialect | neutral wording ("DON'T show this to your mom") | US-only cue ("DON'T show this to the HOA" / "after Thanksgiving dinner" / "Target") | pct_us +5–10 pp | 2 |
| EXP-AUD-06 | L5 audio region | Last Christmas (UK/EU #1) | US-skewed proven song with matching energy (Let It Snow / Bublé / AIWFC), or Jingle Bell Rock in an experiment slot | pct_us +5 pp | 2 |
| EXP-AUD-07 | L7 visual cues | flag only (D24 minimum) | flag + 2 US cues (suburban home, US outlet, Thanksgiving table) | pct_us +5 pp | 3 |
| EXP-AUD-08 | method | — | run 02/04/05 pairs as IG **Trial Reels** first (non-followers only) to pre-screen cheaply, then post winners normally | — | method |

Design rules
- **Fresh renders for both arms** (never re-upload the same file; D21/R06 duplicate risk). Same format spec, same product, same page, posted within the same 48 h; alternate which arm goes first.
- Keep **Meta AI translations OFF** on both arms (LEVERS §0.10).
- Log every arm in `audience/experiments_proposed.csv` → promoted to `learning/experiments.csv` by the learning owner when approved.

## 3. Sample size and decision rules
- Unit = reel pair. Assuming per-reel SD of pct_us ≈ 15 pp (re-estimate from `ig_reel_audience.csv` when it lands), a paired difference of +15 pp needs **≈10 pairs** for 80 % power at α=0.05 (d=1.0); +10 pp needs ≈20 pairs.
- **supported**: ≥8 pairs, median paired diff ≥ +10 pp, sign test p<0.10, views penalty ≤30 %.
- **proven** (D36 standard): Holm-corrected p<0.05 across the AUD family, n≥30 pairs, ≥2 pages agree, and tier1_views (not just pct_us) up.
- **kill**: ≥8 pairs with median diff ≤0 or a views penalty >30 % without tier1_views gain.
- Throughput: 1 innovation slot/product/day ⇒ with 4 active products ≈ 2 pairs/day ⇒ EXP-AUD-02/03/04 reach "supported" in ~2 weeks (before Thanksgiving week, Nov 26 2026).

## 4. The first analysis (runs as soon as `audience/ig_reel_audience.csv` lands)
`nice -n 19 python3 audience/tools/us_share_drivers.py` → `audience/US_SHARE_ANALYSIS.md`. It compares high-US vs low-US reels on: American creator featured, person on screen, US flag in prompts (prompts_ledger), US store/spelling/holiday words, Spanish words, US-evening vs night-PT post hour, psych flags, product, format, hook family and song. Manual coding (who is on screen, US home/store visible) goes in `audience/data/reel_cues.csv` (`reel_key,featured_person,american_creator,recognizable_face,us_store,us_home,notes`). Expect n≈12–20 IG reels → every result is **n-limited / supported at best**; it chooses which experiments run first, it does not prove anything.

## 5. Tier-1 audience score (backtest check proposal, ADVISORY, consistent with D35)
- Code: `audience/tools/tier1_score.py` → `score(plan)` returns 0–100 with itemized checks (US creator/collab 25, US audio 13, US post window 15, US-only text cue 12, flag in all prompts 10, US-style presenter 10, no other-region words 10, US spelling 5). Weights are **priors**.
- Integration proposal for the architect: `backtest.run()` adds `audience.tier1_score` to the report as INFO; it never BLOCKs or FIXes and never changes the verdict (D35). The plan printout shows the 3 cheapest missing checks.
- Validation: after every 10 posted reels with country data, Spearman(score, pct_us); refit weights by logistic/ridge on pct_us once n≥30 (same cadence as D35's re-validation). Promote to a FIX-level check only if it predicts pct_us out-of-sample (Spearman ≥0.3, permutation p<0.05) AND the related levers are supported in §3.

## 6. Data needed from Omar (in order of value)
1. **Per-reel country breakdown** for FB *and* IG reels (screenshot or CSV of "Audience → Top countries" per reel), especially the Jordan Stallion reel and 10+ low-US reels. The browser task is collecting IG; FB is still missing.
2. Approval to run EXP-AUD-03 (scheduling only, zero cost) and EXP-AUD-04 (normal innovation-slot credits).
3. Decision on EXP-AUD-01 (flip FB Page country restriction on one test page for 7 days; reversible).
4. Whether a US creator Collab (EXP-AUD-02) is on the table (budget, which creators; Jordan Stallion terms).
5. Connector access to the Merry Jammies Shopify store (the biggest store) for sessions/orders by country (switching the connector would revoke the current store's token, so we did not do it).
6. Meta dev app (already pending) → weekly account-level `reached_audience_demographics` by country.
