"""Mistake vs preference classifier (rule-based v0; LLM-assisted later). Only 'mistake' with conf>=0.8 is globally eligible."""
MISTAKE = {"physics": ["clip", "phasing", "through the", "floating", "extra paw", "extra finger", "melt"],
  "product": ["wrong product", "deformed", "off-model product", "logo wrong", "doesn't match the product"],
  "cast": ["wrong cat", "different person", "off-ref", "face changed"],
  "metadata": ["c2pa", "metadata", "ai tag", "lavf", "encoder"],
  "edit_defect": ["weird cut", "splice", "broken cut", "loop", "black frame", "desync", "out of sync", "cut off dialogue"],
  "ai_look": ["looks ai", "ai slop", "plastic", "grain", "oversharpen"],
  "pipeline": ["crash", "nan", "gate missed", "didn't catch", "over budget", "overrun", "missing reference"]}
PREF = ["pacing", "faster", "slower", "emoji", "font", "song", "music choice", "tone", "use women", "use a man", "format",
        "structure", "caption style", "i prefer", "i like", "vibe", "cta", "longer", "shorter", "linger"]
def classify(text: str):
    t = text.lower(); m = [c for c, ks in MISTAKE.items() if any(k in t for k in ks)]; p = sum(k in t for k in PREF)
    if m and not p: return {"cls": "mistake", "category": m[0], "conf": 0.9}
    if m and p: return {"cls": "local", "category": m[0], "conf": 0.5}  # ambiguous -> local
    return {"cls": "preference", "category": "style", "conf": 0.8 if p else 0.4}
def globally_eligible(c): return c["cls"] == "mistake" and c["conf"] >= 0.8
