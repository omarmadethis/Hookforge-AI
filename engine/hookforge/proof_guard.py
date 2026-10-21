"""D68 proof guard: an audience/product profile may not ban a format/setting or emoji that has proven performance
in Omar's OWN data (>=50K own reel) unless Omar said so (profile key `omar_bans`: list of {item, said, date})."""
import csv, os, re, functools
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CORPUS = os.path.join(ROOT, "engine/backtest/data/corpus_public.csv")
HIT = 50000
# setting word -> own-reel archetypes / hook families that prove it
SETTING_PROOF = {"store": ("SHOCK_STORE", "PALLET", "store_named", "store_pallet"), "pallet": ("PALLET", "store_pallet")}

@functools.lru_cache()
def _own():
    return [r for r in csv.DictReader(open(CORPUS)) if r.get("source") == "own" and r.get("views")]

def corpus_products(audience_profile):
    """Own-corpus product names for an audience profile (via product_profiles/<key>.json)."""
    out = set()
    for k in audience_profile.get("product_keys") or []:
        f = os.path.join(ROOT, "product_profiles", k + ".json")
        if os.path.exists(f):
            import json; out |= set(json.load(open(f)).get("corpus_products", []))
    return out

def emoji_proof(e, categories=None):
    """Own >=50K reels using emoji e in the hook, limited to the same product categories (niche)."""
    e = e.replace("\ufe0f", "")
    hits = sorted((float(r["views"]), r["key"]) for r in _own() if (not categories or r["category"] in categories) and e in r["hook_text"].replace("\ufe0f", "") and float(r["views"]) >= HIT)
    return [f"own:{k} {int(v):,}" for v, k in reversed(hits)][:5]

def setting_proof(setting, products=None):
    keys = [t for w, t in SETTING_PROOF.items() if w in setting.lower()]
    tags = {x for t in keys for x in t}
    hits = sorted((float(r["views"]), r["key"]) for r in _own() if (not products or r["product"] in products) and (r["archetype"] in tags or r["hook_family"] in tags) and float(r["views"]) >= HIT)
    return [f"own:{k} {int(v):,}" for v, k in reversed(hits)][:5]

def niche_categories(audience_profile):
    prods = corpus_products(audience_profile)
    return {r["category"] for r in _own() if r["product"] in prods}

def omar_banned(profile, item):
    return any(b.get("item") == item for b in (profile.get("omar_bans") or []))

def audit(product_profile=None, audience_profile=None):
    """Return violations: bans that contradict own proven data without Omar's say-so."""
    out = []
    if product_profile:
        for s in product_profile.get("forbidden_settings", []):
            if omar_banned(product_profile, s): continue
            same = setting_proof(s, product_profile.get("corpus_products"))
            if same: out.append(dict(kind="setting", level="BLOCK", item=s, profile=product_profile.get("product_key"), evidence=same, note="proven on THIS product"))
            elif setting_proof(s): out.append(dict(kind="setting", level="WARN", item=s, profile=product_profile.get("product_key"), evidence=setting_proof(s), note="proven on another product; needs Omar's call"))
    return out
