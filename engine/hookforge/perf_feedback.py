"""D119 performance feedback loop. After a Buffer post is published, its stats (Buffer post analytics or Meta reel
insights) are ingested, logged per factor into ab_log, and turned into per-product weights for hooks (format),
captions and songs. Weights are read by concept_lab.rank (hook), fb_caption.generate (caption) and music.select (song).

  ingest(rows, source)  rows = [{post_id, video_id, product, page, format, caption, song, views, avg_watch_s, shares,
                         published_pt}]  -> learning/perf/stats.csv (dedup on post_id, latest snapshot wins) + ab_log rows
  reweight()            -> learning/perf/weights.json  {product: {hook|caption|song: {value: weight}}}
  weight(product, factor, value) -> multiplier in [0.5, 1.5], 1.0 when no data
  from_buffer(post) / from_meta(row) map a Buffer get_post analytics dict / results_feed outcomes row to a stats row.
Retired products (D117) are FULL reference data: their stats feed the pooled prior every active product is
shrunk toward; they get no weights of their own because they get no new content. Read-only: never calls Buffer/Meta
itself; the agent passes in what the read-only tools returned. Simulated with tests/fixtures/perf_stats.json."""
import os, json, datetime
import pandas as pd
from zoneinfo import ZoneInfo
from .config import REPO
from . import products as _products, ab_log

DIR = os.path.join(REPO, "learning", "perf")
FACTORS = {"hook": "format", "caption": "caption", "song": "song"}
PRIOR_N = 4            # pseudo-posts of pooled prior per value (shrinkage)
COLS = ["post_id", "video_id", "product", "page", "format", "caption", "song", "views", "avg_watch_s", "shares", "published_pt", "source", "ingested_pt"]

def _p(n): os.makedirs(DIR, exist_ok=True); return os.path.join(DIR, n)
def now(): return datetime.datetime.now(ZoneInfo("America/Los_Angeles")).isoformat(timespec="seconds")

def from_buffer(post, meta):
    """post = Buffer get_post result (published; statistics may be under 'statistics'/'analytics'); meta = the
    approval-queue item it came from (product, format, song, page) since Buffer does not know those."""
    st = post.get("statistics") or post.get("analytics") or {}
    return dict(post_id=post["id"], video_id=meta.get("video_id", post["id"]), product=meta["product"], page=meta.get("page", ""),
                format=meta.get("format", ""), caption=post.get("text", "")[:200], song=meta.get("song", ""),
                views=st.get("views") or st.get("plays") or st.get("impressions") or 0, avg_watch_s=st.get("avgWatchTime") or 0,
                shares=st.get("shares") or 0, published_pt=post.get("sentAt") or post.get("dueAt") or "")

def from_meta(r, meta):
    return dict(post_id=r.get("post_id") or r.get("reel_key"), video_id=r.get("video_id") or r.get("reel_key"), product=meta["product"],
                page=r.get("page", ""), format=meta.get("format", ""), caption=str(r.get("caption", ""))[:200], song=meta.get("song", ""),
                views=r.get("views") or 0, avg_watch_s=r.get("avg_watch_s") or 0, shares=r.get("shares") or 0, published_pt=r.get("posted_pt", ""))

def ingest(rows, source="buffer", log_ab=True):
    new = pd.DataFrame([dict(r, source=source, ingested_pt=now()) for r in rows], columns=COLS)
    f = _p("stats.csv"); old = pd.read_csv(f, dtype={"post_id": str}) if os.path.exists(f) else pd.DataFrame(columns=COLS)
    first = set(new.post_id) - set(old.post_id.astype(str))
    df = pd.concat([old, new]).drop_duplicates("post_id", keep="last"); df.to_csv(f, index=False)
    if log_ab:
        for r in new[new.post_id.isin(first)].itertuples():
            for fac, col in FACTORS.items():
                v = getattr(r, col)
                if isinstance(v, str) and v:
                    try: ab_log.log_variant(f"perf_{r.product}_{fac}", r.video_id, fac, v[:80], page=r.page, product=r.product)
                    except ValueError: pass
    return dict(rows=len(df), new=len(first))

def _score(df):
    """per-post score: views relative to that product's median (so a small page is not punished), x watch bonus"""
    df = df.copy(); df["views"] = pd.to_numeric(df.views, errors="coerce").fillna(0)
    med = df.groupby("product").views.transform("median").clip(lower=1)
    df["rel"] = (df.views / med).clip(upper=10); return df

def reweight():
    f = _p("stats.csv")
    if not os.path.exists(f): return {}
    df = _score(pd.read_csv(f)); act = set(_products.active()); out = {"_meta": dict(updated_pt=now(), posts=len(df),
           reference_products=sorted(set(df["product"]) - act), note="retired products feed the pooled prior only")}
    for fac, col in FACTORS.items():
        pooled = df.groupby(col).rel.agg(["sum", "count"])          # all products, incl. retired = reference corpus
        for pk in sorted(set(df["product"]) & act):
            g = df[df["product"] == pk].groupby(col).rel.agg(["sum", "count"])
            for v, r in g.iterrows():
                if not isinstance(v, str) or not v: continue
                pr = pooled.loc[v]; prior_mean = (pr["sum"] - r["sum"]) / max(pr["count"] - r["count"], 1) if pr["count"] > r["count"] else 1.0
                post = (r["sum"] + PRIOR_N * prior_mean) / (r["count"] + PRIOR_N)
                out.setdefault(pk, {}).setdefault(fac, {})[v] = dict(weight=round(min(1.5, max(0.5, post)), 3), n=int(r["count"]))
    json.dump(out, open(_p("weights.json"), "w"), indent=1); return out

def weight(product, factor, value):
    f = _p("weights.json")
    if not value or not os.path.exists(f): return 1.0
    return (json.load(open(f)).get(product, {}).get(factor, {}).get(str(value)) or {}).get("weight", 1.0)
