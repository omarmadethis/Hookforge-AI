"""D153 Buffer draft-payload preflight (read-only, sends nothing).
Builds the exact create_post payload publish.build_payload would send for every weekly slot of the 3 active products and
validates it against Buffer's own create_post inputSchema (config/buffer_create_post.schema.json, read via GetDynamicTools
on user-Buffer) with jsonschema + format checks, then the tool's prose rules and our own draft-only rules.
No video is staged yet, so a stand-in https URL on a reserved .invalid host proves the asset SHAPE; a real URL is
checked for share links / expiring presigned params (never printed - only its host is reported)."""
import json, os, re, datetime, urllib.parse
from zoneinfo import ZoneInfo
import jsonschema
from .config import REPO
from . import publish, routing, products as _products

SCHEMA_F = os.path.join(REPO, "config", "buffer_create_post.schema.json")
OUT_DIR = os.path.join(REPO, "learning", "buffer_preflight")
STANDIN = "https://video-pending.invalid/{video}.mp4"
PRESIGN = re.compile(r"(?i)(x-amz-(signature|expires|credential)|[?&](expires|signature|sig|token|se|sp)=)")
SHARE = re.compile(r"(?i)(drive\.google\.com|docs\.google\.com|dropbox\.com/s/|1drv\.ms|onedrive\.live\.com|/share/|/preview)")

def schema(): return json.load(open(SCHEMA_F))["schema"]

def _validator():
    return jsonschema.Draft7Validator(schema(), format_checker=jsonschema.Draft7Validator.FORMAT_CHECKER)

def check_payload(p, service, real_url=True):
    """Returns list of problems ([] = would pass Buffer's create_post validation + our rules)."""
    probs = [f"schema: {'/'.join(map(str, e.absolute_path)) or '(root)'}: {e.message[:140]}" for e in _validator().iter_errors(p)]
    md = p.get("metadata") or {}; assets = p.get("assets") or []
    if service == "facebook" and not (md.get("facebook") or {}).get("type"): probs.append("facebook needs metadata.facebook.type")
    if service == "instagram":
        if not assets: probs.append("instagram needs an image or video asset")
        if not (md.get("instagram") or {}).get("type"): probs.append("instagram needs metadata.instagram.type")
    if (md.get(service) or {}).get("linkAttachment") and assets: probs.append("linkAttachment with non-empty assets")
    if (md.get(service) or {}).get("type") == "reel" and not any("video" in a for a in assets): probs.append("reel without a video asset")
    for a in assets:
        v = a.get("video") or {}
        if "thumbnailUrl" in v: probs.append("thumbnailUrl on a video asset")
        u = v.get("url") or ""
        pu = urllib.parse.urlparse(u)        # schema 'format: uri' is not enforced without rfc3987 -> check it here
        if pu.scheme not in ("http", "https") or not pu.hostname or " " in u: probs.append("schema: assets/video/url is not an absolute http(s) URI")
        if real_url:
            if SHARE.search(u): probs.append(f"video url is a share/preview page (host {urllib.parse.urlparse(u).hostname})")
            if PRESIGN.search(u): probs.append(f"video url carries expiring presigned params (host {urllib.parse.urlparse(u).hostname}) - Buffer fetches later")
    try: publish._check_payload(p)
    except publish.NotAllowed as e: probs.append(f"draft-only rule: {e}")
    if not (p.get("text") or "").strip(): probs.append("empty text")
    if re.search(r"(?i)placeholder", p.get("text") or ""): probs.append("caption contains a PLACEHOLDER link")
    if not re.search(r'\bSAY\s*["“]', p.get("text") or ""): probs.append('caption has no SAY "<KEYWORD>"')
    return probs

def run(write=True, video_urls=None):
    """video_urls: optional {video_id: staged public url}; otherwise the .invalid stand-in (shape check only)."""
    from . import concept_lab
    w = concept_lab.weekly(write=False); rows = []
    for m in w["slot_map"]:
        pk = m["product"]
        if not _products.is_active(pk): continue
        r = routing.route(pk); pg = next((p for p in r["pages"] if p.get("key", p.get("page")) == m["page"] or p.get("page") == m["page"]), None)
        if pg is None:
            pg = next((dict(routing.page(k), key=k) for k in routing.cfg()["products"].get(pk, []) if k == m["page"]), None)
            refused = next((x["reason"] for x in r["refused"] if x["page"] == m["page"]), "page not routed")
        else: refused = None
        real = bool(video_urls and m["video"] in video_urls)
        url = video_urls[m["video"]] if real else STANDIN.format(video=m["video"])
        row = dict(day=m["day"], page=m["page"], product=pk, video=m["video"], service=(pg or {}).get("service"), url="staged" if real else "stand-in (video not staged yet)")
        if pg is None or not pg.get("channel"): row.update(ok=False, problems=[f"no channel for page: {refused}"]); rows.append(row); continue
        try:
            p = publish.build_payload(pg["channel"], pg["service"], m["caption"], video_url=url)
            row["problems"] = check_payload(p, pg["service"], real_url=real)
            if refused: row["problems"].append(f"route refused: {refused}")
            row["namespace"] = pg.get("namespace")
        except Exception as e: row["problems"] = [f"build_payload: {e}"]
        row["ok"] = not row["problems"]; rows.append(row)
    by = {}
    for r_ in rows: by.setdefault(r_["product"], []).append(r_["ok"])
    out = dict(at_pt=datetime.datetime.now(ZoneInfo("America/Los_Angeles")).isoformat(timespec="seconds"), schema=os.path.relpath(SCHEMA_F, REPO),
               slots=len(rows), passed=sum(r_["ok"] for r_ in rows), per_product={k: f"{sum(v)}/{len(v)}" for k, v in by.items()},
               remaining_before_first_push=["stage each rendered video (deliver.stage/verify_staged) and pass its public URL", "Omar approval per post (publish.approve)"],
               rows=rows, nothing_sent=True)
    if write:
        os.makedirs(OUT_DIR, exist_ok=True)
        json.dump(out, open(os.path.join(OUT_DIR, f"{w['start']}.json"), "w"), indent=1, ensure_ascii=False)
    return out
