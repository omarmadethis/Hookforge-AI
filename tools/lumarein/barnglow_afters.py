"""Barn Glow AFTERS template (MR53/MR55/MR56/MR57, Omar 2026-10-22 6:55 PM PT; reference ref/afters_ref_pov.mp4).

Exactly 3 FAST, realistic-feeling cuts, always in this order:
  1 side_tracking   side tracking shot of a glowing rider galloping on a beach at night, camera moving very fast to keep pace
  2 rider_pov       FIRST-PERSON rider POV gallop (horse neck/mane/ears forward over a dark rolling field at night, glowing collar,
                    aggressive handheld shake, extreme forward speed, edge blur, NO hands/reins, glowing rider ahead) - ALWAYS included
  3 high_two_horse  2 horses side by side (blue + green), high tracking angle over a twilight countryside
Swap ONLY the characters, colours and settings (arguments below). Never slow/floaty: every prompt carries FAST words, none carries SLOW words
(master_gate.AFTER_FAST / AFTER_SLOW), the render must reach master_gate.AFTER_MOTION_FLOOR, slow-motion-looking or stiff clips are rejected
and regenerated. MR49: near-zero light trails (NT suffix) with bright bloom. MR10: iPhone realism suffix ends every prompt.

Usage (spec makers):  from barnglow_afters import after_shots, after_prompts
  shots = after_shots(t0s=[8.85, 10.35, 11.85], t1_end=13.35, gens=["X_A1a","X_A1b","X_A2a"], settings=dict(side="beach", pov="dark rolling field", two="twilight countryside"))
  prompts for the generator: after_prompts(rider="woman in a black riding helmet", horse1="bay horse", glow1="electric blue", ...)
"""
NT = "no light trails, no motion streaks, no long-exposure effect"
# MR58 (Omar 10-22 7:00 PM PT): every Barn Glow video AND still prompt carries this; never cinematic / gimbal / polished / glossy / 3D words (gate PHONE_BAN).
PHONE = ("shot on iPhone, handheld, real phone video, authentic, unedited look, slight natural handheld shake, real phone-sensor noise and grain in low light, "
         "slightly imperfect autofocus and exposure, normal phone dynamic range and sharpening, real-world lighting, natural skin texture, LED glow as a phone camera really records it")
SUFFIX = PHONE + ", " + NT
STILL_PHONE = ("shot on iPhone, handheld, real phone photo, authentic, unedited look, real phone-sensor noise in low light, slightly imperfect exposure, "
               "real-world lighting, natural skin texture, normal phone sharpening")
def phone_prompt(text):
    """Video prompt for ANY Barn Glow shot (hook / assembly / body / afters): text + MR58 phone-video suffix + MR49 no-trails suffix."""
    return text.rstrip(" .,") + ", " + SUFFIX
def phone_still(text):
    """Start-frame (gpt_image_2) prompt: text + MR58 phone-photo suffix."""
    return text.rstrip(" .,") + ", " + STILL_PHONE
ORDER = ("side_tracking", "rider_pov", "high_two_horse")

def after_prompts(rider="a rider in a black riding helmet", horse1="bay horse", glow1="electric blue", horse2="grey horse", glow2="neon green",
                  beach="beach at night, wet sand reflecting the lights", field="dark rolling field at night", country="twilight countryside with green hills and fences"):
    """Three seedance prompts (one per after style). Characters / colours / settings are the only free parameters."""
    side = (f"Side tracking shot of {rider} on a {horse1} galloping flat out along a {beach}, glowing {glow1} LED kit on the horse and rider with bright bloom, "
            f"the handheld iPhone camera moves very fast sideways to keep pace with the horse, aggressive fast camera motion, hooves pounding, sand flying, "
            f"fast real-time full gallop speed, {SUFFIX}")
    pov = (f"First-person rider POV gallop at extreme forward speed: the {horse1}'s neck, mane and ears stretch forward over a {field}, "
           f"a bright glowing {glow1} collar strap on its neck, aggressive handheld camera shake, very fast forward motion, strong edge blur and speed blur at the frame edges, "
           f"no hands and no reins in frame, another glowing rider galloping ahead in the distance, fast sprint, bright bloom on the lights, {SUFFIX}")
    two = (f"High angle tracking shot over a {country} at twilight, two horses galloping fast side by side, one {glow1} and one {glow2} glowing LED kit with bright bloom, "
           f"the handheld camera tracks very fast and aggressively above and beside them, fast full gallop, fast real-time speed, {SUFFIX}")
    return dict(zip(ORDER, (side, pov, two)))

def after_shots(t0s, t1_end, gens, settings=None, prompts=None, **swap):
    """Spec shots[] for the 3 afters (role=after) carrying the MR53/56/57 fields. t0s = 3 cut start times, t1_end = video end."""
    st = dict(side="beach", pov="dark rolling field", two="twilight countryside"); st.update(settings or {})
    pr = prompts or after_prompts(**swap); t1s = list(t0s[1:]) + [t1_end]
    glow1 = swap.get("glow1", "blue").split()[-1]; glow2 = swap.get("glow2", "green").split()[-1]
    base = [dict(style="side_tracking", horses=1, setting=st["side"], action="galloping"),
            dict(style="rider_pov", horses=1, setting=st["pov"], action="galloping", pov=dict(hands=0, reins=False, lead_rider=True, collar_glow=True, edge_blur=True)),
            dict(style="high_two_horse", horses=2, colors=["blue", "green"], setting=st["two"], action="galloping")]
    return [dict(gen=gens[i], t0=t0s[i], t1=t1s[i], role="after", prompt=pr[b["style"]], **b) for i, b in enumerate(base)]
