"""Collect PUBLIC TikTok comments (no login) for competitor / reference videos.

Why not `yt-dlp --write-comments`: yt-dlp 2026.08 no longer extracts TikTok comments (tested
2026-10-18: info.json has comment_count but no comments). We read the same public JSON the
logged-out tiktok.com web page loads (`/api/comment/list/`), with curl_cffi browser impersonation
(the transport yt-dlp itself uses). Read-only, ~1 request / 1.5 s, top comments only (TikTok's
default relevance order = most-liked first), no replies, no usernames/user ids stored.

Usage (venv with curl_cffi: /workspace/.venvs/voice):
  /workspace/.venvs/voice/bin/python voice/collect_tiktok.py [--max 300] [--targets voice/targets.csv]
Writes private/voice/raw/tiktok_<video_id>.jsonl (de-identified) and is resumable (skips done ids).
"""
import argparse, csv, json, os, re, sys, time
sys.path.insert(0, os.path.dirname(__file__))
from deid import deid

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "private", "voice", "raw")

def fetch(vid, maxn, sleep=1.5):
    from curl_cffi import requests
    out, cursor = [], 0
    while len(out) < maxn:
        r = requests.get("https://www.tiktok.com/api/comment/list/",
                         params={"aweme_id": vid, "count": 50, "cursor": cursor, "aid": 1988},
                         impersonate="chrome", timeout=30, headers={"Referer": "https://www.tiktok.com/"})
        if r.status_code != 200: break
        try: d = r.json()
        except Exception: break
        cs = d.get("comments") or []
        for c in cs:
            text, n_tags = deid(c.get("text", ""))
            if not text and not n_tags: continue
            out.append({"text": text, "n_tags": n_tags, "likes": c.get("digg_count", 0),
                        "replies": c.get("reply_comment_total", 0), "ts": c.get("create_time"),
                        "lang": c.get("comment_language", "")})
        if not d.get("has_more") or not cs: break
        cursor = d.get("cursor", cursor + 50)
        time.sleep(sleep)
    return out, (d.get("total") if 'd' in locals() and isinstance(d, dict) else None)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--targets", default=os.path.join(HERE, "targets.csv"))
    ap.add_argument("--max", type=int, default=300)
    a = ap.parse_args()
    os.makedirs(RAW, exist_ok=True)
    for row in csv.DictReader(open(a.targets)):
        if row["platform"].lower() != "tiktok": continue
        m = re.search(r"/video/(\d+)", row["url"])
        if not m: continue
        vid = m.group(1); path = os.path.join(RAW, f"tiktok_{vid}.jsonl")
        if os.path.exists(path): continue
        try: cs, total = fetch(vid, a.max)
        except Exception as e: print("ERR", vid, e); continue
        with open(path, "w") as f:
            f.write(json.dumps({"_meta": {"video_id": vid, "total": total, "fetched": time.strftime("%Y-%m-%d %H:%M"), **{k: row[k] for k in row}}}) + "\n")
            for c in cs: f.write(json.dumps(c, ensure_ascii=False) + "\n")
        print(vid, row["product"], len(cs), "of", total, flush=True)
        time.sleep(2)

if __name__ == "__main__":
    main()
