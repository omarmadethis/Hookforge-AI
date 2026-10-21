"""D75 AI-look QA reviewer. Samples frames per shot and scores AI artifacts 0..1:
  warped_hands, text_gibberish, melting_product, plastic_skin, physics_error.
Signals: CLIP zero-shot (artifact vs normal prompt pairs, open_clip ViT-B-32 cached), OCR word-validity (tesseract),
temporal structure break without a cut (melting/morphing/teleport), skin-texture high-frequency energy (plastic skin).
Severity: score >= ABSURD (0.9) on a shot = 'absurd' -> reroll candidate (D33: reroll ONLY absurd); >= WARN_AT = warn; real footage skipped."""
import os, re, subprocess, tempfile, numpy as np
ABSURD, WARN_AT = 0.9, 0.6
PAIRS = {
  "warped_hands":   ("a photo of a deformed hand with extra or fused fingers", "a photo of a normal human hand"),
  "melting_product":("a melted, warped, distorted object", "a normal solid everyday product"),
  "plastic_skin":   ("a waxy plastic CGI face with airbrushed skin", "a real person photographed with a phone, natural skin texture"),
  "physics_error":  ("an impossible physics glitch, floating objects, bodies merging", "an ordinary everyday scene"),
}
_WORDS = None

def frames(path, n=6, size=448):
    d = tempfile.mkdtemp(); dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                                                      capture_output=True, text=True).stdout.strip() or 0)
    from PIL import Image; out = []
    for i in range(n):
        t = dur * (i + 0.5) / n; f = os.path.join(d, f"{i}.png")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", path, "-frames:v", "1", "-vf", f"scale={size}:-2", f], check=False)
        if os.path.exists(f): out.append((t, Image.open(f).convert("RGB")))
    return out

def _clip_scores(imgs):
    try:
        import torch, open_clip, sys
        from .config import REPO
        sys.path.insert(0, os.path.join(REPO, "tools", "preflight")); import product_fidelity as PF
        m, pre = PF.model(); tok = open_clip.get_tokenizer("ViT-B-32")
        with torch.no_grad():
            I = m.encode_image(torch.stack([pre(i) for i in imgs])); I = I / I.norm(dim=-1, keepdim=True)
            res = {}
            for k, (bad, good) in PAIRS.items():
                T = m.encode_text(tok([bad, good])); T = T / T.norm(dim=-1, keepdim=True)
                p = (50 * I @ T.T).softmax(-1)[:, 0].numpy()   # P(bad) per frame
                res[k] = p
        return res
    except Exception as e:
        return {"_error": str(e)}

def _words():
    global _WORDS
    if _WORDS is None:
        _WORDS = set()
        for p in ("/usr/share/dict/words", "/usr/share/dict/american-english"):
            if os.path.exists(p): _WORDS |= {w.strip().lower() for w in open(p, errors="ignore")}
    return _WORDS

def text_gibberish(img):
    """Fraction of OCR'd 4+ letter tokens that are not words (needs >=3 tokens to count)."""
    f = tempfile.mktemp(suffix=".png"); img.save(f)
    txt = subprocess.run(["tesseract", f, "-", "--psm", "11"], capture_output=True, text=True).stdout
    toks = [t.lower() for t in re.findall(r"[A-Za-z]{4,}", txt)]; W = _words()
    if len(toks) < 3 or not W: return 0.0, toks
    bad = [t for t in toks if t not in W]; return round(len(bad) / len(toks), 2), toks

CLIP_CAP = 0.85   # uncalibrated zero-shot alone can WARN but never certify 'absurd' (D33 certainty); needs a measured signal too

def temporal_break(imgs, times=None, cuts=()):
    """Max structural jump between consecutive samples (grayscale 64px correlation); high = morph/melt/teleport if no cut."""
    a = [np.asarray(i.convert("L").resize((64, 112)), np.float32).ravel() for i in imgs]; jumps = []
    times = times or list(range(len(a)))
    for i, (x, y) in enumerate(zip(a, a[1:])):
        if any(times[i] <= c <= times[i + 1] for c in cuts): continue      # a hard cut between samples is not a morph
        x, y = x - x.mean(), y - y.mean(); c = float((x @ y) / (np.linalg.norm(x) * np.linalg.norm(y) + 1e-6)); jumps.append(1 - c)
    return max(jumps) if jumps else 0.0

def skin_texture(img):
    """High-frequency energy in skin-tone pixels; very low = plastic. Returns plastic score 0..1 (None if little skin)."""
    import cv2
    a = np.asarray(img); ycc = cv2.cvtColor(a, cv2.COLOR_RGB2YCrCb)
    m = cv2.inRange(ycc, (0, 135, 85), (255, 175, 135)) > 0
    if m.mean() < 0.04: return None
    lap = np.abs(cv2.Laplacian(cv2.cvtColor(a, cv2.COLOR_RGB2GRAY).astype(np.float32), cv2.CV_32F))
    e = float(lap[m].mean()); return float(np.clip((4.0 - e) / 3.0, 0, 1))   # e<=1 -> 1.0 plastic, e>=4 -> 0

def review_shot(path, shot_id="?", source="ai", n=6, cut_inside=False):
    if source != "ai": return dict(shot=shot_id, skipped="real footage (D75)", scores={}, severity="ok")
    fr = frames(path, n); imgs = [i for _, i in fr]
    if not imgs: return dict(shot=shot_id, error="no frames", scores={}, severity="warn")
    cs = _clip_scores(imgs); sc = {}
    for k in PAIRS:
        if k in cs: sc[k] = round(float(np.sort(cs[k])[-2] if len(cs[k]) > 1 else cs[k][0]), 2)   # 2nd-worst frame: robust to 1 noisy frame
    g = [text_gibberish(i)[0] for i in imgs]; sc["text_gibberish"] = round(sorted(g)[-2] if len(g) > 1 else g[0], 2)
    for k in PAIRS:
        if k in sc: sc[k] = min(sc[k], CLIP_CAP)
    try:
        from .qa import detect_cuts; cuts = [float(c) for c in detect_cuts(path, 0.2)]
    except Exception: cuts = []
    tb = temporal_break(imgs, [t for t, _ in fr], cuts)
    if not cut_inside: sc["melting_product"] = round(max(sc.get("melting_product", 0), float(np.clip((tb - 0.35) / 0.4, 0, 1))), 2)
    sk = [s for s in (skin_texture(i) for i in imgs) if s is not None]
    if sk: sc["plastic_skin"] = round(max(sc.get("plastic_skin", 0) * 0.6, float(np.median(sk)) * 0.6 + sc.get("plastic_skin", 0) * 0.4), 2)
    worst = max(sc.items(), key=lambda kv: kv[1]) if sc else ("none", 0)
    sev = "absurd" if worst[1] >= ABSURD else "warn" if worst[1] >= WARN_AT else "ok"
    return dict(shot=shot_id, scores=sc, worst=worst[0], worst_score=worst[1], severity=sev, reroll=sev == "absurd",
                temporal_break=round(tb, 2), clip_error=cs.get("_error"), frames=[round(t, 2) for t, _ in fr])

def review(shots):
    """shots: [{id, path, source}] -> per-shot results + problems lines for qa.final_checks."""
    res = [review_shot(s["path"], s.get("id", "?"), s.get("source", "ai"), cut_inside=s.get("cut_inside", False)) for s in shots]
    probs = []
    for r in res:
        if r["severity"] == "absurd": probs.append(f"BLOCK AI-look {r['shot']}: {r['worst']} {r['worst_score']} >= {ABSURD} - absurd, reroll this shot only (D75/D33)")
        elif r["severity"] == "warn": probs.append(f"WARN AI-look {r['shot']}: {r['worst']} {r['worst_score']} (no reroll; note for next prompt)")
    return dict(results=res, problems=probs)
