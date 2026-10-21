"""Reusable body blocks (720p, 2 shots per 4 s Seedance 2.5 generation, hard cut at 2 s).
Each block is grounded in measured winner bodies (team/body/REPORT.md §1) and verified prompts (hf_match)."""
from _common import SUFFIX

def recreate_pack(src1, src2, swap, extra=""):
    """Verified T1/T7 recreate pattern, extended to a spliced 2-shot reference.
    <<<video_1>>> = two 2.0 s source segments spliced back-to-back with ffmpeg (see INDEX.md 'Reference splicing')."""
    return (f"Recreate <<<video_1>>> 1:1 perfectly, including its HARD CUT at 2s, no transition (shot 1 = {src1}; shot 2 = {src2}). "
            "Do not change the camera angle and movements. There are only 2 changes you are going to make.\n"
            f"Change 1: Replace the {swap} in both shots of <<<video_1>>> with the {{product}} in <<<image_1>>>, identical colour and details in both shots.{extra}\n"
            "Change 2: Remove the caption from <<<video_1>>>.\n"
            "Other than change 1 and change 2, replicate <<<video_1>>> 1:1 perfectly.\n" + SUFFIX)

def still_t8(scene):
    """T8 start-frame STILL (prompt_templates v2.4 T8; verified 635d76b1, cab97518, 99157737). Ends with the suffix (Omar 2026-10-18)."""
    return f"iPhone photo, vertical 9:16, {scene} Sharp, clean, realistic phone photo, top fifth clear for text. No text or graphics.\n" + SUFFIX

def still_t9(source, change):
    """T9 start-frame EDIT pass (verified 5d2597f9, d03cbf1e, 4fd56690). Ends with the suffix (Omar 2026-10-18)."""
    return (f"Edit {source}. Keep everything exactly the same: the room, camera angle, framing, lens perspective, every piece of furniture and decor in the identical position. "
            f"Only change: {change}. Vertical 9:16, photographic, sharp and clean, no motion blur, no film grain, no text or graphics.\n" + SUFFIX)

def still_from_pack(prompt):
    """Auto T8 still for a scripted 2-shot gen: the first instant of SHOT 1, in the same setting."""
    import re
    m = re.search(r"handheld phone look, (.*?)\. SHOT 1 \(0\.0-2\.0s\), framed as the start image: (.*?) HARD CUT at 2s", prompt, re.S)
    if not m: return None
    setting, s1 = m.group(1).strip(), m.group(2).strip()
    return still_t8(f"{setting}. The first instant of this shot, as a single frame: {s1} Use <<<image_1>>> for the exact {{product}} (identical colour, shape and details).")

def script_pack(setting, s1, s2, audio, guard="The {product} from <<<image_1>>> stays identical in colour, shape and details in both shots."):
    """Verified T5 pattern (MerryFires 63K gen 4ca058a5; Merry Glow 152.9K gen 4dabfa47 used 3 cuts in 4 s)."""
    return ("Two shots in one 4-second vertical 9:16 clip joined by a STRAIGHT HARD CUT, no fade, natural real-time speed, handheld phone look, "
            f"{setting}. SHOT 1 (0.0-2.0s), framed as the start image: {s1} HARD CUT at 2s, no transition. "
            f"SHOT 2 (2.0-4.0s), new angle: {s2} {guard} Audio: {audio}. No background music, no text, no captions.\n" + SUFFIX)

# ---------- WEARABLE (heated robe) body: PUT | FEAT | PLUG | REM | COZY ----------
# Basis: body REPORT §1A (HJ winners >=47K n=20): PUT 1.5, FEAT 3.4 (1-3 jump cuts), PLUG 0.6-0.9 at 66%,
# REM 1.5 at 72%, COZY 2.1 at 84%, hard cut 12.7-13.8. 6.6M exact: 3.300/4.800/7.000/7.900/9.067/10.667/END 13.733.
def wearable_body(hook_end=3.5):
    h = hook_end
    rows = [
        {"t": f"{h:.1f} → {h+1.5:.1f}", "shot": "PUT", "content": "talent slips the {product} on, turned away with her back to the phone, hood up so the hood design is what the phone sees", "camera": "locked medium, eye level", "text": "hook line held", "gen": "B1·S1"},
        {"t": f"{h+1.5:.1f} → {h+5.1:.1f}", "shot": "FEAT", "content": "open it wide: white sherpa lining, step into the foot pouch (legs view); the B1→B2 boundary is the jump cut", "camera": "locked medium-wide, 1 jump cut", "text": "hook line held", "gen": "B1·S2 + B2·S1"},
        {"t": f"{h+5.1:.1f} → {h+5.8:.1f}", "shot": "PLUG (activation 1)", "content": "macro: USB / power-bank clicks into the port in the fur", "camera": "handheld close-up (the only handheld shot)", "text": "JK flip lands exactly here on store hooks", "gen": "B2·S2 (trim to 0.7 s)"},
        {"t": f"{h+5.8:.1f} → {h+7.4:.1f}", "shot": "REM (activation 2)", "content": "POV thumb presses the controller, LED heat levels climb", "camera": "locked close", "text": "held", "gen": "B3·S1 (trim to 1.6 s)"},
        {"t": f"{h+7.4:.1f} → {h+9.45:.2f}", "shot": "COZY (payoff)", "content": "reclined on couch/bed, fully inside, hood up, eyes close / smile, tree lights behind; CUT MID-ACTION", "camera": "locked medium-wide", "text": "held (no CTA card)", "gen": "B3·S2"},
    ]
    gens = [
        {"id": "B1", "kind": "body", "resolution": "720p", "duration_s": 4, "title": "PUT | FEAT-a",
         "shots": "S1 put-on from behind 0-2 s · S2 feature reveal 2-4 s", "feeds": "PUT, FEAT (first half)",
         "inputs": "<<<video_1>>> = spliced 2+2 s reference (library try-on + lining reveal); <<<image_1>>> = product front; optional <<<image_2>>> = lining",
         "basis": "Verified T1/T7 recreate-swap (gens c0ede3c3, f7a6d1c3 in the 1.4M Walmart; 26282071 in the 6.6M). Multi-shot inside one gen is verified (hf_20260826_063252 lining→belt→remote, PLAYBOOK §7.2).",
         "prompt": recreate_pack("a person putting the red robe on from behind, hood up", "the red robe opened wide to show the white lining and foot pouch, legs view", "red blanket robe", " Make sure the hood is up in shot 1."),
         "alt_prompt": script_pack("cozy American living room with a lit Christmas tree, daytime window light",
             "from behind, a woman swings the {product} from <<<image_1>>> over her shoulders and pulls the hood up; the hood design faces the camera; fabric swoosh.",
             "low frame from the waist down on a grey carpet: she opens the {product} wide to show the white fluffy lining and steps into the sealed foot pouch, bouncing one leg.",
             "fabric swoosh, soft footsteps on carpet")},
        {"id": "B2", "kind": "body", "resolution": "720p", "duration_s": 4, "title": "FEAT-b | PLUG",
         "shots": "S1 feature continued (walk/turn/sit) 0-2 s · S2 connector macro 2-4 s (use 0.7 s)", "feeds": "FEAT (second half), PLUG",
         "inputs": "<<<video_1>>> = spliced reference (turn/sit + plug macro); <<<image_1>>> = product; <<<image_2>>> = connector/controller photo",
         "basis": "Verified 3e6bcbbd (1.4M Walmart @10.25 s, blanket swap) + PLAYBOOK §7.5 'one action per clip: the plug is its own ≤0.63 s beat'.",
         "prompt": recreate_pack("the person in the red robe turning and sitting down", "macro of fingers clicking the white connector into the red fur", "red blanket robe"),
         "alt_prompt": script_pack("same living room as the start image",
             "the woman in the {product} from <<<image_1>>>, hood up, turns slowly and sits on the couch arm, the full length and pockets visible.",
             "macro close-up: fingers click the white connector from <<<image_2>>> into the port hidden in the fur, Christmas tree bokeh behind.",
             "fabric rustle, a crisp plastic click")},
        {"id": "B3", "kind": "body", "resolution": "720p", "duration_s": 4, "title": "REM | COZY",
         "shots": "S1 remote LEDs climb 0-2 s · S2 cozy payoff 2-4 s", "feeds": "REM, COZY",
         "inputs": "<<<video_1>>> = spliced reference (remote press + recliner snuggle); <<<image_1>>>; <<<image_2>>> = controller",
         "basis": "Verified 8f761a37 (147K: 'add a red glow around the edges of the remote when they press the button') + c0ede3c3 (cozy payoff in 1.4M ×2 and 16K).",
         "prompt": recreate_pack("POV thumb pressing the remote, heat LEDs stepping up", "person reclined on the couch fully inside the red robe, hood up, snuggling deeper", "red blanket robe", " In shot 1 the controller LEDs step up from level 3 to level 5 with a red glow."),
         "alt_prompt": script_pack("same living room, lamps on, tree lit",
             "POV: a thumb presses the white controller from <<<image_2>>> several times and the LED heat levels step up from 3 to 5, small click sounds.",
             "she is reclined on the couch fully inside the {product} with the hood up, shivers once, then snuggles deeper and pulls it to her chin, eyes closing, smiling.",
             "button clicks, a content sigh")},
    ]
    return rows, gens

# ---------- DECOR LIGHTS body (then-vs-now / tree lights / curtain) ----------
# Basis: body REPORT §1B; recycled exact template MG 119K / 84K / MGS 64.5K cuts 3.067|4.067|7.133|9.900|10.633|12.000|END 13.43,
# with the BOX/UNBOX shot cut to <=2.0 s (drop-off 0:04-0:06 on 6/7 then-vs-now reels; MG 98K box-in-hook moved it to 0:11).
def decor_body(hook_end=3.0):
    h = hook_end
    rows = [
        {"t": f"{h:.1f} → {h+1.0:.1f}", "shot": "THEN2 / bridge", "content": "second 'before' angle (bare / dark / failed setup), same room", "camera": "locked", "text": "\"Vs..\" switches ON at this cut and holds", "gen": "B1·S1 (trim to 1.0 s)"},
        {"t": f"{h+1.0:.1f} → {h+3.0:.1f}", "shot": "BOX (≤2.0 s, motion inside)", "content": "branded box on lap, lid off, product lifted out in one motion", "camera": "locked top-down", "text": "\"Vs..\"", "gen": "B1·S2"},
        {"t": f"{h+3.0:.1f} → {h+5.0:.1f}", "shot": "INSTALL", "content": "hanging / placing the product (tree, gutter, window, table)", "camera": "locked wide", "text": "\"Vs..\"", "gen": "B2·S1"},
        {"t": f"{h+5.0:.1f} → {h+6.2:.1f}", "shot": "LIT 1 (activation, ~66-73%)", "content": "app tap / plug → the product lights up, room transforms", "camera": "locked wide", "text": "\"{Occasion} this year\" switches ON exactly on this cut", "gen": "B2·S2 (trim to 1.2 s)"},
        {"t": f"{h+6.2:.1f} → {h+7.4:.1f}", "shot": "LIT 2 (escalation)", "content": "closer or lower angle, family reacts", "camera": "locked", "text": "held", "gen": "B3·S1 (trim 1.2 s)"},
        {"t": f"{h+7.4:.1f} → {h+9.4:.1f}", "shot": "LIT 3 (hero, payoff ~84%)", "content": "full hero wide, product doing its thing; hard cut at full music level", "camera": "locked hero wide", "text": "held", "gen": "B3·S2"},
    ]
    gens = [
        {"id": "B1", "kind": "body", "resolution": "720p", "duration_s": 4, "title": "THEN2 | BOX",
         "shots": "S1 second 'before' angle · S2 box open + lift out", "feeds": "THEN2, BOX",
         "inputs": "start image = the SAME room as the hook (T9 edit pass of the hook still); <<<image_1>>> = product; <<<image_2>>> = branded box",
         "basis": "Verified start-frame scene scripts behind Merry Glow 153K/119K, Merry Carrier 63K, MerryFires 63K (PLAYBOOK §15 rule 4; T4/T5). Same room in then and now (PLAYBOOK §7.5 rule 4, IG 40.3K).",
         "prompt": script_pack("the same dark, undecorated American living room as the start image, evening",
             "a second angle of the bare, unlit Christmas tree in the dim room, a tangle of old bulbs on the floor, nobody moving.",
             "top-down on a lap: hands lift the lid off the {brand} box from <<<image_2>>> and pull the {product} from <<<image_1>>> out in one smooth motion.",
             "quiet room tone, cardboard lid sliding off, a soft rustle"),
         "start_frame": {"template": "T9 edit of the hook (H1) start still", "prompt": still_t9("the hook start still (H1)", "move the camera framing to a second angle of the same bare, unlit Christmas tree, with a tangle of old bulbs on the floor and nobody in frame")}},
        {"id": "B2", "kind": "body", "resolution": "720p", "duration_s": 4, "title": "INSTALL | LIT 1",
         "shots": "S1 install · S2 activation, dark → lit", "feeds": "INSTALL, LIT 1",
         "inputs": "start image = install framing still; <<<image_1>>> = product; reference video of the real product's lit animation if available (4dabfa47 pattern)",
         "basis": "Verified 4dabfa47 (Merry Glow 152.9K @10.0 s): 'the tree's lights are defined ENTIRELY by the attached reference videos… Do not invent' — integrity guard against fake effects.",
         "prompt": script_pack("same living room, room lights off, night outside the windows",
             "a woman wraps the {product} from <<<image_1>>> around the tree from bottom to top, wires neat, everything still unlit.",
             "POV: a thumb taps the phone app and the {product} switches on instantly, showing exactly the animation in the reference video, the tree becomes the only light source and the room glows.",
             "rustle of branches, a soft phone tap, a delighted gasp from off camera",
             guard="The light artwork appears only on the {product} itself, exactly as in the reference video; nothing floats off it, no projections, no particles."),
         "start_frame": {"template": "T9 edit of the hook (H1) start still", "prompt": still_t9("the hook start still (H1)", "a woman stands beside the tree holding the start of the unlit {product} from <<<image_1>>> at the lowest branch, room lights off, night outside the windows")}},
        {"id": "B3", "kind": "body", "resolution": "720p", "duration_s": 4, "title": "LIT 2 | LIT 3",
         "shots": "S1 lower/closer angle + family reaction · S2 hero wide", "feeds": "LIT 2, LIT 3",
         "inputs": "start image = hero still of the lit room (T9 edit: 'switch off the lamps so the tree is the only light source'); <<<image_1>>>",
         "basis": "Decor payoff = 3-shot escalating block, 1.0-1.4 s each, locked camera (body REPORT §2; MG 152.9K, 119K, 84K).",
         "prompt": script_pack("the same lit living room at night, the {product} is the only light source, American flag on the wall",
             "low angle from beside the sofa: two kids in Christmas pajamas kneel in front of the lit {product}, pointing and laughing, mom behind them with a mug.",
             "locked wide hero shot of the whole room glowing from the {product}, the family on the sofa, a golden retriever on the rug.",
             "kids laughing, soft room tone",
             guard="The {product} keeps exactly the same lit pattern as the previous clip; no camera movement in shot 2."),
         "start_frame": {"template": "T9 edit of the B2 install still", "prompt": still_t9("the B2 install start still", "remove the woman, switch off the lamps so the lit {product} from <<<image_1>>> is the only light source, and add two kids in Christmas pajamas kneeling in front of it with mom behind them holding a mug")}},
    ]
    return rows, gens
