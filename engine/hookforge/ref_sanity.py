"""D100 ref-sanity: a reference image must actually CONTAIN its subject (CLIP ViT-B-32 laion2b, local cache, no network).
Zero-shot: P(subject label) vs distractor labels (grass, floor, wall, sky, blank, random person/room/text); the subject
must win with p >= P_MIN and its cosine must be >= COS_MIN. Manifests: refs/<slug>/manifest.json; label per ref from
LABELS (by file-name keyword) or the ref's 'subject' field.
  ref_sanity.check(path, label) -> dict(ok, p, cos, top)
  ref_sanity.audit() -> rows for every ref of all slugs (use_for_generation refs only fail the audit)"""
import os, json, glob, functools
import numpy as np
from .config import REPO

P_MIN, COS_MIN = 0.35, 0.15
DISTRACT = ["a photo of grass", "a photo of a floor", "a photo of a plain wall", "a photo of the sky", "a blank image",
            "a photo of a room interior", "a photo of text", "a photo of a person", "a photo of a tree", "an empty photo with nothing in it"]
BLUR_WARN = 60.0   # D104: blur is a QUALITY warning (variance of Laplacian on a 512px copy), not a subject-presence fail

@functools.lru_cache(1)
def _model():
    import torch, open_clip; torch.set_num_threads(2)
    m, _, pre = open_clip.create_model_and_transforms("ViT-B-32", pretrained="laion2b_s34b_b79k")
    return m.eval(), pre, open_clip.get_tokenizer("ViT-B-32")

def _txt(labels):
    import torch
    m, _, tok = _model()
    with torch.no_grad(): t = m.encode_text(tok(labels)).float()
    return (t / t.norm(dim=-1, keepdim=True)).numpy()

def _img(path):
    import torch; from PIL import Image
    m, pre, _ = _model()
    with torch.no_grad(): e = m.encode_image(pre(Image.open(path).convert("RGB")).unsqueeze(0)).float()
    return (e / e.norm(dim=-1, keepdim=True)).numpy()[0]

def check(path, label):
    labels = [f"a photo of {label}"] + [d for d in DISTRACT if label.split()[-1] not in d]
    if "person" in label or "woman" in label or "man " in label + " " or "hands" in label: labels = labels[:1] + [l for l in labels[1:] if "person" not in l]
    e = _img(path); t = _txt(labels); sims = t @ e
    p = np.exp(100 * sims - (100 * sims).max()); p = p / p.sum()
    ok = bool(p[0] >= P_MIN and sims[0] >= COS_MIN and int(np.argmax(p)) == 0)
    import cv2
    g = cv2.imread(path, cv2.IMREAD_GRAYSCALE); g = cv2.resize(g, (512, int(512 * g.shape[0] / g.shape[1])))
    sharp = float(cv2.Laplacian(g, cv2.CV_64F).var())
    return dict(ok=ok, p=round(float(p[0]), 3), cos=round(float(sims[0]), 3), top=labels[int(np.argmax(p))], sharpness=round(sharp, 1),
                warn=("blurry (sharpness %.0f < %.0f): usable for identity only, prefer a sharper source" % (sharp, BLUR_WARN)) if sharp < BLUR_WARN else None)

LABELS = [  # (filename keyword, label) - first match wins
    ("man_hands", "a man's hands"), ("box", "a product box"), ("projector", "a light projector"), ("bengal", "a cream bengal cat"), ("greycat", "a grey cat in a ball"), ("ball", "a pet playpen ball"), ("disc", "a folded pet playpen"),
    ("cast_woman", "a woman"), ("cast_man", "a man"), ("woman", "a woman"), ("man_hands", "a man's hands"), ("hands", "hands"),
    ("robe", "a green grinch robe"), ("grinch", "a green grinch"), ("mug", "a mug"), ("melt", "a mug"), ("mask", "a knitted ski mask"),
    ("minion", "a yellow minion mask"), ("brick", "a knitted ski mask"), ("fire", "a tabletop fire pit"), ("firepit", "a tabletop fire pit"),
    ("curtain", "christmas lights"), ("lights", "christmas lights"), ("glow", "lights"), ("projector", "a light projector"), ("trump", "donald trump"),
    ("tree", "a christmas tree with lights"), ("pajama", "pajamas"), ("jammies", "pajamas"), ("carrier", "a pet carrier")]
SLUG_DEFAULT = {"purrventure": "a cat in a pet playpen", "trumpglow": "a light projector", "patriotglow": "a light projector", "grinch_robe": "a green grinch robe",
                "merryglow": "christmas tree lights", "merryfire": "a tabletop fire pit", "jollyglow": "christmas curtain lights", "brickhood": "a knitted ski mask",
                "grinchmelt": "a mug", "minionmask": "a yellow minion mask", "cozyjams": "pajamas", "heatjams": "a robe"}

def label_for(ref, slug):
    if ref.get("subject"): return ref["subject"]
    n = os.path.basename(ref["path"]).lower()
    if ref.get("kind", "").startswith("cast"):
        for k, l in LABELS[:12]:
            if k in n: return l
        return "a person"
    for k, l in LABELS:
        if k in n: return l
    return SLUG_DEFAULT.get(slug, slug.replace("_", " "))

def audit(slugs=None, used_only=True):
    rows = []
    for mf in sorted(glob.glob(os.path.join(REPO, "refs", "*", "manifest.json"))):
        slug = os.path.basename(os.path.dirname(mf))
        if slugs and slug not in slugs: continue
        for r in json.load(open(mf)).get("refs", []):
            p = os.path.join(REPO, r["path"])
            if used_only and not r.get("use_for_generation", True): continue
            if not os.path.exists(p) or os.path.splitext(p)[1].lower() not in (".png", ".jpg", ".jpeg", ".webp"): continue
            if r.get("kind") == "cast_scene": rows.append(dict(slug=slug, path=r["path"], kind="cast_scene", ok=None, note="scene/setting ref - no single subject to check")); continue
            lab = label_for(r, slug); c = check(p, lab)
            rows.append(dict(slug=slug, path=r["path"], kind=r.get("kind"), label=lab, used=r.get("use_for_generation", True), **c))
    return rows
