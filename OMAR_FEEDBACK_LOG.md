
- F96 (2026-10-20): Raw GenerateImage outputs were sent to Omar unstripped; FB flagged them as AI content. Rule: no generated asset is shown or delivered unless it lives on the box, has been stripped, and passes the exiftool/C2PA check. Unreachable outputs are never sent.

## 2026-10-20 - FB caption traction swap trigger (PERMANENT RULE, D93-6)
Omar: the early swap is 10K+ views within an hour, not 1K per hour. Rule: swap the post caption to "Get it here 👉 <product URL>" (same hashtags kept) when a post hits 40K total views OR gains 10K+ views in any one-hour window (incl. the first hour). No other velocity rules. Enforced in engine/hookforge/fb_caption.py traction(); tested in test_fb_caption_d93.py.
