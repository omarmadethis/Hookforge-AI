# Lessons: what worked, what failed, and why

Every item here cost views, credits or the owner's patience. Most became a rule (see `docs/RULES.md`).

## What worked

| Lesson | Evidence | Why it works |
|---|---|---|
| Recreating a proven viral original 1:1 (hook beat, card pattern, pacing, exact song section) | Recreations of a 1.2M "POV: wife said NO" reel, a 7.6M pet problem/solution reel and a 171.6K horse-tack reel all passed and went live in one evening | The format is already proven with that audience; you only change the product |
| One clean card instead of three | Owner feedback after a 3-card video; then-vs-now and problem/solution are the only 2-card exceptions | Fewer words = faster read in the 2-second window |
| Hook = its own 4 s generation; body packed 2 shots per gen | Halves body cost (~28 credits per 4 s 720p clip) with no visible quality loss | Seedance's 4 s minimum would otherwise waste half of each body clip |
| 720p everywhere | 1080p hooks cost more and nobody could see the difference on a phone feed | Feed compression flattens resolution |
| Start frames with refs attached, shown before clip spend | Caught wrong products and odd casting before paying for video | Frames cost ~1-6.5 credits; clips 28 |
| Night posting | ~3x views for 6 PM-4 AM posts (n=75) | Matches the 35-65+ buyer audience's scroll time |
| Naming the recipient | 10 of 12 reels over 100K named mom/wife/grandma | Gift buyers self-select |
| SAY "WORD" captions + link swap at 40K | Avoids engagement-bait penalties; link appears once a reel has momentum | Platform demotes "comment X" bait and fresh link posts |
| An automatic master gate with a fix loop | Stopped re-explaining the same rule; every fix becomes a check | Humans forget; tests don't |

## What failed

| Failure | What happened | Why | Rule |
|---|---|---|---|
| Identical reposts | 6.6M -> 2.2K; 1.4M -> 16K; a duplicate on 2 pages | Platforms detect and suppress duplicates; pages risk shadowbans | MR18, MR19 |
| Reusing footage across "different" videos | Same clips under new text | Same as reposting to the detector | MR18 |
| Three cards on one video | Owner had never asked for it | Clutter; slows the first read | MR31 |
| Non-Apple emoji on cards | Noto/system emoji rendered | Looks off-platform and cheap to iPhone viewers | MR35 |
| Wrong song / wrong section on a recreation | A generic track replaced the original's | The song section is part of what made the original work | MR26 |
| Song starting late or looping | Silent lead-in; audible loop seam | Silence at 0 s loses the scroll | MR25 |
| "The problem -> The result" | Reads oddly; the proven pair is problem -> solution | Pattern fidelity | MR50 |
| Cat in a store | Illogical setting for the subject | Breaks belief instantly | MR51 |
| Glow trails way too long | Smeared light streaks behind LEDs looked fake | Over-processed; the original had crisp lights with bright halos | MR49 |
| Cards over faces / cards appearing mid-shot | Text covered the reaction; card popped in late | Faces carry the emotion; late cards miss the 2 s window | MR36, MR38 |
| Unstripped AI metadata | Generated images were flagged as AI content | C2PA/EXIF tags are read by the platform | MR01 |
| Cinematic AI look (warm light, blur, grain) | Viewers scroll past "AI ads" | Organic reels must look like a phone video | MR10-MR12 |
| One long cinematic payoff shot | Retention dropped at the payoff | Needs >= 2 hard cuts | MR30 |
| No real conflict at 0-1 s | Hooks that only "set the scene" lost viewers at 0:02 | Orienting response needs an event | MR23 |
| "Comment X" captions, engagement-bait questions | Low reach | Platform engagement-bait demotion | MR40, MR43 |
| Packed second halves inventing props | Generic logos and wrong trucks appeared after a hard cut | The model drifts without a start frame for shot 2 | playbook §6 |
| Cost preflight with count>1 | Billed double the cap | Price endpoint returned per-image cost | playbook §6 |
| Speeding up the install/peel beat | Looked fake and rushed | Satisfying beats need >= 2 s | failure memory |
| Hooks/footage reused at 1080p, "lean reuse" | Superseded by the uniqueness and 720p rules | Duplicate detection + cost | MR03, MR18 |

## Process lessons

- **Every owner correction becomes a rule plus a check (MR47).** Saying "that's on me" and repeating the mistake is
  the failure mode this whole gate exists to prevent.
- **Fix it yourself.** When a check fails, apply the free fix, re-run, loop; only regenerate inside the approved cap.
- **Strip metadata from every file without being asked**, images included.
- **Spend only inside an approved plan + cap; log every credit.** Watch for outside spend on shared accounts and
  turn off auto top-up if you need a hard ceiling.
- **Nothing gets posted without an explicit OK** for that post, and the caption is checked against the approved text.
- **Platform identity checks can block a page** (Facebook may ask a page to confirm identity); clear it in the
  Facebook app, then push the same queued post rather than creating a new one (avoids a repost).
