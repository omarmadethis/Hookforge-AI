
- F96 (2026-10-20): Raw GenerateImage outputs were sent to Omar unstripped; FB flagged them as AI content. Rule: no generated asset is shown or delivered unless it lives on the box, has been stripped, and passes the exiftool/C2PA check. Unreachable outputs are never sent.

## 2026-10-20 - FB caption traction swap trigger (PERMANENT RULE, D93-6)
Omar: the early swap is 10K+ views within an hour, not 1K per hour. Rule: swap the post caption to "Get it here 👉 <product URL>" (same hashtags kept) when a post hits 40K total views OR gains 10K+ views in any one-hour window (incl. the first hour). No other velocity rules. Enforced in engine/hookforge/fb_caption.py traction(); tested in test_fb_caption_d93.py.
- 2026-10-22 10:37 AM PT: Omar sent a frame with long light streaks behind the horse's legs — trails must be EXTREMELY minimal, close to none (~3% or zero). MR49 tightened: decay<=0.3, opacity<=0.03 (default no trail pass), prompts must say 'no light trails, no motion streaks, no long-exposure effect'; reject clips with visible streaks.
- 2026-10-22 10:38 AM PT: Omar: VS videos = 3 parts: hook (janky problem only) -> VS (product being assembled/put on the horse, VS card here) -> result (riding, bright glow, >=2 hard cuts). Never skip VS assembly. -> MR52 (auto vs_structure); MR31 allows 3 cards only for this structure.

- 2026-10-22 11:43 AM PT: MR53 multi-horse afters (Barn Glow), MR54 unrushed assembly >= 2 s / reference length, MR55 beat drop on first after frame +-0.1 s (onset/energy detection). Apply to LR6.
- 2026-10-22 11:44 AM PT: MR56 Barn Glow afters = exactly 3 back-to-back cinematic cuts of glowing horses running (farm/barn/beach only), >=1 multi-horse (MR53). Apply to LR6; LR4 not rebuilt.
