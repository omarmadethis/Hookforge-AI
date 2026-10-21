"""D75 real-footage reveal shots from /workspace/research/product_footage/<product>/ (supplier clips pulled by Viral Research).
Real clips are source='real': no iPhone grade, no AI-look reroll, no Higgsfield credits; strip supplier watermarks/text is a manual
check (flag clips whose OCR finds text)."""
import os, glob, json, subprocess
ROOT = "/workspace/research/product_footage"; VID = (".mp4", ".mov", ".m4v", ".webm")

def probe(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:format=duration", "-of", "json", p], capture_output=True, text=True)
    j = json.loads(r.stdout or "{}"); s = (j.get("streams") or [{}])[0]
    return dict(w=s.get("width"), h=s.get("height"), dur=float(j.get("format", {}).get("duration", 0) or 0))

def clips(product, root=ROOT, min_dur=1.0):
    out = []
    for f in sorted(glob.glob(os.path.join(root, product, "**", "*"), recursive=True)):
        if f.lower().endswith(VID):
            m = probe(f)
            if m["dur"] >= min_dur: out.append(dict(path=f, **m, vertical=bool(m["w"] and m["h"] and m["h"] > m["w"])))
    return sorted(out, key=lambda c: (not c["vertical"], -c["dur"]))

def reveal_shot(product, dur=2.2, t_in=0.0, root=ROOT):
    """A timeline shot using real footage for the reveal (D74 reveal ~2.2 s). None if no footage yet -> planner keeps the AI reveal."""
    cs = clips(product, root, min_dur=dur)
    if not cs: return None
    c = cs[0]
    return dict(role="reveal", source="real", kind="footage", path=c["path"], t_in=t_in, dur=dur, credits=0,
                crop="9:16 center" if not c["vertical"] else None, note="real supplier footage (D75): no grade, no AI-look gate")

def use_real_reveal(plan, product, root=ROOT):
    """Swap the planned AI reveal gen for real footage when available; drops its credits from the quote."""
    rs = reveal_shot(product, root=root)
    if not rs: plan.setdefault("notes", []).append(f"D75: no real footage in {root}/{product} yet; AI reveal kept"); return plan
    gens = plan.get("gens", [])
    for g in gens:
        if g.get("role") == "reveal" or "reveal" in str(g.get("id", "")).lower():
            g.update(source="real", footage=rs["path"], credits=0, model="real_footage")
    plan.setdefault("real_shots", []).append(rs); return plan

# ---- D75 addendum (parent steer 2026-10-19 ~10 PM PT): curated supplier footage manifest ----
ALIASES = {"jollyglow_curtain": "jollyglow_curtain_lights", "jollyglow": "jollyglow_curtain_lights",
           "trumpglow": "trump_projector", "trumpglow_projector": "trump_projector"}
# use: reveal = usable as the real reveal; ref = motion/lighting/product reference only; composite = needs believable overlay first.
# crop = (x0, y0, x1, y1) fractions applied before the 9:16 reframe (watermark/caption removal).
MANIFEST = {
  "jollyglow_curtain_lights": {
    "jg04_window_curtain_color_cycle.mp4": dict(use="reveal", note="window curtain, clean"),
    "jg05_window_curtain_blue_green.mp4": dict(use="reveal", note="window curtain, clean"),
    "jg01_homeledpro_patterns_hearts_reindeer.mp4": dict(use="reveal", crop=(0, 0, 1, 0.84), note="4K, @HOMELEDPRO watermark bottom-centre (y~0.86-0.93) cropped; frames 0-3 s spell Chinese characters (wrong for US market) - ranked last; pick in/out on hearts/reindeer patterns only"),
    "jg02_homeledpro_rainbow_pixel_wall.mp4": dict(use="reveal", note="4K rainbow pixel wall"),
  },
  "trump_projector": {
    "tp01_lumi_face_projection.mp4": dict(use="composite", captions_burned=True, note="good reveal; captions burned in, no Trump image - reveal only if Trump logo composite is believable, else ref"),
    "tp03_lumi_dog_projection.mp4": dict(use="composite", captions_burned=True, note="good reveal; captions burned in; projection is a dog - composite needed"),
    "tp02_lumi_unit_install_handle.mp4": dict(use="ref", note="pod install motion reference (install/snap-on action, G12)"),
    "tp06_hr_photo_projection_close.mp4": dict(use="composite", note="clean but dim; lighting/puddle reference; composite+lift exposure if used"),
  },
}

def folder(product): return ALIASES.get(product, product)

def manifest(product):
    m = MANIFEST.get(folder(product), {}); d = os.path.join(ROOT, folder(product))
    return {k: dict(v, path=os.path.join(d, k)) for k, v in m.items() if os.path.exists(os.path.join(d, k))}

def reveal_candidates(product, allow_composite=False):
    ok = ("reveal", "composite") if allow_composite else ("reveal",)
    return [v for v in manifest(product).values() if v["use"] in ok]

def reframe_vf(w, h, crop=None, x_center=0.5, out_w=2160, out_h=3840):
    """Crop the (watermark-free) box, then a 9:16 window centred at x_center, scaled to the export size (lanczos)."""
    x0, y0, x1, y1 = crop or (0, 0, 1, 1)
    cw, ch = int(w * (x1 - x0)) // 2 * 2, int(h * (y1 - y0)) // 2 * 2
    tw = min(cw, int(ch * 9 / 16) // 2 * 2); th = min(ch, int(tw * 16 / 9) // 2 * 2)
    ox = int(w * x0 + max(0, min(cw - tw, cw * x_center - tw / 2))); oy = int(h * y0 + (ch - th) / 2)
    return f"crop={tw}:{th}:{ox}:{oy},scale={out_w}:{out_h}:flags=lanczos,setsar=1"

def reframe(src, dst, t_in=0.0, dur=2.2, crop=None, x_center=0.5, out_w=2160, out_h=3840):
    m = probe(src)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t_in), "-t", str(dur), "-i", src, "-vf", reframe_vf(m["w"], m["h"], crop, x_center, out_w, out_h),
                    "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-an", dst], check=True)
    return dst

def ref_stills(product, out_dir=None, per_clip=2, include_ref=True):
    """Frames from curated clips (cropped, 9:16) as GPT Image 2.0 / Seedance product+motion references."""
    out_dir = out_dir or os.path.join(ROOT, folder(product), "_ref_stills"); os.makedirs(out_dir, exist_ok=True); outs = []
    for name, v in manifest(product).items():
        if v["use"] == "ref" and not include_ref: continue
        m = probe(v["path"]); vf = reframe_vf(m["w"], m["h"], v.get("crop"), out_w=1080, out_h=1920)
        for i in range(per_clip):
            t = m["dur"] * (i + 1) / (per_clip + 1); o = os.path.join(out_dir, f"{os.path.splitext(name)[0]}_{i}.png")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", v["path"], "-frames:v", "1", "-vf", vf, o], check=True); outs.append(o)
    return outs

def reveal_shot(product, dur=2.2, t_in=0.0, root=ROOT, allow_composite=False):  # override: curated manifest first
    if root == ROOT and MANIFEST.get(folder(product)):
        cs = reveal_candidates(product, allow_composite)
        if not cs: return None
        c = cs[0]
        return dict(role="reveal", source="real", kind="footage", path=c["path"], t_in=t_in, dur=dur, credits=0, crop=c.get("crop"),
                    reframe="9:16", needs_composite=c["use"] == "composite", note=c["note"])
    p = folder(product); cs = clips(p, root, min_dur=dur)
    if not cs: return None
    c = cs[0]
    return dict(role="reveal", source="real", kind="footage", path=c["path"], t_in=t_in, dur=dur, credits=0,
                reframe=None if c["vertical"] else "9:16", note="real supplier footage (D75): no grade, no AI-look gate")
