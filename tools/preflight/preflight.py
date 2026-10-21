"""Pre-post preflight for a finished (or candidate) video. Read-only; writes a report + a contact sheet.

Checks (each tied to a documented platform rule or Omar rule):
 1. contact sheet: frames every 0.5 s with timestamps -> PNG for a vision QA pass (hands, product, absurd failures, D33)
 2. text safe zones: RapidOCR (PaddleOCR models on ONNX) boxes vs Meta Reels safe zone (top 14 %, bottom 35 %, sides 6 %;
    Meta Reels ads guide). Organic UI covers less, so flags are WARN not BLOCK; Hookforge winners sit at ~19 % (D30).
 3. provenance metadata: C2PA / IPTC DigitalSourceType markers (Meta reads these for the "AI info" label). Report only.
 4. loudness: ffmpeg ebur128 integrated LUFS + true peak vs D7 (-14 LUFS, TP <= -1 dBTP).
Usage: python3 preflight.py VIDEO.mp4 [--out DIR] [--no-ocr]
"""
import sys, os, re, json, subprocess, numpy as np
from PIL import Image, ImageDraw
from _frames import frames, probe

SAFE = dict(top=0.14, bottom=0.35, side=0.06)

def contact_sheet(path, out_png, every=0.5, cols=6, width=180):
    fr, dur = frames(path, 1 / every, width)
    if not fr: return 0
    h = fr[0][1].shape[0]; rows = (len(fr) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * width, rows * (h + 16)), "white"); d = ImageDraw.Draw(sheet)
    for i, (t, img) in enumerate(fr):
        x, y = (i % cols) * width, (i // cols) * (h + 16)
        sheet.paste(Image.fromarray(img), (x, y + 16)); d.text((x + 3, y + 2), f"{t:.1f}s", fill="black")
    sheet.save(out_png); return len(fr)

def ocr_zones(path):
    from rapidocr_onnxruntime import RapidOCR
    eng = RapidOCR(); fr, _ = frames(path, 1.0, 540); flags, texts = [], []
    for t, img in fr:
        res, _ = eng(img)
        H, W = img.shape[:2]
        for box, txt, conf in (res or []):
            if float(conf) < 0.6: continue
            ys = [p[1] / H for p in box]; xs = [p[0] / W for p in box]
            texts.append(dict(t=t, text=txt, y_top=round(min(ys), 3), y_bot=round(max(ys), 3)))
            z = [k for k, bad in (("top", min(ys) < SAFE["top"]), ("bottom", max(ys) > 1 - SAFE["bottom"]),
                                  ("side", min(xs) < SAFE["side"] or max(xs) > 1 - SAFE["side"])) if bad]
            if z: flags.append(dict(t=t, text=txt, zones=z))
    return texts, flags

C2PA_UUID = bytes.fromhex("d8fec3d61b0e483c92975828877ec481")   # ISO BMFF 'uuid' box type used by C2PA manifests in MP4

def provenance(path):
    """Structural C2PA check (a bare b'c2pa' byte match false-positives on compressed video data: 2026-10-18 fixture
    ref_tiktok_7693569018929630478.mp4 had one random 'c2pa' and no manifest). C2PA = C2PA uuid box OR a JUMBF box
    labelled c2pa; AI-provenance = IPTC DigitalSourceType / trainedAlgorithmicMedia in XMP."""
    with open(path, "rb") as f: b = f.read()
    jumbf = b"jumb" in b and (b"c2pa" in b) and (b"jumd" in b)
    return dict(c2pa=(C2PA_UUID in b) or jumbf or b"c2pa.claim" in b or b"c2pa.signature" in b,
                iptc_digital_source_type=b"igitalSourceType" in b,
                trained_algorithmic_media=b"trainedAlgorithmicMedia" in b)

def loudness(path):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    I = re.findall(r"I:\s+(-?[\d.]+) LUFS", err); P = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", err)
    return dict(lufs=float(I[-1]) if I else None, true_peak=float(P[-1]) if P else None)

def run(path, out=None, ocr=True):
    out = out or os.path.join(os.path.dirname(os.path.abspath(path)), "preflight")
    os.makedirs(out, exist_ok=True); stem = os.path.splitext(os.path.basename(path))[0]
    w, h, dur = probe(path)
    rep = dict(file=path, width=w, height=h, duration=round(dur, 2), aspect_ok=abs(h / w - 16 / 9) < 0.02)
    rep["contact_sheet"] = os.path.join(out, f"{stem}_sheet.png"); rep["n_frames_sheet"] = contact_sheet(path, rep["contact_sheet"])
    rep["provenance"] = provenance(path); rep["loudness"] = loudness(path)
    L = rep["loudness"]; rep["loudness_ok"] = L["lufs"] is not None and abs(L["lufs"] + 14) <= 2 and (L["true_peak"] or 0) <= -1
    if ocr:
        texts, flags = ocr_zones(path); rep["ocr_text"] = texts; rep["safe_zone_warnings"] = flags
    json.dump(rep, open(os.path.join(out, f"{stem}_preflight.json"), "w"), indent=1)
    return rep

if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    o = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
    if o in a: a.remove(o)
    r = run(a[0], o, "--no-ocr" not in sys.argv)
    print(json.dumps({k: v for k, v in r.items() if k != "ocr_text"}, indent=1)[:3000])
