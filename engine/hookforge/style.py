"""Style layer (style/ workstream, accepted 2026-10-18): text scale by line length, emoji rules, shot-grammar checks.
Hard rules: Brick Hood hooks only on chairlift / slope / snowmobile. The rest is advisory (D35)."""
import os, re, json
from .config import REPO

STYLE = os.path.join(REPO, "style")
EMOJI_RX = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\u2300-\u23FF]")

def text_scale(text):
    t = EMOJI_RX.sub("", text).replace("\uFE0F", "").strip()
    if re.fullmatch(r"(?i)vs\W*", t): return 1.2
    n = len(t)
    return 1.0 if n <= 17 else 0.88 if n <= 22 else 0.76 if n <= 28 else 0.72

def emoji_rules():
    p = os.path.join(STYLE, "emoji_rules.json")
    return json.load(open(p)) if os.path.exists(p) else {}

def emoji_problems(cards, proven_own=False):
    r = emoji_rules(); out = []
    mx = r.get("global", {}).get("hook_emoji_count", {}).get("max", 2)
    if cards:
        h = cards[0]["text"]; n = len(EMOJI_RX.findall(h))
        if n > mx: out.append(f"{'WARN' if proven_own else 'FIX'} hook card has {n} emojis (max {mx}; external 3+ emojis 1/7 hit)"
                              + (" - kept: verbatim own proven hook" if proven_own else ""))
        if "🎄" in h and not h.lower().startswith("christmas"): out.append("WARN 🎄 as hook emoji: ours CapCut-truth 0/4 - use it on payoff cards/captions")
    return out

HANDS_RX = re.compile(r"\bPOV\b|\bhands?\b|over-the-shoulder|high angle|high-angle", re.I)
FACE_RX = re.compile(r"face to camera|to camera, portrait|talks? to (the )?camera|talk-to-camera", re.I)
COVERED_RX = re.compile(r"white cloth|sheer \w+ cloth|thin white cloth|under (a|the) (sheer |thin )?(\w+ )?cloth|covered with|cloth off|drape[sd]?\b|covered tray|lid closed|baking tray|muffin tin|on (it|the tray) like a (freshly )?baked loaf", re.I)
HANDLE_RX = re.compile(r"\b(unbox|lift|box|puts?|pulls?|opens?|hold|holds|set|place|placing|install|hanging|adjust|wrap|pour|plug)", re.I)
MOVE_RX = re.compile(r"\b(ski|skiing|riding|walk|walks|running|jump)", re.I)
SKI_HOOK_RX = re.compile(r"chairlift|ski lift|\blift\b|gondola|slope|snowmobile", re.I)

def ensure_hands_on(shots, product_word):
    """PS12: >=2 hands-on-product body shots (POV / over-the-shoulder / high angle). Rewrites the first eligible shots."""
    n = sum(1 for s in shots if HANDS_RX.search(s[3]))
    for s in shots[1:]:
        if n >= 2: break
        if not HANDS_RX.search(s[3]) and not FACE_RX.search(s[3]) and HANDLE_RX.search(s[3]) and not MOVE_RX.search(s[3]):
            s[3] = f"high-angle POV, hands on the {product_word}: " + s[3]; n += 1
    return shots

def shot_problems(plan, profile):
    out = []; descs = [s["desc"] for s in plan["shots"]]
    hands = sum(1 for d in descs if HANDS_RX.search(d)); faces = sum(1 for d in descs if FACE_RX.search(d))
    if hands < 2: out.append(f"FIX only {hands} hands-on-product shots (PS12 needs >=2)")
    if faces > 1: out.append(f"FIX {faces} face-to-camera demo shots (PS19 cap 1)")
    hook = plan["gens"][0]["prompt"] + " " + plan["gens"][0]["start_frame"]["prompt"]
    # Covered-reveal hooks (cloth / tray) are ALLOWED as normal hooks - Omar override 2026-10-18 21:55 PT (D52): our coded data
    # is missing their winners; the style team is re-coding them. No block, no experiment-only restriction.
    if profile["product_key"] == "brickhood_mask" and not SKI_HOOK_RX.search(hook):
        out.append("BLOCK Brick Hood hook must be on a chairlift, slope or snowmobile")
    return out
