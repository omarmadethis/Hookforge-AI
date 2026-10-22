# Hookforge format library (INDEX)

Each format is a full hook-plus-body recipe. Every spec (`<slug>.md` + `<slug>.json`, rendered from one Python source so the two can't diverge) has:
- a timing template with the measured cut lists
- text patterns and caption (always SAY, never COMMENT)
- music picks with offsets
- Higgsfield prompts
- product-fit rules
- an evidence table (views, shares, source)
- failure modes, variant experiments, backtest checks and a creative-director review

## Ranking (by tier, then evidence score)

| # | Format | Tier | Score | Internal hits ≥50K / tested | External organic winners | Evidence rows |
|---|---|---|---|---|---|---|
| 1 | [Then vs Now ("Christmas last year.. → Vs.. → Christmas this year")](then-vs-now.md) | A | 27.1 | 7/13 | 4 | 19 |
| 2 | [3-2-1 countdown prop reveal ("One, two, three. Let's see how it comes out")](321-prop-reveal.md) | A | 27.1 | 11/18 | 0 | 19 |
| 3 | [Fake retailer store reveal (pallet / unveil) + 'JK, we make them' twist](fake-retailer-pallet-jk.md) | A | 24.1 | 7/13 | 2 | 18 |
| 4 | [DO NOT show / let your {recipient} see this](dont-show-recipient.md) | A | 21.2 | 7/13 | 2 | 22 |
| 5 | ["{Recipient}s are hard to gift.." + POV gift handoff](gift-difficulty-pov-handoff.md) | A | 14.1 | 4/7 | 1 | 11 |
| 6 | [Same product, new audience (re-target a proven body to a new tribe or use-case)](same-product-new-audience.md) | B | 15.5 | 4/4 | 0 | 9 |
| 7 | [Unbox-in-hook → use (the package opens inside the first 3 s, never later)](unboxing-to-use.md) | B | 8.9 | 4/4 | 0 | 9 |
| 8 | [POV ritual / envy ("POV: Christmas movie night will never be the same" · "the whole street is JEALOUS")](pov-ritual-envy.md) | B | 8.4 | 2/3 | 2 | 8 |
| 9 | ["Every Christmas {mom} NEEDS this" + store-shelf reaction](statement-needs-store.md) | B | 5.6 | 2/3 | 0 | 8 |
| 10 | [Cut-off word ("The perfect {gift} doesn't exi-")](cutoff-word.md) | B | 5.1 | 2/3 | 1 | 5 |
| 11 | [Friend dare / send-to (group self-purchase accessory)](friend-dare-group.md) | B | 4.6 | 2/4 | 0 | 6 |
| 12 | [Audience / identity callout ("{Tribe}-aholics… this is for you 🥹")](audience-callout.md) | B | 1.3 | 0/1 | 1 | 7 |
| 13 | [Gift outcome ("got my {wife} this & now she won't stop {using it}😂")](gift-outcome.md) | C | 4.0 | 0/0 | 1 | 5 |
| 14 | [Silent reveal (no hook text, plug-in → wow)](silent-reveal.md) | C | 0.9 | 0/0 | 0 | 5 |
| 15 | [Problem → solution ("The problem.. → Vs.. → The solution")](problem-solution.md) | X | 1.0 | 0/4 | 1 | 5 |

## How the score works

- **Internal reels** (Omar's pages, all organic): ≥1M = 4, ≥100K = 3, ≥50K = 2, ≥20K = 1. Flops add 0 but still count toward the hit rate. Rows marked `context` are cited but not scored.
- **External organic reels:** ≥5M = 3, ≥1M = 2, ≥400K = 1, ≥100K = 0.5. Reels flagged as paid or Spark count half and are not counted as winners.
- **Freshness (Omar, 2026-10-18):** our own reels keep full weight regardless of age. The 14-day freshness rule applies only to external reels: an external reel posted more than 14 days before 2026-10-18 is weighted by config.recency_weight (full ≤14 d, exp decay τ=7 d, floor 0.05; undated = floor; '90d_20m' mega-viral rows keep 0.95) and counts as an 'external organic winner' only at weight ≥0.9. Post dates come from external_reels.csv; for TikTok reels missing there, the date is decoded from the video id (id >> 32 = upload time). To re-date, change `AS_OF` in `_common.py` and rebuild.
- **Ranking:** tier first, then score. Tier B formats can score above weak Tier A ones because a tier is a judgment on evidence quality (independent internal winners), not volume.
- **Tiers:**
  - A = at least 3 internal winners ≥50K that were fresh uploads (not reposts of an identical file; age does not matter), plus external support.
  - B = category-specific, or thin internal evidence.
  - C = external-only experiment.
  - X = demoted.
- **Overlap:** formats are hook-plus-body recipes, so one reel can appear in several evidence tables (for example, the 6.6M robe reel). Scores rank evidence; they don't add up across formats.

## Picking a format by product type

- **Wearable gift (robe, hoodie, blanket):** dont-show-recipient, fake-retailer-pallet-jk, gift-difficulty-pov-handoff, statement-needs-store, cutoff-word (store footage). Tests: audience-callout, gift-outcome.
- **Decor, lights, fire:** then-vs-now and 321-prop-reveal by default; also pov-ritual-envy and cutoff-word (box in hook). 'Don't show this to…' is EXPERIMENT ONLY on decor (the MerryFire fire pit went 0 for 3: 3.0K, 3.1K, 33 views). Test: silent-reveal.
- **Group/self-purchase accessory (ski mask):** friend-dare-group.
- **Pet:** audience-callout ('Dog MOMS… this is for you'), silent-reveal test.
- **Toy/gadget:** problem-solution only as a single experiment (Tier X everywhere else).
- **Any proven product, new tribe:** same-product-new-audience. Re-skin the hook only, never the same file (a repost of the 6.6M reel did 2.2K).
- **Every format:** apply the unboxing-to-use guard rail (no box shot after 3.8 s or longer than 2.0 s).

## Generation rules (checked automatically by `_build.py`)

- **Hook:** its own 4 s generation at 720p (D181).
- **Body:** 720p, with 2 shots per 4 s Seedance generation. The prompt must say `HARD CUT at 2s, no transition`.
- **Recreates:** splice two 2 s reference segments into one 4 s `<<<video_1>>>` and add 'including its HARD CUT at 2s, no transition'. The scripted alt_prompt is the fallback:

```
ffmpeg -i a.mp4 -i b.mp4 -filter_complex "[0:v]trim=0:2,setpts=PTS-STARTPTS[a];[1:v]trim=0:2,setpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=1[v]" -map "[v]" ref.mp4
```

- **Start frames:** every start-frame still prompt (T8 still or T9 edit, image model) ALSO ends with the suffix (Omar, 2026-10-18). Every generation that animates 'the start image' carries a `start_frame`: a hand-written T8/T9 still, a still built automatically from that generation's SHOT 1, or a chain from another render's last frame. `_build.py` fails if any start image lacks one, or if any still is missing the suffix.
- **Every prompt (video AND still) ends with:**

> shot on iphone 12, no warm lighting, no blur, nothing cinematic, make it look as organic as possible, remove the caption and the emojis. when recreating do not make the video grainy or sharp in any way, remake it as if it was freshly refilmed 4k iphone 12 footage.

## Innovation budget

No more than 20% of renders go to Tier C formats or variant experiments. The rest go to Tier A and B. Each variant's kill or promote gate is in its spec.

## Caveats

- The 720p body hasn't been A/B tested against 1080p.
- TikTok plays aren't the same as FB views.
- Retro-year grain conflicts with the realism suffix, so add grain in CapCut instead.
- Retailer trademark risk: the JK flip is mandatory on fake-retailer hooks.
- Link captions aren't causal (Omar).

## Sources

/workspace/team/{hooks,body,external,viral_research}/REPORT.md, hook_features.csv, reels_summary.csv, shots.csv, external_reels.csv, analysis.jsonl, /workspace/playbook/PLAYBOOK.md v2.1, prompt_templates.md v2.4, /workspace/hf_match/prompt_analysis.md, /workspace/team/omar_decisions.md.

## Rebuilding

`python3 /workspace/hookforge/formats/_build.py`: re-scores, re-checks every prompt, and rewrites all the .md and .json files plus this index.
