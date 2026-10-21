"""Editor defaults + linter from learning/raw_vs_final/EDIT_RULES.md (35 Omar CapCut drafts vs 39 posted reels).
Defaults: head-trim ~1.05 s and tail-trim ~1.2 s on every clip after the first; split each gen into 2-3 pieces dropping
~0.4 s mid-chunk; median shot ~1.5 s; target 16-17 s with 9-13 shots; 3-card structure; song enters at its famous lyric;
speed 1.0x (1.2-1.5x on action beats); no zoom/crop (scale 1.0). Audio (D63): keep natural clip sound, boost the key real sound 2-4x, ban fake SFX.
Severity: FIX = hard (zoom, slow-mo story shot, unmuted gen audio); WARN = target miss (advisory, logged)."""
import re, statistics
D = dict(head_trim_s=1.05, tail_trim_s=1.2, first_head_trim_s=0.0, split_pieces=(2, 3), split_gap_s=0.4, median_shot_s=1.5,
         max_shot_s=3.3, target_len_s=(16.0, 17.0), shots=(9, 13), cards=3, speed=1.0, action_speed=(1.2, 1.5), scale=1.0,
         clip_audio_volume=1.0, key_sound_gain=(2.0, 4.0), song_intro_exceptions=("holly_jolly", "holly jolly"))
try:  # D74: Omar-style overrides (105 CapCut drafts, top-performer weighted; learning/editing_style/style.json)
    from .omar_style import style as _ostyle, hook_speed as hook_fit
    _T = _ostyle()["timing"]
    D.update(target_len_s=tuple(_T["total_range_s"]), shots=tuple(int(round(x)) for x in _T["shots_range"]), median_shot_s=_T["shot_s"],
             opener_max_s=_T["opener_max_s"], hook_speed_values=tuple(_ostyle()["speed"]["hook_fit_values"]), max_card_lines=_ostyle()["text"]["max_lines"])
except Exception:  # style.json missing -> legacy defaults
    hook_fit = None

def default_timeline(gens, action_roles=("box", "install", "put", "open")):
    """Proposed cut list from raw gen durations: [(gen, src_in, src_out, speed)]."""
    out = []
    for i, g in enumerate(gens):
        dur = float(g.get("dur", 4)); a = D["first_head_trim_s"] if i == 0 else D["head_trim_s"]; b = dur - (0.3 if i == 0 else D["tail_trim_s"])
        sp = D["action_speed"][0] if g.get("role") in action_roles else D["speed"]
        if i == 0 or b - a < 1.4: out.append(dict(gen=g["id"], src_in=round(a, 2), src_out=round(b, 2), speed=sp)); continue
        mid = (a + b) / 2; g2 = D["split_gap_s"] / 2
        out += [dict(gen=g["id"], src_in=round(a, 2), src_out=round(mid - g2, 2), speed=sp), dict(gen=g["id"], src_in=round(mid + g2, 2), src_out=round(b, 2), speed=sp)]
    return out

def _song_in(plan):
    m = plan.get("music") or {}; af = m.get("audience_fit_song") or {}
    pk = m.get("pick") if isinstance(m.get("pick"), dict) else {}
    name = str(af.get("song") or pk.get("song") or m.get("song") or "")
    ip = af.get("in_point") if af else pk.get("offset_s")
    if ip is None and m.get("song"): mm = re.search(r"from (\d+):(\d+(?:\.\d+)?)", str(m.get("alt", ""))); ip = None
    if isinstance(ip, str):
        mm = re.search(r"(\d+):(\d+(?:\.\d+)?)", ip); ip = int(mm.group(1)) * 60 + float(mm.group(2)) if mm else None
    return name, ip

def lint(plan):
    rows = []; W = lambda r, t, f, s="WARN": rows.append(dict(gen="-", kind="edit", rule=r, severity=s, text=t, fix=f))
    shots = plan.get("shots") or []; lens = [s["t1"] - s["t0"] for s in shots]
    if shots:
        med = statistics.median(lens); total = shots[-1]["t1"]
        if not D["shots"][0] <= len(shots) <= D["shots"][1]: W("ER5", f"{len(shots)} shots", "9-13 shots (winners)")
        if not D["target_len_s"][0] - 0.5 <= total <= D["target_len_s"][1] + 0.5: W("ER7", f"length {total:.1f} s", "target 16-17 s")
        if med > 2.0: W("ER5", f"median shot {med:.2f} s", "median ~1.5 s")
        for s, l in zip(shots[1:], lens[1:]):
            if l > D["max_shot_s"]: W("ER5", f"{s['code']} {l:.1f} s", "no non-hook shot > 3.3 s")
        for s in shots[1:]:
            tr = s.get("trim")
            if tr and tr[0] < 0.5: W("ER3", f"{s['code']} src_in {tr[0]}", "head-trim ~1.05 s on clips after the first")
        by = {}
        for s in shots: by.setdefault(s.get("gen"), []).append(s)
        for g, ss in by.items():
            if g != (shots[0].get("gen")) and len(ss) < 2: W("ER2", f"gen {g} used once", "split each gen into 2-3 pieces, drop ~0.4 s middle")
        for s in shots:
            sp = s.get("speed") or 1.0
            if sp < 1.0 and s.get("role") != "after": W("ER9", f"{s['code']} speed {sp}", "never slow a story shot", "FIX")
            if sp > 1.5: W("ER9", f"{s['code']} speed {sp}", "1.2-1.5x max on action beats")
            if (s.get("scale") or 1.0) != 1.0 or s.get("zoom"): W("ER18", f"{s['code']} zoom/scale", "no zoom or crop in the edit (scale 1.0)", "FIX")
    if len(plan.get("text_cards") or []) not in (D["cards"], D["cards"] + 1): W("ER11", f"{len(plan.get('text_cards') or [])} cards", "3-card structure: problem -> Vs... -> solution")
    name, ip = _song_in(plan)
    if name and ip is not None and ip < 15 and not any(x in name.lower() for x in D["song_intro_exceptions"]):
        W("ER15", f"song '{name}' enters at {ip} s", "enter at the famous lyric/chorus, not the intro")
    for g in plan.get("gens") or []:
        if g.get("generate_audio") is False: W("ER17", f"{g['id']} generate_audio off", "D63: keep natural clip sound (generate_audio=True)", "FIX")
    if plan.get("final") and not ((plan.get("music") or {}).get("song_key")):
        W("ER19", "final export has no song", "D64: every final export lays the chosen song in at its proven in-point (hookforge.songlay.lay_song)", "FIX")
    gains = [s.get("audio_gain") for s in shots if s.get("audio_gain")]
    if shots and any(x == 0 for x in gains): W("ER17", "a shot is muted", "D63: keep natural sound on every shot")
    if shots and not any(D["key_sound_gain"][0] <= x <= D["key_sound_gain"][1] for x in gains): W("ER17", "no key real sound boosted", "boost the key real sound (scissors, door, tape, sparks) 2-4x")
    return dict(ok=not any(r["severity"] == "FIX" for r in rows), rows=rows, defaults=D)
