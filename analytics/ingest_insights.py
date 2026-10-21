"""Ingest a Facebook/Instagram page Insights export (CSV) into Hookforge analytics.

One command per page (e.g. when HeatedJammies access arrives):

    python analytics/ingest_insights.py --page "HeatedJammies" --code HJ path/to/export.csv
    python analytics/build_dashboard.py

Accepts any of the shapes we have seen:
  * Meta Business Suite "Content" export (Post ID, Publish time, Views, Reach, 3-second video views,
    Average Seconds viewed, Shares, Link clicks, ...)
  * the team's browser-scraped Insights tables (caption, date_2026, views, viewers, 3s_views,
    avg_watch_time "7s", watch_time "1h 36m", ...)
  * per-reel retention tables (avg_pct_watched, completion_rate, biggest_dropoff "0:05", ...)
Columns are matched by alias (case/space-insensitive); unknown columns are ignored, missing ones
stay empty. Never invents values. Page IDs are dropped on purpose (scrub rule).

Output: analytics/data/insights/<CODE>.csv (one canonical row per reel, merged with earlier
ingests: a newer export overwrites older numbers for the same reel, new reels are appended).

`--seed-existing` re-ingests the team's existing Insights files (see SEED below).
Times in exports are assumed to be Pacific (Omar's Business Suite locale); use --tz-offset-hours
if an export was made in another zone.
"""
import argparse, os, re, sys, datetime as dt
import pandas as pd, numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.environ.get("HOOKFORGE_INSIGHTS_DIR", os.path.join(HERE, "data", "insights"))
W = "/workspace"

CANON = ["page_code", "page", "reel_key", "post_id", "reel_url", "posted_pt", "hook_text", "caption",
         "duration_s", "views", "viewers", "impressions", "three_sec_views", "three_sec_rate", "one_min_views",
         "avg_watch_s", "watch_time_s", "avg_pct_watched", "completion_rate", "biggest_dropoff_s",
         "engagement", "reactions", "comments", "shares", "saves", "follows", "profile_visits", "clicks",
         "link_clicks", "non_follower_pct", "distribution", "source_file", "ingested_pt"]

ALIASES = {  # canonical -> accepted header spellings (normalised: lowercase, alnum only)
    "post_id": ["postid", "videoid", "reelid", "id"],
    "reel_url": ["reelurl", "permalink", "url", "link"],
    "posted_pt": ["publishtime", "date2026", "date", "posted", "publishedtime", "createdtime", "time"],
    "hook_text": ["hooktext", "thumbtext", "title", "reel"],
    "caption": ["caption", "description", "message"],
    "duration_s": ["durationsec", "duration", "lengths"],
    "views": ["views", "plays", "videoviews", "reelsplays", "totalplays"],
    "viewers": ["viewers", "viewersreach", "reach", "accountsreached"],
    "impressions": ["impressions"],
    "three_sec_views": ["3secondvideoviews", "3sviews", "threesecviews", "3secviews"],
    "one_min_views": ["1minutevideoviews", "1minviews"],
    "avg_watch_s": ["averagesecondsviewed", "avgwatchtime", "averagewatchtime", "avgwatchs", "averagewatchtimes"],
    "watch_time_s": ["secondsviewed", "watchtime", "totalwatchtime"],
    "avg_pct_watched": ["avgpctwatched", "averagepercentagewatched", "avgpercentwatched"],
    "completion_rate": ["completionrate"],
    "biggest_dropoff_s": ["biggestdropoff"],
    "engagement": ["engagement", "interactions"],
    "reactions": ["reactions", "likes"],
    "comments": ["comments"],
    "shares": ["shares"],
    "saves": ["saves"],
    "follows": ["follows", "follow"],
    "profile_visits": ["profilevisits"],
    "clicks": ["totalclicks", "clicks"],
    "link_clicks": ["linkclicks"],
    "non_follower_pct": ["nonfollowerspct", "nonfollowerpct"],
    "distribution": ["distribution"],
}
DROP = re.compile(r"page ?id|account ?id|user ?id", re.I)  # scrub: never stored

def _norm(h): return re.sub(r"[^a-z0-9]", "", str(h).lower())

def num(x):
    """'1,029' -> 1029, '4.6M' -> 4.6e6, '59%' -> 59, '--' -> NaN. No guessing beyond that."""
    if x is None or (isinstance(x, float) and np.isnan(x)): return np.nan
    s = str(x).strip().replace(",", "")
    if s in ("", "--", "-", "nan", "not available", "None"): return np.nan
    m = re.match(r"^([+-]?[\d.]+)\s*([KkMm])?\s*%?$", s)
    if not m: return np.nan
    v = float(m.group(1)); return v * {"k": 1e3, "m": 1e6}.get((m.group(2) or "").lower(), 1)

def dur_s(x):
    """'7s' -> 7, '1h 36m' -> 5760, '102:19:26' -> h:m:s, '0:05' -> m:s, '3d 20h' -> ..."""
    if x is None or (isinstance(x, float) and np.isnan(x)): return np.nan
    s = str(x).strip()
    if s in ("", "--", "-"): return np.nan
    if re.match(r"^\d+(\.\d+)?$", s): return float(s)
    if re.match(r"^\d+:\d+(:\d+)?$", s):
        p = [int(v) for v in s.split(":")]
        return p[0] * 60 + p[1] if len(p) == 2 else p[0] * 3600 + p[1] * 60 + p[2]
    tot, hit = 0.0, False
    for v, u in re.findall(r"([\d.]+)\s*([dhms])", s):
        tot += float(v) * {"d": 86400, "h": 3600, "m": 60, "s": 1}[u]; hit = True
    return tot if hit else np.nan

def parse_time(x, year, tz_offset_h=0):
    if x is None or (isinstance(x, float) and np.isnan(x)): return None
    s = str(x).strip()
    fmts = ["%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y %H:%M", "%m/%d/%Y %I:%M %p", "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S", "%b %d %I:%M %p", "%b %d %Y %I:%M %p", "%b %d"]
    for f in fmts:
        try:
            t = dt.datetime.strptime(s, f) if "%Y" in f else dt.datetime.strptime(f"{year} {s}", "%Y " + f)
            if t.tzinfo is not None:  # explicit zone -> convert to PT (UTC-7 during PDT, UTC-8 after Nov 1)
                t = t.astimezone(dt.timezone(dt.timedelta(hours=-7))).replace(tzinfo=None)
            t = t + dt.timedelta(hours=tz_offset_h)
            return t.strftime("%Y-%m-%d %H:%M")
        except ValueError:
            continue
    return None

def canonicalise(df, page, code, src, year=2026, tz_offset_h=0):
    cols = {_norm(c): c for c in df.columns if not DROP.search(str(c))}
    out = pd.DataFrame(index=df.index)
    for canon, al in ALIASES.items():
        hit = next((cols[a] for a in al if a in cols), None)
        out[canon] = df[hit] if hit is not None else np.nan
    # free-text hook in "caption" when there is no separate hook column
    for c in ("views", "viewers", "impressions", "three_sec_views", "one_min_views", "engagement", "reactions",
              "comments", "shares", "saves", "follows", "profile_visits", "clicks", "link_clicks", "duration_s",
              "avg_pct_watched", "completion_rate", "non_follower_pct"):
        out[c] = out[c].map(num)
    for c in ("avg_watch_s", "watch_time_s", "biggest_dropoff_s"):
        out[c] = out[c].map(dur_s)
    out["posted_pt"] = out["posted_pt"].map(lambda x: parse_time(x, year, tz_offset_h))
    out["post_id"] = out["post_id"].map(lambda x: None if pd.isna(x) else re.sub(r"\.0$", "", str(x)))
    rid = out["reel_url"].astype(str).str.extract(r"/reel/(\d+)")[0]
    out["post_id"] = out["post_id"].where(out["post_id"].notna(), rid)
    out["three_sec_rate"] = out["three_sec_views"] / out["views"]
    out["page"], out["page_code"], out["source_file"] = page, code, os.path.relpath(src, W) if src.startswith(W) else src
    out["ingested_pt"] = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    out = out[out["views"].notna() | out["avg_pct_watched"].notna()]
    out["reel_key"] = [_key(r) for r in out.itertuples()]
    return out[CANON]

def _key(r):
    if isinstance(r.post_id, str) and r.post_id not in ("", "nan", "None"): return f"id:{r.post_id}"
    return f"t:{r.posted_pt}"  # browser tables: posting minute is unique per page

def merge_into(new, code):
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, f"{code}.csv")
    if os.path.exists(path):
        old = pd.read_csv(path, dtype={"post_id": str})
        # retention-only tables (no posting time / id) attach to the existing row with the same views
        allrows = pd.concat([old, new], ignore_index=True)
        # later rows win for every non-empty field of the same reel_key
        merged = allrows.groupby("reel_key", sort=False).agg(lambda s: s.dropna().iloc[-1] if s.notna().any() else np.nan).reset_index()
        merged = merged[CANON]
    else:
        merged = new
    merged.sort_values("posted_pt", na_position="last").to_csv(path, index=False)
    return path, len(new), len(merged)

def attach_retention(ret, code):
    """Retention tables: attach by post id / reel URL when present, else by exact views match."""
    path = os.path.join(OUT_DIR, f"{code}.csv")
    if not os.path.exists(path): return 0
    base = pd.read_csv(path, dtype={"post_id": str}); n = 0
    for r in ret.itertuples():
        m = []
        if isinstance(r.post_id, str) and r.post_id not in ("nan", "None", ""):
            m = base.index[base["post_id"].astype(str) == r.post_id]
        if len(m) != 1 and pd.notna(r.views):
            m = base.index[(base["views"] - r.views).abs() < 1]
        if len(m) == 1:
            for c in ("avg_pct_watched", "completion_rate", "biggest_dropoff_s", "non_follower_pct", "shares",
                      "clicks", "link_clicks", "follows", "reactions"):
                v = getattr(r, c)
                if pd.notna(v): base.loc[m[0], c] = v
            n += 1
    base.to_csv(path, index=False); return n

def ingest(path, page, code, year=2026, tz=0, retention=False):
    df = pd.read_csv(path)
    c = canonicalise(df, page, code, path, year, tz)
    if retention or (c["posted_pt"].isna().all() and c["avg_pct_watched"].notna().any()):
        n = attach_retention(c, code); print(f"[{code}] retention rows attached: {n}/{len(c)} from {path}"); return
    p, a, b = merge_into(c, code); print(f"[{code}] {a} rows from {path} -> {p} ({b} reels total)")

# Existing team Insights captures (browser, read-only, 2026-10-18). Order matters: base tables first.
SEED = [
    ("merryglow/insights_reels.csv", "Merry Glow", "MG", False),
    ("merryglow/top5_retention.csv", "Merry Glow", "MG", True),
    ("merryglow/Brick Hood Shop_insights_reels.csv", "Brick Hood Shop", "BH", False),
    ("merryglow/Brick Hood Shop_top_retention.csv", "Brick Hood Shop", "BH", True),
    ("merryglow/Merry Carrier_insights_reels.csv", "Merry Carrier", "MC", False),
    ("merryglow/Merry Carrier_top_retention.csv", "Merry Carrier", "MC", True),
    ("fb2/merry_glows_insights_reels.csv", "Merry Glows", "MGS", False),
    ("fb2/merry_glows_top_retention.csv", "Merry Glows", "MGS", True),
    ("fb2/merryfires_reels.csv", "MerryFires", "MF", False),
    ("fb2/merryfires_top_retention.csv", "MerryFires", "MF", True),
]

def seed():
    for f in os.listdir(OUT_DIR) if os.path.isdir(OUT_DIR) else []:
        if f.endswith(".csv") and f[:-4] in {s[2] for s in SEED}: os.remove(os.path.join(OUT_DIR, f))
    for rel, page, code, ret in SEED:
        p = os.path.join(W, rel)
        if os.path.exists(p): ingest(p, page, code, retention=ret)
        else: print("missing (skipped):", p)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", nargs="*", help="Insights export CSV file(s)")
    ap.add_argument("--page", help='page display name, e.g. "HeatedJammies"')
    ap.add_argument("--code", help="short page code used everywhere, e.g. HJ")
    ap.add_argument("--year", type=int, default=2026, help="year for dates exported without one")
    ap.add_argument("--tz-offset-hours", type=float, default=0, help="add to export times to get PT")
    ap.add_argument("--retention", action="store_true", help="file is a per-reel retention table (attach by views)")
    ap.add_argument("--seed-existing", action="store_true", help="(re)ingest the team's existing Insights captures")
    a = ap.parse_args()
    if a.seed_existing: seed()
    for f in a.csv:
        if not (a.page and a.code): sys.exit("--page and --code are required with a CSV")
        ingest(f, a.page, a.code.upper(), a.year, a.tz_offset_hours, a.retention)
    if not a.csv and not a.seed_existing: ap.print_help()
