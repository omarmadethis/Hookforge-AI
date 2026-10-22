"""D191 MASTER PRE-DELIVERY GATE (Omar 2026-10-21 ~5:15 PM PT: "I should not have to tell you something more than once").

Every deliverable (final video, image, pfp, cover, thumbnail, start frame shown to Omar, any file) passes this gate
before it is rendered as final, shown to Omar, or published. Rules live in rules/MASTER_RULES.md (rules/build_master.py).

    from hookforge import master_gate as MG
    res = MG.ensure(path, spec)            # check -> auto-fix (free first) -> re-check, loop until PASS
    MG.require(path, stage="deliver")      # deliver.stage / publish.prepare call this; raises GateRefused w/o a PASS report

Spec: a dict (or the sidecar <file>.gate.json). Video keys: video_id, product, page, hook{format,first_second_action,
conflict,conflict_t_s,count321}, shots[{gen,t0,t1,role}], cards[{text,t0,t1,y,why,shows}], song{key,path,in_s,
recreate_of{slug,reel_id}}, gens[{id,role,res,dur,model,shots,end_frame}], frames[{id,model,refs}], prompts[], spend{cap,spent},
frames_shown, own_globs[], edit{body,body_gain,W,H} (enables free recompose), regen{cap_remaining,cost_per_clip,runner},
confirm{MRxx:{by,note}} (reviewer sign-off for judgment rules), caption, approved_caption, approval{by,quote}.

Auto-fix order (Omar 2026-10-21): free re-edits first (metadata strip, card text/count/VS/emoji/timing/position, song
re-lay, caption rewrite) -> re-run the gate -> loop. Footage problems regenerate ONLY through spec.regen.runner and only
while the approved cap covers the cost; otherwise the result is NEEDS_REGEN_WITHIN_CAP with the exact plan. Never stops at a
fixable failure. A PASS writes <file>.PASS.json + <file>.PASS.md (sha256-bound) next to the final."""
import copy, datetime, glob, hashlib, json, os, re, shutil, subprocess
from .config import REPO
PT = __import__("zoneinfo").ZoneInfo("America/Los_Angeles")
RULES_JSON = os.path.join(REPO, "rules", "master_rules.json")
REGISTRY = os.path.join(REPO, "learning", "footage_registry.json")
HASH_CACHE = os.path.join(REPO, "learning", "footage_hash_cache.json")
PUBLISH_LOG = os.path.join(REPO, "learning", "publish_log")
VIDEO_EXT = (".mp4", ".mov", ".m4v")
IMAGE_EXT = (".png", ".jpg", ".jpeg", ".webp")
ACTIVE_PRODUCTS = {"jollyglow_curtain", "jollyglow", "trumpglow", "purrventure_carrier", "purrventure", "lumarein"}
try:   # products marked "active": true in config/products.json are active too (how a new user adds their own products)
    ACTIVE_PRODUCTS |= {k for k, v in json.load(open(os.path.join(REPO, "config", "products.json")))["products"].items() if v.get("active")}
except Exception: pass
MAX_ITERS = 8
CANDIDATE_ROOTS = [os.path.join(REPO, "out")]   # every rendered/generated video we have; + learning/footage_registry.json
CARD_WORD_MAX = 8
class GateRefused(Exception): pass

def rules(): return json.load(open(RULES_JSON))
def now_pt(): return datetime.datetime.now(PT).strftime("%Y-%m-%d %I:%M %p PT")
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
def kind_of(path):
    e = os.path.splitext(path)[1].lower()
    return "video" if e in VIDEO_EXT else "image" if e in IMAGE_EXT else "file"
def load_spec(path):
    p = path + ".gate.json"
    return json.load(open(p)) if os.path.exists(p) else {}
def F(rule, msg, fix=None, data=None): return dict(rule=rule, msg=msg, fix=fix, data=data or {})
def _txt(c): return (c.get("text") if isinstance(c, dict) else str(c)) or ""
def _words(t):
    from .gates import words
    return words(t)
def _ffprobe(path):
    o = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height:format=duration", "-of", "json", path],
                       capture_output=True, text=True).stdout
    return json.loads(o or "{}")
def _dur(path): return float(_ffprobe(path).get("format", {}).get("duration", 0) or 0)

# ======================= AUTO CHECKS (fn name == rules[*].fn) =======================
def c_metadata(path, spec, stage):
    from . import deliver
    k = os.path.splitext(path)[1].lower()
    if k in VIDEO_EXT + IMAGE_EXT + (".txt", ".md", ".csv", ".json", ".srt"):
        p = deliver.scan(path)
    else:   # any other file: exiftool must report nothing beyond File/System/ExifTool/Composite groups
        try: meta = json.loads(subprocess.run(["exiftool", "-j", "-G", "-a", "-u", path], capture_output=True, text=True).stdout)[0]
        except Exception as e: return [F("MR01", f"exiftool failed: {e}", "sanitize")]
        p = [k2 for k2 in meta if k2 != "SourceFile" and k2.split(":")[0] not in ("File", "System", "ExifTool", "Composite")]
    return [F("MR01", "metadata/trace: " + "; ".join(p)[:400], "sanitize")] if p else []

def c_res_720(path, spec, stage):
    f = []
    v = [s for s in _ffprobe(path).get("streams", []) if s.get("codec_type") == "video"]
    if v and (min(v[0]["width"], v[0]["height"]) != 720 or max(v[0]["width"], v[0]["height"]) != 1280):
        f.append(F("MR03", f"final is {v[0]['width']}x{v[0]['height']}, not 720x1280", "recompose"))
    for g in spec.get("gens", []):
        if str(g.get("res", "720p")) != "720p": f.append(F("MR03", f"gen {g.get('id')} is {g.get('res')} (all gens 720p, D181)", "regen", dict(gen=g.get("id"))))
    return f

def c_gen_packing(path, spec, stage):
    f = []
    for g in spec.get("gens", []):
        n = len(g.get("shots") or []); role = g.get("role", "body")
        if role == "hook" and (n not in (0, 1) or float(g.get("dur", 4)) != 4):
            f.append(F("MR04", f"hook gen {g.get('id')} must be its own single 4 s gen ({n} shots, {g.get('dur')} s)", "regen", dict(gen=g.get("id"))))
        if role != "hook" and n and n != 2:
            f.append(F("MR04", f"body gen {g.get('id')} packs {n} shots (2 per 4 s gen with a hard cut)", "regen", dict(gen=g.get("id"))))
    return f

def c_gen_len(path, spec, stage):
    f = [F("MR05", f"gen {g.get('id')} is {g.get('dur')} s > 5 s", "regen", dict(gen=g.get("id"))) for g in spec.get("gens", []) if float(g.get("dur", 4)) > 5]
    hk = [s for s in spec.get("shots", []) if s.get("role") == "hook"]
    if hk and hk[-1]["t1"] - hk[0]["t0"] > 5.0 + 1e-6: f.append(F("MR05", f"hook on screen {hk[-1]['t1'] - hk[0]['t0']:.2f} s > 5 s", "recompose"))
    return f

def c_gen_models(path, spec, stage):
    f = []
    for g in spec.get("gens", []):
        m = str(g.get("model", "seedance_2_5")).lower()
        if "seedance" not in m or "kling" in m: f.append(F("MR06", f"gen {g.get('id')} model {m} (Seedance 2.5 only)", "regen", dict(gen=g.get("id"))))
        if g.get("end_frame"): f.append(F("MR06", f"gen {g.get('id')} used an end frame (start frames only)", "regen", dict(gen=g.get("id"))))
    return f

def c_frame_refs(path, spec, stage):
    f = []
    for fr in spec.get("frames", []):
        if "gpt" not in str(fr.get("model", "gpt_image_2")).lower(): f.append(F("MR07", f"frame {fr.get('id')} model {fr.get('model')} (GPT Image 2 only)", "regen"))
        if not fr.get("refs"): f.append(F("MR07", f"frame {fr.get('id')} generated without refs attached", "regen"))
    return f

def c_frames_shown(path, spec, stage):
    return [] if spec.get("frames_shown", True) else [F("MR08", "start frames were not shown to Omar before clip spend", None)]

def c_spend_cap(path, spec, stage):
    s = spec.get("spend") or {}
    if not s: return []
    if s.get("cap") is None: return [F("MR09", "no approved credit cap recorded", None)]
    return [F("MR09", f"spent {s.get('spent')} > approved cap {s['cap']}", None)] if float(s.get("spent", 0)) > float(s["cap"]) + 1e-6 else []

def c_realism_suffix(path, spec, stage):
    return [F("MR10", f"prompt without iPhone realism suffix: {p[:60]}...", "regen") for p in spec.get("prompts", []) if "iphone" not in p.lower()]

def c_flag_hint(path, spec, stage):
    """Auto hint only (vision confirm is the manual half): share of 2 fps frames with saturated red AND blue regions."""
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", "fps=2,scale=90:160,format=rgb24", "-f", "rawvideo", "-"], capture_output=True).stdout
    a = np.frombuffer(raw, np.uint8)
    if not a.size: return []
    fr = a[: a.size // (90 * 160 * 3) * 90 * 160 * 3].reshape(-1, 160, 90, 3).astype(int)
    r, g, b = fr[..., 0], fr[..., 1], fr[..., 2]
    red = ((r > 140) & (g < 90) & (b < 90)).mean((1, 2)); blue = ((b > 90) & (r < 70) & (g < 90)).mean((1, 2))
    share = float(((red > 0.004) & (blue > 0.004)).mean())
    spec.setdefault("_hints", {})["flag_frame_share"] = round(share, 3)
    if share > 0.05: return []
    cf = (spec.get("confirm") or {}).get("MR13") or {}
    if cf.get("by") and cf.get("sha256") == sha(path) and len((cf.get("note") or "").split()) >= 8: return []   # vision reviewer saw the flag (night/desaturated flags defeat the colour hint)
    return [F("MR13", f"US-flag colours found in only {share:.0%} of frames - flag likely missing/too small (reviewer must confirm with timestamps, or regen)", "regen")]

# ---------- footage uniqueness (perceptual hash) ----------
def _hashes(path):
    import numpy as np
    cache = json.load(open(HASH_CACHE)) if os.path.exists(HASH_CACHE) else {}
    st = os.stat(path); key = f"{os.path.abspath(path)}|{st.st_size}|{int(st.st_mtime)}"
    if key in cache: return np.array(cache[key], dtype=np.uint8).reshape(-1, 256) if cache[key] else np.zeros((0, 256), np.uint8)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", "fps=4,scale=16:16:flags=area,format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
    a = np.frombuffer(raw, np.uint8)[: len(raw) // 256 * 256].reshape(-1, 256).astype(float)
    keep = a.std(1) > 8                                      # near-black/flat frames carry no identity
    bits = (a[keep] > a[keep].mean(1, keepdims=True)).astype(np.uint8)
    cache[key] = bits.flatten().tolist(); os.makedirs(os.path.dirname(HASH_CACHE), exist_ok=True)
    json.dump(cache, open(HASH_CACHE, "w")); return bits
def shared_ratio(a, b, max_bits=20):
    import numpy as np
    if not len(a) or not len(b): return 0.0
    pa = np.packbits(a, axis=1).view(np.uint64); pb = np.packbits(b, axis=1).view(np.uint64)
    d = np.bitwise_count(pa[:, None, :] ^ pb[None, :, :]).sum(2)
    return float((d.min(1) <= max_bits).mean())
def _own(path, spec):
    ap = os.path.abspath(path); globs = [os.path.join(REPO, g) if not os.path.isabs(g) else g for g in spec.get("own_globs", [])]
    fam = set(glob.glob(os.path.join(os.path.dirname(ap), os.path.basename(ap).split("_")[0] + "_*")))
    for g in globs: fam |= set(glob.glob(g))
    return {os.path.abspath(x) for x in fam} | {ap}
def candidates(path, spec):
    own = _own(path, spec); out = []
    for p in [x for root in CANDIDATE_ROOTS for x in glob.glob(os.path.join(root, "**", "*.mp4"), recursive=True)]:
        if os.path.abspath(p) in own or "/dryrun/" in p or "/deliver/preview__" in p: continue
        out.append(p)
    reg = json.load(open(REGISTRY)) if os.path.exists(REGISTRY) else {}
    out += [r["path"] for r in reg.values() if os.path.exists(r.get("path", "")) and os.path.abspath(r["path"]) not in own]
    return sorted(set(out))
def c_footage_unique(path, spec, stage, thr=0.02):
    a = _hashes(path); f = []
    for p in candidates(path, spec):
        try: r = shared_ratio(a, _hashes(p))
        except Exception: continue
        if r > thr: f.append(F("MR18", f"{r:.0%} of frames match {os.path.relpath(p, REPO)} (D180: zero shared footage)", "regen", dict(other=p, ratio=r)))
    return f

def c_page_unique(path, spec, stage):
    reg = json.load(open(REGISTRY)) if os.path.exists(REGISTRY) else {}; h = sha(path); f = []; page = spec.get("page")
    a = None
    for vid, r in reg.items():
        if not r.get("posted_pages"): continue
        same = r.get("sha256") == h
        if not same and os.path.exists(r.get("path", "")):
            a = _hashes(path) if a is None else a; same = shared_ratio(a, _hashes(r["path"])) > 0.9
        if same: f.append(F("MR19", f"this video is already posted as {vid} on {r['posted_pages']} - never repost / never 2 pages", None))
    return f

def c_active_product(path, spec, stage):
    p = (spec.get("product") or "").lower()
    return [F("MR21", f"product '{p}' is retired / not active (reference data only)", None)] if p and p not in ACTIVE_PRODUCTS else []

def c_hook_plan(path, spec, stage):
    if not spec.get("hook"): return [F("MR22", "spec has no hook declaration (format/conflict/first-second action)", None)]
    from . import omar_gates_f100 as O
    f = []
    for m in O._hook_gate_base(spec["hook"]):
        f.append(F("MR23" if ("conflict" in m or "first second" in m) else "MR22", m, "regen"))
    return f

def c_count321(path, spec, stage):
    from . import omar_gates_f100 as O
    return [F("MR24", m, "regen") for m in O.count321_gate(spec.get("hook") or {})]

# ---------- audio ----------
def _pcm(path, ss=0.0, t=None, sr=8000):
    import numpy as np
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{ss:.3f}", "-i", path] + (["-t", f"{t:.3f}"] if t else []) + ["-ac", "1", "-ar", str(sr), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32)
def _flux(x, n=512, hop=128):
    import numpy as np
    if len(x) < n: return np.zeros(1)
    fr = np.lib.stride_tricks.sliding_window_view(x, n)[::hop] * np.hanning(n)
    m = np.log1p(np.abs(np.fft.rfft(fr, axis=1)) * 10)
    fl = np.maximum(np.diff(m, axis=0), 0).sum(1)
    return (fl - fl.mean()) / (fl.std() + 1e-9)
def song_continuity(final, ref, in_s, win=2.0, step=1.0, max_lag=0.5, min_corr=0.3, lag_tol=0.08, sr=8000):
    """Per 2 s window: best xcorr lag of final-vs-reference onset envelope. Continuous song = every window at ~0 lag."""
    import numpy as np
    d = _dur(final); x = _flux(_pcm(final, 0, d, sr)); y = _flux(_pcm(ref, max(in_s - max_lag, 0), d + 2 * max_lag, sr))
    fps = sr / 128; L = int(max_lag * fps); W = int(win * fps); bad = []; rows = []
    off = int(min(max_lag, in_s) * fps)
    for s in range(0, max(len(x) - W, 0) + 1, int(step * fps)):
        xs = x[s:s + W]; best = (-1, 0)
        for lag in range(-L, L + 1):
            j = s + off + lag
            if j < 0 or j + W > len(y): continue
            c = float(np.corrcoef(xs, y[j:j + W])[0, 1])
            if c > best[0]: best = (c, lag / fps)
        rows.append(dict(t=round(s / fps, 2), corr=round(best[0], 2), lag_s=round(best[1], 3)))
        if best[0] < min_corr or abs(best[1]) > lag_tol: bad.append(rows[-1])
    return rows, bad
def c_song_continuity(path, spec, stage):
    import numpy as np
    s = spec.get("song") or {}; f = []
    if not s.get("path"): return [F("MR25", "no reference song path in spec - cannot verify song from frame 0 / no loops", None)]
    head = _pcm(path, 0, 0.25)
    db = 20 * np.log10(float(np.sqrt((head ** 2).mean())) + 1e-9) if head.size else -120
    if db < -40: f.append(F("MR25", f"silent lead-in: first 0.25 s at {db:.0f} dBFS (song must start at frame 0)", "recompose"))
    rows, bad = song_continuity(path, os.path.join(REPO, s["path"]) if not os.path.isabs(s["path"]) else s["path"], float(s.get("in_s", 0)))
    spec.setdefault("_hints", {})["song_windows"] = rows
    if bad: f.append(F("MR25", f"song not continuous vs reference at {[(b['t'], b['corr'], b['lag_s']) for b in bad][:6]} (loop/splice/wrong section)", "recompose"))
    return f

def c_recreation_song(path, spec, stage):
    s = spec.get("song") or {}
    if not s.get("recreate_of"): return []
    from . import original_song
    return [F("MR26", m, "recompose") for m in original_song.gate(dict(recreate_of=s["recreate_of"], song_key=s.get("key"), song_in_s=s.get("in_s"), song_start_t=s.get("start_t", 0), song_loops=s.get("loops", False)))]

def c_no_phonk(path, spec, stage):
    from .gates import PHONK
    k = str((spec.get("song") or {}).get("key", ""))
    return [F("MR27", f"song '{k}' is phonk/slowed (banned)", None)] if re.search(PHONK, k) else []

def c_payoff_cuts(path, spec, stage):
    from . import omar_gates_f100 as O
    sh = spec.get("shots") or []
    if not sh: return [F("MR30", "spec has no shot list - cannot verify the payoff cuts", None)]
    f = [F("MR30", m, "regen" if "cuts <" in m else "recompose") for m in O.payoff_gate(sh)]
    p = [s for s in sh if s.get("role") in ("payoff", "reveal", "after")]
    if p:   # measured: hard cuts detected inside the payoff window on the render
        a, b = p[0]["t0"], p[-1]["t1"]
        o = subprocess.run(["ffmpeg", "-v", "info", "-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", path, "-vf", "scdet=threshold=8", "-an", "-f", "null", "-"], capture_output=True, text=True).stderr
        n = len(re.findall(r"lavfi.scd.time", o))
        spec.setdefault("_hints", {})["payoff_measured_cuts"] = n
        if n < 2: f.append(F("MR30", f"render shows {n} hard cuts in the payoff ({a:.2f}-{b:.2f} s), need >= 2", "regen"))
    return f

# ---------- cards ----------
def _fmt(spec): return (spec.get("hook") or {}).get("format") or spec.get("hook_format")
def c_card_count(path, spec, stage):
    from . import card_count
    return [F("MR31", m, "recompose") for m in card_count.gate(spec.get("cards") or [], _fmt(spec))]
def c_card_words(path, spec, stage):
    return [F("MR32", f"card '{_txt(c)}' has {_words(_txt(c))} words > {CARD_WORD_MAX}", "recompose") for c in spec.get("cards") or [] if _words(_txt(c)) > CARD_WORD_MAX]
VS_RE = re.compile(r"(?i)\bvs\b\.*|\bversus\b")
def c_vs_position(path, spec, stage):
    cs = spec.get("cards") or []; f = []
    for i, c in enumerate(cs):
        mid = len(cs) >= 3 and 0 < i < len(cs) - 1
        if VS_RE.search(_txt(c)) and not mid: f.append(F("MR33", f"'VS' on card {i + 1}/{len(cs)} '{_txt(c)}' (only on the middle card)", "recompose"))
    return f
GET_YOURS = re.compile(r"(?i)\bget\s+(yours|it\s+now|one\s+now)\b|https?://|www\.")
def c_no_get_yours(path, spec, stage):
    f = [F("MR34", f"card '{_txt(c)}' has 'Get yours'/URL", "recompose") for c in spec.get("cards") or [] if GET_YOURS.search(_txt(c))]
    if spec.get("caption") and re.search(r"(?i)\bget\s+yours\b", spec["caption"]): f.append(F("MR34", "caption has 'Get yours'", "caption"))
    return f
def c_apple_emoji(path, spec, stage):
    """Text: every emoji has an Apple PNG. Pixels: the card layer equals textcards.render_card (Apple glyphs) at its scale/y."""
    from . import emoji_gate, textcards as TC
    from PIL import Image, ImageChops
    f = []; W, H = (spec.get("edit") or {}).get("W", 720), (spec.get("edit") or {}).get("H", 1280)
    for c in spec.get("cards") or []:
        f += [F("MR35", m, "recompose") for m in emoji_gate.gate_text(_txt(c))]
        if c.get("png") and os.path.exists(c["png"]) and emoji_gate.emojis(_txt(c)):
            ref = TC.render_card(_txt(c), W, H, scale=c.get("scale", 1.0), y=c.get("y")).convert("RGBA"); got = Image.open(c["png"]).convert("RGBA")
            if got.size != ref.size or ImageChops.difference(got, ref).getbbox() is not None:
                f.append(F("MR35", f"card '{_txt(c)}' layer is not the Apple-emoji textcards render (D189)", "recompose"))
    return f
def c_card_timing(path, spec, stage):
    from . import omar_gates_f100 as O
    cs = [dict(text=_txt(c), t0=c["t0"], t1=c["t1"]) for c in spec.get("cards") or [] if "t0" in c]
    f = [F("MR36", m, "recompose") for m in O.card_timing(spec.get("shots") or [], cs)] if spec.get("shots") else []
    for c in spec.get("cards") or []:
        if c.get("png") and os.path.exists(c["png"]) and "t0" in c:
            f += [F("MR36", m, "recompose") for m in O.card_visible_render(path, c["png"], c["t0"])]
    return f
def _card_box(c, W=720, H=1280):
    import numpy as np
    from PIL import Image
    if not (c.get("png") and os.path.exists(c["png"])): return None
    a = np.array(Image.open(c["png"]).convert("RGBA").resize((W, H)))[:, :, 3]; ys, xs = np.where(a > 40)
    return (xs.min(), ys.min(), xs.max(), ys.max()) if len(xs) else None
def c_cards_off_faces(path, spec, stage):
    import cv2, numpy as np
    det = cv2.FaceDetectorYN.create(os.path.join(REPO, "assets", "models", "face_detection_yunet_2023mar.onnx"), "", (720, 1280), 0.7); f = []
    for i, c in enumerate(spec.get("cards") or []):
        box = _card_box(c)
        if not box or "t0" not in c: continue
        for t in np.arange(c["t0"] + 0.05, c["t1"], 0.5):
            raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", path, "-frames:v", "1", "-vf", "scale=720:1280,format=bgr24", "-f", "rawvideo", "-"], capture_output=True).stdout
            if len(raw) != 720 * 1280 * 3: continue
            # sample the frame WITHOUT the card if a textless body exists (faces under an opaque card can't be seen)
            body = (spec.get("edit") or {}).get("body")
            if body and os.path.exists(body):
                raw2 = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", body, "-frames:v", "1", "-vf", "scale=720:1280,format=bgr24", "-f", "rawvideo", "-"], capture_output=True).stdout
                raw = raw2 if len(raw2) == 720 * 1280 * 3 else raw
            g = np.frombuffer(raw, np.uint8).reshape(1280, 720, 3).copy()
            faces = det.detect(g)[1]
            for (x, y, w, h) in ([] if faces is None else [tuple(int(v) for v in fc[:4]) for fc in faces]):
                if x < box[2] and x + w > box[0] and y < box[3] and y + h > box[1]:
                    f.append(F("MR38", f"card {i + 1} '{_txt(c)}' covers a face at {t:.1f}s", "recompose", dict(card=i, face=[int(x), int(y), int(w), int(h)], t=float(t)))); break
            if f and f[-1]["data"].get("card") == i: break
    return f
def _norm_words(t): return set(re.findall(r"[a-z0-9]+", (t or "").lower()))
def c_card_ocr(path, spec, stage):
    import numpy as np
    from PIL import Image
    f = []
    for i, c in enumerate(spec.get("cards") or []):
        box = _card_box(c)
        if not box or "t0" not in c: continue
        tmp = f"/tmp/mg_ocr_{os.getpid()}_{i}.png"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{c['t0'] + 0.2:.3f}", "-i", path, "-frames:v", "1", "-vf", "scale=720:1280", tmp], check=True)
        im = np.array(Image.open(tmp).convert("RGB")).astype(int)[max(box[1] - 6, 0):box[3] + 6, max(box[0] - 6, 0):box[2] + 6]
        m = ((im.min(2) > 215)).astype(np.uint8) * 255                  # white card fill -> black-on-white for tesseract
        Image.fromarray(255 - m).resize((m.shape[1] * 2, m.shape[0] * 2)).save(tmp)
        txt = subprocess.run(["tesseract", tmp, "-", "--psm", "6"], capture_output=True, text=True).stdout; os.remove(tmp)
        want = {w for w in _norm_words(_txt(c)) if len(w) > 2}; got = _norm_words(txt)
        hit = len(want & got) / max(len(want), 1)
        spec.setdefault("_hints", {}).setdefault("ocr", []).append(dict(card=_txt(c), ocr=txt.strip(), match=round(hit, 2)))
        if want and hit < 0.5: f.append(F("MR39", f"OCR of card {i + 1} reads {txt.strip()!r}, expected {_txt(c)!r}", "recompose"))
        from . import textcards as TC
        if len(TC.card_lines(_txt(c), c.get("scale", 1.0))) > 2: f.append(F("MR39", f"card '{_txt(c)}' wraps to > 2 rows", "recompose"))
    return f

# ---------- captions / publish ----------
def c_caption_say(path, spec, stage):
    c = spec.get("caption") or ""
    f = []
    if re.search(r"(?i)\bcomment(ing|s)?\b", c): f.append(F("MR40", "caption says 'Comment' (use SAY)", "caption"))
    if c and not re.search(r'\bSAY\s*["“]', c): f.append(F("MR40", 'caption has no SAY "<KEYWORD>"', "caption"))
    return f
def c_caption_approved(path, spec, stage):
    if not spec.get("approved_caption"): return [F("MR41", "no approved caption recorded for this post", None)]
    f = [] if (spec.get("caption") or "").strip() == spec["approved_caption"].strip() else [F("MR41", "caption differs from the approved caption", "caption")]
    ac = spec.get("approved_cards")
    if ac is not None and [_txt(x) for x in ac] != [_txt(x) for x in spec.get("cards") or []]: f.append(F("MR41", "cards differ from the approved card spec", "recompose"))
    return f
def past_caption_lines(page):
    out = set()
    for p in glob.glob(os.path.join(PUBLISH_LOG, "*.md")) + glob.glob(os.path.join(PUBLISH_LOG, "*.json")):
        t = open(p, encoding="utf-8", errors="ignore").read()
        if page and page.lower().replace(" ", "") not in t.lower().replace(" ", ""): continue
        for m in re.finditer(r"(?im)caption[^:\n]*:\s*(.+)$", t):
            for ln in re.split(r"\s/\s|\n", m.group(1)):
                ln = ln.strip().strip("'\"").strip()
                if len(ln) > 12 and not ln.startswith("#"): out.add(ln.lower())
    reg = json.load(open(REGISTRY)) if os.path.exists(REGISTRY) else {}
    for r in reg.values():
        if page in (r.get("posted_pages") or []): out |= {l.strip().lower() for l in (r.get("caption") or "").split("\n") if len(l.strip()) > 12 and not l.strip().startswith("#")}
    return out
def c_caption_fresh(path, spec, stage):
    seen = past_caption_lines(spec.get("page")); f = []
    for ln in (spec.get("caption") or "").split("\n"):
        if ln.strip().lower() in seen: f.append(F("MR42", f"caption line already posted on {spec.get('page')}: {ln.strip()[:60]}", "caption"))
    return f
def c_caption_style(path, spec, stage):
    from . import publish
    c = spec.get("caption") or ""
    return [F("MR43", "listing-style caption", "caption")] if c and publish.is_listing(c) else ([F("MR43", "empty caption", None)] if not c else [])
def c_publish_approval(path, spec, stage):
    a = spec.get("approval") or {}
    return [] if (a.get("by") == "Omar" and len((a.get("quote") or "").split()) >= 2) else [F("MR44", "no Omar approval/explicit ask (with his quote) for this post", None)]
def c_rules_registry(path, spec, stage):
    bad = [r["id"] for r in rules() if r["check"] in ("auto", "auto+manual") and r["fn"] not in CHECKS]
    return [F("MR47", f"rules without an implemented check: {bad}", None)] if bad else []

def c_glow_trail(path, spec, stage):
    """MR49 (Omar 10-21 8:14 PM): light trails barely visible; glow itself bright."""
    g = spec.get("glow")
    if not g:
        return [F("MR49", "glowing-light product without a declared glow spec (trail_decay/trail_opacity)", None)] if (spec.get("product") == "lumarein") else []
    out = []
    if float(g.get("trail_decay", 1)) > 0.3: out.append(F("MR49", f"trail decay {g.get('trail_decay')} > 0.3 (trail too long)", "recompose"))
    if float(g.get("trail_opacity", 1)) > 0.03: out.append(F("MR49", f"trail opacity {g.get('trail_opacity')} > 0.03 (trail too visible)", "recompose"))
    if re.search(r"long (motion[- ]blur )?(light )?trails|slow-shutter streak", " ".join(g.get("prompts", [])), re.I): out.append(F("MR49", "prompt asks for long light trails/streaks", "regen"))
    if not re.search(r"no (light )?trails", " ".join(g.get("prompts", [])), re.I): out.append(F("MR49", "prompts must say 'no light trails, no motion streaks, no long-exposure effect'", "regen"))
    if not g.get("bloom", True): out.append(F("MR49", "glow bloom disabled - glow must stay bright", "recompose"))
    return out

def c_problem_solution(path, spec, stage):
    """MR50 (Omar 10-21 8:50 PM): 'The problem' card is followed by 'The solution', never 'The result'."""
    ts = [_txt(c).strip().lower() for c in spec.get("cards") or []]
    out = []
    for i, t in enumerate(ts):
        if re.search(r"\bthe problem\b", t) and i + 1 < len(ts) and re.search(r"\bthe result\b", ts[i + 1]):
            out.append(F("MR50", f"'The problem' card followed by '{ts[i+1]}' - second card must be 'The solution'", "recompose"))
    return out

CHECKS = {k[2:]: v for k, v in globals().items() if k.startswith("c_") and callable(v)}
STAGES = ("final", "deliver", "publish")

def applicable(r, kind, stage):
    a = r["applies"]
    if a == "publish": return stage == "publish" and kind == "video"
    return a == "all" or a == kind

def run(path, spec=None, stage="final"):
    """One pass: returns dict(status, failures, manual_missing, checked)."""
    spec = spec if spec is not None else load_spec(path); kind = spec.get("kind") or kind_of(path)
    fails, missing, checked, seen = [], [], [], set()
    for c in spec.get("cards") or []:   # repo-relative card layers; a final video's cards MUST have their layer for pixel checks
        if c.get("png") and not os.path.isabs(c["png"]): c["png"] = os.path.join(REPO, c["png"])
        if kind == "video" and not (c.get("png") and os.path.exists(c["png"])):
            fails.append(F("MR35", f"card '{_txt(c)}' has no rendered layer to verify (OCR/emoji/faces/visibility)", "recompose"))
    for r in rules():
        if not applicable(r, kind, stage) or r["check"] in ("process", "superseded"): continue
        if r["check"] in ("auto", "auto+manual") and r["fn"] not in seen:
            seen.add(r["fn"])
            try: fails += CHECKS[r["fn"]](path, spec, stage)
            except Exception as e: fails.append(F(r["id"], f"check {r['fn']} crashed: {e!r}", None))
            checked.append(r["id"])
        if r["check"] in ("manual", "auto+manual"):
            cf = (spec.get("confirm") or {}).get(r["id"]) or {}
            if not (cf.get("by") and len((cf.get("note") or "").split()) >= 4 and cf.get("sha256") in (None, sha(path)) if os.path.exists(path) else False):
                missing.append(dict(rule=r["id"], rule_text=r["rule"]))
    status = "PASS" if not fails and not missing else ("FAIL" if fails else "NEEDS_REVIEW")
    return dict(status=status, failures=fails, manual_missing=missing, checked=checked, hints=spec.get("_hints", {}))

# ======================= AUTO-FIX =======================
def fix_sanitize(path, spec):
    from . import deliver
    ext = os.path.splitext(path)[1].lower(); tmp = path + ".mgfix" + ext
    if ext in VIDEO_EXT + IMAGE_EXT: deliver.sanitize(path, tmp)
    else:
        shutil.copyfile(path, tmp); subprocess.run(["exiftool", "-q", "-all=", "-overwrite_original", tmp], capture_output=True)
    os.replace(tmp, path); return True

def repair_cards(spec, fails):
    """Free text-level fixes on spec['cards'] (no footage): count, words, VS position, Get yours, non-Apple emoji,
    timing snap to cuts, face-avoid y shift. Returns True if anything changed."""
    from . import card_count, emoji_gate
    cs = spec.get("cards") or []; changed = False; rs = {f["rule"] for f in fails}
    for c in cs:
        t = _txt(c); t2 = GET_YOURS.sub("", t)
        t2 = "".join(ch for ch in t2 if not (emoji_gate.EMOJI_RE.match(ch) and emoji_gate.gate_text(ch)))
        if _words(t2) > CARD_WORD_MAX:
            toks = t2.split(); keep, n = [], 0
            for tok in toks:
                w = _words(tok)
                if n + w > CARD_WORD_MAX and w: continue
                keep.append(tok); n += w
            t2 = " ".join(keep)
        t2 = re.sub(r"\s{2,}", " ", t2).strip()
        if t2 != t: c["text"] = t2; changed = True
    for _ in range(2):   # VS only on a middle card; then the D188 card budget (re-run: removing VS can change what is allowed)
        for i, c in enumerate(cs):
            if VS_RE.search(_txt(c)) and not (len(cs) >= 3 and 0 < i < len(cs) - 1):
                c["text"] = re.sub(r"\s{2,}", " ", VS_RE.sub("", c["text"])).strip(); changed = True
        if not card_count.allowed(cs, _fmt(spec))[0]:
            last = cs[-1]; keep = [cs[0]] + ([last] if card_count.allowed([cs[0], last], _fmt(spec))[0] else [])
            if len(keep) == 1: keep[0]["t1"] = max(c.get("t1", 0) for c in cs)
            else: keep[0]["t1"] = last["t0"]
            spec["cards"] = cs = keep; changed = True
    starts = sorted(s["t0"] for s in spec.get("shots") or [])
    if starts and "MR36" in rs:
        for i, c in enumerate(cs):
            if "t0" in c:
                n = min(starts, key=lambda s: abs(s - c["t0"]))
                if abs(n - c["t0"]) > 1e-3: c["t0"] = n; changed = True
        for a, b in zip(cs, cs[1:]): a["t1"] = b["t0"]
        for c in cs:
            if c.get("t1", 0) - c.get("t0", 0) < 1.0:
                nxt = [s for s in starts if s >= c["t0"] + 1.0]; c["t1"] = nxt[0] if nxt else c["t1"]; changed = True
        for c in cs: c.pop("min_contrast_bump", None)
    need = {f["data"].get("card") for f in fails if f["rule"] == "MR38"}
    need |= {i for i, c in enumerate(cs) for f in fails if f["rule"] == "MR36" and "not visible" in f["msg"] and f"at {c.get('t0')}s" in f["msg"]}
    for i in sorted(x for x in need if x is not None and x < len(cs)):
        y = best_y(spec, cs[i])
        if y is not None and y != cs[i].get("y"): cs[i]["y"] = y; changed = True
    return changed

Y_CANDIDATES = (0.69, 0.62, 0.76, 0.82, 0.55, 0.30, 0.22, 0.16)   # Omar's CapCut hook y ~0.69 first, then nearest
def best_y(spec, c, min_contrast=60.0):
    """Free fix for MR36 (card hard to read) / MR38 (card on a face): pick the y (closest to Omar's 0.69) where the card
    sits on no face and reads >= min_contrast over the textless body at every sampled moment of its span."""
    import numpy as np, cv2
    from . import textcards as TC
    e = spec.get("edit") or {}; body = e.get("body")
    if not (body and os.path.exists(body)): return None
    det = cv2.FaceDetectorYN.create(os.path.join(REPO, "assets", "models", "face_detection_yunet_2023mar.onnx"), "", (720, 1280), 0.7)
    frames = []
    for t in list(np.arange(c["t0"] + 1 / 30, c["t1"], 0.5)):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", body, "-frames:v", "1", "-vf", "scale=720:1280,format=bgr24", "-f", "rawvideo", "-"], capture_output=True).stdout
        if len(raw) == 720 * 1280 * 3:
            fr = np.frombuffer(raw, np.uint8).reshape(1280, 720, 3).copy(); fc = det.detect(fr)[1]
            frames.append((fr.mean(2), [] if fc is None else [tuple(int(v) for v in x[:4]) for x in fc]))
    best = None
    for y in Y_CANDIDATES:
        L = np.array(TC.render_card(_txt(c), 720, 1280, scale=c.get("scale", 1.0), y=y).convert("RGBA")); a = L[:, :, 3]; lum = L[:, :, :3].mean(2)
        m = a > 128; ys, xs = np.where(m)
        if not len(xs): continue
        bx = (xs.min(), ys.min(), xs.max(), ys.max()); fill = (a > 200) & (lum > 200); fill = fill if fill.any() else m
        box = np.zeros_like(m); box[max(bx[1] - 20, 0):bx[3] + 21, max(bx[0] - 20, 0):bx[2] + 21] = True; bg = box & (a < 10)
        ok_face = all(not (x < bx[2] and x + w > bx[0] and yy < bx[3] and yy + h > bx[1]) for _, fc in frames for (x, yy, w, h) in fc)
        con = min((255.0 - g[bg].mean()) if fill.any() else 0 for g, _ in frames) if frames else 0   # card fill is white (~255)
        score = (ok_face, con >= min_contrast, con)
        if ok_face and con >= min_contrast: return y
        if best is None or score > best[0]: best = (score, y)
    return best[1] if best else None
    return changed

def recompose(path, spec):
    """Free re-edit: textless body + continuous song from its verified section + Apple-emoji cards at the spec positions.
    Writes to path (atomic) and sanitizes. Needs spec.edit.body and spec.song.path."""
    from . import emoji_gate, textcards as TC, deliver
    e = spec.get("edit") or {}; s = spec.get("song") or {}
    body = e.get("body"); W, H = e.get("W", 720), e.get("H", 1280)
    if not (body and os.path.exists(body) and s.get("path")): return False
    if s.get("recreate_of"):
        from . import original_song
        v = original_song.verified(s["recreate_of"]["slug"], s["recreate_of"]["reel_id"])
        if v: s["key"], s["in_s"] = v["song_key"], v["in_point_s"]; s["start_t"] = 0; s["loops"] = False
    dur = _dur(body); sp = s["path"] if os.path.isabs(s["path"]) else os.path.join(REPO, s["path"])
    ins = ["-i", body, "-ss", str(s.get("in_s", 0)), "-i", sp]; f = []; last = "0:v"
    work = os.path.join(os.path.dirname(path), ".mg_" + os.path.splitext(os.path.basename(path))[0]); os.makedirs(work, exist_ok=True)
    for j, c in enumerate(spec.get("cards") or []):
        sc = TC.fit_card(_txt(c), c.get("scale_max", 1.0)); c["scale"] = sc
        png = os.path.join(work, f"card{j}.png")
        TC.render_card(_txt(c), W, H, scale=sc, y=c.get("y")).save(png)
        if c.get("y") is None: emoji_gate.gate_card_png(_txt(c), png, W, H, sc)
        c["png"] = png; ins += ["-loop", "1", "-t", f"{dur:.3f}", "-i", png]
        f.append(f"[{last}][{j + 2}:v]overlay=0:0:enable='between(t,{c['t0']:.3f},{c['t1'] - 0.001:.3f})'[c{j}]"); last = f"c{j}"
    f.append(f"[1:a]atrim=0:{dur:.3f},afade=t=out:st={max(dur - 0.4, 0):.3f}:d=0.4[m];[0:a]volume={e.get('body_gain', 0.22)}[n];[m][n]amix=inputs=2:normalize=0[au]")
    if last == "0:v": f.insert(0, "[0:v]null[v0]"); last = "v0"
    tmp = path + ".mgfix.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", ";".join(f), "-map", f"[{last}]", "-map", "[au]", "-t", f"{dur:.3f}",
                    "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-map_metadata", "-1", "-map_chapters", "-1",
                    "-fflags", "+bitexact", "-flags:v", "+bitexact", "-flags:a", "+bitexact", "-metadata", "encoder=", "-movflags", "+faststart", tmp], check=True)
    clean = path + ".mgclean.mp4"; deliver.sanitize(tmp, clean); os.remove(tmp); os.replace(clean, path); return True

def fix_caption(spec, fails):
    from . import publish
    c = spec.get("caption") or ""; o = c; kw = spec.get("say_keyword") or "LINK"
    if any(f["rule"] == "MR41" for f in fails) and spec.get("approved_caption"): c = spec["approved_caption"]
    c = re.sub(r"(?i)\bcomment(ing|s)?\s+([\"“]?)(\w+)", lambda m: f'SAY "{m.group(3).upper()}"', c)
    c = re.sub(r"(?i)\s*get\s+yours[^\n]*", "", c)
    seen = past_caption_lines(spec.get("page")) if spec.get("page") else set()
    c = "\n".join(l for l in c.split("\n") if l.strip().lower() not in seen) or c
    c = publish.ensure_say(c, kw); spec["caption"] = c; return c != o

def ensure(path, spec=None, stage="final", max_iters=MAX_ITERS, log=print):
    """Check -> fix -> re-check loop. Free fixes first; footage regen only via spec.regen.runner within the approved cap.
    Writes the PASS report on success. Returns the last run() dict plus history."""
    spec = spec if spec is not None else load_spec(path); hist = []
    regen = spec.get("regen") or {}
    for it in range(max_iters):
        r = run(path, spec, stage); hist.append(dict(iter=it, status=r["status"], failures=[(f["rule"], f["msg"]) for f in r["failures"]]))
        if r["status"] != "FAIL":
            break
        fixes = {f["fix"] for f in r["failures"]}; did = []
        if "sanitize" in fixes and fix_sanitize(path, spec): did.append("sanitize")
        if "caption" in fixes and fix_caption(spec, r["failures"]): did.append("caption")
        if "recompose" in fixes:
            repair_cards(spec, r["failures"])
            if recompose(path, spec): did.append("recompose")
        if did: log(f"[master_gate] iter {it}: free fixes {did}"); continue
        if "regen" in fixes:
            cost = float(regen.get("cost_per_clip", 28)); left = float(regen.get("cap_remaining", 0))
            if regen.get("runner") and left >= cost and regen.get("approved_by") == "Omar":
                mod, fn = regen["runner"].rsplit(":", 1)
                spent = __import__(mod, fromlist=[fn]).__dict__[fn](path, spec, [f for f in r["failures"] if f["fix"] == "regen"])
                regen["cap_remaining"] = left - float(spent or cost); spec["regen"] = regen; did.append(f"regen ({spent} cr)")
                log(f"[master_gate] iter {it}: {did}"); continue
            r["status"] = "NEEDS_REGEN_WITHIN_CAP"
            r["regen_plan"] = dict(failures=[f for f in r["failures"] if f["fix"] == "regen"], cost_per_clip=cost, cap_remaining=left)
        break
    r["history"] = hist
    if r["status"] == "PASS": write_report(path, spec, r, stage)
    else: write_report(path, spec, r, stage, passed=False)
    return r

def report_paths(path): return path + ".PASS.json", path + ".PASS.md"
def write_report(path, spec, r, stage, passed=True):
    pj, pm = report_paths(path)
    if not passed:
        pj, pm = path + ".GATE_FAIL.json", path + ".GATE_FAIL.md"
        for p in report_paths(path):
            if os.path.exists(p): os.remove(p)
    rep = dict(file=os.path.relpath(path, REPO) if path.startswith(REPO) else path, sha256=sha(path), stage=stage, status=r["status"],
               at=now_pt(), rules_version=sha(RULES_JSON)[:12], auto_checked=r["checked"],
               manual_confirmed={k: v for k, v in (spec.get("confirm") or {}).items()}, failures=r["failures"],
               manual_missing=r["manual_missing"], hints=r.get("hints"), history=r.get("history"), regen_plan=r.get("regen_plan"),
               cards=[dict(text=_txt(c), t0=c.get("t0"), t1=c.get("t1"), y=c.get("y")) for c in spec.get("cards") or []],
               caption=spec.get("caption"), page=spec.get("page"))
    json.dump(rep, open(pj, "w"), indent=1, ensure_ascii=False, default=str)
    md = [f"# Master gate {r['status']} - {os.path.basename(path)}", f"- at {rep['at']}, stage `{stage}`, sha256 `{rep['sha256'][:16]}...`, rules {rep['rules_version']}",
          f"- auto-checked rules: {', '.join(r['checked'])}", f"- reviewer-confirmed: {', '.join(rep['manual_confirmed']) or '-'}",
          f"- cards: {[c['text'] for c in rep['cards']]}", f"- fix loop: {len(r.get('history') or [])} pass(es)"]
    md += [f"- FAIL {f['rule']}: {f['msg']}" for f in r["failures"]] + [f"- NEEDS REVIEW {m['rule']}: {m['rule_text']}" for m in r["manual_missing"]]
    open(pm, "w").write("\n".join(md) + "\n")
    if passed:
        for p in (path + ".GATE_FAIL.json", path + ".GATE_FAIL.md"):
            if os.path.exists(p): os.remove(p)

def require(path, stage="deliver", spec=None):
    """Hard gate used by deliver.stage / publish.prepare / finalize. Images and other files: auto-fix metadata and pass
    on the spot (MR01). Videos: need a PASS report bound to this exact sha256 (and stage 'publish' re-runs publish rules)."""
    if os.environ.get("HOOKFORGE_GATE_TEST_BYPASS") == "1" and os.path.abspath(path).startswith(("/tmp", "/var/folders")): return True
    kind = kind_of(path)
    if kind != "video":
        r = ensure(path, spec if spec is not None else load_spec(path), stage, log=lambda *_: None)
        if r["status"] != "PASS": raise GateRefused(f"{path}: master gate {r['status']}: {[f['msg'] for f in r['failures']] + [m['rule'] for m in r['manual_missing']]}")
        return True
    pj = report_paths(path)[0]
    if not os.path.exists(pj): raise GateRefused(f"{path}: no master-gate PASS report - run master_gate.ensure(path, spec) first (D191)")
    rep = json.load(open(pj))
    if rep.get("status") != "PASS" or rep.get("sha256") != sha(path): raise GateRefused(f"{path}: PASS report is stale or not PASS (file changed since the gate) (D191)")
    if stage == "publish":
        sp = spec if spec is not None else load_spec(path)
        r = ensure(path, sp, "publish", log=lambda *_: None)
        if r["status"] != "PASS": raise GateRefused(f"{path}: publish gate {r['status']}: {[f['msg'] for f in r['failures']] + [m['rule'] for m in r['manual_missing']]}")
    return True

def finalize(draft, final, spec, stage="final"):
    """The render command's last step: the gate (with its fix loop) runs on the draft; only a PASS is promoted to `final`."""
    r = ensure(draft, spec, stage)
    if r["status"] != "PASS": raise GateRefused(f"{draft}: {r['status']} - not promoted to final")
    shutil.copyfile(draft, final); json.dump(spec, open(final + ".gate.json", "w"), indent=1, ensure_ascii=False, default=str)
    write_report(final, spec, run(final, spec, stage) | dict(history=r["history"]), stage)
    return final

PLAN_FNS = ("gen_packing", "gen_len", "gen_models", "frame_refs", "spend_cap", "realism_suffix", "active_product", "hook_plan",
            "count321", "recreation_song", "no_phonk", "card_count", "card_words", "vs_position", "no_get_yours")
def pre_render(spec):
    """Render refuses to start unless the plan-level rules pass (card text/count/VS/emoji text, gens, hook, song, cap).
    Free text fixes are applied to the spec first (repair_cards / fix_caption), then re-checked."""
    for _ in range(3):
        fails = [f for fn in PLAN_FNS for f in CHECKS[fn](None, spec, "final")]
        txt = [f for f in fails if f["fix"] in ("recompose", "caption")]
        if not txt: break
        repair_cards(spec, txt)
        if any(f["fix"] == "caption" for f in txt): fix_caption(spec, txt)
    fails = [f for fn in PLAN_FNS for f in CHECKS[fn](None, spec, "final")]
    if fails: raise GateRefused("pre-render gate: " + "; ".join(f"{f['rule']} {f['msg']}" for f in fails))
    return spec

def register(path, video_id, page=None, caption=None, posted=False):
    """Footage registry for MR18/MR19. Call with posted=True right after a post goes live."""
    reg = json.load(open(REGISTRY)) if os.path.exists(REGISTRY) else {}
    r = reg.setdefault(video_id, dict(path=os.path.abspath(path), sha256=sha(path), posted_pages=[], caption=caption))
    if posted and page and page not in r["posted_pages"]: r["posted_pages"].append(page)
    if caption: r["caption"] = caption
    json.dump(reg, open(REGISTRY, "w"), indent=1, ensure_ascii=False); return r

if __name__ == "__main__":   # python3 -m hookforge.master_gate <file> [stage]
    import sys
    p = sys.argv[1]; r = ensure(p, stage=sys.argv[2] if len(sys.argv) > 2 else "final")
    print(json.dumps(dict(status=r["status"], failures=r["failures"], manual_missing=[m["rule"] for m in r["manual_missing"]]), indent=1, ensure_ascii=False, default=str))
    sys.exit(0 if r["status"] == "PASS" else 2)
