"""Omar 2026-10-21 ~1:29 AM PT rejections of TrumpGlow A2/B2 -> permanent gates (D182-D186, F100-F104).
All are BLOCK unless noted. Plan-level checks run before any spend; render-level checks run on finals."""
import json, os, subprocess
from .config import REPO
FPS = 30.0
PAYOFF_MAX_SHOT_S = 1.5
PAYOFF_MIN_CUTS = 2

def proven_formats():
    return {x["slug"] for x in json.load(open(os.path.join(REPO, "formats", "index.json")))}

# D182 / F100: every card visible from the first frame of its shot
def card_timing(shots, cards, tol=1.0 / FPS):
    """shots: [{gen,t0,t1}], cards: [{text,t0,t1}]. Each card must start exactly on a shot's first frame."""
    f = []
    starts = [s["t0"] for s in shots]
    for c in cards:
        if not any(abs(c["t0"] - t) <= tol for t in starts):
            f.append(f"BLOCK card '{c['text']}' starts at {c['t0']}s, not on a shot's first frame (D182)")
        if c["t1"] - c["t0"] < 1.0: f.append(f"BLOCK card '{c['text']}' on screen < 1.0 s (D182)")
    return f

def card_visible_render(path, card_png, t0, min_contrast=60.0):
    """Render check: grab the final frame 1 frame after the card start; text pixels (card alpha>128) must be
    visibly brighter than the surrounding pixels of the same box."""
    from PIL import Image
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t0 + 1.0 / FPS:.3f}", "-i", path, "-frames:v", "1",
                          "-vf", "scale=1080:1920,format=gray", "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(1920, 1080).astype(float)
    a = np.array(Image.open(card_png).convert("RGBA").resize((1080, 1920)))[:, :, 3]
    m = a > 128
    if not m.any(): return [f"BLOCK card image {card_png} is empty (D182)"]
    ys, xs = np.where(m); box = np.zeros_like(m); box[ys.min():ys.max() + 1, xs.min():xs.max() + 1] = True
    inside = fr[m].mean(); around = fr[box & ~m].mean() if (box & ~m).any() else 0
    return [] if inside - around >= min_contrast else [f"BLOCK card not visible at {t0}s (text {inside:.0f} vs bg {around:.0f}) (D182)"]

# D183 / F101: card copy coherence
def card_coherence(cards):
    """Each card needs 'why': one line saying why the words literally match what is on screen, naming a thing in 'shows'."""
    f = []
    for c in cards:
        why, shows = (c.get("why") or "").strip(), (c.get("shows") or "").lower()
        if len(why.split()) < 6: f.append(f"BLOCK card '{c['text']}' has no coherence line (D183)"); continue
        if not shows or not any(w in why.lower() for w in shows.split() if len(w) > 3):
            f.append(f"BLOCK card '{c['text']}' coherence line doesn't reference what the shot shows (D183)")
    return f

# D184 + D186 / F102 + F104: hook = proven format OR scroll-stopper, with action + conflict in the first second
def hook_gate(h):
    f = []
    fmt, ss = h.get("format"), h.get("scroll_stopper")
    if fmt and fmt not in proven_formats(): f.append(f"BLOCK hook format '{fmt}' not in formats/index.json (D186)")
    if not fmt and not (ss and len((h.get("why_relevant") or "").split()) >= 6):
        f.append("BLOCK hook is neither a proven format nor a scroll-stopper with a relevance line (D186)")
    if not (h.get("first_second_action") or "").strip(): f.append("BLOCK hook has no action in the first second (D184)")
    if not (h.get("conflict") or "").strip(): f.append("BLOCK hook has no point of conflict (D184)")
    if h.get("conflict_t_s", 0) > 1.0: f.append(f"BLOCK conflict lands at {h['conflict_t_s']}s > 1.0 s (D184)")
    return f

# D185 / F103: payoff = >= 2 hard cuts, no shot over 1.5 s
def payoff_gate(shots):
    p = [s for s in shots if s.get("role") in ("payoff", "reveal", "after")]
    f = []
    if len(p) - 1 < PAYOFF_MIN_CUTS: f.append(f"BLOCK payoff has {max(len(p) - 1, 0)} cuts < {PAYOFF_MIN_CUTS} (D185)")
    for s in p:
        if s["t1"] - s["t0"] > PAYOFF_MAX_SHOT_S + 0.02: f.append(f"BLOCK payoff shot {s['gen']} {s['t1'] - s['t0']:.2f}s > {PAYOFF_MAX_SHOT_S}s (D185)")
    for a, b in zip(p, p[1:]):
        if a["gen"] == b["gen"]: f.append(f"BLOCK payoff cut {a['gen']}->{b['gen']} is a same-take splice (F62)")
    return f

def plan_gates(plan):
    out = hook_gate(plan["hook"]) + card_timing(plan["shots"], plan["cards"]) + card_coherence(plan["cards"]) + payoff_gate(plan["shots"])
    return out
