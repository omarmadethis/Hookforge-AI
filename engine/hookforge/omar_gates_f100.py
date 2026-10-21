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
    """Render check (D182): grab the final frame 1 frame after the card start. The card's white FILL pixels
    (alpha>200, luma>200) must be >= min_contrast brighter than the background just around the card box
    (alpha<10, box +20 px). Fixed 2026-10-21: the old version averaged fill + black stroke together, which
    under-read readable white/black-stroke cards on mid-bright backgrounds."""
    from PIL import Image
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t0 + 1.0 / FPS:.3f}", "-i", path, "-frames:v", "1",
                          "-vf", "scale=1080:1920,format=gray", "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(1920, 1080).astype(float)
    c = np.array(Image.open(card_png).convert("RGBA").resize((1080, 1920))); a = c[:, :, 3]; L = c[:, :, :3].mean(2)
    m = a > 128
    if not m.any(): return [f"BLOCK card image {card_png} is empty (D182)"]
    fill = (a > 200) & (L > 200)
    if not fill.any(): fill = m
    ys, xs = np.where(m); box = np.zeros_like(m)
    box[max(ys.min() - 20, 0):ys.max() + 21, max(xs.min() - 20, 0):xs.max() + 21] = True
    bg = box & (a < 10)
    inside = fr[fill].mean(); around = fr[bg].mean() if bg.any() else 0
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

# D187 / F105: Omar's 3-2-1 countdown spec
def count321_gate(h):
    """Applies when hook format == '321-prop-reveal'. Needs a hook['count321'] spec."""
    if h.get("format") != "321-prop-reveal": return []
    c = h.get("count321") or {}; f = []
    if not (c.get("covered_cue_at_0") or "").strip(): f.append("BLOCK 3-2-1: covered product cue not visible at 0 s (D187)")
    if not c.get("all_count"): f.append("BLOCK 3-2-1: everyone in the shot must count '3, 2, 1' together (D187)")
    if "see how it comes out" not in (c.get("reveal_line") or "").lower(): f.append("BLOCK 3-2-1: someone must say 'let's see how it comes out' on the reveal (D187)")
    if c.get("product_full_in_hook", True) or c.get("reveal_flash_s", 99) > 0.5: f.append("BLOCK 3-2-1: reveal must be a split second (<=0.5 s); full payoff saved for the afters (D187)")
    if abs(c.get("vo_over_song_lu", 0) - 8.0) > 2.0 or not c.get("song_from_frame0"): f.append("BLOCK 3-2-1: count voices ~+8 LU over the song, song from frame 0 (D187)")
    return f

_hook_gate_base = hook_gate
def hook_gate(h): return _hook_gate_base(h) + count321_gate(h)
