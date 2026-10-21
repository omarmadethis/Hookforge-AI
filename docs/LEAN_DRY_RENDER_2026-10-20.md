# Lean-plan dry render — 2026-10-20 (summary; renders pruned D155)

DRY RENDER - stand-in hooks, local clips, x264 draft; nothing generated/sent

## trumpglow
Payoff reveal: 1.792 s (ramp); max measured same-page overlap 41.7%; overlap gate PASS; reveal checks all pass

| video | stand-in hook | edit (clip in→out s) | dur s | reveal at |
|---|---|---|---|---|
| trumpglow_V1 | live/trumpglow_A/clips/G1.mp4 | B1 0→4, B2 0→4, B3 0.5→3.5 | 15.0 | 1.29 s |
| trumpglow_V2 | live/trumpglow_B/clips/BG1.mp4 | B2 0→2, B1 0→2, B3 1.5→4 | 10.5 | 0.29 s |
| trumpglow_V3 | live/trumpglow_C/clips/CG1.mp4 | B2 0.5→2.5, B1 2→4, B3 1.5→4 | 10.5 | 0.29 s |
| trumpglow_V4 | live/trumpglow_A/clips/G2.mp4 | B2 2→4, B1 0.5→2.5, B3 1.5→4 | 10.5 | 0.29 s |
| trumpglow_V5 | live/trumpglow_B/clips/BG2.mp4 | B2 0→2, B1 1→3, B3 0.5→2.5 | 10.0 | 1.29 s |
| trumpglow_V6 | live/trumpglow_C/clips/CG2.mp4 | B2 1→3, B1 0→2, B3 0.5→2.5 | 10.0 | 1.29 s |
| trumpglow_V7 | live/trumpglow_B/clips/BG3.mp4 | B2 1.5→3.5, B1 1.5→3.5, B3 0.5→2.5 | 10.0 | 1.29 s |

Measured pairs: patriotsglow_fb:trumpglow_V1~trumpglow_V2 38%, patriotsglow_fb:trumpglow_V1~trumpglow_V3 38%, patriotsglow_fb:trumpglow_V1~trumpglow_V4 36%, patriotsglow_fb:trumpglow_V1~trumpglow_V5 38%, patriotsglow_fb:trumpglow_V2~trumpglow_V3 40%, patriotsglow_fb:trumpglow_V2~trumpglow_V4 36%, patriotsglow_fb:trumpglow_V2~trumpglow_V5 34%, patriotsglow_fb:trumpglow_V3~trumpglow_V4 31%, patriotsglow_fb:trumpglow_V3~trumpglow_V5 32%, patriotsglow_fb:trumpglow_V4~trumpglow_V5 28%, trumpglow_fb:trumpglow_V1~trumpglow_V2 38%, trumpglow_fb:trumpglow_V1~trumpglow_V3 38%, trumpglow_fb:trumpglow_V1~trumpglow_V4 36%, trumpglow_fb:trumpglow_V1~trumpglow_V5 38%, trumpglow_fb:trumpglow_V1~trumpglow_V6 37%, trumpglow_fb:trumpglow_V1~trumpglow_V7 39%, trumpglow_fb:trumpglow_V2~trumpglow_V3 40%, trumpglow_fb:trumpglow_V2~trumpglow_V4 36%, trumpglow_fb:trumpglow_V2~trumpglow_V5 34%, trumpglow_fb:trumpglow_V2~trumpglow_V6 34%, trumpglow_fb:trumpglow_V2~trumpglow_V7 19%, trumpglow_fb:trumpglow_V3~trumpglow_V4 31%, trumpglow_fb:trumpglow_V3~trumpglow_V5 32%, trumpglow_fb:trumpglow_V3~trumpglow_V6 20%, trumpglow_fb:trumpglow_V3~trumpglow_V7 31%, trumpglow_fb:trumpglow_V4~trumpglow_V5 28%, trumpglow_fb:trumpglow_V4~trumpglow_V6 36%, trumpglow_fb:trumpglow_V4~trumpglow_V7 36%, trumpglow_fb:trumpglow_V5~trumpglow_V6 41%, trumpglow_fb:trumpglow_V5~trumpglow_V7 42%, trumpglow_fb:trumpglow_V6~trumpglow_V7 41%

## purrventure_carrier
Payoff reveal: 1.5 s (ramp); max measured same-page overlap 40.0%; overlap gate PASS; reveal checks all pass

| video | stand-in hook | edit (clip in→out s) | dur s | reveal at |
|---|---|---|---|---|
| purrventure_carrier_V1 | pv_clips/P3_G1.mp4 | B1 0→4, B2 0→4, B3 0→4 | 16.0 | 1.5 s |
| purrventure_carrier_V2 | pv_clips/P1_G1.mp4 | B2 0→2, B1 0→2, B3 0→2 | 10.0 | 1.5 s |
| purrventure_carrier_V3 | pv_clips/P2_G1.mp4 | B2 0→2, B1 1→3, B3 1→3 | 10.0 | 0.5 s |

Measured pairs: purrventures2_fb:purrventure_carrier_V1~purrventure_carrier_V2 40%, purrventures2_fb:purrventure_carrier_V1~purrventure_carrier_V3 40%, purrventures2_fb:purrventure_carrier_V2~purrventure_carrier_V3 40%, purrventures_fb:purrventure_carrier_V1~purrventure_carrier_V2 40%

Re-create: `cd engine && PYTHONPATH=. python3 scripts/lean_dry_render.py` (≈6 min, writes out/lean_dryrun/<day>/).