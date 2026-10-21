# Visual US / tier-1 cues for start frames and Seedance prompts
Status: every cue's **geo effect is a hypothesis** (Meta documents visual similarity as a signal, not "US objects attract US viewers"). US flags are already mandatory (D24). Test the rest in EXP-AUD-07.

## Rules that still apply (do not break them)
- The snippet goes **inside the scene description**, BEFORE the suffix. The prompt still ends with the verbatim iPhone 12 suffix (`config.IPHONE12_SUFFIX`, D32); stills use `config.still_prompt(scene)` + suffix. Never put a cue after the suffix.
- **Subtle**: cues are background set dressing, never the subject. Max 2 cues per shot + the flag. Product world first (D37): Brick Hood = ski slope, never a store; GrinchMelt = calm home; MerryFire = backyard/patio.
- Stores look like Target (red) / Walmart (blue) with **no logos** (D26). Store names only in the text overlay + JK flip (D4).
- **No race/ethnicity casting** (D27, `config.sanitize_casting`). "American" is expressed through setting, wardrobe, props and behaviour, never skin tone or ethnicity.
- No real person's likeness (no "looks like <influencer>"). Photorealistic AI people may need Meta's AI label: follow the platform's AI-disclosure prompt when it appears.
- Minor artifacts in cues (odd signage text, a wrong outlet) never trigger a re-roll (D33).

## Snippet library (copy into the scene text; `{…}` = slot)
### Flags (mandatory, D24)
- `a small American flag on a wooden pole by the front door in the background`
- `an American flag hanging from the porch column, gently moving in the wind, in the background`
- `a small desk American flag on a shelf in the background` (indoor)
- Ski (Brick Hood): `an American flag on the ski lodge flagpole in the far background` / `small American flag sticker on a snowboard in the background`

### Suburban US homes (relatable, R25)
- `a typical American suburban two-story house with vinyl siding, a front porch, a two-car garage and a lawn`
- `a cul-de-sac with neighbors' houses decorated with Christmas lights in the background`
- `an open-plan American kitchen with a large stainless-steel French-door fridge, an island with bar stools and white shaker cabinets`
- `a living room with a sectional couch, a big flat-screen TV, a fireplace mantel with stockings`
- `a backyard patio with a gas grill, Adirondack chairs and a wooden privacy fence` (MerryFire)
- `a mailbox on a post at the end of the driveway` · `a basketball hoop above the garage`

### US infrastructure & units (tiny details; strongest "this is the US" signals)
- `a US-style wall outlet (two vertical slots and a round ground hole)`
- `a car in the driveway with a rectangular US license plate (blurred, unreadable)`
- `a yellow school bus passing in the far background` (daytime outdoor)
- `a thermostat on the wall showing 68°F` · `a measuring tape showing inches`
- `a red plastic Solo cup on the counter` · `a Costco-size pack of paper towels in the corner` (no logos)

### US retail look (store-format hooks only; D26)
- `a big-box store aisle with red shelving and red price signs, wide polished concrete floors, red shopping carts, no logos` (Target look)
- `a big-box store aisle with blue signage, tall warehouse shelving, no logos` (Walmart look)
- `a warehouse club with pallets stacked to the ceiling, flatbed carts, no logos` (Costco look)

### US seasonal calendar (Q4)
- Thanksgiving week (Nov 19–29 2026): `a Thanksgiving table with a roast turkey, pumpkin pie and fall leaves centerpiece in the background`, `a 'Happy Thanksgiving' banner` · `a football game on the TV in the background`
- Halloween→Christmas switch (Nov 1): `a carved pumpkin on the porch next to a newly set-up Christmas wreath`
- Christmas: `oversized inflatable yard decorations and a lit-up front lawn`, `stockings on the mantel`, `an ugly-Christmas-sweater party`, `milk and cookies for Santa on the counter`
- Snow cues are fine for US/CA/UK/DE; avoid for AU/NZ variants (summer Christmas).

### Presenter (only in the presenter arms of EXP-AUD-04; D27 applies)
- `a {woman|man} in their {30s} with a friendly, casual, talk-to-camera vibe, wearing {a college hoodie | leggings and a puffer vest | a flannel shirt and a baseball cap}, filming themselves on an iPhone in their kitchen` (no ethnicity, no real-person likeness)
- Audio for presenter shots: native ambient only (D23), no speech generated unless the format needs it; if speech, `speaking casual American English`.

## Avoid (non-target or other-region signals)
- UK/EU plug sockets, right-hand-drive cars, € / £ price tags, °C thermostats, metric tape measures on US-primary variants.
- Terraced UK houses, tropical palms with Christmas lights (reads LatAm/SE Asia/AU), tuk-tuks, scooters-heavy street scenes.
- Spanish/Portuguese signage text.

## Example (start frame, GrinchMelt, calm home)
```
iPhone photo of a cozy American kitchen at night: a woman's hands holding a green Grinch melting mug on a white shaker-cabinet island, stockings on the mantel and a small American flag on a shelf in the background, a US-style wall outlet behind the mug warmer. Sharp, clean, realistic phone photo. shot on iphone 12, no warm lighting, no blur, nothing cinematic, make it look as organic as possible, remove the caption and the emojis. when recreating do not make the video grainy or sharp in any way, remake it as if it was freshly refilmed 4k iphone 12 footage.
```
(The suffix is appended by `config.ensure_suffix`; it is shown here only to make the order explicit.)
