"""D134 reference miner: ranks which CUTS, SOUNDS, HOOKS and HASHTAGS from ALL products (11; 8 retired = full reference
corpus) transfer best to each ACTIVE product, and feeds concept_lab.rank.
transfer score = log10(views) x affinity(source -> target) x fit(target), where
  affinity = AFFINITY matrix (same audience / season / buyer: 1.0 same product .. 0.15 unrelated), 
  fit      = 0 if the element fails the target's gates (world conflict, political_lint, banned song / niche, UK spelling).
Sources: poc/poc_library.json (hooks), learning/music_library.csv (sounds: proven_on per product + external),
learning/captions/hashtags_by_product.json (hashtags), learning/editing_style/shots.csv (cuts: per-draft shot rhythm x
views; product-agnostic -> affinity 0.5). Output learning/ref_miner/transfer.json; boost(product, format) -> 0..1 used by
concept_lab.rank (W_REF)."""
import os, re, json, math, collections
import pandas as pd
from .config import REPO
from . import products, worlds, political_lint

ACTIVE_NICHE = {"jollyglow_curtain": "christmas", "trumpglow": "patriot", "purrventure_carrier": "pet"}
# rows = target, cols = source. Christmas-decor moms share the robe/lights/fire audiences; TrumpGlow (men, patriotic,
# funny) shares little with Christmas; PurrVenture (cat parents, evergreen) borrows only generic grammar.
AFFINITY = {
 "jollyglow_curtain": {"jollyglow_curtain": 1.0, "merryglow_lights": 0.9, "merryfire": 0.6, "grinch_robe": 0.55, "heatjams": 0.5, "cozyjams": 0.5, "grinchmelt_mug": 0.5, "trumpglow": 0.25, "brickhood_mask": 0.2, "minionmask": 0.2, "purrventure_carrier": 0.2},
 "trumpglow":         {"trumpglow": 1.0, "brickhood_mask": 0.45, "minionmask": 0.4, "merryglow_lights": 0.35, "jollyglow_curtain": 0.35, "merryfire": 0.3, "grinch_robe": 0.3, "heatjams": 0.25, "cozyjams": 0.2, "grinchmelt_mug": 0.2, "purrventure_carrier": 0.15},
 "purrventure_carrier": {"purrventure_carrier": 1.0, "grinch_robe": 0.25, "heatjams": 0.25, "cozyjams": 0.25, "jollyglow_curtain": 0.2, "merryglow_lights": 0.2, "brickhood_mask": 0.2, "minionmask": 0.2, "merryfire": 0.15, "grinchmelt_mug": 0.2, "trumpglow": 0.15},
}
POC_PRODUCT = [(r"jollyglow|curtain", "jollyglow_curtain"), (r"tree lights|merry ?glow", "merryglow_lights"), (r"fire", "merryfire"),
               (r"grinch robe|heated grinch", "grinch_robe"), (r"heated robe|wearable blanket", "heatjams"), (r"pajama|jammies", "cozyjams"),
               (r"mug", "grinchmelt_mug"), (r"minion", "minionmask"), (r"ski mask|smiley", "brickhood_mask"), (r"projector|trump|patriot|sill plate|car door", "trumpglow"),
               (r"cat", "purrventure_carrier")]
UK = re.compile(r"(?i)\b(cosy|colour|favourite|mum|jumper|customise)\b")
NOT_TEXT = re.compile(r"(?i)backyard-cam|repost|re-edit|variant|→|identical cuts|\breel\b|=|\d+M\b")
OUT = os.path.join(REPO, "learning", "ref_miner", "transfer.json")

def _src(prod):
    s = str(prod).lower()
    return next((k for rx, k in POC_PRODUCT if re.search(rx, s)), None)

def _fit_text(target, text):
    if UK.search(text): return 0.0, "UK spelling"
    from . import profiles
    try:
        if worlds.world_conflicts(profiles.load(target), text): return 0.0, "world conflict"
    except Exception: pass
    if target in political_lint.POLITICAL and any(l == "BLOCK" for _, l, _ in political_lint.lint_text(text)): return 0.0, "political lint"
    if target == "trumpglow" and re.search(r"(?i)christmas|santa|grinch|xmas", text): return 0.3, "christmas wording on a patriotic product"
    if target == "purrventure_carrier" and re.search(r"(?i)christmas|santa|grinch|mom needs|gift", text): return 0.5, "seasonal wording on an evergreen product"
    return 1.0, ""

def _score(views, aff, fit): return round(math.log10(max(views, 10)) * aff * fit, 3)

def hooks(target):
    L = json.load(open(os.path.join(REPO, "poc", "poc_library.json"))); out = []
    for e in L:
        if e.get("kind") != "hook" or NOT_TEXT.search(e["text"]): continue
        if not re.search(r"[^\x00-\x7F]|\.\.|[!?]|\bPOV\b|\bVS\b", e["text"]): continue      # stage description, not on-screen text
        src = _src(e.get("product"));
        if not src: continue
        aff = AFFINITY[target].get(src, 0.15); fit, why = _fit_text(target, e["text"])
        out.append(dict(text=e["text"], source_product=src, views=int(e.get("views") or 0), affinity=aff, fit=fit, why=why,
                        formats=e.get("formats") or [], poc=e["id"], score=_score(e.get("views") or 0, aff, fit)))
    return sorted(out, key=lambda x: -x["score"])

def sounds(target):
    lib = pd.read_csv(os.path.join(REPO, "learning", "music_library.csv")).drop_duplicates("song"); out = []
    sj = json.load(open(os.path.join(REPO, "music", "songs.json")))
    on_box = {k for k, v in sj.items() if os.path.exists(v.get("file", "") or "")}
    for r in lib.itertuples():
        best, src = 0, None
        for x in str(r.proven_on).split(";"):
            if ":" not in x: continue
            pk, v = x.split(":", 1); v = int(float(v.split("(")[0] or 0)); a = AFFINITY[target].get(pk, 0.15)
            if v * a > best * (AFFINITY[target].get(src, 0.15) if src else 1): best, src = v, pk
        ext = int(r.ext_best_views or 0)
        niche_ok = ACTIVE_NICHE[target] in str(r.niche) or (ACTIVE_NICHE[target] == "christmas" and "cozy" in str(r.niche))
        fit = 1.0 if niche_ok else 0.2
        aff = AFFINITY[target].get(src, 0.15) if src else 0.3
        v = max(best, ext * 0.5)
        file_ok = any(k == r.song or k.replace("_", "") == r.song.replace("_", "") or k.startswith(r.song) for k in on_box)
        out.append(dict(song=r.song, niche=r.niche, source_product=src, own_best=best, ext_best=ext, affinity=aff, fit=fit, on_box=file_ok,
                        score=_score(v, aff, fit) * (1.0 if file_ok else 0.7)))
    slug = {"trumpglow": "patriotglow", "purrventure_carrier": "purrventure", "jollyglow_curtain": "jollyglow"}[target]
    for k, v in sj.items():                    # audience songs from music/songs.json (patriot / pet niches are not in the Christmas library)
        if slug in (v.get("slug") or []) and not any(o["song"] == k for o in out):
            vw = max([int(x) for x in re.findall(r"(\d[\d,]{3,})", str(v.get("in_point_label", "")) + str(v.get("source", ""))) and
                      [int(x.replace(",", "")) for x in re.findall(r"(\d[\d,]{3,})", str(v.get("in_point_label", "")) + str(v.get("source", "")))] or [0]] or [0])
            m = re.search(r"(\d+(?:\.\d+)?)M\b", str(v.get("in_point_label", ""))); vw = max(vw, int(float(m.group(1)) * 1e6) if m else 0, 10_000)
            out.append(dict(song=k, niche=ACTIVE_NICHE[target], source_product=target, own_best=0, ext_best=vw, affinity=1.0, fit=1.0,
                            on_box=os.path.exists(v.get("file", "") or ""), score=_score(vw, 1.0, 1.0)))
    return sorted(out, key=lambda x: -x["score"])

GENERIC = {"jollyglow_curtain": r"christmas|xmas|holiday|decor|lights|gift|mom|viral|fyp|home|cozy",
           "trumpglow": r"trump|maga|america|usa|patriot|4thofjuly|funny|viral|fyp|truck|men|dad",
           "purrventure_carrier": r"cat|kitty|kitten|pet|viral|fyp"}
def hashtags(target):
    H = json.load(open(os.path.join(REPO, "learning", "captions", "hashtags_by_product.json")))["products"]; agg = collections.defaultdict(lambda: dict(score=0.0, src=set(), views=0))
    for pk, d in H.items():
        a = AFFINITY[target].get(pk, 0.15)
        for t in d.get("top", []):
            tag = t["tag"].lower(); fit, _ = _fit_text(target, tag)
            if target == "purrventure_carrier" and not re.search(r"cat|pet|kitty|kitten", tag) and pk != target: fit *= 0.3
            if target == "trumpglow" and re.search(r"christmas|grinch|santa|xmas", tag): fit = 0
            if pk != target and not re.search(GENERIC[target], tag): continue          # another product's own noun (#skimask) never transfers
            s = _score(t.get("total_views") or 0, a, fit) + (0.5 if pk == target and (t.get("total_views") or t.get("own_n")) else 0)
            g = agg[tag]; g["score"] = max(g["score"], s); g["src"].add(pk); g["views"] = max(g["views"], int(t.get("total_views") or 0))
    return sorted([dict(tag=k, score=round(v["score"], 3), sources=sorted(v["src"]), views=v["views"]) for k, v in agg.items()], key=lambda x: -x["score"])

def cuts(target):
    d = pd.read_csv(os.path.join(REPO, "learning", "editing_style", "shots.csv"))
    g = d.groupby("draft").agg(views=("views", "first"), n=("i", "count"), hook_s=("dur", "first"), avg_s=("dur", "mean"), total=("dur", "sum")).dropna()
    g["bucket"] = g.apply(lambda r: f"hook {round(r.hook_s)}s / {int(r.n)} shots / ~{r.avg_s:.1f}s per shot", axis=1)
    b = g.groupby("bucket").agg(views=("views", "max"), drafts=("views", "count")).reset_index()
    b["score"] = b.apply(lambda r: _score(r.views, 0.5, 1.0) + 0.1 * min(r.drafts, 5), axis=1)
    return b.sort_values("score", ascending=False).head(10).to_dict("records")

def build():
    res = {}
    for t in products.active():
        h = hooks(t); res[t] = dict(hooks=h[:15], sounds=sounds(t)[:8], hashtags=[x for x in hashtags(t) if x["score"] > 0][:12], cuts=cuts(t)[:6],
                                    format_boost=_format_boost(h))
    os.makedirs(os.path.dirname(OUT), exist_ok=True); json.dump(res, open(OUT, "w"), indent=1, ensure_ascii=False, sort_keys=True); return res   # D166 deterministic

F_RX = [(r"(?i)\bVS\b|last day|first day|then|last year", ["F04", "F18"]), (r"(?i)\bPOV\b", ["F15", "F09"]), (r"(?i)\bNEEDS?\b", ["F13"]),
        (r"(?i)don'?t show", ["F05"]), (r"(?i)\bRUN\b|walmart|target|costco", ["F17", "F02"]), (r"(?i)problem|solution", ["F19", "F02"]),
        (r"(?i)wife got|got (my|this)|for (my|your) (husband|wife|boyfriend)", ["F09", "F06"]), (r"(?i)buy one", ["F16"]), (r"(?i)lovers|moms,|fans", ["F07"])]
TAG_F = {"pov_street_jealous": ["F15"], "dont_walk_run_to_store": ["F17"], "store_x_brand": ["F02", "F17"], "dont_show_this_to": ["F05"],
         "vs_contrast": ["F04", "F18"], "problem-solution": ["F19", "F02"]}
def _format_boost(h):
    """0..1 per F-code: best transfer score of hooks whose grammar (text) or POC tag maps to that format, normalised."""
    fb = collections.defaultdict(float)
    for x in h:
        fs = {F for t in x["formats"] for F in TAG_F.get(t, [])} | {F for rx, Fs in F_RX if re.search(rx, x["text"]) for F in Fs}
        for f in fs: fb[f] = max(fb[f], x["score"])
    m = max(fb.values() or [1]); return {f: round(v / m, 3) for f, v in fb.items()}

def boost(product, fmt):
    if not os.path.exists(OUT): return 0.0
    return json.load(open(OUT)).get(product, {}).get("format_boost", {}).get(fmt, 0.0)
