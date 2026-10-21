"""D136 post-publish watcher (DRY RUN with fixtures). For every published reel on the CURRENT pages (routing, active
products only) it applies the D93-6 caption-swap rule - 40,000 total views OR +10,000 views inside any one-hour
window (from posted_pt = 0) - via fb_caption.traction, and writes a swap approval item via fb_caption.queue_swap into a
TEMP dir (dry run). Nothing is edited: published FB captions change only after Omar approves (Graph API / Business Suite).
  dry_run(snapshots) snapshots = [{reel_key, post_id, page, product, caption, posted_pt, snapshot_pt, views}] (several
  snapshots per reel = history) -> learning/post_watch/dryrun_<ts>.json"""
import os, json, tempfile, datetime, collections
from zoneinfo import ZoneInfo
from .config import REPO
from . import fb_caption, routing, products

PT = ZoneInfo("America/Los_Angeles")

def current_pages():
    c = routing.cfg(); act = set(products.active())
    return {pg: [pk for pk, ks in c["products"].items() if pg in ks and pk in act] for pg in c["pages"] if any(pg in ks for pk, ks in c["products"].items() if pk in act)}

def dry_run(snapshots, write=True):
    pages = current_pages(); by = collections.defaultdict(list)
    for s in snapshots: by[s["reel_key"]].append(s)
    tmp = tempfile.mkdtemp(prefix="swapdry_"); old = fb_caption.SWAP_DIR; fb_caption.SWAP_DIR = tmp; out = []
    try:
        for rk, ss in by.items():
            ss = sorted(ss, key=lambda s: s["snapshot_pt"]); last = ss[-1]
            row = dict(page=last["page"], product=last["product"])
            if last["page"] not in pages or last["product"] not in pages[last["page"]]:
                out.append(dict(reel_key=rk, page=last["page"], product=last["product"], action="skip", why="not a current page / retired product")); continue
            t = fb_caption.traction(last, [(s["snapshot_pt"], s["views"]) for s in ss[:-1]])
            already = bool(__import__("re").search(r"(?i)get it here|get yours|shop (here|now)|https?://", str(last.get("caption", ""))))
            if already: out.append(dict(row, reel_key=rk, action="skip", why="caption already carries the link", **t)); continue
            if not t["swap"]: out.append(dict(row, reel_key=rk, action="watch", **t)); continue
            it = fb_caption.queue_swap(dict(reel_key=rk, post_id=last.get("post_id"), page=last["page"], product=last["product"], caption=last["caption"], reason=t["reason"]))
            out.append(dict(row, reel_key=rk, action="SWAP_PROPOSED (dry run, awaiting Omar)", new_caption=it["new_caption"], blocked=it["blocked"], **t))
    finally: fb_caption.SWAP_DIR = old
    rep = dict(run_pt=datetime.datetime.now(PT).isoformat(timespec="seconds"), pages=pages, results=out, dry_run=True, swap_items_dir=tmp,
               rule=f"views >= {fb_caption.SWAP_VIEWS:,} or +{fb_caption.SWAP_HOUR_GAIN:,} within any 1 h window")
    if write:
        d = os.path.join(REPO, "learning", "post_watch"); os.makedirs(d, exist_ok=True)
        json.dump(rep, open(os.path.join(d, f"dryrun_{datetime.datetime.now(PT):%Y%m%d_%H%M}.json"), "w"), indent=1, ensure_ascii=False, default=str)
    return rep
