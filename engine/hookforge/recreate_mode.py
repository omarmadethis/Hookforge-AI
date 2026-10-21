"""RECREATE mode (D61, the default since Omar's mg-tvn-001 post-mortem, 2026-10-19):
"we're literally just trying to recreate slightly different original versions of our videos that already exist."

A plan is built from a recreate spec (refs/recreate/<product_key>.json). The spec holds the shot list extracted from the
actual winning reel(s): timing, action, camera, blocking, product behaviour and per-after animation, plus the cards and the
song from Omar's CapCut draft. The prompts below restate those beats. Only the 20 % innovation slot may change: cast,
room decor, and which animations the afters show. Every prompt then goes through the LOGIC lint (logic.py), the failure
memory (gen_failures.lint) and the house prompt checks before anything can be priced.
"""
import os, json, copy, hashlib
from .config import REPO, IPHONE12_SUFFIX
from . import logic, gen_failures as GF, prompts as P, textcards

SILENT = "Natural ambient sound only: real voices and action sounds that match what happens on screen, no added sound effects, no music."   # D63
LOOK = ("Vertical 9:16, 4-second clip, real handheld iPhone footage. Flat natural smartphone colour, neutral white balance, sharp front to back, "
        "no bokeh, no cinematic grading, no film grain, no slow motion. No text, captions or graphics in frame.")
A = lambda p: os.path.join(REPO, "assets", "merryglow", p)
ASSETS = dict(box=A("box/merryglow box.png"), lit_tree=A("lifestyle/hf_20260916_215623_b769b667-2331-4d9d-82e0-b6e83eaea14c.png"),
              ladder=A("lifestyle/hf_20260916_040659_d3012aab-315a-4e93-b5fe-adb9c8ac699a.png"))

def load_spec(product_key):
    p = os.path.join(REPO, "refs", "recreate", f"{product_key}.json")
    return json.load(open(p)) if os.path.exists(p) else None

def _sfx(p): return p.rstrip() + "\n\n" + IPHONE12_SUFFIX.strip()

def merryglow_gens(spec):
    v = spec["variation"]; cast, room = v["cast"], v["room"]
    H_still = (f"iPhone photo at night in a {room}. The Christmas tree in the corner is lit with old multicolour string lights. "
               f"Cast: {cast}. The dad kneels on the floor behind the tree at the wall outlet, pushing one more plug into a white power strip that is already "
               "crammed with plugs and adapters, his eyes on the strip. The mom stands next to the tree holding the end of a tangled light strand, handing it down to him. "
               "The boy sits on the rug untangling another strand in his lap. The beagle sniffs the cords on the floor. Everyone is focused on the outlet and the lights. "
               "Photo taken from standing height across the room. Top 20% plain wall/ceiling. Sharp, clean, realistic phone photo. A small American flag is visible on the bookshelf.")
    H_vid = (f"{LOOK} Start exactly from the start frame and keep every person, the dog and the room identical. "
             "0.0-1.6s: the dad pushes the last plug into the overloaded power strip while the mom holds the strand for him and the boy keeps untangling. "
             "1.6-2.2s: the power strip sparks with a bright flash and a small puff of white smoke; every light on the tree dies at once and the room drops to dim lamp light. "
             "2.2-4.0s: the dad jerks his hand back and falls onto his backside; the mom drops the strand and covers her mouth with both hands; the boy scoots back across the rug; "
             "the beagle backs away from the smoking strip. Their attention stays on the outlet and the dark tree. The phone jolts once when the sparks go, then steadies. "
             "A small American flag is visible on the bookshelf. " + SILENT)
    B1_still = ("iPhone photo, first-person view looking straight down at my own lap while sitting on a beige sofa, cosy cream knit sleeves on both arms. "
                "My hands hold open the green MerryGlow box from the first image, lid lifted: inside, the collapsed stack of thin gold LED rings sits under a conical silver star topper, "
                "with a small white remote and a power adapter in their own slots of the insert. Lights are OFF. Top 20% clear for text. Sharp, clean, realistic phone photo. "
                "A small American flag is visible on the bookshelf in the background.")
    B1_vid = (f"{LOOK} First-person view looking down at my lap, starting exactly from the start frame. "
              "0.0-1.0s: my hands finish lifting the box lid and set it aside. 1.0-3.0s: I pinch the star topper and lift the ring stack out of the box; the thin rings hang below it and "
              "stretch apart a little as they leave the box, swaying slightly. 3.0-4.0s: I hold the stack up above the open box, the remote and adapter still in their slots. "
              "The box and product look exactly like the first image. Lights stay OFF. A small American flag is visible in the background. " + SILENT)
    B2_still = (f"iPhone photo of a {room}, shot from across the room. A tall 7.5 ft Christmas tree stands UNLIT by the fireplace. A man (the dad from the cast) stands near the top of a "
                "silver aluminium step ladder beside the tree, holding the MerryGlow star topper with the collapsed ring stack hanging under it, about to set it on the tip; his eyes are on the tree top. "
                "The mom sits on the sofa with a mug, watching the tree. Lights OFF. Match the ladder set-up of the second image. Top 20% clear for text. Sharp, clean, realistic phone photo. "
                "A small American flag is visible on the bookshelf.")
    B2_vid = (f"{LOOK} Filmed from across the room, very slight natural phone shake. Keep the couple, the room, the tree, the ladder and every object exactly as in the start frame. "
              "0.0-1.0s: the man lowers the star and the stack of LED rings straight down onto the tree, sliding the stack over the very tip so the star sits on the highest branch; he lets go and pulls his hands back. "
              "1.0-3.5s: the stack of about 45 thin rings of tiny warm-white LED dots unfolds slowly downward over the tree like an accordion paper lantern opening, in one smooth, steady motion; "
              "each ring stays flat and horizontal and gets wider as it lowers, wrapping snugly around the cone of the tree; thin dark vertical wires keep the rings evenly spaced; "
              "the rings never tilt, tangle, bounce or pass through the branches. Every LED stays lit as a distinct point of light. "
              "3.5-4.0s: the bottom ring settles just above the base; the man looks down at the finished tree from the ladder; the mom on the sofa keeps watching the tree and sips her drink. "
              "The rings look exactly like the lit tree in the first image. A small American flag is visible on the bookshelf. " + SILENT)
    B3_still = (f"iPhone photo of the same {room} at night with all room lights off and black night outside the windows. The tall tree by the fireplace wears the MerryGlow ring lights from the first image "
                "(dense horizontal rows of individual LED dots, star topper) and is the only light source; wrapped presents at its base. No people. "
                "The rings display a pixel-art steam train. Sharp, clean, realistic phone photo. A small American flag is visible on the bookshelf.")
    B3_vid = ("Use the start frame and the first image as the exact specification for the room and the lights: a coarse low-resolution LED-matrix look, chunky blocky pixels where each bulb reads as one pixel, "
              "artwork flat on the surface of the tree. Nothing leaves the tree: no particles, light trails, projections or objects in the air. "
              f"{LOOK.replace('4-second clip, real handheld iPhone footage', '4-second clip')} Three hard cuts, no transitions, between three locked-off static shots; no camera movement. "
              "Same dark living room in every shot, the tree the only light source. No people. "
              "SHOT 1, 0.0-1.3s: wide shot, full tree and room. The tree shows a pixel steam train: the smoke cloud shifts pixel by pixel, the wheels cycle, snowflakes twinkle. HARD CUT. "
              "SHOT 2, 1.3-2.6s: medium shot from a lower angle off to the side. A pixel snowman face fills the bottom of the tree while Santa's sleigh and reindeer circle the top; the scarf ripples and the reindeer legs cycle. HARD CUT. "
              "SHOT 3, 2.6-4.0s: tight straight-on shot filling the frame. The whole tree shows a crackling pixel fire: the flames flicker and rise pixel by pixel. "
              "A small American flag is visible on the bookshelf in the wide shot. " + SILENT)
    G = []
    for gid, role, res, still, vid, refs in [("H", "problem", "1080p", H_still, H_vid, []),
                                             ("B1", "box", "720p", B1_still, B1_vid, ["box"]),
                                             ("B2", "install", "720p", B2_still, B2_vid, ["lit_tree", "ladder"]),
                                             ("B3", "after", "720p", B3_still, B3_vid, ["lit_tree"])]:
        G.append(dict(id=gid, role=role, model="seedance_2_5", res=res, dur=4, prompt=_sfx(vid), generate_audio=True,
                      start_frame=dict(model="gpt_image_2", prompt=_sfx(still), refs=[ASSETS[r] for r in refs]),
                      video_refs=[ASSETS[r] for r in refs if r != "ladder"], people=role not in ("after",),
                      shots=[s["code"] for s in spec["shots"] if s["gen"] == gid],
                      trims={s["code"]: s["trim"] for s in spec["shots"] if s["gen"] == gid},
                      credits=(64 if res == "1080p" else 28) + 6.5))
    return G

def build(product_key="merryglow_lights"):
    spec = load_spec(product_key)
    if spec is None: return None
    gens = merryglow_gens(spec)
    plan = dict(mode="recreate", product_key=product_key, spec=os.path.relpath(os.path.join(REPO, "refs", "recreate", f"{product_key}.json"), REPO),
                references=spec["references"], shots=copy.deepcopy(spec["shots"]), gens=gens, text_cards=spec["text_cards"],
                problem_scenes=spec["problem_scenes"], duration=spec["shots"][-1]["t1"], music=spec["music"],
                innovation_slot=spec["innovation_slot_20pct"], variation=spec["variation"],
                audio_policy="D63: generate_audio=True + natural-ambient line; keep real clip sound (voices, gasps, action sounds), boost the key real sound 2-4x; ban added SFX/whooshes/cartoon/YAY/music; song added in CapCut",
                credits=dict(per_gen={g["id"]: g["credits"] for g in gens}, total=sum(g["credits"] for g in gens),
                             note="video-reference inputs (B2/B3) may price differently: get_cost before approval"))
    plan["checks"] = check(plan)
    return plan

def check(plan):
    rows = []
    for g in plan["gens"]:
        for kind, p, m in (("video", g["prompt"], g["model"]), ("still", g["start_frame"]["prompt"], "gpt_image_2")):
            l = GF.lint(p, model=m); rows += [dict(gen=g["id"], kind=kind, src="failure_memory", rule=h["rule_id"], severity=h["severity"], text=h.get("trigger", "")) for h in l["hits"]]
            rows += [dict(gen=g["id"], kind=kind, src="prompt_check", rule="P", severity="FIX", text=x) for x in P.check(p, "body" if kind == "video" and g["id"] != "H" else kind) if "HARD CUT" not in x or g["id"] == "B3"]
    lp = logic.lint_plan(plan); rows += [dict(src="logic", **r) for r in lp["rows"]]
    from . import audience_fit                      # D62 mandatory AUDIENCE-FIT stage
    af, af_rows = audience_fit.lint_rows(plan); plan["audience_fit"] = af; rows += [dict(src="audience_fit", **r) for r in af_rows]
    from . import edit_rules                         # EDIT_RULES.md defaults (FIX = zoom/slow-mo/unmuted audio, WARN = targets)
    er = edit_rules.lint(plan); plan["edit_lint"] = er; rows += [dict(src="edit_rules", **r) for r in er["rows"]]
    return dict(ok=not any(r["severity"] == "FIX" for r in rows), rows=rows)

def plan_sha(plan):
    core = [dict(id=g["id"], prompt=g["prompt"], still=g["start_frame"]["prompt"], res=g["res"]) for g in plan["gens"]]
    return hashlib.sha256(json.dumps(core, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

# ---------------- dry run (no generation, no credits) ----------------
def _frame(video, t, w=300):
    import subprocess, io
    from PIL import Image
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", video, "-frames:v", "1", "-vf", f"scale={w}:-2", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
    return Image.open(io.BytesIO(raw)).convert("RGB")

def side_by_side(plan, out_png, w=300):
    from PIL import Image, ImageDraw, ImageFont
    h = int(w * 16 / 9); font = ImageFont.truetype(textcards.MONT, 17); bold = ImageFont.truetype(textcards.MONT, 22)
    refs = {k: (v["file"] if v["file"].startswith("/") else os.path.join(REPO, v["file"])) for k, v in plan["references"].items()}
    cols = ["MG-01 (posted, 152.9K)", "OMAR_REF (draft 0924 (2))", "Shot reference asset", "OUR RECREATE (plan)"]
    head = 40; rows = plan["shots"]; S = Image.new("RGB", (w * 4, head + h * len(rows)), "white"); d = ImageDraw.Draw(S)
    for i, c in enumerate(cols): d.text((i * w + 8, 10), c, fill="black", font=bold)
    gens = {g["id"]: g for g in plan["gens"]}
    for r, s in enumerate(rows):
        y = head + r * h
        for c, key in enumerate(["MG-01", "OMAR_REF"]):
            seg = s["ref"].get(key)
            if seg:
                im = _frame(refs[key], (seg[0] + seg[1]) / 2, w); im = im.resize((w, h)); S.paste(im, (c * w, y))
                d.text((c * w + 6, y + h - 26), f"{key} {seg[0]:.2f}-{seg[1]:.2f}s", fill="yellow", font=font, stroke_width=2, stroke_fill="black")
            else: d.rectangle((c * w, y, c * w + w - 1, y + h - 1), fill=(40, 40, 40)); d.text((c * w + 10, y + 10), "(no matching beat)", fill="white", font=font)
        g = gens[s["gen"]]; ref = (g["start_frame"].get("refs") or [None])[-1] if s["role"] != "after" else (g["start_frame"].get("refs") or [None])[0]
        if ref:
            im = Image.open(ref).convert("RGB"); im = im.resize((w, int(im.height * w / im.width))); S.paste(im.crop((0, 0, w, min(h, im.height))), (2 * w, y))
            d.text((2 * w + 6, y + h - 26), os.path.basename(ref)[:34], fill="yellow", font=font, stroke_width=2, stroke_fill="black")
        panel = Image.new("RGBA", (w, h), (25, 25, 30, 255))
        card = next((c for c in plan["text_cards"] if c["t"] <= s["t0"] < c["t"] + c["dur"]), None)
        if card: panel.alpha_composite(textcards.render_card(card["text"], w, h))
        pd = ImageDraw.Draw(panel); txt = f"{s['code']}  {s['t0']:.1f}-{s['t1']:.1f}s  gen {s['gen']} trim {s['trim']}\n"
        body = (s.get("animation") and "ANIM: " + s["animation"] + "\n" or "") + s.get("action", "") + "\nCAM: " + s.get("camera", "") + "\nPEOPLE: " + s.get("people", "")
        import textwrap
        lines = [txt.strip()] + sum([textwrap.wrap(x, 34) for x in body.split("\n")], [])
        pd.multiline_text((8, int(h * 0.30)), "\n".join(lines[:22]), fill="white", font=font, spacing=3)
        S.paste(panel.convert("RGB"), (3 * w, y))
        d.line((0, y, 4 * w, y), fill="black", width=2)
    S.save(out_png); return out_png

def card_samples(out_dir, W=1080, H=1920):
    from PIL import Image
    os.makedirs(out_dir, exist_ok=True); paths = []
    bg = Image.open(ASSETS["lit_tree"]).convert("RGBA").resize((W, H))
    for i, t in enumerate(["The problem... 🤕", "Vs... ⏰", "The solution 🤩"]):
        L = textcards.render_card(t, W, H); L.save(os.path.join(out_dir, f"card{i}_transparent.png"))
        im = bg.copy(); im.alpha_composite(L); im.convert("RGB").save(os.path.join(out_dir, f"card{i}_on_frame.png")); paths.append(os.path.join(out_dir, f"card{i}_on_frame.png"))
    for e in "🤕⏰🤩": paths.append(textcards.apple_png(e))
    return paths

def capcut_draft(plan, out_root, name="RECREATE_MG_DRYRUN"):
    """Draft with the plan's timing + house cards (first preset style, stroke 45 = width 0.09, scale 1.0, y 0.582), clip audio 0.
    Media = Omar's reference reel segments as PLACEHOLDERS until the live clips exist."""
    import shutil
    from . import capcut_export, qa
    ref = os.path.join(REPO, plan["references"]["OMAR_REF"]["file"]); md = os.path.join(out_root, "_media"); os.makedirs(md, exist_ok=True)
    mf = os.path.join(md, "placeholder_omar_ref.mp4"); shutil.copy(ref, mf); pr = qa.probe(mf)
    mac = "/Users/omar/Movies/CapCut/User Data/Projects/com.lveditor.draft"
    shots = [dict(file=mf, clip_start=s["ref"]["OMAR_REF"][0], dur=round(s["t1"] - s["t0"], 3), speed=1.0, clip_dur=pr["dur"], w=pr["w"], h=pr["h"]) for s in plan["shots"]]
    cplan = dict(name=name, canvas=[1080, 1920], fps=30, clip_audio_volume=1.0, mac_draft_root=mac, media_root_map=(md, f"{mac}/{name}/media"), shots=shots,
                 texts=[dict(t=c["t"], dur=c["dur"], text=c["text"], y=0.582, scale=None) for c in plan["text_cards"]])
    cdir = capcut_export.export(cplan, out_root); shutil.move(md, os.path.join(cdir, "media"))
    return cdir, capcut_export.verify(cdir)

def dry_run(out_dir=None, product_key="merryglow_lights"):
    plan = build(product_key); out_dir = out_dir or os.path.join(REPO, "out", "dryrun", "mg_recreate_mg01"); os.makedirs(out_dir, exist_ok=True)
    plan["plan_sha256"] = plan_sha(plan)
    json.dump(plan, open(os.path.join(out_dir, "plan.json"), "w"), indent=1, ensure_ascii=False)
    sheet = side_by_side(plan, os.path.join(out_dir, "side_by_side_vs_MG01_and_OMAR_REF.png"))
    samples = card_samples(os.path.join(out_dir, "cards"))
    cdir, probs = capcut_draft(plan, os.path.join(out_dir, "capcut"))
    return dict(plan=plan, sheet=sheet, samples=samples, capcut=cdir, capcut_problems=probs)
