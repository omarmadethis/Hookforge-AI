# Hookforge rules

Generated from `rules/master_rules.json` by `tools/build_rules_doc.py`; do not edit by hand. The master gate
(`engine/hookforge/master_gate.py`) enforces these on every file before it is shown to anyone or published.
The machine table with sources is `rules/MASTER_RULES.md`.

**60 rules.** How each is checked: *automatic* (the gate measures it), *reviewer sign-off* (a human or
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

- **MR03** Every generation is 720p, hooks included (supersedes 'hook 1080p' F10/R10). Final export is 720x1280. [UPDATED by MR60: Kling 4.0 gens are 1080p 9:16; the 720p wording applies to legacy Seedance gens and the gated 720x1280 master that MR59 then upscales.]  
  _Check:_ automatic (`res_720`). _Fix:_ regenerate footage (within the approved credit cap). _Applies to:_ video.
- **MR04** Hook = its own single 4 s generation; body clips packed 2 per 4 s generation joined by a hard cut.  
  _Check:_ automatic (`gen_packing`). _Fix:_ regenerate footage (within the approved credit cap). _Applies to:_ video.
- **MR05** Every gen <= 5 s (4 s typical), never 8 s; hook <= 5 s on screen.  
  _Check:_ automatic (`gen_len`). _Fix:_ regenerate footage (within the approved credit cap). _Applies to:_ video.
- **MR06** Seedance 2.5 only (no Kling); start frames only, never end frames. [UPDATED by MR60 2026-10-23: Kling 4.0 (kling4_0) is now the required model for all new videos; Seedance only validates for legacy/already-posted specs; start-frames-only still applies.]  
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
- **MR49** Glow trail / motion blur behind lights is EXTREMELY minimal, close to none: no streaks behind the horse at all, only the bright glow on the product itself (white-hot cores + halo/bloom). Post trail pass: lagfun decay <= 0.3 and trail opacity <= 0.03 (default 0 = no trail pass); prompts must say 'no light trails, no motion streaks, no long-exposure effect' and never ask for trails; any clip with visible streaks is rejected.  
  _Check:_ automatic + reviewer sign-off (`glow_trail`). _Fix:_ regenerate footage (within the approved credit cap). _Applies to:_ video.
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
- **MR31** ONE on-screen card by default; a 2nd only for a problem-vs-solution / then-vs-now hook or a closing 'get it from the caption below 👇' card; 3 cards ONLY for the MR52 idea / VS / result structure (VS on the middle card); never 4+.  
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
- **MR52** VS / idea-vs-result videos have 3 parts in order: (1) HOOK = the problem, only the makeshift janky version (duct tape etc.); (2) VS = a separate segment right after the hook showing the product being ASSEMBLED / put on the horse, the VS card starts here; (3) RESULT = the afters, riding with the bright glow, >= 2 hard cuts. Never skip the VS assembly segment. Spec shots carry role hook/vs/after.  
  _Check:_ automatic.
- **MR53** Barn Glow / LumaRein afters ALWAYS include multiple glowing horses: at least one after shot with 2+ horses wearing the product (spec shots[].horses, confirmed on the render).  
  _Check:_ automatic + reviewer sign-off.
- **MR54** Assembly / VS segments are never rushed: the product assembly reads clearly, >= 2.0 s on screen and >= the reference's assembly length (spec.reference.assembly_s) when recreating.  
  _Check:_ automatic.
- **MR55** The song's beat drop lands exactly on the first frame of the afters (+-0.1 s): drop detected by onset/energy analysis of the used song section; align song in_s (or the cut) so the drop hits the after cut.  
  _Check:_ automatic.
- **MR56** Barn Glow afters = EXACTLY three back-to-back cinematic cuts of the glowing horses running, in relevant settings only (farm, barn in the background, occasionally a beach); never irrelevant places. With MR53, at least one of the three shows multiple horses. Spec after shots carry setting + action.  
  _Check:_ automatic + reviewer sign-off.
- **MR57** Barn Glow afters = EXACTLY 3 FAST, realistic-feeling cuts in this order and style (ref/afters_ref_pov.mp4): (1) side tracking shot of a glowing rider galloping on a beach at night, camera moving very fast to keep pace; (2) FIRST-PERSON RIDER POV gallop - horse's neck, mane and ears stretching forward over a dark rolling field at night, glowing collar/strap, aggressive handheld shake, extremely fast forward speed, edge blur, NO hands or reins, another glowing rider ahead (ALWAYS include this shot); (3) 2-horse side-by-side shot (blue + green), high tracking angle across a twilight countryside. Never slow or floaty: prompts use fast gallop + aggressive camera wording (no slow/floaty words), render motion must reach the per-style speed floor, slow-motion-looking or stiff clips are rejected. Keep MR49 (near-zero trails) and MR53/55/56; only characters, colors and settings change. Spec after shots carry style (side_tracking|rider_pov|high_two_horse), prompt, pov flags, horses/colors.  
  _Check:_ automatic + reviewer sign-off.
- **MR58** ALL Barn Glow / LumaRein footage (hook, VS assembly and afters) looks like GENUINE handheld iPhone video, like the competitor's: vertical, slight handheld shake, real phone-sensor noise and grain in low light, slightly imperfect autofocus and exposure, usual phone dynamic range and sharpening, real-world lighting; NO cinematic or polished AI sheen, no plastic skin, no perfectly smooth gimbal motion, no glossy 3D-render glow. Every Seedance and image prompt carries 'shot on iPhone, handheld, real phone video, authentic, unedited look' language and never cinematic wording; spec.phone_look flags + shots[].prompt are checked; reviewer signs off that every clip looks like real phone footage - any clip that looks AI-generated is rejected and regenerated. Extends MR57; keep MR49 (near-zero trails) and MR01 (zero metadata). Footage look only: our own post grade still adds no grain/sharpening (MR12). For Barn Glow this overrides the 'not grainy/sharp, nothing cinematic' tail of the generic iPhone-12 suffix (the iPhone/realism wording still satisfies MR10).  
  _Check:_ automatic + reviewer sign-off.
- **MR59** FINAL STEP, after every other gate passes and immediately before posting: every finished video is UPSCALED TO 4K in Higgsfield (upscale_video: provider bytedance, resolution 4k, preset ugc, fps 30, source width/height passed; Topaz 2160p only as a fallback). The file that is posted (and any hosted/Buffer video_url copy) MUST be that 4K upscaled output of the gated video: 2160 px on the short side (2160x3840 for vertical), nothing below 4K. Order: build -> full master gate PASS (720x1280, MR03 unchanged for the gated master) -> upscale to 4K -> download -> re-strip ALL metadata on the upscaled file (MR01) -> verify it against the gated source: audio unchanged, length unchanged (+-0.1 s), card text unchanged (OCR) and visuals unchanged (SSIM) -> bind it to the gated source in <file>.UPSCALE.json -> post. The publish step refuses any file below 4K, any file without a valid .UPSCALE.json binding to a sha-matching PASS report, and any upscaled file that is not metadata-clean. The upscale credit cost counts toward the video's approved spend cap (spend.upscale_credits; reserve 5 cr provisional (Omar 2026-10-23: should cost <= 5 cr/video; lowered from 30) until the first measured job - Higgsfield has no cost preflight for upscale_video). Never upscale or post before the gate passes; never post the 720p master.  
  _Check:_ automatic.
- **MR60** ALL videos are generated with Kling 4.0 in Higgsfield (model id kling4_0; modes text-to-video, image-to-video, reference-to-video, video-edit), 1080p, 9:16, duration 3-30 s - 5 s clips are enough as long as they show everything. Supersedes the Seedance-only rule (MR06) for new videos and the 720p-gens rule (MR03) for generation resolution. Reference recipe: Omar's near-perfect Barn Glow afters gen cost 10 credits for 10 s (video-edit style: his horse clip as the source + Barn Glow kit reference images: Y harness, 4 leg bands, fiber-optic tail, neon blue; red variant swaps blue->red). Saved clip: assets/lumarein/afters_banger/afters_banger_kling_01.mp4 (known flaws: jump cut ~0:07, garbled text on the harness ~0:05, saddle pad pops in ~0:04; clean window ~0:00-0:04). Cost ESTIMATE ~1 credit/second of Kling 4.0 (verified against that single 10 cr / 10 s data point only - confirm from Higgsfield transactions after each gen). Spend rules (plan + cap approved by Omar, MR09) are unchanged.  
  _Check:_ automatic.
