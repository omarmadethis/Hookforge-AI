# TrumpGlow / PatriotGlow research (2026-10-19, no generation, 0 credits)

## How the product works
- **Wireless stick-on puddle projector**, the dominant dropship SKU. It's a small square pod, often in carbon-fibre look, about 6.5×6.8×2.5 cm.
  - Stuck to the bottom of the inner door panel with 3M tape. No drilling.
  - Powered by 3×AAA batteries or a USB-C rechargeable cell.
  - A magnet goes on the door sill. A Hall sensor turns the light on when the door opens more than ~2 cm, and auto-off is usually after about 2 minutes. Newer units use a proximity sensor with no magnet.
  - The image comes from a tiny film or glass "gobo" chip lit by an LED. It throws a round image, about 40–60 cm across, onto the ground under the door.
- **Wired OEM-replacement versions** plug into factory puddle-light sockets (BMW, VW, Ford, Lexus). They're brighter and permanent.
- **Film vs HD glass:** cheap plastic film fades or blurs within months. This is the classic Reddit complaint ("blurry as hell in a couple months"). "HD / never-fade laser-etched glass" is the upsell claim.
- **Image quality:** colour photos project fine, but soft at the edges with a vignette. That's fine for a cartoon badge like Omar's decal.
- **In the box:** 2 projectors (driver plus passenger), 2 magnets, 3M pads. Batteries are often NOT included.
- **Price:** around $10–25 per pair on Amazon. Custom-photo DTC brands (Lumi Door, Getledsy, door.light.us) sell for about $30–50. AliExpress wholesale is a few dollars per unit.
- **Top complaints:** adhesive or magnet falls off, the sensor won't trigger so it's button-only, batteries drain or leak, the image is dim, fading, and the magnets were sometimes missing from the box. Product only; don't put any of this in the ad.
- **Variants:**
  - Brand logos (BMW, Audi, NFL teams).
  - Characters (Hello Kitty and Kuromi via Sanrio-style sellers, Iron Man, anime).
  - Meme text (TAKOJII "6 7").
  - Custom photos: girlfriend's face, pets. These are the biggest viral driver.

## Top reference videos
All are downloaded to /workspace/hookforge/refs/trumpglow/, with keyframes in kf/ and contact sheets in sheet_*.jpg. Full detail is in refs.csv.
1. Lumi Door, "His last day with us.. VS... ❤️ → his first day", **2.4M views / 115K likes**, 10 s.
2. Lumi Door, "POV: ur wife got this… so you don't cheat 😂🤝", **1.2M views / 47K likes**, 9 s. Shows the 3M pod, the film chip, the stick-on install, the handle pull and the face on the pavement.
3. Getledsy sill-plate trio, ~200K each. This is an adjacent product (a lit name sill plate, not a projector), but it uses the same night door-open grammar.
4. YouTube: the NFL logo Short (202K) and a BMW install tutorial (922K, a long-form tutorial).
5. Omar's Hello Kitty reference and his own TrumpGlow draft. These are the **anchor grammar**.

## Winning shot grammar
Shared across the 1M+ winners and Omar's Hello Kitty reference, total 8–12 s:
1. **Problem/contrast (0–3 s):** a daytime "fake" version. A paper cutout taped to the asphalt or door with a disapproving gesture, or an emotional "before" shot. One card on it.
2. **"Vs..." beat:** a close-up of the hand peeling the 3M backing off the pod (optionally holding up the tiny film chip), then pressing it onto the inner door panel. This is the logic and credibility shot.
3. **Night trigger:** a POV hand pulls the door handle. The door swings open.
4. **Reveal:** the camera tilts down and the round projection lands on the pavement, then a slow push-in or zoom. The payoff hits at 5–7 s and gets held.
5. Optional second after: the passenger side, or a wider car-in-lot shot with both doors lit. It must move differently from the first after.

The cards are always two-part ("X.. VS... → Y"), with emoji, top-centre and white-box style. The audio is a trending song or phonk. There's no voice-over on the viral ones.

## Recommended concepts
Every character or face is replaced with Omar's decal, `assets/patriotglow/product/3715deca-…png`. Use the American Pride Trump badge for the cutout AND the projection.

**A. "Fake fans" recreate (primary, 1:1 with the Hello Kitty ref):**
- Shot 1, daylight: hands cut a paper Trump-badge with scissors, tape it under the open door on the asphalt, step back and wag a finger. Card: "Fake Trump Fans.. 🤢👎".
- Shot 2: peel 3M, stick the black carbon pod to the inner panel. Card: "Vs...".
- Shot 3, night: the hand opens the door, the camera tilts down to the glowing badge on the pavement and pushes in.
- Shot 4: a wide shot of the truck with both doors open and two badges, with a slow orbit.
- Card on shots 3–4: "What We ACTUALLY Sell... 😎🇺🇸".
- Song: Southern rock (Omar's Free Bird vibe) or phonk.

**B. Omar's own draft, fixed:**
- Same beats as his clip ("What people THINK we sell..." → "VS...⏳" → "the projector we ACTUALLY made 😎🇺🇸").
- Gimbal-smooth moves and hard cuts. No smoke transition.

**C. POV joke (Lumi 1.2M format):**
- Card: "POV: your buddy found out you're a liberal 😂🇺🇸".
- Shots: 3M pod → chip → stick on → handle pull → badge on the ground.
- This is the 20% innovation slot.

## Hookforge rules applied in the plans
- **Logic step in every shot:** cutting, taping, peeling, pulling the handle. Nobody looks at the camera.
- **Captions:** one problem caption → "Vs..." → the solution card.
- **Emoji:** Apple iOS emoji PNGs only.
- **CapCut text:** first preset, stroke 45.
- **Audio:** generated audio is muted; the song is the only sound.
- **Afters:** two different moves, a push-in and an orbit.
- **Metadata:** C2PA is stripped on export.

## Omar's existing material
- `/workspace/library/Ecomstein/PatriotGlow/`:
  - trump light 1st.mov
  - 2nd light trump.mov
  - light vid.mov
- Mac finals:
  - trumpy.mp4 (proxy `team/mac/proxies/prox/0503.m4v`)
  - businessman-decal-final.mp4 (`0814.m4v`)
- Review sheets: `assets/patriotglow/other/`. These contain Real Madrid IP, so use them for reference only.
