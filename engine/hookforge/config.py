"""Hookforge v3 constants. Standing decisions live here so every module enforces them.

Nothing in this file is private: no IDs, no sales figures.
"""
import os

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# --- Standing decision 1 (D32, Omar override): realism suffix, verbatim, ends EVERY prompt: video AND start-frame stills ---
IPHONE12_SUFFIX = (
    "shot on iphone 12, no warm lighting, no blur, nothing cinematic, make it look as organic "
    "as possible, remove the caption and the emojis. when recreating do not make the video grainy "
    "or sharp in any way, remake it as if it was freshly refilmed 4k iphone 12 footage."
)

# Start-frame stills (D32 supersedes D17): positive recipe + the verbatim iPhone 12 suffix.
# Still prompt = "iPhone photo of <scene>. Sharp, clean, realistic phone photo. " + IPHONE12_SUFFIX
STILL_PREFIX = "iPhone photo of "
STILL_SUFFIX = "Sharp, clean, realistic phone photo."

def still_prompt(scene):
    scene = scene.strip()
    if not scene.lower().startswith("iphone photo"): scene = STILL_PREFIX + scene[0].lower() + scene[1:]
    if STILL_SUFFIX.lower() not in scene.lower(): scene = scene.rstrip(". ") + ". " + STILL_SUFFIX
    return ensure_suffix(scene)

def ensure_suffix(prompt):
    p = prompt.rstrip()
    return p if p.endswith(IPHONE12_SUFFIX) else (p + "\n\n" + IPHONE12_SUFFIX)

# --- Standing decision 2: resolution + packing ---
MODEL_VIDEO = "seedance_2_5"          # Seedance only (Omar: no Kling)
MODEL_STILL = "gpt_image_2"           # GPT Image 2 only for start frames
HOOK_RES = "720p"                     # D181 (Omar 2026-10-20 8:02 PM PT): hooks are 720p, permanent; replaces 1080p
BODY_RES = "720p"                     # every other generation
GEN_SECONDS = 4                       # Seedance 2.5 minimum
PACK_CUT_DEFAULT = 2.0                # hard cut inside a packed body gen
PACK_CUT_WINDOW = (1.5, 2.5)          # allowed cut point ("~2 s")
SHOTS_PER_BODY_GEN = 2

# Credit costs are NOT known from data on disk. Fill these from the Higgsfield pricing page
# before autonomous runs; the planner prints estimates with these placeholders.
# Inferred 2026-10-18 from the read-only Higgsfield transaction history (new account): Seedance 2.5 spends of 28 (x8, batches of 4 =
# body 720p 4 s), 64 (x6 = 1080p 4 s), 80 (1080p 5 s), 128 (1080p 8 s) => ~7 cr/s at 720p, ~16 cr/s at 1080p; GPT Image 2.0 = 1/image (D72; the old 6.5 figure was wrong).
# Reference-video (recreate) gens may bill differently - confirm on the first live run.
# MR60 (2026-10-23): default video model is Kling 4.0 (kling4_0), 1080p 9:16. ESTIMATE ~1 cr/s, verified only against ONE data point (Omar's Barn Glow afters gen: 10 cr for 10 s). Confirm from `transactions` after each gen.
VIDEO_MODEL_DEFAULT, VIDEO_RES_DEFAULT, KLING_CR_PER_S_EST = "kling4_0", "1080p", 1.0
CREDITS = {"hook_1080p_4s": 64, "body_720p_4s": 28, "still_gpt_image_2": 1.0, "per_s_720p": 7, "per_s_1080p": 16,
           "source": "inferred from Higgsfield transactions 2026-10-18 (read-only)"}
# --- LIVE generation gate (Omar 2026-10-18 10:35 PM PT): DISABLED. Nothing is submitted unless enabled=True AND a valid, unexpired,
# single-use approval file learning/approvals/<run_id>.json (approved_by Omar, plan sha256, gen ids, account, credit cap) exists. See FIRST_LIVE_RUN.md.
LIVE = {"enabled": False, "account": "user-Higgsfield--new-account", "approvals_dir": "learning/approvals", "runs_dir": "out/live",
        "cost_tolerance": 0.5, "still": {"model": "gpt_image_2", "resolution": "2k", "quality": "high", "aspect_ratio": "9:16"},
        "video": {"mode": "omni_reference", "aspect_ratio": "9:16", "generate_audio": True},   # D63: natural clip sound kept (fake SFX banned in prompt + QA audio check); song added in CapCut
        "costs_confirmed": "get_cost preflight 2026-10-18 ~10:55 PM PT on new-account: seedance_2_5 1080p 4s = 64, 720p 4s = 28, 1080p 5s = 80; gpt_image_2 2k high = 6.5, 1k high = 3.5"}
# D140: gpt_image_2 is billed per image BY TIER (2026-10-20 transactions: 2k high = 6.5 each, matching get_cost; 2026-10-19's
# 1.0/image was the 1k-medium tier). The engine prices stills at the tier LIVE['still'] actually requests.
STILL_TIER = {("1k", "medium"): 1.0, ("1k", "high"): 3.5, ("2k", "high"): 6.5}
CREDITS["still_gpt_image_2"] = STILL_TIER.get((LIVE["still"]["resolution"], LIVE["still"]["quality"]), 6.5)
CREDIT_BUDGET_PER_VIDEO = 175         # Omar's ceiling (typ. 100-175; variants 100 max). ALWAYS print cost per video.
CREDIT_BUDGET_VARIANT = 100
# D33 (Omar override, supersedes zero-re-roll D18): auto re-roll ONLY on an ABSURD failure with high confidence.
REROLL = {
    "auto": True, "min_confidence": 0.9, "max_auto_rerolls_per_shot": 1,
    "absurd_failures": [   # any ONE, certain => re-roll (logged with reason + credit cost)
        "product_missing", "product_deformed", "wrong_product", "wrong_colour", "mangled_person_or_limbs",
        "scene_unrelated", "hard_cut_missing_or_broken", "hook_unusable", "wrong_aspect_ratio"],
    "never_reroll": [      # minor: ship and note in learning log
        "background_logo", "weird_text_on_display_or_signage", "small_artifact", "slight_lighting_issue"],
}
MAX_GEN_SECONDS = 5                   # D25: hooks/gens 5 s or less (Omar: "that can be done in 5 tops")
HOOK_MAX_S = 5.0

# --- Standing decision 3-5: copy rules ---
CTA_VERB = "SAY"                       # never "COMMENT" (FB engagement-bait demotion)
BANNED_CTA_WORDS = ["comment", "tag ", "tag your", "vote", "share if", "like if"]
JK_FLIPS = ["JK, We make them🎅🎄", "JK, Get in bio", "Jk we make them:)"]

# --- Decision 7: export spec (FB serves 1440/2560 only after watch time; upload 4K) ---
EXPORT = {
    "width": 2160, "height": 3840, "fps": 30,
    "vcodec": "libx265", "vbitrate": "30M", "pix_fmt": "yuv420p",
    "acodec": "aac", "abitrate": "192k", "ar": 44100,
    "lufs": -14.0, "true_peak": -1.0,
}

# --- Edit spec (body report, winner medians) ---
EDIT = {
    "length_target": 13.26, "length_ok": (12.7, 13.8), "length_soft": (11.5, 15.5),
    "hook_cut": (2.5, 4.1), "activation_frac": (0.55, 0.75), "payoff_start_frac": (0.78, 0.90),
    "payoff_min_s": 1.3, "shots": (5, 9), "max_prep_shot_s": 2.2, "max_prep_total_s": 4.5,
}
TEXT = {
    "font_candidates": [
        os.path.join(REPO, "assets", "fonts", "TikTokSans.ttf"),
        "/usr/share/fonts/truetype/sand-box/google/Montserrat/Montserrat-VariableFont_wght.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "emoji_font": "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
    "center_y_frac": 0.19,            # CapCut drafts (n=110): transform.y median 0.62 -> (1-0.62)/2 = 19 % from top; IQR 17-22 %
    "center_y_ok": (0.10, 0.25),      # measured on exports: 13-20 %; drafts IQR y 0.56-0.66
    "capcut_y": 0.62, "capcut_font_size": 15, "capcut_stroke": 0.09,
    "height_frac": 0.03,              # line height ~2.4-4 % of frame height
    "max_words": 9, "stroke_frac": 0.12,
}

# Posting windows (PT). Views evidence: 18:00-04:00 (x3.4, p=0.03). Sales evidence: post 22:00-08:00
# so the first-day peak lands in the 6 AM-7 PM PT buying window. Intersection used as default.
POST_WINDOW_PT = {"primary": (22, 2), "secondary": (18, 22), "allowed": (18, 8)}
POSTS_PER_PRODUCT_PER_DAY = 5
INNOVATION_SHARE = 0.20               # explore budget (Omar steering 2026-10-18)

# Hit definition used by learning + bandit: page-relative so new pages are comparable
HIT_ABS_VIEWS = 50_000


# --- Freshness / recency weighting (D28 FINAL, Omar 2026-10-18 8:32 PM PT). ONE knob: RECENCY ---
# Applies ONLY to EXTERNAL reels (research reference library tiers, external/competitor reels).
# OWN data (all our pages' reels, CapCut drafts, prompts, Insights, Shopify) = FULL weight regardless of age.
# weight(age) = 1 within full_days; then exp(-(age - full_days) / tau_days), floored at prior_floor (90+ d = weak prior).
RECENCY = {"full_days": 14, "tau_days": 7.0, "prior_days": 90, "prior_floor": 0.05}
OWN_SOURCES = {"own", "capcut", "prompt", "insights", "shopify", "library"}   # library = our finished videos
EXTERNAL_SOURCES = {"external", "research", "reference", "ref_index", "ref_archive", "ref_near_miss"}

# Library inclusion rules (D34): '14d_1m' follows RECENCY; '90d_20m' (mega viral, 20M+ within 90 d) is exempt from decay.
INCLUSION_WEIGHT = {"14d_1m": "recency", "90d_20m": 0.95}

def recency_weight(age_days, source="external", cfg=None, inclusion_rule=None):
    """Evidence weight. Own data -> 1.0 always. External 90d_20m -> INCLUSION_WEIGHT (near-full, no decay).
    External 14d_1m / unspecified -> 14-day full weight, steep decay, weak-prior floor."""
    import math
    c = cfg or RECENCY
    if source in OWN_SOURCES: return 1.0
    w = INCLUSION_WEIGHT.get(inclusion_rule or "", "recency")
    if w != "recency": return float(w)
    if age_days is None: return 1.0
    a = max(0.0, float(age_days))
    if a <= c["full_days"]: return 1.0
    return max(math.exp(-(a - c["full_days"]) / c["tau_days"]), c["prior_floor"])

def freshness_label(age_days, cfg=None):
    c = cfg or RECENCY
    if age_days is None: return "unknown"
    return "fresh" if age_days <= c["full_days"] else ("aging" if age_days < c["prior_days"] else "prior-only")

# --- Content safety (D27): never cast by race/ethnicity; strip from reused prompts; block in outputs ---
import re as _re
ETHNICITY_RX = _re.compile(r"\b(caucasian|white|black|asian|indian|latino|latina|hispanic|african[- ]american|middle[- ]eastern|arab)\s+"
                           r"(?=(people|person|man|men|woman|women|guy|guys|girl|girls|boy|boys|family|families|couple|character|characters|kid|kids|mom|dad|lady|ladies|talent|actor|actors|employee|employees|staff|shopper|shoppers)\b)", _re.I)
_ETH = r"(caucasian|white|black|asian|indian|indians|latino|latina|hispanic|african[- ]american|middle[- ]eastern|arab)"
_INSTR = _re.compile(r"\b(only|instead of|no|not|never|make (him|her|them)|use|cast|low roi)\b", _re.I)

def sanitize_casting(text):
    """Strip ethnicity casting: drop sentences that instruct casting by race; delete descriptors before person nouns."""
    if not isinstance(text, str): return text
    out = []
    parts = _re.split(r"((?<=[.!?])\s+|\n+)", text)          # keep separators: never split "2.1" or drop newlines
    for i, sent in enumerate(parts):
        if i % 2 == 1: out.append(sent); continue
        if _re.search(r"\bcaucasian\b", sent, _re.I) and _INSTR.search(sent) and not ETHNICITY_RX.search(sent): continue
        if _re.search(r"\b" + _ETH + r"\b", sent, _re.I) and _INSTR.search(sent) and _re.search(r"\b(people|characters?|only|instead|roi|make (him|her|them)|indians?|blacks?)\b", sent, _re.I) \
           and not _re.search(r"\b(snow|light|lights|wall|background|shirt|robe|box|text|color|colour|leds?)\b", sent, _re.I):
            continue
        out.append(ETHNICITY_RX.sub("", sent))
    t = "".join(out)
    t = _re.sub(r"\bcaucasian\s+(american\s+)?", "", t, flags=_re.I)   # never benign in a prompt
    return _re.sub(r"[ \t]{2,}", " ", t).strip()

def casting_violations(text):
    return [m.group(0) for m in ETHNICITY_RX.finditer(text or "")] + [m.group(1) for m in _re.finditer(r"\b(caucasian|only white|instead of black|race-based)\b", text or "", _re.I)]

# Race-targeted hooks are excluded (parent steering 2026-10-18 10:50 PM PT, e.g. "Do NOT show this to a Black Mom"): neutral recipient framing only.
RACE_HOOK_RX = _re.compile(r"\b" + _ETH + r"s?\s+(mom|moms|mum|mother|dad|dads|wife|wives|husband|girlfriend|boyfriend|grandma|grandpa|family|families|people|"
                           r"women|men|girls|guys|kids|aunt|aunties|uncle|friend|friends|lady|ladies|household)\b", _re.I)
def race_targeted(text): return bool(RACE_HOOK_RX.search(text or ""))
