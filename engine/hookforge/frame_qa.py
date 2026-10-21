"""F90 / D81 strict frame self-QA (Omar 2026-10-20 9:27 AM: "these should be caught before he sees anything").
Every start frame gets a recorded checklist BEFORE Omar sees it; sheets/contact sheets may only be built when every frame passes.
    frame_qa.record(dir, frame, checks={...}, notes="", reviewer="agent-fullres")   # checks: key -> True/False (+ reason in notes)
    frame_qa.require_all_pass(dir, frames)   # raises FrameQAFail listing failures; call before ANY sheet build
    frame_qa.build_sheet(dir, frames, out)    # gated sheet builder (PIL, metadata-free)
The reviewer must inspect at FULL resolution with zoomed crops of product + animal + hands (not a thumbnail)."""
import os, json, datetime
CHECKS = {
 "physics_no_clipping": "no body part / object passes through mesh, wire, ground or other bodies",
 "inside_or_outside": "cat clearly fully inside the zipped ball, or fully outside it - never straddling the mesh",
 "ground_contact": "ball and feet touch the ground correctly (no floating, no paws below the ball floor)",
 "cat_matches_ref": "cream snow Bengal, tan rosettes, clear blue eyes (second cat matches its own ref)",
 "product_matches_ref": "black mesh ball on wire hoops, white-trim zipper, no logo (or folded disc per ref)",
 "cast_outfit_match": "same person/outfit as the cast ref for that plan",
 "flag_tiny": "exactly one small US flag, <~2% of frame, background",
 "gaze_ok": "organic scene: nobody looks at the camera",
 "no_ai_tells": "no warped hands/fingers, extra limbs, melted text, plastic skin, impossible geometry",
}
class FrameQAFail(Exception): pass
def _path(d): return os.path.join(d, "frame_qa.json")
def load(d): return json.load(open(_path(d))) if os.path.exists(_path(d)) else {}
def record(d, frame, checks, notes="", reviewer="agent-fullres", file_sha=None):
    miss = [k for k in CHECKS if k not in checks]
    if miss: raise ValueError(f"{frame}: checklist incomplete, missing {miss}")
    db = load(d); fails = [k for k, v in checks.items() if not v]
    db[frame] = dict(passed=not fails, fails=fails, checks=checks, notes=notes, reviewer=reviewer, file_sha=file_sha,
                     at=datetime.datetime.now().isoformat(timespec="seconds"))
    json.dump(db, open(_path(d), "w"), indent=1); return db[frame]
def _sha(p):
    import hashlib; return hashlib.sha256(open(p, "rb").read()).hexdigest()
def require_all_pass(d, frames):
    db = load(d); bad = []
    for f in frames:
        r = db.get(f); p = os.path.join(d, f + ".png")
        if not r: bad.append(f"{f}: never reviewed")
        elif not r["passed"]: bad.append(f"{f}: FAIL {r['fails']} - {r['notes']}")
        elif r.get("file_sha") and os.path.exists(p) and _sha(p) != r["file_sha"]: bad.append(f"{f}: file changed after review")
    if bad: raise FrameQAFail("; ".join(bad))
    return True
def build_sheet(d, frames, out, w=432, h=768):
    require_all_pass(d, frames)
    from PIL import Image; import numpy as np
    s = Image.new("RGB", (w * len(frames), h))
    for i, f in enumerate(frames): s.paste(Image.open(os.path.join(d, f + ".png")).convert("RGB").resize((w, h)), (w * i, 0))
    Image.fromarray(np.array(s)).save(out, quality=90); return out
