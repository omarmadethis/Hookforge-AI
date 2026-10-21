"""D69 POC LIBRARY: searchable index of proven hooks, songs (with in-points), formats and captions, each with views + source.
Built from learning/raw_vs_final/performance_all.csv (own FB/IG, incl. Merry Carrier + HeatedJammies), analytics/fb_hj/ranked.csv
(HeatedJammies insights: hook/song per reel), music/songs.json (verified in-points), research/trumpglow SONG_INPOINTS/refs.csv
(Ad Library matches + external TikTok refs). Output poc/poc_library.json. Strength: strong >=100K own or verified xcorr>=0.9 match
of >=2 ads; ok >=50K; weak otherwise."""
import glob, csv, datetime, json, os, re
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(REPO, "poc", "poc_library.json")
FORMATS = {  # Omar's proven hook formats (regex -> name)
    "dont_show_this_to": r"(?i)^\W*do(n'?t|nt| not) show this to",
    "pov_street_jealous": r"(?i)^pov\W.*(street|neighbou?rs?).*jealous",
    "dont_walk_run_to_store": r"(?i)don'?t walk.{0,6}run.{0,4}to",
    "store_x_brand": r"(?i)\bx (target|walmart|costco)\b|\b(target|walmart|costco)\b",
    "vs_contrast": r"(?i)\bvs\.{0,3}\b",
    "get_yours": r"(?i)^get yours",
}
def strength(views=0, verified=False):
    v = float(views or 0)
    return "strong" if v >= 100_000 or verified else "ok" if v >= 50_000 else "weak"
def fmt_of(text):
    return [k for k, rx in FORMATS.items() if text and re.search(rx, text)]
def _f(x):
    try: return float(x)
    except Exception: return 0.0
def build(write=True):
    E = []
    p = os.path.join(REPO, "learning/raw_vs_final/performance_all.csv")
    for r in csv.DictReader(open(p)):
        v = _f(r["views"]); src = f"own {r['platform']} {r['page']} {r['url']}"
        for kind, t in (("hook", r.get("hook_text_ref")), ("caption", r.get("caption"))):
            t = (t or "").strip()
            if t and t.lower() not in ("link in bio!",):
                E.append(dict(kind=kind, text=t, views=v, page=r["page"], product=r.get("product", ""), source=src, formats=fmt_of(t), strength=strength(v)))
    p = os.path.join(REPO, "analytics/fb_hj/ranked.csv")
    if os.path.exists(p):
        for r in csv.DictReader(open(p)):
            v = _f(r["Views"]); src = f"own FB HeatedJammies insights {r['uid']}"
            if r.get("hook"): E.append(dict(kind="hook", text=r["hook"], views=v, page="HeatedJammies", product="heated robe", source=src, formats=fmt_of(r["hook"]), strength=strength(v)))
            if r.get("audio_label"): E.append(dict(kind="song", text=r["audio_label"], views=v, page="HeatedJammies", product="heated robe", source=src, in_point_s=None, strength=strength(v), note="in-point not measured"))
    for k, s in json.load(open(os.path.join(REPO, "music/songs.json"))).items():
        ver = (s.get("verify") or {}).get("xcorr", 0) >= 0.9
        E.append(dict(kind="song", key=k, text=s["song"], in_point_s=s.get("in_point_s"), in_point_label=s.get("in_point_label"), views=None, source=s.get("source"),
                      slugs=s.get("slug"), strength="strong" if ver and k == "acdc_you_shook_me" else "weak",
                      note="3 Ad Library Trump ads start here (xcorr 0.92-0.93)" if k == "acdc_you_shook_me" else "in-point from Omar's own CapCut draft + TikTok sound stats; no ad match"))
    for r in csv.DictReader(open(os.path.join(REPO, "learning/music_library.csv"))):
        v = max(_f(r.get("own_best_views")), _f(r.get("ext_best_views")))
        E.append(dict(kind="song", key=r["song"], text=r["version"], in_point_s=_f(r.get("capcut_offset_s")), in_point_label="CapCut offset in Omar's own drafts",
                      views=v, source=f"own drafts n={r['n_own_drafts']}, proven_on {r['proven_on'][:120]}; ext best {r['ext_best_views']}",
                      strength=strength(_f(r.get("own_best_views"))) if r.get("proven") == "True" else "weak", region_skew=r.get("region_skew")))
    p = os.path.join(REPO, "research/trumpglow/refs.csv")
    if os.path.exists(p):
        for r in csv.DictReader(open(p)):
            v = _f(r["views"])
            for t in re.split(r"\s*->\s*", r.get("hook_card") or ""):
                if t: E.append(dict(kind="hook", text=t, views=v, page=r["platform"], product=r.get("type", ""), source=f"external {r['url']}", formats=fmt_of(t), strength=strength(v), external=True))
            E.append(dict(kind="format", text=r.get("shot_list", ""), views=v, product=r.get("type", ""), source=f"external {r['url']}", strength=strength(v), external=True))
    E += trend_songs()
    # aggregate formats from own data
    for name in FORMATS:
        hits = [e for e in E if e["kind"] in ("hook", "caption") and name in (e.get("formats") or []) and not e.get("external")]
        if hits:
            b = max(hits, key=lambda e: e["views"] or 0)
            E.append(dict(kind="format", key=name, text=name, n=len(hits), views=b["views"], best=b["text"], source=b["source"], strength=strength(b["views"])))
    for i, e in enumerate(E): e["id"] = f"POC-{i:04d}"
    for xf in sorted(glob.glob(os.path.join(REPO, "poc", "extra", "*.json"))):   # D84: hand-curated competitor POC (stable ids) survives rebuilds
        E += json.load(open(xf))
    if write:
        os.makedirs(os.path.dirname(OUT), exist_ok=True); json.dump(E, open(OUT, "w"), indent=1, ensure_ascii=False)
    return E
TREND_MD = "/workspace/research/reference_library/christmas_songs_2026-10-19.md"
TREND_TTL_DAYS = 14
SLUG = {"Christmas (Baby Please Come Home)": "darlene_love_baby_please", "All I Want for Christmas Is You": "aiwfc", "Last Christmas (Single Version)": "last_christmas",
        "Rockin' Around the Christmas Tree": "rockin_around", "Let It Snow! Let It Snow! Let It Snow!": "let_it_snow", "Winter Wonderland": "winter_wonderland",
        "It's Beginning to Look a Lot Like Christmas": "beginning_to_look", "Underneath the Tree": "underneath_the_tree",
        "Have Yourself a Merry Little Christmas": "merry_little_christmas", "Jingle Bell Rock": "jingle_bell_rock"}
def _views(t):
    return [float(n) * (1e6 if u.upper() == "M" else 1e3) for n, u in re.findall(r"(\d+(?:\.\d+)?)\s*([MK])\b", t)]
def trend_songs(path=TREND_MD, observed="2026-10-19"):
    """D72 TREND PROOF: 7-day Christmas songs (mostly TikTok, Shazam in-points, lyrics unconfirmed) -> strength 'ok' (never 'strong'),
    expires observed + 14 days."""
    if not os.path.exists(path): return []
    exp = (datetime.date.fromisoformat(observed) + datetime.timedelta(days=TREND_TTL_DAYS)).isoformat(); out = []
    for line in open(path):
        c = [x.strip() for x in line.split("|")]
        if len(c) < 10 or not c[1].isdigit(): continue
        song, artist, inp, f0, ex, uses, trend, conf = c[2], c[3], c[4], c[5], c[6], c[7], c[8], c[9]
        m = re.search(r"(\d+):(\d+(?:\.\d+)?)", inp); ip = round(int(m.group(1)) * 60 + float(m.group(2)), 2) if m else (0.0 if "start" in inp.lower() else None)
        v = _views(ex); urls = re.findall(r"\((https?://[^)]+)\)", ex)
        out.append(dict(kind="song", key=SLUG.get(song, re.sub(r"\W+", "_", song.lower()).strip("_")), text=f"{artist} - {song}", in_point_s=ip, in_point_label=re.sub(r"\*", "", inp)[:120],
                        frame0=f0[:40], views=max(v) if v else 0, n_examples=len(urls), examples=urls[:5], trend=re.sub(r"\*", "", trend)[:80], confidence=conf[:60],
                        source=f"trend {os.path.basename(path)} (TikTok/IG 10/12-10/19, Shazam in-point, lyric unconfirmed)", proof_type="trend",
                        strength="ok", observed=observed, expires=exp))
    return out
def alive(e, today=None):
    """Trend proof decays: invalid after its expires date (re-run the trend scan to refresh)."""
    if not e.get("expires"): return True
    return (today or datetime.date.today()) <= datetime.date.fromisoformat(e["expires"])
def rank_songs(slug, today=None):
    """D72 song-ranking rule: (1) product-niche proof (own reels/drafts on this audience's products, or Ad Library matches for it),
    then (2) current trend proof (unexpired), then (3) other. Within a tier: views desc."""
    try:
        from . import audience_fit as AF; pks = AF.load(slug).get("product_keys") or []
    except Exception: pks = []
    rows = []
    for e in load():
        if e["kind"] != "song" or not e.get("key") or not alive(e, today): continue
        niche = any(pk in str(e.get("source", "")) for pk in pks) or slug in (e.get("slugs") or [])
        tier = "niche" if niche and e.get("proof_type") != "trend" else "trend" if e.get("proof_type") == "trend" else "other"
        rows.append(dict(e, tier=tier))
    order = {"niche": 0, "trend": 1, "other": 2}
    return sorted(rows, key=lambda e: (order[e["tier"]], -(e.get("views") or 0)))
def load():
    return json.load(open(OUT)) if os.path.exists(OUT) else build()
def search(q="", kind=None, min_views=0, fmt=None, limit=20):
    rx = re.compile(re.escape(q), re.I) if q else None
    r = [e for e in load() if (not kind or e["kind"] == kind) and (e.get("views") or 0) >= min_views
         and (not fmt or fmt in (e.get("formats") or []) or e.get("key") == fmt) and (not rx or rx.search(json.dumps(e, ensure_ascii=False)))]
    return sorted(r, key=lambda e: -(e.get("views") or 0))[:limit]
def cite(text, kind="hook"):
    """Best citation for a line: exact own text, else its proven format. None if unproven."""
    n = lambda s: re.sub(r"\W+", " ", s or "").strip().lower()
    ex = [e for e in load() if e["kind"] in ("hook", "caption") and n(e["text"]) == n(text)]
    if ex: return max(ex, key=lambda e: e["views"] or 0)
    fs = fmt_of(text)
    fm = [e for e in load() if e["kind"] == "format" and e.get("key") in fs]
    return max(fm, key=lambda e: e["views"] or 0) if fm else None
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "build": print(len(build()), "entries ->", OUT)
    else:
        for e in search(" ".join(sys.argv[1:])): print(e["id"], e["kind"], e.get("strength"), int(e.get("views") or 0), "|", e["text"][:70], "|", (e.get("source") or "")[:60])
