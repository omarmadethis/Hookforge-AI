# Hookforge capability audit: what access and tools would actually improve it
2026-10-18, 8:40 PM PT. This is research only. Nothing was bought, signed up for or authenticated, and no commands ran on the Mac. The only install was one open-source tool on the box (PySceneDetect, see §4).
Filter (Omar): only proven, widely used tools, and each one is tied to the exact Hookforge step it improves. Marginal items are listed under "Cut" with the reason.

## Top 5 asks for Omar
1. **Give the box browser admin access to HeatedJammies Insights, then do one Business Suite CSV export.** The 38 HJ reels (including all four 1M+ winners) have views but no 3-second rate, average watch, retention curve, shares or follows. With these, the backtester can learn from retention (what the edit controls) and not only views (which are mostly luck). §2 describes the pipeline, which is ready.
2. **Create a free Meta developer app and a long-lived Page token for each FB page plus IG.** This takes about 20 minutes and the steps are in item 2. It gives automated daily per-reel metrics with no browser scraping, plus first-day velocity, and later it handles posting for the 5-videos-a-day autonomy phase. It's free and it's Meta's official API.
3. **Approve a read-only CapCut drafts sync, only `draft_info.json` and `draft_meta_info.json`, about 100 KB each.** A one-off snapshot of 110 drafts is already on the box, and all of them parse. They hold the team's exact cut times, text overlays, song and song start, speed ramps and which `hf_` clip went where. The sync keeps new edits coming in, and the same format lets Hookforge hand back an **editable CapCut project** instead of a flat MP4.
4. **Export every finished video into one Google Drive folder synced by Drive for Desktop**, for example the existing "Finished Videos & Captions". The box picks new files up through the Drive connector, so it needs no extra Mac access and no machine approvals.
5. **Confirm the privacy rules for Mac reads, listed in §5.** Allowed: CapCut drafts, product folders and exported videos. Never touched: Downloads finance files, IDs, credentials or browser profiles. One example of what's at stake: the inventory shows a bank statement PDF and a payouts CSV in Downloads, and both stay excluded.

---

## Ranked items (by impact on Hookforge quality)

| # | Item | What it unlocks (Hookforge step) | Evidence it's established | Cost | Effort | What Omar must do | Recommendation |
|---|---|---|---|---|---|---|---|
| 1 | **HeatedJammies Insights via Business Suite** (browser plus CSV export) | Retention labels for the flagship page: 3s views, avg watch, % watched, biggest drop-off second, the retention curve, shares, follows, non-follower %. **Backtester (Phase 2)** targets and **body formula** checks | First-party Meta tool. The same process already produced `merryglow/top5_retention.csv` and the per-page `*_insights_reels.csv` | Free | Omar 5 min; us 1-2 h | Grant page access to the logged-in box FB profile, or export Content → Reels → CSV (lifetime) | **Do now** |
| 2 | **Meta Graph API with a free developer app and Page/IG tokens** | Daily automated per-reel pulls. FB `/{video_id}/video_insights`: `blue_reels_play_count`, `post_video_avg_time_watched`, `post_video_view_time`, `post_video_social_actions`, reactions. IG `/{media_id}/insights`: `views`, `reach`, `ig_reels_avg_watch_time`, `ig_reels_video_view_total_time`, `shares`, `saved`, `reposts`, **`reels_skip_rate`** (a direct hook-strength label), `follows`. Daily snapshots give view velocity, which models the page-burst confound found in the audit. Later it handles publishing (`/{page_id}/video_reels`, IG Content Publishing) for **autonomy (Phase 6)** | Official Meta API (developers.facebook.com/docs/graph-api, Instagram Platform docs), used by every serious social tool (Sprout, Hootsuite, Supermetrics) | Free | Omar ~20 min; us ~half a day | Steps below | **Do now**. Note: the second-by-second **retention curve is not exposed by the API**, so keep the Business Suite browser scrape for curves |
| 3 | **CapCut draft JSONs** (`~/Movies/CapCut/User Data/Projects/com.lveditor.draft/<project>/draft_info.json`) | Ground truth for the **body formula and edit engine (Phase 3-4)**: exact cut times to the microsecond, text content, timing and style, audio file plus in/out offset (exact song section), speed ramps, effects. Joins `hf_` clip → draft → export → posted reel → Insights, so each prompt gets credit for real results. Write-back: Hookforge outputs a draft Omar opens and tweaks in CapCut | Verified on the box: **110/110 drafts parse** (Sep 12 to Oct 18; 203 `hf_` clips, 148 text items, 171 audio items, median 12.9 s, 1080×1920). For write-back, the established library is **pyJianYingDraft** (4.6k GitHub stars, active Oct 2026; same draft family) | Free | us 1 day to harvest, 1-2 days for write-back | Approve a read-only sync of draft JSON files only (no media). Don't update CapCut until write-back is tested: newer builds can encrypt drafts | **Do now**. Harvest the snapshot already on the box immediately |
| 4 | **PySceneDetect** (installed on the box today, v0.7.2) | **Backtest measurement and pre-flight checks**: content-aware and adaptive cut detection to replace the ad-hoc `ffmpeg select=scene>0.25`. That threshold missed the inner cuts behind the Oct 2 Ad Multiplier failure (~368 credits). Also needed to verify the new "2 clips per 4 s generation, hard cut at 2 s" rule on every packed generation | 5.3k GitHub stars, active (pushed Oct 2026), standard in video pipelines | Free | us 2 h | Nothing | **Done.** Wire into `engine/backtest` and the generation QC gate |
| 5 | **Box analysis stack already installed**: faster-whisper (26k★), open_clip (14k★), OpenCV, tesseract, librosa, shazamio, ImageHash, ffmpeg (ssim/psnr) | Speech/lyric timing, first-frame visual similarity to winners (CLIP embeddings), on-screen text timing, song ID and offset, loop/duplicate detection: the **backtester feature set** | All mature and widely used | Free | none | Nothing | **Keep.** Use faster-whisper's `word_timestamps=True`; whisperX isn't needed |
| 6 | **PaddleOCR** (91k★) replacing tesseract for burned-in captions | Text-overlay OCR on stylized TikTok/Reels fonts (outlines, emojis, colored boxes), where tesseract's white-mask approach misses text. Feeds **hook text and caption features** for the research library's 1M+ reels, which have no text metadata | Most-starred OCR project on GitHub; production use across the industry | Free | us 2-3 h | Nothing | **Install after `measure_corpus` finishes.** Box RAM is currently 15/15 GB used, so it wasn't installed today. Keep tesseract as the fallback |
| 7 | **Google Drive for Desktop sync folder** for finished exports (and raw `hf_` downloads) | Every new finished video and Higgsfield download lands on the box without Mac approvals. Feeds the **learning loop (Phase 5)**: the shipped file is always matched to its draft and its Insights | Google's official client; the Drive connector is already working | Free | Omar 5 min | Point CapCut exports at the synced "Finished Videos & Captions" folder | **Do** |

### Item 2 setup steps (Omar, about 20 min, free)
1. Go to developers.facebook.com → My Apps → Create App → type **Business**, and attach it to your Business portfolio.
2. Add the products **Facebook Login for Business** and **Instagram** (Instagram API with Facebook Login).
3. In Graph API Explorer, select the app and request `pages_show_list`, `pages_read_engagement`, `read_insights`, `instagram_basic` and `instagram_manage_insights`. Later, for posting: `pages_manage_posts`, `publish_video` and `instagram_content_publish`.
4. Generate a User token → exchange it for a long-lived token → call `/me/accounts` to get **Page tokens**. These don't expire while you remain an admin.
5. Put the tokens in one file on the box (Hookforge `private/secrets.env`, gitignored, never in chat or repo). Standard (Standard Access) works for pages you admin, so no app review is needed for reading your own pages.

---

## §2: HeatedJammies Insights → backtester pipeline (ready for when access lands)
- **Landing:** `hookforge/private/insights/<PAGE_CODE>/raw/<YYYY-MM-DD>/`, holding the Business Suite CSV export, per-reel detail scrapes (JSON, including the retention curve as a 1-second array) and Graph API JSON.
- **Normalizer:** `engine/backtest/insights_ingest.py` (to build). It maps every source onto one schema in `private/insights/insights_reels.csv`: `page_code, reel_id, snapshot_at, posted_pt, views, reach, three_sec_views, avg_watch_s, avg_pct_watched, completion, dropoff_s, retention_curve, shares, comments, reactions, follows, link_clicks, non_follower_pct, src_reels_pct`. These are the same fields as `merryglow/top5_retention.csv` and `*_insights_reels.csv`, so the MG, MGS, BH and MC data loads through the same path.
- **Join key:** HJ corpus rows already carry `reel_id` (the FB reel URL id, e.g. HJ-01 → 1624473615929591), which is also the Graph `video_id`. `engine/backtest/corpus.py` fills the empty `three_sec_rate, avg_watch_s, avg_watch_pct, completion, dropoff_s, shares, likes` columns. With item 3, rows also get `draft_id → hf_ clips → prompts`.
- **Snapshots:** append-only daily rows, giving view velocity (day 1, day 3, day 7). This lets the model separate the page-burst effect from the creative.
- **Labels:** the backtester gets two targets. `retention_score` combines the 3s rate, % watched and drop-off position, and is controlled by the edit. `reach_outcome` is views, controlled by the edit plus luck and burst. A video ships on retention backtest plus format proof, not on a views prediction.
- **Privacy/repo:** `private/` stays gitignored. The shareable repo gets anonymised keys and rates only (no IDs, sales or page names).

## §3: Current access (summary) and gaps
- **Working:**
  - Connectors: Gmail, Google Drive, Slack, Higgsfield (both accounts), Shopify (MerryGlow, Brick Hood), GitHub, X public reads.
  - Box browser: MerryJammies IG, Merry Glow FB admin Insights, Higgsfield web.
  - Mac (via approvals): Claude Code projects, product folders, Downloads, and the CapCut drafts snapshot already copied to `team/mac/text/...`.
- **Gaps, in impact order:**
  - HJ Insights (ask 1)
  - no API pull or velocity data (ask 2)
  - no ongoing CapCut draft feed (ask 3)
  - no automatic finished-video feed (ask 4)
  - Merry Jammies Shopify is disconnected (its report is already done, so it isn't needed)
- **Plugin marketplace:** no `SearchPlugins` tool is exposed in this session, so marketplace plugins couldn't be enumerated. Higgsfield's `apps_search` returned nothing relevant.

## §4: Box changes made today
- Installed **PySceneDetect 0.7.2** (`pip --user`, nice 19).
- Nothing else was installed. PaddleOCR is deferred because RAM is full while `measure_corpus` runs.

## §5: Mac access and privacy rules (proposed)
- **Allowed (read-only):**
  - `~/Movies/CapCut/User Data/Projects/com.lveditor.draft/*/draft_info.json`, `draft_meta_info.json` (no other CapCut files)
  - product folders (`~/Documents/<product>/`, `~/Jolly Glow/`)
  - video files (`*.mp4/*.mov`) in Downloads
- **Never:**
  - finance (statements, `payouts_export*.csv`, tax), IDs and passports
  - `~/Library` keychains, browser profiles, `.env`/token files, SSH keys
  - Messages, Photos library (unless Omar names specific screen recordings)
- **No writes to the Mac** except files Omar asks for (e.g. a generated CapCut draft into the drafts folder, after a test project works).

## Cut (considered, not recommended)
- **Higgsfield `virality_predictor` and `video_analysis`:** already connected, but opaque, unvalidated against our winners and flops, and they spend credits. Use one only if it beats our own backtester on held-out reels.
- **TikTok API:** the business is FB/IG; Content Posting needs an app audit. Revisit if TikTok becomes a channel.
- **ElevenLabs/voice:** winners use licensed songs and on-screen text, not voiceover.
- **Notion/Airtable/Sheets, Postiz/schedulers:** no quality gain. Meta's API covers posting for free.
- **whisperX, aesthetic predictors, VMAF, chromaprint:** redundant with faster-whisper, CLIP, ffmpeg SSIM and shazamio plus chroma cross-correlation, or marginal for UGC-style iPhone footage.
