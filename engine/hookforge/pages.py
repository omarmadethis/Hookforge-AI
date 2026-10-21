"""Page registry (D41). private/pages.json (real, gitignored) - public example at config/pages.example.json.
Each page: code, platform(s), products, audience/market, daily_quota per product, posting windows (from posting_time),
variant_family (pages in the same family must never receive near-duplicate content), status.
"""
import os, json
import pandas as pd
from .config import REPO, POSTS_PER_PRODUCT_PER_DAY
from .worlds import WORLDS

PRIV = os.path.join(REPO, "private", "pages.json"); EXAMPLE = os.path.join(REPO, "config", "pages.example.json")

def bootstrap():
    """Seed the registry from the corpus (own pages x products) + posting windows. Real page names stay private."""
    c = pd.read_csv(f"{REPO}/private/corpus/corpus.csv", low_memory=False); o = c[c.source == "own"]
    pw = json.load(open(os.path.join(REPO, "learning", "posting_windows.json")))
    reg = {}
    for code, g in o.groupby("page_code"):
        prods = sorted({pk for pk, w in WORLDS.items() if set(w["corpus_products"]) & set(g["product"].dropna())})
        win = pw.get(code, pw.get("default", {}))
        reg[code] = dict(code=code, name=str(g.page.dropna().iloc[0]) if g.page.notna().any() else code,
                         platforms=sorted(set(g.platform.dropna())), products=prods, market="US", audience={pk: WORLDS[pk]["audience"] for pk in prods},
                         daily_quota={pk: POSTS_PER_PRODUCT_PER_DAY for pk in prods}, windows=dict(exploit=win.get("exploit"), explore=win.get("explore")),
                         variant_family=prods[0] if prods else code, status="active", autopost=False)
    os.makedirs(os.path.dirname(PRIV), exist_ok=True); json.dump(reg, open(PRIV, "w"), indent=1, ensure_ascii=False)
    os.makedirs(os.path.dirname(EXAMPLE), exist_ok=True)
    ex = {f"PAGE_{i+1}": {**{k: v for k, v in r.items() if k != "name"}, "code": f"PAGE_{i+1}"} for i, r in enumerate(reg.values())}
    json.dump(ex, open(EXAMPLE, "w"), indent=1, ensure_ascii=False)
    return reg

def load():
    return json.load(open(PRIV)) if os.path.exists(PRIV) else bootstrap()

def pages_for(product_key):
    return [p for p in load().values() if product_key in p["products"] and p["status"] == "active"]

def buffer_pages():
    """D94: Buffer-routed pages (config/buffer_routing.json) with their account/org/channel/lock state."""
    from . import routing
    return {k: routing.page(k) for k in routing.cfg()["pages"]}
