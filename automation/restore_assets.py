#!/usr/bin/env python3
"""D163 Asset restore PLAN (DRY RUN ONLY). Reads docs/MANIFEST_EXCLUDED.md (directory groups and every file
>= 10 MB) and plans how to rehydrate the git-excluded data/, out/ and other assets from Google Drive.
It never downloads, writes into data/ or out/, or calls any API. It only writes a plan JSON.
  python3 automation/restore_assets.py [--drive-index idx.json] [--out plan.json]
--drive-index: a JSON list of {id, name, size, path?} exported read-only from Drive by an agent (Drive search or
  list_folder). Entries are matched to manifest files by relative path, otherwise by name plus size (±1%).
Each item gets one action:
  present    already on disk at the expected size
  download   a Drive match was found (drive_id, dest, size). An agent restores it later with DownloadFile, file by file.
  unresolved no Drive copy is known. Restore from the box (/workspace/hookforge) or regenerate (out/ = renders).
  manual_only  private/ (D10) and anything sensitive. Never restored automatically.
--execute is refused (exit 2). Restoring is a separate, approved step."""
import os, re, sys, json, argparse, datetime
from zoneinfo import ZoneInfo
R = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MAN = os.path.join(R, "docs", "MANIFEST_EXCLUDED.md")
IDX = os.path.join(R, "docs", "backup_drive_index.json")   # D164: written after each Drive backup upload
SENSITIVE = re.compile(r"(^private/|\.env|secret|credential|cookie|token|bank|statement|tax|llc|rental|passport|license|vids w isaac|IMG_5172)", re.I)
UNIT = {"KB": 1e3, "MB": 1e6, "GB": 1e9}

def size(s):
    n, u = s.split(); return float(n) * UNIT[u]

def parse(path=MAN):
    dirs, files, sec = [], [], None
    for ln in open(path):
        if ln.startswith("## By directory"): sec = "d"
        elif ln.startswith("## Every excluded file"): sec = "f"
        elif ln.startswith("## "): sec = None                 # e.g. "Backed up to Drive" (read from the index)
        if re.match(r"\|\s*(dir|path|-+)\s*\|", ln): continue
        m = re.match(r"\|\s*(.+?)\s*\|\s*(.+?)\s*\|(?:\s*(.+?)\s*\|)?(?:\s*(.+?)\s*\|)?\s*$", ln)
        if not m or not sec: continue
        if sec == "d": dirs.append(dict(dir=m[1].rstrip("/"), files=int(m[2]), bytes=size(m[3]), why=m[4]))
        else: files.append(dict(path=m[1].strip("*"), bytes=size(m[2])))
    return dirs, files

def plan(index=None):
    dirs, files = parse()
    if index is None and os.path.exists(IDX): index = json.load(open(IDX))
    idx = index["files"] if isinstance(index, dict) else (index or [])
    by_path = {i.get("path"): i for i in idx if i.get("path")}
    items = []
    def match(rel, b):
        if rel in by_path: return by_path[rel]
        nm = os.path.basename(rel)
        return next((i for i in idx if i.get("name") == nm and i.get("size") and abs(float(i["size"]) - b) <= 0.01 * b + 1e6), None)
    big = {f["path"] for f in files}
    for i in idx:                                            # backed-up files that are below the manifest's 10 MB listing
        if i.get("path") and i["path"] not in big: files.append(dict(path=i["path"], bytes=float(i.get("orig_size") or i["size"]))); big.add(i["path"])
    for f in files:
        rel, b, full = f["path"], f["bytes"], os.path.join(R, f["path"])
        it = dict(kind="file", path=rel, bytes=int(b))
        if SENSITIVE.search(rel): it.update(action="manual_only")
        elif os.path.exists(full) and abs(os.path.getsize(full) - b) <= 0.01 * b + 1e6: it.update(action="present")
        elif (m := match(rel, b)): it.update(action="download", drive_id=m["id"], dest=rel, **({"sha256": m["sha256"]} if m.get("sha256") else {}))
        else: it.update(action="unresolved", hint="regenerate (renders)" if rel.startswith("out/") else "copy from the box /workspace/hookforge")
        items.append(it)
    for d in dirs:
        rel = d["dir"]; full = os.path.join(R, rel)
        if rel in big or any(b.startswith(rel + "/") for b in by_path): continue   # covered file by file
        it = dict(kind="dir", path=rel + "/", files=d["files"], bytes=int(d["bytes"]), why=d["why"])
        if SENSITIVE.search(rel + "/"): it.update(action="manual_only")
        elif os.path.isdir(full) and sum(len(fs) for _, _, fs in os.walk(full)) >= d["files"]: it.update(action="present")
        elif (m := by_path.get(rel) or by_path.get(rel + "/")): it.update(action="download", drive_id=m["id"], dest=rel + "/", note="folder: list it and download file by file")
        else: it.update(action="unresolved", hint="regenerate (renders)" if rel.startswith("out/") else "copy from the box /workspace/hookforge")
        items.append(it)
    tot = lambda a: int(sum(i["bytes"] for i in items if i["action"] == a))
    return dict(dry_run=True, generated_pt=datetime.datetime.now(ZoneInfo("America/Los_Angeles")).isoformat(timespec="seconds"),
                manifest=os.path.relpath(MAN, R), drive_index_entries=len(idx),
                summary={k: {a: dict(n=sum(1 for i in items if i["kind"] == k and i["action"] == a), bytes=int(sum(i["bytes"] for i in items if i["kind"] == k and i["action"] == a)))
                         for a in ("present", "download", "unresolved", "manual_only")} for k in ("file", "dir")},
                note="dir groups include their big files, so do not add file and dir bytes together",
                items=items)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--drive-index"); ap.add_argument("--out"); ap.add_argument("--execute", action="store_true")
    a = ap.parse_args()
    if a.execute:
        print("REFUSED: dry-run plan only (D163). Restoring needs a separate approved step.", file=sys.stderr); sys.exit(2)
    p = plan(json.load(open(a.drive_index)) if a.drive_index else None)
    out = a.out or os.path.join(R, "learning", "restore_plan.json")
    json.dump(p, open(out, "w"), indent=1)
    print(json.dumps(dict(out=out, **p["summary"]), indent=1))
