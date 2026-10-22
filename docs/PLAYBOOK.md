# The Hookforge playbook: how organic product reels go viral

Distilled from the full evidence playbook (hundreds of measured reels across 6+ product pages and the competitors
they copied), the consumer-psychology map, `learning/` and the POC hook formats in `formats/`.
**Precedence:** `docs/RULES.md` (enforced by the gate) wins over this playbook wherever they differ; the rules are
newer and came from real failures. Older evidence (e.g. link captions, 1440p export) is marked superseded below.

## 1. The five things that decide views

1. **The hook decides views; the template is a constant.** Winners and flops on the same page shared length
   (12-14 s), 6-7 shots, ~2 s per shot and one held text line. Only the hook family and hook footage separated a
   6.6M reel from a 1.1K one.
2. **The first 2 seconds are the whole game.** 98-99.9% of views come from non-followers via the Reels feed; the
   biggest drop-off is at 0:02; only ~35-48% reach 3 s. So: product on screen at 0 s and a **real conflict or action
   in the first second** (MR23).
3. **Distribution is a lottery, so buy many tickets with NEW videos.** The identical file did 6.6M and later 2.2K;
   1.4M -> 16K; 326K -> 1.6K. Same body + new hook text went 4.2K -> 183K. Reposts now get pages shadowbanned:
   every video is fully unique, one page only, never reposted (MR18, MR19).
4. **Copy proven winners 1:1 ("POC'd to the max").** Recreate the original's hook beat, card wording pattern,
   pacing, shot order and **exact song section** (MR22, MR26). Untested ideas are experiments, not posts.
5. **Look idealized, not polished.** AI artefacts (warped logos, odd box text) did not stop 1M+ reels. What kills
   them is anything that reads as cinematic AI slop: warm light, blur, grain, slow-mo. Every prompt ends with the
   iPhone 12 realism suffix (MR10).

## 2. Proven hook formats (POC library)

Ranked by evidence in `formats/INDEX.md`; each has a full recipe (timing, card patterns, music, prompts, failure modes).

| Tier | Format | Pattern | Best for |
|---|---|---|---|
| A | Then vs Now | `Christmas 2024.. -> Vs.. -> Christmas 2026` (2 cards allowed) | decor, lights, gadgets with a clear before/after |
| A | 3-2-1 prop reveal | covered product cue at 0 s, everyone counts, "let's see how it comes out", split-second reveal | anything with a satisfying reveal |
| A | Fake retailer pallet + "JK, we make them" | huge branded pallet in a big-box aisle | gift wearables |
| A | DO NOT show this to your {recipient} | names who it's FOR (mom, wife, horse girl...) | gifts, hobby niches. Flopped on decor. |
| A | "{Recipient}s are hard to gift.." + POV handoff | gift box handed over, POV | cozy gifts |
| B | Same product, new audience | re-skin a proven body for a new tribe (new footage!) | scaling a winner |
| B | POV ritual / envy | "POV: movie night will never be the same" | home experience products |
| B | Cut-off word | "The perfect gift doesn't exi-" | store-shelf footage |
| B | Friend dare / send-to | "Send this to a horse girlie 🙈✨" | group/self-purchase niche items |
| X->A (pets) | Problem -> solution | `The problem 😕 -> The solution 😊` (never "The result", MR50) | pet products (7.6M competitor family); weak elsewhere |

**Name the recipient, not the buyer.** 10 of 12 reels over 100K named mom/wife/grandma/women; buyers skewed 35-65+.

## 3. Production spec (what the gate enforces)

- **Generation:** Seedance 2.5 via Higgsfield, start frames only (GPT Image, refs always attached), **720p**, 4 s gens.
  Hook = its own gen; body = 2 shots per gen joined by a hard cut at ~2 s. Show frames before clip spend.
- **Length/pace:** 10-14 s, hard cuts only, a new angle every ~1.4-2 s, no fades or lingering shots.
- **Payoff:** at least 2 hard cuts (3+ shots), none longer than 1.5 s; end on the most rewarding image (peak-end).
- **Cards:** ONE card by default, <= 8 words, Apple iOS emoji, visible from its shot's first frame, never over a face,
  literally true for what's on screen. "VS" only on a middle card. No "Get yours", no URL on screen.
- **Music:** the original's song AND section, starting at frame 0, continuous, no loops/splices, no phonk/slowed.
  Real ambient clip audio under it; voices audible.
- **World:** settings the product/subject would really be in (no cat in a store), relatable homes, chronological
  time of day, a US flag where plausible, correct gaze and physics, product exactly matching the real one.
- **Glow products:** lights bright and glowy (white-hot cores, saturated halo, bloom, spill, reflections) but the
  motion trail barely visible (MR49: lagfun decay <= 0.6, trail opacity <= 0.15).
- **Files:** zero metadata on everything (videos AND images), 720x1280 export.
  *(Superseded: the old 1440x2560@30 export and 1080p hooks.)*

## 4. Captions

- Hook-style line + 1-2 emoji + `SAY "WORD" and we'll send you the link` + 3 niche hashtags. Never "Comment"
  (reach penalty for engagement bait), never a store-listing title, never a repeated line on that page.
- At **40K views** (or 10K+ inside one hour) swap to `Get it here 👉 <url>` with the same hashtags.
  *(Superseded: link-in-first-caption. It won historically on one page, but URLs in fresh captions are now banned.)*
- Curiosity/envy lines work: "They'll be asking where you got it..", "Your neighbors are gonna be jealous...".
- Never: "Who's your squad?", "Tag your gang", comfort adjectives ("SO COMFORTABLE😍").

## 5. Posting

- 6 PM-4 AM local: night posts had ~3x the views (n=75, p~0.02); weekends also stronger.
- 2-3 posts/day per page, each a NEW video; keep >= 6 h between posts on a page.
- Retire a hook family after 2 posts under 0.2x the page median for that product.

## 6. Generation craft

- **Lock the product:** the same 3-5 product refs in every frame; re-roll colour drift or a wrong brand name.
- **Same cast and room** across a body; same room for then and now.
- **One action per clip**; never speed up an install/peel beat (>= 2 s).
- **Re-roll tells:** boiling textures, hands merging into product, extra fingers, wrong-room tails (trim them),
  non-English native audio (mute), fake-looking faces (prefer from-behind/POV/hands).
- Put a big reveal in its own generation rather than the second half of a packed gen (packed second halves tend
  to invent props).
- Preflight cost with count=1 and multiply; some price endpoints return per-image cost.

## 7. Consumer psychology map

Every creative choice names the principle, the visible feature that carries it, and how you'd check it.

| Principle | On screen | Check |
|---|---|---|
| Information gap (needs a cue) | card withholds the answer while a partial product cue is visible | answer by ~2-3 s, cue at 0 s |
| Orienting response | unexpected event in 0-1 s (fall, chase, flare-up) | scripted conflict <= 1 s |
| Contrast | bad then -> Vs.. -> good now | payoff in the last 40% |
| Open loop -> closure | last shot answers the hook | final shot = answer |
| Peak-end | last shot is the most rewarding image | product fills >= 60% |
| Touch / endowment | POV hands using the product | >= 2 hands-on shots |
| Self-referencing | viewer-as-actor framing, few face-to-camera shots | face share <= 0.4 |
| High-arousal emotion | awe/excitement/amusement payoff that fits the product world | energy matches product |
| Gifting | names a recipient | hook names who it's for |
| Benign violation | absurd but harmless | nobody really hurt |
| Social proof | others visibly reacting | shown, not claimed |
| Reactance | "Don't show this to..." | category-dependent; test first |

Emoji grammar: one face emoji for the emotion + optional one world emoji at the end of the card; cringe on "then"
cards (😬🤕), payoff 🤩😻✨, humour 😂. Guardrails: no race casting, no minors, no false scarcity, no comment/tag/vote bait.

## 8. Competitor-copy workflow

1. Find the competitor's top reel (sort their reels by views); download it.
2. Split it at its cuts into <= 4 s blocks; note card text, timing and song section.
3. Build start frames for each block with YOUR product, packaging and cast refs; change at most 1-2 things
   (location, cast look, prop). Keep the competitor's pacing.
4. Scrub leftovers: competitor brand names on boxes, watermarks.
5. Gate, then post on one page.

## 9. Product screen (before spending credits)

Score 0-4 each on: visual "wow" in 1 s, giftability / clear recipient, demo-ability in 2 s, price under ~$60,
proven competitor reels. Under 14/20: flag it before spending.
