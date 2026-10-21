"""D84 per-product reference library: refs/<slug>/manifest.json (+ clean product/cast copies).
build(slug) copies store/lifestyle photos from assets/<asset_dir> (ASSETS.csv clean_for_reference=y) into
refs/<slug>/product|cast/ through deliver.sanitize + deliver.scan (zero metadata, hard fail), and indexes files that
already live in refs/<slug>/ (POC sheets, worker-made refs) WITHOUT modifying them. attach(gen, product_key) adds
manifest refs to a planned gen (start_frame.refs + reference_image_paths) - planner.d75 calls it."""
import csv, json, os, glob, datetime
from .config import REPO
ROOT = os.path.join(REPO, "refs")
SLUGS = {   # product_key -> (refs slug, assets dir)
 "grinch_robe": ("grinch_robe", "grinch_robe"), "grinchmelt_mug": ("grinchmelt", "grinchmelt"), "brickhood_mask": ("brickhood", "brickhood"),
 "merryfire": ("merryfire", "merryfire"), "merryglow_lights": ("merryglow", "merryglow"), "jollyglow_curtain": ("jollyglow", "jollyglow"),
 "purrventure_carrier": ("purrventure", "purrventure"), "trumpglow": ("trumpglow", "patriotglow"), "minionmask": ("minionmask", "minionmask"),
 "heatjams": ("heatjams", "heatjams"), "cozyjams": ("cozyjams", "cozyjams"), "lumarein": ("lumarein", "lumarein")}
CAST = {   # F94 (Omar 2026-10-20): cast locked from avatars in each product's top proven video; default women, buyer logic wins
 "purrventure": "WOMAN (F94 cat products -> woman): woman cast ref refs/purrventure/ref_cast_woman_P2SF1.png + cream snow Bengal (tan rosettes, blue eyes). Supersedes the earlier man default. Proof video (Omar FB 1131865399523539) shows a man; RollyMew winners use women (gardening 7.6M/6.4M/5.4M)",
 "grinch_robe": "WOMAN: brown-haired woman in the Grinch robe from the 6.6M FB reel 1624473615929591 (refs/grinch_robe/cast/cast_woman_top.png)",
 "merryglow": "WOMAN (mom) + kids family scene from the 152.9K Merry Glow reel (cast_woman_top.png)",
 "merryfire": "WOMAN: blonde woman at the fire pit, 67.7K Merry Glows 1703965718404034; family movie-night woman, 63K MerryFires 1082602281322454",
 "jollyglow": "WOMEN: two young women in green + navy dresses from the 63.3K Merry Carrier reel (cast_women_top.png)",
 "grinchmelt": "WOMAN: woman in a cream sweater, living room, 23K IG DeGrL-XKMFp",
 "brickhood": "MASKED RIDER (face hidden by the product): skier in a teal jacket, 61.3K Brick Hood Shop; gender not visible",
 "minionmask": "MASKED RIDER: snowboarder in an orange jacket, 4.4K IG DeAurrvvndh",
 "trumpglow": "MAN (F94 Trump/car/patriotic -> man). Approved A v7 is hands-only POV (man's hands, car door): no face ref exists yet",
 "heatjams": "WOMAN (default, same buyer as grinch_robe; no own video for this slug)",
 "cozyjams": "WOMAN (default; no own video for this slug)",
 "lumarein": "WOMAN: young woman rider in a helmet (horse girl), as in LumaRein 2.6M/383.5K reels; new faces generated from scratch, no face copied",
}
PROTECTED = {"purrventure"}   # another worker owns these files (F88 redo): index only, never write images there
IMG = (".png", ".jpg", ".jpeg", ".webp"); VID = (".mp4", ".mov")

def _rows(asset_dir):
    p = os.path.join(REPO, "assets", "ASSETS.csv")
    return [r for r in csv.DictReader(open(p)) if r["slug"] == asset_dir] if os.path.exists(p) else []

def build(slug):
    from . import deliver
    asset_dir = next((a for s, a in SLUGS.values() if s == slug), slug); d = os.path.join(ROOT, slug); os.makedirs(d, exist_ok=True)
    items, refused = [], []
    for r in _rows(asset_dir):
        if r["clean_for_reference"] != "y" or r["type"] not in ("product", "box", "lifestyle") or not os.path.exists(r["box_path"]): continue
        if slug in PROTECTED: continue
        sub = "cast" if r["type"] == "lifestyle" else "product"; os.makedirs(os.path.join(d, sub), exist_ok=True)
        base = os.path.splitext(os.path.basename(r["box_path"]))[0]; ext = os.path.splitext(r["box_path"])[1].lower()
        src = r["box_path"]
        if ext == ".webp":   # deliver.sanitize has no webp branch: decode to PNG first, then sanitize the PNG
            from PIL import Image; src = os.path.join("/tmp", base + "_webp.png"); Image.open(r["box_path"]).convert("RGB").save(src); ext = ".png"
        ext = ".jpg" if ext == ".jpeg" else ext
        dst = os.path.join(d, sub, f"{r['type']}_{base}{ext}")
        if not os.path.exists(dst) or deliver.scan(dst): deliver.sanitize(src, dst)
        probs = deliver.scan(dst)
        if probs: os.remove(dst); refused.append(dict(src=r["box_path"], problems=probs)); continue
        items.append(dict(path=os.path.relpath(dst, REPO), kind="product" if sub == "product" else "cast_scene", type=r["type"],
                          what=r["product"], source=r["source_path_mac"] or r["box_path"], clean=True, use_for_generation=True))
    known = {i["path"] for i in items}
    for f in sorted(glob.glob(os.path.join(d, "**", "*"), recursive=True)):
        rel = os.path.relpath(f, REPO)
        if rel in known or not os.path.isfile(f) or not f.lower().endswith(IMG + VID): continue
        n = os.path.basename(f).lower()
        sub = os.path.basename(os.path.dirname(f))
        kind = "cast" if sub == "cast" or "cast" in n or "bengal" in n else "product" if sub == "product" or n.startswith(("ref_ball", "ref_disc", "product")) else "poc_reference"
        if slug == "purrventure" and "cast_man" in n: kind = "cast_superseded"   # F94 cat products -> woman
        items.append(dict(path=rel, kind=kind, what=n, source="existing refs/ file (see DECISIONS D80/D75)", clean=not deliver.scan(f),
                          use_for_generation=kind in ("product", "cast") and f.lower().endswith(IMG)))
    mid = os.path.join(d, "higgsfield_new_account_media_ids.json")
    man = dict(slug=slug, product_keys=[k for k, (s, _) in SLUGS.items() if s == slug], assets_dir=f"assets/{asset_dir}",
               approved_cast=CAST.get(slug), approved_cast_status=("locked (F94)" if CAST.get(slug) else "MISSING"),
               higgsfield_media_ids=os.path.relpath(mid, REPO) if os.path.exists(mid) else None,
               built_pt=datetime.datetime.now().isoformat(timespec="seconds"), refs=items, refused=refused,
               rule="F88: no generation without product AND cast refs; F87: every file passes deliver.scan")
    json.dump(man, open(os.path.join(d, "manifest.json"), "w"), indent=1, ensure_ascii=False)
    return man

def build_all(): return {s: build(s) for s in sorted({s for s, _ in SLUGS.values()})}

def manifest(product_key):
    slug = SLUGS.get(product_key, (product_key, None))[0]; p = os.path.join(ROOT, slug, "manifest.json")
    return json.load(open(p)) if os.path.exists(p) else None

def refs_for(product_key, kinds=("product", "cast")):
    m = manifest(product_key) or {}
    return [os.path.join(REPO, r["path"]) for r in m.get("refs", []) if r.get("use_for_generation") and r["kind"] in kinds and os.path.exists(os.path.join(REPO, r["path"]))]

def attach(gen, product_key, limit=4):
    prod = refs_for(product_key, ("product",))[:2]; cast = refs_for(product_key, ("cast", "cast_scene"))[:2]
    r = (prod + cast)[:limit]
    if not r: return gen
    sf = gen.setdefault("start_frame", {}); sf["refs"] = list(dict.fromkeys((sf.get("refs") or []) + r))
    gen["reference_image_paths"] = list(dict.fromkeys((gen.get("reference_image_paths") or []) + r))
    gen["ref_manifest"] = f"refs/{SLUGS.get(product_key, (product_key,))[0]}/manifest.json"
    return gen

if __name__ == "__main__":
    for s, m in build_all().items(): print(s, len(m["refs"]), "refs,", len(m["refused"]), "refused, cast:", m["approved_cast_status"])
