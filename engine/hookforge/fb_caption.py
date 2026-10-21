"""D93 - Facebook POST caption module (the post text, NOT the on-screen text).

    from hookforge import fb_caption as FC
    FC.build_library()                       # study every caption we have -> learning/captions/*.json
    FC.generate("grinch_robe", plan)         # -> {"caption","hashtags","text","poc",...}
    FC.check_traction(rows)                  # results_feed rows -> swap candidates (40K views OR velocity)
    FC.queue_swap(item_id_or_post, ...)      # approval item: "Get it here 👉 <url>" + same hashtags
    FC.ingest_trending()                     # research/trending_captions/*.csv -> relevance-filtered items

Rules: FB CTA verb is SAY, never "Comment" (F93/G23); Apple iOS emoji only and each emoji must pass
audience_fit.check_emoji; the caption line must pass audience_fit.check_text with POC evidence; every pattern
carries its source reel + views. No network code here: nothing is posted or edited by this module (D41/D78/D91).
"""
import os, re, json, glob, sqlite3, datetime as dt
from collections import Counter, defaultdict
from .config import REPO

CAP_DIR = os.path.join(REPO, "learning", "captions")
LIB_F, TAGS_F = os.path.join(CAP_DIR, "caption_library.json"), os.path.join(CAP_DIR, "hashtags_by_product.json")
TREND_DIR, TREND_OUT = "/workspace/research/trending_captions", os.path.join(CAP_DIR, "trending_ingested.json")
SWAP_DIR = os.path.join(REPO, "learning", "publish_queue", "caption_swaps")
URLS_F = os.path.join(REPO, "config", "product_urls.json")

# D93-6 (Omar 2026-10-20, permanent): swap at 40K total views OR 10K+ views gained inside any one-hour window
# (incl. 10K in the first hour after posting). Replaces the D93-2 1K v/h, 24K day-1 and 2h/5K rules.
SWAP_VIEWS = 40_000
SWAP_HOUR_GAIN = 10_000

# product key -> match regex (product/page/caption/filename), audience slug, trend aliases, hashtag stoplist
PRODUCTS = {
 "grinch_robe":  dict(name="Grinch Robe (MerryJammies)", rx=r"grinch\W*robe|merry\.?jammies|heated ?jammies|heated grinch|festive.heating.robe|grinch.*(robe|heated)", aud="grinch_robe",
                      trend=["grinch robe", "merryjammies"], topics=r"robe|heated|grinch|wearable blanket|cozy"),
 "heatjams":     dict(name="HeatJams", rx=r"heatjams|heated (pajama|jammies|wearable|blanket hoodie)", aud="grinch_robe",
                      trend=["heatjams"], topics=r"heated|robe|blanket|warm"),
 "cozyjams":     dict(name="CozyJams", rx=r"cozyjams|christmas paja|matching paja|christmas pjs|holiday pajama", aud="grinch_robe",
                      trend=["cozyjams"], topics=r"pajama|pjs|matching|cozy"),
 "grinchmelt_mug": dict(name="GrinchMelt", rx=r"grinch ?melt|melt(ing|ie)? ?mug|fondue mug|chocolate.melt|grinch mug", aud="grinchmelt_mug",
                      trend=["grinchmelt"], topics=r"mug|grinch|cocoa|fondue|melt"),
 "brickhood_mask": dict(name="Brick Hood", rx=r"brick ?hood|lego.?head|ski mask|balaclava", aud="brickhood_mask",
                      trend=["brick hood", "brickhood"], topics=r"ski|mask|balaclava|lego"),
 "merryfire":    dict(name="MerryFire", rx=r"merry ?fires?|fire ?(pit|bowl)", aud="merryfire",
                      trend=["merryfire"], topics=r"fire|s'?mores|patio"),
 "merryglow_lights": dict(name="MerryGlow", rx=r"merry ?glows?|tree lights|smart.animated|ceiling projector|christmas projector|tryglowmas", aud="merryglow_lights",
                      trend=["merryglow"], topics=r"light|projector|tree|decor|glow|home depot"),
 "jollyglow_curtain": dict(name="Jolly Glow", rx=r"jolly ?glow|curtain light", aud="jollyglow_curtain",
                      trend=["jolly glow", "jollyglow"], topics=r"curtain|light|window|decor|home depot"),
 "trumpglow":    dict(name="TrumpGlow / PatriotsGlow", rx=r"trump ?glow|patriots? ?glow|\btrump\b|maga", aud="patriotglow",
                      trend=["trumpglow", "patriotsglow", "patriotglow"], topics=r"\btrump|\bmaga\b|\bpatriot|\bvote\b|politic|republican|conservative|\bliberal|\bdemocrat|4th ?of ?july|\bgod bless america\b"),
 "minionmask":   dict(name="Minion Mask", rx=r"minion", aud="minionmask",
                      trend=["minion mask", "minionmask"], topics=r"minion|mask|despicable|banana"),
 "purrventure_carrier": dict(name="PurrVenture", rx=r"purr ?venture|rollymew|merry carrier|cat (carrier|bubble)|pop-up cat", aud="purrventure_carrier",
                      trend=["purrventure"], topics=r"cat|kitten|pet|purr"),
}
# D93-4: products with no viewed captions of their own borrow a sibling with the same page/audience (proof cited)
FALLBACK = {"heatjams": ("grinch_robe", "HeatedJammies FB page sells the MerryJammies heating robe (all its links -> merryjammies.com); HeatJams shares that buyer"),
            "cozyjams": ("grinch_robe", "same cozy-apparel mom/wife gift buyer; CozyJams has no own posts"),
"minionmask": ("brickhood_mask", "same ski-mask page/audience; audience/minionmask.yaml caption_proof cites brickhood sibling"),
            "jollyglow_curtain": ("merryglow_lights", "same Christmas-lights buyer; JollyGlow has 2 own captions <65K"),
            "trumpglow": (None, "own TrumpGlow captions have no views yet: POC = patriotglow.yaml caption_proof (Don't show this to... 183K own; D67 approved)")}
TRUMP_POC = [dict(ref="HeatedJammies FB 'DONT show this to your Grandma' (patriotglow.yaml caption_proof)", views=183145, source="audience/patriotglow.yaml", own=True,
                  caption='Don\'t show this to a liberal 😎🦅 SAY "VOTE" if you like Trump 🇺🇸 #trump #maga #america #usa')]
TAG_STOP = {"fyp", "foryou", "foryoupage", "viral", "fy", "xyzbca", "trending", "explore", "reels", "tiktokshop", "tiktokmademebuyit"}
HASHTAG_RX = re.compile(r"#(\w+)")
COMMENT_RX = re.compile(r"(?i)\bcomment(ing|s)?\b")

def _now(): return dt.datetime.now().isoformat(timespec="seconds")
def _f(x):
    try:
        v = float(x); return 0.0 if v != v else v
    except Exception: return 0.0

def product_key(name):
    n = (name or "").lower().replace("_", " ")
    for k, p in PRODUCTS.items():
        nn = n.replace(" ", "")
        if nn in (k.replace("_", ""), k.split("_")[0], p["name"].lower().replace(" ", "")) or any(nn == t.replace(" ", "") for t in p["trend"]): return k
    for k, p in PRODUCTS.items():
        if re.search(p["rx"], n): return k
    return None

def classify(*texts):
    blob = " ".join(str(t or "") for t in texts).lower()
    for k in ("trumpglow", "jollyglow_curtain", "grinchmelt_mug", "purrventure_carrier", "minionmask", "brickhood_mask", "merryfire", "cozyjams", "heatjams", "grinch_robe", "merryglow_lights"):
        if re.search(PRODUCTS[k]["rx"], blob): return k
    return None

def split_caption(text):
    """-> (body without hashtags/urls, [hashtags lowercased])."""
    t = str(text or "")
    tags = [h.lower() for h in HASHTAG_RX.findall(t)]
    if tags and (re.search(r"#\w+(\.\.\.|…)\s*$", t.strip()) or (len(t) >= 195 and re.search(r"#\w+\s*$", t))): tags = tags[:-1]   # caption cut off mid-tag
    body = re.sub(r"\s+", " ", HASHTAG_RX.sub("", re.sub(r"https?://\S+|\{url\}", "", t))).strip(" \n/")
    return body, tags

def pattern_of(body):
    b = body.lower()
    if re.search(r"\b(say|comment|type)\b\W+[\"“']?\w+", b): return "keyword_cta"         # SAY "X" if you want one
    if re.search(r"(get|shop|grab) (yours|it|here|now)|👉", b): return "link_cta"
    if re.search(r"do ?n.?t (show|let)|run to|who needs|who would", b): return "callout"
    if re.search(r"\b(mom|moms|wife|grandma|her|women|dad|him)\b", b): return "gift_target"
    if re.search(r"heated|it'?s heated|and it", b): return "reveal_tag"
    if re.search(r"\bvs\.?\b|fake|actually|jk", b): return "contrast"
    if not b: return "hashtags_only"
    return "statement"

# ---------------- 1. study every caption we have ----------------
def _rows():
    out = []
    def add(src, own, ref, views, caption, *ctx):
        if not str(caption or "").strip() or str(caption) == "nan": return
        k = classify(*ctx, caption)
        if k: out.append(dict(product=k, source=src, own=own, ref=str(ref), views=_f(views), caption=str(caption)))
    db = os.path.join(REPO, "data", "hookforge.db")
    if os.path.exists(db):
        c = sqlite3.connect(db)
        for page, prod, rid, url, v, cap, tier, src in c.execute("select page,product,reel_id,url,views,caption,tier,source from reels where caption!=''"):
            own = bool(re.search(r"(?i)heatedjammies|merry|purrventure|brick hood|jolly|patriot|trumpglow", str(page))) and "ext" not in str(tier).lower()
            add("hookforge.db", own, url or rid, v, cap, prod, page)
    import pandas as pd
    for f, own_rx in (("private/corpus/corpus.csv", r"(?i)heatedjammies|merry|purrventure|brick hood|jolly|patriot"),
                      ("audience/data/text_corpus.csv", None), ("learning/results/reels.csv", r".")):
        p = os.path.join(REPO, f)
        if not os.path.exists(p): continue
        d = pd.read_csv(p, low_memory=False, dtype=str)
        for _, r in d.iterrows():
            page = str(r.get("page", ""))
            own = bool(own_rx and re.search(own_rx, page))
            add(f, own, r.get("url") or r.get("reel_id") or r.get("post_id") or r.get("reel_key"), r.get("views"), r.get("caption"), r.get("product", ""), page)
    for f in glob.glob(os.path.join(REPO, "learning/results/snapshots/*.csv")):
        d = pd.read_csv(f)
        for _, r in d.iterrows(): add("snapshot:" + os.path.basename(f), True, r.get("reel_key"), r.get("views"), r.get("caption"), r.get("page"))
    for f in glob.glob(os.path.join(REPO, "out/deliver/*Caption*.txt")):   # our shipped captions (no views yet: style evidence only)
        add("out/deliver", True, os.path.basename(f), 0, open(f).read(), os.path.basename(f))
    poc = json.load(open(os.path.join(REPO, "config", "poc_defaults.json")))
    for k, v in poc.items():
        if isinstance(v, dict) and isinstance(v.get("caption"), dict):
            kk = product_key(k) or classify(k)
            m = re.search(r"([\d.]+)M", v["caption"].get("why", ""))
            if kk: out.append(dict(product=kk, source="config/poc_defaults.json", own=False, ref=v["caption"].get("poc", k), views=float(m.group(1)) * 1e6 if m else 0, caption=v["caption"]["text"], why=v["caption"].get("why", "")))
    # de-dup same caption+views (crossposts / same reel in several sources)
    seen, uniq = set(), []
    for r in sorted(out, key=lambda r: -r["views"]):
        key = (r["product"], re.sub(r"\W+", "", r["caption"].lower())[:80], int(r["views"]) // 1000)
        if key not in seen: seen.add(key); uniq.append(r)
    return uniq

def build_library(write=True):
    rows = _rows(); lib, tags_out = {}, {}
    for k, p in PRODUCTS.items():
        rs = [r for r in rows if r["product"] == k]
        pats = defaultdict(list); tagstat = defaultdict(lambda: dict(n=0, views=0.0, own=0, best=None))
        for r in rs:
            body, tags = split_caption(r["caption"]); pat = pattern_of(body)
            pats[pat].append(dict(body=body, caption=r["caption"][:300], views=r["views"], ref=r["ref"], source=r["source"], own=r["own"], n_tags=len(tags)))
            for t in dict.fromkeys(tags):
                if t in TAG_STOP or len(t) < 3: continue
                s = tagstat[t]; s["n"] += 1; s["views"] += r["views"]; s["own"] += r["own"]
                if not s["best"] or r["views"] > s["best"]["views"]: s["best"] = dict(ref=r["ref"], views=r["views"], source=r["source"])
        # own data outranks external at equal views (x2 weight), mirrors ly_season / proof_guard policy
        def score(ex): return sum(e["views"] * (2 if e["own"] else 1) for e in ex) / max(1, len(ex)) ** 0.5
        plist = []
        for pat, ex in sorted(pats.items(), key=lambda kv: -score(kv[1])):
            ex = sorted(ex, key=lambda e: -e["views"])
            if not any(e["views"] > 0 for e in ex): continue          # a pattern without a viewed POC reel is not a winning pattern
            ntags = sorted(e["n_tags"] for e in ex if e["views"] > 0)
            plist.append(dict(pattern=pat, n=len(ex), total_views=sum(e["views"] for e in ex), median_tags=ntags[len(ntags)//2] if ntags else 0,
                              poc=[dict(ref=e["ref"], views=e["views"], source=e["source"], own=e["own"], caption=e["caption"]) for e in ex[:5]]))
        ranked = sorted(tagstat.items(), key=lambda kv: -(kv[1]["views"] * (1 + kv[1]["own"]) * min(kv[1]["n"], 5) ** 0.5))
        shipped = Counter(t for r in rs if r["source"] == "out/deliver" for t in split_caption(r["caption"])[1])
        top = [dict(tag="#" + t, n=s["n"], own_n=s["own"], total_views=s["views"], poc=s["best"]) for t, s in ranked if s["views"] > 0 and (s["n"] >= 2 or s["own"])][:15]
        own_n = [len(x["poc"]) for x in plist]
        fb = FALLBACK.get(k)
        if k == "trumpglow" and not plist:
            plist = [dict(pattern="callout", n=1, total_views=183145, median_tags=4, poc=TRUMP_POC, fallback=fb[1])]
            top = [dict(tag=t, n=0, own_n=0, total_views=0, poc="own shipped TrumpGlow captions (out/deliver) + D67; no viewed POC yet") for t in ("#trump", "#maga", "#america", "#usa")]
        weak = len(plist) < 2 or not any(e["own"] and e["views"] > 0 for x in plist for e in x["poc"])
        lib[k] = dict(name=p["name"], fallback=(fb[0] if fb and weak else None), fallback_why=(fb[1] if fb and weak else None), n_captions=len(rs), n_own=sum(r["own"] for r in rs), patterns=plist,
                      gap=None if rs else "no captions in any source")
        if not top and shipped:   # no viewed tags: our own shipped captions (style proof, no views yet)
            top = [dict(tag="#" + t, n=n, own_n=n, total_views=0, poc="out/deliver shipped captions (no views yet)") for t, n in shipped.most_common(5)]
        tags_out[k] = dict(name=p["name"], top=top, default_set=[t["tag"] for t in top[:4]])
    if write:
        os.makedirs(CAP_DIR, exist_ok=True)
        meta = dict(_built=_now(), _doc="D93 caption study: every pattern cites its POC reels + views. own=True rows weighted x2.")
        json.dump({**meta, "products": lib}, open(LIB_F, "w"), indent=1, ensure_ascii=False)
        json.dump({**meta, "products": tags_out}, open(TAGS_F, "w"), indent=1, ensure_ascii=False)
    return lib, tags_out

def _load():
    if not (os.path.exists(LIB_F) and os.path.exists(TAGS_F)): build_library()
    return json.load(open(LIB_F))["products"], json.load(open(TAGS_F))["products"]

def product_url(key):
    if os.path.exists(URLS_F):
        u = json.load(open(URLS_F)).get(key, {}).get("url")
        if u and not u.startswith("PLACEHOLDER"): return u
    return None

# ---------------- 2. generate ----------------
def fb_safe(text):
    """F93: FB never says Comment. 'Comment "X" if...' -> 'SAY "X" if...'."""
    t = re.sub(r"(?i)\bcomment(ing|s)?\b(?=\s*[\"“'A-Z])", "SAY", text)
    return COMMENT_RX.sub("SAY", t)

JUNK_RX = re.compile(r"(?i)chills|horror|terrifying|link in (my |our )?bio|\btuts?\b|on (my )?(story|profile)|@\w|amazon|target|walmart|aerie|holdman|\busb\b|\b20\d\d new\b|sponsor|\bpaid\b|tiktok ?shop|founder|\b(he|she) (said|got)|discount code|\b\d+% off|ends at midnight")
GOOD_PATTERNS = ("keyword_cta", "callout", "gift_target", "reveal_tag", "contrast", "statement")

def _short(body):
    """Keep the hook sentence (+ any SAY/Comment clause). FB post captions that won are short (own median 5 words)."""
    sents = re.split(r"(?<=[.!?…🎄🎁❄️😊🤭])\s+", body.strip())
    keep = sents[0]
    cta = next((x for x in sents[1:] if re.search(r"(?i)\b(say|comment)\b", x)), None)
    if cta and cta != keep: keep = keep + " " + cta
    return keep.strip()

def _audience_filter(slug, body):
    from . import audience_fit as AF
    keep, dropped = body, []
    for e in AF.emojis(body):
        r = AF.check_emoji(slug, e)
        if not r["ok"]: keep = keep.replace(e, ""); dropped.append((e, r["reason"]))
    return re.sub(r"\s{2,}", " ", keep).strip(), dropped

def generate(product, video_plan=None, platform="facebook", n_tags=None, trending=True, rank=0, avoid=()):
    """rank=n returns the n-th passing caption; avoid = caption bodies already used on sibling pages (D95 per-page)."""
    k = product_key(product) or product
    if k not in PRODUCTS: raise KeyError(f"unknown product {product}")
    lib, tags = _load(); p = PRODUCTS[k]; plan = video_plan or {}
    cands = []
    src_keys = [k] + ([lib[k]["fallback"]] if lib[k].get("fallback") else [])
    for pat in [pp for sk in src_keys for pp in lib[sk]["patterns"]]:
        for e in pat["poc"]:
            body = split_caption(e["caption"])[0]
            body = _short(body) if body else body
            if body and e["views"] > 0 and not JUNK_RX.search(body) and len(body) <= 90 and pat["pattern"] in GOOD_PATTERNS + ("hashtags_only",) and not re.search(r"(?i)get (it|yours)|shop (here|now)|👉", body):   # link lines are the swap, not the launch caption
                cands.append(dict(body=body, views=e["views"], own=e["own"], ref=e["ref"], pattern=pat["pattern"], source=e["source"], median_tags=pat["median_tags"]))
    if trending and os.path.exists(TREND_OUT):
        for t in json.load(open(TREND_OUT)).get("accepted", []):
            if t["product"] == k and not JUNK_RX.search(t["body_fb"]) and len(t["body_fb"]) <= 90:
                cands.append(dict(body=t["body_fb"], views=_f(t["views"]) * 0.5, own=False, ref=t["source_url"], pattern="trending:" + t["pattern"], source="viral_research", median_tags=len(t["hashtags"])))
    if plan.get("caption_override"): cands.insert(0, dict(body=plan["caption_override"], views=1e12, own=True, ref=plan.get("caption_poc", "plan"), pattern="plan", source="plan", median_tags=4))
    from . import perf_feedback as _pf                                                       # D119: our posted results re-weight captions
    cands.sort(key=lambda c: (not (c["own"] and c["views"] >= 50_000), -c["views"] * _pf.weight(k, "caption", c["body"])))   # own page proof outranks competitors (proof_guard policy)
    from . import audience_fit as AF
    tried = []
    try:                                   # D115: product truth (worlds caption_forbidden) + US spelling (every caption_voice says US)
        from .worlds import WORLDS
        cf = [re.compile(x, re.I) for x in (WORLDS.get(k) or {}).get("caption_forbidden", [])]
    except Exception: cf = []
    UK = re.compile(r"(?i)\b(cosy|colour|favourite|mum|jumper)\b")
    from .publish import is_listing as _is_listing                   # D138
    for c in cands:
        if any(x.search(c["body"]) for x in cf) or UK.search(c["body"]) or _is_listing(c["body"]): continue
        body = fb_safe(c["body"]) if platform == "facebook" else c["body"]
        if re.search(r"\bSAY\b(?!\s*[\"“'])", body) and not re.search(r"\bSAY\b", c["body"]): continue   # D115: 'the comments about the price' -> 'the SAY about' is not a CTA
        body, dropped = _audience_filter(p["aud"], body)
        if len(body) > 200 or len(body) < 3: continue
        ev = f"{c['source']}:{c['ref']} {int(c['views']):,} views ({c['pattern']})"
        chk = AF.check_text(p["aud"], body, kind="caption", extra_evidence=ev)
        tried.append((body, chk["ok"], chk.get("reason")))
        if not chk["ok"] or body in avoid: continue
        if rank > 0: rank -= 1; continue
        nt = n_tags or (3 if k == "grinchmelt_mug" else max(3, min(5, c["median_tags"] or 4)))   # VR 2026-10-20: tiny tag sets win on mugs
        hs = (tags[k]["default_set"] or (tags[lib[k]["fallback"]]["default_set"] if lib[k].get("fallback") else []))[:nt]
        # fan-base / niche tag first (Viral Research 2026-10-20: fandom tag leads on robes/pajamas)
        text = body + ("\n" + " ".join(hs) if hs else "")
        assert not (platform == "facebook" and COMMENT_RX.search(text))
        return dict(product=k, platform=platform, caption=body, hashtags=hs, text=text, pattern=c["pattern"], poc=ev,
                    audience_fit=dict(ok=True, score=chk.get("score"), emoji_dropped=dropped), swap_text=swap_text(k, hs))
    raise ValueError(f"{k}: no proven caption passed audience_fit (tried {len(tried)}): {tried[:3]}")

# ---------------- 3. traction swap ----------------
def swap_text(product, hashtags):
    url = product_url(product) or f"PLACEHOLDER_URL_{product}"
    return f"Get it here 👉 {url}" + ("\n" + " ".join(hashtags) if hashtags else "")

def _ts(x):
    try: return dt.datetime.fromisoformat(str(x).replace(" ", "T")[:16])
    except Exception: return None

def hour_gain(points):
    """points: [(datetime, views)] incl. (posted_pt, 0). Max views gained between two points <= 1 h apart."""
    pts = sorted((t, v) for t, v in points if t is not None)
    best = 0.0
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            if (pts[j][0] - pts[i][0]).total_seconds() > 3600: break
            best = max(best, pts[j][1] - pts[i][1])
    return best

def traction(row, history=()):
    """row: latest results_feed row; history: earlier [(snapshot_pt, views)] for the same reel."""
    v = _f(row.get("views"))
    pts = [(_ts(row.get("posted_pt")), 0.0), (_ts(row.get("snapshot_pt")), v)] + [(_ts(t), _f(x)) for t, x in history]
    g = max(hour_gain(pts), _f(row.get("views_1h_gain")))
    if v >= SWAP_VIEWS: return dict(swap=True, views=v, hour_gain=g, reason=f"views {int(v):,} >= {SWAP_VIEWS:,}")
    if g >= SWAP_HOUR_GAIN: return dict(swap=True, views=v, hour_gain=g, reason=f"+{int(g):,} views within one hour >= {SWAP_HOUR_GAIN:,}")
    return dict(swap=False, views=v, hour_gain=g)

def check_traction(rows=None, history=None):
    """rows: latest results_feed snapshot rows. history: {reel_key: [(snapshot_pt, views)]}; default = all older snapshots."""
    import pandas as pd
    fs = sorted(glob.glob(os.path.join(REPO, "learning/results/snapshots/*.csv")))
    if rows is None: rows = pd.read_csv(fs[-1]).to_dict("records") if fs else []
    if history is None:
        history = defaultdict(list)
        for f in fs[:-1]:
            for r in pd.read_csv(f).to_dict("records"): history[r.get("reel_key")].append((r.get("snapshot_pt"), r.get("views")))
    out = []
    for r in rows:
        t = traction(r, history.get(r.get("reel_key"), ()))
        if not t["swap"] or re.search(r"(?i)get it here|get yours|shop (here|now)|https?://", str(r.get("caption", ""))): continue
        k = classify(r.get("page"), r.get("caption"), r.get("file"))
        out.append(dict(reel_key=r.get("reel_key"), post_id=r.get("post_id"), page=r.get("page"), product=k, caption=r.get("caption"), **t))
    return out

def queue_swap(cand, buffer_post_id=None):
    """Writes an approval item. Nothing is edited here. Execution path documented in item['how']."""
    k = cand.get("product")
    old = str(cand.get("caption") or ""); hs = ["#" + h for h in HASHTAG_RX.findall(old)] or (_load()[1][k]["default_set"] if k else [])
    new = swap_text(k, hs) if k else None
    url_ok = bool(k and product_url(k))
    it = dict(id=f"swap_{re.sub(r'[^A-Za-z0-9]+', '_', str(cand.get('reel_key') or cand.get('post_id')))}", status="AWAITING_OMAR_APPROVAL",
              created=_now(), product=k, page=cand.get("page"), reel_key=cand.get("reel_key"), fb_post_id=cand.get("post_id"),
              buffer_post_id=buffer_post_id, reason=cand.get("reason"), old_caption=old, new_caption=new,
              blocked=None if (k and url_ok) else ("product unknown" if not k else f"no product URL in config/product_urls.json for {k}"),
              how=("Buffer edit_post only edits posts still in Buffer (draft/scheduled; check allowedActions). A PUBLISHED FB reel caption "
                   "cannot be changed through Buffer -> after Omar approves, the edit goes through Meta Graph API: "
                   "POST /{video-id} with description=<new_caption> using a Page access token (pages_manage_posts). "
                   "Token not configured yet; until then Omar pastes new_caption in Meta Business Suite."))
    os.makedirs(SWAP_DIR, exist_ok=True)
    json.dump(it, open(os.path.join(SWAP_DIR, it["id"] + ".json"), "w"), indent=1, ensure_ascii=False)
    return it

def swap_buffer_payload(post, new_text):
    """For a post STILL IN BUFFER (draft/scheduled) only: edit_post args that change text and carry everything else forward."""
    if str(post.get("status")) in ("sent", "sending"): raise ValueError("published post: Buffer cannot edit it; use the Graph API path (queue_swap)")
    if "editPost" not in str(post.get("allowedActions", "editPost")) and "edit" not in str(post.get("allowedActions", "edit")).lower():
        raise ValueError("Buffer allowedActions has no edit for this post")
    return dict(postId=post["id"], text=new_text, assets=post.get("assets"), metadata=post.get("metadata"))

# ---------------- 5. trending ingest ----------------
def _relevant(k, caption, hashtags, product_col):
    blob = f"{caption} {hashtags}".lower(); p = PRODUCTS[k]
    named = product_key(product_col) == k
    topical = bool(re.search(p["topics"], blob))
    if k == "trumpglow": return topical, "political/patriot trend" if topical else "not political"
    if k in ("grinch_robe", "heatjams") and not re.search(r"robe|heated|wearable|blanket|cozy|grinch|hoodie", blob): return False, "not a robe/heated trend"
    return (named and topical) or (topical and not product_col), ("named+topical" if named and topical else "topic only" if topical else "off-topic for product")

def _route(caption, hashtags, product_col):
    """Pick the product a trend belongs to: Viral Research's label if relevant, else by topic (political -> TrumpGlow, heated robe -> MerryJammies)."""
    blob = f"{caption} {hashtags}".lower()
    if re.search(PRODUCTS["trumpglow"]["topics"], blob): return "trumpglow"
    if re.search(r"heated (robe|blanket)|wearable blanket", blob): return "grinch_robe"
    return product_key(product_col)

def ingest_trending(paths=None, write=True):
    import csv
    paths = paths or sorted(glob.glob(os.path.join(TREND_DIR, "*.csv")))
    acc, rej = [], []
    for f in paths:
        for r in csv.DictReader(open(f, encoding="utf-8")):
            k = _route(r.get("caption", ""), r.get("hashtags", ""), r.get("product", ""))
            base = dict(file=os.path.basename(f), product_in=r.get("product"), source_url=r.get("source_url"), views=_f(r.get("views")), date=r.get("date"))
            if not k: rej.append({**base, "why": "no product match"}); continue
            ok, why = _relevant(k, r.get("caption", ""), r.get("hashtags", ""), r.get("product", ""))
            if not r.get("source_url") or not _f(r.get("views")): ok, why = False, "no POC (source_url+views required)"
            if ok and JUNK_RX.search(r.get("caption", "")) and len(split_caption(r.get("caption", ""))[0]) > 120: ok, why = False, "brand/haul description, not a reusable caption"
            if not ok: rej.append({**base, "product": k, "why": why}); continue
            body, tags = split_caption(r.get("caption", ""))
            tags = list(dict.fromkeys(tags + [h.lower() for h in HASHTAG_RX.findall(r.get("hashtags", ""))]))
            body = re.sub(r"@\w[\w.]*", "", body).strip()            # never carry other brands' handles
            acc.append({**base, "product": k, "why": why, "body": body, "body_fb": fb_safe(body), "hashtags": ["#" + t for t in tags if t not in TAG_STOP],
                        "pattern": pattern_of(body)})
    res = dict(_built=_now(), accepted=acc, rejected=rej, by_product=dict(Counter(a["product"] for a in acc)))
    if write:
        os.makedirs(CAP_DIR, exist_ok=True); json.dump(res, open(TREND_OUT, "w"), indent=1, ensure_ascii=False)
    return res
