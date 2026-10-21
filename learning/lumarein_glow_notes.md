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
