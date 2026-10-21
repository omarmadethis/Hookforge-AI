# voice/: Hookforge customer-voice intelligence layer
Owner: customer-voice executor (2026-10-18 PT). Plain Python (stdlib + curl_cffi for the TikTok collector). Any AI or engineer can continue from this file alone.

## What it does
It mines what buyers and viewers say about our products and our competitors' products, and turns that into:
- **video moves** (on-screen text answering top questions, proof shots, hook lines in customers' own words, objection handling),
- **website fixes** (FAQ, shipping clarity, what's-in-the-box, sizing), and
- **competitor gaps** (where their customers are unhappy).

The output is machine-readable (`voice_rules.csv`, in the same format as `learning/rules_core.csv`) so the planner, QA and backtester can consume it.

## Files
| file | what | shareable? |
|---|---|---|
| `products.py` | product keys (= product_profiles), routing regexes for competitor videos, search terms, `EXCLUDE_URLS` (mislabeled corpus rows) | yes |
| `deid.py` | de-identification applied to every text (handles, display names after @, emails, phones, links, order ids, addresses, "my name is") | yes |
| `codebook.py` | transparent multi-label codebook (EN/ES/PT + some FR/DE/NL): q_where_buy, q_price, q_shipping, q_sizing, q_how_it_works, q_material_safety, q_other, objection, skeptic, ai_callout, too_early, desire, tag_friend, complaint, comparison, humor, praise, emotional | yes |
| `build_targets.py` → `targets.csv` | competitor/reference videos routed to our products (reference library tiers + corpus external rows) | yes (public URLs) |
| `collect_tiktok.py` | public TikTok comments, top ~150–350 per video, no login → `private/voice/raw/tiktok_<id>.jsonl` | raw is private |
| `collect_youtube.py` | yt-dlp search + comments. **Currently blocked from the box** (YouTube bot check); kept for a machine where it works | – |
| `gmail_themes.py` → `support_themes.csv` | Gmail support inbox, READ-ONLY search snippets → aggregated themes + short name-checked quotes. Raw results are deleted after the run | yes (aggregate) |
| `pipeline.py` → `comments.csv`, `voice_stats.json`, `engagement_correlation.csv` | ingest + de-id + classify + aggregate + correlations | yes (no usernames) |
| `make_recommendations.py` → `recommendations.json` | curated alerts and per-product recommendations with evidence counts (edit here) | yes |
| `report.py` → `INSIGHTS.md`, `voice_rules.csv` | human report + engine rules (rules_core columns + `rule_type, engine_slot, evidence_n` + the `plugins.voice()` columns `rule_id, product, type, text, evidence`) | yes |
| `build_browser_queue.py` → `browser_queue.csv` | FB/IG reels needing a logged-in browser (ours by views + competitors + discovery searches) | **gitignored** (our reel URLs) |
| `inbox/` (+ `inbox_TEMPLATE.csv`) | drop browser captures / review exports here | **gitignored** |

## Run (from repo root; light on CPU, run under `nice`)
```
python3 voice/build_targets.py
nice -n 19 /workspace/.venvs/voice/bin/python voice/collect_tiktok.py --max 150   # resumable; ~30 s/video
# Gmail (agent only): save user-Gmail search_threads results as JSON into private/voice/gmail_tmp/, then:
python3 voice/gmail_themes.py            # aggregates, then DELETES the raw files
python3 voice/build_browser_queue.py
nice -n 19 python3 voice/pipeline.py
python3 voice/make_recommendations.py && python3 voice/report.py
```
venv: `python3 -m venv /workspace/.venvs/voice && /workspace/.venvs/voice/bin/pip install "yt-dlp[default,curl-cffi]"`.

## Browser queue (run by an agent that has a logged-in browser; READ ONLY)
For each row of `browser_queue.csv` (P1 first):
1. Open the URL.
2. Open comments and sort by **Most relevant**.
3. Scroll until `max_comments` top-level comments are loaded, or the end.
4. For each comment, record only: `comment_text, likes, reply_count, has_tag (1 if it @-mentions someone), is_page_reply (1 if written by our page/brand), age_text`.
5. Save as `voice/inbox/browser_<YYYYMMDD>.csv` with the `inbox_TEMPLATE.csv` header. Fill `source` (fb_browser|ig_browser), `product_key`, `reel_ref` (copy from the queue: the reel_key for our reels) and `views`.

Never record names, handles or profile links. Never like, reply, react, follow, DM or report. `discovery_search` rows: search reels for the term, take the top 3 with ≥300K views from the last 90 days, record `reel_url, views, post_date` and their comments. Then re-run `pipeline.py` and `report.py`. Rows from our reels become `audience=own`.

## Classification: transparent first, LLM optional
- Rules and keywords (`codebook.py`) are authoritative and auditable. Each comment gets every matching code plus one `primary` code (priority order in `PRIORITY`). Edit the regexes, re-run, and diff `voice_stats.json`.
- **Optional LLM pass (not run; documented).** Take comments with `primary=other` (about 50%) or `q_other`, send them in batches of 100 to any LLM with the codebook labels as an enum, and ask for `{"i":<row>,"codes":[...],"subtopic":"<3-6 words>"}`. Save the result as `private/voice/llm_labels.csv` (row index, codes, subtopic). Merge rule: LLM codes may only ADD codes to rows where the rules found none. Never override rules, and keep `coder=llm` in a separate column. Spot-check 50 rows before trusting it. No API keys go in files.

## Weighting and freshness
- Counts = comments with the code. "Liked share" weights each comment by `1 + ln(1 + likes)`.
- Customer questions and objections are product truths, so there's **no recency decay**. The comment date and the video post date are kept for trend checks. Re-run weekly in season.
- Competitor comments come from TikTok's top-ranked comments (relevance order). They are biased toward jokes and popular takes, so questions are under-represented.

## Privacy (D10)
No commenter usernames, user ids, avatars or profile links are ever stored. Text goes through `deid.py` at fetch time and again at ingest. Gmail: only `search_threads` snippets are read (no bodies, no sending). Raw results are deleted after aggregation, and quotes must pass `safe_quote` (first 1–2 sentences, ≤140 chars, rejected if a Title-Case name pair remains). Order numbers become `[n]`/`[id]`. Shopify was not needed.

## Known gaps / next steps
1. Run `browser_queue.csv`: 72 own reels (30 P1) + 5 competitor reels + 38 discovery searches. Own-audience comment data is 0 until then.
2. YouTube (box IP gets the bot check) and Reddit (403 without OAuth) are blocked from the box. Amazon/Etsy reviews were taken from web-search summaries only.
3. MerryFire has little data (1 on-topic competitor video). Priority: discovery searches + our MerryFire reels.
4. Hook the planner and QA to `voice_rules.csv` (`engine_slot` column). Proposed in DECISIONS.
