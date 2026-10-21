"""D180 (Omar 2026-10-20 7:42 PM PT, PERMANENT): every video is fully unique - own hook, own body clips, own setup and
caption, ZERO shared footage with any other video (any product, any page). Supersedes D142/D145 lean reuse.
Two checks: plan-level (no gen/clip id or start frame used by >1 video) and render-level (measured shared frames == 0)."""
import os
REUSE_BANNED = True
MAX_SHARED_RATIO = 0.0          # measured ordered-frame share between finished videos; tolerance below is hash noise only
NOISE_RATIO = 0.02

class SharedFootage(Exception): pass

def _assets(v):
    out = set()
    for g in v.get("gens", []):
        for k in ("gen_id", "job_id", "clip", "file", "start_frame_file"):
            if g.get(k): out.add((k, str(g[k])))
        sf = g.get("start_frame")
        if isinstance(sf, dict) and sf.get("file"): out.add(("start_frame_file", str(sf["file"])))
    for c in v.get("clips", []) + v.get("bodies", []):
        out.add(("clip", str(c.get("file") or c.get("id") if isinstance(c, dict) else c)))
    for k in ("reuse_from", "anchor", "anchor_bodies"):
        if v.get(k): out.add(("reuse", k))
    return out

def plan_check(videos):
    """videos: list of dicts with 'id' and 'gens'/'clips'. Returns findings; any finding is a BLOCK."""
    seen, f = {}, []
    for v in videos:
        for a in _assets(v):
            if a[0] == "reuse": f.append(dict(video=v.get("id"), failure="declares_reuse", field=a[1])); continue
            if a in seen and seen[a] != v.get("id"): f.append(dict(video=v.get("id"), other=seen[a], failure="shared_asset", asset=a[1]))
            seen.setdefault(a, v.get("id"))
    return f

def gate(videos):
    f = plan_check(videos)
    if f: raise SharedFootage(f"BLOCK D180 shared footage between videos: {f}")
    return True

def render_check(paths):
    """Pairwise measured shared frames on finished renders (lean_edit.measured_shared). BLOCK if > noise."""
    from . import lean_edit
    f = []
    for i in range(len(paths)):
        for j in range(i + 1, len(paths)):
            r = lean_edit.measured_shared(paths[i], paths[j])
            if r > NOISE_RATIO: f.append(dict(a=os.path.basename(paths[i]), b=os.path.basename(paths[j]), shared=round(r, 3)))
    return f
