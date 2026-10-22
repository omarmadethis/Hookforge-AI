# Hookforge rules

Generated from `rules/master_rules.json` by `tools/build_rules_doc.py`; do not edit by hand. The master gate
(`engine/hookforge/master_gate.py`) enforces these on every file before it is shown to anyone or published.
The machine table with sources is `rules/MASTER_RULES.md`.

**51 rules.** How each is checked: *automatic* (the gate measures it), *reviewer sign-off* (a human or
vision reviewer confirms it in the spec's `confirm` block), *process* (a habit, not a file check).

**Fix order when a check fails:** free fixes first (strip metadata, re-edit cards, re-lay the song, rewrite the
caption), re-run the gate, loop up to 8 rounds. Footage problems are regenerated only inside an approved credit cap;
otherwise the gate stops at `NEEDS_REGEN_WITHIN_CAP` with the plan. Nothing ships without a PASS report for that exact file.

## Files and delivery

- **MR01** Zero metadata on EVERY deliverable (video, image, pfp, cover, thumbnail, start frame, any file): no EXIF/XMP/C2PA/encoder/AI tags. Auto-stripped then re-verified.  
  _Check:_ automatic (`metadata`). _Fix:_ free fix: sanitize. _Applies to:_ all.
- **MR02** Finished videos go to Omar as in-chat attachments/players, never Drive links.  
  _Check:_ process rule. _Fix:_ no auto-fix. _Applies to:_ video.
- **MR46** Superseded Drive versions get trashed after a new version ships.  
  _Check:_ process rule. _Fix:_ no auto-fix. _Applies to:_ all.
- **MR47** Every Omar fix becomes a permanent rule in this file plus an automated check or required review item.  
  _Check:_ automatic (`rules_registry`). _Fix:_ no auto-fix. _Applies to:_ all.

## Generation (Higgsfield)

- **MR03** Every generation is 720p, hooks included (supersedes 'hook 1080p' F10/R10). Final export is 720x1280.  
  _Check:_ automatic (`res_720`). _Fix:_ regenerate footage (within the approved credit cap). _Applies to:_ video.
- **MR04** Hook = its own single 4 s generation; body clips packed 2 per 4 s generation joined by a hard cut.  
  _Check:_ automatic (`gen_packing`). _Fix:_ regenerate footage (within the approved credit cap). _Applies to:_ video.
- **MR05** Every gen <= 5 s (4 s typical), never 8 s; hook <= 5 s on screen.  
  _Check:_ automatic (`gen_len`). _Fix:_ regenerate footage (within the approved credit cap). _Applies to:_ video.
- **MR06** Seedance 2.5 only (no Kling); start frames only, never end frames.  
  _Check:_ automatic (`gen_models`). _Fix:_ regenerate footage (within the approved credit cap). _Applies to:_ video.
- **MR07** Stills are GPT Image 2 only and every start frame has its product/cast refs attached.  
  _Check:_ automatic (`frame_refs`). _Fix:_ regenerate footage (within the approved credit cap). _Applies to:_ video.
- **MR08** Start frames are shown to Omar before any clip spend.  
  _Check:_ automatic + reviewer sign-off (`frames_shown`). _Fix:_ no auto-fix. _Applies to:_ video.
- **MR09** No credit spend without Omar's approved plan + cap; total spend stays within the cap; always list cost.  
  _Check:_ automatic (`spend_cap`). _Fix:_ no auto-fix. _Applies to:_ video.
- **MR10** Every prompt ends with the iPhone-12 realism suffix (no blur, no warm light, nothing cinematic).  
  _Check:_ automatic (`realism_suffix`). _Fix:_ regenerate footage (within the approved credit cap). _Applies to:_ video.

## Look, cast and realism

- **MR11** Start frames/footage look like a genuine iPhone photo, not AI slop.  
  _Check:_ reviewer sign-off. _Fix:_ regenerate footage (within the approved credit cap). _Applies to:_ video.
- **MR12** No visible grain or sharpening in the grade.  
  _Check:_ reviewer sign-off. _Fix:_ free fix: none. _Applies to:_ video.
- **MR13** A US flag is visible in the video (every clip where plausible), big enough to read.  
  _Check:_ automatic + reviewer sign-off (`flag_hint`). _Fix:_ regenerate footage (within the approved credit cap). _Applies to:_ video.
- **MR14** Gaze and physics correct: no phasing, no blank stares at camera unless staged.  
  _Check:_ reviewer sign-off. _Fix:_ regenerate footage (within the approved credit cap). _Applies to:_ video.
- **MR15** Natural motion; no permanent shock face; not slow/robotic.  
  _Check:_ reviewer sign-off. _Fix:_ regenerate footage (within the approved credit cap). _Applies to:_ video.
- **MR16** Time of day progresses chronologically; settings are relatable homes.  
  _Check:_ reviewer sign-off. _Fix:_ regenerate footage (within the approved credit cap). _Applies to:_ video.
- **MR17** Product shown working and exactly matching the real product (colour, density, box) in every shot.  
  _Check:_ reviewer sign-off. _Fix:_ regenerate footage (within the approved credit cap). _Applies to:_ video.
- **MR20** No race-based casting; never sexualize or feature minors; exclude FEMBOY child content.  
  _Check:_ reviewer sign-off. _Fix:_ regenerate footage (within the approved credit cap). _Applies to:_ video.
- **MR49** Glow trail / motion blur behind lights is barely visible (subtle, only slightly there) - never long smeared streaks like LR1/LR2; the glow itself stays bright, saturated and glowy (white-hot cores + halo/bloom). Post trail pass: lagfun decay <= 0.6 and trail opacity <= 0.15; prompts say 'faint, barely visible trail', never 'long light trails'.  
  _Check:_ automatic + reviewer sign-off (`glow_trail`). _Fix:_ free fix: recompose. _Applies to:_ video.
- **MR51** No illogical settings for the product: every scene is a place the product/subject would actually be. PurrVentures: the cat never appears in a store or garden center - use yards, parks, patios and similar.  
  _Check:_ reviewer sign-off. _Fix:_ regenerate footage (within the approved credit cap). _Applies to:_ video.

## Uniqueness, products and pages

- **MR18** Every video fully unique: zero footage shared with any other video on any page (perceptual hash vs all registered/posted videos).  
  _Check:_ automatic (`footage_unique`). _Fix:_ regenerate footage (within the approved credit cap). _Applies to:_ video.
- **MR19** Never the same video on 2 pages, and never repost a video (reposts get shadowbanned).  
  _Check:_ automatic (`page_unique`). _Fix:_ no auto-fix. _Applies to:_ video.
- **MR21** Only active products (jollyglow_curtain, trumpglow, purrventure_carrier, lumarein); retired products are reference data only; no Roblox.  
  _Check:_ automatic (`active_product`). _Fix:_ no auto-fix. _Applies to:_ video.

## Hook and structure

- **MR22** Hook is a proven POC format (formats/index.json) or a truly scroll-stopping relevant moment; every element POC-backed.  
  _Check:_ automatic + reviewer sign-off (`hook_plan`). _Fix:_ regenerate footage (within the approved credit cap). _Applies to:_ video.
- **MR23** Real point of conflict/action visible in the first second.  
  _Check:_ automatic + reviewer sign-off (`hook_plan`). _Fix:_ regenerate footage (within the approved credit cap). _Applies to:_ video.
- **MR24** 3-2-1 spec: covered product cue at 0 s, everyone counts together, 'let's see how it comes out' on the reveal, split-second (<=0.5 s) reveal, full product saved for the afters, count voices ~+8 LU over the song.  
  _Check:_ automatic + reviewer sign-off (`count321`). _Fix:_ regenerate footage (within the approved credit cap). _Applies to:_ video.
- **MR30** The payoff/after is >= 2 hard cuts (3+ shots), no payoff shot > 1.5 s, never one cinematic shot.  
  _Check:_ automatic (`payoff_cuts`). _Fix:_ regenerate footage (within the approved credit cap). _Applies to:_ video.

## Music

- **MR25** Song starts at frame 0 (no silent lead-in) and plays continuously: no loops, no splices (audio fingerprint vs the reference song).  
  _Check:_ automatic (`song_continuity`). _Fix:_ free fix: recompose. _Applies to:_ video.
- **MR26** Recreations use the competitor's exact song AND section (verified fingerprint in refs/<slug>/songs_verified.json).  
  _Check:_ automatic (`recreation_song`). _Fix:_ free fix: recompose. _Applies to:_ video.
- **MR27** No phonk / slowed+reverb; proven song section people actually use.  
  _Check:_ automatic (`no_phonk`). _Fix:_ free fix: recompose. _Applies to:_ video.
- **MR28** Real ambient clip audio only, never fake SFX; voices audible over the song.  
  _Check:_ reviewer sign-off. _Fix:_ free fix: recompose. _Applies to:_ video.

## Edit and on-screen cards

- **MR29** Straight hard cuts only: no fades, no jump cut inside one take, no lingering boring shot.  
  _Check:_ reviewer sign-off. _Fix:_ free fix: recompose. _Applies to:_ video.
- **MR31** ONE on-screen card by default; a 2nd only for a problem-vs-solution / then-vs-now hook or a closing 'get it from the caption below 👇' card; never 3+.  
  _Check:_ automatic (`card_count`). _Fix:_ free fix: recompose. _Applies to:_ video.
- **MR32** Every card is <= 8 words.  
  _Check:_ automatic (`card_words`). _Fix:_ free fix: recompose. _Applies to:_ video.
- **MR33** 'VS' only ever on the middle card, never on the first card.  
  _Check:_ automatic (`vs_position`). _Fix:_ free fix: recompose. _Applies to:_ video.
- **MR34** No 'Get yours' and no URL on screen or in captions.  
  _Check:_ automatic (`no_get_yours`). _Fix:_ free fix: recompose. _Applies to:_ all.
- **MR35** Card emojis are Apple iOS (Apple Color Emoji) art, pixel-verified against textcards.  
  _Check:_ automatic (`apple_emoji`). _Fix:_ free fix: recompose. _Applies to:_ video.
- **MR36** Every card is visible from its shot's first frame (starts on a cut +-1 frame, >= 1 s, readable contrast on the render).  
  _Check:_ automatic (`card_timing`). _Fix:_ free fix: recompose. _Applies to:_ video.
- **MR37** Card copy makes literal logical sense for what is on screen.  
  _Check:_ reviewer sign-off. _Fix:_ free fix: recompose. _Applies to:_ video.
- **MR38** Cards never cover a face.  
  _Check:_ automatic (`cards_off_faces`). _Fix:_ free fix: recompose. _Applies to:_ video.
- **MR39** Rendered card text matches the approved card copy (OCR) and fits in <= 2 rows.  
  _Check:_ automatic (`card_ocr`). _Fix:_ free fix: recompose. _Applies to:_ video.
- **MR50** Problem-vs-solution card pairs use 'The solution' as the second card, never 'The result' ('The problem' -> 'The solution').  
  _Check:_ automatic (`problem_solution`). _Fix:_ free fix: recompose. _Applies to:_ video.

## Captions and publishing

- **MR40** FB/IG captions use SAY "<KEYWORD>", never 'Comment'.  
  _Check:_ automatic (`caption_say`). _Fix:_ free fix: caption. _Applies to:_ publish.
- **MR41** Before publish the exact caption equals the approved caption and every card equals the approved card spec.  
  _Check:_ automatic (`caption_approved`). _Fix:_ free fix: caption. _Applies to:_ publish.
- **MR42** No caption line repeats a line already posted on that page.  
  _Check:_ automatic (`caption_fresh`). _Fix:_ free fix: caption. _Applies to:_ publish.
- **MR43** Caption is a proven hook-style caption (not a store listing title); no engagement-bait questions.  
  _Check:_ automatic (`caption_style`). _Fix:_ free fix: caption. _Applies to:_ publish.
- **MR44** Nothing is posted without Omar's approval or explicit ask for that post.  
  _Check:_ automatic (`publish_approval`). _Fix:_ no auto-fix. _Applies to:_ publish.
- **MR45** Caption swap only at 40K views or 10K+ within an hour.  
  _Check:_ process rule. _Fix:_ no auto-fix. _Applies to:_ publish.

## Other

- **MR48** Never burn in captions (F04) - SUPERSEDED: on-screen cards are now required (D188); post captions live in the FB caption.  
  _Check:_ SUPERSEDED.
