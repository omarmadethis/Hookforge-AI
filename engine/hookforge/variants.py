"""Per-page originality (D41). One master plan -> N page variants that are original enough to avoid Meta's
duplicate / unoriginal-content demotion. Evidence: BH-01 posted as an IDENTICAL file on IG got 2.6K vs 61.3K on FB
(corpus dup_note); repost/re-shoot of the 17.4M IKEA reel got 755K. Rules:
  - NEVER reuse a generated clip or a rendered file across pages (fresh gens per page; hashes logged).
  - Each variant changes >= 4 of 7 axes: hook line, start-frame scene (subject/setting/props), shot order of
    interchangeable body shots, song or song offset, text card wording/emoji, caption, edit rhythm (+/- 0.2-0.4 s).
  - Similarity score (0-1) vs every other variant in the same variant_family must be <= MAX_SIM.
Costs: each page variant is a full generation (budget CREDIT_BUDGET_VARIANT=100 when the hook is re-used as a
recreate with a different scene; full 175 otherwise) - estimate printed, generation gated by credit approval.
"""
import copy, hashlib, itertools, random
from .format_defaults import FORMATS
from . import music

MAX_SIM = 0.45
AXES = ["hook", "scene", "order", "music", "cards", "caption", "rhythm"]

def _jac(a, b):
    A, B = set(a.lower().split()), set(b.lower().split()); return len(A & B) / max(1, len(A | B))

def similarity(p, q):
    s = dict(hook=_jac(p["hook"]["text"], q["hook"]["text"]), scene=float(p["setting"] == q["setting"] and p.get("subject") == q.get("subject")),
             order=float([x["code"] for x in p["shots"]] == [x["code"] for x in q["shots"]]),
             music=float((p["music"]["pick"] or {}).get("song") == (q["music"]["pick"] or {}).get("song") and abs(((p["music"]["pick"] or {}).get("offset_s") or 0) - ((q["music"]["pick"] or {}).get("offset_s") or 0)) < 3),
             cards=_jac(" ".join(c["text"] for c in p["text_cards"]), " ".join(c["text"] for c in q["text_cards"])),
             caption=_jac(p["caption"]["text"], q["caption"]["text"]), rhythm=float(abs(p["duration"] - q["duration"]) < 0.15))
    return round(sum(s.values()) / len(s), 3), s

def make_variants(master, profile, pages, seed=0):
    rng = random.Random(seed); F = FORMATS[master["brief"]["format"]]
    hooks = [h for h in profile["proven_hooks"] if h["format"] == master["brief"]["format"]]
    hook_pool = [dict(text=h["hook"], tag="P", why=f"own {h['views']:,}") for h in hooks] + [dict(text=h[0], tag=h[1], why=h[2]) for h in F["hook_lines"] if h[1] in ("P", "F")]
    settings = profile["settings"]; caps = profile["proven_captions"] or [dict(caption=c, views=0) for c in F["captions"]]
    tracks, _ = music.select(profile, master["brief"]["format"], master["fit"]["video_energy"], "core", n=5)
    out = []
    for i, page in enumerate(pages):
        v = copy.deepcopy(master); v["page"] = page["code"]; changed = []
        if i == 0: out.append(v); continue
        used = {x["hook"]["text"] for x in out}
        fresh = [x for x in hook_pool if x["text"] not in used]
        h = fresh[0] if fresh else (hook_pool[i % len(hook_pool)] if hook_pool else master["hook"])
        if h["text"] != master["hook"]["text"]: v["hook"] = h; changed.append("hook")
        for c in v["text_cards"]:
            if c["text"] == master["hook"]["text"] or c["t"] == 0: c["text"] = h["text"]
        v["setting"] = settings[i % len(settings)]; v["subject"] = f"variant cast {i}"; changed.append("scene")
        if tracks: 
            t = tracks[i % len(tracks)]; t = dict(t, offset_s=(t.get("offset_s") or 0) + (0 if t["song"] != (master["music"]["pick"] or {}).get("song") else 4.0 * i))
            v["music"]["pick"] = t; changed.append("music")
        v["caption"] = dict(text=caps[i % len(caps)]["caption"], why="proven caption rotation"); changed.append("caption")
        sh = v["shots"]; 
        if len(sh) > 4: sh[2], sh[3] = sh[3], sh[2]; changed.append("order")
        v["duration"] = round(master["duration"] + rng.choice([-0.3, -0.2, 0.2, 0.3]), 2); changed.append("rhythm")
        v["variant_axes_changed"] = changed; v["fresh_generation_required"] = True
        out.append(v)
    report = []
    for a, b in itertools.combinations(range(len(out)), 2):
        s, parts = similarity(out[a], out[b]); report.append(dict(a=out[a]["page"], b=out[b]["page"], sim=s, ok=s <= MAX_SIM, parts=parts))
    return out, report

def file_hash(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""): h.update(ch)
    return h.hexdigest()
