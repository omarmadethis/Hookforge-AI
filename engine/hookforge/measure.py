"""Measure everything Hookforge can measure on an mp4 (used by QA + backtest).

python -m hookforge.measure video.mp4 [--product "green robe"] [--json out.json]

All heavy work is low-res and single pass; run under `nice -n 19` on the shared box.
"""
import json, os, re, subprocess, sys, math
import numpy as np

def _run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)

def probe(path):
    r = _run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path])
    d = json.loads(r.stdout or "{}")
    v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), {})
    a = next((s for s in d.get("streams", []) if s.get("codec_type") == "audio"), None)
    fr = v.get("avg_frame_rate", "30/1").split("/")
    fps = float(fr[0]) / float(fr[1]) if len(fr) == 2 and float(fr[1]) else 30.0
    dur = float(d.get("format", {}).get("duration", 0) or 0)
    w, h = int(v.get("width", 0)), int(v.get("height", 0))
    rot = 0
    for sd in v.get("side_data_list", []) or []:
        if "rotation" in sd: rot = abs(int(sd["rotation"]))
    if rot in (90, 270): w, h = h, w
    return {"duration": dur, "width": w, "height": h, "fps": round(fps, 3), "has_audio": a is not None,
            "vcodec": v.get("codec_name")}

def frames_lowres(path, width=144, fps=None):
    """Return (frames uint8 [N,H,W,3], fps_used)."""
    p = probe(path)
    f = fps or min(30.0, p["fps"] or 30.0)
    hgt = int(round(width * (p["height"] or 16) / max(p["width"] or 9, 1) / 2) * 2)
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={f},scale={width}:{hgt}", "-f", "rawvideo",
           "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True).stdout
    n = len(raw) // (width * hgt * 3)
    arr = np.frombuffer(raw[: n * width * hgt * 3], np.uint8).reshape(n, hgt, width, 3)
    return arr, f

def detect_cuts(fr, fps, min_gap=0.35):
    """Hard-cut detector: HSV-histogram distance + pixel diff, adaptive threshold."""
    import cv2
    if len(fr) < 3: return []
    hs, px = [], []
    prev = None
    for im in fr:
        hsv = cv2.cvtColor(im, cv2.COLOR_RGB2HSV)
        hist = cv2.calcHist([hsv], [0, 1], None, [16, 8], [0, 180, 0, 256]); hist = cv2.normalize(hist, None).flatten()
        g = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY).astype(np.float32)
        if prev is not None:
            hs.append(cv2.compareHist(prev[0], hist, cv2.HISTCMP_BHATTACHARYYA))
            px.append(np.mean(np.abs(g - prev[1])) / 255.0)
        prev = (hist, g)
    hs, px = np.array(hs), np.array(px)
    score = hs * 0.6 + px * 2.0
    med = np.median(score); mad = np.median(np.abs(score - med)) + 1e-6
    cuts = []
    for i, s in enumerate(score):
        local = score[max(0, i - 8): i + 9]
        if s > max(med + 6 * mad, 0.22) and s >= local.max() and s > 2.2 * np.median(local):
            t = (i + 1) / fps
            if not cuts or t - cuts[-1] >= min_gap:
                cuts.append(round(t, 3))
    return cuts

def motion_stats(fr, fps):
    g = fr.mean(axis=3).astype(np.float32)
    d = np.abs(np.diff(g, axis=0)).mean(axis=(1, 2)) / 255.0 if len(g) > 1 else np.array([0.0])
    def seg(a, b):
        i0, i1 = int(a * fps), max(int(b * fps), int(a * fps) + 1)
        x = d[i0:i1]; return float(x.mean()) if len(x) else 0.0
    return {"motion_0_1": seg(0, 1), "motion_1_3": seg(1, 3)}

def image_stats(im):
    import cv2
    x = im.astype(np.float32)
    hsv = cv2.cvtColor(im, cv2.COLOR_RGB2HSV)
    r, g, b = x[..., 0], x[..., 1], x[..., 2]
    rg, yb = r - g, 0.5 * (r + g) - b
    colorful = float(np.sqrt(rg.std() ** 2 + yb.std() ** 2) + 0.3 * np.sqrt(rg.mean() ** 2 + yb.mean() ** 2))
    gray = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)
    return {"bright_0": float(gray.mean()), "contrast_0": float(gray.std()), "sat_0": float(hsv[..., 1].mean()),
            "colorful_0": colorful, "warmth_0": float((r - b).mean())}

def audio_stats(path, has_audio):
    out = {"audio_start_s": None, "lufs": None, "true_peak": None, "end_drop_db": None}
    if not has_audio: return out
    r = _run(["ffmpeg", "-v", "info", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"])
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr); p = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r.stderr)
    if m: out["lufs"] = float(m[-1])
    if p: out["true_peak"] = float(p[-1])
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", "8000", "-f", "s16le", "-"],
                         capture_output=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0
    if len(a) > 800:
        win = 400  # 50 ms
        n = len(a) // win
        rms = np.sqrt((a[: n * win].reshape(n, win) ** 2).mean(axis=1) + 1e-12)
        db = 20 * np.log10(rms + 1e-9)
        above = np.where(db > -45)[0]
        out["audio_start_s"] = round(float(above[0] * 0.05), 3) if len(above) else None
        med = float(np.median(db[db > -60])) if (db > -60).any() else -60
        out["end_drop_db"] = round(float(med - db[-6:].mean()), 2)   # >6 dB => faded ending
    return out

def ocr_text(path, t, width=720):
    """OCR white text in top 55% of frame at time t. Returns dict with words, centre y, height (fractions)."""
    import cv2, pytesseract
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", path, "-frames:v", "1", "-vf",
                        f"scale={width}:-2", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
    if not r: return None
    im = cv2.imdecode(np.frombuffer(r, np.uint8), cv2.IMREAD_COLOR)
    H, W = im.shape[:2]
    top = im[: int(H * 0.55)]
    hsv = cv2.cvtColor(top, cv2.COLOR_BGR2HSV)
    mask = ((hsv[..., 2] > 215) & (hsv[..., 1] < 45)).astype(np.uint8) * 255
    inv = 255 - mask
    d = pytesseract.image_to_data(inv, config="--psm 11", output_type=pytesseract.Output.DICT)
    words = []
    for i, w in enumerate(d["text"]):
        w = w.strip()
        try: c = float(d["conf"][i])
        except Exception: c = -1
        if len(re.sub(r"[^A-Za-z]", "", w)) >= 2 and c >= 55:
            words.append((w, d["top"][i], d["height"][i], d["left"][i], d["width"][i]))
    if not words: return {"t": t, "n_words": 0, "text": ""}
    # keep the dominant line cluster (largest vertical group)
    ys = np.array([wd[1] + wd[2] / 2 for wd in words]); hs = np.array([wd[2] for wd in words])
    cy = float(np.median(ys))
    keep = [wd for wd, y in zip(words, ys) if abs(y - cy) < 4 * np.median(hs)]
    ys2 = [wd[1] + wd[2] / 2 for wd in keep]
    return {"t": t, "n_words": len(keep), "text": " ".join(w[0] for w in keep),
            "center_y_frac": round(float(np.mean(ys2)) / H, 4),
            "height_frac": round(float(np.median([w[2] for w in keep])) / H, 4),
            "n_lines": int(len(set(int(y // (1.6 * np.median(hs))) for y in ys2)))}

_CLIP = None
def product_share(path, prompt, t=0.0):
    """Fraction of a 4x6 tile grid on frame t that CLIP rates as the product (vs generic scene)."""
    global _CLIP
    try:
        import torch, open_clip
        from PIL import Image
        import io
    except Exception:
        return None
    if _CLIP is None:
        torch.set_num_threads(2)
        m, _, pre = open_clip.create_model_and_transforms("ViT-B-32", pretrained="openai"); m.eval()
        _CLIP = (m, pre, open_clip.get_tokenizer("ViT-B-32"))
    m, pre, tok = _CLIP
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", path, "-frames:v", "1", "-vf", "scale=480:-2",
                        "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
    if not r: return None
    im = Image.open(io.BytesIO(r)).convert("RGB"); W, H = im.size
    neg = ["a photo of a room", "a photo of a person's face", "a photo of a store shelf", "a photo of a wall",
           "a photo of the floor", "a photo of a sofa", "text on a screen"]
    texts = [f"a photo of {prompt}"] + neg
    with torch.no_grad():
        te = m.encode_text(tok(texts)); te = te / te.norm(dim=-1, keepdim=True)
        tiles = []
        for gy in range(6):
            for gx in range(4):
                box = (int(gx * W / 4), int(gy * H / 6), int((gx + 1) * W / 4), int((gy + 1) * H / 6))
                tiles.append(pre(im.crop(box)))
        ie = m.encode_image(torch.stack(tiles)); ie = ie / ie.norm(dim=-1, keepdim=True)
        p = (100 * ie @ te.T).softmax(dim=-1)[:, 0].numpy()
        whole = pre(im).unsqueeze(0); we = m.encode_image(whole); we = we / we.norm(dim=-1, keepdim=True)
        pw = float((100 * we @ te.T).softmax(dim=-1)[0, 0])
    return {"product_share_0": round(float((p > 0.5).mean()), 3), "product_prob_0": round(pw, 3)}

def measure(path, product_prompt=None, ocr_every=1.0, do_clip=True):
    p = probe(path)
    fr, fps = frames_lowres(path)
    cuts = detect_cuts(fr, fps)
    dur = p["duration"] or (len(fr) / fps)
    bounds = [0.0] + [c for c in cuts if 0.2 < c < dur - 0.2] + [dur]
    shots = np.diff(bounds)
    out = dict(p)
    out.update({"cuts": cuts, "n_shots": int(len(shots)), "first_cut": cuts[0] if cuts else dur,
                "cut_fracs": [round(c / dur, 3) for c in cuts] if dur else [],
                "last_shot_start_frac": round(bounds[-2] / dur, 3) if dur and len(bounds) > 2 else 0.0,
                "last_shot_s": round(float(shots[-1]), 3) if len(shots) else dur,
                "max_shot_s": round(float(shots.max()), 3) if len(shots) else dur,
                "avg_shot_s": round(float(shots.mean()), 3) if len(shots) else dur})
    out.update(motion_stats(fr, fps))
    if len(fr): out.update(image_stats(fr[0]))
    out.update(audio_stats(path, p["has_audio"]))
    t0 = ocr_text(path, 0.05) or {}
    out["text0"] = t0
    events, last = [], t0.get("text", "")
    t = ocr_every
    while ocr_every and t < dur - 0.2:
        o = ocr_text(path, t) or {}
        if o.get("n_words", 0) and last and _sim(o.get("text", ""), last) < 0.35:
            events.append(round(t, 2))
        if o.get("n_words", 0): last = o.get("text", "")
        t += ocr_every
    out["text_change_times"] = events
    if do_clip and product_prompt:
        ps = product_share(path, product_prompt)
        if ps: out.update(ps)
    return out

def _sim(a, b):
    a, b = set(a.lower().split()), set(b.lower().split())
    return len(a & b) / max(1, len(a | b))

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("video"); ap.add_argument("--product"); ap.add_argument("--json")
    a = ap.parse_args()
    res = measure(a.video, a.product)
    s = json.dumps(res, indent=1, default=float)
    if a.json: open(a.json, "w").write(s)
    print(s)
