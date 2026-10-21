"""Detect looped / repeated footage: a frame that matches an earlier NON-adjacent frame
within the same shot (backward jump). Uses 32x32 gray thumbnails + normalized MAD + motion check."""
import subprocess, numpy as np

def _frames(path, fps=30, w=48, h=64):
    raw = subprocess.run(["ffmpeg","-v","error","-i",path,"-vf",f"fps={fps},scale={w}:{h},format=gray",
                          "-f","rawvideo","-"],capture_output=True,check=True).stdout
    return np.frombuffer(raw,np.uint8).reshape(-1,h,w).astype(np.float32), fps

def find_repeats(path, fps=30, min_gap_s=0.5, min_run=6, match_thr=2.0, cut_thr=25.0, motion_min=0.6):
    """Return list of dicts {src_t, dup_t, len_s}. A repeat = run of >=min_run consecutive frames whose
    content matches frames >=min_gap_s earlier in the same shot, where the source run actually moves
    (so a static held shot doesn't false-trigger)."""
    F, fps = _frames(path, fps)
    n = len(F)
    if n < 2: return []
    d = np.abs(np.diff(F,axis=0)).mean(axis=(1,2))
    shot = np.concatenate([[0], np.cumsum(d > cut_thr)])
    gap = int(min_gap_s*fps); flat = F.reshape(n,-1)
    hits = []; i = gap
    while i < n:
        cand = [j for j in range(max(0,i-int(8*fps)), i-gap+1) if shot[j]==shot[i]]
        best=None
        if cand:
            errs = np.abs(flat[cand]-flat[i]).mean(axis=1); k=int(np.argmin(errs))
            if errs[k] < match_thr: best=cand[k]
        if best is not None:
            run=0
            while i+run<n and best+run<i and shot[i+run]==shot[i] and \
                  np.abs(flat[i+run]-flat[best+run]).mean()<match_thr: run+=1
            motion = d[best:best+run].mean() if run>1 else 0
            if run>=min_run and motion>=motion_min:
                hits.append(dict(src_t=round(best/fps,2),dup_t=round(i/fps,2),len_s=round(run/fps,2)))
                i+=run; continue
        i+=1
    return hits
