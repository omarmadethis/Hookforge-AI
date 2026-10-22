# OMAR FEEDBACK LOG
Every fix or critique Omar has given (all products, all time) → rule → enforcement. Times PT. Merge-append only; never delete rows (supersede instead).
Sources: rules_core.csv (R01–R30, Mac chat history), DECISIONS.md (D1–D75, D-NOLOOP, D-NOSPLICE, D44b–d), failure_memory.csv, PLAYBOOK.md, parent chat transcript (t206–t223).
Enforcement key: gates.py G1–G19 (`gates.run_all`), qa.final_checks gates, speech_gates SG1/SG2, prompts.lint, config.*, or `manual`.

| # | Date | Omar (quote/paraphrase) | Product | Rule | Enforcement |
|---|---|---|---|---|---|
| F01 | 2026-10-01 | "the start frames are everything… if it looks like AI slop… shadow ban" | all | Start frames are the #1 quality lever; look like a genuine iPhone photo | G8 (Omar approves frames before any video) + manual |
| F02 | 2026-09-27→10-18 | "shot on iphone… no blur, nothing cinematic, no warm lighting… remember this forever"; start frames keep it too | all | iPhone 12 realism suffix on EVERY prompt (video + stills) | config.ensure_suffix + QA rejects missing suffix (D32/D35) |
| F03 | 2026-10-04 | "US flags in the background of every single clip" | all | US flag in every clip | prompts.with_flag + prompts.lint "no US flag" |
| F04 | 2026-10-08 | "NEVER BURN IN CAPTIONS" | all | No burned captions/music in generations | qa.raw_gen_checks OCR burned-text check (D43) |
| F05 | 2026-10-03 | "i already told you to always generate audio"; keep natural clip sound (real voices, cheering, gasps, environment), never fake/weird SFX | all | Native ambient audio on every gen, no music, no fake SFX | prompt builder; G6 fake-SFX BLOCK |
| F06 | 2026-09-24 | Ad Multiplier variants get own fresh audio (shadowban) | variants | Never reuse original track on variants | manual (variants.py fresh gen) |
| F07 | 2026-10-07 | "combine clips… same prompt" | all | Pack 2 shots per 4 s gen | planner (D20) + qa.packed_cut_check |
| F08 | 2026-10-07 | "straight cuts no fades, different angles" | all | Hard cuts only, new angle each cut | omar_style.compare (no fades) + packed_cut_check |
| F09 | 2026-10-10 | "8 seconds? that can be done in 5 tops" | all | Every gen ≤5 s; hook ≤5 s; Omar-approved exceptions only (JollyGlow combo garage afters 6 s, D71) | **G18** + learning/approvals/long_gens.json; D35 hook>5s BLOCK |
| F10 | 2026-09-29 | "hook is seedance 2.5 1080p, rest 720p" | all | Only hook gens 1080p | G4 |
| F11 | 2026-10-06 | "no kling what so ever… seedance only"; t206 "seedance 2.5 is the best by a landslide", no model comparisons | all | Seedance 2.5 only | **G16 (new)** |
| F12 | 2026-10-09 | "only use gpt image 2" | all | GPT Image 2.0 only for stills | **G16 (new)** |
| F13 | 2026-09-29 | "we dont need end frames ever" | all | No end frames, ever (RESOLVED 2026-10-19: rule stands; the TrumpGlow A end_image fix in failure_memory is retired) | **G16** |
| F14 | 2026-09-28 / 10-18 | no regen without permission; later: auto re-roll only on absurd failure ≥0.9, max 1 | all | Re-roll policy D33 | qa.reroll_decision |
| F15 | 2026-10-03 | "always list cost"; budgets 150/175/100 variants; JollyGlow cap 400 | all | Cost listed per output; stay under budget (default 200) | G5 quote + **G17 (new)** |
| F16 | 2026-10-08 | active working product on top of any display | all | Top unit lit | manual (prompt rule D24) |
| F17 | 2026-10-08 | time of day must make sense chronologically | all | Time progresses | qa.logic_check / manual |
| F18 | 2026-10-06 | "shocked the whole time… slow and robotic" | all | Natural motion, no permanent shock face | G13 motion + ai_look + manual |
| F19 | 2026-10-10 | FaceTime whip + whoosh unnatural; real FaceTime UI | FaceTime fmt | No whip/whoosh | G6 fake-SFX BLOCK + manual |
| F20 | 2026-10-09 | "just look like a target" | store hooks | Store look-alike, no logos | manual (D12/D26) |
| F21 | 2026-10-13 | "ad multiplier… the whole fucking video"; Christmas bg adjustments | variants | Ad Multiplier = remake whole video | manual (D21) |
| F22 | 2026-09-28 | variants changed enough to re-upload from another page | variants | ≥4 of 7 axes changed | variants.py + qa.originality_gate |
| F23 | 2026-10-03 | thoroughly listen and watch references | all | Watch+listen fully before working | manual |
| F24 | 2026-10-07 | gasoline pour + ignition before snacks | MerryFire | Build order | qa.logic_check / manual |
| F25 | 2026-10-08 | "relatable… patio/backyard of a home" | all | Relatable homes, no nonsense props | logic_check world anchors / manual |
| F26 | 2026-10-09 | hook needs wow factor; stand out from slop | all | Wow-factor hooks | manual (G7 POC) |
| F27 | 2026-10-05 | "these are all organic videos, i dont even do ads" | all | Organic posts framing | manual |
| F28 | 2026-10-08 | captions from the Caption Bank | all | Proven caption patterns | G7 POC citation |
| F29 | 2026-09-29 | gondola hook = first-person POV | BrickHood | POV unboxing hook | manual (worlds.py) |
| F30 | 2026-10-08 | lights in start frame before unfold, reproduced correctly | JollyGlow/all | Hero prop matches reference | CLIP fidelity (rank-only) + manual |
| F31 | 2026-10-18 | race-based casting excluded | all | No race/ethnicity casting | config.sanitize_casting + QA casting_violations + prompts.lint |
| F32 | 2026-10-18 | JK flip on fake-store hooks | store hooks | "JK, we make them" flip | manual |
| F33 | 2026-10-18 | 20 % innovation; t214 test new concepts from POC on own (core rule) | all | ≥1 experiment slot; every concept cites POC | planner D16 + G7 |
| F34 | 2026-10-18 8:32 PM | recency only for external reels | research | RECENCY on external only | config.RECENCY |
| F35 | 2026-10-18 9:39 PM; 2026-10-19 (t211, t218) | "there should never ever be a trace ever"; anything generated, images included, gets AI metadata stripped | all | Strip C2PA/AI/encoder/codec traces from every delivered file (video + image) | qa.final_checks metadata BLOCK + deliver.py chokepoint (D44–D44d) |
| F36 | 2026-10-18 9:48/9:50 PM | drop voice-layer suggestions except AI-doubt proof; drop safety holds | all | PROOF shot per video only | QA FIX on missing PROOF (D49/D50/D51) |
| F37 | 2026-10-19 | v3 AC/DC silent lead-in; song from frame 0 | all | Song starts at t=0 at proven in-point | G1 + songlay.song_start_check |
| F38 | 2026-10-19 | B "POV…Thanksgiving" too long, not catchy | TrumpGlow | Hooks ≤8 words, proven formats | G2 |
| F39 | 2026-10-19 9:05 PM | store-aisle ban and 😳/🎅 block "stupid" | all | No ban against own proven data | G3 proof_guard |
| F40 | 2026-10-19 | no phonk; iOS emoji only; real ambient only | all | Bans | G6 |
| F41 | 2026-10-19 | show start frames first | all | Frames approved before video | G8 |
| F42 | 2026-10-19 | shared enterprise workspace; only our job ids | all | Spend from our ledger only | G5 our_spend |
| F43 | 2026-10-19 9:20 PM | staged scenes may look at camera; organic not | all | Gaze follows scene logic | G9 + logic LG1 |
| F44 | 2026-10-19 9:17 PM | JollyGlow cap 400; chain afters in one clip | JollyGlow | Chain 2–3 afters per clip | manual (planner) + G17 budget field |
| F45 | 2026-10-19 9:25 PM | no "Get yours"/URL on screen; comment CTA OK | all | Link in caption/bio only | G10 |
| F46 | 2026-10-19 | B 3M peel "way too slow, long and boring" | TrumpGlow | Opener/peel fast, ~2 s, speed up 1.5–2x (WINS over F49) ; PurrVenture backyard-cam opener ~4 s allowed (t219) | G11 (WARN) |
| F47 | 2026-10-19 | chip-glint showcase shot | TrumpGlow | Action over showcase | G12 |
| F48 | 2026-10-19 | (failure_memory) no cut between door opening and reveal | TrumpGlow | Reveal continuous from trigger | manual |
| F49 | 2026-10-19 | (failure_memory) peel too fast at 1.2x | TrumpGlow | SUPERSEDED by F46 (newer note wins: fast, ~2 s) | — |
| F50 | 2026-10-19 | "make editing on POINT, as good as me" | all | Edit within Omar CapCut ranges | omar_style.compare in qa.final_checks |
| F51 | 2026-10-19 | hook too long → speed up, never cut; never cut dialogue | all | Hook speed 1.0–1.5x; dialogue complete | omar_style hard miss + SG1 |
| F52 | 2026-10-19 | voices buried under song | JollyGlow | Speech ≥6 dB over music (+8 LU) | SG2 + omar_style |
| F53 | 2026-10-19 9:37 PM | captions max 2 rows; everyone counts together | all | ≤2 rows; countdown spoken by all groups | CAP2 caption_lines_gate + logic LG7 |
| F54 | 2026-10-19 | iOS emoji; CapCut preset size 15 stroke 0.09, y≈0.20 | all | Text style | omar_style.compare / plugins capcut_text_preset |
| F55 | 2026-10-19 | TrumpGlow A first close-up "repeats" | all | Never loop/repeat footage | qa.final_checks repeat_detect |
| F56 | 2026-10-19 | jump cut inside one take | all | No same-take splice | qa.final_checks splice_detect (needs timeline) |
| F57 | 2026-10-19 t206 | do it all yourself; realistic product shots, real footage reveals | all | Realism stack (refs, grade, simple motion, AI-look QA) | G13 + ai_look in final_checks |
| F58 | earlier (grade note) | "do not make the video grainy or sharp in any way" | all | iPhone grade subtle; off if Omar objects | manual (plan.grade) |
| F59 | 2026-10-19 | US market | all | US English/US cues | prompts US cues (D46); P-AUD-5 still PROPOSED → manual |
| F60 | 2026-10-19 t207/t208 | organize Drive per product, clear names; trash rejected old variants | all | Delivery layout + replace-not-stack | deliver.py/drive_layout.json + manual |
| F61 | 2026-10-19 t214/t217 | study competitor harder; get Instagram viewed; follow proof (~4 s opener for PurrVenture) | PurrVenture | Competitor proof drives format | G7 + manual |
| F62 | 2026-10-19 t220 | A ACDC weird cut still there after Free Bird was fixed | TrumpGlow | Same-take splice gate runs on EVERY song variant with its own timeline | qa.final_checks BLOCKs when no timeline is passed + qa.final_checks_variants() |
| F63 | 2026-10-19 t220 | clip "lingers wayyy too long for how uninteresting it is" | TrumpGlow/all | Non-key shots ≤~2.2 s (WARN >2.5, BLOCK >3.2) | **G15 (new)** |
| F64 | 2026-10-19 t220 | "Vs. part… should only come during the mid. never in the first" | all | Vs only in mid card | **G14 (new)** |
| F65 | 2026-10-19 t220 | pensive 😔 over 💔, pair with 🇺🇸 | TrumpGlow/all | Sad beat = 😔 + second emoji | **G19 (new, WARN)** |
| F66 | 2026-10-19 t221–223 | take note of every fix to improve Hookforge | all | Every fix → this log + gate/test | process (this file) |
| F67 | playbook | never engagement-bait questions or comfort adjectives | all | Caption bans | audience_fit caption score / manual |
| F68 | playbook | keep change list 1–2 items + "Remove the caption" in recreates | recreate | Recreate = 1–2 changes | recreate.check (D45) |
| F69 | playbook | product/lining colour and box brand never drift | all | Product consistency | CLIP fidelity + consistency line + manual |
| F70 | stored fact | song section must be the part people actually use | all | In-point = proven offset (own CapCut / verified ref), never an arbitrary section | G1 (in-point required) + G7 |
| F71 | stored fact | afters animated on the product and differ from each other | decor | Every after animates; no repeated after design | **G20 (new)** |
| F72 | stored fact | every element (song, start point, cards, shots) POC-backed; unproven excluded | all | No unproven element in core slots | G7 BLOCK + D38 (unproven = experiment slot only) |
| F73 | stored fact | core job: recreate slightly different originals of his winners shot for shot, not invent scenes | all | Recreate mode default, 1–2 changes, per-shot ref cites | recreate.check + G7 per-shot refs; manual |
| F74 | stored fact | every prompt needs a logic step (no family staring blankly at the camera) | all | Logic check per prompt | qa.logic_check + G9/LG1 |
| F75 | stored fact | one caption per problem scene, then "Vs...", then "Christmas 2026" on the afters | then-vs-now | Card order problem(s) → Vs → Christmas 2026 | **G21 (new)** + G14 |
| F76 | stored fact | song, emoji, caption matched to audience/niche; proven songs first, then trends | all | Niche/energy match; rank own proof > trend > other | D38 music + poc_library.rank_songs + audience_fit + G3 |
| F77 | stored fact | exact original song recording, never a substitute | all | Official recording verified xcorr ≥0.9 vs preview; no covers/remixes | G1 (verified) + fetch_song filters |
| F78 | stored fact | always send a proven-converting caption with each video | all | Post caption present, POC-cited | **G22 (new)** |
| F79 | stored fact | track posting-time patterns | all | Posting-time stats per page | learning/rules_learned.csv PT-*, posting_windows.json; manual |
| F80 | stored fact | prefer free tools | all | Free/open tools first | manual |
| F81 | 2026-10-19 | "the 2nd scene where he's just showcasing the pin… could've made it more engaging (toss it like a coin / put it on the device)" | TrumpGlow B | Product shots need action on the product, never just held up | G12 showcase (plan) + manual frame review |
| F82 | 2026-10-19 | voices audible under the music (countdown, crowd) | Jolly Glow | Dialogue sits about +8 LU over the song | songlay.lay_song(dialogue=…) + omar_style compare (D74) |
| F83 | 2026-10-19 | everyone in the shot says "3-2-1" together | Jolly Glow 3-2-1 | All on-screen people take part in the countdown | speech_gates SG1/SG2 + manual |
| F84 | 2026-10-19 23:22 | "the weird cut is STILL in the ACDC v6" | TrumpGlow A | Cause: G5 ended on a static logo close-up and the next shot (G3) opened on the same framing, so it read as the scene repeating. A cut must change framing, and song variants must share one identical video | qa.final_checks → pacing.near_duplicate_cuts (BLOCK) + qa.final_checks_variants → pacing.variants_identical |
| F85 | 2026-10-19 23:22 | "that clip now lingers way too long for how uninteresting it is" | TrumpGlow A | Non-reveal shots stay under Omar's p90 hold for their role (style.json timing.hold_p90_s: after 1.82 s, before 2.41 s, ending 3.5 s, opener 4.1 s). Only the reveal (or a proven shot) gets the long beat. Trim, or speed up to at most 1.5x; never loop | qa.final_checks → pacing.hold_violations (BLOCK) + G15 |
| F86 | 2026-10-19 23:30 | "😔 was a suggestion, not a hard rule" (correction to F-😔) | TrumpGlow C | Choose the sad/problem-card emoji by POC; pair it. C card 1 = "His last day on my truck.. ❤️🇺🇸", from POC-0255 (Lumi Door "His last day with us.. VS... ❤️", 2.4M, the reference C copies) | G19 POC check (WARN only, never forces 😔) + G14 (Vs never on card 1, BLOCK via qa.final_checks(card_texts=…)) |
| F87 | 2026-10-19 22:18 | "there should never ever be a trace ever" | all | Every file leaves the box only through deliver.stage() + verify_staged() (whitelist metadata + byte scan, no override) | deliver.py + qa.final_checks deliver scan (D44d) |
| F88 | 2026-10-20 9:17 AM | annoyed that PurrVenture v1 start frames were generated without references (ball shape + cat drifted in 7 of 12) | all | NO image or video generation without product AND cast reference images attached (Higgsfield media ids in medias); only exception is a shot whose prompt explicitly says "no product anywhere in frame" / "no people + no cat" | **HARD GATE** engine/hookforge/ref_gate.py, enforced in runner.build_calls/start_run/next_call (no override); test engine/tests/test_ref_gate.py; refs in refs/<product>/ + higgsfield_new_account_media_ids.json |
| F89 | 2026-10-20 9:17 AM | iPhone grade must show no visible grain or sharpening (restates F58) | all | Default grade = "light" (tone only: no noise, no unsharp, softer vignette) | iphone_grade.STRENGTH["light"] default |
| F90 | 2026-10-20 9:27 AM | "cat phasing through the ball" in 2 frames - "these should be caught before he sees anything" | all | Every frame passes a strict full-resolution self-QA before Omar sees it: physics (no clipping/phasing, cat fully inside the zipped ball or fully outside, nothing through the mesh, correct ground contact), cat = ref, product = ref, cast/outfit = ref, flag tiny, gaze, no AI tells. Max 2 regen attempts per frame within cap | **HARD GATE** engine/hookforge/frame_qa.py (record per-frame checklist + reasons; build_sheet refuses unless all pass, re-checks file hash); test engine/tests/test_frame_qa.py |
| F91 | 2026-10-20 (t233) | PurrVenture defaults kept picking Christmas songs / 'Get yours' / unproven emoji | PurrVenture | Per-product POC defaults: song by proof (Mambo No. 5 / Be My Baby), comment CTA 'Comment "PURR"', emoji from the competitor's proven cards | config/poc_defaults.json + product_poc.apply + audience-fit AF1/AF2/AF3 + G10/G19/G22 |
| F92 | 2026-10-20 9:17 AM (t230) | refs should have been loaded from the start | all | Every product has a ref library with manifest (product + cast) auto-attached to every plan | refs_lib.attach in planner.d75 + tests/test_ref_manifests.py + ref_gate (F88) |
| F93 | 2026-10-20 ~9:47 AM | FB captions use 'SAY ...', never 'Comment ...' | all | Every caption/card/hook variant uses SAY "<KEYWORD>"; 'Comment' is refused. PurrVenture caption = SAY "PURR" if you want one! 🐈 | **G23 (new, BLOCK)** gates.g23_say_not_comment + publish._caption_checks refusal + config.BANNED_CTA_WORDS; test tests/test_ref_manifests.py::test_g23_say_not_comment |
| F94 | 2026-10-20 ~9:50 AM | lock each product's cast from the avatars in its proven/top videos; default women, buyer logic wins (Trump/car/patriotic = man, cat = woman) | all | Cast per product locked in refs_lib.CAST + refs/<slug>/cast/cast_*_top.png (frames from the top own reel, caption band cropped, metadata stripped); PurrVenture cast switched to the woman | refs_lib.CAST + manifest.approved_cast + ref_gate (F88) needs a cast ref |
| F95 | 2026-10-20 ~9:47 AM | asked before for a clean TrumpGlow product photo | TrumpGlow | Product hero ref must exist for every product before generation (carbon-fiber projector, Trump/flag projection, rally background, no NFL logos) | refs/trumpglow/product/ + frame_qa.json + manifest |
| F96 | 2026-10-20 ~3:37 PM | brickhood, merryglow lights, merryfire, grinchmelt mug and minionmask are OLD/retired; keep all their cuts, tags/hashtags, captions, stats, sounds and hooks as full reference data for active products; no new content for them | 5 retired | **D117**: config/products.json `active` flag + hookforge/products.py; excluded from concept_lab/rank, e2e, Buffer routing (routing.route raises Retired) and missing-channel warnings; 7 queue items status RETIRED; corpus untouched; perf_feedback uses their stats as the pooled prior |
| F97 | 2026-10-20 ~4:09 PM | grinch_robe, heatjams and cozyjams are also retired; active = jollyglow_curtain, trumpglow, purrventure_carrier only; retired stay as full reference data | robe family | **D131**: products.json inactive; routing removed (merryjammies_ig_b2 idle); 3 queue items RETIRED → _archive; calendar cadence redistributed to the 5 remaining pages; heatjams URL question moot |
| F98 | 2026-10-20 7:42 PM | banned the lean reuse plan permanently; the 2 TrumpGlow videos (and every video) must be fully unique: own hook, own body clips, own setup and caption, zero shared footage | all | **D180** supersedes D142/D145: unique_footage.gate (plan BLOCK on shared gen/clip/start-frame or declared anchor) + render_check (BLOCK >2% measured shared frames); lean runner paths raise | **G-D180 (BLOCK)** |
| F99 | 2026-10-20 8:02 PM | F06 JollyGlow hook rejected: "nothing engaging happening, no point of conflict"; wants a much better hook like the proven JollyGlow hooks but more engaging; hooks are now 720p permanently | all | **D181**: config.HOOK_RES=720p (28 cr); hooks need real motion + clear conflict/tension in the first second; F06 hook redo cap 35 |
| F100 | 2026-10-21 1:29 AM | A2: "the 3rd card is invisible for the first few seconds" | TrumpGlow/all | **D182**: card starts on its shot's first frame, >=1 s, scale 1.0, render-checked 1 frame in | omar_gates_f100.card_timing + card_visible_render (BLOCK) |
| F101 | 2026-10-21 1:29 AM | A2: "fake trump fans vs what we actually sell isn't coherent" | TrumpGlow/all | **D183**: every card carries a literal-sense line tied to the shot | omar_gates_f100.card_coherence (BLOCK) |
| F102 | 2026-10-21 1:29 AM | B2: "opening hook is boring, no point of conflict" | TrumpGlow/all | **D184**: action + conflict by 1.0 s | omar_gates_f100.hook_gate (BLOCK) |
| F103 | 2026-10-21 1:29 AM | B2: "the final after is one single cinematic shot with no cuts" (liked the rest of B) | TrumpGlow/all | **D185**: payoff >= 2 hard cuts, each shot <= 1.5 s | omar_gates_f100.payoff_gate (BLOCK) |
| F104 | 2026-10-21 1:30 AM | every hook must be a proven POC format or a truly scroll-stopping, relevant moment; B2 -> 3-2-1 countdown like jollyglow_321 | all | **D186** | omar_gates_f100.hook_gate (BLOCK) |
| F105 | 2026-10-21 1:33 AM | 3-2-1 spec: covered cue at 0 s, everyone counts, 'let's see how it comes out', split-second reveal, full payoff in the afters, count ~+8 LU over the song from frame 0 | all | **D187** | omar_gates_f100.count321_gate (BLOCK) |

- 2026-10-21 02:27 PT run trumpglow_fix_A3B3: A3+B3 passed all gates, posted (B3 also to PatriotsGlow). D182 card_visible_render fixed to measure white fill vs background (old version averaged fill+black stroke and false-blocked readable cards). B3 3-2-1 reveal made in edit (0.3 s flash) because the generated clip never pulled the cloth.

| F106 | 2026-10-21 4:21 PM | ONE on-screen card per video; 2nd only for problem-vs-solution/then-vs-now or a closing 'get it from the caption below 👇' card; never 3+ | all | **D188** | card_count.gate / gates.g26_card_count / autoedit enforce (BLOCK) |
| F107 | 2026-10-21 5:09 PM | Card emojis must be Apple iOS (existing D61 was skipped in LR1/LR2) | all | **D189** | emoji_gate.render / gates.g28 / render-path test (BLOCK) |
| F108 | 2026-10-21 5:09 PM | Recreations use the original reel's exact song and section, frame 0, no loops | recreations | **D190** | original_song.gate / gates.g27 (BLOCK) |
