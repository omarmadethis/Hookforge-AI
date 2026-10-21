"""Gate 2: jump cut inside one take = two ADJACENT timeline segments from the same source clip id,
confirmed visually by high similarity across the boundary in the final render."""
import subprocess, numpy as np

def _frame(path, t, w=48, h=64):
    raw = subprocess.run(["ffmpeg","-v","error","-ss",f"{max(t,0):.3f}","-i",path,"-frames:v","1",
                          "-vf",f"scale={w}:{h},format=gray","-f","rawvideo","-"],capture_output=True,check=True).stdout
    return np.frombuffer(raw,np.uint8).astype(np.float32)

def find_same_take_splices(shots, path=None, sim_thr=30.0):
    """shots: list of dicts with gen/clip id + t0,t1 (timeline.json 'shots'). Returns findings.
    Same clip id adjacent -> candidate; if path given, boundary frames' mean abs diff < sim_thr confirms
    (a real angle change between different shots of the same id would differ a lot)."""
    out = []
    for a, b in zip(shots, shots[1:]):
        ga, gb = a.get("gen") or a.get("clip"), b.get("gen") or b.get("clip")
        if not ga or ga != gb: continue
        f = dict(clip=ga, boundary_t=round(b["t0"], 3), trim_a=a.get("trim"), trim_b=b.get("trim"))
        if path:
            diff = float(np.abs(_frame(path, b["t0"]-0.05) - _frame(path, b["t0"]+0.05)).mean())
            f["boundary_diff"] = round(diff, 1); f["visual_confirmed"] = diff < sim_thr
        else: f["visual_confirmed"] = None
        if f["visual_confirmed"] is not False: out.append(f)
    return out
