# raw_vs_final: how Omar edits (built 2026-10-19 PT)

| File | What |
|---|---|
| PERFORMANCE_RANK.md / performance_all.csv | 96 own reels (FB + IG) ranked by views, with shares/saves/follows |
| pairs.csv | 286 rows: one per clip segment of each paired reel (draft, raw file, gen uuid, raw length, in/out, head/tail cut, timeline start/dur, speed, volume, scale/crop, model, prompt, reuse count, match confidence) |
| draft_segments.csv | every segment (video/text/audio) of all 110 CapCut drafts (mirror of ~/Movies/CapCut/.../com.lveditor.draft) |
| draft_reel_match.csv / draft_to_reel.csv | draft → posted-reel matching (CLIP of draft timeline vs reel frames, ±1 s offset) |
| draft_features.csv | per-draft shots, avg shot, cards, song and in-point, muted/sped clips vs views |
| recon_top.csv | frame-level reconstruction of top reels whose drafts are gone |
| rejected_clips.csv | gens in each draft's generation window never used in any draft |
| contact_sheets/ | top 5 pairs: FINAL frame vs RAW start/in/out/end, plus trim/speed notes |
| EDIT_RULES.md | the checkable rules |
| scripts | parse_drafts.py, match_drafts.py, pairs.py, fill.py, recon.py, sheets.py |

Method: the drafts' `draft_info.json` give exact in/out, speed, volume and text. Raw clips were identified by Mac path → low-res proxy CLIP embeddings (team/mac). Deleted raws (BrickHood 09-28..10-01) were matched by gen uuid → Higgsfield frame embeddings, or by exact export duration. Models were looked up read-only on Higgsfield (new account; the main account didn't have these ids). The MCP doesn't expose prompts, so prompts come from hf_match and the Mac Claude transcripts and job JSONs.
