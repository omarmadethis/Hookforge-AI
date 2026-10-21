# Meta Business Suite CSV → learning/results/inbox (D102)

Read-only feed for results_feed + the hourly snapshot loop (10K-views-in-one-hour caption swap, 40K total).

## Which export
**Facebook reels, per page** (one file per page):
Meta Business Suite → Insights → **Content** → pick the page → set the date range to **Last 28 days** (or "Lifetime")
→ filter to **Reels** → **Export data** → **Post-level / Content** → format **CSV** → Download.
**Instagram (merry.jammies)**: same screen, switch to the Instagram account, export Content as CSV.

Drop the downloaded file(s) **as-is** into `/workspace/hookforge/learning/results/inbox/` (any filename ending in .csv;
naming it `<Page>_insights_reels.csv` helps if the export has no "Page name" column).

## Columns the parser reads (exact Meta headers, matched case/space-insensitively)
| Meta header (FB) | Meta header (IG) | → field |
|---|---|---|
| Post ID | Post ID | post_id |
| Page name | Account username / Account name | page |
| Title | — | hook_text |
| Description | Description | caption |
| Duration (sec) | Duration (sec) | duration_s |
| Publish time | Publish time | posted_pt (Pacific) |
| Permalink | Permalink | reel_url |
| Views | Views | views (**required**) |
| Reach | Reach | viewers |
| Reactions | Likes | reactions |
| Comments | Comments | comments |
| Shares | Shares | shares |
| — | Saves | saves |
| — | Follows | follows |
| Total clicks / Link clicks | — | clicks / link_clicks |
| Seconds viewed | — | watch_time_s |
| Average Seconds viewed | — | avg_watch_s |
| 3-second video views | — | three_sec_views |
| 1-minute video views | — | one_min_views |

Ignored on purpose: Page ID / Account ID (scrubbed, never stored), earnings, ad columns. Unknown columns are ignored;
missing ones stay empty (never invented).

## Timing (why it matters for the 10K/hour trigger)
Each file is a lifetime snapshot **at the moment it was exported**; the loop stamps it with the file's modified time,
so drop it right after downloading. One export per hour per page gives the hour-by-hour curve. The loop (on the hour PT)
moves processed files to `inbox/processed/`, writes `learning/results/snapshots/<stamp>.csv`, refreshes velocity, and
turns any reel that gained >= 10,000 views between two snapshots <= 1 h apart (or >= 40,000 total) into a caption-swap
**approval item** (nothing is edited). With a Graph token (META_TOKEN env, never in a file) the loop pulls the same
numbers itself every hour and no CSVs are needed.
