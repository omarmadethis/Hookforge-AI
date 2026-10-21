"""D160: docs/MANIFEST_EXCLUDED.md = every git-ignored asset (paths + sizes), so a fresh clone knows what to restore.
Groups by directory; lists every individual file >= 10 MB and every file > 50 MB. Secret-pattern files are listed by NAME only
(no content). Run: cd engine && python3 scripts/build_manifest.py"""
import subprocess, os, json, collections, datetime, hashlib
from zoneinfo import ZoneInfo
R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
files = subprocess.run(["git", "ls-files", "--others", "--ignored", "--exclude-standard", "-z"], cwd=R, capture_output=True).stdout.decode().split("\0")
rows = []
for f in filter(None, files):
    try: rows.append((f, os.path.getsize(os.path.join(R, f))))
    except OSError: pass
fmt = lambda b: f"{b/1e9:.2f} GB" if b >= 1e9 else f"{b/1e6:.1f} MB" if b >= 1e6 else f"{b/1e3:.0f} KB"
grp = collections.defaultdict(lambda: [0, 0])
for f, b in rows:
    k = "/".join(f.split("/")[:2]) if "/" in f else f; grp[k][0] += 1; grp[k][1] += b
why = {"out": "generated renders/runs (regenerable or delivered elsewhere)", "data": "features DB + reel proxies (shared features workstream, 5.7 GB)", "private": "PRIVATE (D10): sales, IDs, team, corpus",
       "assets": "product media", "refs": "reference media", "music": "copyrighted songs (*.m4a)", "learning": "large logs/registries"}
now = datetime.datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%Y-%m-%d %-I:%M %p PT")
L = [f"# MANIFEST of excluded assets (not in git)\nGenerated {now} by engine/scripts/build_manifest.py. Total {len(rows)} files, {fmt(sum(b for _, b in rows))}. "
     "Restore from the box (/workspace/hookforge) or the owner's Drive; never commit these. Secret/env files would be listed by name only (none found at generation time).\n",
     "## By directory\n| dir | files | size | why excluded |\n|---|---|---|---|"]
for k, (n, b) in sorted(grp.items(), key=lambda x: -x[1][1]):
    if b < 1e6 and n < 20: continue
    L.append(f"| {k}/ | {n} | {fmt(b)} | {why.get(k.split('/')[0], 'media / cache / lock')} |")
IDX = os.path.join(R, "docs", "backup_drive_index.json")   # D164 Drive backup ids
drv = {f["path"]: f["id"] for f in json.load(open(IDX))["files"]} if os.path.exists(IDX) else {}
big = sorted([r for r in rows if r[1] >= 10 * 2**20], key=lambda r: -r[1])
L += [f"\n## Every excluded file >= 10 MB ({len(big)}; >50 MB marked **)\n| path | size | drive_id |\n|---|---|---|"] + [f"| {'**' if b > 50*2**20 else ''}{f}{'**' if b > 50*2**20 else ''} | {fmt(b)} | {drv.get(f, '')} |" for f, b in big]
L += [f"\n## Backed up to Drive \"Hookforge Backup\" ({len(drv)} files; docs/backup_drive_index.json)\n| path | drive_id |\n|---|---|"] + [f"| {p} | {i} |" for p, i in sorted(drv.items())]
open(os.path.join(R, "docs", "MANIFEST_EXCLUDED.md"), "w").write("\n".join(L) + "\n"); print(len(rows), len(big))
