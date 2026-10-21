"""#7a Trump projector composite (D89): put PatriotsGlow art into REAL projector footage. Local only, zero spend.
Plate: research/product_footage/trump_projector/tp06_hr_photo_projection_close.mp4 (real door-light disc on a dark
surface, handheld, no burned-in text). Per frame: detect the lit disc (largest bright blob -> fitEllipse), smooth the
ellipse over time (handheld follows), warp the round art into the ellipse, light it like a projector (additive light
x surface albedo from the plate, radial falloff, slight defocus, edge vignette and the plate's colour cast), then
crop 9:16 around the disc, 720p (F: only hooks at 1080p), clean_export (zero metadata).
Usage: python3 tools/trump_projector/composite.py [--art PATH] [--plate PATH] [--secs N]
"""
import os, sys, argparse, subprocess, tempfile
import cv2, numpy as np
R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(R, "engine"))
PLATE = "/workspace/research/product_footage/trump_projector/tp06_hr_photo_projection_close.mp4"
ART = os.path.join(R, "assets", "patriotglow", "product", "3715deca-80ec-4996-b995-c400f8a9c8fe.png")
OUT = os.path.join(R, "out", "trump_projector")

def detect_disc(frame, thr=None):
    """(cx, cy, ax1, ax2, angle) of the projected disc, or None."""
    g = cv2.GaussianBlur(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (0, 0), 9)
    thr = thr or max(40, np.percentile(g, 99.0) * 0.45)
    m = (g > thr).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cs = [c for c in cs if len(c) >= 20]
    if not cs: return None
    c = max(cs, key=cv2.contourArea)
    if cv2.contourArea(c) < 0.004 * frame.shape[0] * frame.shape[1]: return None
    (cx, cy), (a1, a2), ang = cv2.fitEllipse(c)
    return np.array([cx, cy, a1, a2, ang], float)

def smooth(track, k=5):
    t = np.array([x if x is not None else [np.nan] * 5 for x in track], float)
    for j in range(5):
        s = t[:, j]; idx = np.arange(len(s)); ok = ~np.isnan(s)
        s[~ok] = np.interp(idx[~ok], idx[ok], s[ok]); t[:, j] = s
    ker = np.ones(k) / k
    return np.stack([np.convolve(np.pad(t[:, j], (k // 2, k // 2), mode="edge"), ker, "valid") for j in range(5)], 1)

def load_art(path, size=1024):
    a = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if a.shape[2] == 4:   # flatten transparency onto black (a projector projects no light there)
        al = a[:, :, 3:4] / 255.0; a = (a[:, :, :3] * al).astype(np.uint8)
    h, w = a.shape[:2]; s = max(h, w); pad = np.zeros((s, s, 3), np.uint8); pad[(s - h) // 2:(s - h) // 2 + h, (s - w) // 2:(s - w) // 2 + w] = a
    return cv2.resize(pad, (size, size), interpolation=cv2.INTER_AREA)

def composite(frame, ell, art, strength=1.0):
    H, W = frame.shape[:2]; cx, cy, a1, a2, ang = ell
    while ang > 45: ang -= 90; a1, a2 = a2, a1      # keep the art upright (projector gobo is fixed to the door)
    while ang <= -45: ang += 90; a1, a2 = a2, a1
    S = art.shape[0]
    M = cv2.getRotationMatrix2D((S / 2, S / 2), 0, 1)
    sx, sy = a1 / S, a2 / S
    th = np.deg2rad(ang); c, s = np.cos(th), np.sin(th)
    A = np.array([[c * sx, -s * sy], [s * sx, c * sy]])
    T = np.hstack([A, (np.array([cx, cy]) - A @ np.array([S / 2, S / 2]))[:, None]])
    warped = cv2.warpAffine(art, T, (W, H), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0)).astype(np.float32) / 255
    disc = np.zeros((H, W), np.float32); cv2.ellipse(disc, ((cx, cy), (a1 * 0.985, a2 * 0.985), ang), 1.0, -1)
    disc = cv2.GaussianBlur(disc, (0, 0), max(2, a1 * 0.012))
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    rx, ry = (xx - cx), (yy - cy)
    u = (rx * c + ry * s) / (a1 / 2 + 1e-6); v = (-rx * s + ry * c) / (a2 / 2 + 1e-6)
    falloff = np.clip(1 - 0.35 * (u * u + v * v), 0.45, 1)   # brighter centre, like the real disc
    f = frame.astype(np.float32) / 255
    def bigblur(x, sig):   # large-sigma blur on a downscaled copy (speed)
        k = max(1, int(sig / 6)); sm = cv2.resize(x, (max(8, W // k), max(8, H // k)), interpolation=cv2.INTER_AREA)
        sm = cv2.GaussianBlur(sm, (0, 0), max(0.8, sig / k)); return cv2.resize(sm, (W, H), interpolation=cv2.INTER_LINEAR)
    blur = bigblur(f, a1 * 0.08)
    ring = (disc < 0.05)
    nstd = float(np.std((f - blur)[ring])) if ring.any() else 0.01   # plate's own sensor noise/surface grain
    rng = np.random.default_rng(int(cx * 7 + cy))
    albedo = 1 + rng.normal(0, min(nstd * 4, 0.06), (H, W, 1)).astype(np.float32)   # NOT the plate's photo (it would bleed through)
    ambient = bigblur(f * (1 - disc[..., None]), a1 * 0.6) / (bigblur(1 - disc, a1 * 0.6)[..., None] + 1e-3)
    inside = f[disc > 0.9]
    cast = inside.mean(0) / (inside.mean() + 1e-6) if len(inside) else np.ones(3)
    gray = warped.mean(2, keepdims=True); warped = gray + 0.82 * (warped - gray) + 0.04   # projected light is a bit washed out
    light = cv2.GaussianBlur(warped, (0, 0), 1.6) * cast * falloff[..., None] * 1.15 * strength   # projector defocus
    new = np.clip((ambient + light) * albedo, 0, 1)
    out = f * (1 - disc[..., None]) + new * disc[..., None]
    return (out * 255).astype(np.uint8)

def crop916(frame, cx, out_w=720, out_h=1280):
    H, W = frame.shape[:2]; cw = int(H * 9 / 16); x0 = int(np.clip(cx - cw / 2, 0, W - cw))
    return cv2.resize(frame[:, x0:x0 + cw], (out_w, out_h), interpolation=cv2.INTER_AREA)

def crop_track(cx, W, H, fps=30, win_s=0.5, max_px_s=None):
    """D90: per-frame 9:16 crop x0 that FOLLOWS the disc (the fixed median crop let the disc drift to the right edge
    in the last second). Centred moving average over win_s (linear-extrapolated pad so the tail does not lag/flatten),
    speed-limited so the reframe reads as a handheld follow, clamped to the plate."""
    cw = int(H * 9 / 16); cx = np.asarray(cx, float); n = len(cx)
    k = max(1, int(round(win_s * fps)) | 1); h = k // 2
    if n > 1:
        i = np.arange(n); lo = np.polyfit(i[:min(n, k)], cx[:min(n, k)], 1); hi = np.polyfit(i[-min(n, k):], cx[-min(n, k):], 1)
        pad = np.concatenate([np.polyval(lo, np.arange(-h, 0)), cx, np.polyval(hi, np.arange(n, n + h))])
        c = np.convolve(pad, np.ones(k) / k, "valid")
    else: c = cx.copy()
    vmax = (max_px_s or W * 0.6) / fps
    for j in range(1, n): c[j] = c[j - 1] + np.clip(c[j] - c[j - 1], -vmax, vmax)
    return np.clip(np.round(c - cw / 2), 0, W - cw).astype(int)

def run(plate=PLATE, art_path=ART, secs=None, out=OUT):
    os.makedirs(out, exist_ok=True)
    cap = cv2.VideoCapture(plate); fps = cap.get(cv2.CAP_PROP_FPS) or 30
    frames = []
    while True:
        ok, fr = cap.read()
        if not ok or (secs and len(frames) >= secs * fps): break
        frames.append(fr)
    raw = [detect_disc(f) for f in frames]; tr = smooth(raw); art = load_art(art_path)
    H0, W0 = frames[0].shape[:2]; xs = crop_track(tr[:, 0], W0, H0, fps)
    tmp = tempfile.mktemp(suffix=".mp4")
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", "720x1280", "-r", f"{fps:.3f}", "-i", "-",
                          "-i", plate, "-map", "0:v", "-map", "1:a?", "-shortest", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    still = None
    for i, (f, e) in enumerate(zip(frames, tr)):
        H, W = f.shape[:2]; cw = int(H * 9 / 16); x0 = int(xs[i])
        e2 = e.copy(); e2[0] -= x0
        o = cv2.resize(composite(np.ascontiguousarray(f[:, x0:x0 + cw]), e2, art), (720, 1280), interpolation=cv2.INTER_AREA)
        if i == len(frames) // 2: still = o
        p.stdin.write(o.tobytes())
    p.stdin.close(); p.wait()
    from hookforge import autoedit, deliver
    clip = os.path.join(out, "trump_projector_sample_720p.mp4"); autoedit.clean_export(tmp, clip); os.remove(tmp)
    raw_png = os.path.join(out, "_still_raw.png"); cv2.imwrite(raw_png, still)
    still_p = os.path.join(out, "trump_projector_sample_still.jpg"); deliver.sanitize(raw_png, still_p); os.remove(raw_png)
    probs = deliver.scan(clip) + deliver.scan(still_p)
    return dict(clip=clip, still=still_p, frames=len(frames), fps=round(fps, 2), detected=int(sum(r is not None for r in raw)), metadata_problems=probs)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--art", default=ART); ap.add_argument("--plate", default=PLATE); ap.add_argument("--secs", type=float)
    a = ap.parse_args(); print(run(a.plate, a.art, a.secs))
