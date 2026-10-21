# Results feed: what Omar provides (pick A now, B when ready)

Never paste a token or password in chat. Never put one in a file.

## A. Business Suite exports (no setup, works today)
1. Open business.facebook.com, pick the page, then go to **Insights → Content**.
2. Set the date range to the last 28 days and the filter to **Reels**. Click **Export data** and choose **CSV**, keeping all columns.
3. Switch the account picker to the linked **Instagram** account and repeat (Content → Reels → Export → CSV).
4. Drop the CSVs into the Drive folder "Hookforge / Insights inbox", or onto the Mac. The agent copies them to
   `learning/results/inbox/`, and `python3 learning/results_feed.py` ingests them.
5. For velocity, export again on day 1, day 3 and day 7 after a post. Every export becomes a dated snapshot.
   Once the API path (B) is live, this step runs by itself.

## B. Meta Graph API (automatic daily snapshots)
1. Go to developers.facebook.com, then **My Apps → Create app → Other → Business**. Name it "Hookforge Insights" and
   attach it to your Business portfolio.
2. Add the products **Facebook Login for Business** and **Instagram Graph API**. Stay in **Development** mode,
   which is fine for your own pages and needs no App Review.
3. Open the Graph API Explorer, select the app, then **Get User Access Token** with these permissions only:
   `pages_show_list, pages_read_engagement, read_insights, instagram_basic, instagram_manage_insights, business_management`.
   Do NOT grant any publish or manage permissions. The feed is read-only.
4. Exchange it for a long-lived token (about 60 days) in the Access Token Debugger by clicking "Extend Access Token". Or, better,
   create a **System User** in Business Settings, assign it the pages with "View insights", and generate a
   non-expiring token with the same read scopes.
5. Paste the token **only into the secure form the agent sends you**. It is stored as the env var `META_TOKEN` on the box,
   never in a file or in chat. Revoke it at any time in Business Settings → System users, or in Facebook settings → Business integrations.

Fields pulled: FB `blue_reels_play_count`, `fb_reels_total_plays`, `post_video_avg_time_watched`, `post_impressions_unique`,
`post_video_view_time`; IG `views`, `reach`, `reels_skip_rate`, `ig_reels_avg_watch_time`, `shares`, `saved`, `comments`, `likes`.

## C. Sales per reel
Nothing to set up. Captions get UTM links automatically (`utm_source=fb|ig`, `utm_campaign=<product>`,
`utm_content=<video id>`) once the product URL is known. Still needed: the PatriotsGlow product URL.
