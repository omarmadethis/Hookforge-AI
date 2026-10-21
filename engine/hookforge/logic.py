"""LOGIC step (D61, Omar 2026-10-19 post-mortem of mg-tvn-001): every prompt must pass a believability check
BEFORE any credit is spent, and every generated clip gets a vision check after.

Prompt side (lint_prompt / lint_plan):
  LG1 camera stare     - gaze follows scene logic (D70): organic moments nobody looks at the camera; staged scenes (shot.scene_type in STAGED_SCENES) or shot.allow_camera may
  LG2 idle people      - every person named in a shot needs a motivated action (doing something TO something, for a reason)
  LG3 audio (D63)      - natural ambient sound only (real voices, some cheering, gasps, action sounds); FIX on added SFX
                         (whoosh, cartoon, boing, inserted YAY, sound effects, music) and on a missing natural-ambient line
  LG4 afters animate   - each after shot names its animation (what moves on the tree) and its design differs from the other afters
  LG7 everyone counts - (D73, Omar 2026-10-19) countdown/chant shots: EVERY on-screen speaker group (e.g. the girls holding the product AND the staff) says the line together; the prompt must name all of them as speaking. Never patch with added audio.
  LG5 recreate beats   - in recreate mode a shot may only deviate from the reference beat inside the 20 % innovation slot
Clip side (vision_check): YuNet face landmarks -> frontal faces held >= 0.75 s = person_facing_camera;
bright-region frame difference per shot -> static_lights; after-shot histogram similarity -> afters_not_distinct.
"""
import os, re, json, subprocess
import numpy as np
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
YUNET = os.path.join(REPO, "assets", "models", "face_detection_yunet_2023mar.onnx")

CAMERA_RX = re.compile(r"\b(look(?:s|ing)?|star(?:e|es|ing)|smil(?:e|es|ing)|grin(?:s|ning)?|pos(?:e|es|ing)|fac(?:e|es|ing)|wav(?:e|es|ing))\s+(?:straight\s+|directly\s+)?(?:at|into|to|toward|towards)\s+(?:the\s+)?(?:camera|lens|viewer)\b|\bto camera\b|\bbreaks? the fourth wall\b", re.I)
VOICE_RX = re.compile(r"\b(yay|hooray|woo+hoo+|whoosh\w*|swoosh\w*|boing\w*|cartoon\w*|sound effects?|sfx|ding|riser|stinger|laugh track|(?:background |added )?music)\b|\b(?:yells?|shouts?|screams?)\s+\W?yeah\b", re.I)   # D63: fake/inserted sounds only
AUDIO_RX = re.compile(r"(natural sound only|audio)\s*:\s*[^.\n]*", re.I)
PEOPLE_RX = re.compile(r"(?<!first-)\b(dad|mom|mum|man|woman|wife|husband|boy|girl|kids?|children|child|family|couple|person|teen|grandma|grandpa|guy|people)\b", re.I)
ACTION_RX = re.compile(r"\b(yank|pull|plug|kneel|reach|grab|lift|open|hold|carr(?:y|ies)|climb|lower|drop|place|hang|drap|lean|fall|flinch|jump|scramble|duck|step|turn|point|watch|wrap|untangl|sip|hand|pass|set|put|press|tap|slide|stretch|unfold|tilt|lunge|catch|tug|knock|cover|tip|walk|run|scoot|back(?:s|ing)? away|look(?:s|ing)? (?:down|up) at|eyes (?:are |stay )?on|focus|sit[s ]? (?:on|with|beside)|sits? up)\w*", re.I)
IDLE_RX = re.compile(r"\b(sit|sits|sitting|stand|stands|standing)\b(?![^.;]*\b(holding|untangl|watch|sipping|wrapping|plug|reach|turn|point|with|while)\w*)[^.;]*?(\.|;|$)", re.I)
ANIM_RX = re.compile(r"\b(animat\w*|ripple\w*|cycl\w*|puls\w*|twinkl\w*|sweep\w*|flicker\w*|crackl\w*|scroll\w*|chas\w*|spiral\w*|circl\w*|shift\w*|bob\w*|wav(?:e|es|ing)|flow\w*|blink\w*|switch(?:es)? on and off)\b", re.I)
DESIGNS = ["snowman", "train", "sleigh", "santa", "reindeer", "fire", "flame", "sweep", "snowflake", "candy cane", "gingerbread", "heart", "star", "rainbow", "present", "penguin", "grinch", "tree"]

STAGED_SCENES = {"staged", "planned", "countdown", "store_staff", "announcement", "presentation"}
def camera_allowed(shot):
    """D70: gaze follows scene logic. Staged/planned scenes (store staff countdown, announcement) may look into the lens;
    organic/unplanned moments (unbox, install, reaction, afters) may not. Default scene_type = organic."""
    shot = shot or {}
    return bool(shot.get("allow_camera")) or str(shot.get("scene_type", "organic")).lower() in STAGED_SCENES

def _sentences(p): return [s.strip() for s in re.split(r"(?<=[.;])\s+|\n+", p) if s.strip()]

def lint_prompt(prompt, kind="video", shot=None):
    """Returns list of {rule, severity, text, fix}. severity FIX blocks the plan; WARN is advisory."""
    shot = shot or {}; out = []
    if not camera_allowed(shot):
        for m in CAMERA_RX.finditer(prompt):
            if re.search(r"\b(never|not|no one|nobody|don't|doesn't)\b[^.]{0,40}$", prompt[:m.start()], re.I): continue
            out.append(dict(rule="LG1", severity="FIX", text=m.group(0), fix="nobody faces the camera: give them a task that points them at the tree/box/each other"))
    body = AUDIO_RX.sub("", prompt)
    for m in VOICE_RX.finditer(body):
        ctx = body[max(0, m.start() - 50):m.end() + 10]
        if re.search(r"\bno\b[^.]{0,60}$", body[:m.start()], re.I): continue
        out.append(dict(rule="LG3", severity="FIX", text=ctx.strip(), fix="no fake/added sounds (whoosh, cartoon, inserted YAY, SFX, music): keep only real sounds that match the action"))
    for m in AUDIO_RX.finditer(prompt):
        if re.search(r"\b(whoosh|cartoon|yay|music|sound effect)", m.group(0), re.I) and not re.search(r"\bno\b", m.group(0), re.I):
            out.append(dict(rule="LG3", severity="FIX", text=m.group(0)[:120], fix="audio line: 'Natural ambient sound only: ..., no added sound effects, no music'"))
    if kind == "video" and not re.search(r"natural ambient sound", prompt, re.I):
        out.append(dict(rule="LG3", severity="FIX", text="(missing)", fix="add 'Natural ambient sound only: real voices and action sounds that match what happens on screen, no added sound effects, no music.'"))
    if shot.get("people", True):
        for s in _sentences(prompt):
            if PEOPLE_RX.search(s) and not ACTION_RX.search(s) and not re.search(r"\b(no|never|nobody|keep|same|consistent|every)\b|^(cast|an?\s[\w -]*(?:dad|mom|boy|girl|man|woman)\b[^.]*\b(?:in|with)\b)", s, re.I):
                out.append(dict(rule="LG2", severity="FIX", text=s[:140], fix="every person needs a motivated action (what are they doing, to what, why)"))
        for m in re.finditer(r"\b(robotic\w*|blank(?:ly)? star\w*|motionless|frozen smile|posed|lined up)\b", prompt, re.I):
            out.append(dict(rule="LG2", severity="FIX", text=m.group(0), fix="people must move naturally with a reason"))
    if shot.get("role") == "after" and kind == "video":
        if not ANIM_RX.search(prompt): out.append(dict(rule="LG4", severity="FIX", text="(no animation verb)", fix="say what moves: e.g. 'the snowman's scarf ripples, snowflakes twinkle'"))
    if re.search(r"\b(3[-, ]+2[-, ]+1|three,? two,? one|countdown)\b", prompt, re.I) and kind == "video":
        groups = (shot or {}).get("speaker_groups") or []
        low = prompt.lower()
        if not re.search(r"\b(all|everyone|together|in unison)\b", low) or any(g.lower() not in low for g in groups):
            out.append(dict(rule="LG7", severity="FIX", text="(countdown not said by everyone)", fix="countdown: say who counts, e.g. 'the two girls holding the curtain AND the staff behind them all shout \"3, 2, 1\" together'; list every group in shot.speaker_groups"))
    return out

def designs(text): return {d for d in DESIGNS if re.search(r"\b" + d + r"s?\b", text, re.I)} - {"tree", "star"}

def lint_plan(plan):
    """Plan-level LOGIC: per-shot prompt lint + afters distinct + then-card count."""
    rows = []
    for g in plan["gens"]:
        for kind, p in (("video", g["prompt"]), ("still", g["start_frame"]["prompt"])):
            for f in lint_prompt(p, kind, dict(role=g.get("role"), allow_camera=g.get("allow_camera"), scene_type=g.get("scene_type"), people=g.get("people", True), speaker_groups=g.get("speaker_groups"))):
                rows.append(dict(gen=g["id"], kind=kind, **f))
    afters = [s for s in plan.get("shots", []) if s.get("role") == "after"]
    seen = []
    for s in afters:
        d = designs(s.get("animation", "") + " " + s.get("desc", ""))
        if not d: rows.append(dict(gen=s.get("gen"), kind="shot", rule="LG4", severity="FIX", text=s["code"], fix="name the design shown in this after shot"))
        for o, od in seen:
            if d and d == od: rows.append(dict(gen=s.get("gen"), kind="shot", rule="LG4", severity="FIX", text=f"{s['code']} == {o}", fix="each after shot shows a DIFFERENT animation"))
        seen.append((s["code"], d))
    if plan.get("problem_scenes") is not None:
        from . import textcards
        for p in textcards.check_cards(plan["text_cards"], plan["problem_scenes"]): rows.append(dict(gen="-", kind="cards", rule="LG6", severity="FIX", text=p, fix="1 problem scene = 1 caption"))
    return dict(ok=not any(r["severity"] == "FIX" for r in rows), rows=rows)

# ---------------- clip-side vision checks ----------------
def _frames(path, fps=4, w=360):
    pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", path], capture_output=True, text=True)
    W0, H0 = map(int, pr.stdout.strip().split(",")[:2]); h = int(round(H0 * w / W0 / 2) * 2)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={fps},scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True).stdout
    n = len(raw) // (w * h * 3); return np.frombuffer(raw[:n * w * h * 3], np.uint8).reshape(n, h, w, 3), fps

def facing_camera(path, fps=4, min_hold_s=1.0):
    import cv2
    fr, fps = _frames(path, fps, 480); H, W = fr.shape[1:3]
    det = cv2.FaceDetectorYN.create(YUNET, "", (W, H), 0.7)
    hits = []
    for i, f in enumerate(fr):
        _, faces = det.detect(f); n = 0
        for fc in (faces if faces is not None else []):
            x, y, w, h = fc[:4]; re_, le, nose = fc[4:6], fc[6:8], fc[8:10]
            ed = abs(le[0] - re_[0]) + 1e-6; off = abs(nose[0] - (le[0] + re_[0]) / 2) / ed
            if h > 0.035 * H and off < 0.18 and ed > 0.32 * w: n += 1      # frontal: nose centred between eyes, eyes wide apart
        hits.append(n)
    need = int(round(min_hold_s * fps)); runs, cur, start = [], 0, 0
    for i, n in enumerate(hits + [0]):
        if n: cur += 1; start = i - cur + 1
        else:
            if cur >= need: runs.append(dict(t0=round(start / fps, 2), t1=round((start + cur) / fps, 2), faces=max(hits[start:start + cur])))
            cur = 0
    return dict(frontal_faces_per_frame=hits, runs=runs, flag=bool(runs))

def cuts(path, thr=0.3):
    o = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-vf", f"select='gt(scene,{thr})',showinfo", "-an", "-f", "null", "-"], capture_output=True, text=True)
    return [round(float(x), 2) for x in re.findall(r"pts_time:([\d.]+)", o.stderr)]

def lights_motion(path, segments=None, fps=8):
    """Per segment: mean abs change of the bright (lit) pixels between consecutive frames. Static lights < 3.0 (calibrated: mg-tvn-001 B2 1.46, B3 2.51 = static per Omar; MG-01 train 19.7, Omar ref afters 6.6-25.8)."""
    fr, fps = _frames(path, fps, 240); g = fr.astype(np.float32).mean(3); n = len(g); dur = n / fps
    if segments is None:
        c = [0.0] + [x for x in cuts(path) if 0.2 < x < dur - 0.2] + [dur]; segments = list(zip(c, c[1:]))
    out = []
    for a, b in segments:
        i0, i1 = int(a * fps) + 1, max(int(a * fps) + 2, int(b * fps) - 1)
        seg = g[i0:i1]
        if len(seg) < 3: continue
        bright = seg.mean(0) > np.percentile(seg.mean(0), 85)
        d = np.abs(np.diff(seg, axis=0))[:, bright].mean()
        hist = np.histogram(fr[i0:i1].reshape(-1, 3)[::7], bins=24, range=(0, 255))[0].astype(float)
        out.append(dict(t0=round(a, 2), t1=round(b, 2), bright_motion=round(float(d), 2), static=bool(d < 3.0), _h=(hist / hist.sum()).tolist()))
    return out

def vision_check(path, role=None, after_segments=None):
    """Clip-level LOGIC checks. role 'after' adds static-light + distinct-after checks."""
    rep = dict(clip=os.path.basename(path), findings=[])
    fc = facing_camera(path); rep["facing_camera"] = {k: v for k, v in fc.items() if k != "frontal_faces_per_frame"}
    if fc["flag"]: rep["findings"].append(dict(failure="person_facing_camera", runs=fc["runs"]))
    if role == "after":
        lm = lights_motion(path, after_segments); rep["lights"] = [{k: v for k, v in s.items() if k != "_h"} for s in lm]
        for s in lm:
            if s["static"]: rep["findings"].append(dict(failure="static_lights", t0=s["t0"], t1=s["t1"], bright_motion=s["bright_motion"]))
        for i in range(len(lm)):
            for j in range(i + 1, len(lm)):
                a, b = np.array(lm[i]["_h"]), np.array(lm[j]["_h"]); sim = float(np.minimum(a, b).sum())
                if sim > 0.93: rep["findings"].append(dict(failure="afters_not_distinct", a=lm[i]["t0"], b=lm[j]["t0"], hist_overlap=round(sim, 3)))
    rep["ok"] = not rep["findings"]
    return rep
