"""Hookforge customer-voice pipeline: ingest -> de-identify -> classify -> aggregate.

  python3 voice/pipeline.py            # rebuild everything (pure stdlib, light on CPU)
Inputs
  private/voice/raw/tiktok_*.jsonl, youtube_*.jsonl   (collect_tiktok.py / collect_youtube.py; already de-identified)
  voice/inbox/*.csv   browser captures (browser_queue.csv runs) and any review exports. Columns:
      source, product_key, reel_ref, url, views, comment_text, likes, reply_count, has_tag, is_page_reply, age_text|date
  voice/support_themes.csv  (gmail_themes.py, aggregated only)
Outputs
  voice/comments.csv               one row per comment/review (de-identified, no usernames)
  voice/voice_stats.json           per product x code counts, subtopics, examples (machine-readable)
  voice/engagement_correlation.csv comment-mix vs views (per video) and own Insights correlations
Then `python3 voice/report.py` writes INSIGHTS.md + voice_rules.csv from voice_stats.json + recommendations.json.
"""
import csv, glob, json, math, os, re, sys, collections, datetime
sys.path.insert(0, os.path.dirname(__file__))
from deid import deid
from codebook import classify, QUESTION_CODES
from products import EXCLUDE_URLS
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.join(HERE, ".."); RAW = os.path.join(REPO, "private", "voice", "raw")
COLS = ["source", "audience", "product_key", "reel_ref", "views", "views_tier", "video_post_date", "text", "n_tags", "likes", "replies", "date", "lang", "primary", "codes"]

def tier(v):
    try: v = float(v)
    except Exception: return "unknown"
    return "10M+" if v >= 1e7 else "1M-10M" if v >= 1e6 else "100K-1M" if v >= 1e5 else "<100K"

def ingest():
    rows = []
    for f in sorted(glob.glob(os.path.join(RAW, "*.jsonl"))):
        lines = open(f).read().splitlines()
        if not lines: continue
        meta = json.loads(lines[0])["_meta"]; src = os.path.basename(f).split("_")[0] + "_public"
        if meta.get("url") in EXCLUDE_URLS: continue
        for ln in lines[1:]:
            c = json.loads(ln); c["text"], extra = deid(c["text"]); p, codes = classify(c["text"], max(c.get("n_tags", 0), extra))
            d = datetime.datetime.fromtimestamp(c["ts"], __import__("zoneinfo").ZoneInfo("America/Los_Angeles")).strftime("%Y-%m-%d") if c.get("ts") else ""
            rows.append({"source": src, "audience": "competitor", "product_key": meta.get("product_key", ""), "reel_ref": meta.get("url", ""),
                         "views": meta.get("views", ""), "views_tier": tier(meta.get("views")), "video_post_date": meta.get("post_date", ""),
                         "text": c["text"], "n_tags": c.get("n_tags", 0), "likes": c.get("likes", 0), "replies": c.get("replies", 0), "date": d,
                         "lang": c.get("lang", ""), "primary": p, "codes": "|".join(codes)})
    for f in sorted(glob.glob(os.path.join(HERE, "inbox", "*.csv"))):
        for x in csv.DictReader(open(f)):
            if str(x.get("is_page_reply", "0")).strip() == "1": continue       # our/brand replies are not customer voice
            text, n = deid(x.get("comment_text", ""))
            n = max(n, int(x.get("has_tag") or 0))
            p, codes = classify(text, n)
            own = x.get("reel_ref", "")[:3] in {"HJ-", "MG-", "MGS", "MF-", "MC-", "BH-", "PV-", "MJI"}
            rows.append({"source": x.get("source", "browser"), "audience": "own" if own else "competitor", "product_key": x.get("product_key", ""),
                         "reel_ref": x.get("reel_ref", "") if own else (x.get("url") or x.get("reel_ref", "")),   # own reels: reel_key only (D10)
                         "views": x.get("views", ""), "views_tier": tier(x.get("views")), "video_post_date": x.get("video_post_date", ""),
                         "text": text, "n_tags": n, "likes": x.get("likes") or 0, "replies": x.get("reply_count") or 0,
                         "date": x.get("date") or x.get("age_text", ""), "lang": "", "primary": p, "codes": "|".join(codes)})
    with open(os.path.join(HERE, "comments.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(rows)
    return rows

STOP = set("""a an the and or but if to of in on for with at by from is are was were be been it this that these those i you he she we they me my
your our their its as so just do does did not no yes can could would should will what how where when why who which there here than then too very
im i'm it's its dont don't u ur lol omg pls please one get got have has had like really all some any more most also que de la el en y es lo un una
los las por para con se mi me te le si ya""".split())
def ngrams(texts, n_max=3, top=8):
    c = collections.Counter()
    for t in texts:
        toks = [w for w in re.findall(r"[a-záéíóúñ']+", t.lower())]
        seen = set()
        for n in range(2, n_max + 1):
            for i in range(len(toks) - n + 1):
                g = toks[i:i + n]
                if g[0] in STOP or g[-1] in STOP: continue
                s = " ".join(g)
                if s not in seen: seen.add(s); c[s] += 1
        for w in set(toks):
            if w not in STOP and len(w) > 3: c[w] += 0.5   # unigrams count half (bigram phrases preferred)
    return [(g, int(round(v))) for g, v in c.most_common(top) if v >= 2]

def weight(r): return 1.0 + math.log1p(float(r["likes"] or 0))

def aggregate(rows):
    stats = {}
    by_p = collections.defaultdict(list)
    for r in rows: by_p[r["product_key"]].append(r)
    for p, rs in by_p.items():
        vids = {r["reel_ref"] for r in rs}
        s = {"n_comments": len(rs), "n_videos": len(vids), "sources": dict(collections.Counter(r["source"] for r in rs)),
             "audience": dict(collections.Counter(r["audience"] for r in rs)), "codes": {}}
        W = sum(weight(r) for r in rs)
        allcodes = sorted({c for r in rs for c in r["codes"].split("|") if c} | {"other"})
        for code in allcodes:
            sub = [r for r in rs if code in r["codes"].split("|")] if code != "other" else [r for r in rs if r["primary"] == "other"]
            if not sub: continue
            ex = sorted([r for r in sub if 15 <= len(r["text"]) <= 160 and "emotional" not in r["codes"]], key=lambda r: -float(r["likes"] or 0))
            exs, seen = [], set()
            for r in ex:
                k = r["text"].lower()[:40]
                if k in seen: continue
                seen.add(k); exs.append({"text": r["text"], "likes": int(float(r["likes"] or 0)), "audience": r["audience"]})
                if len(exs) == 6: break
            s["codes"][code] = {"n": len(sub), "share": round(len(sub) / len(rs), 4), "like_weighted_share": round(sum(weight(r) for r in sub) / W, 4),
                                "n_videos": len({r["reel_ref"] for r in sub}), "likes_sum": int(sum(float(r["likes"] or 0) for r in sub)),
                                "subtopics": ngrams([r["text"] for r in sub]), "examples": exs}
        stats[p] = s
    return stats

def spearman(x, y):
    n = len(x)
    if n < 5: return None, n
    def rank(v):
        o = sorted(range(n), key=lambda i: v[i]); r = [0.0] * n; i = 0
        while i < n:
            j = i
            while j + 1 < n and v[o[j + 1]] == v[o[i]]: j += 1
            for k in range(i, j + 1): r[o[k]] = (i + j) / 2 + 1
            i = j + 1
        return r
    rx, ry = rank(x), rank(y); mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry)); den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return (round(num / den, 3) if den else None), n

def correlations(rows):
    out = []
    # (a) per competitor video: comment mix vs log10 views
    vids = collections.defaultdict(list)
    for r in rows:
        if r["views"]: vids[r["reel_ref"]].append(r)
    vids = {k: v for k, v in vids.items() if len(v) >= 30}
    lv = {k: math.log10(float(v[0]["views"])) for k, v in vids.items()}
    for feat in ["q_any", "q_where_buy", "q_price", "tag_friend", "desire", "objection", "humor", "complaint", "comparison"]:
        xs, ys = [], []
        for k, v in vids.items():
            if feat == "q_any": share = sum(any(c.startswith("q_") for c in r["codes"].split("|")) for r in v) / len(v)
            else: share = sum(feat in r["codes"].split("|") for r in v) / len(v)
            xs.append(share); ys.append(lv[k])
        rho, n = spearman(xs, ys)
        out.append({"dataset": "competitor/library videos (top comments)", "x": f"share_{feat}", "y": "log10 views", "spearman_rho": rho, "n": n,
                    "note": "top-ranked comments per video (TikTok relevance order); association only"})
    # (b) own Insights: comments per 1K views and shares per 1K views vs views
    ins = []
    for f in glob.glob(os.path.join(REPO, "analytics", "data", "insights", "*.csv")):
        for x in csv.DictReader(open(f)):
            try: v = float(x["views"] or 0)
            except Exception: continue
            if v >= 500: ins.append((x["page_code"], v, float(x["comments"] or 0), float(x["shares"] or 0) if x["shares"] else None))
    for feat, idx in [("comments_per_1k_views", 2), ("shares_per_1k_views", 3)]:
        pts = [(i[idx] / i[1] * 1000, math.log10(i[1])) for i in ins if i[idx] is not None]
        rho, n = spearman([p[0] for p in pts], [p[1] for p in pts])
        out.append({"dataset": "own reels, Meta Insights exports (MG/MGS/MF/MC/BH, views>=500)", "x": feat, "y": "log10 views", "spearman_rho": rho, "n": n,
                    "note": "per-view rates; HJ/MJIG Insights not available yet (audit ask #1)"})
        pts2 = [(i[idx], math.log10(i[1])) for i in ins if i[idx] is not None]
        rho, n = spearman([p[0] for p in pts2], [p[1] for p in pts2])
        out.append({"dataset": "own reels, Meta Insights exports", "x": feat.replace("_per_1k_views", "_count"), "y": "log10 views", "spearman_rho": rho, "n": n,
                    "note": "raw counts scale with views (mechanical); see per-1K row for signal"})
    with open(os.path.join(HERE, "engagement_correlation.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    return out

if __name__ == "__main__":
    rows = ingest(); stats = aggregate(rows); corr = correlations(rows)
    json.dump({"generated": datetime.datetime.now(__import__("zoneinfo").ZoneInfo("America/Los_Angeles")).strftime("%Y-%m-%d %H:%M PT"), "products": stats, "correlations": corr},
              open(os.path.join(HERE, "voice_stats.json"), "w"), indent=1, ensure_ascii=False)
    print(len(rows), "comments;", {p: s["n_comments"] for p, s in stats.items()})
