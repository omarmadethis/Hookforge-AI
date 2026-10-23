# LumaRein glow study (originals 2.6M / 383.5K; frames at 6.2-13.3 s)
- Ambient darkness: night shots are almost black (median V 24/255, mean 39). The horse body is a near-silhouette and the sky is deep navy. Only the LEDs carry light.
- LED cores: clipped white-hot cores (1.3-2.1% of pixels >240), with a saturated electric-blue / hot-pink halo around them (sat of bright px 160-195).
- Bloom: a wide soft halo of 2-4x the strap width, and the light spills onto the horse's coat and the ground (blue pool under the legs).
- Light trails: the tail strands smear into long streaks behind the horse (motion blur); leg bands leave short arcs; the camera's shutter drag is visible.
- Reflections: a mirror of each LED on wet sand, smeared vertically into long columns.
- Dusk shots (field): the lights still read as neon dots/streaks against dim grass; sky slightly bright.
- Switch-on: unlit grey strap → instant full neon with a halo, no fade.
Prompt block (every clip): "LEDs glowing extremely bright neon, white-hot cores with a thick saturated halo and bloom, light spilling onto the coat and ground, long motion-blur light trails from the tail and legs, slow-shutter streaks, very dark surroundings, wet-ground reflections"
Post: ffmpeg bloom (screen-blend gblur of a highlight key) + LED-only trails (lagfun on a highlight key) - free.

## UPDATE 2026-10-21 8:14 PM PT - Omar feedback (MR49): trails WAY too much in LR1/LR2
- The glow trail / motion blur behind the lights must be only slightly there - significantly more subtle, barely visible.
- KEEP the glow itself super bright and glowy (white-hot cores, saturated halo, bloom, light spill, reflections).
- New prompt block: "LEDs glowing extremely bright neon, white-hot cores with a thick saturated halo and bloom, light spilling onto the coat and ground, crisp lights with only a faint barely-visible trail, very dark surroundings, wet-ground reflections". NEVER "long motion-blur light trails" / "slow-shutter streaks".
- New post pass (tools/lumarein/build_lr3.py GLOW_SUBTLE): bloom unchanged; trail = lagfun decay 0.55, gblur 4, mixed at 12% opacity (was decay 0.90, gblur 14, 100% screen).
- Gate: master_gate c_glow_trail (decay <= 0.6, opacity <= 0.15, no long-trail prompt wording) + manual reviewer confirm.
- The "Light trails" bullet above is SUPERSEDED.

## UPDATE 2026-10-22 6:55 PM PT - Omar's afters reference (MR57), ref/afters_ref_pov.mp4 (14.37 s, 1080x1920)
Reference afters (cuts found by frame-diff scene detection): beach side tracking 8.07-10.0 s, rider POV 10.0-11.9 s, two-horse high tracking 11.9-14.4 s (the reference holds each ~2 s; our MR30 caps payoff shots at 1.5 s, so we use 1.5 s each).
1. Side tracking: glowing rider galloping on a night beach, wet-sand reflections, camera moving very fast to keep pace (keep).
2. Rider POV (the favourite, ALWAYS include): horse neck, mane and ears stretch forward over a dark rolling field at night, glowing collar strap, aggressive handheld shake, extreme forward speed, edge blur, no hands or reins, another glowing rider ahead.
3. Two horses (blue + green) side by side, high tracking angle across a twilight countryside (keep).
Speed rule: afters must never feel slow or floaty. Prompts use FAST words (fast, very fast, flat out, aggressive, sprint) and never slow/floaty/gentle/calm/trot/canter/walk words; reject slow-motion-looking or stiff clips and regenerate.
Gate (master_gate.c_afters_style, MR57): shot styles in order side_tracking, rider_pov, high_two_horse; each after shot carries `prompt`; rider_pov carries pov={hands:0,reins:False,lead_rider:True,collar_glow:True,edge_blur:True}; high_two_horse has horses=2, colors [blue, green]; render speed (mean abs frame diff @15 fps, 90x160 gray) must reach side 4.0 / POV 6.5 / two-horse 3.2 (about 75% of the reference's 5.5 / 8.6 / 4.3; LR6 measured 4.7 / 7.5 / 6.0). Manual sign-off still required.
Templates: tools/lumarein/barnglow_afters.py (prompts + after shots; swap only rider/horse/colour/setting) and tools/lumarein/make_spec_barnglow.py (generic spec maker using it). make_spec_lr6.py is frozen (LR6 posted, not rebuilt; re-gating LR6 now would fail MR57 because its afters predate the rule).

## UPDATE 2026-10-22 7:00 PM PT - MR58 genuine handheld iPhone look (extends MR57)
- Every Barn Glow clip (hook, VS assembly, body, afters) must read as real handheld iPhone footage: vertical, slight natural shake, phone-sensor noise/grain in low light, slightly imperfect autofocus and exposure, normal phone dynamic range and sharpening, real-world lighting, natural skin texture, LED glow as a phone camera really records it. No cinematic/polished AI sheen, plastic skin, perfectly smooth gimbal motion, or glossy 3D-render glow. Reject any clip that looks AI-generated and regenerate.
- Prompt language (tools/lumarein/barnglow_afters.py `PHONE`, `phone_prompt()` for video, `phone_still()` for gpt_image_2 frames): "shot on iPhone, handheld, real phone video, authentic, unedited look, ..." in EVERY prompt, plus the MR49 no-trails suffix. Banned words (gate PHONE_BAN): cinematic, filmic, gimbal, smooth, polished, glossy, 3D, render, studio, hyperreal, ultra HD/sharp/clean, 4K/8K, perfect, CGI, movie, drone shot.
- Gate (master_gate.c_phone_look, MR58): spec.phone_look flags all true, every shot has shots[].prompt, every shot/frame/spec prompt has the phone-video language and none has banned wording; plus a reviewer sign-off that each clip looks like real phone footage. make_spec_barnglow.py now takes pre_prompts (hook/assembly/body scene text) and frame_prompts and appends the suffixes.
- Conflict flagged: the generic IPHONE12_SUFFIX (D32) says 'not grainy or sharp, nothing cinematic, 4K'; for Barn Glow MR58 (newer) wants real sensor noise/grain. The Barn Glow suffix replaces that tail (iPhone wording kept so MR10 passes). MR12 still forbids adding grain/sharpening in OUR post grade.
