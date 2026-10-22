"""PRODUCT WORLD layer (D37, Omar 2026-10-18): hand-curated world facts per product, from Omar's transcripts
(rules_core R29 etc.), our posted reels and the CapCut drafts. profiles.py merges this with data-derived evidence
(proven formats, music, captions) into product_profiles/<product>.json. Formats are ADAPTED into the world;
the planner rejects settings or energy that contradict it.
energy: 1 = calm ... 5 = hype.
"""
WORLDS = {
 "grinch_robe": dict(
   display="Heated Grinch robe", brand="HeatedJammies", category="wearable_gift",
   corpus_products=["heated Grinch robe", "HeatedJammies robe"], pages=["HJ", "MJIG"],
   energy=2, mood=["cozy", "gifting", "family", "funny-mom"],
   audience="US moms and wives 25-55 buying a Christmas gift; Grinch fans; cold-aholics",
   world="cozy home at Christmas: living room with tree, kitchen, couch, bedroom; gifting moments; family",
   settings=["bright living room with Christmas tree", "kitchen counter", "couch with blanket", "bedroom", "front door gift handoff",
             "big-box store aisle (proven ONLY as the fake-retail pallet JK; HJ-03/HJ-04 1.4M)"],
   actions=["tray 3-2-1 drop", "put on with the hood up", "plug in the power bank", "thumb on the heat controller", "curl up on the couch", "gift handoff"],
   forbidden_settings=["ski slope", "gym", "nightclub", "outdoor sports", "beach"],
   product_look="green plush hooded Grinch robe (Grinch face on the hood)", subject="a young woman in grey loungewear", body_setting="in a bright cozy living room with a Christmas tree",
   product="Grinch robe", feature_1="the plush Grinch face hood", feature_2="the full length of the robe down to the ankles",
   activation_action="the power bank clicks into the hidden pocket and the controller light turns on",
   activation_result="the heat controller set to high, warm glow on the screen",
   payoff_scene="she curls up on the couch by the tree in the robe, hood up, smiling with a mug",
   room="living room", sounds="her voice, fabric rustle, soft room tone", source_object="folded blanket",
   store_look="a big US discount store with red-accented plain shelving (unbranded)",   # GF-C1: never name a retailer in a gen prompt
   music_forbidden=[], keyword="WARM",
   proof_shot=("PROOF", "AI-doubt proof: close-up as she adjusts the robe in natural light - hood face, foot pockets and lining identical to <<<image_1>>>, natural fabric folds"),
   body_override={"FEAT_B": ("PROOF", "AI-doubt proof: handheld close-up as she adjusts the robe in natural light, the hood face, foot pockets and lining exactly as in the reference, natural fabric folds")},
   processing_days=None, ship_days=None,
 ),
 "merryfire": dict(
   display="MerryFire tabletop fire pit", brand="MerryFire", category="decor_fire",
   corpus_products=["tabletop fire pit", "fire pit", "MerryFire tabletop fire bowl"], pages=["MF", "MGS", "MJIG"],
   energy=2, mood=["cozy", "evening", "family", "warm"],
   audience="US homeowners and families 28-60 who host; cozy-decor lovers; patio people",
   world="cozy evening at home or on the patio: coffee table by the tree, patio table at dusk, s'mores, movie night",
   settings=["living room coffee table at night by the Christmas tree", "backyard patio table at dusk", "balcony at night",
             "kitchen island during a family evening"],
   actions=["box on lap, lift it out", "set it on the table", "pour fuel into the steel cup only", "long-lighter ignition",
            "roast s'mores", "family gathers around the flame"],
   forbidden_settings=["ski slope", "gym", "daytime beach", "office"],
   product_look="round tabletop fire pit", product="tabletop fire pit", subject="a family of four and a golden retriever", body_setting="in a cozy living room at night by the Christmas tree",
   feature_1="the steel fuel cup inside the bowl", feature_2="the stones around the flame",
   activation_action="a long lighter clicks over the steel cup and the flame catches and rises steadily",
   activation_result="a tall clean flame dancing in the bowl, warm light on everyone's faces",
   payoff_scene="the family roasting marshmallows around the flame, golden retriever beside them",
   room="living room", sounds="crackle, gasps, laughter, dog bark", source_object="candle centrepiece",
   disaster="a pine-scented candle tips over and the paper decorations catch a small harmless flicker that is blown out",
   then_state="a sad unlit candle centrepiece on the coffee table and everyone bored on their phones", n_people="four",
   house="a suburban house", store_look="a big US discount store",
   proof_shot=("PROOF", "AI-doubt proof: wide shot showing the real size of the fire pit on a normal coffee table, steady flame, design identical to the reference"),
   body_override={"FAMILY": ("PROOF", "AI-doubt proof: the real-size fire pit on a normal coffee table, family roasting s'mores around the steady flame, design identical to the reference")},
   music_forbidden=[], keyword="FIRE", processing_days=None, ship_days=None,
   caption_forbidden=[r"outdoor fire pit", r"\b\d{2}\s?(\"|”|''|in(ch)?\b)"],   # D115: library caption '32” outdoor fire pit' is a different product
 ),
 "brickhood_mask": dict(
   display="Brick Hood ski mask", brand="Brick Hood", category="accessory",
   corpus_products=["ski mask", "Smiley ski mask"], pages=["BH", "MJIG"],
   energy=5, mood=["hype", "goofy", "funny", "squad", "crazy"],
   audience="US skiers and snowboarders 16-30, friend groups, ski-trip squads (55% of BH orders were multi-packs)",
   world="THE SLOPES: ski lifts, gondolas, snowmobiles, terrain park tricks, wipeouts, apres-ski; always outdoors in snow, never a store",
   settings=["ski lift / chairlift", "gondola", "snowy slope run", "terrain park jump", "snowmobile", "lodge patio apres-ski"],
   actions=["first-person POV unbag on the lift, plastic wrap rip (R29)", "pull it on, face to camera", "ski or ride toward camera",
            "matching squad on the chairlift", "trick / jump / goofy wipeout", "snow angel", "apres-ski cheers", "3-2-1 on the slope then pull it on"],
   forbidden_settings=["living room", "kitchen", "bedroom", "couch", "office", "store aisle"],
   product_look=("yellow knit ski mask (smiley knit face, ONE single wide sideways-oval eye cutout, short knit stud on top, rolled ribbed neck)"),
   subject="a snowboarder in a red jacket and black goggles with three friends", body_setting="on a bright snowy ski slope and chairlift, blue sky",
   product="ski mask", feature_1="the smiley knit face and the wide eye cutout", feature_2="the rolled ribbed neck under the jacket",
   activation_action="the whole squad pulls their masks down at once on the chairlift", activation_result="four matching masks staring at the camera",
   payoff_scene="the squad clinks drinks on the lodge patio in their masks, goggles up, laughing",
   room="ski lift", sounds="wind, plastic rip, lift creak, friends laughing, skis carving", source_object="beanie",
   music_forbidden=["Christmas songs (wrong niche)"], music_preferred=["boombastic_tiktok"],
   proof_shot=("PROOF", "AI-doubt proof: close-up on the chairlift: the mask worn under black goggles, the eye cutout fitting the goggles, breath fogging in the cold"),
   body_override={"ACTION2": ("PROOF", "AI-doubt proof: close-up on the chairlift, gloved hands adjust the mask under black goggles, the eye cutout fitting the goggles, breath fogging in the cold")}, copy_forbidden=["grinch", "santa", "christmas", "xmas", "mom", "grandma", "cozy", "heated"], keyword="MASK", processing_days=None, ship_days=None,
   # D113: innovation slot stays on the slopes - F01 3-2-1 on the snowy slope (ADAPTATIONS F01) with the own proven BH line
   poc_hooks={"F01": ("If you buy one, I'll buy one too 😂", "P", "own BH-01 61,290 views (proven BH line, here on the snowy-slope 3-2-1 visual)")},
 ),
 "grinchmelt_mug": dict(
   display="GrinchMelt chocolate melter mug", brand="GrinchMelt", category="decor_mug",
   corpus_products=["Grinch mug"], pages=["MJIG"],
   energy=1, mood=["calm", "cozy", "ASMR", "satisfying"],
   audience="US women 22-50, hot-cocoa and cozy-night lovers, Grinch fans",
   world="calm cozy night in: kitchen counter, by the tree, blanket, melting chocolate, steam, tealight glow",
   settings=["kitchen counter at night", "coffee table by the Christmas tree", "window seat with blanket"],
   actions=["chocolate pieces into the mug", "tealight lit under the mug", "macro chocolate melting", "slow sip under a blanket"],
   forbidden_settings=["ski slope", "party", "outdoor sports"],
   product_look="Grinch chocolate melter mug", product="melter mug", subject="a young woman in a cozy sweater", body_setting="at a kitchen counter at night with warm tealight glow",
   feature_1="the open-mouth tealight window", feature_2="the candy-cane handle",
   activation_action="a tealight is lit inside the mouth window", activation_result="chocolate slowly melting, glossy, steam rising",
   payoff_scene="a slow sip by the tree under a blanket", room="kitchen", sounds="match strike, soft crackle, spoon clink",
   source_object="mug", copy_forbidden=["run", "ski", "squad"],
   proof_shot=("PROOF", "AI-doubt proof: real-time close-up of the chocolate softening over the tealight in a normal kitchen, mug design identical to the reference"),
   body_override={"MELT": ("PROOF", "AI-doubt proof: real-time handheld close-up, the chocolate wafers softening into glossy melted chocolate over the lit tealight in a normal home kitchen, spoon stirring once, mug design identical to the reference")}, music_forbidden=["Last Christmas", "Boombastic", "Free Bird", "Jingle Bells (Viibez)"], keyword="COZY", processing_days=None, ship_days=None,
 ),
 "merryglow_lights": dict(
   display="MerryGlow tree lights", brand="MerryGlow", category="decor_light",
   corpus_products=["tree lights"], pages=["MG", "MGS"], energy=3, mood=["wow", "transformation", "family", "festive"],
   audience="US families decorating for Christmas", world="decorating the home: tree, living room, front of house at night",
   settings=["living room with tree at night", "front yard of a house at night"], actions=["hang lights", "plug in", "lights burst on", "kids react"],
   forbidden_settings=["ski slope", "gym"], product_look="programmable pixel LED tree lights: strands of tiny LEDs hanging from the star down the whole tree, showing animated colour pictures (a snowman, a train, snowflakes) across the tree", product="tree lights", hands_word="LED strands and controller", subject="a family with two kids", body_setting="in a living room at night with a Christmas tree",
   activation_action="the plug clicks in", activation_result="the tree lights up and an animated snowman picture slides across the LED strands",
   proof_shot=("PROOF", "AI-doubt proof: the plug going into a normal US wall outlet, then the lights on a normal 6 ft tree in a normal-size living room"),
   body_override={"LIT2": ("PROOF", "AI-doubt proof: the lights on a normal 6 ft tree in a normal-size living room, realistic wire and plug, kids react"),
                  "BOX": ("BOX", "a plain unbranded gift box already in hands, lid off, the coiled LED light strands with their small controller lifted out (never a slow unbox)"),
                  # D110 (GF-Q5/GF-Q6 promoted, MG-01 2d4f23c9 / OMAR_REF 7.17-9.92 s): own install grammar + named, distinct after animations
                  "INSTALL": ("INSTALL", "the dad on a silver step ladder drops the star topper and ring stack onto the tip of the tree and the LED strands unfold slowly down around it, locked wide"),
                  "LIT3": ("LIT3", "final after, a different animation: a little train picture chugs in a spiral around the tree while snowflakes drift down the strands; hard cut out")}, payoff_scene="family in front of the glowing tree",
   room="living room", sounds="click, gasps, kids cheering", source_object="old tree lights", music_forbidden=[], keyword="LIGHTS", processing_days=None, ship_days=None,
   # F04 then-vs-now (own MG-01 153K / MG-02 119K / MG-04 84K, all DISASTER_THEN, 4-5 people + golden retriever; contact sheets checked 2026-10-19 London)
   disaster="the dad yanks a knot of old tangled string lights, they spark and short out, the tree lights die and the whole room goes dark",
   then_state="a heap of tangled old string lights on the rug and a half-lit tree with dead bulbs", n_people="five",
 ),
 "jollyglow_curtain": dict(
   display="JollyGlow curtain lights", brand="JollyGlow", category="decor_light",
   corpus_products=["JollyGlow curtain"], pages=["MC"], energy=3, mood=["wow", "envy", "festive"],
   audience="US homeowners who decorate the house front", world="the house at night: windows, porch, front yard, neighbours",
   settings=["front of a house at night", "living room window"], actions=["hang the curtain", "plug in", "house lights up", "neighbours stare"],
   forbidden_settings=["ski slope"], product_look="curtain lights", product="curtain lights", subject="a couple", body_setting="at the front of a suburban house at night",
   activation_action="the remote clicks", activation_result="the curtain lights up with snowflakes falling down the window",
   body_override={"LIT2": ("LIT2", "second after, a different animation: closer angle, a Merry Christmas script writes itself across the curtain while the couple steps back on the lawn and reacts"),
                  "LIT3": ("LIT3", "final after, a third animation: red and green waves ripple across the curtain, wide from the sidewalk with the neighbours' houses in frame; hard cut out")}, payoff_scene="the whole street looking at the house",
   room="front window", sounds="click, gasps", source_object="plain curtain", music_forbidden=[], caption_forbidden=["hard to gift"],
   poc_hooks={"F06": ("POV: the whole street is JEALOUS 😏🏠", "P", "own JollyGlow curtain reel fb_28305014139198128 63,320 views, cut to 6 words (D149 8-word hard rule; D146 curtain-fit, replaces 'Women are hard to gift..')")},
   caption_extra=['Your window is boring. Fix it 🎄 SAY "LIGHTS"'], keyword="LIGHTS", processing_days=None, ship_days=None,
 ),
 "purrventure_carrier": dict(
   caption_forbidden=[r"carrier pouch", r"hands-?free carrier", r"rushing around"],   # D135: Omar rejected the 'rushing around' line (D123)   # D118: it is a cat ball playpen (D-POC), not the carrier pouch
   display="PurrVenture pop-up cat carrier", brand="PurrVenture", category="pet",
   corpus_products=["pop-up cat carrier"], pages=["PV"], energy=3, mood=["cute", "funny", "pet"],
   audience="US cat moms 22-50", world="home with the cat, car rides, vet trips, outdoors walks",
   settings=["living room floor", "car back seat", "park path"], actions=["pop open", "cat walks in", "zip", "carry outside"],
   forbidden_settings=["ski slope"], product_look="pop-up cat carrier", product="cat carrier", subject="a young woman and her tabby cat", body_setting="in a bright living room",
   activation_action="the zip closes with a click", activation_result="the cat peeks happily through the mesh window", payoff_scene="cat and owner outside, both happy",
   room="living room", sounds="pop, zip, meow", source_object="cardboard box", music_forbidden=[], keyword="CAT", processing_days=None, ship_days=None,
 ),

 # ---- D109 (2026-10-20): 4 new products. No own posted reels yet -> evidence is POC from the corpus (features.csv EXT rows,
 # poc/poc_library.json) + research/; every field cites it in "poc_sources". Cast per F94: women default, Trump -> man.
 "heatjams": dict(
   display="HeatJams heated wearable blanket", brand="HeatJams", category="wearable_gift",
   corpus_products=["heatjams", "HeatJams blanket"], pages=["MJIG"], energy=2, mood=["cozy", "gifting", "funny-mom"],
   audience="US moms and wives 25-55 buying a Christmas gift; always-cold people (same buyer as grinch_robe, D93)",
   world="cozy home at Christmas: couch, living room with tree, bedroom; movie nights; gifting moments",
   settings=["couch with the Christmas tree behind", "bright living room with Christmas tree", "bedroom", "front door gift handoff"],
   actions=["unfold the blanket off the couch", "wrap up in it", "plug in the power bank", "thumb on the heat controller", "curl up for a movie", "gift handoff"],
   forbidden_settings=["ski slope", "gym", "nightclub", "beach"],
   product_look="bright green shaggy faux-fur heated throw blanket, long plush pile, soft and fluffy",
   subject="a young woman in grey loungewear", body_setting="on a cozy couch in a bright living room with a Christmas tree",
   product="heated blanket", feature_1="the long shaggy green pile", feature_2="how big it is, covering her from shoulders to toes on the couch",
   activation_action="the power bank clicks into the hidden pocket and the controller light turns on",
   activation_result="the heat controller set to high, warm glow on the screen",
   payoff_scene="she curls up under the blanket on the couch by the tree with a mug, smiling at the TV",
   room="living room", sounds="her voice, fabric rustle, soft room tone", source_object="plain grey throw",
   music_forbidden=[], keyword="WARM", processing_days=None, ship_days=None,
   body_override={"PUT": ("PUT", "lifts the folded {product} off the couch and wraps it around her shoulders, turned three-quarter away from the phone"),
                  "FEAT_B": ("PROOF", "AI-doubt proof: handheld close-up as she runs her hand through the shaggy pile in natural light, the colour and pile exactly as in the reference, natural folds")},
   poc_hooks={"F07": ("Cold-aholics this is for you... 🥹💕", "P", "ext warmly.official heated wearable blanket 6.0M views (features.csv)"),
              "F05": ("Don't let your mom see this...😳❄️", "P", "ext merry.made2 wearable blanket hoodie 1.4M views; own grinch_robe 'DO NOT let your mom see this' 2.73M (same buyer)"),
              "F13": ("Every Christmas mom NEEDS this 😳❄️", "P", "ext merry.made2 wearable blanket hoodie 1.4M views; own MC-02 62.8K")},
   poc_sources=["ext warmly.official 'Cold-aholics this is for you' heated wearable blanket 6.0M (features.csv)", "ext illsellyouwhat1 heated wearable blanket 12.4M",
                "ext merry.made2 'Don't let your mom see this...' wearable blanket hoodie 1.4M", "ext kaia.makes 'DON'T show this to a Highland cow girl' heated wearable blanket 563K",
                "own grinch_robe (same buyer, D93): F05 7/10 hits, F06 6.6M"],
 ),
 "cozyjams": dict(
   display="CozyJams Christmas pajama set", brand="CozyJams", category="wearable_gift",
   corpus_products=["cozyjams", "CozyJams pajamas"], pages=["MJIG"], energy=2, mood=["cozy", "festive", "girls-trip", "gifting"],
   audience="US women 18-45 buying Christmas pajamas for themselves, a sister or a matching family set (same buyer family as grinch_robe, D93)",
   world="Christmas at home: bedroom mirror, living room with tree, Christmas-morning couch; store-drop excitement",
   settings=["bedroom full-length mirror", "bright living room with Christmas tree", "couch on Christmas morning", "front door gift handoff"],
   actions=["pull the set out of the gift bag", "hold it up to the mirror", "twirl in the mirror", "matching set reveal with her sister", "Christmas morning on the couch"],
   forbidden_settings=["ski slope", "gym", "nightclub", "beach"],
   product_look="red-and-green Fair Isle Christmas pajama set: knit-look reindeer sweater top and red tartan plaid pants",
   subject="a young woman with long blonde hair", body_setting="in a bright bedroom with a Christmas tree in the corner",
   product="Christmas pajama set", feature_1="the Fair Isle reindeer pattern on the top", feature_2="the red tartan plaid pants down to the ankles",
   activation_action="her sister walks in wearing the same set and they both laugh", activation_result="two matching sets side by side in the mirror",
   payoff_scene="she curls up on the couch by the tree in the set with a mug of cocoa, smiling",
   room="bedroom", sounds="her voice, laughter, fabric rustle, soft room tone", source_object="old grey sweatpants",
   music_forbidden=[], keyword="PJS", processing_days=None, ship_days=None,
   body_override={"PLUG": ("MATCH", "her sister walks in wearing the same {product} and they both laugh"),
                  "REM": ("MIRROR", "both stand side by side in the mirror showing {feature_2}"),
                  "FEAT_B": ("PROOF", "AI-doubt proof: handheld close-up of the knit pattern and plaid in natural window light, the print exactly as in the reference, natural fabric folds")},
   poc_hooks={"F17": ("Sneaking out at 6am for Christmas pjs 😂🎄", "P", "ext sheispat0 Christmas pajamas 1.5M views; justurzoey 548K; Five Below 7am 657K (features.csv)"),
              "F05": ("DO NOT let your mom see this 😳🎄", "P", "own grinch_robe (same buyer, D93) 'DO NOT let your mom see this' 2.73M views"),
              "F13": ("Every Christmas mom NEEDS this 😳❄️", "P", "ext merry.made2 1.4M views; own MC-02 62.8K")},
   poc_sources=["ext sheispat0 'me dragging my sis to Aerie at 6am...' Christmas pajamas 1.5M (features.csv)", "ext sally70958 VS Christmas pajamas 3.5M",
                "ext Five Below / Aerie 'sneaking out at 7am' 657K / 548K", "ext alannaxo Target Christmas pajamas silent reveal 727K",
                "own grinch_robe buyer (D93): F05 / F02 store hooks proven"],
 ),
 "minionmask": dict(
   display="Minion Mask yellow-character ski mask", brand="Brick Hood", category="accessory",
   corpus_products=["minionmask", "Minion Mask"], pages=["BH", "MJIG"], energy=5, mood=["hype", "goofy", "meme", "squad"],
   audience="US skiers/snowboarders 16-30 who want the funniest mask on the mountain (Brick Hood sub-line, audience/minionmask.yaml)",
   world="THE SLOPES: ski lifts, gondolas, terrain park, apres-ski; always outdoors in snow, never a store",
   settings=["ski lift / chairlift", "snowy slope run", "terrain park jump", "lodge patio apres-ski"],
   actions=["first-person POV unbag on the lift, plastic wrap rip (R29)", "pull it on, face to camera", "ride toward camera",
            "matching squad on the chairlift", "goofy wipeout", "apres-ski cheers"],
   forbidden_settings=["living room", "kitchen", "bedroom", "couch", "office", "store aisle"],
   product_look="bright yellow knit ski mask with one big round grey goggle-style eye window behind a black strap, a wide open grin with white teeth stitched on, and a blue ribbed rolled neck",
   subject="a snowboarder in an orange jacket", body_setting="on a bright snowy ski slope and chairlift, blue sky",
   product="ski mask", feature_1="the big goggle eye window and the stitched grin", feature_2="the blue rolled neck under the jacket",
   activation_action="the whole squad pulls their masks down at once on the chairlift", activation_result="four matching yellow masks grinning at the camera",
   payoff_scene="the squad clinks drinks on the lodge patio in their masks, laughing",
   room="ski lift", sounds="wind, plastic rip, lift creak, friends laughing, board carving", source_object="beanie",
   music_forbidden=["Christmas songs (wrong niche)"], music_preferred=["boombastic_tiktok"],
   proof_shot=("PROOF", "AI-doubt proof: close-up on the chairlift: the mask worn under the strap, the eye window and the stitched grin exactly as in the reference, breath fogging in the cold"),
   body_override={"ACTION2": ("PROOF", "AI-doubt proof: close-up on the chairlift, gloved hands adjust the mask, the eye window and the stitched grin exactly as in the reference, breath fogging in the cold")},
   copy_forbidden=["minion", "illumination", "despicable", "grinch", "santa", "christmas", "xmas", "mom", "grandma", "cozy", "heated"],
   keyword="MASK", processing_days=None, ship_days=None,
   poc_hooks={"F16": ("If you buy one, I'll buy one too 😂", "P", "own Brick Hood sibling BH-01 61,290 views (same page/audience)"),
              "F02": ("This CHANGED the game... 🤣😂👀", "P", "ext legohead007 yellow character ski mask fake pallet 806.8K views; novaminiusa 'HOW IS THIS NOT IN COSTCO?!' 1.1M")},
   poc_sources=["own Brick Hood sibling BH-01 61.3K 'If you buy one, I'll buy one too' (F16) + BH 61.1K (same page/audience)",
                "ext novaminiusa 'HOW IS THIS NOT IN COSTCO?!' yellow character ski mask 1.1M", "ext wearlegohead 'POV: You bought the best ski mask EVER' 1.0M",
                "ext legohead007 fake pallet 'This CHANGED the game' 807K", "approved cast: masked rider IG 4.4K (refs/minionmask manifest)"],
 ),
 "trumpglow": dict(
   display="TrumpGlow car door projector", brand="TrumpGlow", category="gadget",
   corpus_products=["trumpglow", "PatriotGlow"], pages=["TG", "PG"], energy=3, mood=["pride", "trolling", "wow"],
   audience="US Trump supporters 35-70, truck/SUV owners; gift buyers for a MAGA dad or husband (audience/patriotglow.yaml)",
   world="the truck at night: driveway, parking lot, the driver door opening; daytime install in the driveway",
   settings=["driveway next to a pickup truck at night", "parking lot at night", "driveway in daylight (install)"],
   actions=["peel the 3M backing", "stick the pod under the inner door panel", "pull the door handle at night", "badge lands on the pavement", "both doors open"],
   forbidden_settings=["living room", "kitchen", "bedroom", "ski slope", "store aisle"],
   product_look="small black carbon-fibre-look square door projector pod with a round lens, and the round American Pride Trump badge it projects on the ground",
   subject="a man's hands (POV)", body_setting="next to a pickup truck in a driveway",
   product="door projector", feature_1="his hand peels the 3M backing off the black carbon pod", feature_2="he presses the pod onto the bottom of the inner door panel, no drilling",
   activation_action="at night his hand pulls the door handle and the door swings open",
   activation_result="the camera tilts down and the round glowing Trump badge lands on the pavement under the door",
   payoff_scene="wide shot of the truck with both front doors open and two badges on the pavement, slow orbit",
   room="driveway", sounds="tape peel, door handle click, door creak, night crickets", source_object="paper cutout of the badge",
   music_forbidden=["Christmas songs (wrong niche)"], keyword="USA", processing_days=None, ship_days=None,
   body_override={"UNBOX": ("UNBOX", "the box open in his hands in the driveway, the two black pods and magnets lifted out")},
   copy_forbidden=["grinch", "santa", "mom", "cozy", "heated", "ski"],
   poc_hooks={"F04": ("Old projector's last night.. 😔🇺🇸 → First night with the real one 😎🇺🇸", "P", "D183/F101: 'Fake Trump Fans vs What We ACTUALLY Sell' rejected as incoherent 2026-10-21; A3 copy modeled on Lumi Door 'His last day with us.. VS...' 2.4M views (POC-0255)"),
              "F09": ("POV: your wife got this for your truck 😂🇺🇸", "P", "Lumi Door 'POV: ur wife got this…' 1.2M views (POC-0258/0260)")},
   poc_sources=["research/trumpglow/RESEARCH.md: Lumi Door 'His last day with us.. VS...' 2.4M (POC-0255/0257) and 'POV: ur wife got this...' 1.2M (POC-0258/0260)",
                "NFL car door light 202K (POC-0277/0278)", "Omar's Hello Kitty 'Fake ... Fans.. / What We ACTUALLY Sell' anchor grammar (POC-0281..0283)",
                "own TrumpGlow draft A v7 hands-only POV (approved cast, refs/trumpglow manifest)"],
 ),
 "lumarein": dict(
   display='LumaRein horse + rider LED glow kit',
   brand='LumaRein',
   category='gadget',
   corpus_products=['lumarein'],
   pages=[],
   energy=3,
   mood=['wow', 'identity', 'aspiration'],
   audience='US horse girls / equestrians 16-45 who ride at dusk; gift buyers for a horse-loving daughter, sister or partner',
   world='the barn, arena and fields at golden hour, dusk and night; night rides on a beach or open field',
   settings=['sandy arena at golden hour', 'stable aisle', 'white-fenced paddock at dusk', 'wet beach at night', 'open field at dusk'],
   actions=['strap the leg band above the fetlock', 'clip the Y chest strap', 'press the round grey remote', 'horse lights up neon', 'canter / gallop at night'],
   forbidden_settings=['living room', 'kitchen', 'ski slope', 'driveway'],
   product_look='grey padded nylon Y-shaped chest strap with an LED strip, 4 grey leg bands with hook-and-loop closure, 100 cm LED tail strands; glows saturated neon blue (also red, green); round grey puck remote; black retail box with blue LED triangles and a white horse glowing blue',
   subject='a young woman rider in a helmet, plus POV hands with scrunchies',
   body_setting='arena / paddock with a white fence',
   product='horse LED glow kit',
   feature_1='POV hands wrap a grey leg band above the fetlock and press the velcro',
   feature_2="hands clip the grey Y chest strap across the horse's chest",
   activation_action='her hand presses the round grey remote',
   activation_result='the whole horse snaps to neon blue: chest, legs and tail',
   payoff_scene='riders galloping at night, glowing horses reflected on wet sand',
   room='arena',
   sounds='hooves, velcro rip, remote click',
   source_object='silver duct tape and a cheap LED strip',
   music_forbidden=['Christmas songs (wrong niche)'],
   keyword='GALLOP',
   processing_days=None,
   ship_days=None,
   copy_forbidden=['grinch', 'santa', 'christmas', 'trump', 'maga', 'cat', 'Comment', 'Get yours'],
   poc_hooks={'F06': ('The idea... 😭💡 → VS... → The result 😍', 'P', 'LumaRein TikTok 7698178513446128902, 2.6M views (refs/lumarein)'), 'F21': ('Do NOT show this to an equestrian... 😏', 'P', 'LumaRein TikTok 7698418896054783284, 383.5K views (covered reveal)')},
   poc_sources=['learning/lumarein_study.md (12 TikTok reels; FB page login-walled)'],
 ),
}

# Format energy deltas (format mood vs product energy) and format settings (what the format natively implies).
FORMAT_ENERGY = {"F01": 1, "F02": 2, "F03": 2, "F04": 1, "F05": 0, "F06": 0, "F07": 1, "F08": 0, "F09": 0, "F10": -1,
                 "F11": 1, "F12": -1, "F13": 1, "F14": 0, "F15": 0, "F16": 1, "F17": 2, "F18": 0, "F19": 0}
FORMAT_NATIVE_SETTING = {"F02": "store aisle", "F03": "store aisle", "F17": "store aisle", "F13": "store aisle"}

# World adaptations: how a format is re-staged inside a product world (overrides the format's default hook/startframe).
ADAPTATIONS = {
 ("F01", "brickhood_mask"): dict(
   setting="snowy ski slope",
   hook_prompt=("First-person-adjacent handheld iPhone video on a bright snowy ski slope, blue sky, a small American flag on a ski-patrol pole behind. "
                "A snowboarder in a red jacket and black goggles holds a snowboard flat at chest height toward the camera like a tray; the folded "
                "{product_look} from <<<image_1>>> sits on the board, face design toward the lens, filling the middle third of the frame. He shouts in American English, "
                "one word per second: \"One... two... three!\" and on \"three\" flips the board so the mask flies toward the lens. "
                "Natural sound only: wind, his voice, board clack, friends laughing. No background music, no text, no captions, no logos."),
   startframe=("iPhone photo on a bright snowy ski slope with a small American flag on a ski-patrol pole: a snowboarder in a red jacket and black "
               "goggles holds a snowboard flat at chest height like a tray, the folded {product_look} from the first image on it facing the camera, filling the middle "
               "third of the frame; top 20% is blue sky. Sharp, clean, realistic phone photo."),
   hook_lines=[("Ski bros.. this is for you 😂", "T", "F01 formula '{Audience}... this is for you' (HJ/ext 6.0M) x BH audience"),
               ("POV: your whole ski group needs this 😂", "T", "BH-03 43.2K x F01"),
               ("\"If you buy one, I'll buy one too\" 😂", "P", "BH-01 61.3K (proven BH line on a 3-2-1 visual)")],
   why="3-2-1 tray mechanic (HJ-05 524K) re-staged on the slope (Omar: 'a 3-2-1 ON the slope'); board replaces the baking tray"),
 ("F16", "brickhood_mask"): dict(setting="ski lift", why="native: BH-01 61.3K / BH-02 61.1K hooks are POV unbag on the lift"),
 ("F04", "merryfire"): dict(setting="living room at night by the tree", why="native: MGS-01 67.7K, MJIG-01 IG 40.3K (then-vs-now with the fire pit)"),
 ("F01", "grinch_robe"): dict(setting="bright living room with Christmas tree", why="native: HJ-05 524K tray 3-2-1"),
 # --- Covered-reveal hook options (D52 + style re-code 2026-10-18 10:09 PM PT: covered 5/16 >=50K incl HJ-02 2.7M; robe-only 5/11 vs 21/48;
 # wins all show the product's own cue at 0 s and reveal by 3.0 s; fully hidden / mismatched cue 0/6). Keyed (format, product, option).
 ("F05", "grinch_robe", "covered_reveal"): dict(setting="bright living room with Christmas tree", option="covered_reveal", hook_lines_first=True,
   refs=["HJ-02 2.7M (robe folded into a 'baked loaf' on a tray, reveal 3.0 s)", "HJ-05 524K (muffin tin on folded robe, 2.6 s)", "HJ-14 97K (muffin tin on Grinch-face robe, 3.0 s)"],
   reveal_s=2.6, cover="tray",
   hook_prompt=("Static eye-level medium shot on a phone propped at chest height in a bright {room} with a Christmas tree. A young woman holds a metal baking tray "
                "level toward the camera; the {product_look} from <<<image_1>>> is folded on it like a freshly baked loaf, its lime-green fur and the red Grinch "
                "heart clearly visible around and above the tray edges, the tray and robe filling about half of the frame. She says in American English, about one "
                "word per second: \"One, two, three. Let's see how it comes out!\" and right on \"three\" (by 2.6 seconds) she flips the tray so the robe drops open "
                "toward the lens. Natural sound only: her voice, tray clink, fabric thud. No background music, no text, no captions."),
   startframe=("iPhone photo, still eye-level medium shot in a bright {room} with a Christmas tree and a small American flag on the wall. A young woman in grey "
               "loungewear holds a metal baking tray level toward the camera; the {product_look} from the first image is folded on it like a baked loaf, lime-green "
               "fur and the red Grinch heart visible around the tray, tray and robe filling 45% of the frame. Top 20% plain wall. Sharp, clean, realistic phone photo."),
   cover_variants=["muffin tin pressed onto the folded robe with lime fur and red Santa trim showing around it, 40% of frame (HJ-05)",
                   "muffin tin on the Grinch-face part of the robe, face and fur visible, 60% of frame, torso-only framing (HJ-14)"],
   hook_lines=[("DO NOT let your mom see this ❄️😳", "P", "HJ-02 2.7M (covered tray)"), ("DO NOT show this to you're mom 😳❄️", "P", "HJ-14 97K (covered tin)"),
               ("ALL mom's NEED this 😳❄️", "P", "HJ-05 524K (covered tin, 3-2-1)")],
   why="covered-reveal hook option (HJ-02 / HJ-05 / HJ-14): product cue visible at 0 s, reveal on 'three' by 3.0 s"),
 ("F03", "grinch_robe", "covered_drape"): dict(setting="warehouse-style store aisle", option="covered_drape", hook_lines_first=True,
   refs=["MJIG-17 240.7K IG (lime fur drape = the robe fabric over a store pallet, staff line-up, reveal 1.2 s)", "HJ-10 147K (Grinch-green drape over a store display, 12 staff, 2.3 s)"],
   reveal_s=1.5, cover="drape",
   hook_prompt=("Static eye-level wide shot in a warehouse-style store aisle with plain unbranded signage and a small American flag overhead. A line of store staff "
                "in plain red shirts stands beside a tall pallet display draped in a long sheet of the lime-green fluffy fur from the {product_look} in <<<image_1>>>, "
                "the drape clearly the robe's own fur and colour. At 1.5 seconds two staff pull the fur drape off in one move: a pallet stacked with the folded "
                "robes from <<<image_1>>>. Staff cheer. Natural sound only: store murmur, fabric rustle, cheering. No background music, no text, no captions, no logos."),
   startframe=("iPhone photo, static eye-level wide shot of a warehouse-style store aisle with plain unbranded signage: a line of staff in plain red shirts beside a tall "
               "pallet display draped in lime-green fluffy fur matching the {product_look} from the first image; small American flag overhead. Top 20% clear. Sharp, realistic phone photo."),
   hook_lines=[("Grinch X Target 😂🎁❄️", "P", "HJ-10 147K (store drape unveil)"), ("Christmas X Target 🎁❄️", "T", "HJ-10 x F03 formula")],
   why="store drape unveil variant (MJIG-17, HJ-10): the drape IS the product's fur/colour (cue visible at 0 s), reveal by 2.3 s"),
 ("F01", "merryfire", "covered_glow"): dict(setting="living room at night by the tree", option="covered_glow", hook_lines_first=True, experiment_only=True,
   reveal_s=2.5, cover="cloth",
   hook_prompt=("Static eye-level medium shot in a cozy living room at night by the Christmas tree. On the coffee table the {product_look} from <<<image_1>>> sits under "
                "a sheer red cloth that two hands hold just above it; the warm flame glow shines through the cloth and the painted Christmas village pattern is "
                "visible through it. A woman counts in American English: \"One, two, three!\" and on \"three\" (by 2.5 seconds) she lifts the cloth away to reveal the "
                "steady flame. Natural sound only: her voice, cloth swish, soft crackle. No background music, no text, no captions."),
   hook_lines=[("Wait for it.. 🔥", "T", "innovation: glow-under-cloth covered reveal")],
   why="INNOVATION SLOT (20%): glow-under-cloth covered reveal for the fire pit - cue (glow + pattern) visible at 0 s"),
 ("F01", "brickhood_mask", "covered_glow"): dict(setting="snowy ski slope", option="covered_glow", hook_lines_first=True, experiment_only=True,
   reveal_s=2.5, cover="cloth",
   hook_prompt=("Static eye-level medium shot on a bright snowy ski slope, a small American flag on a ski-patrol pole behind. A snowboarder in a red jacket and black "
                "goggles holds a snowboard flat like a tray; the {product_look} from <<<image_1>>> lies on it under a thin white cloth, low sun behind so the mask's "
                "colours and face design glow through the cloth. He shouts \"One, two, three!\" and on \"three\" (by 2.5 seconds) whips the cloth off. Natural sound "
                "only: wind, his voice, friends laughing. No background music, no text, no captions, no logos."),
   hook_lines=[("POV: your whole ski group needs this 😂", "T", "BH-03 43.2K line on an innovation covered reveal")],
   why="INNOVATION SLOT (20%): glow-under-cloth covered reveal on the slope - mask design visible through the cloth at 0 s"),
 ("F01", "grinchmelt_mug"): dict(setting="kitchen counter at night",
   hook_prompt=("Static eye-level medium shot on a kitchen counter at night, warm tealight glow, a small American flag magnet on the fridge behind. A young woman "
                "in a cozy sweater holds a wooden board at chest height toward the camera; the {product_look} from <<<image_1>>> sits on it full of chocolate wafers, "
                "the Grinch face and candy-cane handle facing the lens, filling about 40% of the frame. She whispers in American English, one word per second: "
                "\"One... two... three...\" and on \"three\" she tilts the mug toward the lens: the chocolate inside is already glossy and melted, steam rising. "
                "Natural sound only: her whisper, soft crackle, spoon clink. No background music, no text, no captions."),
   startframe=("iPhone photo, still eye-level medium shot of a kitchen counter at night with warm tealight glow and a small American flag magnet on the fridge: "
               "a young woman in a cozy sweater holds a wooden board with the {product_look} from the first image on it, full of chocolate wafers, Grinch face and "
               "candy-cane handle facing the camera, filling 40% of the frame. Top 20% plain wall. Sharp, realistic phone photo."),
   hook_lines=[("When the nights get colder, this comes back out 🤍", "F", "EXT-10 7.3M cozy-ritual line, re-used on the mug's calm world"),
               ("Hot cocoa just got an upgrade ☕😳", "T", "mug-specific product line (2 emojis)")],
   why="3-2-1 adapted to the calm cocoa world: the count lands on the melted-chocolate tilt, not a drop (whisper, ASMR - PS16)"),
 ("F01", "merryfire"): dict(setting="patio table at dusk",
   hook_prompt=("Handheld iPhone video on a backyard patio at dusk, string lights and a small American flag on the fence. A woman holds a wooden "
                "serving board at chest height toward the camera with the {product_look} from <<<image_1>>> on it. She says in American English, one word per second: "
                "\"One... two... three...\" and on \"three\" a long lighter clicks and the flame catches and rises in the bowl. Natural sound only: her voice, "
                "lighter click, flame crackle, crickets. No background music, no text, no captions, no logos."),
   hook_lines=[("POV: Christmas movie night will never be the same 🥹❄️", "P", "MerryFire own proven line on the count-to-ignition visual"),
               ("Wait for it.. 🔥", "T", "F01 count-to-ignition formula")],
   why="3-2-1 adapted to the cozy-evening world: the count lands on ignition, not a drop"),
}


# ---- D113 world-consistency (G24): canonical setting terms found in prompts, checked against each product's world
SETTING_LEX = {
 "store aisle": r"store aisle|big-box store|discount store|\bshelving\b|pallet display|supermarket|warehouse-style store|checkout lane|retail (store|aisle)",
 "living room": r"living room|sectional couch|fireplace mantel",
 "kitchen": r"\bkitchen\b",
 "bedroom": r"\bbedroom\b",
 "couch": r"\bcouch\b|\bsofa\b",
 "office": r"\boffice\b|cubicle",
 "ski slope": r"ski slope|chairlift|ski lift|snowy slope|terrain park|gondola",
 "gym": r"\bgym\b", "beach": r"\bbeach\b", "nightclub": r"nightclub",
}

def world_forbidden(profile):
    """forbidden_settings + every 'never a/an/the X' clause in the world text (canonicalised via SETTING_LEX)."""
    import re
    f = {x.lower() for x in profile.get("forbidden_settings") or []}
    for m in re.findall(r"never (?:a |an |the |in a )?([a-z ]+?)(?:[;,.]|$)", (profile.get("world") or "").lower()):
        for k, rx in SETTING_LEX.items():
            if re.search(rx, m) or k.split()[0] == m.strip().split()[0]: f.add(k)
    return f

def world_conflicts(profile, text):
    """[(setting, matched words)] for settings the text puts the product in that its world forbids."""
    import re
    out, t = [], (text or "").lower()
    for k in world_forbidden(profile):
        rx = SETTING_LEX.get(k) or re.escape(k)
        m = re.search(rx, t)
        if m: out.append((k, m.group(0)))
    return out
