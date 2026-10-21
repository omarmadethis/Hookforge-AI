"""Plug-in layer for teammate workstreams (D39). Each loader returns the teammate file when it exists AND passes
its schema check, else the engine default (and records which one was used in the plan's provenance block).
  style/capcut_text_preset.json  -> text style for CapCut export + ffmpeg animatic
  style/emojis.(json|csv)        -> emoji choice per product/format/mood
  style/shot_grammar.md|json     -> shot grammar (angles, motion, framing) appended to shot descriptions
  psychology/psych_codebook.csv  -> psych codes for the backtester + plan tagging
"""
import os, json, csv
from .config import REPO, TEXT

def _p(*a): return os.path.join(REPO, *a)

DEFAULT_TEXT = dict(source="engine default (config.TEXT, CapCut drafts n=110)", font="TikTok Sans / system", size=TEXT["capcut_font_size"],
                    stroke=TEXT["capcut_stroke"], color="#FFFFFF", stroke_color="#000000", capcut_y=TEXT["capcut_y"],
                    center_y_frac=TEXT["center_y_frac"], animation_in=None, animation_out=None)
DEFAULT_EMOJI = {"default": ["😳", "❄️", "🎄"], "cozy": ["🥹", "❄️", "☺️"], "hype": ["😂", "😳", "🔥"], "ski": ["😂"], "store": ["😳", "🎄", "❄️"]}

def text_preset():
    p = _p("style", "capcut_text_preset.json")
    if os.path.exists(p):
        try:
            d = json.load(open(p))
            if "default" in d and "font_size" in d["default"]:   # teammate schema (style/ forensics, version draft)
                dd = d["default"]; y = dd.get("transform_y", TEXT["capcut_y"])
                return {**DEFAULT_TEXT, "source": f"style/capcut_text_preset.json (version {d.get('version')})", "size": dd["font_size"],
                        "stroke": dd.get("stroke_width", TEXT["capcut_stroke"]), "capcut_y": y, "center_y_frac": round((1 - y) / 2, 3),
                        "color": dd.get("fill", "#ffffff"), "stroke_color": dd.get("stroke_color", "#000000"), "scale": dd.get("scale"),
                        "font_render": d.get("render", {}).get("font_file_box")}
            if all(k in d for k in ("size", "stroke")) and ("capcut_y" in d or "transform_y" in d):
                d.setdefault("capcut_y", d.get("transform_y")); d["source"] = "style/capcut_text_preset.json"; return {**DEFAULT_TEXT, **d}
        except Exception: pass
    return DEFAULT_TEXT

def emojis(mood_keys):
    for ext in ("json", "csv"):
        p = _p("style", f"emojis.{ext}")
        if os.path.exists(p):
            try:
                d = json.load(open(p)) if ext == "json" else {r["key"]: r["emojis"].split() for r in csv.DictReader(open(p))}
                for k in mood_keys:
                    if k in d: return d[k], f"style/emojis.{ext}"
            except Exception: pass
    for k in mood_keys:
        if k in DEFAULT_EMOJI: return DEFAULT_EMOJI[k], "engine default"
    return DEFAULT_EMOJI["default"], "engine default"

def shot_grammar():
    for name in ("shot_grammar.json", "shot_grammar.md"):
        p = _p("style", name)
        if os.path.exists(p): return open(p).read(), f"style/{name}"
    return None, "none (body shot descriptions from bodies.py)"

def psych_codebook():
    p = _p("psychology", "psych_codebook.csv")
    if os.path.exists(p):
        rows = list(csv.DictReader(open(p)))
        if rows and "code" in rows[0]: return rows, "psychology/psych_codebook.csv"
    from .taxonomy import PSYCH
    return [{"code": c} for c in PSYCH], "engine default (taxonomy.PSYCH)"

def provenance():
    return dict(text_style=text_preset()["source"], emojis=emojis(["default"])[1], shot_grammar=shot_grammar()[1], psych=psych_codebook()[1])

# ---- audience/ (tier-1 market targeting) and voice/ (customer comment intelligence) - D41
def _csv(*parts):
    p = _p(*parts)
    return (list(csv.DictReader(open(p, encoding="utf-8"))), "/".join(parts)) if os.path.exists(p) else ([], None)

def audience():
    """audience/lexicon.csv (term,market,use|avoid,replacement), audience_rules.csv (rule_id,market,check,pattern,severity),
    visual_cues.md, audio_regions.md -> dict; empty lists if not landed yet."""
    lex, s1 = _csv("audience", "lexicon.csv"); rules, s2 = _csv("audience", "audience_rules.csv")
    vis = open(_p("audience", "visual_cues.md")).read() if os.path.exists(_p("audience", "visual_cues.md")) else None
    aud = open(_p("audience", "audio_regions.md")).read() if os.path.exists(_p("audience", "audio_regions.md")) else None
    return dict(lexicon=lex, rules=rules, visual_cues=vis, audio_regions=aud, source=[x for x in (s1, s2) if x] or "not landed")

def voice():   # REFERENCE DATA ONLY (Omar 2026-10-18 21:48) - not used by planner/QA
    """voice/voice_rules.csv (rule_id,product,type=hook|caption|objection|avoid,text,evidence) + INSIGHTS.md."""
    rules, s = _csv("voice", "voice_rules.csv")
    ins = open(_p("voice", "INSIGHTS.md")).read() if os.path.exists(_p("voice", "INSIGHTS.md")) else None
    return dict(rules=rules, insights=ins, source=s or "not landed")

def audience_checks(texts, market="US"):
    """Apply lexicon 'avoid' terms + regex audience_rules to on-screen text/captions. Returns problems (severity, msg)."""
    import re as _re
    a = audience(); out = []
    blob = " \n".join(texts).lower()
    for r in a["lexicon"]:
        if r.get("use", "").lower() == "avoid" and r.get("market", market) in (market, "ALL") and r.get("term", "").lower() in blob:
            out.append(("FIX", f"audience lexicon: avoid '{r['term']}' for {market}" + (f" -> '{r.get('replacement')}'" if r.get("replacement") else "")))
    for r in a["rules"]:
        if r.get("pattern") and r.get("market", market) in (market, "ALL"):
            try:
                if _re.search(r["pattern"], blob, _re.I): out.append((r.get("severity", "FIX"), f"audience rule {r.get('rule_id')}: {r.get('check')}"))
            except _re.error: pass
    return out

def voice_for(product_key):
    v = voice(); return [r for r in v["rules"] if r.get("product") in (product_key, "ALL", "")]

def provenance():
    return dict(text_style=text_preset()["source"], emojis=emojis(["default"])[1], shot_grammar=shot_grammar()[1], psych=psych_codebook()[1],
                audience=audience()["source"], voice=voice()["source"])
