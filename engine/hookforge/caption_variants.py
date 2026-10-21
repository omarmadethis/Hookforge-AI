"""D101 per-page caption variants for products routed to >= 2 pages (routing.py). Every variant is POC-backed:
(a) fb_caption.generate candidates (own corpus >= 50K first, then trending_captions batches), walked with rank=0..n;
(b) own-corpus PATTERN adaptations: the caption shape is proven by our own reels (evidence pulled live from
private/corpus/corpus.csv: count + peak views), the noun is swapped to the product's audience (audience/<slug>.yaml
caption_proof must match). Each must pass audience_fit.check_text (iOS emoji, banned words), use SAY never Comment, and
be original vs every sibling page: word-Jaccard <= variants.MAX_SIM (0.45) - the same rule variants.py uses for
captions. Output: learning/captions/page_variants.json {product: {page_key: {caption, hashtags, text, poc}}}.
publish.prepare_fb_all uses it when a page's plan has no caption_override."""
import os, re, json, datetime
import pandas as pd
from .config import REPO
from . import fb_caption as FC, variants, routing

OUT = os.path.join(REPO, "learning", "captions", "page_variants.json")
# (corpus regex proving the shape, product -> adapted line). The CTA line keeps the SAY keyword (F93).
ADAPT = {
 "trumpglow": [
   (r"(?i)do(?:n'?t|nt| not) show this to", "Don't show this to your liberal neighbor 🇺🇸😳"),
   (r"(?i)do(?:n'?t|nt| not) show this to", "DONT show this to a liberal 😎🦅"),
   (r"(?i)who needs one", "Who needs one for the front porch? 🇺🇸"),
   (r"(?i)who would (?:wear|get)", "Who would put this on their garage door? 🦅🇺🇸"),
   (r"(?i)it'?s heated|it'?s (?:real|here)", "It's real.. and it's on my house 🇺🇸"),
 ],
}
CTA = {"trumpglow": 'SAY "VOTE" if you like Trump 🇺🇸'}

def _own():
    c = pd.read_csv(os.path.join(REPO, "private", "corpus", "corpus.csv"), low_memory=False, usecols=["source", "page", "views", "hook_text", "caption"])
    o = c[c.source == "own"].copy(); o["txt"] = o.hook_text.fillna("") + " | " + o.caption.fillna(""); return o

def _evidence(rx, own):
    m = own[own.txt.str.contains(rx, regex=True)]
    if not len(m): return None
    top = m.sort_values("views", ascending=False).iloc[0]
    return f"own corpus: {len(m)} reels match /{rx}/, peak {int(top.views):,} ({top.page}: {str(top.hook_text)[:50]!r})"

def _orig(line, chosen):
    return all(variants._jac(line, c) <= variants.MAX_SIM for c in chosen)

def candidates(product):
    out = []
    for r in range(12):
        try: g = FC.generate(product, {}, platform="facebook", rank=r)
        except (ValueError, KeyError): break
        out.append(dict(caption=g["caption"], hashtags=g["hashtags"], poc=g["poc"], src="fb_caption"))
    own = _own(); slug = FC.PRODUCTS[product]["aud"]
    for rx, line in ADAPT.get(product, []):
        ev = _evidence(rx, own)
        if not ev: continue
        full = line + (" " + CTA[product] if product in CTA else "")
        try: g = FC.generate(product, {"caption_override": full}, platform="facebook")
        except ValueError: continue
        out.append(dict(caption=g["caption"], hashtags=g["hashtags"], poc=ev + f"; audience/{slug}.yaml caption_proof", src="own_pattern"))
    return out

def build(products=None, write=True):
    res = {}
    multi = {p: ks for p, ks in routing.cfg()["products"].items() if len(ks) >= 2}
    for p in (products or multi):
        pages = multi.get(p) or routing.cfg()["products"].get(p, [])
        chosen, per = [], {}
        cands = candidates(p)
        for pk in pages:
            c = next((c for c in cands if c["caption"] not in [x["caption"] for x in per.values()] and _orig(c["caption"], chosen)), None)
            if c is None: per[pk] = dict(blocked="no original POC-backed caption left"); continue
            chosen.append(c["caption"]); per[pk] = dict(c, text=c["caption"] + ("\n" + " ".join(c["hashtags"]) if c["hashtags"] else ""))
        res[p] = dict(pages=per, n_candidates=len(cands), built=datetime.datetime.now().isoformat(timespec="seconds"))
    if write:
        os.makedirs(os.path.dirname(OUT), exist_ok=True); json.dump(res, open(OUT, "w"), indent=1, ensure_ascii=False)
    return res

PINNED = {   # D123: chosen from winning captions, survives rebuilds
 ("purrventure_carrier", "purrventures2_fb"): dict(
    caption='Finally a way for kitties to explore outside safely! 🐈 SAY "PURR" if you want one!',
    hashtags=["#cat", "#catmom", "#catlover"],
    poc="TikTok 7694841614191070477 @juan.webdaily.find 52,400 plays (same mesh cat-ball product, hook verbatim; research/reference_library) + POC-PV-CAP1 SAY \"PURR\" CTA (RollyMew 20.8M)",
    src="pinned D123"),
}

def for_page(product, page_key):
    if (product, page_key) in PINNED:
        v = dict(PINNED[(product, page_key)]); v["text"] = v["caption"] + "\n" + " ".join(v["hashtags"]); return v
    if not os.path.exists(OUT): return None
    v = json.load(open(OUT)).get(product, {}).get("pages", {}).get(page_key)
    return v if v and not v.get("blocked") else None
