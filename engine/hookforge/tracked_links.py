"""#5 per-reel tracked links (D87). utm_source=fb|ig, utm_medium=social, utm_campaign=<product>, utm_content=<video_id>.
Captions keep the literal {url} until the product's real link is known (F45: links live in the caption, never on screen)."""
import re, urllib.parse
PLATFORMS = {"fb": "fb", "facebook": "fb", "ig": "ig", "instagram": "ig"}

def tracked_url(base_url, video_id, platform, product):
    if not base_url or "{url}" in base_url: return None
    src = PLATFORMS[str(platform).lower()]
    p = urllib.parse.urlsplit(base_url)
    q = [(k, v) for k, v in urllib.parse.parse_qsl(p.query) if not k.startswith("utm_")]
    q += [("utm_source", src), ("utm_medium", "social"), ("utm_campaign", _slug(product)), ("utm_content", _slug(video_id))]
    return urllib.parse.urlunsplit((p.scheme, p.netloc, p.path, urllib.parse.urlencode(q), ""))

def fill_caption(caption, video_id, platform, product, base_url=None):
    """Replace {url} with the tracked link; with no known base_url the caption keeps {url} unchanged."""
    u = tracked_url(base_url, video_id, platform, product)
    return caption if u is None else caption.replace("{url}", u)

def _slug(s): return re.sub(r"[^a-z0-9_\-]+", "-", str(s).lower()).strip("-")
