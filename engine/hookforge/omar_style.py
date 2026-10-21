"""D74 OMAR STYLE: edit defaults + "edit vs Omar" QA, learned from his CapCut drafts (learning/editing_style/style.json,
built by learning/editing_style/extract.py; write-up OMAR_STYLE.md).
  hook_speed(src_s, max_s)        -> speed to fit a spoken hook instead of cutting words (1.1-1.5, prefer 1.2)
  card_layout(text)               -> textcards scale/y with <= 2 rows (shrinks, never adds a 3rd row)
  dialogue_gain_db(clip_lufs, song_lufs) -> clip gain so speech sits dialogue_over_music_lu above the song
  compare(timeline)               -> per-dimension score 0-100 vs Omar's ranges + overall; FAIL rows for hard rules
timeline = dict(dur, shots=[dict(dur, speed=1, role)], cards=[dict(text, t0, dur, lines?, scale?, y?)],
                song=dict(onset_s), dialogue_minus_music_lu=None|float, transitions=0)"""
import json, os, re
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
STYLE_PATH = os.path.join(REPO, "learning", "editing_style", "style.json")
_S = None
def style():
    global _S
    if _S is None: _S = json.load(open(STYLE_PATH))
    return _S
EMO = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF]")

def hook_speed(src_s, max_s):
    """Smallest of Omar's speed values that fits src_s into max_s. Never < 1, never cut: if even max speed doesn't fit,
    return max speed and fits=False so the caller trims silence/picks a shorter take instead of clipping a word."""
    sp = style()["speed"]
    if src_s <= max_s: return dict(speed=1.0, fits=True, out_s=round(src_s, 3))
    for v in sp["hook_fit_values"]:
        if src_s / v <= max_s: return dict(speed=v, fits=True, out_s=round(src_s / v, 3))
    v = sp["max_hook_speed"]; return dict(speed=v, fits=False, out_s=round(src_s / v, 3))

def card_layout(text):
    t = style()["text"]
    try:
        from .textcards import fit_card, card_lines, OMAR_HOOK
        sc = min(fit_card(text, scale=OMAR_HOOK["scale"], max_lines=t["max_lines"]), OMAR_HOOK["scale"])
        n = len(card_lines(text, sc))
    except Exception:  # renderer/font missing: char-count fallback
        sc = t["scale"]; n = sum(max(1, -(-len(EMO.sub("ww", l)) // t["chars_per_line_max"])) for l in text.split("\n"))
    return dict(scale=sc, lines=n, ok=n <= t["max_lines"], y_center_frac_from_top=t["y_center_frac_from_top"])

def dialogue_gain_db(clip_lufs, song_lufs, song_gain_db=0.0):
    a = style()["audio"]; g = (song_lufs + song_gain_db + a["dialogue_over_music_lu"]) - clip_lufs
    cap = a.get("clip_gain_cap_db", 20.0)
    return dict(clip_gain_db=round(min(g, cap), 2), song_gain_db=round(song_gain_db - max(0.0, g - cap), 2))

def _band(v, lo, hi, hard_lo=None, hard_hi=None):
    """100 inside [lo,hi], linear to 0 at 2x the band width outside."""
    if v is None: return None
    if lo <= v <= hi: return 100
    w = max(hi - lo, 1e-6); d = (lo - v) if v < lo else (v - hi)
    return max(0, round(100 - 100 * d / (2 * w)))

def compare(tl):
    S = style(); T = S["timing"]; X = S["text"]; A = S["audio"]; W = S["qa_weights"]; rows = []
    def R(k, score, got, want, hard=False, warn_out=False):
        rows.append(dict(dim=k, score=score, got=got, omar=want, level=("FAIL" if hard and score is not None and score < 100 else
                    "WARN" if score is not None and (score < 60 or (warn_out and score < 100)) else "OK")))
    sh = tl.get("shots") or []
    # D79: outside Omar's CapCut range is always a WARN (was silent until score < 60, so 9.7 s finals passed unflagged)
    R("total", _band(tl.get("dur"), *T["total_range_s"]), tl.get("dur"), T["total_range_s"], warn_out=True)
    sh0 = tl.get("shots") or []
    if sh0: R("shot_count", _band(len(sh0), *T["shots_range"]), len(sh0), T["shots_range"], warn_out=True)
    if sh:
        op = sh[0]["dur"]; R("opener", _band(op, T["opener_range_s"][0], T["opener_max_s"]), round(op, 2), [T["opener_range_s"][0], T["opener_max_s"]])
        body = [s["dur"] for s in sh[1:]]
        if body:
            med = sorted(body)[len(body) // 2]; R("shot_len", _band(med, *T["role_s"]["body"]["range"]), round(med, 2), T["role_s"]["body"]["range"])
        hs = sh[0].get("speed", 1.0)
        R("hook_speed", 100 if 1.0 <= hs <= S["speed"]["max_hook_speed"] else 0, hs, [1.0, S["speed"]["max_hook_speed"]], hard=True)
        if any(s.get("speed", 1) < 1 and s.get("role") not in ("after",) for s in sh): R("story_slowmo", 0, "slow-mo story shot", "never", hard=True)
        ed = sh[-1]["dur"]; R("ending", _band(ed, *T["ending_range_s"]), round(ed, 2), T["ending_range_s"])
    cards = tl.get("cards") or []
    if cards:
        lines = [c.get("lines") or card_layout(c["text"])["lines"] for c in cards]
        R("text_lines", 100 if max(lines) <= X["max_lines"] else 0, max(lines), "<= %d" % X["max_lines"], hard=True)
        cpl = max(max(len(EMO.sub("ww", l)) for l in c["text"].split("\n")) for c in cards)
        R("chars_per_line", _band(cpl, 4, X["chars_per_line_max"] + 2), cpl, "<= %d" % X["chars_per_line_max"])
        scs = [c["scale"] for c in cards if c.get("scale")]
        if scs: R("text_size", _band(min(scs), *X["scale_range"]), min(scs), X["scale_range"])
        ys = [c["y"] for c in cards if c.get("y") is not None]
        if ys: R("text_y", _band(ys[0], *X["y_range"]), ys[0], X["y_range"])
        ne = [len(EMO.findall(c["text"])) for c in cards]
        R("emoji", 100 if ne and max(ne) <= X["emoji"]["max_per_card"] and ne[0] >= 1 else 50, ne, "hook card 1-2, at the end")
        if re.search(r"https?://|www\.|\.com\b|get yours|link in bio", " ".join(c["text"] for c in cards), re.I):
            R("onscreen_link", 0, "link/CTA on screen", "none (link lives in caption)", hard=True)
        R("first_card_t0", 100 if cards[0].get("t0", 0) <= 0.05 else 0, cards[0].get("t0", 0), 0.0, hard=True)
        last = cards[-1]; R("last_card_to_end", 100 if tl.get("dur") is None or last.get("t0", 0) + last.get("dur", 0) >= tl["dur"] - 0.25 else 40, round(last.get("t0", 0) + last.get("dur", 0), 2), tl.get("dur"))
    on = (tl.get("song") or {}).get("onset_s")
    if on is not None: R("song_t0", 100 if on <= 0.1 else 0, on, "<= 0.1 s", hard=True)
    dm = tl.get("dialogue_minus_music_lu")
    if dm is not None:
        lo, hi = A["dialogue_over_music_lu_range"]; R("dialogue", _band(dm, lo, hi + 4), dm, [lo, hi], hard=dm < lo - 2)
    lu = tl.get("lufs")   # D79: Omar's top reels export at -14.0..-14.7 LUFS integrated (15 reels >= 50K, 2026-10-20 audit)
    if lu is not None: R("loudness", _band(lu, -15.0, -13.5), lu, [-15.0, -13.5], warn_out=True)
    R("transitions", 100 if not tl.get("transitions") else 0, tl.get("transitions", 0), 0)
    sc = [(r["score"], W.get(r["dim"], 1)) for r in rows if r["score"] is not None]
    overall = round(sum(s * w for s, w in sc) / max(1e-9, sum(w for _, w in sc)), 1)
    fails = [r for r in rows if r["level"] == "FAIL"]
    return dict(gate="EDIT_VS_OMAR", overall=overall, ok=not fails and overall >= 75, level="BLOCK" if fails else ("WARN" if overall < 75 else "INFO"), rows=rows)

def timeline_from_final(path, cards=None, dialogue_minus_music_lu=None, cut_thr=0.15):
    """Build a compare() timeline from a rendered final: cuts via qa.detect_cuts, song onset via songlay.onset_s."""
    from . import qa, songlay
    dur = qa.probe(path)["dur"]
    ts = [0.0] + [c for c in qa.detect_cuts(path, cut_thr) if 0.05 < c < dur - 0.05] + [dur]
    shots = [dict(dur=round(b - a, 3), speed=1.0) for a, b in zip(ts, ts[1:]) if b - a > 0.05]
    return dict(dur=dur, shots=shots, cards=cards or [], song=dict(onset_s=songlay.onset_s(path)), dialogue_minus_music_lu=dialogue_minus_music_lu,
                transitions=0, lufs=integrated_lufs(path))

def integrated_lufs(path):
    import subprocess, re
    o = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", o); return float(m[-1]) if m else None
