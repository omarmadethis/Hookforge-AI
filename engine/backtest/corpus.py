"""Phase A: build the unified reel corpus (every reel we have + metadata + outcome labels).

Writes:
  private/corpus/corpus.csv     full rows incl. reel IDs/URLs/page names (gitignored)
  engine/backtest/data/corpus_public.csv  shareable: anonymised keys, no IDs, relative sales only

Sources (all read-only):
  own posted reels  : team/hooks/hook_features.csv (+ manifest video paths), team/body/reels_summary.csv,
                      Insights CSVs (merryglow/, fb2/), IG insights note, Shopify reel allocations
  external 1M-class : team/external/external_reels.csv (+ videos/)
  viral research    : team/viral_research/work/*.mp4 (metadata from its REPORT)
  library finished  : library/index.csv  (unlabelled; FEMBOY TITS folder + bank image excluded)
  reference library : research/reference_library/index.csv  (auto-included when it exists)
"""
import os, sys, json, re, hashlib
import pandas as pd, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from hookforge.taxonomy import format_of, code_psych, norm_category, PSYCH
from hookforge.config import REPO

W = "/workspace"
EXCLUDE = re.compile(r"FEMBOY|IMG_5172", re.I)
PAGE_CODE = {"HeatedJammies": "HJ", "merry.jammies IG": "MJIG", "Merry Glows": "MGS", "Merry Glow": "MG",
             "MerryFires": "MF", "Brick Hood Shop": "BH", "Merry Carrier": "MC", "Purrventure": "PV"}

def _f(x):
    m = re.match(r"^\s*([\d.]+)\s*([KkMm])\s*$", str(x))
    if m: return float(m.group(1)) * (1e3 if m.group(2) in "Kk" else 1e6)
    try:
        x = float(str(x).replace("%", "").replace(",", "").replace("s", ""))
        return x if np.isfinite(x) else np.nan
    except Exception:
        return np.nan

def own():
    h = pd.read_csv(f"{W}/team/hooks/hook_features.csv")
    man = {m["id"]: m for m in json.load(open(f"{W}/team/hooks/manifest.json"))}
    body = pd.read_csv(f"{W}/team/body/reels_summary.csv")
    body["rid"] = body["key"].str.replace(r"^(hj|ig|mgs|mg|mf|bh|mc|pv)_", "", regex=True)
    bmap = {r.rid: r for r in body.itertuples()}
    # sales: Merry Jammies by reel id, MG/BH by (page, views)
    mj = pd.read_csv(f"{W}/team/shopify/reel_alloc.csv"); mj["id"] = mj["id"].astype(str)
    mjs = {r.id: r for r in mj.itertuples()}
    mg = pd.read_csv(f"{W}/team/shopify/merryglow/reel_alloc.csv")
    bh = pd.read_csv(f"{W}/team/shopify/brickhood/reels.csv")
    ig = _ig_insights()
    rows = []
    counters = {}
    for r in h.sort_values("views", ascending=False).itertuples():
        code = PAGE_CODE.get(r.page, "X"); counters[code] = counters.get(code, 0) + 1
        rid = str(r.id).replace("bh_post", "").replace("mg_post", "")
        b = bmap.get(str(r.id)) or bmap.get(rid) or _bmatch(body, r)
        fmt = format_of(r.hook_family, r.opening_archetype, r.hook_text, bool(getattr(r, "vo_321", 0) == 1))
        row = dict(key=f"{code}-{counters[code]:02d}", source="own", platform=r.platform, page=r.page, page_code=code,
                   reel_id=str(r.id), url=r.url, file=(man.get(r.id) or {}).get("video"), category=norm_category(r.category),
                   product=r.product, views=r.views, posted_pt=r.posted_pt, post_hour=r.post_hour, page_day=r.page_day,
                   product_day=r.product_day, hook_text=r.hook_text, hook_family=r.hook_family, archetype=r.opening_archetype,
                   format=fmt, multi_card=r.multi_card_text, product_pct_0_coded=r.product_pct_0,
                   product_visible_0_coded=r.product_visible_0, people_n=r.people_n, three_sec_rate=r.three_sec_rate,
                   avg_watch_s=r.insights_avg_watch_s, caption=r.caption, caption_link=r.caption_link, audio=r.audio,
                   res_served=r.res, organic=1, paid_flag=0)
        if b is not None:
            row.update(avg_watch_pct=_f(getattr(b, "pct", np.nan)), completion=_f(getattr(b, "completion", np.nan)),
                       dropoff_s=_drop(getattr(b, "dropoff", "")), song=getattr(b, "song_match", None),
                       song_offset=getattr(b, "song_offset", None), served_codec=getattr(b, "served_codec", None))
        s = mjs.get(rid)
        if s is not None and r.page == "HeatedJammies":
            row.update(orders_per_1k=s.orders_per_1k, net_per_1k=s.rev_per_1k, sessions_per_1k=s.sessions_per_1k, sales_store="MJ")
        if r.page == "Merry Glow":
            m = mg[(mg.views - r.views).abs() < 2]
            if len(m): row.update(orders_per_1k=m.orders_per_1k.iloc[0], net_per_1k=m.net_per_1k.iloc[0], sessions_per_1k=m.sessions_per_1k.iloc[0], sales_store="MG")
        if r.page == "Brick Hood Shop":
            m = bh[(bh.views - r.views).abs() < 2]
            if len(m): row.update(orders_per_1k=m.o_per_1k.iloc[0], net_per_1k=m.n_per_1k.iloc[0], sessions_per_1k=m.s_per_1k.iloc[0], sales_store="BH")
        if r.platform == "IG":
            code_ = str(r.id).split("_")[-1]          # ids look like ig_40.3K_<shortcode>
            if code_ in ig: row.update(ig[code_]); ig[code_]["_used"] = True
        row.update(code_psych(r.hook_text, fmt, r.opening_archetype, caption=str(r.caption)))
        rows.append(row)
    # IG reels that exist only in the IG Insights capture (6 biggest, Sep 7-20): add as own rows (no video file on disk)
    igpage = next((r["page"] for r in rows if r["platform"] == "IG"), "merry.jammies IG")
    igcode = next((r["page_code"] for r in rows if r["platform"] == "IG"), "MJIG")
    for code_, d in sorted(ig.items(), key=lambda kv: -(kv[1].get("ig_plays") or 0)):
        if d.get("_used"): continue
        counters[igcode] = counters.get(igcode, 0) + 1
        row = dict(key=f"{igcode}-{counters[igcode]:02d}", source="own", platform="IG", page=igpage, page_code=igcode,
                   reel_id=f"ig_{code_}", url=f"https://www.instagram.com/reel/{code_}/", file=None, category="wearable_gift",
                   product="HeatedJammies robe", views=d.get("ig_plays"), posted_pt=d.get("posted_pt"), hook_text="", hook_family="",
                   archetype="", format="F99", organic=1, paid_flag=0, insights_only=1, note=d.get("note", ""))
        row.update({k: v for k, v in d.items() if not k.startswith("_") and k not in ("posted_pt", "note")})
        row.update(code_psych("", "F99", "", caption=str(d.get("note", ""))))
        rows.append(row)
    return rows

def _bmatch(body, r):
    m = body[(body.page == r.page) & ((body.views - r.views).abs() < 2)]
    return next(m.itertuples()) if len(m) == 1 else None

def _drop(s):
    m = re.search(r"(\d+):(\d+)", str(s)); return int(m.group(1)) * 60 + int(m.group(2)) if m else np.nan

def _ig_insights():
    """Shares/profile visits for the 6 biggest IG reels (team/instagram note)."""
    out = {}
    for line in open(f"{W}/team/instagram/merryjammies_ig_reels.md"):
        p = [x.strip() for x in line.split("|")]
        if len(p) >= 9 and re.match(r"^[A-Za-z0-9_-]{8,}$", p[0]):
            n = lambda x: _f(x)
            note = re.search(r"\((.*)\)", p[8]); mon, day = p[1].split()
            out[p[0]] = dict(ig_plays=n(p[2]), likes=n(p[3]), comments=n(p[4]), shares=n(p[5]), saves=n(p[6]),
                             reach=n(p[7]), profile_visits=n(p[8].split(" ")[0]),
                             posted_pt=f"2026-{['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'].index(mon)+1:02d}-{int(day):02d}",
                             note=note.group(1) if note else "")
    return out

def external():
    e = pd.read_csv(f"{W}/team/external/external_reels.csv")
    rows = []
    for i, r in enumerate(e.itertuples(), 1):
        fmt = format_of(r.hook_family, "", r.hook_text)
        f = f"{W}/team/external/{r.local_file}" if isinstance(r.local_file, str) else None
        row = dict(key=f"EXT-{i:02d}", source="external", platform=r.platform, page=r.account, page_code="EXT",
                   reel_id=None, url=r.url, file=f if f and os.path.exists(f) else None, category=norm_category(r.product_category),
                   product=r.product_category, views=r.views, posted_pt=r.posted, hook_text=r.hook_text, hook_family=r.hook_family,
                   archetype="", format=fmt, caption=r.caption, audio=r.audio, likes=r.likes, shares=r.shares,
                   paid_flag=int(str(r.paid_or_spark_flag) == "True"), organic=int(str(r.paid_or_spark_flag) != "True"),
                   hook_visual=r.hook_visual, body_desc=r.body)
        row.update(code_psych(r.hook_text, fmt, "", body_hint=str(r.body), caption=str(r.caption)))
        rows.append(row)
    return rows

RESEARCH = [  # from team/viral_research/REPORT.md (counts as shown Oct 18)
    ("ig_DegGRHtMucS.mp4", "Instagram", "merryglow.official", 755000, "IKEA X Christmas 🎄🎁", "store_x_brand unveil", "projector"),
    ("ig_DemwMq0sB5r.mp4", "Instagram", "merryglow.official", 198000, "do NOT show this to a Christmas mom...😱🎄", "dont_show_recipient", "projector"),
    ("tt_cyber.gun1.mp4", "TikTok", "cyber.gun1", 374200, "\"Kids are hard to gift\" 🎄🔫", "gift_difficulty", "laser toy"),
    ("tt_deseos.del.polo.n.mp4", "TikTok", "deseos.del.polo.n", 2200000, "COSTCO X Navidad 🎄🎁", "store_x_brand unveil", "projector"),
    ("tt_grumpyriderr.mp4", "TikTok", "grumpyriderr", 211100, "Christmas HATERS... this is for YOU", "audience_callout", "pet harness"),
    ("tt_snugbaby00.mp4", "TikTok", "snugbaby00", 488400, "The perfect gift for BABY MOM doesn't exi-", "cutoff_word", "baby hoodie"),
    ("tt_whovilleheist.mp4", "TikTok", "whovilleheist", 145300, "No le enseñes esto a un amante de la NAVIDAD 😩", "dont_show (holiday-lover)", "curtain lights"),
]

def research():
    rows = []
    for i, (fn, pl, acct, v, hook, fam, prod) in enumerate(RESEARCH, 1):
        fmt = format_of(fam, "", hook)
        row = dict(key=f"VR-{i:02d}", source="viral_research", platform=pl, page=acct, page_code="EXT", file=f"{W}/team/viral_research/work/{fn}",
                   category=norm_category(prod), product=prod, views=v, hook_text=hook, hook_family=fam, format=fmt, organic=1, paid_flag=0)
        row.update(code_psych(hook, fmt)); rows.append(row)
    return rows

def library():
    l = pd.read_csv(f"{W}/library/index.csv")
    l = l[(l.kind == "finished") & (l.status == "ok") & ~l.folder.str.contains(EXCLUDE) & ~l.name.str.contains(EXCLUDE)]
    rows = []
    for i, r in enumerate(l.itertuples(), 1):
        if not isinstance(r.local_path, str) or not os.path.exists(r.local_path): continue
        txt = r.ocr_first3s if isinstance(r.ocr_first3s, str) else ""
        hook = txt.split("|")[0].strip()
        fmt = format_of("", "", hook)
        row = dict(key=f"LIB-{i:03d}", source="library", platform="", page="", page_code="LIB", file=r.local_path,
                   category=norm_category(r.folder + " " + r.name), product=r.folder, views=np.nan, hook_text=hook, format=fmt,
                   organic=1, paid_flag=0, lib_folder=r.folder, lib_name=r.name, dup_of=r.dup_of)
        row.update(code_psych(hook, fmt)); rows.append(row)
    return rows

def reference_library():
    p = f"{W}/research/reference_library/index.csv"
    if not os.path.exists(p): return []
    d = pd.read_csv(p); cols = {c.lower(): c for c in d.columns}
    g = lambda r, *names: next((getattr(r, cols[n]) for n in names if n in cols), None)
    rows = []
    for i, r in enumerate(d.itertuples(index=False), 1):
        r = r._asdict() if hasattr(r, "_asdict") else r
        get = lambda *n: next((r.get(cols[k]) for k in n if k in cols), None)
        f = get("video_file", "local_file", "file", "path", "video", "local_path")
        if f and not os.path.isabs(str(f)): f = os.path.join(os.path.dirname(p), str(f))
        hook = str(get("on_screen_hook_text", "hook_text", "hook", "on_screen_text") or "")
        fam = str(get("format", "hook_family", "family") or "")
        fmt = format_of(fam, "", hook)
        row = dict(key=f"REF-{i:03d}", source="reference_library", platform=get("platform"), page=get("page_handle", "account", "page", "handle"),
                   page_code="EXT", url=get("url", "link"), file=f if f and os.path.exists(str(f)) else None,
                   category=norm_category(str(get("category", "product_category", "product") or "")), product=get("product", "product_category"),
                   views=_f(get("views", "plays", "view_count")), posted_pt=get("post_date", "posted", "date", "posted_at"), hook_text=hook,
                   hook_family=fam, format=fmt, organic=1 - int(str(get("is_paid", "paid", "paid_flag", "is_ad") or "").lower() in ("true", "1", "yes")),
                   caption=get("caption"), audio=get("audio", "music"), shares=_f(get("shares")), likes=_f(get("likes")))
        row["paid_flag"] = 1 - row["organic"]
        row.update(code_psych(hook, fmt)); rows.append(row)
    return rows

def build():
    rows = own() + external() + research() + reference_library() + library()
    df = pd.DataFrame(rows)
    df["views"] = df["views"].map(_f)
    df["log10_views"] = np.log10(df["views"].astype(float))
    os.makedirs(f"{REPO}/private/corpus", exist_ok=True)
    df.to_csv(f"{REPO}/private/corpus/corpus.csv", index=False)
    share = df[df.source != "library"].drop(columns=[c for c in ["reel_id", "url", "file", "page", "caption", "dup_of", "lib_name"] if c in df.columns])
    share.loc[share.source != "own", "page_code"] = share.loc[share.source != "own", "source"]
    share = share.drop(columns=[c for c in ["net_per_1k"] if False])
    share.to_csv(f"{REPO}/engine/backtest/data/corpus_public.csv", index=False)
    print(df.groupby("source").agg(n=("key", "size"), with_file=("file", lambda s: s.notna().sum()), with_views=("views", lambda s: s.notna().sum())))
    print(df[df.source != "library"].format.value_counts().to_string())
    return df

if __name__ == "__main__":
    build()
