# PERFORMANCE_RANK: Omar's own posted reels (FB + IG)

Built 2026-10-19 (PT) from `data/features/inventory.csv` (own_posted, 99 rows → 96 unique reels after merging IG duplicates) plus `audience/ig_reel_audience.csv` (IG Insights screenshots: reach, saves, follows). FB numbers come from the public pages / Business Suite exports already on the box, so FB **saves and follows are mostly missing**. Full table: `performance_all.csv`.

"Paired" = a raw→final pairing exists in `pairs.csv`.

## Top 10 by views
| # | Platform / page | Product | Posted | Views | Reach | Likes | Shares | Saves | Follows | Shares/1k | Paired | Link |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | FB HeatedJammies | heated Grinch robe | 2026-09-05 | 6,600,000 |  | 58,200 | 2,400 |  |  | 0.4 | yes | https://www.facebook.com/reel/1624473615929591/ |
| 2 | IG merry.jammies IG | Grinch robe (MJ IG, product not tagged) | 2026-09-21 | 4,626,729 | 2,934,339 | 396,249 | 15,142 | 8,563 | 2,518 | 3.3 | yes | https://www.instagram.com/reel/Ddii6mOKO2G/ |
| 3 | FB HeatedJammies | heated Grinch robe | 2026-09-08 | 2,700,000 |  | 30,400 | 1,300 |  |  | 0.5 | yes | https://www.facebook.com/reel/1381141263599559/ |
| 4 | FB HeatedJammies | heated Grinch robe | 2026-09-12 | 1,400,000 |  | 9,900 | 979 |  |  | 0.7 | yes | https://www.facebook.com/reel/1621118726207387/ |
| 5 | FB HeatedJammies | heated Grinch robe | 2026-09-05 | 1,400,000 |  | 13,500 | 1,600 |  |  | 1.1 | yes | https://www.facebook.com/reel/2121138075159387/ |
| 6 | IG merry.jammies IG | Grinch robe (MJ IG, product not tagged) | 2026-09-14 | 686,895 | 436,892 | 117,230 | 1,664 | 1,309 | 263 | 2.4 | yes | https://www.instagram.com/reel/DdQw1jyKI63/ |
| 7 | FB HeatedJammies | heated Grinch robe | 2026-09-27 | 524,000 |  | 4,000 | 971 |  |  | 1.9 | yes | https://www.facebook.com/reel/38670473745933796/ |
| 8 | IG merry.jammies IG | Grinch robe (MJ IG, product not tagged) | 2026-09-22 | 362,211 | 287,438 | 5,510 | 5,869 | 992 | 594 | 16.2 | yes | https://www.instagram.com/reel/DdTC2suKD0l/ |
| 9 | IG merry.jammies IG | Grinch robe (MJ IG, product not tagged) | 2026-09-15 | 334,167 | 214,722 | 20,840 | 16,081 | 3,388 | 2,676 | 48.1 | no | https://www.instagram.com/reel/DdK34IiqRx4/ |
| 10 | FB HeatedJammies | heated Grinch robe | 2026-09-24 | 326,000 |  | 1,100 | 184 |  |  | 0.6 | no | https://www.facebook.com/reel/1823842129037913/ |

**Share-rate leaders** (shares per 1k views, ≥100K views): IG DdK34IiqRx4 (334K, **48/1k shares, 8 follows/1k**, probable Jordan Stallion Grinch-robe reel) and IG DdTC2suKD0l (362K, 16/1k, "Last Christmas" audio). These spread far better per view than the 4.6M reel (3.3/1k), so they're the ones to copy for shares and follows.

## Bottom 5 by views
| # | Platform / page | Product | Posted | Views | Reach | Likes | Shares | Saves | Follows | Shares/1k | Paired | Link |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 92 | FB HeatedJammies | heated Grinch robe | 2026-09-28 | 1,100 |  |  |  |  |  |  | no | https://www.facebook.com/reel/1073780918870688/ |
| 93 | IG merry.jammies IG | Smiley ski mask | 2026-10-02 | 1,071 |  |  |  |  |  |  | no | nan |
| 94 | IG merry.jammies IG | Grinch robe (MJ IG, product not tagged) | 2026-09-05 | 958 | 751 | 9 | 0 | 0 | 0 | 0.0 | no | https://www.instagram.com/reel/Dc5M3cYqnEe/ |
| 95 | FB Merry Glows | fire pit | 2026-10-08 | 457 |  |  |  |  | 0 |  | yes | https://www.facebook.com/reel/28876831118647366/ |
| 96 | FB MerryFires | tabletop fire pit | 2026-10-12 | 33 |  | 1 |  |  | 0 |  | yes | https://www.facebook.com/reel/1074037222295921/ |

Also weak among the paired reels: Merry Glows 1,211 (draft 0924, a stripped variant), Merry Glows 2,191 (0925, "POV: You just won the tree contest", 2 shots), MerryFires 2,705 (1010 (2), Dean Martin from 0.9 s).

## Coverage of the ranked reels
- Top 10: **8 of 10 paired.** Two have a CapCut draft (#2 4.6M → draft `0920 (1)`; #6 687K → `0913 (1)`). Six are reconstructed frame by frame from raw generations because their drafts no longer exist (#1, #3, #4, #5, #7 weak, #8). #9 (334K) and #10 (326K) have no confident pairing: the raws are similar Grinch-robe scenes and the matcher is ambiguous on them.
- Bottom 5: 2 of 5 paired (457 → `1008 (3)`; 33 → `1007 (2)`). The 1.1K FB, 1.07K IG ski-mask and 958 IG reels have no surviving draft or raws.


## FB HeatedJammies page insights (D63, 2026-10-19 PT)
Source: Omar's FB Reels insights CSV (`audience/fb_heatedjammies_insights.csv`, 38 reels + 1 profile-pic post dropped). Joined by reel id to reels DB (38/38), performance_all (38/38), style/shots (11), raw_vs_final pairs (5, all reconstructed, no draft). Full: `analytics/fb_hj/ranked.csv`.

| # | Views | Shares/1K | Link clicks/1K | Avg watched / % | Dur | Posted (PT) | Caption | Song |
|---|---|---|---|---|---|---|---|---|
| 1 | 6,668,888 | 0.38 | 0.55 | 9.7s / 70% | 14s | 2026-09-05 23:55 | Get yours👉 | Dean Martin · Let It Snow - Let It Snow - Let It Snow |
| 2 | 2,729,169 | 0.49 | 1.36 | 10.6s / 76% | 14s | 2026-09-08 01:08 | Get yours👉🏻 | HeatedJammies · Original audio |
| 3 | 1,460,419 | 1.14 | 1.26 | 7.2s / 56% | 13s | 2026-09-05 17:00 | Get yours👉 | Mariah Carey · All I Want for Christmas Is You |
| 4 | 1,412,048 | 0.71 | 1.38 | 6.1s / 47% | 13s | 2026-09-12 23:00 | Get yours 👉 | Mariah Carey · All I Want for Christmas Is You |
| 5 | 524,946 | 1.86 | 0.00 | 12.6s / 97% | 13s | 2026-09-27 10:30 | All moms need this🎁 | Wham! · Last Christmas (Remastered) |
| 6 | 326,777 | 0.57 | 1.97 | 6.3s / 53% | 12s | 2026-09-24 08:15 | Get yours👉🏻 | Mariah Carey · All I Want for Christmas Is You |
| 7 | 304,756 | 1.05 | 0.00 | 12.6s / 70% | 18s | 2026-09-20 00:35 | And its heated😊 | Michael Bublé · It's Beginning to Look a Lot like Christmas |
| 8 | 183,145 | 1.41 | 0.87 | 9.7s / 69% | 14s | 2026-09-19 04:15 | Shop here👉🏻 | Wham! · Last Christmas (Pudding Mix) |
| 9 | 165,962 | 0.87 | 2.11 | 6.7s / 39% | 17s | 2026-09-16 23:59 | Shop Now👉🏻 | Mariah Carey · All I Want for Christmas Is You |
| 10 | 147,215 | 0.72 | 0.76 | 7.9s / 53% | 15s | 2026-09-11 22:53 | Get yours👉 | Wham! · Last Christmas (Pudding Mix) |
| 11 | 112,666 | 0.73 | 0.00 | 8.2s / 63% | 13s | 2026-09-07 01:43 | Dont show a MOM | HeatedJammies · Original audio |
| 12 | 101,597 | 0.32 | 0.00 | 10.6s / 59% | 18s | 2026-09-09 16:49 | The best Christmas gift🎅🏻🎄 | HeatedJammies · Original audio |
| 13 | 98,652 | 0.64 | 0.00 | 7.2s / 60% | 12s | 2026-09-14 04:59 | It's heated❄️☺️ | Viibez · Jingle Bells |
| 14 | 97,023 | 0.25 | 0.00 | 9.4s / 67% | 14s | 2026-09-11 16:59 | Who needs one😉🎄 | Dean Martin · Let It Snow - Let It Snow - Let It Snow |
| 15 | 91,943 | 0.85 | 0.00 | 8.4s / 60% | 14s | 2026-09-10 02:00 | HEATED JAMMIES☃️🎄 | Dean Martin · Let It Snow! Let It Snow! Let It Snow! |
| 16 | 90,761 | 0.41 | 0.00 | 7.1s / 55% | 13s | 2026-09-08 17:24 | For all the moms🎄💝 | Mariah Carey · All I Want for Christmas Is You |
| 17 | 88,062 | 0.30 | 0.00 | 7.0s / 50% | 14s | 2026-09-21 00:14 | who would wear this🎄 | Dean Martin · Let It Snow! Let It Snow! Let It Snow! |
| 18 | 87,644 | 0.95 | 0.00 | 6.0s / 43% | 14s | 2026-09-21 00:20 | AND they're heated ☃️🎅🏻 | Viibez · Jingle Bells |
| 19 | 71,027 | 0.84 | 0.00 | 5.3s / 41% | 13s | 2026-09-18 18:49 | Run to Target🎄 | Wham! · Last Christmas (Pudding Mix) |
| 20 | 47,458 | 0.78 | 0.00 | 7.1s / 48% | 15s | 2026-09-06 13:01 | The coziest robe!🎄 | Michael Bublé · It's Beginning to Look a Lot like Christmas (Sped Up) |
| 21 | 16,857 | 0.12 | 0.00 | 5.8s / 42% | 14s | 2026-09-16 11:03 | Heated Jammies😁🎄 | nan |
| 22 | 16,660 | 0.96 | 0.00 | 6.2s / 48% | 13s | 2026-09-14 12:37 | Im in love🎄 | nan |
| 23 | 6,790 | 0.29 | 0.00 | 5.8s / 45% | 13s | 2026-09-10 11:36 | The best gift for X-Mas🎄🎅🏻 | nan |
| 24 | 6,292 | 0.64 | 0.00 | 6.7s / 51% | 13s | 2026-09-08 21:44 | Heated Grinch Robe🎄😭 | nan |
| 25 | 6,262 | 0.48 | 0.00 | 8.8s / 68% | 13s | 2026-09-04 17:15 | Heated Jammies☃️🎄 | nan |
| 26 | 5,960 | 0.50 | 0.00 | 9.0s / 65% | 14s | 2026-09-04 20:49 | Christmas is around the corner☃️💝 | nan |
| 27 | 5,659 | 0.18 | 0.00 | 6.7s / 48% | 14s | 2026-09-15 01:52 | Different level💡☃️ | nan |
| 28 | 4,810 | 0.83 | 0.00 | 10.3s / 57% | 18s | 2026-09-22 22:49 | The cure to the cold❄️ | nan |
| 29 | 4,672 | 0.43 | 0.00 | 6.6s / 47% | 14s | 2026-09-10 23:11 | Who would get this🎄👇 | nan |
| 30 | 4,278 | 0.70 | 0.00 | 6.8s / 43% | 16s | 2026-09-14 17:21 | New and Improved🎄 | nan |
| 31 | 4,263 | 0.23 | 0.00 | 6.1s / 41% | 15s | 2026-09-26 10:15 | Who would wear this🤩 | nan |
| 32 | 3,996 | 1.75 | 0.00 | 10.3s / 65% | 16s | 2026-09-04 14:08 | For my Christmas lovers☃️🎄 | nan |
| 33 | 3,950 | 1.01 | 0.00 | 7.2s / 45% | 16s | 2026-09-27 12:25 | Christmas Special🎁 | nan |
| 34 | 3,786 | 2.11 | 0.00 | 8.3s / 49% | 17s | 2026-09-13 16:01 | Comfort for Christmas🎄 | nan |
| 35 | 2,748 | 0.36 | 0.00 | 7.9s / 53% | 15s | 2026-09-26 16:53 | Winter ready❄️ | nan |
| 36 | 2,272 | 0.88 | 0.00 | 7.5s / 54% | 14s | 2026-09-21 17:23 | Comfort for Christmas | nan |
| 37 | 1,615 | 1.86 | 0.00 | 8.3s / 64% | 13s | 2026-09-25 17:03 | SO COMFORTABLE😍 | nan |
| 38 | 1,136 | 0.00 | 0.88 | 12.1s / 93% | 13s | 2026-09-28 14:50 | The best when cold❄️ | nan |
