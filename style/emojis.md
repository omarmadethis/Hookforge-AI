# Emojis: what we use, what others use, what's proven (2026-10-18 PT)
Files: `emojis.csv` (one row per emoji × side × where, with n, median views, hit rate, rest hit rate, formats, categories, examples), `emoji_usage_rows.csv` (every text unit and its emojis), `emoji_count_vs_hit.csv`, `emoji_rules.json` (machine rules for the engine). Script: `emoji_analysis.py`.

**Hit definitions.** Ours = ≥50K views. External = ≥1M. Ours are judged on the CapCut draft text, which is ground truth (33 joined reels with views). External = 205 reels (72 external corpus, 7 viral research, 126 reference-library rows across index, archive and near-miss tiers). External weighting is unweighted here; the backtester applies `recency_weight`.

## Data-quality finding (fix this first)
The corpus `hook_text` emojis for our reels are vision transcriptions. They match the CapCut draft on **only 6 of 35 joined reels**. For example, 😬 and 🤕 were read as 😩, and 🤭 was read as 😏. Any model feature built on corpus emojis for our reels is noise. Use `style/text_styles.csv` emojis wherever a draft is joined. Also, 2 joins (HJ-13, HJ-15) have different posted text from the joined draft (frames show "Don't show this to your mom..", "The perfect X-MAS gift doesnt exi-🎄"), so those drafts are variants of the posted reel.

## What we actually use (148 CapCut cards + 24 CaptionBank lines)
🎄 24 · ❄️ 24 · 🤩 21 · 😳 20 · 🤮 11 · 😂 10 · 🥹 10 · 🤕 8 · ⏳ 8 · 🤣 8 · 😬 6 · 😻 6 · ✨ 6 · 🎅🏻 5 · 🫪 5 · ⏰ 5 · 🤭 5 · 🎿 4 · ⛷️ 4.
- 92% of cards end with an emoji run, placed after a space at the end of the last line. 55% have 1 emoji, 32% have 2, 5% have 3, 7% have none.
- Grammar: **one face emoji (the emotion) + optional one world emoji (❄️ 🎄 🏠 ⛷️ 🎿)**.

## Proven emojis by use (ours CapCut-truth; external ≥1M)
| use | emoji | evidence |
|---|---|---|
| Then/problem card (F04, F18) | 😬 🤕 🤮 👴🤦‍♂️ | 😬 152.9K, 84.4K · 🤕 67.7K, 40.3K(IG) · 🤮 64.5K, 30.9K(IG) · 👴🤦‍♂️ 70.4K · external hook 🤮 6/9 ≥1M (median 1.4M) |
| Bridge "Vs..." | ⏳ (⏱️) | on all 5 F04 winners' bridge cards |
| Payoff card | 🤩🎄 · 😻 · 😻✨ · ✨😻❄️ | the 6 F04 winners' payoff cards |
| POV / identity hooks, decor | 🤭🏠 · 😳❄️ · 🥹❄️ · 🤩 | 63.3K · 62.8K · 63.0K · 62.0K |
| Ski accessory hooks | 😂 · 🤣 · 🤣⛷️ | 61.1K · 43.2K · 61.3K on FB. The same emojis on IG copies got 1–4K, so the platform decides that, not the emoji |
| Wearable don't-show | 😳 ❄️ | ours ❄️-in-hook 12/18 (corpus read, medium); external ❄️ hook 4/4, 😳 4/7 |
| Gift hooks (external only → experiment) | 😭 ❤️ 💕 | 4/4 (median 2.8M) · 4/5 (2.6M) · 4/6 (4.3M) |
| Caption CTA | ✨ ❤️ 🎄 | external CTA ✨ 6/7, ❤️ 4/5, 🎄 14/20 (decor_light). Ours 👉 14/16 and 👉🏻 4/4, but those are link captions added after take-off (D6), so they're not a lever |

## Avoid list
| emoji / pattern | evidence |
|---|---|
| 👇 in CTA | ours 0/4 (median 2,960); external 1/5 (median 576K) |
| 🎄 as the hook's emoji | ours CapCut-truth 0/4 (4.2K, 3.1K, 457, 5.3K); external 15/27 = 56% vs 62% without. Keep 🎄 for payoff cards and captions |
| 🎁 in hook | external 3/8 (median 757K) vs base 61% |
| 👀 in hook | external 2/5 (median 819K) |
| 🫪 | ours 0/2 |
| 🥹 on decor don't-show | ours 0/2 (3.1K, 457). 🥹 works on POV and nostalgia (63K) |
| 3+ emojis on a card | external 1/7 vs 63–68% at 0–2; ours 5.3K (n=1) |

**Emoji count.** External hit rate: 0 emojis 63% (n=113), 1 emoji 68% (n=40), 2 emojis 58% (n=45), 3+ 14% (n=7). Ours (corpus read, unreliable): 0 = 71% (n=17, mostly early HJ reels with older posts), 1 = 37%, 2 = 45%. So emoji presence isn't a lever. What matters is emotion fit (cringe → payoff) and a cap of 2.

**Caveats.** Per-emoji n is 2–27. The "use" lists are exploit defaults; any other emoji goes in experiment slots and gets logged. External hook emojis come from OCR (medium reliability).
