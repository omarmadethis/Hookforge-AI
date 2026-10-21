# style/ (Hookforge style, emoji and shot workstream, 2026-10-18 PT)
| file | what |
|---|---|
| capcut_text_preset.json | **Machine spec**: CapCut material fields (for capcut_export) + render constants (for the auto-edit) + edit/music defaults |
| render_text.py | `render_card(text,W,H,scale,y)` → RGBA text layer (Montserrat Medium ≈ CapCut System font, colour emoji); `burn(frame,out,text)` |
| STYLE_GUIDE.md | Human spec: default text style, variants, winners vs flops, edit and audio defaults, verification |
| text_styles.csv | 148 text elements × 70 style fields (text, emojis, font, size, fill, stroke, shadow, bg, spacing, align, anims, x/y/% from top, scale, rotation, timing, concurrency, lines/chars) |
| segments.csv | 837 segments: video (speed, volume, scale/x/y, crop, keyframes, transition, hf clip), audio (song, in-point, volume, fades), adjust layers |
| style_stats.json | aggregates (all, hook card, winners vs flops, by format, by page, music in-points, video defaults) |
| verification_textrows.csv | 16/16 hand-verified rows (11%) |
| emoji_rules.json / emojis.md / emojis.csv / emoji_usage_rows.csv / emoji_count_vs_hit.csv | emoji catalogue, proven + avoid lists |
| shots.csv / shots_by_reel.csv / shot_codes.py / shots_by_reel.py / shot_grammar.md / shot_prompt_phrasings.csv | hand-coded shot table (52 reels) and grammar + Seedance phrasings |
| covered_hooks.csv / covered_hooks.py / covered_stats.json | covered-reveal hook audit (16 edits + PV-02 without views; max views across FB/IG copies; covered vs other stats; cue/reveal split), 2026-10-18 ~10 PM PT |
| extract_capcut_style.py, style_stats.py, emoji_analysis.py | reproducible scripts (run from /workspace/hookforge) |
| _work/ | frames, calibration and verification renders (private: contains posted-reel frames) |
