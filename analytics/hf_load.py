"""Adaptive loaders. Every frame returned carries the source file(s) it came from (PROVENANCE).

Reel table priority (first that exists wins):
  1. hookforge/data/hookforge.db, table `reels`       (teammate's DB, when built)
  2. hookforge/private/corpus/corpus.csv              (Phase A corpus, full)
  3. hookforge/engine/backtest/data/corpus_public.csv (Phase A corpus, shareable; legacy: analytics/data/reels.csv)
  4. team/hooks/hook_features.csv                     (raw team table, minimal fallback)
Enrichments (joined when present): first-frame features (team/hooks/hook_features.csv),
shot timing (team/body/reels_summary.csv, team/body/shots.csv), Insights (analytics/data/insights/*.csv),
Shopify aggregates (team/shopify/**), IG Insights note (team/instagram/merryjammies_ig_reels.md),
experiments (learning/experiments.csv, else analytics/schemas/experiments.example.csv).
"""
import os, re, glob, json, sqlite3, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
W = os.environ.get("HOOKFORGE_WORKSPACE", "/workspace")
T = os.path.join(W, "team")
PROVENANCE = []  # (panel/data, path, rows, note)

def _prov(what, path, rows, note=""):
    PROVENANCE.append(dict(data=what, path=os.path.relpath(path, W) if str(path).startswith(W) else str(path),
                           rows=int(rows), modified=pd.Timestamp(os.path.getmtime(path), unit="s", tz="UTC")
                           .tz_convert("America/Los_Angeles").strftime("%Y-%m-%d %H:%M PT") if os.path.exists(path) else "", note=note))

PAGE_NAMES = {"HJ": "HeatedJammies", "MJIG": "merry.jammies IG", "MGS": "Merry Glows", "MG": "Merry Glow",
              "MF": "MerryFires", "BH": "Brick Hood Shop", "MC": "Merry Carrier", "PV": "Purrventure"}
ALIASES = {"views": ["views", "plays", "view_count"], "posted_pt": ["posted_pt", "posted", "post_date", "posted_at"],
           "page_code": ["page_code", "code"], "format": ["format", "format_id", "format_ref"], "key": ["key", "corpus_key", "uid"], "hook_family": ["hook_family", "family"],
           "source": ["source", "origin"], "page": ["page", "page_name", "account"]}

def _adapt(df):
    low = {c.lower(): c for c in df.columns}
    for canon, al in ALIASES.items():
        if canon not in df.columns:
            hit = next((low[a] for a in al if a in low), None)
            df[canon] = df[hit] if hit else np.nan
    df["views"] = pd.to_numeric(df["views"], errors="coerce")
    if df["source"].isna().all(): df["source"] = "own"
    if df["page"].isna().all(): df["page"] = df["page_code"].map(PAGE_NAMES).fillna(df["page_code"])
    df["page"] = df["page"].fillna(df["page_code"])
    df["posted_dt"] = pd.to_datetime(df["posted_pt"], errors="coerce")
    if "post_hour" not in df.columns or df["post_hour"].isna().all(): df["post_hour"] = df["posted_dt"].dt.hour
    for c in ("category", "product", "platform", "archetype", "hook_text", "reel_id"):
        if c not in df.columns: df[c] = np.nan
    return df

def load_reels():
    db = os.path.join(REPO, "data", "hookforge.db")
    try:   # DB is the default once learning/db_review.json passed for the DB file on disk (engine/hookforge/reels_db.py)
        sys.path.insert(0, os.path.join(REPO, "engine")); from hookforge import reels_db
        if reels_db.db_is_default():
            df = reels_db.merged()
            _prov("reels (primary)", db, len(df), "hookforge.db (read-only) + corpus overlay for format/coded fields; review passed"); return _adapt(df), "hookforge.db"
        elif os.path.exists(db):
            PROVENANCE.append(dict(data="reels (primary)", path=db, rows=0, modified="", note="DB present but latest review not passed for this file; using corpus"))
    except Exception as e:
        PROVENANCE.append(dict(data="reels (primary)", path=db, rows=0, modified="", note=f"DB load failed ({e}); using corpus"))
    for p, label in ((os.path.join(REPO, "private", "corpus", "corpus.csv"), "corpus.csv (private)"),
                     (os.path.join(REPO, "engine", "backtest", "data", "corpus_public.csv"), "engine/backtest/data/corpus_public.csv (shareable)"),
                     (os.path.join(HERE, "data", "reels.csv"), "analytics/data/reels.csv (shareable, legacy path)")):
        if os.path.exists(p):
            df = pd.read_csv(p, low_memory=False)
            df = df[df.get("source", "own") != "library"] if "source" in df else df  # library = unlabelled (no views)
            _prov("reels (primary)", p, len(df), "Phase A corpus; library rows (no views) excluded"); return _adapt(df), label
    p = os.path.join(T, "hooks", "hook_features.csv"); df = pd.read_csv(p)
    df = df.rename(columns={"id": "reel_id", "opening_archetype": "archetype", "posted_pt": "posted_pt"})
    df["source"] = "own"; _prov("reels (primary)", p, len(df), "fallback: raw team table"); return _adapt(df), "hook_features.csv (fallback)"

def _norm_page(s): return re.sub(r"[^a-z0-9]", "", str(s).lower().replace("@", ""))
def sufkfix(s): return str(s).split("_")[-1]

def join_by_id_or_views(own, other, other_page_col, other_view_col, other_key_col, cols, prefix):
    """Attach `cols` from `other` to own reels by id suffix, else unique (page, views±2) match."""
    other = other.copy(); other["sufk"] = other[other_key_col].map(sufkfix); other["pgk"] = other[other_page_col].map(_norm_page)
    bysuf = {r.sufk: r for r in other.itertuples()}
    out = {c: [] for c in cols}; how = []
    for r in own.itertuples():
        m = bysuf.get(sufkfix(r.reel_id)) if isinstance(r.reel_id, str) else None
        h = "id"
        if m is None:
            cand = other[(other.pgk == _norm_page(r.page)) & ((other[other_view_col] - r.views).abs() <= 2)]
            m = next(cand.itertuples()) if len(cand) == 1 else None; h = "views" if m is not None else "none"
        for c in cols: out[c].append(getattr(m, c) if m is not None else np.nan)
        how.append(h)
    for c in cols: own[prefix + c] = out[c]
    own[prefix + "join"] = how
    return own

FF_COLS = ["product_pct_0", "product_visible_0", "contrast_0", "bright_0", "sat_0", "colorful_0", "people_n",
           "face_visible_0", "shock_face_0", "flow_0_1", "flow_1_3", "first_cut_s", "audio_start_s", "res_1440plus",
           "night_18_04", "product_day", "n_words", "n_emoji", "text_pos"]
SHOT_COLS = ["dur", "n_shots", "avg_shot", "first_cut", "last_shot_dur", "lufs", "tempo", "luma", "sat"]

def enrich(reels):
    own = reels[reels.source == "own"].copy()
    p = os.path.join(T, "hooks", "hook_features.csv")
    if os.path.exists(p):
        h = pd.read_csv(p); cols = [c for c in FF_COLS if c in h.columns]
        own = join_by_id_or_views(own, h, "page", "views", "id", cols, "ff_")
        _prov("first-frame features", p, len(h), f"joined to {int((own.ff_join != 'none').sum())}/{len(own)} own reels")
    p = os.path.join(T, "body", "reels_summary.csv")
    if os.path.exists(p):
        b = pd.read_csv(p); cols = [c for c in SHOT_COLS if c in b.columns]
        own = join_by_id_or_views(own, b, "page", "views", "key", cols + ["key"], "sh_")
        _prov("shot timing (per reel)", p, len(b), f"joined to {int((own.sh_join != 'none').sum())}/{len(own)} own reels")
    return own

def load_shots():
    p = os.path.join(T, "body", "shots.csv")
    if not os.path.exists(p): return None
    s = pd.read_csv(p); _prov("shot timing (per shot)", p, len(s)); return s

def load_feature_screen():
    p = os.path.join(T, "hooks", "feature_screen_census.csv")
    if not os.path.exists(p): return None
    d = pd.read_csv(p); _prov("adjusted first-3s effects (team model)", p, len(d), "page FE + product_day + resolution; hooks REPORT §1")
    lo_hi = d["ci95"].astype(str).str.split("–", expand=True)
    d["lo"] = pd.to_numeric(lo_hi[0], errors="coerce"); d["hi"] = pd.to_numeric(lo_hi[1], errors="coerce")
    return d

def load_insights():
    files = sorted(glob.glob(os.path.join(HERE, "data", "insights", "*.csv")))
    if not files: return None
    d = pd.concat([pd.read_csv(f, dtype={"post_id": str}) for f in files], ignore_index=True)
    for f in files: _prov(f"Insights ({os.path.basename(f)[:-4]})", f, sum(1 for _ in open(f)) - 1, "ingest_insights.py output")
    d["posted_dt"] = pd.to_datetime(d["posted_pt"], errors="coerce")
    return d

def load_ig_note():
    """Parse the 6-reel IG Insights table (shares, saves, profile visits) from the team note."""
    p = os.path.join(T, "instagram", "merryjammies_ig_reels.md")
    if not os.path.exists(p): return None
    from ingest_insights import num
    rows = []
    for line in open(p):
        parts = [x.strip() for x in line.split("|")]
        if len(parts) == 9 and re.match(r"^[A-Za-z0-9_-]{8,}$", parts[0]):
            rows.append(dict(code=parts[0], date=parts[1], plays=num(parts[2]), likes=num(parts[3]), comments=num(parts[4]),
                             shares=num(parts[5]), saves=num(parts[6]), reach=num(parts[7]),
                             profile_visits=num(parts[8].split(" ")[0])))
    d = pd.DataFrame(rows); _prov("IG Insights (6 biggest reels)", p, len(d), "logged-in capture 2026-10-18"); return d

STORES = {  # store label -> (daily file, net column, hourly file, page codes it sells for)
    "Merry Jammies": ("shopify/daily.csv", "net_sales", "shopify/hourly_pt.csv", ["HJ", "MJIG"]),
    "Merry Glow": ("shopify/merryglow/daily.csv", "net_sales", "shopify/merryglow/hourly_pt.csv", ["MG"]),
    "Brick Hood": ("shopify/brickhood/daily_pt.csv", "net", "shopify/brickhood/hourly_pt.csv", ["BH"]),
}

def load_store_daily():
    out = []
    for store, (f, netc, _, _) in STORES.items():
        p = os.path.join(T, f)
        if not os.path.exists(p): continue
        d = pd.read_csv(p)
        if "day" not in d.columns: d = d.rename(columns={d.columns[0]: "day"})
        d = d.rename(columns={netc: "net"}); d["store"] = store; d["day"] = pd.to_datetime(d["day"])
        out.append(d[["store", "day", "orders", "net", "sessions"]]); _prov(f"Shopify daily ({store})", p, len(d), "aggregates only")
    return pd.concat(out, ignore_index=True) if out else None

def load_store_hourly():
    out = []
    for store, (_, _, f, _) in STORES.items():
        p = os.path.join(T, f)
        if not os.path.exists(p): continue
        d = pd.read_csv(p)
        if "t" not in d.columns: d = d.rename(columns={d.columns[0]: "t"})
        d["t"] = pd.to_datetime(d["t"]); d["store"] = store
        out.append(d[["store", "t", "orders", "sessions"]]); _prov(f"Shopify hourly PT ({store})", p, len(d), "aggregates only")
    return pd.concat(out, ignore_index=True) if out else None

def load_family_per1k():
    out = []
    specs = [("Merry Jammies", "shopify/family_estimates.csv", "n_reels", "orders_per_1k", "p10", "p90", "rev_per_1k", "p10–p90 over windows"),
             ("Merry Glow", "shopify/merryglow/family_estimates.csv", "n", "orders_per_1k", None, None, "net_per_1k", "allocation lo/hi in orders"),
             ("Brick Hood", "shopify/brickhood/family_estimates.csv", "reels", "orders_1k", "lo_1k", "hi_1k", "net_1k", "allocation lo/hi")]
    for store, f, nc, oc, lo, hi, nc2, note in specs:
        p = os.path.join(T, f)
        if not os.path.exists(p): continue
        d = pd.read_csv(p)
        o = pd.DataFrame(dict(store=store, family=d["family"], n_reels=d[nc], views=d["views"], orders_per_1k=d[oc],
                              lo=d[lo] if lo else (d["lo"] / d["views"] * 1000 if "lo" in d else np.nan),
                              hi=d[hi] if hi else (d["hi"] / d["views"] * 1000 if "hi" in d else np.nan), net_per_1k=d[nc2]))
        out.append(o); _prov(f"Shopify per-hook-family allocation ({store})", p, len(d), note)
    return pd.concat(out, ignore_index=True) if out else None

def load_experiments():
    real = os.path.join(REPO, "learning", "experiments.csv")
    ex = os.path.join(HERE, "schemas", "experiments.example.csv")
    if os.path.exists(real):
        d = pd.read_csv(real); _prov("experiments", real, len(d)); return d, False
    d = pd.read_csv(ex); _prov("experiments (EXAMPLE schema only)", ex, len(d), "learning/experiments.csv not created yet"); return d, True

def taxonomy():
    import sys
    sys.path.insert(0, os.path.join(REPO, "engine"))
    try:
        from hookforge.taxonomy import FORMAT_TITLES
        return FORMAT_TITLES
    except Exception:
        return {}

def shopify_raw_total(rel, col):
    """Sum one column of a raw ShopifyQL result saved by the Shopify workstream (store-timezone days)."""
    import json as _j
    p = os.path.join(T, rel)
    if not os.path.exists(p): return np.nan
    s = open(p).read(); j = _j.loads(s[s.find('{"query"'):s.rfind('}') + 1])
    cols = [c["name"] for c in j["columns"]]; i = cols.index(col)
    _prov(f"Shopify raw {col} (cross-check)", p, len(j["rows"]), "ShopifyQL output, store timezone")
    return float(sum(float(r[i] or 0) for r in j["rows"]))
