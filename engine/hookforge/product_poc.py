"""D84 per-product POC defaults (config/poc_defaults.json). prepare() runs before the planner: syncs the product
profile with the POC world/body (idempotent) and sets the proven format. apply() runs after it: replaces hook/cards,
post caption and song with the cited POC picks, then re-runs the audience-fit stage so the gates judge the final plan.
Omar rules enforced here: F45 no 'Get yours'/{url} on screen, F86 emoji by POC, no Christmas songs off-season niches."""
import json, os, re
from .config import REPO, ensure_suffix
CFG = os.path.join(REPO, "config", "poc_defaults.json")

def load(pk=None):
    d = json.load(open(CFG)) if os.path.exists(CFG) else {}
    return d.get(pk) if pk else d

def prepare(brief, override=None):
    from . import profiles
    pk = profiles.resolve(brief); d = load(pk) if pk else None
    if not d: return override
    p = os.path.join(profiles.PDIR, f"{pk}.json")
    prof = profiles.load(pk); want = dict(d.get("world") or {}); want.pop("why", None)
    if d.get("body_override"): want["body_override"] = {k: list(v) for k, v in d["body_override"].items()}
    if any(prof.get(k) != v for k, v in want.items()):
        prof.update(want); json.dump(prof, open(p, "w"), indent=1, ensure_ascii=False)
    if d.get("adaptation") and d.get("format"):          # world-adapted hook for the proven format (registered at runtime)
        from .worlds import ADAPTATIONS
        ADAPTATIONS[(d["format"], pk)] = dict(d["adaptation"])
    ov = dict(override or {})
    if d.get("format") and not ov.get("format") and not re.search(r"\bF\d\d\b", brief): ov["format"] = d["format"]
    return ov

def apply(out):
    pk = (out.get("product") or {}).get("key"); d = load(pk) if pk else None
    if not d or not out.get("gens"): return out
    if d.get("cards"):
        cards = d["cards"]; tc = out["text_cards"]
        out["hook"] = dict(text=cards[0], tag="P", cards=cards, why=d["cards_why"] + " (views 22M/20.8M, proven)")
        if len(tc) == len(cards):
            for c, t in zip(tc, cards): c["text"] = t
        else: out.setdefault("prompt_checks", []).append(f"POC cards {cards} need a {len(cards)}-card format, got {len(tc)}")
    if d.get("caption"):
        out["caption"] = dict(d["caption"])
    if d.get("music"):
        m = d["music"][0]
        out["music"] = dict(pick=dict(song=m["song"], version=m["version"], offset_s=m["offset_s"], energy=m["energy"], region="US", score=9, why=m["why"], poc=m["poc"]),
                            alternatives=[dict(song=x["song"], version=x["version"], offset_s=x["offset_s"], why=x["why"]) for x in d["music"][1:]],
                            rejected=[dict(song=r["song"], reason=r["reason"]) for r in out["music"].get("rejected", [])],
                            audience_fit_song=dict(song=m["song"], version=m["version"], genre=m["genre"], in_point=m["offset_s"], tier="c",
                                                   evidence=m["evidence"], in_point_evidence=m["in_point_evidence"]))
    for g in out["gens"]:   # D32: suffix must END every prompt (d75 motion rules append after it)
        g["prompt"] = ensure_suffix(g["prompt"]); g["start_frame"]["prompt"] = ensure_suffix(g["start_frame"]["prompt"])
    from .planner import BANNED_CTA_WORDS
    out["banned_cta_found"] = [w for w in BANNED_CTA_WORDS if w in (out["caption"]["text"] + " ".join(c["text"] for c in out["text_cards"])).lower()]
    from . import audience_fit
    out["prompt_checks"] = [c for c in out["prompt_checks"] if not c.startswith("AUDIENCE-FIT")]
    out["audience_fit"], rows = audience_fit.lint_rows(out)
    out["prompt_checks"] += [f"AUDIENCE-FIT {r['rule']}: {r['text']}" for r in rows]
    out["poc_defaults"] = dict(source="config/poc_defaults.json", format_why=d.get("format_why"))
    return out
