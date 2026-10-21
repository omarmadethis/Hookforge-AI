"""Product-fidelity score: is OUR product (from its reference photos) visible and on-model in each shot?

CLIP image embeddings (open_clip ViT-B-32 laion2b, already cached on the box) of product reference images vs video frames.
Per frame: max cosine to any reference image. Per video: score per 0.5 s, plus 'product_present_0s' (first frame).
Use: QA gate input for D33 absurd failures (product missing / wrong product / wrong colour). Calibrate thresholds on own
reels (see GAP_AUDIT.md validation) before using as a BLOCK; until then it only ranks shots for the vision pass.
Usage: python3 product_fidelity.py VIDEO.mp4 /path/to/product_images_dir [--json]
"""
import sys, os, glob, json, numpy as np, torch, open_clip
from PIL import Image
from _frames import frames

_M = None
def model():
    global _M
    if _M is None:
        m, _, pre = open_clip.create_model_and_transforms("ViT-B-32", pretrained="laion2b_s34b_b79k"); m.eval(); _M = (m, pre)
    return _M

@torch.no_grad()
def embed(imgs):
    m, pre = model(); x = torch.stack([pre(i.convert("RGB")) for i in imgs])
    e = m.encode_image(x); return torch.nn.functional.normalize(e, dim=-1).numpy()

def score(video, img_dir, fps=2.0):
    refs = [Image.open(p) for p in sorted(glob.glob(os.path.join(img_dir, "*"))) if p.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]
    R = embed(refs); fr, _ = frames(video, fps, 360)
    F = embed([Image.fromarray(f) for _, f in fr]); s = (F @ R.T).max(1)
    return dict(video=video, refs=len(refs), per_frame=[(round(t, 1), round(float(v), 3)) for (t, _), v in zip(fr, s)],
                mean=round(float(s.mean()), 3), p90=round(float(np.quantile(s, .9)), 3), first=round(float(s[0]), 3))

if __name__ == "__main__":
    torch.set_num_threads(2)
    r = score(sys.argv[1], sys.argv[2])
    print(json.dumps(r) if "--json" in sys.argv else f"mean={r['mean']} p90={r['p90']} first={r['first']} refs={r['refs']}  {r['video']}")
