"""US/tier-1 visual cue snippets from audience/visual_cues.md (hypothesis-level geo effect; EXP-AUD-07).
Rules from that file: cues are background set dressing inside the scene text (before the suffix), max 2 per shot + flag,
product world first (D37), no race/ethnicity (D27), no logos (D26)."""
import os, re
from .config import REPO
P = os.path.join(REPO, "audience", "visual_cues.md")
WORLD_KEYS = {"grinch_robe": ["sectional couch", "thermostat"], "merryfire": ["sectional couch", "thermostat"],
              "grinchmelt_mug": ["open-plan American kitchen", "thermostat"], "merryglow_lights": ["sectional couch", "cul-de-sac"],
              "jollyglow_curtain": ["suburban two-story house", "cul-de-sac"], "purrventure_carrier": ["sectional couch", "thermostat"],
              "brickhood_mask": ["ski lodge flagpole", "snowboard"]}   # slopes: only the ski flag cues (replace the generic flag line)
PATIO_KEYS = ["backyard patio", "cul-de-sac"]

def snippets():
    if not os.path.exists(P): return []
    out = []
    for line in open(P, encoding="utf-8").read().splitlines():
        if line.startswith("- "): out += [x for x in re.findall(r"`([^`]+)`", line) if " " in x and len(x) > 15 and "." not in x.split()[0]]
    return out

def for_world(product_key, setting="", k=2):
    sn = snippets(); keys = PATIO_KEYS if "patio" in setting.lower() else WORLD_KEYS.get(product_key, [])
    out = [s for key in keys for s in sn if key.lower() in s.lower() and ("flag" not in s.lower() or product_key == "brickhood_mask")]
    return list(dict.fromkeys(out))[:k]
