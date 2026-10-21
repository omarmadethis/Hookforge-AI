"""Estimate on-screen caption band (centre y fraction, height fraction) at t=0.6 s: rows dense in pure-white pixels
that sit next to near-black stroke pixels. Used to compare our finals vs Omar's top reels (2026-10-20 audit)."""
import subprocess, json, glob, os, re, sys, numpy as np, pandas as pd
def frame(p, t=0.6, W=270, H=480):
    b = subprocess.run(["ffmpeg","-v","error","-ss",str(t),"-i",p,"-frames:v","1","-vf",f"scale={W}:{H}","-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout
    return np.frombuffer(b,np.uint8).reshape(H,W,3).astype(int) if len(b)==W*H*3 else None
def band(p):
    f = frame(p)
    if f is None: return None
    white = (f.min(2) > 235); dark = (f.max(2) < 40)
    near = np.zeros_like(white); near[:, 1:] |= dark[:, :-1]; near[:, :-1] |= dark[:, 1:]
    score = (white & np.roll(near, 0)).sum(1) + (white & np.roll(dark,1,0)).sum(1)
    rows = np.where(score > 6)[0]; rows = rows[rows < f.shape[0]*0.6]
    if len(rows) < 3: return None
    return dict(y=round(float(np.median(rows))/f.shape[0],3), h=round((rows.max()-rows.min())/f.shape[0],3))
if __name__ == "__main__":
    ours = [f for f in glob.glob("out/deliver/*.mp4") if re.search(r"v7|v4\.mp4|v3\.mp4",f) and "Proof" not in f]
    c = pd.read_csv("private/corpus/corpus.csv", low_memory=False); c["views"]=pd.to_numeric(c.views,errors="coerce")
    own = [f for f in c[(c.source=="own")&c.file.notna()&(c.views>=50000)].sort_values("views",ascending=False).file if os.path.exists(f)][:15]
    r = {"ours":{os.path.basename(f):band(f) for f in ours},"omar":{os.path.basename(f):band(f) for f in own}}
    print(json.dumps(r,indent=0))
