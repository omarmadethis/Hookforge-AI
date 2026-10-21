"""D107 Graph API caption edit for a PUBLISHED FB reel (Buffer cannot edit sent posts). APPROVAL-GATED.
Flow: fb_caption.queue_swap -> publish.approve_swap(id, "Omar", quote) -> graph_caption.execute(id, video_id)
  1. refuses unless the swap item is APPROVED, its text sha matches the approval, and the caption passes the gates
  2. the Page token comes ONLY from the environment (META_PAGE_TOKEN), supplied through the Secure Form / box
     handoff for this one run - never read from or written to a file, never logged, never returned
  3. GET /{video-id}?fields=id,description (ownership + before-text check; the before-text must still be the
     caption the swap was approved against, so we never overwrite a caption someone changed meanwhile)
  4. POST /{video-id} description=<approved text>  (needs pages_manage_posts + pages_read_engagement on that Page)
  5. GET again to verify, then publish.mark_swapped(id, "graph_api") with before/after, no token
plan(id, video_id) returns the exact request (token redacted) for Omar's review without calling anything."""
import os, json, hashlib, urllib.request, urllib.parse

GRAPH = "https://graph.facebook.com/v21.0"
TOKEN_ENV = "META_PAGE_TOKEN"
SCOPES = ("pages_manage_posts", "pages_read_engagement")

class Refused(Exception): pass

def _item(sid):
    from . import publish
    return publish._swap_load(sid)

def _check(sid):
    from . import publish
    it = _item(sid)
    if it["status"] != publish.STATUS_OK: raise Refused(f"{sid} is {it['status']} - Omar must approve the swap first")
    if hashlib.sha256((it["new_caption"] or "").encode()).hexdigest() != it.get("approved_text_sha"): raise Refused("swap text changed after approval")
    probs = publish._caption_checks(it["new_caption"])
    if probs or "PLACEHOLDER" in it["new_caption"]: raise Refused("; ".join(probs) or "placeholder URL")
    return it

def plan(sid, video_id):
    it = _check(sid)
    if not str(video_id).isdigit(): raise Refused("video_id must be the numeric FB video id")
    return dict(method="POST", url=f"{GRAPH}/{video_id}", data=dict(description=it["new_caption"], access_token="<Page token via Secure Form>"),
                needs_scopes=SCOPES, verify=f"GET {GRAPH}/{video_id}?fields=id,description")

def _call(method, path, token, opener=None, **params):
    params["access_token"] = token
    if method == "GET":
        req = urllib.request.Request(f"{GRAPH}/{path}?{urllib.parse.urlencode(params)}", method="GET")
    else:
        req = urllib.request.Request(f"{GRAPH}/{path}", data=urllib.parse.urlencode(params).encode(), method="POST")
    try:
        with (opener or urllib.request.urlopen)(req, timeout=30) as r: return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        raise Refused(f"Graph {method} {path.split('?')[0]} -> HTTP {e.code}: {body.replace(token, '<redacted>')[:300]}") from None

def execute(sid, video_id, opener=None, token=None):
    """Runs ONLY after Omar's approval; token from env (or passed in-memory by the secure handoff), never persisted."""
    it = _check(sid); token = token or os.environ.get(TOKEN_ENV)
    if not token: raise Refused(f"no Page token in env {TOKEN_ENV}: Omar enters it via the Secure Form for this run (scopes {', '.join(SCOPES)})")
    before = _call("GET", str(video_id), token, opener, fields="id,description")
    old = (before.get("description") or "").strip()
    if it.get("old_caption") and old and old != it["old_caption"].strip():
        raise Refused("live caption differs from the one this swap was approved against - re-queue the swap")
    r = _call("POST", str(video_id), token, opener, description=it["new_caption"])
    if not r.get("success", r.get("id")): raise Refused(f"Graph did not confirm: {str(r)[:200]}")
    after = _call("GET", str(video_id), token, opener, fields="id,description")
    if (after.get("description") or "").strip() != it["new_caption"].strip(): raise Refused("verify failed: description not updated")
    from . import publish
    return publish.mark_swapped(sid, dict(via="graph_api", video_id=str(video_id), before=old))
