"""Product profiles (D37). build() writes product_profiles/<product>.json = worlds.WORLDS (curated world: settings,
energy, audience, actions, forbidden settings) + evidence derived from our posted reels / CapCut drafts:
proven formats (own views per format), proven music (music_library), proven captions and hook lines.
URLs, page ids and sales are NOT written (public-safe); views are kept as relative evidence.
"""
import os, re, json
import pandas as pd
from .config import REPO, HIT_ABS_VIEWS
from .worlds import WORLDS
from . import music

PDIR = os.path.join(REPO, "product_profiles")
URL_RX = re.compile(r"https?://\S+|\b[\w.-]+\.(?:myshopify\.com|com)\S*", re.I)

def _clean_caption(s):
    s = URL_RX.sub("{url}", str(s)); s = re.sub(r"#\w+", "", s); return re.sub(r"\s+", " ", s).strip()

def build():
    os.makedirs(PDIR, exist_ok=True)
    c = __import__("hookforge.reels_db", fromlist=["x"]).load_reels()[0]
    own = c[(c.source == "own") & c.views.notna()]
    lib = music.load()
    out = {}
    for pk, w in WORLDS.items():
        g = own[own["product"].isin(w["corpus_products"])]
        fm = []
        for f, gg in g.groupby("format"):
            fm.append(dict(format=f, n=len(gg), hits=int((gg.views >= HIT_ABS_VIEWS).sum()), median_views=int(gg.views.median()),
                           best_views=int(gg.views.max()), reels=sorted(gg.key.tolist())))
        fm.sort(key=lambda d: (-d["hits"], -d["best_views"]))
        mus = []
        for r in lib.itertuples():
            for x in str(r.proven_on).split(";"):
                if x.startswith(pk + ":"):
                    v = int(x.split(":")[1].split("(")[0]); mus.append(dict(song=r.song, version=r.version, offset_s=r.capcut_offset_s, energy=int(r.energy), best_views=v, formats=x.split("(")[1].rstrip(")")))
        mus.sort(key=lambda d: -d["best_views"])
        win = g[g.views >= HIT_ABS_VIEWS]
        caps = [dict(caption=_clean_caption(cap), views=int(v)) for cap, v in zip(win.caption, win.views) if isinstance(cap, str)]
        seen, caps2 = set(), []
        for x in sorted(caps, key=lambda d: -d["views"]):
            if x["caption"] not in seen: seen.add(x["caption"]); caps2.append(x)
        e = pd.read_csv(f"{REPO}/private/edits/edits.csv"); e = e[e.primary == True]
        cards = {r.reel_key: [t["text"] for t in json.loads(r.text_cards)] for r in e.itertuples() if isinstance(r.text_cards, str)}
        import difflib
        EM = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\u2300-\u23FF\uFE0F\u200d]")
        def _words(t): return re.sub(r"[^a-z ]", "", EM.sub("", t.lower()).replace("x-mas", "xmas")).split()
        hooks = []
        for h, f, v, k in zip(win.hook_text, win.format, win.views, win.key):
            if not isinstance(h, str): continue
            cc = cards.get(k); txt, note = h, "frame-read"
            if cc:
                sim = difflib.SequenceMatcher(None, _words(h), _words(cc[0])).ratio()
                REC = {"mom", "dad", "wife", "husband", "grandma", "grandpa", "sister", "brother", "girlfriend", "boyfriend", "mum"}
                rec_a, rec_b = set(_words(h)) & REC, set(_words(cc[0])) & REC
                if rec_a != rec_b: sim = min(sim, 0.5)   # different recipient = different video (e.g. HJ-13 mom vs dad draft)
                if sim >= 0.8:
                    txt = EM.sub("", h).rstrip() + " " + "".join(EM.findall(cc[0])); note = f"frame text + CapCut emojis (sim {sim:.2f})"
                else:
                    cc = None; note = f"JOIN UNCERTAIN: frame '{h}' vs CapCut card (sim {sim:.2f}) - CapCut text not used"
            hooks.append(dict(hook=txt.strip(), format=f, views=int(v), reel=k, capcut_cards=cc, text_source=note))
        prof = dict(product_key=pk, **w, proven_formats=fm, proven_music=mus, proven_captions=caps2[:8],
                    proven_hooks=sorted(hooks, key=lambda d: -d["views"])[:25],
                    n_own_reels=len(g), own_hits=int((g.views >= HIT_ABS_VIEWS).sum()),
                    product_look_status="description from Omar's prompts; <<<image_1>>> product photo is the ground truth",
                    sources="corpus own reels (FB+IG), CapCut drafts (edits.csv), music_library.csv, Omar transcripts (rules_core), worlds.py")
        with open(os.path.join(PDIR, f"{pk}.json"), "w") as fh: json.dump(prof, fh, indent=1, ensure_ascii=False)
        out[pk] = prof
    return out

def load(pk):
    p = os.path.join(PDIR, f"{pk}.json")
    if not os.path.exists(p): build()
    return json.load(open(p))

def resolve(text):
    """Find the product key from free text (brief)."""
    t = text.lower()
    alias = {"grinch_robe": ["robe", "jammies", "heatedjammies"], "merryfire": ["merryfire", "merry fire", "fire pit", "fire bowl"],
             "brickhood_mask": ["brick hood", "brickhood", "ski mask", "balaclava"], "grinchmelt_mug": ["grinchmelt", "melt", "mug"],
             "merryglow_lights": ["merryglow", "tree lights"], "jollyglow_curtain": ["jollyglow", "curtain"], "purrventure_carrier": ["purrventure", "cat carrier", "carrier"],
             "heatjams": ["heatjams", "heat jams"], "cozyjams": ["cozyjams", "cozy jams", "christmas pajama"],
             "minionmask": ["minionmask", "minion mask"], "trumpglow": ["trumpglow", "trump glow", "patriotglow", "door projector"]}
    order = ["heatjams", "cozyjams", "minionmask", "trumpglow"] + [k for k in alias if k not in ("heatjams", "cozyjams", "minionmask", "trumpglow")]
    for pk in order:
        al = alias[pk]
        if any(a in t for a in al): return pk
    return None

if __name__ == "__main__":
    for pk, p in build().items():
        print(pk, "E", p["energy"], "own", p["n_own_reels"], "hits", p["own_hits"], "| fmts", [(f["format"], f["n"], f["best_views"]) for f in p["proven_formats"][:4]], "| music", [(m["song"], m["best_views"]) for m in p["proven_music"][:3]])
