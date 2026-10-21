"""D130 render queue: every calendar slot is paired with ONE Omar-approved video or flagged NEEDS_VIDEO, so the
calendar can never yield a post without its video.
  build(calendar) -> learning/render_queue/<start>.json: per slot status
     READY        - bound to a publish_queue item that is APPROVED (Omar), same product + page, staged file still
                    verifies (deliver.verify_staged) and its sha matches the approved sha; each item binds to one slot only
     NEEDS_URL    - approved video bound but no public video_url yet (publish.set_video_url -> re-approval)
     NEEDS_VIDEO  - nothing approved: render need = the queued concept id (approval_queue) + credits, or 'no concept'
  schedulable(slot) -> raises NotSchedulable unless READY (content_calendar marks every slot through this)."""
import os, json, datetime
from .config import REPO
from . import publish, deliver, approval_queue

DIR = os.path.join(REPO, "learning", "render_queue")
class NotSchedulable(Exception): pass

def _approved_videos():
    out = []
    for it in publish.pending():
        if it.get("status") != publish.STATUS_OK: continue
        try:
            deliver.verify_staged(it["staged"]); ok = deliver._sha(it["staged"]) == it.get("approved_file_sha", it["sha256"])
        except Exception: ok = False
        if ok: out.append(it)
    return sorted(out, key=lambda i: i.get("approved_at") or "")

def build(cal, write=True):
    vids = _approved_videos(); used = set()
    concepts = {i["product"]: i for i in approval_queue.pending() if i.get("status") == "AWAITING_OMAR_APPROVAL"}
    rows = []
    for s in cal["slots"]:
        v = next((i for i in vids if i["id"] not in used and i.get("product") == s["product"] and (i.get("buffer") or {}).get("page_key") == s["page"]), None)
        if v:
            used.add(v["id"]); st = "READY" if v["payload"].get("assets") else "NEEDS_URL"
            rows.append(dict(s, render_status=st, publish_item=v["id"], video_sha=v["sha256"][:12]))
        else:
            c = concepts.get(s["product"])
            rows.append(dict(s, render_status="NEEDS_VIDEO", publish_item=None,
                             render_need=dict(concept=c["id"], credits=c["credits"], ready_for_approval=c.get("ready_for_approval")) if c else "no queued concept - run concept_lab"))
    out = dict(start=cal["start"], slots=rows, summary={k: sum(1 for r in rows if r["render_status"] == k) for k in ("READY", "NEEDS_URL", "NEEDS_VIDEO")})
    if write: os.makedirs(DIR, exist_ok=True); json.dump(out, open(os.path.join(DIR, f"{cal['start']}.json"), "w"), indent=1, ensure_ascii=False)
    return out

def schedulable(slot):
    if slot.get("render_status") != "READY" or not slot.get("publish_item"):
        raise NotSchedulable(f"{slot['day']} {slot['page']} {slot['product']}: {slot.get('render_status', 'NO VIDEO')} - no post without its approved video")
    publish.ready_payload(slot["publish_item"])         # re-verifies approval, file sha, payload sha, URL
    return True
