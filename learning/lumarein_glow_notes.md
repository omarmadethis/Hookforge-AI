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
