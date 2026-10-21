
## D137 (2026-10-20 PT) PL6 group-insult lint
political_lint PL6 WARN on "fake/fraud/so-called/wannabe/pretend/bandwagon + fans/patriots/supporters/americans/conservatives". Weekly caption pool drops any PL6 text on political products, so 'Fake Trump Fans.. SAY "VOTE"' is gone. The F04 on-screen hook stays as reference but carries the WARN.
## D138 Listing-style captions blocked
publish.is_listing (4+ Title-Case words, or listing words such as with/for…LED/stained glass/programmable). Blocked in publish._caption_checks, skipped in fb_caption.generate, and filtered from the weekly pool.
## D139 Distinct caption TEXT
Caption distinctness (weekly per page and per video, plus the e2e_dryrun distinct_captions stage) compares the caption's own line with hashtags, emoji and the SAY CTA stripped. Page-variant own captions are exempt from the 12-word cap.
## D140 Real still price + lean plan
config.STILL_TIER: gpt_image_2 is 6.5 at 2k high, 3.5 at 1k high, 1.0 at 1k medium. Per-video quote 156 -> 200; standard weekly plan 2,028 -> 2,600. lean_plan.py: one anchor video per product plus hook-only extras that reuse the anchor's B1–B3, with 1 still per gen. That comes to 1,227 (1080p hooks) or 759 (720p hooks); written to learning/weekly_batch/<start>_lean.json. P2 redo now uses 1 still (34.5 <= cap 35). approval_queue is not ready when quote > cap. Daily concepts at 200 > innovation budget 175, so none are recommended; caps are unchanged.

## D141 (2026-10-20 PT) P2 payoff redo archived for good; lean plan uses 1080p hooks only
pv_p2_redo.queue() now returns ARCHIVED_STALE (P2 v2 shipped). It quotes nothing and writes nothing, and the old D140 requote edit is reverted. lean_plan has a single option, lean_1080p_hook at 1,227 credits; the 720p-hook option is removed.
## D142 Near-duplicate video gate for the lean plan
lean_plan.edit_plan gives each video its own order and trim of the shared B1–B3 clips. B3 (the payoff) always closes. Body is at least 6 s, with trims on a 0.5 s grid. lean_plan.check is an exact frame-level LCS (24 fps): no two videos on the same page may share more than 50% of their frames in the same order, measured against the shorter video. Current plan: worst case 40%, 0 violations. Extras run 10 s (4 s hook + 6 s body).
## D143 Daily and weekly budget logic picks lean automatically
concept_lab.daily attaches a lean option to each concept (1 start-frame still per gen, 174 credits, with its own approval-file draft capped at 174). It recommends the full plan if that fits the budget, otherwise the lean one. Today: trumpglow_F09, lean, 174 ≤ 175. The weekly queue item recommends lean_1080p_hook (1,227 credits, cap 1,227, standard 2,600 kept for reference) only when D142 passes.
## D144 JollyGlow caption
"hard to gift" is now caption_forbidden for jollyglow_curtain. The new caption_extra line 'Your window is boring. Fix it 🎄 SAY "LIGHTS"' is adapted from the MerryGlow "Your ceiling is boring. Fix it 🎄" winner (17.4M views, same decor-light category).

## D145 (2026-10-20 PT) Lean editor, real build
lean_edit.build renders a lean video with ffmpeg: the video's own 4 s hook, then the anchor's B1–B3 clips re-ordered and trimmed per lean_plan.edit_plan, finished through autoedit.clean_export (provenance strip).
runner.build_calls_lean: role "anchor" makes H + B1–B3 calls with 1 still each (174 credits); role "extra" makes only the 1080p H calls (70.5 credits).
runner.assemble_lean refuses to render if the reveal check fails. lean_edit.gate_built measures the finished renders (16x16 perceptual frame hash + LCS) and blocks any same-page pair above 50%.
Real test on the local out/live/jollyglow_321 clips (stand-ins: hook G1/G5/G6; bodies B1=G2, B2=G4, B3=G3): 3 videos at 15.0, 10.0 and 10.0 s. Measured overlap 0.40/0.40/0.43 (planned 0.40). Identical control 1.0. Outputs in out/lean_test/ (result.json).
## D146 JollyGlow F06 on-screen hook
F06 for the curtain now uses the poc_hook "POV: the whole street is JEALOUS of your house.. 😏🏠" (own JollyGlow curtain reel fb_28305014139198128, 63,320 views). It replaces "Women are hard to gift.." and is 9 words, which G2 allows as WARN because it is Omar's own ≥50K line verbatim (D67).
## D147 Payoff reveal check
lean_edit.reveal_frame_s finds the reveal as the biggest standout frame change after 0.25 s, or None. reveal_check flags any edit where the reveal falls more than 1.5 s into the payoff segment, is trimmed off, comes less than 0.25 s in (flash frame), or is unknown (human check). lean_plan.edit_plan only picks trims that pass.
## D148 SAY rule on JollyGlow
hook_variants.CTA jollyglow = SAY "LIGHTS". publish.ensure_say adds SAY "<KEYWORD>" before hashtags when a caption is missing it, and the weekly batch applies it to every caption. All 20 slots now carry a SAY CTA.

## D149 (2026-10-20 PT) 8-word hook rule, no exceptions
G2 blocks any hook over 8 words, including Omar's own past lines (the D67 own-line WARN exemption is removed). Text cards are also capped at 8 words (was 10). planner._pick_hook only considers lines of 8 words or fewer; longer lines stay as reference data. JollyGlow F06 hook = "POV: the whole street is JEALOUS 😏🏠" (6 words).
## D150 Slow-reveal detection
lean_edit.reveal_info combines two detectors:
- ramp: ffmpeg signalstats |ΔYAVG| + |ΔSATAVG| + 0.5|ΔYHIGH| over 0.75 s windows, threshold 6 (8-bit); the reveal is where the ramp is half done.
- cut: the existing hard-cut/flash detector.
The ramp wins when present. JollyGlow results:
| Clip | Result |
|---|---|
| G1 | ramp, 4.50 s (Santa build) |
| G2 | cut, 0.83 s (lid) |
| G3 | ramp, 3.38 s (lights ripple; the 1.54 s hard cut is no longer taken as the reveal) |
| G4, G5, G6 | none (steady "after" footage; flagged for a human look) |
## D151 Lean dry render, trumpglow + purrventure
scripts/lean_dry_render.py runs this week's real slot map on local clips with stand-in hooks (x264 draft, no Higgsfield calls). Output goes to out/lean_dryrun/<day>/report.json.
| Product | Anchor clips | Payoff reveal | Videos | Reveal checks | Max measured overlap |
|---|---|---|---|---|---|
| trumpglow | trumpglow_A G3/G4/G5 | ramp, 1.79 s | 7 | 7/7 pass | 41.7% |
| purrventure | P3_G2/G3/G4 | ramp, 1.50 s | 3 | 3/3 pass | 40% |
Overlap gate passes for both.
## D152 Output cleanup
Removed from the box:
- out/lean_test (127 MB)
- out/dryrun placeholder mp4/mov renders (513 MB; the purrventure worker's folder was skipped; plans and md kept)
- out/live/*/final/_tmp* intermediates (~900 MB)
- 2 stale proxy .tmp.mp4 partials whose finished file exists
The list is in out/CLEANUP_2026-10-20.txt. Untouched: out/deliver, final deliverables, drive_up, Drive. One partial (lib_159311963a) was kept because it has no finished file.

## D153 (2026-10-20 PT) Buffer draft-payload preflight
Omar clarified that the 8-word rule covers on-screen text only. FB post captions stay as the proven winners (no change).
buffer_preflight.run builds the exact publish.build_payload create_post payload for every weekly slot of the 3 active products and validates it four ways:
- Buffer's own create_post inputSchema, read-only via GetDynamicTools on user-Buffer and snapshotted to config/buffer_create_post.schema.json. This uses jsonschema Draft 7 with format checks, plus a manual URI check because "format: uri" isn't enforced without rfc3987.
- The tool's prose rules: facebook.type required; instagram asset + type; reel needs a video; no linkAttachment alongside assets; no thumbnailUrl on video.
- The draft-only rules from publish._check_payload.
- SAY CTA present and no PLACEHOLDER link.
Real URLs are refused if they are share pages or carry presigned/expiring params; only the host is reported, never the URL. Result: 20/20 pass (trumpglow 12/12, purrventure 5/5, jollyglow 3/3), checked against a .invalid stand-in URL because no video is staged yet. Nothing was sent; no Buffer write tools were called.
## D154 One-command regenerate
`cd engine && PYTHONPATH=. python3 -m hookforge.regen` rebuilds, in order: calendar → daily concepts → weekly batch + lean plan → render queue → Buffer preflight → approval digest (analytics/approval_digest.html). It prints one line per artifact and exits non-zero on any failure.
## D155 lean_dryrun pruned
Summary in docs/LEAN_DRY_RENDER_2026-10-20.md. 353 MB removed and logged in out/CLEANUP_2026-10-20.txt. Re-create with scripts/lean_dry_render.py.
