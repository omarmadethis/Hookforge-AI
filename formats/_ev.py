"""Evidence-row helpers. Every row points to a reel that a teammate measured."""
import csv as _csv
_POSTED = {}
try:
    for _r in _csv.DictReader(open("/workspace/team/external/external_reels.csv")):
        _POSTED[_r["url"].rstrip("/")] = (_r.get("posted") or "")[:10]
except FileNotFoundError:
    pass
def FB(rid):  # HeatedJammies-style numeric FB reel id
    return f"https://www.facebook.com/reel/{rid}/"

def I(rid, page, views, role, note, src="H,B", url=None, platform="FB", shares=None):
    if url is None and rid.isdigit(): url = FB(rid)
    return {"origin": "internal", "id": rid, "page": page, "platform": platform, "views": views,
            "shares": shares, "role": role, "note": note, "src": src, "url": url}

def _tiktok_date(url):
    """TikTok video ids encode the upload time: id >> 32 = unix seconds (used only when the CSV has no date)."""
    import re, datetime
    m = re.search(r"tiktok\.com/.*/video/(\d+)", url)
    if not m: return ""
    return datetime.datetime.utcfromtimestamp(int(m.group(1)) >> 32).date().isoformat()

def X(account, views, url, note, shares=None, flag=False, platform=None, src="X"):
    if platform is None: platform = "IG" if "instagram.com" in url else "TikTok"
    rid = url.rstrip("/").split("/")[-1]
    return {"origin": "external", "id": f"{account}/{rid[-8:]}", "page": account, "platform": platform,
            "views": views, "shares": shares, "flag": flag, "role": "external winner", "note": note,
            "src": src, "url": url, "posted": _POSTED.get(url.rstrip("/")) or _tiktok_date(url)}
