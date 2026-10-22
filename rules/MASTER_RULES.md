# MASTER RULES (D191) - every video and every deliverable passes these before final / shown to Omar / published

Generated from rules/build_master.py. Enforced by engine/hookforge/master_gate.py (auto checks + required reviewer confirmations + auto-fix loop).
Totals: 51 rules - auto 30, auto+manual 6, manual (reviewer must confirm) 11, process 3, superseded 1.

| ID | Rule | Source | Date (PT) | Check | Auto-fix | Applies |
|---|---|---|---|---|---|---|
| MR01 | Zero metadata on EVERY deliverable (video, image, pfp, cover, thumbnail, start frame, any file): no EXIF/XMP/C2PA/encoder/AI tags. Auto-stripped then re-verified. | F35,F87,D44,D99,memory 'zero metadata' | 2026-10-18..2026-10-21 | auto `metadata` | free:sanitize | all |
| MR02 | Finished videos go to Omar as in-chat attachments/players, never Drive links. | memory 2026-10-21 | 2026-10-21 | process | none | video |
| MR03 | Every generation is 720p, hooks included (supersedes 'hook 1080p' F10/R10). Final export is 720x1280. | D181,F99,memory '720p' | 2026-10-20 8:02 PM | auto `res_720` | regen | video |
| MR04 | Hook = its own single 4 s generation; body clips packed 2 per 4 s generation joined by a hard cut. | playbook skill,memory | 2026-10-20 | auto `gen_packing` | regen | video |
| MR05 | Every gen <= 5 s (4 s typical), never 8 s; hook <= 5 s on screen. | F09,H03 | 2026-10-10 | auto `gen_len` | regen | video |
| MR06 | Seedance 2.5 only (no Kling); start frames only, never end frames. | F11,F13,memory | 2026-09-29..10-06 | auto `gen_models` | regen | video |
| MR07 | Stills are GPT Image 2 only and every start frame has its product/cast refs attached. | F12,F88,F92,memory | 2026-10-09..10-20 | auto `frame_refs` | regen | video |
| MR08 | Start frames are shown to Omar before any clip spend. | F41,D69 G8 | 2026-10-19 | auto+manual `frames_shown` | none | video |
| MR09 | No credit spend without Omar's approved plan + cap; total spend stays within the cap; always list cost. | F14,F15,security | 2026-10-03.. | auto `spend_cap` | none | video |
| MR10 | Every prompt ends with the iPhone-12 realism suffix (no blur, no warm light, nothing cinematic). | F02,R02,playbook | 2026-09-27..10-05 | auto `realism_suffix` | regen | video |
| MR11 | Start frames/footage look like a genuine iPhone photo, not AI slop. | F01,F26 | 2026-10-01 | manual | regen | video |
| MR12 | No visible grain or sharpening in the grade. | F58,F89 | 2026-10-20 | manual | free:none | video |
| MR13 | A US flag is visible in the video (every clip where plausible), big enough to read. | F03,R03,memory | 2026-10-04 | auto+manual `flag_hint` | regen | video |
| MR14 | Gaze and physics correct: no phasing, no blank stares at camera unless staged. | F90,F43,D70,F74 | 2026-10-19..10-20 | manual | regen | video |
| MR15 | Natural motion; no permanent shock face; not slow/robotic. | F18 | 2026-10-06 | manual | regen | video |
| MR16 | Time of day progresses chronologically; settings are relatable homes. | F17,F25 | 2026-10-08 | manual | regen | video |
| MR17 | Product shown working and exactly matching the real product (colour, density, box) in every shot. | F16,F30,F69,R30 | 2026-10-08 | manual | regen | video |
| MR18 | Every video fully unique: zero footage shared with any other video on any page (perceptual hash vs all registered/posted videos). | D180,F98 | 2026-10-20 7:42 PM | auto `footage_unique` | regen | video |
| MR19 | Never the same video on 2 pages, and never repost a video (reposts get shadowbanned). | memory 2026-10-21 (B3 dup on TrumpGlow+PatriotsGlow) | 2026-10-21 | auto `page_unique` | none | video |
| MR20 | No race-based casting; never sexualize or feature minors; exclude FEMBOY child content. | F31,H01,security | 2026-10-18 | manual | regen | video |
| MR21 | Only active products (jollyglow_curtain, trumpglow, purrventure_carrier, lumarein); retired products are reference data only; no Roblox. | F96,F97,memory | 2026-10-20 | auto `active_product` | none | video |
| MR22 | Hook is a proven POC format (formats/index.json) or a truly scroll-stopping relevant moment; every element POC-backed. | F104,D186,F72 | 2026-10-21 1:30 AM | auto+manual `hook_plan` | regen | video |
| MR23 | Real point of conflict/action visible in the first second. | F102,D184,F99,D181 | 2026-10-21 1:29 AM | auto+manual `hook_plan` | regen | video |
| MR24 | 3-2-1 spec: covered product cue at 0 s, everyone counts together, 'let's see how it comes out' on the reveal, split-second (<=0.5 s) reveal, full product saved for the afters, count voices ~+8 LU over the song. | F105,D187,F83,F82 | 2026-10-21 1:33 AM | auto+manual `count321` | regen | video |
| MR25 | Song starts at frame 0 (no silent lead-in) and plays continuously: no loops, no splices (audio fingerprint vs the reference song). | F37,D66,memory | 2026-10-19 | auto `song_continuity` | free:recompose | video |
| MR26 | Recreations use the competitor's exact song AND section (verified fingerprint in refs/<slug>/songs_verified.json). | F108,D190,F77 | 2026-10-21 5:09 PM | auto `recreation_song` | free:recompose | video |
| MR27 | No phonk / slowed+reverb; proven song section people actually use. | F40,F70,F76 | 2026-10-19 | auto `no_phonk` | free:recompose | video |
| MR28 | Real ambient clip audio only, never fake SFX; voices audible over the song. | F05,F40,F52,F82 | 2026-10-03..10-19 | manual | free:recompose | video |
| MR29 | Straight hard cuts only: no fades, no jump cut inside one take, no lingering boring shot. | F08,F56,F62,F63,F85 | 2026-10-07..10-19 | manual | free:recompose | video |
| MR30 | The payoff/after is >= 2 hard cuts (3+ shots), no payoff shot > 1.5 s, never one cinematic shot. | F103,D185 | 2026-10-21 1:29 AM | auto `payoff_cuts` | regen | video |
| MR31 | ONE on-screen card by default; a 2nd only for a problem-vs-solution / then-vs-now hook or a closing 'get it from the caption below 👇' card; 3 cards ONLY for the MR52 idea / VS / result structure (VS on the middle card); never 4+. | F106,D188,memory | 2026-10-21 4:21 PM | auto `card_count` | free:recompose | video |
| MR32 | Every card is <= 8 words. | D67,memory | 2026-10-19 | auto `card_words` | free:recompose | video |
| MR33 | 'VS' only ever on the middle card, never on the first card. | F64,memory | 2026-10-19 | auto `vs_position` | free:recompose | video |
| MR34 | No 'Get yours' and no URL on screen or in captions. | F45,F91,memory | 2026-10-19 | auto `no_get_yours` | free:recompose | all |
| MR35 | Card emojis are Apple iOS (Apple Color Emoji) art, pixel-verified against textcards. | F107,D189,F40,F54,D61 | 2026-10-21 5:09 PM | auto `apple_emoji` | free:recompose | video |
| MR36 | Every card is visible from its shot's first frame (starts on a cut +-1 frame, >= 1 s, readable contrast on the render). | F100,D182 | 2026-10-21 1:29 AM | auto `card_timing` | free:recompose | video |
| MR37 | Card copy makes literal logical sense for what is on screen. | F101,D183 | 2026-10-21 1:29 AM | manual | free:recompose | video |
| MR38 | Cards never cover a face. | memory 2026-10-21 (own commitment) | 2026-10-21 | auto `cards_off_faces` | free:recompose | video |
| MR39 | Rendered card text matches the approved card copy (OCR) and fits in <= 2 rows. | F53,memory 'check every card vs spec' | 2026-10-21 | auto `card_ocr` | free:recompose | video |
| MR40 | FB/IG captions use SAY "<KEYWORD>", never 'Comment'. | F93,D148 | 2026-10-20 9:47 AM | auto `caption_say` | free:caption | publish |
| MR41 | Before publish the exact caption equals the approved caption and every card equals the approved card spec. | memory 2026-10-21 | 2026-10-21 | auto `caption_approved` | free:caption | publish |
| MR42 | No caption line repeats a line already posted on that page. | memory 2026-10-21,F22 | 2026-10-21 | auto `caption_fresh` | free:caption | publish |
| MR43 | Caption is a proven hook-style caption (not a store listing title); no engagement-bait questions. | F78,F67,D138 | 2026-10-19 | auto `caption_style` | free:caption | publish |
| MR44 | Nothing is posted without Omar's approval or explicit ask for that post. | security,D78 | standing | auto `publish_approval` | none | publish |
| MR45 | Caption swap only at 40K views or 10K+ within an hour. | memory,D93 | 2026-10-20 | process | none | publish |
| MR46 | Superseded Drive versions get trashed after a new version ships. | F60,memory | 2026-10-19 | process | none | all |
| MR47 | Every Omar fix becomes a permanent rule in this file plus an automated check or required review item. | F66,memory 2026-10-21 | 2026-10-21 | auto `rules_registry` | none | all |
| MR48 | Never burn in captions (F04) - SUPERSEDED: on-screen cards are now required (D188); post captions live in the FB caption. | F04 | 2026-10-08 | superseded | none | video |
| MR49 | Glow trail / motion blur behind lights is EXTREMELY minimal, close to none: no streaks behind the horse at all, only the bright glow on the product itself (white-hot cores + halo/bloom). Post trail pass: lagfun decay <= 0.3 and trail opacity <= 0.03 (default 0 = no trail pass); prompts must say 'no light trails, no motion streaks, no long-exposure effect' and never ask for trails; any clip with visible streaks is rejected. | Omar 2026-10-21 8:14 PM (LR1/LR2 trails way too much); tightened Omar 2026-10-22 10:37 AM (frame with long leg streaks: ~3% or zero) | 2026-10-22 10:37 AM | auto+manual `glow_trail` | regen | video |
| MR50 | Problem-vs-solution card pairs use 'The solution' as the second card, never 'The result' ('The problem' -> 'The solution'). | Omar 2026-10-21 8:50 PM (PV4 feedback) | 2026-10-21 8:50 PM | auto `problem_solution` | free:recompose | video |
| MR51 | No illogical settings for the product: every scene is a place the product/subject would actually be. PurrVentures: the cat never appears in a store or garden center - use yards, parks, patios and similar. | Omar 2026-10-21 8:50 PM (PV4 cat-in-store) | 2026-10-21 8:50 PM | manual | regen | video |
| MR52 | VS / idea-vs-result videos have 3 parts in order: (1) HOOK = the problem, only the makeshift janky version (duct tape etc.); (2) VS = a separate segment right after the hook showing the product being ASSEMBLED / put on the horse, the VS card starts here; (3) RESULT = the afters, riding with the bright glow, >= 2 hard cuts. Never skip the VS assembly segment. Spec shots carry role hook/vs/after. | Omar 2026-10-22 10:38 AM | 2026-10-22 10:38 AM | auto `vs_structure` | regen | video |
| MR53 | Barn Glow / LumaRein afters ALWAYS include multiple glowing horses: at least one after shot with 2+ horses wearing the product (spec shots[].horses, confirmed on the render). | Omar 2026-10-22 11:43 AM PT (LR4 had only single-horse afters) | 2026-10-22 11:43 AM | auto+manual `multi_horse` | regen | video |
| MR54 | Assembly / VS segments are never rushed: the product assembly reads clearly, >= 2.0 s on screen and >= the reference's assembly length (spec.reference.assembly_s) when recreating. | Omar 2026-10-22 11:43 AM PT | 2026-10-22 11:43 AM | auto `vs_duration` | regen | video |
| MR55 | The song's beat drop lands exactly on the first frame of the afters (+-0.1 s): drop detected by onset/energy analysis of the used song section; align song in_s (or the cut) so the drop hits the after cut. | Omar 2026-10-22 11:43 AM PT | 2026-10-22 11:43 AM | auto `drop_on_after` | recompose | video |
| MR56 | Barn Glow afters = EXACTLY three back-to-back cinematic cuts of the glowing horses running, in relevant settings only (farm, barn in the background, occasionally a beach); never irrelevant places. With MR53, at least one of the three shows multiple horses. Spec after shots carry setting + action. | Omar 2026-10-22 11:44 AM PT | 2026-10-22 11:44 AM | auto+manual `afters_cinematic` | regen | video |
