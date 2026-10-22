"""Built-in machine format specs (engine fallback). formats/formats.json (format-library workstream) overrides
these field by field when present. Every hook line is tagged P (proven exact line), F (proven formula, new slot),
T (transfer from another category/platform). Evidence cites corpus reel_keys + views.
Prompts here do NOT include the iPhone 12 suffix; prompts.py appends it to EVERY prompt, video and still (D32),
via config.ensure_suffix / config.still_prompt, and QA rejects any prompt without it.
"""

NAT = "Natural sound only: {sounds}. No background music, no text, no captions, no logos."

FORMATS = {
"F01": dict(
  title="3-2-1 Countdown Reveal", tier="A",
  categories=["wearable_gift", "decor_light", "decor_mug", "pet", "gadget"],
  evidence=["HJ 2.7M 'DO NOT let your mom see this' = tray loaf + VO 'One, two, three. Let's see how it comes out' (HJ-02)",
            "HJ 524K 'ALL mom's NEED this' muffin-tin 3-2-1 (HJ-05)", "MC 63.3K POV envy + 3-2-1 VO (MC-01)",
            "TRAY_321 opening: 3/6 HJ fresh posts >=50K, median 57K (hooks REPORT §4)",
            "external nocturne.robes0 1.3M muffin-tin tray (callout text)"],
  psych=["countdown", "curiosity_gap"],
  hook_formulas=["DO NOT let your {recipient} see this ❄️😳 (+3-2-1 VO)", "ALL {recipient}'s NEED this 😳❄️ (+3-2-1)",
                 "{Audience}... this is for you 🥹 (+3-2-1 tray)"],
  hook_lines=[("DO NOT let your mom see this ❄️😳", "P", "HJ-02 2.7M"), ("ALL mom's NEED this 😳❄️", "P", "HJ-05 524K"),
              ("DO NOT let your wife see this 😳❄️", "F", "HJ-02 x HJ 165K"), ("DO NOT let your grandma see this ❄️😳", "F", "HJ-02"),
              ("ALL wife's NEED this 😳❄️", "F", "HJ-05"), ("Cold-aholics this is for you 🥹💕", "T", "ext warmly 6.0M"),
              ("DO NOT show this to you're mom 😳", "P", "HJ 97K"), ("POV: the whole street is JEALOUS of your house.. 😏🏠", "P", "MC-01 63.3K (3-2-1 VO)"),
              ("Every Christmas mom NEEDS this 😳❄️", "F", "MC-02 62.8K"), ("Grinch lovers.. this is for you 😳🎅🏻🎄", "T", "CapCut draft 0912"),
              ("DO NOT let a Christmas MOM see this... 🎄✨", "T", "JingleMagic FB (viral research)"), ("Cat moms... this is for you 🥹🐾", "T", "ext callout")],
  text_cards=[(0, "end_or_activation", "{hook}")],
  hook_prompt_original=("A young woman stands in a bright {room} holding a metal baking tray at chest height toward the camera; "
                        "the folded {product_look} from <<<image_1>>> sits on the tray like a freshly baked loaf, its design facing the lens. "
                        "She says loudly in American English, about one word per second: \"One… two… three… let's see how it comes out!\" "
                        "and on \"three\" flips the tray so the {product} drops toward the lens. The product fills the middle third of the frame "
                        "and looks exactly like <<<image_1>>>. Slight handheld micro-shake. " + "Natural sound: her voice, tray clink, fabric thud. No background music, no text, no captions."),
  hook_prompt_recreate=("Recreate <<<video_1>>> 1:1 perfectly. Do not change the camera angle and movements. There are only 2 changes you are going to make.\n"
                        "Change 1: Replace the {source_object} in <<<video_1>>> with the {product_look} in <<<image_1>>>.\n"
                        "Change 2: Remove the caption from <<<video_1>>>.\nOther than change 1 and change 2, replicate <<<video_1>>> 1:1 perfectly."),
  startframe_prompt=("iPhone photo in a bright {room} with a Christmas tree and a small American flag on the wall. A young woman in grey loungewear "
                     "holds a metal baking tray at chest height; the folded {product_look} from the first image sits on it like a baked loaf, "
                     "design facing the camera, filling the middle third of the frame. Top 20% of the frame is plain wall (room for text). "
                     "Sharp, clean, realistic phone photo."),
  music=[("3-2-1 VO + Holly Jolly Christmas (Bublé) from its opening line at the first body cut", 0.1), ("Jingle Bells (Viibez) 0:00", 0.0)],
  captions=["Get yours👉{url}", "It's heated❄️☺️ {url}", "They'll be asking where you got it.. 🤭🎄"],
  say_keywords=["COZY", "WARM", "{KEYWORD}"],
  explore=["tray swap for a muffin tin / cake tin / silver platter (prop bank)", "pet: cat sits on the tray beside the folded carrier",
           "decor: box on the tray, 3-2-1 then the room lights up"],
  kill_rule="family judged on >=3 fresh renders inside the page's first 10 days; product must fill >=30% at 0 s (2.7M vs 16K pair)",
),
"F02": dict(
  title="Fake Store Pallet Reveal (+JK twist)", tier="A",
  categories=["wearable_gift", "pet", "decor_mug", "decor_light", "decor_fire", "accessory", "gadget"],
  evidence=["HJ 1.4M 'Grinch X Target 😳🎄❄️' (HJ-03)", "HJ 1.4M 'Christmas-HOLICS RUN, dont walk to Walmart' -> 'JK, We make them' at 8.33 s (HJ-04)",
            "HJ 326K 'HeatedJammies at Target' -> 'JK, Get in bio' at 7.33 s; best buyers-per-view in the dataset (0.19 orders/1K)",
            "HJ 147K staff unveil, 87K, 71K -> 'Jk we make them:)' at 6.5 s", "PALLET opening: 5/6 HJ fresh posts >=50K, median 206K (hooks REPORT §4)",
            "Store-pallet family #1 for sales in every attribution method: 0.07-0.15 orders/1K, ~2x sessions/1K (shopify MJ §3)",
            "ext tryglowmas Costco pallet 246K IG; warmrobestore 'Period girls RUN don't walk to Target' 834K"],
  psych=["store_surprise", "jk_twist", "social_proof", "urgency"],
  hook_formulas=["{Character/Brand} X {Store} 😳🎄❄️ -> JK, We make them🎅🎄", "{Holiday}-HOLICS RUN, dont walk to {Store} 🎅🎄 -> JK, We make them🎅🎄",
                 "{Brand} at {Store} 😳❄️ -> JK, Get in bio", "{Product name} 😳 (over the pallet, no store)"],
  hook_lines=[("Grinch X Target 😳🎄❄️", "P", "HJ-03 1.4M"), ("Christmas-HOLICS RUN, dont walk to Walmart 🎅🎄", "P", "HJ-04 1.4M"),
              ("HeatedJammies at Target 😳❄️", "P", "HJ 326K"), ("Target X Grinch 😱", "P", "HJ 71K"), ("Heated Grinch Jammies 😳", "P", "HJ 87K"),
              ("{Brand} X Walmart 😳🎄❄️", "F", "HJ-03 x HJ-04"), ("Moms RUN dont walk to Target 😳🎄", "F", "HJ-04 (pallet required)"),
              ("Grinch X Costco 😳🎄", "F", "ext Costco pallet 246K"), ("Christmas moms, don't walk RUN to costco!🎄👀", "T", "ext tryglowmas 246K"),
              ("PurrVenture X PetSmart 😳🐾", "T", "HJ-03 transfer"), ("Cat moms RUN dont walk to PetSmart 😳", "T", "HJ-04 transfer"),
              ("Ski Mask X Target 😳", "T", "HJ-03 transfer"), ("Grinch Mug X Target 😳🎄❄️", "T", "HJ-03 transfer")],
  text_cards=[(0, "end", "{hook}")],  # D188/D191: one card; JK line lives in the FB caption
  body_override={"wearable_gift": [("HOOK", 0.0, 3.0, "pallet push-in, nobody in frame", "H"),
                                    ("PULL", 3.0, 4.9, "a hand pulls one folded {product} off the pallet toward the lens", "B1"),
                                    ("PUT", 4.9, 6.9, "man puts it on, hood up, his back to the phone", "B1"),
                                    ("FEAT_B", 6.9, 8.4, "feature: {feature_1}", "B2"),
                                    ("PLUG", 8.4, 9.2, "ACTIVATION macro: {activation_action} (JK flip lands on this cut)", "B2"),
                                    ("REM", 9.2, 10.7, "POV controller: {activation_result}", "B3"),
                                    ("COZY", 10.7, 13.0, "cozy payoff on the couch: {payoff_scene}", "B3")],
                 "_cuts": {"B1": 1.9, "B2": 1.5, "B3": 1.5}},
  hook_prompt_original=("Static wide shot down a big-box store aisle that looks like {store_look} (no logos, no readable store name), bright store lighting. "
                        "A huge perfectly stacked cardboard pallet display printed with \"{brand}\" holds a pyramid of identical folded {product_look}s from <<<image_1>>> "
                        "with the design facing out, the {brand} box from <<<image_2>>> repeated on the display, and one actively working {product} on top of the display. "
                        "Very slow push-in toward the pallet, nobody in frame, store ambience. The pallet fills the middle of the frame; top 20% is store ceiling."),
  hook_prompt_recreate=("Recreate <<<video_1>>> 1:1 perfectly. Do not change the camera angle and movements. There are only 2 changes you are going to make.\n"
                        "Change 1: Replace the {source_object} on the pallet in <<<video_1>>> with the {product_look} in <<<image_1>>> and the box in <<<image_2>>>.\n"
                        "Change 2: Remove the caption from <<<video_1>>>.\nOther than change 1 and change 2, replicate <<<video_1>>> 1:1 perfectly."),
  startframe_prompt=("iPhone photo down a wide big-box store aisle that looks like {store_look}, with plain unbranded signage. Centre frame: a huge cardboard "
                     "pallet display printed with \"{brand}\" stacked in a perfect pyramid of folded {product_look}s from the first image, the {brand} box from the second "
                     "image repeated around the base, one working {product} displayed on top, a large American flag hanging overhead. Bright even store light, top 20% clear. "
                     "Sharp, clean, realistic phone photo."),
  music=[("All I Want for Christmas Is You (Mariah Carey), slow intro 'I don't want a lot for Christmas' (album master 0:00; MV edit ~0:49.6 per CapCut drafts)", 0.0),
         ("Last Christmas (Wham!) ~2:50 of the 4:27 master (CapCut drafts median 170.2 s)", 170.2)],
  captions=["Get yours 👉 {url}", "AND they're heated ☃️🎅🏻 {url}", "Shop here👉🏻{url}"],
  say_keywords=["TARGET", "GRINCH", "{KEYWORD}"],
  explore=["cloth-pull crowd unveil instead of static pallet (F03 crossover)", "Costco/IKEA look with pallet (Costco only failed WITHOUT a pallet)",
           "use-case retarget text: 'Period girls RUN don't walk to Target' (ext 834K)"],
  kill_rule="pallet must carry brand box art; store words without a pallet flopped (6.2K, 3.9K day-1 posts)",
),
"F03": dict(
  title="Fake-Retail Crowd Unveil", tier="B",
  categories=["decor_light", "wearable_gift", "decor_mug", "decor_fire", "gadget"],
  evidence=["ext MerryGlow IG 'IKEA X Christmas' 17.4M (repost/re-shoot 755K)", "ext 'COSTCO X Navidad' 2.2M TikTok (VR-04)",
            "HJ 147K Grinch X Target staff unveil (UNVEIL opening 1/2 >=50K)"],
  psych=["store_surprise", "social_proof", "curiosity_gap", "jk_twist"],
  hook_formulas=["{Store} X Christmas 🎄🎁 -> JK, We make them", "{Store} X {Character} 😳🎄"],
  hook_lines=[("IKEA X Christmas 🎄🎁", "P", "ext 17.4M"), ("COSTCO X Navidad 🎄🎁", "P", "VR-04 2.2M"), ("Target X Christmas 🎄🎁", "F", "17.4M"),
              ("Walmart X Christmas 🎄🎁", "F", "17.4M"), ("Grinch X Target 😳🎄❄️", "P", "HJ 147K staff unveil"), ("Costco X Christmas 🎄🎁", "F", "VR-04"),
              ("Target X Grinch 😱", "P", "HJ 71K"), ("IKEA X Christmas lights 🎄✨", "F", "17.4M"), ("Walmart X Grinch 😳🎄", "F", "HJ-03"),
              ("PetSmart X Christmas 🐾🎄", "T", "17.4M"), ("Costco X Grinch 😳", "F", "VR-04")],
  text_cards=[(0, "end", "{hook}")],  # D188/D191: one card; JK line lives in the FB caption
  hook_prompt_original=("In a warehouse-style store aisle that looks like {store_look} (no logos), two employees in plain red shirts stand beside a tall display covered "
                        "with a white cloth while a small crowd of shoppers watches with phones up. On a count they pull the cloth off: a pallet of {brand} boxes from "
                        "<<<image_2>>> with working {product_look}s from <<<image_1>>> on top. Shoppers gasp and step closer. Handheld from the crowd, slow push-in. "
                        + NAT.format(sounds="crowd murmur, cloth rustle, gasps")),
  hook_prompt_recreate=("REPLICATE <<<video_1>>> 1:1 PERFECTLY. THE ONLY CHANGE YOU WILL MAKE IS THE {source_object} REVEALED UNDER THE CLOTH IN <<<video_1>>> WILL INSTEAD BE "
                        "THE {product_look} AND BOXES IN <<<image_1>>> AND <<<image_2>>>. CHANGE NOTHING ELSE."),
  startframe_prompt=("iPhone photo from inside a crowd of shoppers in a warehouse store aisle that looks like {store_look}, with plain unbranded signage. Two staff in plain red shirts hold the "
                     "corners of a white cloth draped over a tall pallet display; phones raised; American flag overhead. Top 20% clear. Sharp, clean, realistic phone photo."),
  music=[("All I Want for Christmas Is You, intro", 0.0), ("No Pique Do Natal (IG test)", 0.0)],
  captions=["Get yours👉{url}", "They'll be asking where you got it.. 🤭🎄"], say_keywords=["CHRISTMAS"],
  explore=["unveil reveals the product working (lit / heated LEDs) not just boxes", "fictional store name for legal safety"],
  kill_rule="3 renders; IG first (largest external evidence), FB second",
),
"F04": dict(
  title="Then-vs-Now (recent & retro year)", tier="A",
  categories=["decor_light", "decor_fire", "decor_mug", "wearable_gift", "pet", "gadget"],
  evidence=["MG 152.9K 'Christmas 2024.. → And Christmas 2025.. → VS... → Christmas 2026' (MG-01)", "MG 119K, 84K, 72K 'Christmas last year.. → Vs.. → Christmas in 2026'",
            "MGS 67.7K fire pit 'Christmas last year..' (= IG 40.3K)", "MGS 64.5K 'Christmas in 2025..'", "MG 70.4K retro 'Christmas trees in 1968' (1080p re-render 1.2K)",
            "ext retro winners: 'Christmas Decor in 1950' 5.5M IG, '1965🤮' 3.2M TT / 2.9M IG, '1995🤮' 1.0M",
            "Decor 3-s rate tracks views within decor pages (rho 0.72) - the disaster must land by 1-3 s (hooks REPORT §6)"],
  psych=["transformation", "curiosity_gap", "humor"],
  hook_formulas=["{Occasion} last year.. → Vs.. → {Occasion} this year", "{Occasion} {Y-2}.. → And {Occasion} {Y-1}.. → VS... → {Occasion} {Y}",
                 "{Things} in {retro year}🤮 → Vs → {Things} in 2026"],
  hook_lines=[("Christmas last year.. → Vs.. → Christmas this year", "P", "MGS-01 67.7K"), ("Christmas last year.. → VS... → Christmas in 2026", "P", "MG 119K/84K"),
              ("Christmas 2024.. → And Christmas 2025.. → VS... → Christmas 2026", "P", "MG-01 152.9K"), ("Christmas in 2025.. → Vs.. → Christmas in 2026", "P", "MGS-02 64.5K"),
              ("Christmas trees in 1968 → VS.. → Christmas trees in 2026", "P", "MG-06 70.4K"), ("Christmas Decor In 1950 → Vs… → Christmas Decor In 2026", "P", "ext 5.5M"),
              ("Christmas Decor in 1965🤮 → Vs → 2026", "P", "ext 3.2M"), ("Christmas Decor in 1995🤮 → Vs → 2026", "P", "ext 1.0M"),
              ("Movie night last year.. → Vs.. → Movie night this year", "F", "MGS-01 x MF-01"), ("Christmas morning in 1965.. → Vs.. → Christmas morning in 2026", "T", "robe transfer"),
              ("Hot cocoa in 1957.. → Vs.. → Hot cocoa in 2026", "T", "mug transfer"), ("S'mores last year.. → Vs.. → S'mores this year", "F", "MGS-01")],
  text_cards=[(0, "payoff_reveal", "{then_card}"), ("payoff_reveal", "end", "{now_card}")],  # D188/D191: VS format = max 2 cards
  hook_prompt_original=("Locked wide iPhone video of a lived-in {room} at night, Christmas tree, a family of {n_people} and a golden retriever, small American flag on the wall. "
                        "Within two seconds {disaster}; everyone jumps up and the dog runs toward the camera. HARD CUT at 2.9s to a second angle of the same messy room. "
                        "No product anywhere in frame. " + NAT.format(sounds="crackle, gasps, dog bark")),
  hook_prompt_recreate=("Recreate <<<video_1>>> 1:1 perfectly. Do not change the camera angle and movements. Change 1: make the room match the room in <<<image_3>>>. "
                        "Change 2: Remove the caption from <<<video_1>>>. Other than change 1 and change 2, replicate <<<video_1>>> 1:1 perfectly."),
  startframe_prompt=("iPhone photo at night inside a lived-in {room}: a Christmas tree, {n_people} family members in sweaters on the couch, a golden retriever, a small American "
                     "flag on the wall, {then_state}. Same room that will be used for the product shots. Top 20% plain wall/ceiling. Sharp, clean, realistic phone photo."),
  music=[("Last Christmas (Wham!) ~2:50 (CapCut median 170.2 s; MG-01 171.2)", 170.2), ("It's Beginning to Look a Lot Like Christmas (Bublé) ~0:31.6", 31.6),
         ("All I Want for Christmas Is You, intro (retro variants)", 0.0)],
  captions=["Get it here 👉 {url}", "Be the envy of your friends.. 🤭🎄", "Your neighbors are gonna be jealous... 🤭❄️"], say_keywords=["TREE", "LIGHTS", "FIRE"],
  explore=["retro year with 🤮 'then' and vintage grade added in the EDIT (prompt stays iPhone-12 clean)", "box in the hook (MG 98K moved drop-off to 0:11)",
           "kids-wonder payoff (ext projector)", "wearable: shivering cold house 1965 → robe LEDs climb"],
  kill_rule="run BOTH recent and retro on every decor product; judge each on 3 renders",
  body_note="Decor: product NOT at 0 s (disaster first) — QA inverts the product-at-0s check for this format.",
),
"F05": dict(
  title="Don't Show This To...", tier="A",
  categories=["wearable_gift", "decor_mug", "pet", "accessory", "gadget"],
  experiment_only_categories=["decor_light", "decor_fire"],   # D19: MerryFire 0/3 (457/33/3K); MGS-05 3.0K; MJIG-04 9.0K. Pending Omar.
  evidence=["HJ 2.7M, 183K, 165K, 112K, 98K, 97K, 88K (don't-let/show); flops 16K, 4.6K, 4.2K — 7/10 fresh >=50K, median 97.5K (audit R2b)",
            "ext thecozygrump 'DO NOT show this to your mom😱😂' 12.4M (heated Grinch robe, Let It Snow)", "ext 'DO NOT let your KIDS see this..👀🎄' 3.2M decor",
            "VR-02 MerryGlow IG 'do NOT show this to a Christmas mom...😱🎄' 198K in 31 h (decor)", "Omar decision D3 allowed on decor; D19 demotes decor to experiment-only after own decor 0/5 >=10K (MGS-09 457, MF 33, MF-02 3.1K, MGS-05 3.0K, MJIG-04 9.0K)"],
  psych=["forbidden", "recipient", "curiosity_gap"],
  hook_formulas=["DO NOT let your {recipient} see this ❄️😳", "DONT show this to your {recipient} ❄️😳", "do NOT show this to a {identity}...😱🎄"],
  hook_lines=[("DO NOT let your mom see this ❄️😳", "P", "HJ-02 2.7M"), ("DONT show this to your Grandma ❄️😳", "P", "HJ 183K"), ("DO NOT let your wife see this 😳❄️", "P", "HJ 165K"),
              ("DONT show this to you mom 😳🎅", "P", "HJ 112K"), ("Don't show this to your mom...", "P", "HJ 98K"), ("DO NOT show this to your mom😱😂", "P", "ext 12.4M"),
              ("do NOT show this to a Christmas mom...😱🎄", "P", "VR-02 198K"), ("DO NOT let your KIDS see this..👀🎄", "P", "ext 3.2M"),
              ("DONT show this to your mother-in-law 😳🎄", "F", "HJ 183K"), ("DO NOT let your grandkids see this..👀🎄", "F", "ext 3.2M"),
              ("DON'T show this to a Christmas lover...😳🎄", "P", "ext 576K"), ("Don't show this to a cat mom 🙀", "T", "PV test"), ("DONT show this to your dad..👨🏻", "P", "HJ-13 98K (CapCut 0912)")],
  text_cards=[(0, "end", "{hook}")],
  hook_prompt_original=("POV from a couch in a {room} with a Christmas tree: a smiling bearded man in a sweater walks toward the camera holding the {brand} gift box from <<<image_2>>> "
                        "open, the {product_look} from <<<image_1>>> visible inside and filling a third of the frame; her hands reach in from the bottom of frame. Gentle push-in. "
                        + NAT.format(sounds="footsteps, box rustle, soft laugh")),
  hook_prompt_recreate=("Recreate <<<video_1>>> 1:1 perfectly. Do not change the camera angle and movements. There are only 2 changes you are going to make.\n"
                        "Change 1: Replace the {source_object} in <<<video_1>>> with the {product_look} in <<<image_1>>>.\nChange 2: Remove the caption from <<<video_1>>>.\n"
                        "Other than change 1 and change 2, replicate <<<video_1>>> 1:1 perfectly."),
  startframe_prompt=("iPhone photo, POV from a couch: a woman's legs in light pants in the lower third, a smiling bearded man in a sweater just beyond her feet holding the open "
                     "{brand} gift box from the second image toward the camera with the {product_look} from the first image inside, Christmas tree and small American flag behind. "
                     "Product fills a third of the frame. Top 20% clear. Sharp, clean, realistic phone photo."),
  music=[("Let It Snow! (Dean Martin) 0:00 (CapCut offset 0.87 s on the MV file)", 0.87), ("Holly Jolly Christmas after a 3-2-1 VO", 0.1)],
  captions=["Get yours👉{url}", "It's heated❄️☺️", "Who needs one😉🎄"], say_keywords=["MOM", "COZY", "{KEYWORD}"],
  explore=["decor: shocked shopper pointing at a shelf of {brand} boxes (VR-02 visual)", "kids recipient on lights", "typo bait 'you're mom'"],
  kill_rule="needs a recipient word AND a product-first visual; Times Square/no-product openers flopped (4.2K)",
),
"F06": dict(
  title="Gift-Difficulty POV Handoff", tier="A",
  categories=["wearable_gift", "decor_mug", "decor_fire", "gadget", "pet", "decor_light"],
  evidence=["HJ 6.6M '\"Women are hard to gift..\"' POV handoff (HJ-01, Let It Snow, cuts 3.3/4.8/7.0/7.9/9.07/10.67)", "HJ 304K/101K (same file), 90K",
            "VR-03 '\"Kids are hard to gift\"' 374K from a 553-follower account", "ext 'Christmas gift ideas for Your dad!' 2.7M; '#1 gift Dad will actually use' 705K",
            "S1: 3/5 fresh >=50K (highest ceiling, not most reliable — audit R2b)"],
  psych=["gift_framing", "recipient", "cozy_payoff"],
  hook_formulas=["\"{Recipients} are hard to gift..\" (quotes, two dots)", "\"{Recipients} are so hard to gift 🥺❄️🎅\""],
  hook_lines=[("\"Women are hard to gift..\"", "P", "HJ-01 6.6M"), ("\"Moms are so hard to gift 🥺❄️🎅\"", "P", "HJ 90K"), ("\"Kids are hard to gift\" 🎄", "P", "VR-03 374K"),
              ("\"Wives are hard to gift..\"", "F", "HJ-01"), ("\"Grandmas are hard to gift..\"", "F", "HJ-01"), ("\"Girlfriends are hard to gift..\"", "F", "HJ-01"),
              ("\"Dads are impossible to gift..\"", "F", "ext 2.7M dad"), ("\"Moms are impossible to gift 🥺❄️\"", "F", "HJ 90K"), ("\"Cat moms are hard to gift..\"", "T", "HJ-01"),
              ("\"Grinch lovers are hard to gift..\"", "T", "VR-03"), ("\"Skiers are hard to gift..\"", "T", "HJ-01"), ("\"Husbands are hard to gift..\"", "F", "ext dad 705K")],
  text_cards=[(0, "end", "{hook}")],
  hook_prompt_original=("POV from a couch in a {room}: a woman's legs in light pants stretched toward the camera in the lower third. A smiling bearded man in a sweater steps in "
                        "and hands the {brand} gift box from <<<image_2>>> down toward the camera; her hands reach in from the bottom of the frame and take it. Gentle push-in. "
                        + NAT.format(sounds="footsteps, box rustle, she gasps happily")),
  hook_prompt_recreate=("REPLICATE <<<video_1>>> 1:1 PERFECTLY. THE ONLY CHANGE YOU WILL MAKE IS THE {source_object} IN <<<video_1>>> WILL INSTEAD BE THE {product_look} / BOX IN "
                        "<<<image_1>>>. CHANGE NOTHING ELSE."),
  startframe_prompt=("iPhone photo, POV from a couch: a woman's legs in light pants in the lower third, a smiling bearded man in a sweater holding the {brand} gift box from the second "
                     "image out toward the camera, Christmas tree, small American flag. Box fills a third of the frame. Top 20% clear. Sharp, clean, realistic phone photo."),
  music=[("Let It Snow! (Dean Martin) from the opening line", 0.87)], captions=["Get yours👉{url}", "And its heated😊"], say_keywords=["GIFT", "MOM"],
  explore=["husband-buyer framing", "store version: mom+daughter gasp in an aisle (304K)", "dads for fire pit"],
  kill_rule="S1 = highest ceiling, lower reliability: never retire on <4 posts (audit P10 replay)",
),
"F07": dict(
  title="Audience Callout", tier="B",
  categories=["wearable_gift", "decor_mug", "pet", "decor_light", "decor_fire", "accessory"],
  evidence=["ext warmly.official 'Cold-aholics this is for you... 🥹💕' 6.0M; jinglenap 1.8M; goth.robes 1.3M; nocturne.robes0 1.3M", "VR-05 'Christmas HATERS... this is for YOU' 211K",
            "MGS 35.4K 'Calling ALL Christmas-aholics' (81% avg watch, best retention measured)"],
  psych=["identity_callout", "curiosity_gap"],
  hook_formulas=["{Audience}-aholics this is for you 🥹💕", "{Audience}... this is for you 👀", "Calling ALL {audience} 😁"],
  hook_lines=[("Cold-aholics this is for you... 🥹💕", "P", "ext 6.0M"), ("Dog MOMS... This is for you 👀🐶", "P", "ext 1.8M"), ("I made this for the Goths... 🥹", "P", "ext 1.3M"),
              ("Christmas HATERS... this is for YOU 😂", "P", "VR-05 211K"), ("Calling ALL Christmas-aholics 😁", "P", "MGS-03 35.4K"), ("Grinch lovers.. this is for you 😳🎅🏻🎄", "F", "CapCut 0912"),
              ("Cat MOMS... this is for you 👀🐱", "F", "ext 1.8M"), ("Hot-cocoa-aholics this is for you 🥹☕", "F", "ext 6.0M"), ("Calling ALL Christmas moms 😁🎄", "F", "MGS-03"),
              ("Night-shift nurses... this is for you 🥹", "T", "ext niche"), ("Calling ALL ski bums 😁", "T", "MGS-03"), ("Always-cold wives... this is for you 🥹", "F", "ext 6.0M")],
  text_cards=[(0, "end", "{hook}")],
  hook_prompt_original=("Close medium shot in a {room}: hands lift the {product_look} from <<<image_1>>> out of the open {brand} box from <<<image_2>>> and hold it up to the camera, "
                        "turning it slowly so the design faces the lens; the product fills a third of the frame. " + NAT.format(sounds="box rustle, soft fabric sounds")),
  hook_prompt_recreate="(use F01/F05 recreate template with a callout-genre reference clip)",
  startframe_prompt=("iPhone photo in a {room} with a Christmas tree and small American flag: hands holding the {product_look} from the first image up to the camera above the open "
                     "{brand} box from the second image; product fills a third of the frame; top 20% clear. Sharp, clean, realistic phone photo."),
  music=[("Let It Snow! 0:00 (robe)", 0.87), ("Sleigh Ride (Ronettes)", 0.0)], captions=["Get yours👉{url}", "Made for you 🥹"], say_keywords=["ME", "COLD"],
  explore=["tribe list rotation: goths, nurses, teachers, gamers, BTS army (same footage = F08)"], kill_rule="3 renders per tribe; tribes are cheap — rotate fast",
),
"F08": dict(
  title="Same Footage, New Audience (niche re-skin)", tier="B",
  categories=["wearable_gift", "decor_mug", "pet", "decor_light"],
  evidence=["ext warmrobestore 'Period girls RUN don't walk to Target' 834K; obsidianrobes 509K; thecozybts BTS 417K; goth/nocturne 1.3M each",
            "Re-shoot with new talent of the 17.4M body did 755K; identical reposts collapse (6.6M→2.2K, 1.4M→16K) — re-render, never re-upload"],
  psych=["identity_callout", "recipient"],
  hook_formulas=["any proven formula with a new tribe/use-case in the slot, over a RE-RENDERED proven body (new seed/talent/room)"],
  hook_lines=[("Period girls RUN don't walk to Target 🩸🙃", "P", "ext 834K"), ("DO NOT show this to a BTS army😱😂", "P", "ext 417K"), ("I made this for the Goths... 🥹", "P", "ext 1.3M"),
              ("\"Just wear slippers\"🙄", "P", "ext 509K"), ("Nurses after a 12-hr shift... this is for you 🥹", "T", "ext niche"), ("DONT show this to a gamer 😳", "T", "HJ 183K"),
              ("Teachers are hard to gift..", "T", "HJ-01"), ("Grandmas with cold feet NEED this 😳❄️", "T", "HJ-05"), ("DO NOT let a cold wife see this ❄️😳", "F", "HJ-02"),
              ("Swifties... this is for you 🥹", "T", "ext fandom"), ("Cat dads are hard to gift..", "T", "HJ-01")],
  text_cards=[(0, "end", "{hook}")],
  hook_prompt_original="(re-render the proven hook with one change: talent or room — T3/T7 pattern; never change >1 thing)",
  hook_prompt_recreate=("KEEP THE EXACT SAME EVERYTHING 1:1. THE ONLY THING YOU ARE DOING IS CHANGING THE {person_or_background} IN <<<video_1>>> TO THE ONE IN <<<image_1>>>."),
  startframe_prompt="(reuse the proven start frame; T9 edit pass: 'Edit this photo. Keep everything exactly the same... Only change {one thing}.')",
  music=[("same song/section as the proven reel", None)], captions=["Get yours👉{url}"], say_keywords=["{TRIBE}"],
  explore=["one new tribe per day per product (cheapest experiment: 1 hook gen, body reused)"], kill_rule="tribe dead after 3 renders under page median",
),
"F09": dict(
  title="Gift Outcome", tier="B",
  categories=["wearable_gift", "decor_mug", "decor_fire", "gadget", "decor_light"],
  evidence=["ext ccreamyco IG 'got my gf this & now she won't stop…' 12.1M (TikTok 2.5M)", "ext 'The best Christmas gift for your husband😉🎄' 1.0M", "ext 'I found the best gift for my wife' 13.5M (paid flag)"],
  psych=["gift_framing", "recipient", "humor"],
  hook_formulas=["got my {recipient} this & now she won't {stop using it}😂", "pov: you finally found the perfect gift for your {recipient}"],
  hook_lines=[("got my wife this & now she won't take it off😂", "F", "ext 12.1M"), ("got my mom this & now she makes cocoa every night😂", "F", "ext 12.1M"),
              ("got my husband this & now we never go inside😂", "F", "ext 12.1M"), ("got my gf this & now she won't stop wearing it😂", "F", "ext 12.1M"),
              ("The best Christmas gift for your husband😉🎄", "P", "ext 1.0M"), ("pov: you finally found the perfect gift for your mom", "F", "ext 1.0M"),
              ("got my grandma this & now she won't leave the couch😂", "F", "ext 12.1M"), ("got my kids this & now they won't go to bed😂", "F", "ext"),
              ("bought my dad this & now he won't stop talking about it😂", "F", "ext"), ("got my cat this & now she lives in it😂", "T", "pet"),
              ("got my roommate this & now she stole it😂", "T", "MJIG ringcam")],
  text_cards=[(0, "end", "{hook}")],
  hook_prompt_original=("Medium shot in a {room}: a woman already wearing/using the {product_look} from <<<image_1>>> happily refuses to give it back as a man reaches for it, she laughs and "
                        "turns away; product fills a third of the frame. " + NAT.format(sounds="laughter, playful 'no!'")),
  hook_prompt_recreate="(T1 with a gift-reaction reference clip)", startframe_prompt=("iPhone photo in a {room}: a smiling woman wearing/using the {product_look} from the first image on the couch, "
                     "Christmas tree, small American flag; top 20% clear. Sharp, clean, realistic phone photo."),
  music=[("Christmas (Baby Please Come Home)", 0.0), ("Let It Snow!", 0.87)], captions=["Get yours👉{url}", "Best gift I've ever bought 😂"], say_keywords=["GIFT"],
  explore=["husband-buyer voice", "outcome as payoff card instead of hook"], kill_rule="3 renders",
),
"F10": dict(
  title="Silent Reveal", tier="C",
  categories=["decor_light", "pet", "gadget"],
  evidence=["ext sarvina450 silent plug-in projector 23.7M (+2.5M); pet.scanner.pk kitten 8.0M; beamllyhome 48.5M (paid flag) — all TikTok", "No FB evidence yet: A/B only"],
  psych=["curiosity_gap", "transformation"],
  hook_formulas=["(no text) dark → plug/tap → full effect by 0.5-1 s"],
  hook_lines=[("(no text)", "P", "ext 23.7M"), ("(no text) — kitten walks into carrier", "P", "ext 8.0M"), ("✨", "T", "minimal"), ("(no text) dark tree → full animation", "T", "ext"),
              ("🎄", "T", ""), ("(no text) window → snow scene", "P", "ext 48.5M paid"), ("😳", "T", ""), ("(no text) fire lights in one click", "T", ""),
              ("(no text) curtain → Santa", "T", ""), ("(no text) mug melts", "T", ""), ("(no text) robe LEDs climb", "T", "")],
  text_cards=[],
  hook_prompt_original=("Locked iPhone shot of a dark {room} at night. A hand plugs the {product_look} from <<<image_1>>> into the wall / taps the remote and within half a second the whole "
                        "room fills with {activation_result}. " + NAT.format(sounds="plug click, soft hum, kid's 'whoa'")),
  hook_prompt_recreate="(T7 only-change with the silent reference)", startframe_prompt="iPhone photo of a dark {room} at night with the {product_look} visible, hand near the plug. Sharp, clean, realistic phone photo.",
  music=[("All I Want for Christmas Is You, intro", 0.0), ("Christmas Theme (royalty-free, Sound Gallery)", 0.0)], captions=["The perfect christmas gift {url}"], say_keywords=["LIGHTS"],
  explore=["A/B vs the same body with F04 text"], kill_rule="experiment only until 3 FB renders",
),
"F11": dict(
  title="Activation / Plug-in Reveal", tier="B",
  categories=["decor_light", "wearable_gift", "decor_fire", "decor_mug", "gadget"],
  evidence=["HJ allowed variant: activation first (147K, 112K, 304K, 47K) — works, never top (body REPORT 1A)", "ext hollyglow 'EVERY Christmas Mom NEEDS this' 5.2M in 7.85 s: shelf grab → install → projection",
            "MC 62.0K staff holding the LIT product at 0 s"],
  psych=["transformation", "curiosity_gap"],
  hook_formulas=["any text formula over an activation-first opening (lit/heating at 0-1 s)"],
  hook_lines=[("Every Christmas mom NEEDS this 😏❄️", "P", "MC-02 62.8K"), ("EVERY Christmas Mom NEEDS this 🎄😱", "P", "ext 5.2M"), ("It's heated❄️☺️", "P", "HJ 98K caption"),
              ("A Grinch Heated blanket?", "P", "HJ 47K"), ("Wait for it... 🎄", "T", ""), ("One click. 🎄✨", "T", ""), ("This is a heated robe 😳", "T", ""),
              ("POV: you plug it in 😳🎄", "T", ""), ("It lights up?! 😳", "T", ""), ("Christmas just changed.. FOREVER! 😮🎄", "P", "MGS caption 1.2K (weak)"), ("Watch the window 👀🎅", "T", "")],
  text_cards=[(0, "end", "{hook}")],
  hook_prompt_original=("Handheld close-up: a hand plugs the {product_look} from <<<image_1>>> in / presses the controller and it instantly {activation_result}; "
                        "the product fills the middle of the frame. " + NAT.format(sounds="click, hum")),
  hook_prompt_recreate="(T2 short re-dress of a plug-in reference)", startframe_prompt="iPhone photo close on the {product_look} from the first image with a hand on the plug/controller; top 20% clear. Sharp, clean, realistic phone photo.",
  music=[("Jingle Bells (Viibez) 0:00", 0.0)], captions=["Get yours👉{url}"], say_keywords=["ON"], explore=["sub-10 s shelf-grab version (5.2M)"], kill_rule="3 renders",
),
"F12": dict(
  title="Cozy Ritual Payoff", tier="B",
  categories=["decor_fire", "decor_mug", "wearable_gift", "decor_light"],
  evidence=["MF 63K 'POV: Christmas movie night will never be the same 🥹❄️' (MF-01, 65% watched, 24.4% completion)", "ext meltiemug 'Me this Christmas night 🎄' 1.7M (+437K re-shot)",
            "ext 'When the nights get dark and colder, this comes back out 🤍' 7.3M (paid flag)"],
  psych=["cozy_payoff", "identity_callout"],
  hook_formulas=["POV: {ritual} will never be the same 🥹❄️", "Me this Christmas night 🎄", "When the nights get colder, this comes back out 🔥"],
  hook_lines=[("POV: Christmas movie night will never be the same 🥹❄️", "P", "MF-01 63K"), ("Me this Christmas night 🎄", "P", "ext 1.7M"),
              ("When the nights get colder, this comes back out 🔥", "F", "ext 7.3M"), ("POV: Christmas morning will never be the same 😳❄️", "F", "MF-01"),
              ("POV: s'mores night will never be the same 😳🔥", "F", "MF-01"), ("POV: hot cocoa will never be the same 🥹☕", "F", "MF-01"), ("Me every night in December 🎄", "F", "ext 1.7M"),
              ("you + me oct 1st…", "P", "ext 2.5M IG"), ("POV: winter nights will never be the same 🥹", "F", "MF-01"), ("POV: your couch just got an upgrade 🥹", "T", ""),
              ("Me after work in December 😮‍💨🎄", "T", "")],
  text_cards=[(0, "end", "{hook}")],
  hook_prompt_original=("Cozy dim living room at night, a family on the couch under blankets with a movie on; within one second a smiling woman carries the {brand} box from <<<image_2>>> "
                        "into frame toward the camera. Christmas tree lights, small American flag. " + NAT.format(sounds="movie murmur, blanket rustle, soft laugh")),
  hook_prompt_recreate="(T1 with a cozy-scene reference)", startframe_prompt=("iPhone photo of a dim cozy living room at night: family under blankets on the couch, Christmas tree, small American flag, "
                     "a woman entering with the {brand} box from the second image. Top 20% clear. Sharp, clean, realistic phone photo."),
  music=[("Last Christmas intro 0:00 (MF-01 offset 0.4 s)", 0.4), ("It's Beginning to Look a Lot Like Christmas ~0:31.6", 31.6)],
  captions=["Get it here 👉 {url}", "It's so perfect 🥹🔥"], say_keywords=["COZY", "FIRE"], explore=["mug: 'Me this Christmas night' with melt macro"], kill_rule="3 renders",
),
"F13": dict(
  title="Statement NEEDS", tier="B",
  categories=["decor_light", "wearable_gift", "decor_mug", "pet"],
  evidence=["MC 62.8K 'Every Christmas mom NEEDS this 😳❄️' (MC-02)", "ext hollyglow 'EVERY Christmas Mom NEEDS this 🎄😱' 5.2M; merry.made2 1.4M; tryglowmas 1.1M; carolvyl 892K",
            "HJ 524K 'ALL mom's NEED this' but 0.02 orders/1K (views without buyers, shopify MJ)", "HJ 'EVERY Grandma NEEDS this..' 4.2K"],
  psych=["recipient", "identity_callout"],
  hook_formulas=["Every Christmas {mom} NEEDS this 😏❄️", "ALL {recipient}'s NEED this 😳❄️"],
  hook_lines=[("Every Christmas mom NEEDS this 😳❄️", "P", "MC-02 62.8K"), ("EVERY Christmas Mom NEEDS this 🎄😱", "P", "ext 5.2M"), ("Every Christmas lover NEEDS THIS...😳🎄", "P", "ext 892K"),
              ("ALL mom's NEED this 😳❄️", "P", "HJ-05 524K"), ("Every Christmas grandma NEEDS this 😏❄️", "F", "MC-02"), ("Every Christmas-aholic NEEDS this 😏🎄", "F", "MC-02 x MGS-03"),
              ("Every cat mom NEEDS this 😏🐾", "T", "MC-02"), ("Every ski dad NEEDS this 😏❄️", "T", "MC-02"), ("Every Christmas Parents NEEDS this!", "P", "ext 564K paid"),
              ("ALL wife's NEED this 😳❄️", "F", "HJ-05"), ("Every Grinch lover NEEDS this 😳🎄", "F", "MC-02")],
  text_cards=[(0, "end", "{hook}")],
  hook_prompt_original=("POV in a store aisle that looks like {store_look} (no logos): a hand pulls the {brand} box from <<<image_2>>> off a shelf stacked with them, a working "
                        "{product_look} displayed on top of the shelf. " + NAT.format(sounds="store ambience, box slide")),
  hook_prompt_recreate="(T1 with the store-aisle reference)", startframe_prompt="iPhone photo POV in a store aisle that looks like {store_look}, a shelf stacked with {brand} boxes, one working {product} on top, American flag overhead. Sharp, clean, realistic phone photo.",
  music=[("Last Christmas intro 0:00 (MC-02 0.33 s)", 0.33)], captions=["Your neighbors are gonna be jealous... 🤭❄️", "Get it here 👉 {url}"], say_keywords=["NEED"],
  explore=["use for reach on decor; demote on robe for sales (524K sold 0.02/1K)"], kill_rule="on wearables keep as reach-only slot",
),
"F14": dict(
  title="Cut-off Word", tier="B",
  categories=["wearable_gift", "decor_light", "decor_mug", "gadget", "pet"],
  evidence=["HJ 91K 'The perfect X-MAS gift doesnt exi-' (HJ-15)", "MG 98K 'The perfect christmas decor doesn't exi-' — 2x store sessions/1K of then-vs-now (15.7 vs 3.5-8.3)",
            "VR-06 'The perfect gift for BABY MOM doesn't exi-' 488K", "ext my_everorb 701K (paid flag)"],
  psych=["curiosity_gap", "recipient"],
  hook_formulas=["\"The perfect {gift noun} doesnt exi-\"", "The perfect gift for {recipient} doesn't exi-"],
  hook_lines=[("\"The perfect X-MAS gift doesnt exi-\"", "P", "HJ-15 91K"), ("\"The perfect christmas decor doesn't exi-\"", "P", "MG 98K"), ("The perfect gift for BABY MOM doesn't exi-", "P", "VR-06 488K"),
              ("\"The perfect gift for mom doesnt exi-\"", "F", "HJ-15"), ("\"The perfect Christmas tree doesn't exi-\"", "F", "MG 98K"), ("The perfect stocking stuffer doesn't exi-", "F", "VR-06"),
              ("The perfect gift for a Christmas MOM doesn't exi-", "F", "VR-06"), ("The perfect ski mask doesn't exi-", "T", "HJ-15"), ("The perfect gift for cat moms doesnt exi-", "T", "HJ-15"),
              ("\"The perfect Christmas decoration doesn't exi-\" 😳🎄", "P", "CapCut 0914(1)"), ("The perfect gift for grandma doesn't exi-", "F", "VR-06")],
  text_cards=[(0, "end", "{hook}")],
  hook_prompt_original=("In a store aisle full of Christmas goods that looks like {store_look} (no logos), a woman in a Grinch-green robe holds the {product_look} from <<<image_1>>> "
                        "up toward the camera with a delighted face; product fills a third of the frame. " + NAT.format(sounds="store ambience")),
  hook_prompt_recreate="(T1/T2 with store-reaction reference)", startframe_prompt="iPhone photo in a store aisle that looks like {store_look}: a woman holding the {product_look} from the first image toward the camera, top 20% clear. Sharp, clean, realistic phone photo.",
  music=[("Mariah AIWFCIY intro (HJ-15)", 0.0), ("Last Christmas ~2:50 (MG 98K)", 170.2)], captions=["Get it here 👉 {url}"], say_keywords=["PERFECT"],
  explore=["use for CLICKS on decor (2x sessions/1K)"], kill_rule="3 renders",
),
"F15": dict(
  title="POV Envy", tier="B", categories=["decor_light", "decor_fire", "accessory", "pet"],
  evidence=["MC 63.3K 'POV: the whole street is JEALOUS of your house.. 😏🏠' (MC-01) + 3-2-1 VO", "MC captions 'Your neighbors are gonna be jealous...' 62.8K; MGS 'Be the envy of your friends..' 64.5K"],
  psych=["envy", "social_proof"],
  hook_formulas=["POV: the whole {street/family/lift line} is JEALOUS of your {house/tree/...}.. 😏🏠"],
  hook_lines=[("POV: the whole street is JEALOUS of your house.. 😏🏠", "P", "MC-01 63.3K"), ("POV: your neighbors are JEALOUS of your tree.. 😏🎄", "F", "MC-01"),
              ("POV: the whole family is JEALOUS of your fireplace.. 😏🔥", "F", "MC-01"), ("POV: the whole lift line is JEALOUS of you.. 😏", "T", "MC-01"),
              ("POV: the whole park is JEALOUS of your cat.. 😏", "T", "MC-01"), ("POV: every house on the block wants to know where you got this 😏", "F", "MC caption"),
              ("POV: you just won the neighborhood light contest 😏🏠", "F", "MC-01 (tree-contest wording flopped 2.1K at 1080p)"), ("POV: your house is the one everyone slows down for 😏🎄", "F", "MC-01"),
              ("POV: the in-laws are JEALOUS of your living room.. 😏", "F", "MC-01"), ("POV: the group chat is JEALOUS of your porch.. 😏", "F", "MC-01"), ("POV: the whole street is JEALOUS of your window.. 😏🎅", "F", "MC-01")],
  text_cards=[(0, "end", "{hook}")],
  hook_prompt_original=("Two smiling young women stand in front of a {house} at dusk holding a lit strand of the {product_look} from <<<image_1>>>; neighbors walking by stop and stare. "
                        + NAT.format(sounds="street ambience, 'whoa'")),
  hook_prompt_recreate="(T4 start-frame decor scene)", startframe_prompt=("iPhone photo at dusk: two smiling young women in front of a wooden front door holding the {brand} box from the second image, "
                     "a small American flag in a planter. Use the first image for the door and framing. Sharp, clean, realistic phone photo."),
  music=[("3-2-1 VO + Holly Jolly Christmas (MC-01 offset 0.13 s)", 0.13)], captions=["They'll be asking where you got it.. 🤣🎄"], say_keywords=["JEALOUS"], explore=[], kill_rule="3 renders",
),
"F16": dict(
  title="Friend / Squad Dare", tier="B", categories=["accessory", "wearable_gift", "gadget", "pet"],
  evidence=["BH 61.3K '\"If you buy one, I'll buy one too\" 😂' (BH-01)", "BH 61.1K 'Send this to someone you'd absolutely wear this with' (BH-02)", "BH 43.2K 'POV: You finally found the perfect ski mask'",
            "55% of BH orders were multi-packs (squad hooks sell squads, shopify BH §6)", "ext friend-group 2.3M", "Caveat: BH winners = first 3 posts (burst)"],
  psych=["squad", "humor"],
  hook_formulas=["\"If you buy one, I'll buy one too\" 😂", "\"Send this to someone you'd absolutely {verb} this with\" 😂", "POV: You finally found the perfect {item} 😂"],
  hook_lines=[("\"If you buy one, I'll buy one too\" 😂", "P", "BH-01 61.3K"), ("\"Send this to someone you'd absolutely wear this with\" 😂", "P", "BH-02 61.1K"),
              ("POV: You finally found the perfect ski mask 😂", "P", "BH-03 43.2K"), ("\"If you get one, I'm getting one too\" 😂", "F", "BH-01"), ("\"Buy one for me and one for you\" 😂", "F", "BH-01"),
              ("\"Send this to your ski buddy\" 😂", "F", "BH-02"), ("\"Send this to the friend who'd actually wear this\" 😂", "F", "BH-02"), ("POV: your whole ski group matches 😂", "F", "BH-03 x BH-01"),
              ("\"If you buy one, I'll buy one too\" 😂🐾", "T", "BH-01"), ("\"Send this to someone you'd match with\"", "P-flop", "HJ 1.1K (late, day 24)"), ("POV: you finally found the perfect cat carrier 😂", "T", "BH-03")],
  text_cards=[(0, "end", "{hook}")],
  hook_prompt_original=("First-person POV on a ski lift/gondola: gloved hands rip the plastic wrap off the {product_look} from <<<image_1>>> and hold it up to the camera against bright snow "
                        "and blue sky; product fills a third of the frame. " + NAT.format(sounds="wind, plastic rip, lift creak")),
  hook_prompt_recreate="(T1 with the POV unbag reference)", startframe_prompt="iPhone photo, first-person POV on a ski lift: gloved hands holding the {product_look} from the first image in its plastic bag, snow and blue sky. Sharp, clean, realistic phone photo.",
  music=[("Boombastic (Shaggy) ~0:21.6 (CapCut median)", 21.6), ("Free Bird ~0:14 (CapCut median)", 14.0)], captions=["Get it here 👉 {url}", "2 for {price2} 😂"], say_keywords=["MASK", "SQUAD"],
  explore=["3 friends in matching product as the opening frame (ext 2.3M)"], kill_rule="needs the 2-pack/squad offer live",
),
"F17": dict(
  title="Store Shock / RUN (no pallet)", tier="C", categories=["wearable_gift", "decor_light", "decor_fire"],
  evidence=["SHOCK_STORE: 3/7 HJ fresh >=50K but median 6.2K (high variance; hits had a striking reaction beat: 304K, 183K, 91K)", "MC 62.0K 'Christmas moms, don't walk RUN to Walmart' staff holding LIT product at 0 s",
            "MGS 35.4K store FaceTime (81% watched)", "Fails when product not legible: MF 2.7K, MGS 3K"],
  psych=["store_surprise", "urgency", "recipient"],
  hook_formulas=["Christmas {moms}, don't walk RUN to {Store} 😏 (staff hold the LIT product at 0 s)"],
  hook_lines=[("Christmas moms, don't walk RUN to Walmart 😏", "P", "MC-03 62.0K"), ("Christmas moms, don't walk RUN to Target 😏", "F", "MC-03"), ("Moms don't walk RUN to Costco... 😳🎄", "P-flop", "HJ 6.2K (day 1, no pallet)"),
              ("Calling ALL Christmas-aholics 😁 (FaceTime)", "P", "MGS-03 35.4K"), ("Babe, can you please get me this? 🥹", "T", "FaceTime"), ("Grandmas RUN dont walk to Walmart 😳", "F", "MC-03"),
              ("Christmas dads, don't walk RUN to Home Depot 😏", "F", "MC-03"), ("Christmas moms RUN to Walmart", "P-flop", "HJ 3.9K day 0"), ("Cat moms, don't walk RUN to Walmart 😏", "T", "MC-03"),
              ("Christmas lovers, don't walk RUN to Target 😏", "F", "MC-03"), ("Wives, don't walk RUN to Target 😏", "F", "MC-03")],
  text_cards=[(0, "end", "{hook}")],  # D188/D191: one card; JK line lives in the FB caption
  hook_prompt_original=("In a store aisle that looks like {store_look} (no logos), a store employee holds the switched-on {product_look} from <<<image_1>>> toward the camera, glowing; "
                        "a shopper gasps and points. " + NAT.format(sounds="store ambience, gasp")),
  hook_prompt_recreate="(T1 with the store-reaction reference)", startframe_prompt="iPhone photo in a store aisle that looks like {store_look}: an employee holding the working {product_look} from the first image; American flag overhead. Sharp, clean, realistic phone photo.",
  music=[("Holly Jolly Christmas (MC-03 offset 2.3 s)", 2.3)], captions=["Get it here 👉 {url}"], say_keywords=["RUN"], explore=["FaceTime UI version (Omar R19: real FaceTime UI, natural flip, no whip, no whoosh SFX)"], kill_rule="product must be lit/legible at 0 s",
),
"F18": dict(
  title="Idea vs Result", tier="C", categories=["decor_fire", "decor_light", "gadget"],
  evidence=["IG 30.9K 'The idea 🤮 → Vs... → The result 🤩' (MJIG-02)", "ext 'The first idea of our Christmas Cross Tree...🤮👎' 933K"],
  psych=["transformation", "humor"],
  hook_formulas=["The idea 🤮 → Vs... → The result 🤩", "The concept 🤮 → Vs → The product 😏"],
  hook_lines=[("The idea 🤮 → Vs... → The result 🤩", "P", "MJIG-02 30.9K"), ("The first idea... 🤮👎", "P", "ext 933K"), ("The concept 🤮", "P", "CapCut 0913(1)"),
              ("The prototype... 🤮 → Vs... → The product... 😏", "P", "library MerryTables"), ("DIY version 🤮 → Vs → the real one 🤩", "F", ""), ("My husband's idea 🤮 → Vs → mine 🤩", "F", ""),
              ("Pinterest 🤮 → Vs → reality 🤩", "T", ""), ("2 AM idea 🤮 → Vs → the result 🤩", "F", ""), ("Version 1 🤮 → Vs → Version 10 😏", "F", ""), ("Expectation 🤮 → Vs → result 🤩", "T", ""), ("Dad's DIY 🤮 → Vs → this 🤩", "F", "")],
  text_cards=[(0, "payoff_reveal", "{then_card}"), ("payoff_reveal", "end", "{now_card}")],  # D188/D191: VS format = max 2 cards
  hook_prompt_original=("On a backyard table a homemade DIY version of the {product} made from tin cans and duct tape; a hand tries it and it immediately fails (flares up / collapses). "
                        + NAT.format(sounds="'oh no no no', clatter")),
  hook_prompt_recreate="(T1 with DIY-fail reference)", startframe_prompt="iPhone photo of a backyard table with a messy homemade DIY {product} made of tin cans and tape. Sharp, clean, realistic phone photo.",
  music=[("Last Christmas ~2:50", 170.2)], captions=["Get it here 👉 {url}"], say_keywords=["RESULT"], explore=[], kill_rule="3 renders",
),
"F19": dict(
  title="Problem / Solution (avoid as lead)", tier="X", categories=["gadget"],
  evidence=["HJ 0/3 PROBLEM_CHASE >=50K (5.6K, 4.2K, 2.7K); PV 2 of 3 reels used it", "ext laser-tag 'The problem😬' 429K IG (gadgets only)"],
  psych=["transformation"], hook_formulas=["The problem.. → Vs.. → The solution"],
  hook_lines=[("The problem.. → Vs.. → The solution", "P-flop", "HJ 5.6K")], text_cards=[(0, "end", "{hook}")],
  hook_prompt_original="", hook_prompt_recreate="", startframe_prompt="", music=[], captions=[], say_keywords=[], explore=["gadgets only, as an experiment"], kill_rule="never as lead on wearables/decor/pet",
),
}

def get(fid):
    return FORMATS[fid]
