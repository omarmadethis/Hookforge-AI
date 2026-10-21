"""Pacing / timeline gates (Omar 2026-10-19 t2xx: 'that clip lingers way too long for how uninteresting it is').
- hold_violations: any non-reveal shot longer than Omar's p90 hold for its role (style.json timing.hold_p90_s) BLOCKS,
  unless it's the reveal or marked proven=True.
- near_duplicate_cuts: adjacent shots (even from DIFFERENT clips) whose frames across the cut look the same -> reads as a
  repeated scene (TrumpGlow A v6: G5 ended on the logo close-up, G3 opened on the same framing).
- variants_identical: song variants of one video must have bit-identical decoded video."""
import json, os, subprocess, hashlib, numpy as np
STYLE = os.path.join(os.path.dirname(__file__), "..", "..", "learning", "editing_style", "style.json")

def p90():
    return json.load(open(STYLE))["timing"]["hold_p90_s"]

def infer_roles(tl):
    shots = tl.get("shots", []); rv = tl.get("reveal_t"); out = []
    for i, s in enumerate(shots):
        r = s.get("role")
        if not r:
            if i == 0: r = "opener"
            elif rv is not None and s["t0"] <= rv < s["t1"]: r = "reveal"
            elif i == len(shots) - 1: r = "ending"
            elif rv is not None and s["t1"] <= rv: r = "before"
            else: r = "after"
        out.append(r)
    return out

def hold_violations(tl):
    lim = p90(); probs = []
    for s, r in zip(tl.get("shots", []), infer_roles(tl)):
        if r == "reveal" or s.get("proven"): continue
        d = s["t1"] - s["t0"]; cap = lim.get(r, lim["non_reveal"])
        if d > cap + 0.02: probs.append(f"{s.get('gen')} ({r}) holds {d:.2f}s > Omar p90 {cap}s - trim or speed up (<=1.5x)")
    return probs

def _thumb(path, t):
    raw = subprocess.run(["ffmpeg","-v","error","-ss",f"{max(t,0):.3f}","-i",path,"-frames:v","1","-vf","scale=64:112,format=gray",
                          "-f","rawvideo","-"],capture_output=True,check=True).stdout
    a = np.frombuffer(raw, np.uint8).astype(np.float32); return (a - a.mean()) / (a.std() + 1e-6)

def near_duplicate_cuts(tl, path, corr_thr=0.88):
    out = []
    for a, b in zip(tl.get("shots", []), tl.get("shots", [])[1:]):
        c = float((_thumb(path, b["t0"] - 0.07) * _thumb(path, b["t0"] + 0.07)).mean())
        if c >= corr_thr: out.append(dict(cut_t=round(b["t0"], 3), a=a.get("gen"), b=b.get("gen"), corr=round(c, 3)))
    return out

def video_hash(path):
    r = subprocess.run(["ffmpeg","-v","error","-i",path,"-map","0:v:0","-vf","scale=270:480","-f","framemd5","-"],capture_output=True,text=True,check=True).stdout
    return hashlib.md5("".join(l.split(",")[-1] for l in r.splitlines() if l and not l.startswith("#")).encode()).hexdigest()

def variants_identical(paths):
    h = {p: video_hash(p) for p in paths}
    return len(set(h.values())) == 1, h
