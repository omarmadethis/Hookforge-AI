"""Auto-posting interface (D41) - DISABLED. Nothing in this module posts. enqueue() writes a scheduled row to
learning/post_queue.csv; a Poster backend may only be activated when AUTO_POST_ENABLED is True in config AND
private/autopost_approval.json exists with Omar's explicit approval (page list, date, signer). Until then
DisabledPoster raises. Schedule = page windows (posting_windows.json): core slots in exploit windows, experiment
slots in explore windows; >= MIN_GAP_H between posts on the same page (gap<12h is a hypothesis, x0.52).
"""
import os, csv, json, datetime
from .config import REPO

AUTO_POST_ENABLED = False
MIN_GAP_H = 4
QUEUE = os.path.join(REPO, "learning", "post_queue.csv")
FIELDS = ["queued_at", "page", "product", "slot", "window_pt", "video_path", "caption", "status", "approved_by"]

class DisabledPoster:
    name = "disabled"
    def post(self, *a, **k): raise PermissionError("Auto-posting is disabled until Omar approves (D41).")

class MetaGraphPoster(DisabledPoster):
    """Future: Meta Graph API reels publish (FB Page / IG). Interface only - not implemented, no tokens read."""
    name = "meta_graph (not implemented)"

def backend():
    appr = os.path.join(REPO, "private", "autopost_approval.json")
    return MetaGraphPoster() if (AUTO_POST_ENABLED and os.path.exists(appr)) else DisabledPoster()

def enqueue(page, product, slot, window_pt, video_path, caption):
    new = not os.path.exists(QUEUE)
    with open(QUEUE, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        if new: w.writeheader()
        w.writerow(dict(queued_at=datetime.datetime.now(__import__("zoneinfo").ZoneInfo("America/Los_Angeles")).isoformat(timespec="seconds"), page=page, product=product, slot=slot, window_pt=window_pt,
                        video_path=video_path, caption=caption, status="queued_manual_post", approved_by=""))
