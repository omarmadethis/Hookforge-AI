"""D91 #4 A/B VARIANT LOG tied to results_feed (learning/results/outcomes.csv, keyed by video_id) and sales_attribution
(utm_content = video_id, aggregates only). One test = one parent + variants that differ in ONE declared factor.
  ab_log.log_variant(test_id, video_id, factor, value, parent=None, page="", product="")  -> learning/ab_variants.csv
  ab_log.results(test_id)  -> per-variant views / avg watch / day-1 velocity + shop sessions/orders/net sales, and a
     verdict only when every variant has >= MIN_VIEWS views (else 'insufficient data'). Sales come only from the UTM
     last-click attribution; landing-page allocations are never mixed in."""
import os, csv, datetime
import pandas as pd
from zoneinfo import ZoneInfo
from .config import REPO
from . import sales_attribution

LOG = os.path.join(REPO, "learning", "ab_variants.csv")
OUTCOMES = os.path.join(REPO, "learning", "results", "outcomes.csv")
FIELDS = ["logged_pt", "test_id", "video_id", "parent", "factor", "value", "page", "product"]
MIN_VIEWS = 500

def log_variant(test_id, video_id, factor, value, parent=None, page="", product=""):
    rows = pd.read_csv(LOG, dtype=str) if os.path.exists(LOG) else pd.DataFrame(columns=FIELDS)
    t = rows[rows.test_id == test_id]
    if video_id in set(t.video_id): raise ValueError(f"{video_id} already in {test_id}")
    if len(t) and set(t.factor) != {factor}: raise ValueError(f"{test_id} tests '{t.factor.iloc[0]}'; one factor per test")
    new = not os.path.exists(LOG)
    with open(LOG, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        if new: w.writeheader()
        w.writerow(dict(logged_pt=datetime.datetime.now(ZoneInfo("America/Los_Angeles")).isoformat(timespec="seconds"), test_id=test_id,
                        video_id=video_id, parent=parent or "", factor=factor, value=value, page=page, product=product))

def results(test_id, outcomes=None, sales=None):
    v = pd.read_csv(LOG, dtype=str); v = v[v.test_id == test_id]
    if v.empty: raise KeyError(test_id)
    o = outcomes if outcomes is not None else (pd.read_csv(OUTCOMES) if os.path.exists(OUTCOMES) else pd.DataFrame(columns=["video_id"]))
    o = o[o.video_id.notna()].copy(); o["video_id"] = o.video_id.astype(str)
    perf = o.groupby("video_id").agg(views=("views", "sum"), avg_watch_s=("avg_watch_s", "mean"), views_d1=("views_d1", "sum"), n_reels=("video_id", "size")) if len(o) else pd.DataFrame()
    s = sales if sales is not None else sales_attribution.load_attribution()
    s = s.set_index("video_id") if "video_id" in s.columns and len(s) else pd.DataFrame()
    df = v.set_index("video_id")[["factor", "value", "parent"]].join(perf, how="left").join(s[[c for c in ("shop_sessions", "shop_orders", "shop_net_sales") if c in s.columns]] if len(s) else pd.DataFrame(index=v.video_id), how="left")
    for c in ("views", "views_d1", "shop_sessions", "shop_orders", "shop_net_sales"):
        if c not in df: df[c] = 0.0
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    df["orders_per_1k_views"] = (df.shop_orders / df.views.where(df.views > 0) * 1000).round(3)
    ok = len(df) >= 2 and (df.views >= MIN_VIEWS).all()
    verdict = "insufficient data" if not ok else dict(
        by_sales=df.shop_net_sales.idxmax() if df.shop_net_sales.max() > 0 else None, by_views=df.views.idxmax(), by_watch=df.avg_watch_s.idxmax() if df.avg_watch_s.notna().any() else None)
    return dict(test_id=test_id, factor=v.factor.iloc[0], table=df.reset_index(), verdict=verdict)
