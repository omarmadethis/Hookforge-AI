# FIRST_LIVE_RUN: the single cheapest real test, now MerryGlow (Omar, Mon 19 Oct 2026, 07:04 London)

Status: **NOT RUN. The live path is DISABLED** (`config.LIVE["enabled"] = False`) and there is no approval file. Nothing has been submitted.
Updated Mon 19 Oct 2026, ~07:15 London (BST). Prices were re-confirmed that morning with Higgsfield `get_cost` on the new account; get_cost submits nothing.
The earlier robe test (3-2-1, also 174 credits) is kept at the bottom as the fallback.

## The test: one finished video, MerryGlow tree lights, then-vs-now (F04, core slot)
Brief: `then vs now video for MerryGlow tree lights`. Dry run: `out/dryrun/then_vs_now_video_for_merryglow_tree_lights/`.

**Why F04.** The data decided; this was not a guess.
- **Own reels on this product (10):** F04 then-vs-now has 8 reels, median 71K, best 153K (MG-01 152,878; MG-02 119,070; MG-04 84,377; MG-05 72,193; MG-06 70,437; MGS-02 64,542). That is 6 of 8 at ≥50K.
- **The alternative:** F01 3-2-1 has 2 reels (MG-03 97,955 and MGS-07 2,191).
- **All 6 F04 winners share one shape:** DISASTER_THEN, a 4–5 person family plus a golden retriever, then the product reveal. Watch was 59–64% (8–9 s average), 3-second rate 0.42–0.51.
- **Engine fit:** F04 scores STRONG (6.0) against F01 4.4.
- **External:** research library and external pages show F13 "Statement NEEDS" (EXT-47 879K, EXT-58 564K, other pages) and a 23.7M silent-reveal projector (a different product). Neither beats own proven evidence for a core slot. F13 is a candidate for a 20% experiment slot.
- **Tangled lights:** this is the "then" disaster. The hook gen shows the dad yanking tangled old string lights, which spark and short out, and the room goes dark. That matches the winners' family-disaster opening (MG-01/02 contact sheets).

## Plan (engine output, 13.2 s)
- **Text cards** (own MG-01 CapCut card set, all ≤2 emojis):
  - "Christmas 2024.. 😬" (0–2.9 s)
  - "And Christmas 2025.. 🤕" (2.9–3.9)
  - "Vs... ⏳" (3.9–8.6)
  - "Christmas 2026 🤩🎄" (8.6–end)
- **Shots:**
  - H, 1080p: THEN 0–2.9 tangled-lights short-out, family jumps, dog runs | THEN2 2.9–3.9 second dark angle
  - B1: BOX 3.9–5.8 plain unbranded box, lid off, LED strands + controller out | INSTALL 5.8–7.9 POV hanging the strands
  - B2: ACT 7.9–8.6 plug clicks in | LIT1 8.6–10.0 whole tree bursts into animated colour (reveal)
  - B3: **PROOF 10.0–11.5 (D49)** normal 6 ft tree in a normal-size living room, real wire + plug, kids react | LIT3 11.5–13.2 hero wide
- **Song:** Wham! "Last Christmas" from **2:50.5 (170.5 s)**. It's on the top 3 own MG reels (153K/119K/84K); own CapCut in-points were 169.8–171.0 s. Alternatives: Mariah AIWFC intro 0:49.6 (MG-06 70K), Bublé 0:32.4 (MGS-02 65K).
- **Caption:** "Get it here 👉 {url}". Proven on this product (MG-01, 152,878).
- **US cues:**
  - sectional couch, big flat-screen TV, mantel with stockings
  - small American flag (D24)
  - a cul-de-sac with neighbours' lights (alternative setting)
- **Checks:**
  - D42 pre-flight linter clean
  - plan_checks [] and logic_check passed
  - psych score 7 (advisory): PS01/03/04/05/12/13/15/16/19
  - tier-1 audience score 35/100 (advisory, never blocks; no US-creator collab or US-only text cue in this plan)
- **Posting window (MG page):** 18–21 or 21–24 PT, which is **02:00–05:00 or 05:00–08:00 London**. 20% of slots explore other windows.
- **Plan sha256:** `543c6b31407e61d1a1da332d31025fe8ff74e81a6c4521a70ab3d98ed1b524be`. Any prompt edit changes it and closes the gate.
- **Animatic** (mock clips from MG-01, not for posting): `animatic.mp4`. **Contact sheet:** `preflight/animatic_sheet.png`.

## Exact credit cost: 174 credits; cap 244.5 with one hook re-roll
| step | model / settings | credits (get_cost, exact) |
|---|---|---|
| H_still | gpt_image_2, 2k, high, 9:16 | 6.5 |
| H_video | seedance_2_5 omni_reference, 1080p, 4 s, 9:16 | 64 |
| B1/B2/B3_still | gpt_image_2, 2k, high, 9:16 | 3 × 6.5 = 19.5 |
| B1/B2/B3_video | seedance_2_5 omni_reference, 720p, 4 s, 9:16 | 3 × 28 = 84 |
| **total** | | **174.0** (ceiling 175) |
| re-roll reserve: 1 hook re-roll (video 64 + still 6.5) | | +70.5, so **cap 244.5** |

- Re-rolls only happen when vision_judge (D56) is certain (≥0.9) of an absurd failure, max 1 per shot. Any spend beyond the cap is refused.
- **Account: `user-Higgsfield--new-account`** (enterprise, **10,496.49 credits**, read Mon ~07:10 London).

## Product reference image
**`out/live/refs/merryglow_lights.png`** (1440×1860). It's a frame from our own top reel MG-01 (152,878 views) at 9.5 s: the lit tree showing the animated train/cloud/snowflake design.
- The burned-in "Christmas 2026" caption was cropped off (top 700 px removed). There's no brand text or logo.
- **Rejected:**
  - all 4 Shopify product photos for "Smart Animated Christmas Tree Lights" (merryglows.com): every one has MerryGlow brand text, infographics or a phone UI
  - the MerryGlow box frames
- The other candidates are in `out/live/refs/mg_candidates/`.

## The gate (unchanged, see runner.py / D57)
- `LIVE["enabled"] = True` for the run only.
- live=True.
- `learning/approvals/<run_id>.json` written from `runner.approval_template(plan, run_id, credit_cap=244.5)`, with:
  - Omar's words
  - this plan sha
  - gens [H, B1, B2, B3]
  - the new-account
  - cap 244.5, expiry, single use
- A get_cost quote must come before every paid call, and the run stops on a price mismatch or when the cap would be passed. No resubmission after a timeout.

## Steps (after Omar says yes)
1. `cd engine && python3 -c "from hookforge import planner, runner; p=planner.plan('then vs now video for MerryGlow tree lights'); print(runner.plan_sha(p), runner.preflight(p)['ok'])"`. The sha must equal the one above.
2. Upload `out/live/refs/merryglow_lights.png` to the new account (`media_upload` → PUT → `media_confirm`; no credits) and keep the media id.
3. Write `learning/approvals/mg-tvn-001.json` (cap 244.5, +24 h) and set `LIVE["enabled"] = True`.
4. `runner.start_run(plan, "mg-tvn-001", live=True, product_media_id=<id>)`.
5. Loop `next_call` → get_cost → `record_cost` → paid call → `record_submit` → wait (`job_status`) → `record_result`. For each video, run `runner.judge(run, step, clip, "merryglow_lights")`.
6. Set `LIVE["enabled"] = False`.
7. Edit, then `autoedit.clean_export` (C2PA strip, D44, `final_checks` provenance clean), then the CapCut draft. Posting is manual (Omar).
8. Log the outcome in `learning/experiments.csv`.

## Approval line for Omar
"Approve live run mg-tvn-001: 1 video (MerryGlow tree lights, then-vs-now, tangled-lights 'then', Last Christmas 2:50), 4 Seedance 2.5 clips + 4 GPT Image 2 start frames on the Higgsfield new account (10,496 credits available), 174 credits, cap 244.5 (one hook re-roll allowed)."

## Fallback: Grinch robe 3-2-1 (previous first test)
Also 174 credits on the new account. Plan sha `67365456ff0cba3978c80634635914e3984d32cfa2b081b4c7f11b5ac3879fd1`. Use a clean robe frame from own HJ-05 footage, not the branded box image.
