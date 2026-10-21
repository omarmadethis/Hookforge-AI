"""#5 SALES ATTRIBUTION (D87). READ-ONLY ShopifyQL aggregates only (no orders, no customers, no PII).
The agent runs QUERIES via the Shopify MCP run-analytics-query on the CURRENTLY connected store (never switch stores)
and saves each raw result JSON into analytics/data/shopify_utm/<YYYY-MM-DD>_<name>.json. This module parses those
files into per-video sales: sessions, checkouts, orders and net sales (last-click) keyed by utm_content = video_id.
Landing-page fallback (pre-UTM reels): social sessions per product landing path, shared across that product's reels
(labelled allocated=True, never mixed with tracked numbers)."""
import os, glob, json, pandas as pd
from .config import REPO
DIR = os.path.join(REPO, "analytics", "data", "shopify_utm")
QUERIES = {
    "utm_sessions": "FROM sessions SHOW sessions, sessions_that_completed_checkout GROUP BY utm_content, utm_source, utm_campaign SINCE -30d UNTIL today ORDER BY sessions DESC LIMIT 1000",
    "utm_sales": "FROM sales SHOW orders, net_sales GROUP BY utm_content, utm_source, utm_campaign WITH LAST_CLICK_ATTRIBUTION SINCE -30d UNTIL today ORDER BY orders__last_click DESC LIMIT 1000",
    "landing_social": "FROM sessions SHOW sessions, sessions_that_completed_checkout WHERE referrer_source = 'social' GROUP BY landing_page_path SINCE -30d UNTIL today ORDER BY sessions DESC LIMIT 200",
}
FORBIDDEN = ("customer_email", "customer_name", "order_id", "customer_id", "billing", "shipping_address", "phone")

def check_query(q):
    ql = q.lower()
    assert ql.lstrip().startswith("from "), "ShopifyQL read query only"
    bad = [f for f in FORBIDDEN if f in ql]
    if bad: raise ValueError(f"PII field in query: {bad}")
    return q

def _tbl(path):
    j = json.load(open(path))
    df = pd.DataFrame(j["rows"], columns=[c["name"] for c in j["columns"]])
    for c in df.columns:
        if c not in ("utm_content", "utm_source", "utm_campaign", "landing_page_path", "referrer_source"):
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def _latest(name):
    fs = sorted(glob.glob(os.path.join(DIR, f"*_{name}.json")))
    return _tbl(fs[-1]) if fs else None

def load_attribution():
    s, o = _latest("utm_sessions"), _latest("utm_sales")
    parts = []
    if s is not None: parts.append(s[s.utm_content.astype(str) != ""].groupby("utm_content")[["sessions", "sessions_that_completed_checkout"]].sum())
    if o is not None: parts.append(o[o.utm_content.astype(str) != ""].groupby("utm_content")[["orders__last_click", "net_sales__last_click"]].sum())
    if not parts: return pd.DataFrame(columns=["video_id"])
    df = pd.concat(parts, axis=1).reset_index().rename(columns={"utm_content": "video_id", "sessions": "shop_sessions",
         "sessions_that_completed_checkout": "shop_checkouts", "orders__last_click": "shop_orders", "net_sales__last_click": "shop_net_sales"})
    df["attribution"] = "utm_last_click"
    return df

def coverage():
    """How much traffic is UTM-tagged at all (drives whether per-reel numbers mean anything yet)."""
    s = _latest("utm_sessions")
    if s is None: return {}
    t = s.sessions.sum(); tagged = s[s.utm_content.astype(str) != ""].sessions.sum()
    return dict(sessions=int(t), utm_content_tagged=int(tagged), share=round(tagged / t, 4) if t else 0)
