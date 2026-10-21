#!/usr/bin/env python3
"""D167 Resumable, chunked Drive backup for Tier 2 (paid Higgsfield generations plus learning registries, about 6 GB).
State lives in learning/backup_state.json, so any session can pick up where the last one stopped.
  python3 automation/backup_chunks.py plan  [--tier 2] [--chunk-mb 500]  build chunks of pending files (not yet in docs/backup_drive_index.json)
  python3 automation/backup_chunks.py stage <chunk#>   deliver.stage + verify_staged every file in the chunk -> prints staged paths (no upload)
  python3 automation/backup_chunks.py record <path> <drive_id> [folder]   after an UploadFile succeeds: append to the index, delete the staged copy
  python3 automation/backup_chunks.py status
Uploading itself is done by an agent with the UploadFile tool, file by file, into Hookforge Backup/<folder>. There are no tokens on the
box, so nothing can upload unattended in the background, by design. Files the gate refuses are marked refused and never worked around.
The staged copies of each chunk are deleted once recorded, so the extra disk used stays around one chunk."""
import os, sys, json, hashlib, argparse
R = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(R, "engine")); sys.path.insert(0, os.path.join(R, "automation"))
STATE, IDX, PLAN = (os.path.join(R, *p) for p in (("learning", "backup_state.json"), ("docs", "backup_drive_index.json"), ("learning", "backup_plan.json")))
FOLDERS = {"out": "generations", "learning": "learning"}
load = lambda p, d: json.load(open(p)) if os.path.exists(p) else d
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
def staged_name(path): return "backup__" + path.replace("/", "__")

def plan(tier=2, chunk_mb=500):
    import backup_plan
    items, _ = backup_plan.plan(); done = {f["path"] for f in load(IDX, {"files": []})["files"]}
    st = load(STATE, {"files": {}}); chunks, cur, size = [], [], 0
    for i in items:
        if i["tier"] != tier or i["path"] in done or st["files"].get(i["path"], {}).get("status") in ("uploaded", "refused"): continue
        if i["bytes"] > 2e9: st["files"][i["path"]] = dict(status="too_big", bytes=i["bytes"]); continue
        if cur and size + i["bytes"] > chunk_mb * 1e6: chunks.append(cur); cur, size = [], 0
        cur.append(i["path"]); size += i["bytes"]; st["files"].setdefault(i["path"], dict(status="pending", bytes=i["bytes"]))
    if cur: chunks.append(cur)
    st.update(tier=tier, chunk_mb=chunk_mb, chunks=chunks); json.dump(st, open(STATE, "w"), indent=1); return st

def stage(n):
    from hookforge import deliver as D
    st = load(STATE, None); out = []
    for p in st["chunks"][n]:
        f = st["files"][p]
        if f["status"] in ("uploaded", "refused"): continue
        try:
            s = D.stage(os.path.join(R, p), staged_name(p)); D.verify_staged(s); f.update(status="staged", staged=s, sha256=sha(s)); out.append(s)
        except Exception as e: f.update(status="refused", reason=str(e)[-200:])
    json.dump(st, open(STATE, "w"), indent=1); return out

def record(path, drive_id, folder=None):
    st = load(STATE, None); f = st["files"][path]; idx = load(IDX, None)
    folder = folder or FOLDERS.get(path.split("/")[0], "misc")
    idx["files"].append(dict(path=path, id=drive_id, name=os.path.basename(path), folder=folder, size=os.path.getsize(f["staged"]),
                             orig_size=os.path.getsize(os.path.join(R, path)), sha256=f["sha256"], sanitized=os.path.getsize(f["staged"]) != os.path.getsize(os.path.join(R, path))))
    json.dump(idx, open(IDX, "w"), indent=1, ensure_ascii=False)
    os.remove(f["staged"]); f.update(status="uploaded", drive_id=drive_id); f.pop("staged", None); json.dump(st, open(STATE, "w"), indent=1)

PRIO = {"mp4": 0, "mov": 0, "png": 1, "jpg": 1, "jpeg": 1, "webp": 1}       # D172: paid media first, rebuildable json/text last
def stage_next(n):
    """Stage the next n pending files across all chunks, mp4 first, then images, then everything else."""
    from hookforge import deliver as D
    st = load(STATE, None)
    todo = sorted((p for p, f in st["files"].items() if f["status"] == "pending"), key=lambda p: (PRIO.get(p.rsplit(".", 1)[-1].lower(), 9), p))[:n]; out = []
    for p in todo:
        f = st["files"][p]
        try: s = D.stage(os.path.join(R, p), staged_name(p)); D.verify_staged(s); f.update(status="staged", staged=s, sha256=sha(s)); out.append(s)
        except Exception as e: f.update(status="refused", reason=str(e)[-200:])
        json.dump(st, open(STATE, "w"), indent=1)
    return out

def dedupe():
    """D170: a pending file byte-identical (sha256) to one already on Drive is recorded under the existing drive id, with no re-upload."""
    st = load(STATE, None); idx = load(IDX, None); by = {f["sha256"]: f for f in idx["files"] if f.get("sha256")}; n = 0
    for p, f in st["files"].items():
        if f["status"] not in ("pending", "staged"): continue
        h = f.get("sha256") or sha(os.path.join(R, p)); src = by.get(h)
        if not src: continue
        idx["files"].append(dict(path=p, id=src["id"], name=os.path.basename(p), folder=src["folder"], size=src["size"], orig_size=os.path.getsize(os.path.join(R, p)),
                                 sha256=h, sanitized=src.get("sanitized", False), dedup_of=src["path"]))
        if f.get("staged") and os.path.exists(f["staged"]): os.remove(f["staged"])
        f.update(status="uploaded", drive_id=src["id"], dedup_of=src["path"]); f.pop("staged", None); n += 1
    json.dump(idx, open(IDX, "w"), indent=1, ensure_ascii=False); json.dump(st, open(STATE, "w"), indent=1); return n

def status():
    st = load(STATE, {"files": {}, "chunks": []}); c = {}
    for f in st["files"].values(): k = f["status"]; c.setdefault(k, [0, 0]); c[k][0] += 1; c[k][1] += f["bytes"]
    return dict(chunks=len(st.get("chunks", [])), by_status={k: dict(n=n, gb=round(b / 1e9, 2)) for k, (n, b) in c.items()})

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("args", nargs="*"); ap.add_argument("--tier", type=int, default=2); ap.add_argument("--chunk-mb", type=int, default=500)
    a = ap.parse_args()
    if a.cmd == "plan": s = plan(a.tier, a.chunk_mb); print(json.dumps(dict(status(), chunk_sizes_mb=[round(sum(s["files"][p]["bytes"] for p in c) / 1e6) for c in s["chunks"]])))
    elif a.cmd == "stage": print("\n".join(stage(int(a.args[0]))))
    elif a.cmd == "recmany":                       # stdin lines: <staged basename>\t<drive_id>
        st = load(STATE, None); by = {os.path.basename(f["staged"]): p for p, f in st["files"].items() if f.get("staged")}
        for ln in sys.stdin:
            if ln.strip(): n, i = ln.rstrip("\n").split("\t"); record(by[n], i)
        print(json.dumps(status()))
    elif a.cmd == "next": [print(os.path.basename(x)) for x in stage_next(int(a.args[0]))]
    elif a.cmd == "dedupe": print("deduped", dedupe())
    elif a.cmd == "record": record(*a.args); print("recorded", a.args[0])
    else: print(json.dumps(status(), indent=1))
