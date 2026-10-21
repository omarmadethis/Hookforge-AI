"""Collect PUBLIC YouTube comments for videos about products equivalent to ours (yt-dlp, proven tool).

For each product's `search` terms (products.py): `ytsearch15:<term>` (flat), keep videos whose TITLE
routes to the same product (products.route / product search words) with >=3,000 views, top 4 per term
by views, then `yt-dlp --skip-download --write-comments` with max 150 top comments.
Writes private/voice/raw/youtube_<id>.jsonl (de-identified; no author names/ids kept).
Usage: /workspace/.venvs/voice/bin/python voice/collect_youtube.py
"""
import json, os, re, subprocess, sys, time, tempfile
sys.path.insert(0, os.path.dirname(__file__))
from deid import deid
from products import PRODUCTS, route

HERE = os.path.dirname(os.path.abspath(__file__)); RAW = os.path.join(HERE, "..", "private", "voice", "raw")
YTDLP = "/workspace/.venvs/voice/bin/yt-dlp"

def search(term, n=15):
    out = subprocess.run([YTDLP, "--flat-playlist", "--print", "%(id)s\t%(title)s\t%(view_count)s", f"ytsearch{n}:{term}"],
                         capture_output=True, text=True, timeout=180).stdout
    res = []
    for line in out.splitlines():
        p = line.split("\t")
        if len(p) == 3: res.append((p[0], p[1], int(p[2]) if p[2].isdigit() else 0))
    return res

def relevant(pkey, title, term):
    t = title.lower()
    if route(t) == pkey: return True
    words = [w for w in re.findall(r"[a-z]+", term.lower()) if w not in ("review", "christmas", "indoor", "app")]
    return sum(w in t for w in words) >= max(2, len(words) - 1)

def comments(vid, maxn=150):
    with tempfile.TemporaryDirectory() as d:
        subprocess.run([YTDLP, "--skip-download", "--write-comments", "--no-warnings",
                        "--extractor-args", f"youtube:max_comments={maxn},all,0;comment_sort=top",
                        "-o", f"{d}/%(id)s.%(ext)s", f"https://www.youtube.com/watch?v={vid}"],
                       capture_output=True, text=True, timeout=300)
        p = f"{d}/{vid}.info.json"
        if not os.path.exists(p): return None, []
        info = json.load(open(p))
    cs = []
    for c in info.get("comments") or []:
        if c.get("parent", "root") != "root": continue
        if c.get("author_is_uploader"): continue   # seller replies excluded from customer voice
        text, n = deid(c.get("text", ""))
        cs.append({"text": text, "n_tags": n, "likes": c.get("like_count") or 0, "replies": 0, "ts": c.get("timestamp"), "lang": ""})
    meta = {"title": info.get("title"), "views": info.get("view_count"), "upload_date": info.get("upload_date"), "total": info.get("comment_count")}
    return meta, cs

def main():
    os.makedirs(RAW, exist_ok=True)
    for pkey, p in PRODUCTS.items():
        for term in p["search"]:
            try: hits = search(term)
            except Exception as e: print("search ERR", term, e); continue
            keep = sorted([h for h in hits if h[2] >= 3000 and relevant(pkey, h[1], term)], key=lambda h: -h[2])[:4]
            for vid, title, views in keep:
                path = os.path.join(RAW, f"youtube_{vid}.jsonl")
                if os.path.exists(path): continue
                meta, cs = comments(vid)
                if meta is None: print("no info", vid); continue
                with open(path, "w") as f:
                    f.write(json.dumps({"_meta": {"video_id": vid, "product_key": pkey, "platform": "youtube", "search_term": term,
                        "url": f"https://www.youtube.com/watch?v={vid}", "product": title, "views": meta["views"],
                        "post_date": meta["upload_date"], "total": meta["total"], "source_set": "youtube_search"}}, ensure_ascii=False) + "\n")
                    for c in cs: f.write(json.dumps(c, ensure_ascii=False) + "\n")
                print(pkey, vid, views, len(cs), title[:70], flush=True)
                time.sleep(2)

if __name__ == "__main__":
    main()
