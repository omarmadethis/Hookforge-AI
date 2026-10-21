"""#1 RESULTS FEED (D86): per-reel performance -> learning loop.

Sources (all READ-ONLY; nothing here posts, likes, comments or writes to Meta):
  (a) Meta Business Suite CSV exports (FB "Content" export, IG reels export, team insights tables) dropped in
      learning/results/inbox/  -> canonicalised with analytics/ingest_insights.canonicalise (alias matching).
  (b) Meta Graph API when env META_TOKEN is set (never read from / written to a file, never logged):
      FB  /{page}/video_reels + /{video}/video_insights (blue_reels_play_count, fb_reels_total_plays,
          post_video_avg_time_watched, post_impressions_unique, post_video_view_time)
      IG  /{ig_user}/media + /{media}/insights (views, reach, saved, shares, comments, likes,
          ig_reels_avg_watch_time, ig_reels_video_view_total_time, reels_skip_rate)
  (c) every ingest writes a dated snapshot -> day-1/3/7 view velocity (interpolated between snapshots).
Join: reel -> Hookforge video_id via (1) utm_content in caption link, (2) caption text, (3) publish time vs
publish-queue time, (4) duration, (5) perceptual hash of frames when the reel file is local. Score >= 0.6 = match.
Outputs: learning/results/reels.csv (latest per reel), snapshots/*.csv, velocity.csv, outcomes.csv (joined,
incl. sales from sales_attribution), backtest_eval.csv (predicted band vs actual).
"""
import os, re, sys, glob, json, math, hashlib, subprocess, datetime as dt, urllib.request, urllib.parse
import pandas as pd, numpy as np
from .config import REPO

RES = os.path.join(REPO, "learning", "results")
INBOX, SNAP, RAW = (os.path.join(RES, d) for d in ("inbox", "snapshots", "graph_raw"))
REGISTRY = os.path.join(RES, "video_registry.csv")
GRAPH = "https://graph.facebook.com/v21.0"
FB_METRICS = ["blue_reels_play_count", "fb_reels_total_plays", "post_video_avg_time_watched", "post_impressions_unique", "post_video_view_time"]
IG_METRICS = ["views", "reach", "saved", "shares", "comments", "likes", "ig_reels_avg_watch_time", "ig_reels_video_view_total_time", "reels_skip_rate"]
COLS = ["platform", "page", "reel_key", "post_id", "reel_url", "posted_pt", "caption", "duration_s", "views", "viewers",
        "three_sec_views", "avg_watch_s", "watch_time_s", "skip_rate", "shares", "saves", "comments", "reactions",
        "follows", "link_clicks", "file", "source", "snapshot_pt"]

def _now(): return dt.datetime.now().replace(microsecond=0)
sys.path.insert(0, os.path.join(REPO, "analytics"))

# ---------------- (a) CSV exports ----------------
def _page_of(df, path):
    for c in ("Page name", "Account username", "Account name", "page"):
        if c in df.columns and df[c].notna().any(): return str(df[c].dropna().iloc[0])
    return os.path.basename(path).split("_insights")[0].replace(".csv", "")

def read_csv_export(path, year=2026, snapshot_pt=None):
    import ingest_insights as II
    df = pd.read_csv(path, encoding="utf-8-sig")
    page = _page_of(df, path)
    platform = "ig" if any(c in df.columns for c in ("Account username", "Plays", "Saves")) or "ig" in os.path.basename(path).lower().split("_") else "fb"
    c = II.canonicalise(df, page, re.sub(r"\W", "", page)[:6].upper(), path, year=year)
    out = pd.DataFrame({k: c[k] if k in c else np.nan for k in COLS})
    out["platform"], out["source"] = platform, "csv:" + os.path.basename(path)
    out["reel_key"] = platform + ":" + c["reel_key"].astype(str)
    out["skip_rate"] = np.nan
    out["snapshot_pt"] = snapshot_pt or dt.datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M")
    return out

# ---------------- (b) Graph API ----------------
def _get(path, token, **params):
    params["access_token"] = token
    with urllib.request.urlopen(f"{GRAPH}/{path}?{urllib.parse.urlencode(params)}", timeout=30) as r:
        return json.loads(r.read())

def _ins(data):
    o = {}
    for m in data.get("data", []):
        v = (m.get("values") or [{}])[0].get("value", m.get("total_value", {}).get("value"))
        o[m["name"]] = v
    return o

def parse_fb(video, insights):
    i = _ins(insights)
    plays = i.get("blue_reels_play_count", i.get("fb_reels_total_plays"))
    avg_ms = i.get("post_video_avg_time_watched")
    return dict(platform="fb", reel_key=f"fb:id:{video['id']}", post_id=video["id"], reel_url=video.get("permalink_url"),
                posted_pt=_pt(video.get("created_time")), caption=video.get("description"), duration_s=video.get("length"),
                views=plays, viewers=i.get("post_impressions_unique"), avg_watch_s=(avg_ms / 1000 if avg_ms else None),
                watch_time_s=(i["post_video_view_time"] / 1000 if i.get("post_video_view_time") else None), source="graph:fb")

def parse_ig(media, insights):
    i = _ins(insights)
    aw = i.get("ig_reels_avg_watch_time")
    return dict(platform="ig", reel_key=f"ig:id:{media['id']}", post_id=media["id"], reel_url=media.get("permalink"),
                posted_pt=_pt(media.get("timestamp")), caption=media.get("caption"), views=i.get("views"), viewers=i.get("reach"),
                avg_watch_s=(aw / 1000 if aw else None), skip_rate=i.get("reels_skip_rate"), shares=i.get("shares"),
                saves=i.get("saved"), comments=i.get("comments"), reactions=i.get("likes"), source="graph:ig")

def _pt(iso):
    if not iso: return None
    from zoneinfo import ZoneInfo
    t = dt.datetime.fromisoformat(str(iso).replace("Z", "+00:00").replace("+0000", "+00:00"))
    return t.astimezone(ZoneInfo("America/Los_Angeles")).strftime("%Y-%m-%d %H:%M")

def fetch_graph(limit=50):
    """Read-only. Uses META_TOKEN from the environment only; returns [] when absent. Token never persisted."""
    tok = os.environ.get("META_TOKEN")
    if not tok: return []
    rows = []
    pages = _get("me/accounts", tok, fields="id,name,access_token,instagram_business_account").get("data", [])
    for p in pages:
        ptok = p.get("access_token") or tok
        for v in _get(f"{p['id']}/video_reels", ptok, fields="id,description,created_time,length,permalink_url", limit=limit).get("data", []):
            try: r = parse_fb(v, _get(f"{v['id']}/video_insights", ptok, metric=",".join(FB_METRICS)))
            except Exception as e: r = parse_fb(v, {}); r["source"] = f"graph:fb(insights error {type(e).__name__})"
            r["page"] = p["name"]; rows.append(r)
        ig = (p.get("instagram_business_account") or {}).get("id")
        if ig:
            for m in _get(f"{ig}/media", ptok, fields="id,caption,timestamp,media_product_type,permalink", limit=limit).get("data", []):
                if m.get("media_product_type") != "REELS": continue
                try: r = parse_ig(m, _get(f"{m['id']}/insights", ptok, metric=",".join(IG_METRICS)))
                except Exception as e: r = parse_ig(m, {}); r["source"] = f"graph:ig(insights error {type(e).__name__})"
                r["page"] = p["name"] + " IG"; rows.append(r)
    df = pd.DataFrame(rows)
    if len(df): df["snapshot_pt"] = _now().strftime("%Y-%m-%d %H:%M")
    return df

# ---------------- (c) snapshots + velocity ----------------
def write_snapshot(df, stamp=None):
    os.makedirs(SNAP, exist_ok=True)
    stamp = stamp or _now().strftime("%Y-%m-%dT%H%M")
    p = os.path.join(SNAP, f"{stamp}.csv"); df.reindex(columns=COLS).to_csv(p, index=False); return p

def load_snapshots():
    fs = sorted(glob.glob(os.path.join(SNAP, "*.csv")))
    return pd.concat([pd.read_csv(f) for f in fs], ignore_index=True) if fs else pd.DataFrame(columns=COLS)

def velocity(snaps, days=(1, 3, 7), tol_h=12):
    """views at age d days: linear interpolation between bracketing snapshots, else nearest snapshot within tol_h."""
    out = []
    s = snaps.dropna(subset=["posted_pt", "views"]).copy()
    if not len(s): return pd.DataFrame(columns=["reel_key"] + [f"views_d{d}" for d in days])
    s["age_h"] = (pd.to_datetime(s.snapshot_pt) - pd.to_datetime(s.posted_pt)).dt.total_seconds() / 3600
    for k, g in s.groupby("reel_key"):
        g = g.sort_values("age_h").drop_duplicates("age_h", keep="last"); row = dict(reel_key=k, n_snapshots=len(g))
        a, v = g.age_h.values, g.views.astype(float).values
        for d in days:
            h = 24 * d; val = None
            if len(a) >= 2 and a[0] <= h <= a[-1]: val = float(np.interp(h, a, v))
            else:
                j = int(np.argmin(abs(a - h)))
                if abs(a[j] - h) <= tol_h: val = float(v[j])
            row[f"views_d{d}"] = val
        if row.get("views_d1") and row.get("views_d7"): row["growth_d1_d7"] = row["views_d7"] / max(row["views_d1"], 1)
        out.append(row)
    return pd.DataFrame(out)

# ---------------- join to Hookforge videos ----------------
UTM_RX = re.compile(r"utm_content=([A-Za-z0-9_\-]+)")
def _norm_text(s): return re.sub(r"\s+", " ", re.sub(r"https?://\S+|#\w+|[^\w\s]", " ", str(s or "").lower())).strip()

def _dur(path):
    try: return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path], text=True).strip())
    except Exception: return None

def phash(path, at=(0.5, 1.5, 3.0)):
    """Perceptual hash (64-bit pHash) of a few frames; robust to re-encode/compression by Meta."""
    import imagehash
    from PIL import Image
    import io
    hs = []
    for t in at:
        try:
            png = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", str(t), "-i", path, "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"])
            hs.append(str(imagehash.phash(Image.open(io.BytesIO(png)))))
        except Exception: pass
    return "|".join(hs)

def phash_dist(a, b):
    import imagehash
    A, B = [x for x in str(a or "").split("|") if x], [x for x in str(b or "").split("|") if x]
    if not A or not B: return None
    return min(imagehash.hex_to_hash(x) - imagehash.hex_to_hash(y) for x in A for y in B)

def build_registry(roots=None):
    """One row per deliverable Hookforge video: video_id, product, caption, duration, phash, queued_pt."""
    roots = roots or [os.path.join(REPO, "out", "live")]
    rows = []
    for root in roots:
        for f in sorted(glob.glob(os.path.join(root, "**", "*.mp4"), recursive=True)):
            if "/_" in f or "/._" in f or "preflight" in f: continue
            name = os.path.splitext(os.path.basename(f))[0]
            cap = next((open(c, errors="ignore").read().strip() for c in [f[:-4] + " - Caption.txt", re.sub(r" - [^-]+ - (v\d+)\.mp4$", r" - \1 - Caption.txt", f)] if os.path.exists(c)), "")
            rows.append(dict(video_id=video_id(name), name=name, product=_product(name, f), file=f, caption=cap,
                             duration_s=_dur(f), phash=phash(f), queued_pt=None))
    q = os.path.join(REPO, "learning", "publish_queue")
    for j in glob.glob(os.path.join(q, "*.json")):
        it = json.load(open(j))
        rows.append(dict(video_id=it.get("video_id") or it["id"], name=it["id"], product=it.get("product"), file=it.get("video"),
                         caption=it.get("caption"), duration_s=None, phash=None, queued_pt=it.get("created_pt")))
    df = pd.DataFrame(rows).drop_duplicates("video_id", keep="last")
    os.makedirs(RES, exist_ok=True); df.to_csv(REGISTRY, index=False); return df

def video_id(name):
    """Stable short id used in utm_content: slug + 6-hex of the name."""
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:40]
    return f"{slug}-{hashlib.sha1(name.encode()).hexdigest()[:6]}"

def _product(name, path):
    s = (name + " " + path).lower()
    for k, v in (("jolly", "jollyglow"), ("trump", "trumpglow"), ("patriot", "trumpglow"), ("purr", "purrventure"), ("brick", "brickhood"), ("grinch", "grinch_robe")):
        if k in s: return v
    return "unknown"

def match(reels, reg, thresh=0.6):
    out = []
    for r in reels.itertuples(index=False):
        best = (0, None, "")
        u = UTM_RX.search(str(r.caption or ""))
        for v in reg.itertuples(index=False):
            if u and u.group(1) == v.video_id: best = (1.0, v.video_id, "utm_content"); break
            s, why = 0.0, []
            a, b = _norm_text(r.caption), _norm_text(v.caption)
            if a and b and (a == b or (len(b) > 8 and (b in a or a in b))): s += 0.5; why.append("caption")
            if pd.notna(getattr(v, "queued_pt", None)) and pd.notna(r.posted_pt):
                if abs((pd.to_datetime(r.posted_pt) - pd.to_datetime(v.queued_pt)).total_seconds()) <= 6 * 3600: s += 0.2; why.append("time")
            if pd.notna(r.duration_s) and pd.notna(v.duration_s) and abs(float(r.duration_s) - float(v.duration_s)) <= 0.6: s += 0.15; why.append("duration")
            f = getattr(r, "file", None)
            if isinstance(f, str) and os.path.exists(f) and isinstance(v.phash, str):
                d = phash_dist(phash(f), v.phash)
                if d is not None and d <= 10: s += 0.5; why.append(f"phash{d}")
            if s > best[0]: best = (min(s, 1.0), v.video_id, "+".join(why))
        out.append(dict(reel_key=r.reel_key, video_id=best[1] if best[0] >= thresh else None, match_score=round(best[0], 2), match_on=best[2]))
    return pd.DataFrame(out, columns=["reel_key", "video_id", "match_score", "match_on"])

# ---------------- orchestration ----------------
def ingest(inbox=None, use_graph=True, stamp=None):
    inbox = inbox or INBOX
    files = sorted(glob.glob(os.path.join(inbox, "*.csv")))
    parts = [read_csv_export(p) for p in files]
    done = os.path.join(inbox, "processed"); os.makedirs(done, exist_ok=True)
    for p in files: os.replace(p, os.path.join(done, _now().strftime("%Y%m%dT%H%M_") + os.path.basename(p)))
    if use_graph:
        g = fetch_graph()
        if len(g): parts.append(g.reindex(columns=COLS))
    if not parts: return pd.DataFrame(columns=COLS), None
    df = pd.concat(parts, ignore_index=True)
    return df, write_snapshot(df, stamp)

def run(use_graph=True, rebuild_registry=False, inbox=None):
    new, snap = ingest(inbox, use_graph)
    snaps = load_snapshots()
    latest = snaps.sort_values("snapshot_pt").drop_duplicates("reel_key", keep="last") if len(snaps) else snaps
    reg = build_registry() if (rebuild_registry or not os.path.exists(REGISTRY)) else pd.read_csv(REGISTRY)
    m = match(latest, reg) if len(latest) else pd.DataFrame(columns=["reel_key", "video_id", "match_score", "match_on"])
    vel = velocity(snaps)
    out = latest.merge(m, on="reel_key", how="left").merge(vel, on="reel_key", how="left")
    try:
        from . import sales_attribution as SA
        sales = SA.load_attribution()
        if len(sales): out = out.merge(sales, on="video_id", how="left")
    except Exception as e: out["sales_note"] = f"no sales: {e}"
    latest.to_csv(os.path.join(RES, "reels.csv"), index=False); vel.to_csv(os.path.join(RES, "velocity.csv"), index=False)
    out.to_csv(os.path.join(RES, "outcomes.csv"), index=False)
    ev = backtest_eval(out)
    return dict(step="results_feed", ok=True, new_rows=len(new), snapshot=snap, reels=len(latest), matched=int(out.video_id.notna().sum()),
                with_velocity=int(vel.filter(like="views_d").notna().any(axis=1).sum()) if len(vel) else 0, backtest_rows=len(ev),
                graph="on" if os.environ.get("META_TOKEN") else "off (META_TOKEN not set)")

def backtest_eval(outcomes):
    """Backtester wiring: for matched videos with a stored plan feature file, compare predict_band to actual views."""
    rows = []
    for r in outcomes.dropna(subset=["video_id"]).itertuples(index=False):
        fp = os.path.join(RES, "features", f"{r.video_id}.json")
        if not os.path.exists(fp) or pd.isna(r.views): continue
        try:
            sys.path.insert(0, os.path.join(REPO, "engine"))
            from backtest.backtest import predict_band
            b = predict_band(json.load(open(fp)))
            rows.append(dict(video_id=r.video_id, reel_key=r.reel_key, actual=r.views, p10=b["p10"], p50=b["p50"], p90=b["p90"],
                             in_band=b["p10"] <= r.views <= b["p90"], log_err=math.log10(max(r.views, 1)) - math.log10(max(b["p50"], 1))))
        except Exception as e: rows.append(dict(video_id=r.video_id, reel_key=r.reel_key, error=str(e)[:200]))
    ev = pd.DataFrame(rows); ev.to_csv(os.path.join(RES, "backtest_eval.csv"), index=False); return ev

if __name__ == "__main__":
    print(json.dumps(run(rebuild_registry="--registry" in sys.argv), indent=1, default=str))
