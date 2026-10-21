"""Body formulas per product category, with Omar's packing rule baked in.

Each shot: (code, start_s, end_s, description, gen) where gen is
  "H"  -> the hook generation: its own 4 s Seedance 2.5 gen at FULL res (1080p)
  "B1".."B4" -> packed 720p 4 s gens, two shots each, hard cut at `cut` seconds inside the gen
Timings are edit-timeline seconds (winner medians from team/body/REPORT.md, adjusted so every
packed shot fits its half of a 4 s gen). Activation lands at ~60-66 %, payoff starts ~80-84 %,
hard cut out at 12.7-13.3 s with music at full level.
"""

BODIES = {
 "wearable_gift": {
  "source": "HJ winners >=47K (n=20): modal PUT FEAT PLUG REM COZY; 6.6M cuts 3.3/4.8/7.0/7.9/9.07/10.67 end 13.73",
  "shots": [
   ("HOOK", 0.0, 3.5, "hook visual (format-specific); product legible and >=30% of frame at 0.0 s", "H"),
   ("PUT", 3.5, 5.0, "puts {product} on, turned away with her back to the phone, hood up so the hood design is what the phone sees", "B1"),
   ("FEAT_A", 5.0, 6.9, "feature reveal: opens it wide to show {feature_1}", "B1"),
   ("FEAT_B", 6.9, 8.3, "jump cut, same set-up, new pose: {feature_2} (legs/foot-pouch view)", "B2"),
   ("PLUG", 8.3, 9.1, "ACTIVATION insert, handheld macro: {activation_action}", "B2"),
   ("REM", 9.1, 10.6, "POV thumb on the controller: {activation_result}", "B3"),
   ("COZY", 10.6, 13.0, "cozy payoff, locked medium-wide: {payoff_scene}; cut mid-action", "B3"),
  ],
  "cuts": {"B1": 2.0, "B2": 2.0, "B3": 1.6},
  "activation_shot": "PLUG", "payoff_shot": "COZY",
 },
 "decor_light": {
  "source": "Merry Glow 119K/84K + Merry Glows 64.5K recycled template (cuts 3.07/4.07/7.13/9.90/10.63/12.0 end 13.43); "
            "MG 98K box-in-hook variant moved drop-off to 0:11",
  "shots": [
   ("THEN", 0.0, 2.9, "'then' scene (format-specific): busy lit living room / bare house, 3-6 people + dog, disaster lands by 1-3 s", "H"),
   ("THEN2", 2.9, 3.9, "second 'before' angle inside the same hook gen (internal hard cut)", "H"),
   ("BOX", 3.9, 5.8, "{brand} box already in hands, lid off, {product} lifted out (never a slow unbox)", "B1"),
   ("INSTALL", 5.8, 7.9, "installing {product} in {room} the way our own reels show it, locked wide, motion in frame", "B1"),
   ("ACT", 7.9, 8.6, "ACTIVATION insert: {activation_action}", "B2"),
   ("LIT1", 8.6, 10.0, "first after: {activation_result}, locked wide", "B2"),
   ("LIT2", 10.0, 11.5, "escalation: closer/wider angle, kids or family react", "B3"),
   ("LIT3", 11.5, 13.2, "final after: a different named animation from the first after, wide; hard cut out", "B3"),
  ],
  "cuts": {"B1": 1.9, "B2": 1.5, "B3": 2.0},
  "activation_shot": "ACT", "payoff_shot": "LIT3",
 },
 "decor_fire": {
  "source": "Merry Glows 67.7K = IG 40.3K (THEN 0-2.8, BOX, PLACE, SETUP, ACT lighter 9.57 (66%), FAMILY 11.23-14.51); "
            "Omar rule: fuel pour + ignition before snacks",
  "shots": [
   ("THEN", 0.0, 2.9, "'then' disaster (format-specific)", "H"),
   ("BOX", 2.9, 4.7, "POV {brand} box on lap, {product} lifted out", "B1"),
   ("PLACE", 4.7, 6.6, "{product} set on the coffee/patio table, family gathering", "B1"),
   ("POUR", 6.6, 7.6, "quick setup insert: fuel poured into the steel cup only", "B2"),
   ("IGNITE", 7.6, 9.2, "ACTIVATION: {activation_action}", "B2"),
   ("FAMILY", 9.2, 11.3, "family roasting s'mores around it, dog, laughter", "B3"),
   ("HERO", 11.3, 13.2, "hero shot of the flame at night; hard cut out", "B3"),
  ],
  "cuts": {"B1": 1.8, "B2": 1.0, "B3": 2.1},
  "activation_shot": "IGNITE", "payoff_shot": "HERO",
 },
 "decor_mug": {
  "source": "transfer of the wearable/decor ratios (no FB winner yet; IG 23K then-vs-now mug)",
  "shots": [
   ("HOOK", 0.0, 3.3, "hook visual (format-specific); mug legible at 0 s", "H"),
   ("UNBOX", 3.3, 5.0, "{brand} box open in hands, mug lifted out", "B1"),
   ("POUR", 5.0, 6.8, "chocolate pieces / cocoa going into the mug", "B1"),
   ("PLACE", 6.8, 8.3, "mug set on its stand, tealight below", "B2"),
   ("LIGHT", 8.3, 9.2, "ACTIVATION: tealight lit, flame catches", "B2"),
   ("MELT", 9.2, 10.8, "macro: chocolate melting, steam", "B3"),
   ("COZY", 10.8, 13.1, "cozy sip by the tree, blanket, smile; hard cut", "B3"),
  ],
  "cuts": {"B1": 1.7, "B2": 1.5, "B3": 1.7},
  "activation_shot": "LIGHT", "payoff_shot": "COZY",
 },
 "accessory": {
  "source": "Brick Hood 61.3K (HOOK 0-2.73, WEAR -4.87, ACTION, GROUP, ACTION, FUN, PAYOFF -12.43); 61.1K",
  "shots": [
   ("HOOK", 0.0, 2.9, "POV gloved hands unbag {product} on a ski lift; product 30-35% of frame", "H"),
   ("WEAR", 2.9, 4.9, "pulls it on, three-quarter view, eyes on the product, portrait", "B1"),
   ("ACTION", 4.9, 6.4, "skiing/riding toward camera", "B1"),
   ("GROUP", 6.4, 7.8, "the squad in matching {product}s on the chairlift", "B2"),
   ("ACTION2", 7.8, 9.3, "second action angle", "B2"),
   ("FUN", 9.3, 11.0, "snow angel / goofy moment", "B3"),
   ("PAYOFF", 11.0, 12.8, "social payoff: apres-ski cheers; hard cut", "B3"),
  ],
  "cuts": {"B1": 2.0, "B2": 1.4, "B3": 1.7},
  "activation_shot": "GROUP", "payoff_shot": "PAYOFF",
 },
 "pet": {
  "source": "body REPORT 1E recommended pet template (no performance data yet)",
  "shots": [
   ("HOOK", 0.0, 3.5, "hook visual; product WITH the pet >=30% of frame at 0 s", "H"),
   ("OPEN", 3.5, 5.0, "{product} popped open", "B1"),
   ("ENTER", 5.0, 6.8, "pet walks in, locked", "B1"),
   ("INSIDE", 6.8, 7.8, "close-up: pet's face through the window", "B2"),
   ("ACT", 7.8, 8.7, "ACTIVATION: zip/strap click, handheld close-up (JK flip lands here)", "B2"),
   ("CARRY", 8.7, 10.5, "carried outdoors, follow shot", "B3"),
   ("PAYOFF", 10.5, 12.7, "pet peeking out happily, smiling owner; hard cut", "B3"),
  ],
  "cuts": {"B1": 1.5, "B2": 1.0, "B3": 1.8},
  "activation_shot": "ACT", "payoff_shot": "PAYOFF",
 },
 "gadget": {
  "source": "generic product-demo transfer (external toys/gadgets 374K-2.3M)",
  "shots": [
   ("HOOK", 0.0, 3.3, "hook visual; gadget legible at 0 s", "H"),
   ("UNBOX", 3.3, 5.0, "box open in hands, gadget out", "B1"),
   ("DEMO1", 5.0, 6.8, "feature 1: {feature_1}", "B1"),
   ("DEMO2", 6.8, 8.3, "feature 2: {feature_2}", "B2"),
   ("ACT", 8.3, 9.2, "ACTIVATION: {activation_action}", "B2"),
   ("RESULT", 9.2, 10.8, "{activation_result}", "B3"),
   ("PAYOFF", 10.8, 13.1, "{payoff_scene}; hard cut", "B3"),
  ],
  "cuts": {"B1": 1.7, "B2": 1.5, "B3": 1.6},
  "activation_shot": "ACT", "payoff_shot": "PAYOFF",
 },
}
BODIES["home"] = BODIES["gadget"]
BODIES["other"] = BODIES["gadget"]

def body_for(category):
    return BODIES.get(category, BODIES["gadget"])

def validate_body(b):
    """Check packing feasibility: each shot fits its half of the 4 s gen; returns list of problems."""
    probs = []
    gens = {}
    for code, s, e, _, g in b["shots"]:
        gens.setdefault(g, []).append((code, e - s))
    for g, shots in gens.items():
        if g == "H":
            if sum(d for _, d in shots) > 4.0 + 1e-6: probs.append(f"hook gen over 4 s: {shots}")
            continue
        if len(shots) != 2: probs.append(f"{g} has {len(shots)} shots (need 2)")
        cut = b["cuts"][g]
        if not 1.0 <= cut <= 3.0: probs.append(f"{g} cut {cut} outside 1-3 s")
        if shots[0][1] > cut + 1e-6: probs.append(f"{g} shot1 {shots[0]} longer than cut {cut}")
        if len(shots) > 1 and shots[1][1] > 4.0 - cut + 1e-6: probs.append(f"{g} shot2 {shots[1]} longer than {4-cut:.1f}")
    end = b["shots"][-1][2]
    if not 12.7 <= end <= 13.8: probs.append(f"length {end} outside 12.7-13.8")
    return probs
