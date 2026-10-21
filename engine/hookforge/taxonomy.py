"""Format taxonomy + psychology coding. One mapping used everywhere (corpus, backtest, briefs, learning).

Formats are *hook formats* (what happens in 0-4 s + the text device). The body follows the
category body formula (formats/BODY_FORMULAS.md). Psychology factors are coded by deterministic
rules from hook text + family + opening so own reels, external reels and new drafts are coded the
same way (no hand-waving): see code_psych().
"""
import re

FORMATS = {
    "F01": "countdown_321",          # 3-2-1 tray/tin/prop reveal with VO
    "F02": "fake_store_pallet",      # branded pallet in a store aisle, optional JK flip
    "F03": "crowd_unveil",           # staff/crowd cloth-pull "X X Christmas"
    "F04": "then_vs_now",            # disaster 'then' -> Vs -> product 'now' (recent or retro year)
    "F05": "dont_show",              # DO NOT show/let {recipient} see this
    "F06": "gift_difficulty_pov",    # "{Recipients} are hard to gift.." + POV handoff
    "F07": "audience_callout",       # "{Audience}... this is for you 🥹" / Calling ALL
    "F08": "niche_reskin",           # same footage, new tribe/use-case in the hook
    "F09": "gift_outcome",           # got my wife this & now she won't...
    "F10": "silent_reveal",          # no hook text, product-first activation
    "F11": "activation_reveal",      # plug-in / switch-on is the hook
    "F12": "cozy_ritual",            # POV: movie night will never be the same / me this Christmas night
    "F13": "statement_needs",        # Every Christmas mom NEEDS this
    "F14": "cutoff_word",            # The perfect X doesn't exi-
    "F15": "pov_envy",               # POV: the whole street is JEALOUS
    "F16": "friend_squad",           # If you buy one I'll buy one too / send this to
    "F17": "store_shock",            # gasping shopper / RUN don't walk (no pallet) / FaceTime
    "F18": "idea_vs_result",         # The idea 🤮 -> Vs -> The result
    "F19": "problem_solution",       # The problem.. -> Vs -> The solution (avoid as lead)
    "F99": "other",
}
FORMAT_TITLES = {
    "F01": "3-2-1 Countdown Reveal", "F02": "Fake Store Pallet Reveal (+JK twist)", "F03": "Fake-Retail Crowd Unveil",
    "F04": "Then-vs-Now (recent & retro year)", "F05": "Don't Show This To...", "F06": "Gift-Difficulty POV Handoff",
    "F07": "Audience Callout", "F08": "Same Footage, New Audience (niche re-skin)", "F09": "Gift Outcome",
    "F10": "Silent Reveal", "F11": "Activation / Plug-in Reveal", "F12": "Cozy Ritual Payoff",
    "F13": "Statement NEEDS", "F14": "Cut-off Word", "F15": "POV Envy", "F16": "Friend / Squad Dare",
    "F17": "Store Shock / RUN (no pallet)", "F18": "Idea vs Result", "F19": "Problem / Solution (avoid as lead)",
    "F99": "Other",
}

def format_of(hook_family="", archetype="", hook_text="", vo321=False):
    f = (hook_family or "").lower(); a = (archetype or "").upper(); t = (hook_text or "").lower()
    if "silent" in f or (t.strip() in ("", "(no text)", "nan") and "product_first" in f): return "F10"
    if "then_vs_now" in f or "nostalgia" in f: return "F04"
    if "idea_vs_result" in f or "first idea" in t: return "F18"
    if "problem" in f: return "F19"
    if "unveil" in f or a == "UNVEIL" or re.search(r"\bx christmas\b|\bx navidad\b", t): return "F03"
    if "store_pallet" in f or a == "PALLET" or "store_run + pallet" in f: return "F02"
    if a == "TRAY_321" or vo321 or "3-2-1" in f: 
        if "dont" in f or "don't" in t or "do not" in t: return "F05"
        if "callout" in f: return "F07"
        return "F01"
    if f.startswith("dont") or "don't show" in t or "dont show" in t or "do not" in t and ("see this" in t or "show this" in t): return "F05"
    if "gift_difficulty" in f or "hard to gift" in t: return "F06"
    if "callout" in f or "this is for you" in t or "calling all" in t: return "F07"
    if "gift_outcome" in f or "surprise_gift" in f or re.search(r"got my .* (this|one)", t): return "F09"
    if "ritual" in f or "will never be the same" in t or "me this christmas" in t: return "F12"
    if "needs" in f or "statement" in f or "need this" in t: return "F13"
    if "cutoff" in f or "exi-" in t or "exi…" in t: return "F14"
    if "envy" in f or "jealous" in t: return "F15"
    if f in ("friend_dare", "send_to", "pov_found", "friend_group") or "buy one" in t or "send this to" in t: return "F16"
    if "store" in f or a == "SHOCK_STORE" or "run" in t and ("walk" in t): return "F17"
    if "niche" in f or "use-case" in f: return "F08"
    if "pov" in f: return "F12"
    if "gift_for_recipient" in f or "gift" in f: return "F09"
    return "F99"

RECIPIENTS = r"\b(mom|moms|mom's|mother|wife|wives|grandma|grandmas|grandmother|women|girlfriend|gf|husband|dad|dads|kids|boys mom|baby mom|mother-in-law|sister|bestie)\b"
IDENTITY = r"(-aholic|aholics|holics|lovers?|army|goths?|girls|moms|dads|cat mom|dog mom|skiers?|snowboarders?|haters|nurses|bums|crew)"

PSYCH = ["curiosity_gap", "forbidden", "recipient", "identity_callout", "store_surprise", "jk_twist", "social_proof",
         "gift_framing", "humor", "transformation", "envy", "urgency", "countdown", "cozy_payoff", "squad"]

def code_psych(hook_text="", fmt="F99", archetype="", body_hint="", caption=""):
    t = (hook_text or "").lower(); a = (archetype or "").upper()
    c = {k: 0 for k in PSYCH}
    c["curiosity_gap"] = int(fmt in ("F01", "F03", "F10", "F11", "F14", "F18") or "?" in t or "exi-" in t or "…" in t and fmt == "F14")
    c["forbidden"] = int(fmt == "F05" or "don't show" in t or "do not" in t)
    c["recipient"] = int(bool(re.search(RECIPIENTS, t)))
    c["identity_callout"] = int(fmt in ("F07", "F08") or bool(re.search(IDENTITY, t)))
    c["store_surprise"] = int(fmt in ("F02", "F03", "F17") or bool(re.search(r"target|walmart|costco|ikea|petsmart|petco", t)))
    c["jk_twist"] = int("jk" in t or "just kidding" in t or "jk" in (body_hint or "").lower())
    c["social_proof"] = int(fmt in ("F03", "F15") or a in ("UNVEIL",) or "everyone" in t or "whole street" in t)
    c["gift_framing"] = int(fmt in ("F06", "F09") or "gift" in t)
    c["humor"] = int("😂" in (hook_text or "") or "🤣" in (hook_text or "") or fmt in ("F16", "F18"))
    c["transformation"] = int(fmt in ("F04", "F18", "F19"))
    c["envy"] = int(fmt == "F15" or "jealous" in t or "envy" in t or "jealous" in (caption or "").lower())
    c["urgency"] = int("run" in t and "walk" in t or "ends tonight" in t)
    c["countdown"] = int(fmt == "F01" or a == "TRAY_321")
    c["cozy_payoff"] = int(fmt in ("F06", "F12") or "cozy" in (body_hint or "").lower())
    c["squad"] = int(fmt == "F16" or "buy one" in t)
    return c

CATEGORY_MAP = {  # free-text category -> engine category
    "wearable": "wearable_gift", "robe": "wearable_gift", "blanket": "wearable_gift", "hoodie": "wearable_gift",
    "pajama": "wearable_gift", "slipper": "wearable_gift",
    "projector": "decor_light", "light": "decor_light", "lights": "decor_light", "curtain": "decor_light",
    "window": "decor_light", "tree": "decor_light", "fire": "decor_fire", "decor": "decor_light",
    "mug": "decor_mug", "melter": "decor_mug", "cup": "decor_mug",
    "mask": "accessory", "ski": "accessory", "carrier": "pet", "cat": "pet", "dog": "pet", "pet": "pet",
    "toy": "gadget", "laser": "gadget", "gadget": "gadget", "pillow": "home", "tray": "home",
}

def norm_category(s):
    s = (s or "").lower()
    if s in ("wearable_gift", "decor_light", "decor_fire", "decor_mug", "accessory", "pet", "gadget", "home"): return s
    if s == "decor": return "decor_light"
    if s == "accessory_skimask": return "accessory"
    for k, v in CATEGORY_MAP.items():
        if k in s: return v
    return "other"
