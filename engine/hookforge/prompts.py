"""Prompt builder (D32/D33). Fills format + world-adaptation templates with the product profile, packs body shots
two per 4 s gen with a HARD CUT, adds the US flag, sanitises casting, and appends the iPhone 12 suffix to EVERY prompt.
"""
import re
from .config import ensure_suffix, IPHONE12_SUFFIX, sanitize_casting, casting_violations, STILL_SUFFIX

FLAG = "A small American flag is visible in the background."

class _D(dict):
    def __missing__(self, k): return "{" + k + "}"

def fill(t, ctx): return t.format_map(_D(ctx)) if t else t

def with_flag(p):
    return p if re.search(r"american flag|us flag|u\.s\. flag", p, re.I) else p.rstrip() + " " + FLAG

def with_cues(p, cues):
    if not cues: return p
    add = " Background details: " + "; ".join(cues) + "."
    m = re.search(r"\s*(Natural sound only:|No background music)", p)
    return p[:m.start()] + add + " " + p[m.start():].lstrip() if m else p.rstrip() + add

def finish(p, cues=None):
    p = sanitize_casting(with_flag(with_cues(p, cues)))
    return ensure_suffix(silent(p))

SILENT = NATURAL = "Natural ambient sound only: real voices and action sounds that match what happens on screen, no added sound effects, no music."   # D63 (Omar 2026-10-19 PT): keep natural clip sound, ban fake SFX
OLD_SILENT = "Silent clip: no dialogue, no voices, no sound effects, no music."
def silent(p):
    """D63: natural ambient sound only (real voices, some cheering/gasps, action sounds); never added SFX/whooshes/cartoon sounds/an inserted YAY/music."""
    p = p.replace(OLD_SILENT, "")
    p = re.sub(r"Natural sound only:[^.]*\.\s*", "", p, flags=re.I)
    p = re.sub(r"No background music,\s*no text", "No text", p, flags=re.I)
    p = re.sub(r"\b(yells?|shouts?|screams?)\s+\"?(yay|yeah)!?\"?", "reacts", p, flags=re.I)
    return p if SILENT in p else re.sub(r"(\n\n|$)", " " + SILENT + r"\1", p.rstrip(), count=1) if "\n\n" not in p else p.replace("\n\n", " " + SILENT + "\n\n", 1)

def still(p, cues=None):
    p = p.strip()
    if not p.lower().startswith("iphone photo"): p = "iPhone photo of " + p[0].lower() + p[1:]
    if cues: p = p.replace(STILL_SUFFIX, "").rstrip(". ") + ". Background details: " + "; ".join(cues) + ". " + STILL_SUFFIX
    if STILL_SUFFIX not in p: p = p.rstrip(". ") + ". " + STILL_SUFFIX
    return finish(p)

def body_gen(shots, cut, ctx, sounds, cues=None):
    (c1, d1, t1), (c2, d2, t2) = shots
    p = (f"Handheld iPhone video, real-time normal speed, starting from the start frame. Keep {ctx.get('subject','the same people')} consistent throughout, {ctx.get('body_setting','')}. Shot 1 (0-{cut:g}s, {c1}): {fill(t1, ctx)}. "
         f"HARD CUT at {cut:g}s, no transition. Shot 2 ({cut:g}-4s, {c2}): {fill(t2, ctx)}. The product always looks exactly like <<<image_1>>> and stays identical in both shots (same parts, same design); bags and boxes open naturally, plugs and fit look real, store shelves look lived-in rather than perfect. "
         f"Natural sound only: {sounds}. No background music, no text, no captions, no logos.")
    return finish(p, cues)

def body_still(shot_desc, ctx, setting, cues=None, unlit=False):
    """unlit=True (D60): start frame of a pre-reveal shot (BOX/INSTALL/ACT before the activation_result shot) of an activation product -
    describe the product switched OFF instead of appending the lit product_look, which spoiled the reveal (mg-tvn-001 B1)."""
    prod = (f"the {ctx.get('product','product')} from the first image installed/held but still switched OFF: dark, no colours, pictures or glow yet (the reveal comes later)"
            if unlit else f"the {ctx.get('product_look','product')} from the first image clearly visible")
    return still(cues=cues, p=f"iPhone photo {ctx.get('body_setting', 'in ' + setting)}: {ctx.get('subject', 'a person')}, {fill(shot_desc, ctx)}, {prod}. Top 20% clear for text. Sharp, clean, realistic phone photo.")

def check(prompt, kind):
    probs = []
    if not prompt.rstrip().endswith(IPHONE12_SUFFIX.strip()): probs.append(f"{kind}: missing iPhone 12 suffix (D32)")
    if not re.search(r"american flag", prompt, re.I): probs.append(f"{kind}: no US flag")
    if casting_violations(prompt): probs.append(f"{kind}: casting violation")
    if re.search(r"\{\w+\}", prompt): probs.append(f"{kind}: unfilled placeholder {re.findall(r'{\w+}', prompt)[:3]}")
    if kind.startswith("body") and "HARD CUT" not in prompt: probs.append(f"{kind}: no HARD CUT")
    return probs
