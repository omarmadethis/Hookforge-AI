# Evidence: Members pass 2 (copied from /workspace/hf_match/members/pass2_REPORT.md; rules MP2-1..MP2-9)

Inputs: 80 distinct Members-tab generations, in `members/clips/`. The 2 "(1)" duplicates of 6c1cd3e1 and 7e2f6f67 were deleted. Index: `members/clips_index.csv` (id, full id, filename, member, created UTC, ffprobe duration/res/codec/fps/audio, catalogue status, pass-1 flag, visual description, inferred change, prompt pattern, prompt status). Prompts: `members/prompts_pass2.json` (35 entries). Reviewed candidates: `members/matches_members_pass2.csv` (source=members_pass2). Proofs: `proof/members_pass2/`.
Nothing was generated, no credits were spent, and the matching ran at nice 19.

## 1. Clip inventory
- 80 clips: 23 were in pass 1 and 57 are new (pass 1 listed 24 ids, but 9192aba8 was not in this download).
- **34 of 80 were already in our phase-2 catalogue**, so they had been matched before:
  - 30 are in the AIO Ventures shared "Unfiled_Videos" folder (CDN owner user_3CSe…). Their file uuid differs from the job id. I infer this owner is **shiningdonut1538**.
  - 4 are in the new-account's own history: 7dc03c5d, 3938aa35, 58860351, 80e00515.
- The other 46 are in members' private histories. The Members download does not attribute them, so the member is unknown: one of glowinggarlic1527, hockneyruler1880 or throbbingcamel1387. Pass-1 notes name "isaac" for 79a76d8a and 1ca2248a, and "abdallah" for 56829d58 and 0fa9e481.
- Format: 74 are 1080x1920 HEVC, 3 are 1078x1920, and 2 are 720x1280 H.264 (cb773019, d0cae9cb). **f90b878c is landscape 1920x1080.** Durations are 4.04–4.06 s, with one at 5.05 s.
- Prompts:
  - 31 full prompts were read read-only with job_display (folder 6ad62ba9 for the shared ones). 4 had already been fetched in phase 2.
  - 3 shared jobs return no text because they are edit/tool jobs: 0ea972db, d59908c1, 1aa87f73.
  - 7b3bc8c5 has a partial prompt from the browser.
  - **The other 45 member-private ids are not reachable:** job_display and show_generation_by_ids on both user-Higgsfield and user-Higgsfield--new-account return "Generation not found or not accessible" (tested on 7b3bc8c5 and 56829d58). get_project_asset_prompt needs a project placement_id, so it doesn't apply.

## 2. Matching (same method as phase 2, plus a pixel-level control)
Method:
1. Frames at 4 fps.
2. CLIP ViT-B/32 embeddings with the same crop as phase 2 (drop the top 18% and bottom 8%), compared against all 63 posted reels (`emb_reel.npz`).
3. Per (reel, clip) pair, the max frame cosine and a diagonal sequence score.
4. All 73 pairs with cos ≥ 0.92, plus the top 3 per big unmatched reel, were checked by eye on 3-frame side-by-sides (`review_pass2/r_*.jpg`).
5. The 10 strongest got hi-res aligned pairs (`hires/*.jpg`), 2 fps filmstrips and one 4 fps fine strip.
6. **New control:** all-pairs 12 fps pixel NCC over 2 s windows, which tolerates speed ramps. A known phase-2 true match (8f761a37 → 147K) scores **0.986**. A known sibling take (ada3ab4b → 524K) scores **0.929**.

**Result: 0 new exact matches.**
- The best cosine of any clip against any reel is 0.966 (79a76d8a → fb_6.2K_28206279789000326). Every phase-1/2 verified match was ≥ 0.970 (median 0.994).
- 79a76d8a scores **NCC 0.784**, below even the sibling control, so it is a re-roll and not the posted footage.
- Coverage is unchanged at **31/63 reels and 119 shot rows**. **No row was appended to matches.csv**, because nothing passed. The reviewed candidates are in `matches_members_pass2.csv`.
- **Big unmatched reels: 0 of 8 matched.** Best candidate per reel:

| Reel | Best clip | cos |
|---|---|---|
| 2.7M | 61035b7c | 0.924 |
| 524K | 1232877c | 0.921 |
| 326K | 98e696f7 | 0.886 |
| 183K | cf41eabc | 0.933 (sibling) |
| 165K | d7bf7598 | 0.946 (sibling, also phase-2 proof 083) |
| 97K | 82a0dca2 | 0.917 |
| 90K | 1aa87f73 | 0.934 (sibling) |
| 47K | 1ca2248a | 0.795 |

### Sibling takes: same source video or start frame, different roll (useful proxy evidence)
| Posted reel (views, hook) | Clip(s) | What is shared | What differs | Proof |
|---|---|---|---|---|
| fb_6.2K_28206279789000326 "A grinch heated blanket?" | 79a76d8a (isaac, i2v hood flip) | same woman, bed, robe, heart placement, hood-flip beats | eyes/hair, warmer grade, faster flip; NCC 0.784 | hires/79a76d8a__…, fine_79a76d8a_6.2K.jpg |
| fb_6.6M_1624473615929591 "Women are hard to gift.." (also 2.2K_1610499813849290 and 91K_28171203645867196, which reuse that footage) | 9aca3a1a, 8ca0e409 (shiningdonut) | couch, red pillow, rug, foot-hole robe | hands/phone, legs, framing; NCC 0.566 | hires/9aca3a1a__…, strip_9aca3a1a__… |
| fb_165K_2176512149911383 "DO NOT let your wife see this" | d7bf7598, c30309c1 (shiningdonut) | man wraps into robe on couch, same action | room/lamp/person | review_pass2/r_01.jpg |
| fb_90K_952384320521622 "Moms are so hard to gift" | 1aa87f73 (shiningdonut, tool job) | same girl, maroon snowflake pajamas, robe-open pose | room (panelled vs apartment); NCC 0.519 | hires/1aa87f73__fb_90K… |
| fb_101K_1976820096287385 and fb_304K_1410913797833886 "Women are hard to gift.." | c9b866df (unattributed) | same couch-wrap choreography: woman wrapped, man stands, wraps, sits | man and room; NCC 0.341 | strip_c9b866df__… |
| fb_16K_1655048449619269 "DO NOT let your mom see this" | 1ca2248a (isaac); 80e00515 (new-acct) | same woman/living room (1ca2248a); back-view put-on (80e00515) | outfit/pose; room | r_00.jpg, r_03.jpg |
| fb_183K_1103827319264144 "DONT show this to your Grandma" | cf41eabc | same curl-up-in-robe action | couch/room/person | r_03.jpg |
| fb_4.6K_973615392415491 | 80e00515 | back-view robe put-on | room | r_02.jpg |
| fb_3.7K_1081446424374980 | 0fa9e481 (abdallah) | lie-down on bed in robe | room | r_05.jpg |

**Which members' clips reached posted reels:**
- **None exactly.**
- By sibling linkage, these members' prompt families sit behind posted viral reels:
  - **shiningdonut1538:** the 6.6M couch shot family, 165K and 90K.
  - **isaac:** 6.2K and 16K.
  - **unattributed c9b866df:** 101K and 304K.
  - **unattributed cf41eabc:** 183K.
  - **new-account owner:** 16K and 4.6K.
- The posted takes themselves are rolls that are still not in any space we can reach. This repeats the phase-2 near-miss finding: the team rolls the same prompt many times and posts one take.

## 3. What each clip changes (prompt pattern counts; full per-clip table in clips_index.csv)
- **P1 "Recreate @video 1:1 perfectly… only N changes: Change 1 swap robe (hood on) / Change 2 remove caption / Change 3 background → @image" (60 clips; 31 confirmed by text).** Sub-variants:
  - (a) Robe swap only: bc82e4d7.
  - (b) Robe swap plus the camera-holder also in the robe: 1232877c, 437ecf7b.
  - (c) Robe swap plus inserted dialogue in the subject's "natural voice": e665b3c8 (spoken CTA "…link in our page"), a1ffc2e4, c758deb5, 949cdf1b, 18bc9e36, 9aca3a1a/8ca0e409.
  - (d) Feature/action transplant from a second video: 18bc9e36 (plug-in remote), 9aca3a1a (foot holes).
  - (e) Reveal-under-object, keeping the prop: 1cd5837a (bowl), 296ceaba (sheet pan).
  - (f) Blanket-unroll reveal plus background swap: a6f87a80, 4b3197f8, 6c1cd3e1, 23536f80.
  - (g) Couch/background swap plus robe and hood: d7bf7598, c30309c1, f23fe7af.
- **P2 short "replicate 1:1 however…" (new-account, Sep 9–20):** 7dc03c5d (store shelf box swap plus red→green furry blanket), 58860351, 80e00515 (scenery "keep it christmasy" plus blanket → Grinch version).
- **P3 multi-reference choreography transfer (Aug 24–25, shiningdonut):** c094da54, 89b569a5, f175a54e, 49f86801, 0399685f, 6f210cde. That is video_1 motion, optionally video_2 framing, image_1 background, image_2/3 Santa and Grinch robes, and image_4/5 characters: a 2-person 3-2-1 reveal. **No posted sibling found.**
- **P4 person swap keeping the product:** d0cae9cb, 3938aa35.
- **P5 text-to-video scene script / start-frame i2v:**
  - cb773019 is a long T2V script with a 3-2-1 onesie bounce.
  - 79a76d8a and 1ca2248a are i2v hood flips.
- **P6 edit/tool jobs with no prompt:** 0ea972db, d59908c1, 1aa87f73.
- **Other product (Grinch plush):** 4ebab18e, 5112dcab, 92f9b44e (plate-lift reveal; 92f9b44e has a "GrinchBuddies" logo).
- **Inferred P1 robe/hood swaps in member-private clips (45).** Recurring visual families:
  - Hood flip: 3c93c4e1, 435a1054, 2d34c26e, 1ca2248a, 79a76d8a.
  - Wings-open showing white lining: 61035b7c, 7e2f6f67, 4aa80343, 1148314f, e3979fd4, 48b59913, 173ae574.
  - Wrap/lie down: cf41eabc, 0fa9e481, 56829d58, 9fb103c4, 47440079, 82a0dca2, 44351552.
  - Bathroom put-on (one man): 25e505a7, 05a4ab45, 627eb1a5, 87c567a0, 173ae574, c9df4eda.
  - Controller demo: 294a0076 (branded "Grinchy Jammies" remote), 120ed5e8.
  - Unboxing: e18e89c9.
  - Outdoor snow: 5a4fa0c8, 09460382.
  - Couple: c9b866df.
  - Pink-robe source: 7b3bc8c5, 6864b4f0.
  - Wearable-blanket unfold: 7f0e6aca, f7a42727.

### Failure modes seen (direct evidence for the QA gate)
- **Product swap ignored on some rolls.** 6c1cd3e1 kept the GREY blanket, while the same prompt worked on a6f87a80 and 4b3197f8. 6864b4f0 swapped only the hood and left the robe pink.
- **Product drift on person-only swaps.** d0cae9cb's 98-character prompt produced a dark-green sherpa robe, not the Grinch robe.
- **Baked captions kept when removal wasn't asked for.** 7dc03c5d and 58860351, which used short P2 prompts. c4112412 is the same, inferred.
- **Wrong aspect ratio:** f90b878c is 16:9.
- **Broken reference tags:** 0399685f has an empty "reference video from ." (the `<<<video_1>>>` tags were lost); its output reveals plain backs.
- **720p outputs:** cb773019, d0cae9cb.

## 4. Lessons and Hookforge rules (each cites clip ids and reel ids)
- **MP2-1: Roll every recreate prompt 2–3 times, QA-select one, and log the losing rolls.**
  - Identical prompts give different outcomes: 6c1cd3e1 failed where a6f87a80 and 4b3197f8 succeeded.
  - The posted 165K, 90K, 6.6M couch shot, 101K/304K and 6.2K reels are each a roll we don't have, from a prompt family we do have (d7bf7598/c30309c1, 1aa87f73, 9aca3a1a/8ca0e409, c9b866df, 79a76d8a).
- **MP2-2: The workhorse that produced our posted viral reels is still P1: "Recreate 1:1 + robe swap with hood on + caption removal + background → @image".**
  - In this pass that is shown by sibling evidence for 165K (d7bf7598's verbatim prompt: couch/background swap, grey→Grinch robe "also wearing the grinch hood", remove caption).
  - It extends the phase-2 template evidence; prompt_analysis v2 §1.
- **MP2-3: Swapping the background or character image while keeping the source choreography is how the team made variants.**
  - Same choreography in different rooms: 1aa87f73 vs 90K; c9b866df vs 101K/304K; d7bf7598 vs 165K; 80e00515 vs 16K and 4.6K.
  - Hookforge should generate variants by rotating background and character reference images on a proven source video, not by rewriting the motion.
- **MP2-4: The "gift-guilt" hooks ("Women/Moms are hard to gift", "DO NOT let your wife/mom see this") sat on comfort/lounging and feature-demo shots.**
  - Couch scroll with foot holes: 9aca3a1a family → 6.6M.
  - Couch wrap: c9b866df → 101K/304K.
  - Wrap on couch: d7bf7598 → 165K.
  - Robe-open pose: 1aa87f73 → 90K.
  - Pair these hooks with lounging/demo body shots.
- **MP2-5: Always state caption removal and "keep the grinch hood on" explicitly, and keep reference tags intact.**
  - Baked captions survived in 7dc03c5d and 58860351.
  - The hood or robe was not applied in 6864b4f0.
  - Tags were lost in 0399685f.
- **MP2-6: Don't use bare person-swap prompts.** Always re-anchor the product with an @image (d0cae9cb drifted to a non-Grinch robe).
- **MP2-7: Treat the 5-image P3 couple-3-2-1 prompts as UNPROVEN.** Six rolls (c094da54, 89b569a5, f175a54e, 49f86801, 0399685f, 6f210cde) have no posted sibling, and 3 of them reveal plain backs. Use them only inside the innovation budget.
- **MP2-8: Dialogue/CTA insertion (e665b3c8, a1ffc2e4, c758deb5, 949cdf1b, 18bc9e36, 9aca3a1a) has no exact posted match.** But the 9aca3a1a family's source sits behind the 6.6M couch shot. Treat spoken lines as a test variable, not a default.
- **MP2-9: The QA gate must reject non-9:16 output (f90b878c) and verify the product appears correctly before edit (6c1cd3e1, 6864b4f0).** This fits Omar's 720p body / full-res hook rule.

## 5. Priority prompt-fetch list (member-private; the connectors cannot read them)
Route: browser detail page https://higgsfield.ai/asset/members/<id>, the same as the Members view.

| # | Id | Why |
|---|---|---|
| 1 | 79a76d8a | Sibling of 6.2K_28206; i2v hood flip, so get the prompt AND the start-frame image |
| 2 | 1aa87f73 | Sibling of 90K; tool job, so read its tool settings on the page |
| 3 | c9b866df | Sibling of 101K and 304K |
| 4 | 1ca2248a | Sibling of 16K; i2v, also hood flip |
| 5 | cf41eabc | Sibling of 183K |
| 6 | 0fa9e481 | Sibling of 3.7K (lie-down family; same source as 56829d58?) |
| 7 | 7b3bc8c5 | Complete the partial pink-robe recreate |
| 8 | 6864b4f0 | Failed roll of the same pink-robe source, for QA contrast |
| 9 | 3c93c4e1 | Hood-flip family |
| 10 | 2d34c26e | Hood-flip family |
| 11 | d59908c1 | Tool job, hood-on profile (112K-style action) |
| 12 | e18e89c9 | Unboxing plus dialogue |
| 13 | 294a0076 | Branded controller close-up |
| 14 | 98e696f7 | Wings-open family (326K best candidate, although cos is only 0.886) |
| 15 | 56829d58 | Lie-down family |

## 6. Honest limits
- The posted takes for the 8 big unmatched reels are still not in any space we can reach.
- 46 member-private clips have unknown member attribution.
- Matching used CLIP plus pixel NCC on posted reel files that cover 63 reels.
