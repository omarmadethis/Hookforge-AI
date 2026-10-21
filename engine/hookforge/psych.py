"""Psych codebook scorer (psychology/psych_codebook.csv, PS01-PS19). ADVISORY per D35. PS02 (covered reveal) is an advisory cue/timing check, never a block (D52; style re-code 22:09 PT).
Shot-level codes (PS12 hands-on, PS19 presenter) use the plan's shot descriptions; the evidence base for them is style/shots.csv."""
import os, re, csv
import pandas as pd
from .config import REPO
from . import style as STY

CB = os.path.join(REPO, "psychology", "psych_codebook.csv")
GAP_RX = re.compile(r"(-|\.\.+)\s*\W*$|need(s)? this|doesn'?t exi|the idea|the problem|the concept|pov: you finally", re.I)
CALLOUT_RX = re.compile(r"calling all|\bevery\b.*\b(mom|dad|wife|guy|girl)|\ball\b.*\b(mom|moms|mom's)|-aholics?|\bbros?\b|this is for you|if you'?re a", re.I)
CONTRAST_RX = re.compile(r"\bvs\b|last year|this year|then|now", re.I)

def callout_primary(text):
    """PS09: an identity callout as the sole hook device (not embedded in a gap or contrast hook)."""
    t = STY.EMOJI_RX.sub("", text or "").strip()
    return bool(CALLOUT_RX.search(t)) and not GAP_RX.search(t) and not CONTRAST_RX.search(t)

def _shots_evidence():
    p = os.path.join(REPO, "style", "shots.csv")
    if not os.path.exists(p): return None
    s = pd.read_csv(p); s = s[s.side == "ours"]; s["hit"] = s.views >= 30000
    hands = s[(s.is_hook == 0) & (s.angle.isin(["high", "pov"]) | s.camera.astype(str).str.contains("pov|ots", case=False))]
    return dict(n_shots=len(s), hands_on_share_hits=float(round(len(hands[hands.hit]) / max(1, (s[s.is_hook == 0].hit).sum()), 2)),
                hands_on_share_flops=float(round(len(hands[~hands.hit]) / max(1, (~s[s.is_hook == 0].hit).sum()), 2)))

CUE_RX = re.compile(r"visible (around|above|through)|design facing|shines through|glow through|colours? .{0,40}(through|around)|own fur|the robe's own|fur and colour|"
                    r"(fur|heart|face|pattern|design).{0,40}(visible|showing|through)|draped in .{0,40}(fur|fabric) (matching|from)", re.I)
HIDDEN_RX = re.compile(r"white cloth|plain cloth|fully (covered|hidden)", re.I)

def ps02(plan):
    """Advisory PS02 (style re-code 2026-10-18 10:09 PM PT: cue visible 5/10 wins vs fully hidden 0/6; wins reveal <= 3.0 s 5/5).
    1 = covered AND product cue visible at 0 s AND reveal <= 3.0 s (+ tray/tin: product 35-60% of a still eye-level medium shot);
    0 = covered but fully hidden / mismatched cue / late reveal; None = not a covered hook."""
    g = plan["gens"][0]; hp, sf = g["prompt"], g["start_frame"]["prompt"]
    if plan["brief"]["format"] == "F04" or not STY.COVERED_RX.search(hp + " " + sf): return None, []
    ho = plan.get("hook_option") or {}; notes = []
    cue = bool(CUE_RX.search(hp + " " + sf)) and not (HIDDEN_RX.search(hp) and not CUE_RX.search(hp))
    if not cue: notes.append("PS02: product fully hidden at 0 s (no colour/texture/face cue around the cover, or a white/mismatched drape): covered-hidden reels 0/6")
    rs = ho.get("reveal_s")
    if rs is None and re.search(r'on \\?"three', hp, re.I) and re.search(r"one word per second|about one word per second", hp, re.I): rs = 3.0
    if rs is None:
        m = re.search(r"by (\d+(?:\.\d+)?) ?s(?:econds)?|at (\d+(?:\.\d+)?) ?s(?:econds)?", hp)
        rs = float(next(x for x in m.groups() if x)) if m else None
    if rs is None: notes.append("PS02: reveal time not stated - state it lands by 3.0 s")
    elif rs > 3.0: notes.append(f"PS02: reveal at {rs}s is late (wins all <= 3.0 s)")
    tray = ho.get("cover") == "tray" or (not ho and re.search(r"baking tray|muffin tin", hp + sf, re.I))
    if tray:
        m = re.search(r"(?<!top )(?<!Top )\b(\d{2})% of the frame|about half of the frame", sf + " " + hp)
        if not m and re.search(r"middle third of the frame|a third of the frame", sf + " " + hp): m = re.search(r"(3)(3)?", "33")
        pct = 50 if m and "half" in m.group(0) else 33 if m and m.group(0) == "33" else int(m.group(1)) if m else None
        if pct is None or not 35 <= pct <= 60: notes.append(f"PS02 tray/tin: product should fill 35-60% of the frame (found {pct})")
        if not re.search(r"(still|static).{0,20}eye-level medium shot|eye-level medium shot", sf + " " + hp, re.I):
            notes.append("PS02 tray/tin: use a still, eye-level medium shot")
    return (1 if not notes else 0), notes

def score(plan):
    cb = {r["code"]: r for r in csv.DictReader(open(CB))} if os.path.exists(CB) else {}
    hook = plan["hook"]["text"]; cards = [c["text"] for c in plan["text_cards"]]; descs = [s["desc"] for s in plan["shots"]]
    allp = " ".join(g["prompt"] for g in plan["gens"]); f = plan["brief"]["format"]; pk = plan["brief"]["product_key"]
    hit = {
        "PS01_info_gap": bool(GAP_RX.search(STY.EMOJI_RX.sub("", hook).strip())),
        "PS02_gap_without_cue": ps02(plan)[0],
        "PS03_orienting": f in ("F04", "F18") or bool(re.search(r"chaos|disaster|whoosh", descs[0], re.I)),
        "PS04_open_loop": len(cards) >= 2,
        "PS05_peak_end": bool(re.search(r"payoff|hero|reaction|cheers|glow", descs[-1], re.I)),
        "PS06_social_proof": bool(re.search(r"jealous|everyone|whole street|sold out|neighbou?rs", hook, re.I)),
        "PS07_scarcity_urgency": bool(re.search(r"\brun\b|hurry|before it'?s gone|selling out", hook, re.I)),
        "PS09_identity_ingroup": bool(CALLOUT_RX.search(hook)),
        "PS10_gifting": bool(re.search(r"gift|for your (mom|dad|wife|husband)|christmas present", hook + " " + plan["caption"]["text"], re.I)),
        "PS11_forbidden": bool(re.search(r"don'?t show|do not show|not allowed|banned", hook, re.I)),
        "PS12_endowment_touch": sum(1 for d in descs if STY.HANDS_RX.search(d)) >= 2,
        "PS13_contrast": bool(CONTRAST_RX.search(" ".join(cards))),
        "PS14_humor_bv": pk == "brickhood_mask" and bool(re.search(r"goofy|snow angel|prank|dare|🤣|😂", " ".join(descs + cards))),
        "PS15_cute_aww": bool(re.search(r"retriever|dog|puppy|kid|baby|cat", allp, re.I)),
        "PS16_sensory_asmr": bool(re.search(r"crackl|sizzl|clink|whoosh|sound of|asmr", allp, re.I)),
        "PS17_mere_exposure": "proven" in (plan["music"]["pick"].get("why") or ""),
        "PS18_arousal": bool(re.search(r"cozy|cheers|glow|reaction|laugh", " ".join(descs[-2:]), re.I)),
        "PS19_presenter_vs_pov": sum(1 for d in descs if STY.FACE_RX.search(d)) <= 1,
    }
    pts, notes = 0, []
    for code, on in hit.items():
        use = (cb.get(code, {}).get("engine_use") or "").lower()
        if code == "PS02_gap_without_cue":     # D52 + re-code: advisory; never blocks
            if on == 1: pts += 1
            elif on == 0: notes += ps02(plan)[1]
            continue
        elif code == "PS09_identity_ingroup":
            if on and callout_primary(hook): pts -= 2; notes.append("PS09 audience-callout is the sole hook device: down-weighted (27% vs 58% hit)")
        elif on and use.startswith(("exploit", "require")): pts += 1
        elif not on and use.startswith("require"): notes.append(f"{code} required but not detected")
    return dict(advisory=True, score=pts, codes={k: (v if v is None else bool(v)) for k, v in hit.items()}, notes=notes,
                evidence={k: cb[k]["our_evidence"][:120] for k, v in hit.items() if v and k in cb}, shots_csv=_shots_evidence())
