# Audience-geography levers: how FB/IG Reels pick early test audiences, and what we can steer
Last updated 2026-10-18 ~9:45 PM PT · owner: audience workstream · status of every lever is one of
**documented-by-Meta** (Meta system card / Help Center says so), **widely-reported** (multiple reputable marketing sources, not confirmed by Meta), **anecdotal** (creator folklore), **own-data** (our Shopify/Insights).

## 0. What Meta actually documents (read this before believing any tip)
1. **Candidate pool = similarity + social graph.** "reels from people or accounts you follow, or reels that are similar to those you've recently interacted with … reels from people or accounts that are similar to those you've followed or interacted with" [S1 FB Reels card; S2 IG Reels Chaining card]. No published FB/IG Reels card lists *viewer country* or *language* as a candidate-retrieval rule.
2. **Country IS an engagement feature on IG.** IG Reels Chaining "How likely you are to comment on a reel" uses "*How much time has viewers from your country spent on this reel*" [S2]. => Watch-time from viewers in a country raises the reel's predicted engagement for *other viewers in that country*. Early US watch-time compounds into more US distribution; early non-target watch-time compounds into more non-target distribution. **This is the core mechanism the whole layer is built on.**
3. **Content signals** used for prediction: reel length, similarity to other reels, topic match, "the audio track or visuals in the video" [S1, S2, S3 Mosseri "Instagram Ranking Explained" 2023]. Audio is explicitly a signal (audio-page clicks, "Use audio" predictions) [S2].
4. **Author signals**: "the author of the reel", author popularity/engagement [S1, S3]. Who the author's followers are therefore shapes the first audience.
5. **Search** (not Reels) uses country explicitly ("people performing the same search in your country") [S4 IG Search card].
6. **FB Feed Recommendations** uses "the current time" / "time stamp of the session" [S9] → posting time matters for who is online.
7. **Hard geo control exists on Facebook only:** Page → Settings & privacy → Followers and public content → **Country restrictions** ("Show only in certain countries" / "Hide from certain countries"); applies to all Page content incl. Reels; overrides per-post targeting [S10 Ayrshare docs quoting the setting; Meta help text "When you add age or country restrictions, you may not be able to see your Page when logged out" via S11]. Instagram has no equivalent.
8. **Collabs (IG)**: a Collab post appears on both profiles and is shown to both accounts' followers [S12 Instagram Help Center "Collabs"]. A US creator as collaborator seeds the reel into a US follower base on day 0.
9. **Trial Reels (IG, Dec 2024)**: reels shown first to non-followers only, with results before deciding to share to followers [S13 Instagram announcement]. Sanctioned A/B tool for our experiments.
10. **Meta AI translations** dub/translate reels into other languages for viewers (creator can switch it off per reel) [S14 TechCrunch 2025-08-19]. Our reels are music + on-screen text, so the effect is mostly text translation; keep it OFF on tier-1 tests so we don't invite other-language audiences.

## 1. Ranked levers (strength of evidence that it moves *audience country*, not just views)
| # | Lever | Evidence class | Why / mechanism | Our evidence | Hookforge action |
|---|---|---|---|---|---|
| L1 | **FB Page country restriction** (show only in tier-1 list) | documented-by-Meta (hard filter) | Non-listed countries cannot see the Page's content at all | none yet | EXP-AUD-01 on ONE test page (Omar must flip the setting; it may cut total reach) |
| L2 | **Seed audience = followers of the author / collaborator** (US creator Collab, US-heavy follower base) | documented (candidate pool + Collabs) + own-data (supported) | Day-0 viewers come from the follower graph; their country then feeds the per-country engagement signal (§0.2) | Omar: the ~300K Grinch robe reel with US creator Jordan Stallion had an excellent US audience; almost all other IG reels poor | EXP-AUD-02 (US creator Collab vs solo), EXP-AUD-04 (AI US-style presenter vs faceless) |
| L3 | **Early watch-time by country compounds** (per-country engagement feature) | documented-by-Meta (IG) | §0.2 | — | Everything below exists to win the first ~1–3 h of US watch-time |
| L4 | **Posting time aligned to US evening** (2–8 PM PT = 5–11 PM ET) | widely-reported; FB uses current time | Who is online in the first hour = the seed pool for non-follower tests | own D36: night 18:00–04:00 PT = more *views* (x3.2, supported-hypothesis). **Conflict:** 21:00–04:00 PT = 05:00–13:00 CET, Europe's morning → likely EU-heavy seed | EXP-AUD-03 (US-evening vs late-night PT); measure %US not just views |
| L5 | **Audio with US chart popularity** | documented (audio is a signal) + widely-reported (trending audio lists are regional; IG's Trending-audio dashboard is documented for US pro accounts) | Audio similarity clusters reels with others using it; region-popular tracks cluster with that region's viewers | music_library.csv proof is views only | audio_regions.md; EXP-AUD-06 |
| L6 | **Language & dialect of on-screen text and caption** (US spelling, US-only terms; no Spanish/Portuguese words) | widely-reported (language match is a basic relevance feature; Meta translates text for other-language viewers) | English-only already filters toward English speakers; US-only terms (Target, HOA, Thanksgiving, °F) add US-specific topic similarity | lexicon.csv: phrasing grounded in viral reels (reach), geo effect = hypothesis | lexicon.csv; EXP-AUD-05 |
| L7 | **Visual cultural cues** (US flags, US suburban homes, US-style big-box stores, US outlets/plates/units, Thanksgiving décor) | anecdotal→widely-reported (visual similarity is documented; "US cues attract US viewers" is not) | Visual embeddings cluster with reels US viewers already watch | Omar rule D24 (flags) has no measured geo effect yet | visual_cues.md; EXP-AUD-07 |
| L8 | **Hashtags/caption language** | widely-reported (weak; Mosseri says hashtags matter little) | Caption text = topic/language signal | — | English caption, US spelling, ≤3 tags, no geo tags of non-target regions |
| L9 | **Page/account location & admin location** | anecdotal (IG "About this account" shows account country; no ranking doc) | Possibly a locale prior | — | Keep pages admin'd/created from the US where possible; do not use VPN tricks (policy risk) |
| L10 | **Engagement seeding** (first comments/shares from US accounts, e.g. sharing to US-heavy Stories/groups) | anecdotal; FB demotes engagement bait (D5) | Feeds §0.2 | — | Only organic: share to own US-heavy IG Story / Collab; never buy engagement |

## 2. Why tier-1 targeting matters (own Shopify, read-only aggregates, 2026-08-01..10-18 PT)
Pooled Merry Glow + Brick Hood stores (Merry Jammies store not reachable through the connector without switching store auth; not done):
| tier | session→order CR | 95% CI | share of orders (billing country, 55 orders) |
|---|---|---|---|
| T1-PRIMARY (US) | 0.51 % | 0.36–0.72 % | 64 % |
| T1-EN (UK, CA, AU, NZ, IE) | 0.36 % | 0.18–0.70 % | 16 % |
| T1-WEST (CH, NL, DE, NO) | 0.46 % | 0.20–1.08 % | 11 % |
| T2 (DK, BE, AT, SE, FI, FR, PT, GR, ES, JP, PL) | 0.24 % | 0.10–0.63 % | 7 % |
| NON-TARGET (IT, RO, HU, MX, BR, CO, PH, IN, …) | 0.05 % | 0.01–0.30 % | 2 % |
US converts **~10×** better per session than non-target regions (non-overlapping CIs) and is 46 % of sessions but 64 % of orders. Non-target sessions reach checkout (e.g. 2.9 % of MX sessions) but almost never complete (likely shipping cost, price or payment friction: not measured). **This is the proven business case (own-data, n≈14.2K sessions).**

## Sources
- [S1] Meta Transparency Center, "Facebook Reels AI system" (updated Jun 19 2026) https://transparency.meta.com/features/explaining-ranking/fb-reels/
- [S2] Meta Transparency Center, "Instagram Reels Chaining AI system" (updated Nov 11 2025) https://transparency.meta.com/features/explaining-ranking/ig-reels-chaining/
- [S3] Adam Mosseri, "Instagram Ranking Explained" (2023), summarized by Social Media Today https://www.socialmediatoday.com/news/instagram-explainer-feed-reels-and-stories-algorithm/651705/ and The Verge https://www.theverge.com/2023/5/31/23744125/
- [S4] Meta Transparency Center, "Instagram Search" https://transparency.meta.com/features/explaining-ranking/ig-search/
- [S5] Statista (Salesforce Shopping Index), online shopper conversion rate by country Q2'25–Q2'26 https://www.statista.com/statistics/439576/online-shopper-conversion-rate-worldwide/
- [S6] ECDB, E-Commerce KPI and Benchmarks Report 2026 (2025 market table: CR, AOV, frequency) https://static.ecdb.com/media/2026/07/ecdb-e-commerce-kpi-and-benchmarks-report-2026-14366.pdf
- [S7] Adtraction, E-commerce Insights Q2 2025 (AOV index by European market)
- [S8] IMF World Economic Outlook, GDP per capita PPP 2024 (via Worldometer) https://www.worldometers.info/gdp/gdp-per-capita/ ; World Bank NY.GDP.PCAP.PP.CD
- [S9] Meta Transparency Center, "Facebook Feed Recommendations" (updated Jun 24 2026) https://transparency.meta.com/features/explaining-ranking/fb-feed-recommendations/
- [S10] Ayrshare docs, "Facebook Page Country Restrictions Explained" https://www.ayrshare.com/docs/help-center/technical-support/facebook_page_country_restrictions
- [S11] DigitalShift Media, "Facebook Page Visibility Troubleshooting" (quotes Meta help) https://docs.digitalshiftmedia.com/en/facebook-page-visibility-troubleshooting
- [S12] Instagram Help Center, "Collabs: invite a collaborator to a post" (help.instagram.com)
- [S13] Instagram, "Trial reels" announcement (Dec 2024, about.instagram.com / @creators)
- [S14] TechCrunch, "Meta rolls out AI-powered translations to creators globally" (2025-08-19) https://techcrunch.com/2025/08/19/meta-rolls-out-ai-powered-translations-to-creators-globally-starting-with-english-and-spanish/
- [S15] Billboard Holiday 100, week of 2025-12-27 https://www.billboard.com/charts/hot-holiday-songs/2025-12-27/
- [S16] Official Charts (UK) Streaming Chart 2025-12-26 and "Top 40 most-streamed Christmas songs" https://www.officialcharts.com/charts/streaming-chart/20251226/7510/
- [S17] Instagram Graph API user insights: `reached_audience_demographics` / `engaged_audience_demographics` with `breakdown=country`, `timeframe=this_week|this_month` (account-level only; media insights have no country breakdown) – Meta developer docs, summarized by Sprinklr https://www.sprinklr.com/help/articles/reporting-glossary/instagram-user-insights-api-changes/668546d1679a1c4c5c780ae5
Local copies of fetched pages: none kept (pages are JS-rendered); quotes above are verbatim from WebFetch on 2026-10-18.
