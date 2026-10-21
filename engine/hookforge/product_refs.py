"""D75 product-reference module: photoreal product reference shots via GPT Image 2.0 (1 credit/image) FROM the product's own
store photos (assets/<brand>/product|box|other). Output feeds start frames (refs=[...]) and Seedance reference_image_paths.
Spend happens only through the order runner with Omar's approved cap; this module builds the plan + registers results."""
import os, glob, json
from .config import REPO
ASSETS = os.path.join(REPO, "assets"); OUT = os.path.join(REPO, "assets", "_product_refs")
IMG = (".jpg", ".jpeg", ".png", ".webp")
ANGLES = {
  "hero":    "the product alone on a plain real-world surface (kitchen counter / porch railing), three-quarter angle",
  "in_hand": "the product held in one normal adult hand, natural five fingers, product filling 40% of frame",
  "lit":     "the product switched on/in use in a dim real home at night, light spilling naturally onto nearby surfaces",
  "packaged":"the product in its real retail box on a store shelf, label text kept exactly as in the reference photo",
}
REAL_LOOK = ("shot on iPhone 15 Pro main camera, natural available light, slight sensor noise, real textures and dust, "
             "imperfect framing, no studio lighting, no CGI gloss, no extra text or logos beyond those in the reference photo; "
             "the product shape, colours, proportions, parts and print must match the reference photo exactly")

def store_photos(brand, limit=4, product_key=None):
    """Store photos first; for products with curated supplier footage, add its 9:16 reference stills (D75)."""
    fs = []
    for sub in ("product", "box", "other", ""):
        fs += sorted(f for f in glob.glob(os.path.join(ASSETS, brand, sub, "*")) if f.lower().endswith(IMG))
    seen, out = set(), []
    for f in fs:
        if f not in seen: seen.add(f); out.append(f)
    if product_key:
        from . import real_footage as RF
        d = os.path.join(RF.ROOT, RF.folder(product_key), "_ref_stills")
        if not os.path.isdir(d) and RF.manifest(product_key):
            try: RF.ref_stills(product_key)
            except Exception: pass
        out += sorted(glob.glob(os.path.join(d, "*.png")))
    return out[:limit] if not product_key else out[:limit + 4]

def ref_prompt(product_desc, angle):
    return f"Photoreal photo of {product_desc}: {ANGLES[angle]}. {REAL_LOOK}."

def plan_refs(brand, product_desc, angles=("hero", "in_hand", "lit"), variants=1, product_key=None):
    """Return GPT Image 2.0 calls (model gpt_image_2, 1 credit each, 9:16) that use the store photos as image refs."""
    photos = store_photos(brand, product_key=product_key)
    if not photos: raise FileNotFoundError(f"no store photos under assets/{brand}/(product|box|other)")
    calls = [dict(id=f"PR_{brand}_{a}_{v}", model="gpt_image_2", aspect_ratio="9:16", prompt=ref_prompt(product_desc, a),
                  image_refs=photos, credits=1.0, angle=a) for a in angles for v in range(variants)]
    return dict(brand=brand, calls=calls, credits=sum(c["credits"] for c in calls), out_dir=os.path.join(OUT, brand))

def register(brand, angle, path, job_id=None):
    d = os.path.join(OUT, brand); os.makedirs(d, exist_ok=True)
    idx = os.path.join(d, "index.json"); data = json.load(open(idx)) if os.path.exists(idx) else []
    data.append(dict(angle=angle, path=path, job_id=job_id)); json.dump(data, open(idx, "w"), indent=1); return data

def refs_for(brand, angles=None):
    """Reference paths for start frames / Seedance: generated refs first (if any), else raw store photos."""
    idx = os.path.join(OUT, brand, "index.json")
    gen = [r["path"] for r in (json.load(open(idx)) if os.path.exists(idx) else []) if os.path.exists(r["path"]) and (not angles or r["angle"] in angles)]
    return gen + store_photos(brand, 2)

def attach_to_gen(gen, brand):
    """Add product refs to a planned gen: start_frame.refs + seedance reference_image_paths (prompt cites <<<image_1>>>)."""
    r = refs_for(brand)[:4]
    gen.setdefault("start_frame", {}).setdefault("refs", []); gen["start_frame"]["refs"] = list(dict.fromkeys(gen["start_frame"]["refs"] + r))
    gen["reference_image_paths"] = r; return gen
