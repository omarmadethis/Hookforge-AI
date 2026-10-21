"""D96 hourly results snapshots for the 10K/hour caption-swap trigger (fb_caption.SWAP_HOUR_GAIN). READ-ONLY.
Each tick (default every 60 min, aligned to :00 PT + jitter-free):
  1. results_feed.ingest: Meta Business Suite CSVs in learning/results/inbox + Graph GETs when META_TOKEN is in the
     environment (GET only; token never stored). A snapshot is written ONLY when there is new data, so a stale export
     is never re-stamped as a new hour (that would fake a 0-gain hour).
  2. results_feed.run refreshes reels/velocity/outcomes; fb_caption.check_traction finds reels that gained >= 10K in
     one hour or hit 40K; each becomes an approval ITEM (fb_caption.queue_swap) - nothing is edited or posted.
  3. a line in learning/results/snapshot_log.jsonl (ts, rows, snapshot, swap candidates, graph on/off).
Run: python3 -m hookforge.snapshot_scheduler --loop  (single-instance lock: learning/results/.snapshot.lock)"""
import os, sys, json, time, datetime, fcntl
from zoneinfo import ZoneInfo
from . import results_feed as RF

PT = ZoneInfo("America/Los_Angeles")
LOG = os.path.join(RF.RES, "snapshot_log.jsonl")
LOCK = os.path.join(RF.RES, ".snapshot.lock")
INTERVAL_S = 3600

def tick(use_graph=None, queue_swaps=True):
    use_graph = bool(os.environ.get("META_TOKEN")) if use_graph is None else use_graph
    now = datetime.datetime.now(PT).isoformat(timespec="minutes")
    new, snap = RF.ingest(use_graph=use_graph)
    rec = dict(ts_pt=now, rows=len(new), snapshot=snap, graph="on" if use_graph else "off (META_TOKEN not set)", swaps=[])
    if snap:
        RF.run(use_graph=False)                     # already ingested; just refresh joins/velocity
        from . import fb_caption
        for c in fb_caption.check_traction():
            rec["swaps"].append(dict(reel=c["reel_key"], reason=c["reason"]))
            if queue_swaps:
                sid = "swap_" + "".join(ch if ch.isalnum() else "_" for ch in str(c.get("reel_key") or c.get("post_id")))
                if not os.path.exists(os.path.join(fb_caption.SWAP_DIR, sid + ".json")): fb_caption.queue_swap(c)
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a") as fh: fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec

def loop(interval=INTERVAL_S):
    os.makedirs(os.path.dirname(LOCK), exist_ok=True); fh = open(LOCK, "w")
    try: fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError: print("another snapshot loop is running"); return
    while True:
        try: print(tick(), flush=True)
        except Exception as e: print(dict(error=repr(e)[:300]), flush=True)
        n = time.time(); time.sleep(interval - (n % interval) + 5)   # next hour boundary (+5 s)

def ensure_running():
    """Start the supervisor if it is not running (idempotent; flock inside the script makes a 2nd start a no-op)."""
    import subprocess
    sup = os.path.join(RF.REPO, "automation", "snapshot_supervisor.sh")
    lk = os.path.join(RF.RES, ".supervisor.lock")
    if os.path.exists(lk):
        fh = open(lk, "a")
        try: fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB); fcntl.flock(fh, fcntl.LOCK_UN)
        except BlockingIOError: return "running"
    subprocess.Popen(["setsid", "nohup", sup], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    return "started"

if __name__ == "__main__":
    if "--loop" in sys.argv: loop()
    elif "--ensure" in sys.argv: print(ensure_running())
    else: print(tick())
