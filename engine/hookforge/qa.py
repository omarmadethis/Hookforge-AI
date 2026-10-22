"""QA gate (Phase D): plan checks, LOGIC CHECK (product world, D37), music/caption proof (D38), rendered-edit checks,
and the D33 absurd-failure re-roll decision with logging (learning/reroll_log.csv).
"""
import os, re, csv, json, subprocess, datetime
from .config import REPO, REROLL, CREDITS, EDIT, HOOK_MAX_S, TEXT

def _kw(s): return s.split("(")[0].strip().lower()

def logic_check(plan, profile):
    """Would a viewer find this setting/story natural for this product? Rule layer + a reviewer question on the render."""
    issues, notes = [], []
    text = " ".join([g["prompt"] + " " + g["start_frame"]["prompt"] for g in plan["gens"]]).lower()
    text_nosuffix = text.replace("no logos", "")
    for f in profile["forbidden_settings"]:
        k = _kw(f)
        if k and re.search(r"\b" + re.escape(k) + r"\b", text_nosuffix): issues.append(f"setting '{k}' is forbidden for {profile['display']} (world: {profile['world'][:80]})")
    world_words = {w for s in profile["settings"] for w in re.findall(r"[a-z]{4,}", _kw(s))} - {"with", "bright", "night", "table", "front"}
    hits = sorted(w for w in world_words if w in text)
    (notes if hits else issues).append(f"world anchors in prompts: {hits[:6]}" if hits else "no world setting words found in prompts")
    copy = " ".join([c["text"] for c in plan["text_cards"]] + [plan["caption"]["text"]]).lower()
    for w in profile.get("copy_forbidden", []):
        if re.search(r"\b" + re.escape(w) + r"\b", copy): issues.append(f"copy word '{w}' is off-world for {profile['display']}")
    m = plan["music"]["pick"]
    if not m: issues.append("no proven, niche-matching song available (core slot)")
    else:
        gap = abs(m["energy"] - plan["fit"]["video_energy"])
        if gap > 1 and "proven on this product" not in m["why"]: issues.append(f"music energy {m['energy']} vs video {plan['fit']['video_energy']}")
        notes.append(f"music {m['song']}: {m['why']}")
    if "format default" in plan["caption"]["why"] and plan["brief"]["slot"] != "experiment": issues.append("caption not proven on this product (core slot)")
    if plan["fit"]["verdict"] in ("WEAK", "REJECT"): issues.append(f"format fit {plan['fit']['verdict']}")
    return dict(passed=not issues, issues=issues, notes=notes,
                reviewer_question=f"Would a viewer find '{plan['setting']}' + this story natural for {profile['display']} ({profile['world'][:60]})? Answer on the render.")

def plan_checks(plan):
    p = list(plan["prompt_checks"])
    if plan["hook_s"] > HOOK_MAX_S: p.append(f"hook {plan['hook_s']} s > {HOOK_MAX_S}")
    from .config import race_targeted
    for t in [plan["hook"]["text"]] + [v.get("text", "") for v in (plan.get("hook_variants") or []) if isinstance(v, dict)]:
        if race_targeted(t): p.append(f"race-targeted hook excluded (neutral recipient framing only): {t[:40]}")
    for g in plan["gens"]:
        if g["dur"] > 5: p.append(f"gen {g['id']} {g['dur']} s > 5 s")
        if g["res"] != "720p": p.append(f"gen {g['id']} not 720p (D181)")
        if g["id"] != "H" and g["res"] != "720p": p.append(f"{g['id']} not 720p")
    lo, hi = EDIT["length_soft"]
    if not lo <= plan["duration"] <= hi: p.append(f"length {plan['duration']} outside {lo}-{hi}")
    if plan["banned_cta_found"]: p.append(f"banned CTA words {plan['banned_cta_found']}")
    from . import plugins
    try:
        from . import gen_failures
    except ImportError:
        gen_failures = None
    for sev, msg in plugins.audience_checks([c["text"] for c in plan["text_cards"]] + [plan["caption"]["text"]], market="US"):
        p.append(f"[{sev}] {msg}")
    # voice/ V01-V16 are REFERENCE DATA ONLY (Omar 21:48): not applied to generation or QA; only D49 (AI-doubt proof + AI-tells log) is kept
    for g in (plan["gens"] if gen_failures else []):
        for kind, pr in (("video", g["prompt"]), ("still", g["start_frame"]["prompt"])):
            for hit in gen_failures.lint(pr, model=g["model"] if kind == "video" else "gpt_image_2")["hits"]:
                if hit["status"] == "promoted": p.append(f"[lint] {g['id']} {kind}: '{hit['trigger']}' -> {hit['fix']} ({hit['rule_id']})")
    from . import season as _season, profiles as _prof
    for m in _season.claim_problems([c["text"] for c in plan["text_cards"]] + [plan["caption"]["text"]] + [h["text"] for h in plan.get("hook_variants", [])],
                                    _prof.load(plan["product"]["key"]), plan["season"]["date"]):
        p.append(m)
    prof_ = _prof.load(plan["product"]["key"])
    blob = " ".join([c["text"] for c in plan["text_cards"]] + [plan["caption"]["text"]] + [h["text"] for h in plan.get("hook_variants", [])]
                    + [g["prompt"] for g in plan["gens"]] + [g["start_frame"]["prompt"] for g in plan["gens"]]
                    + [s["desc"] for s in plan["shots"]]).lower()
    if prof_.get("proof_shot") and not plan.get("proof_shot", {}).get("present"): p.append(f"FIX no PROOF shot (V02): {prof_['proof_shot'][1]}")
    from . import style as _sty
    _own = plan["hook"].get("tag") == "P" and bool(re.search(r"\b(HJ|MG|MGS|MJ|MJIG|BH|MF|GM)-\d+", plan["hook"].get("why", "")))
    p += _sty.emoji_problems(plan["text_cards"], proven_own=_own) + _sty.shot_problems(plan, prof_)
    if not plan["credits"]["within_budget"]: p.append(f"credits {plan['credits']['total']} > budget {plan['credits']['budget']}")
    return p

def probe(path):
    o = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:format=duration", "-of", "json", path],
                       capture_output=True, text=True, timeout=30)
    j = json.loads(o.stdout); s = j["streams"][0]
    return dict(w=s["width"], h=s["height"], dur=float(j["format"]["duration"]))

def detect_cuts(path, thr=0.30):
    o = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-vf", f"select='gt(scene,{thr})',showinfo", "-an", "-f", "null", "-"],
                       capture_output=True, text=True, timeout=120)
    return [round(float(x), 2) for x in re.findall(r"pts_time:([\d.]+)", o.stderr)]

def edit_checks(path, plan, final=False):
    pr = probe(path); out = []
    if abs(pr["dur"] - plan["duration"]) > 0.25: out.append(f"rendered {pr['dur']:.2f} s vs plan {plan['duration']}")
    if final and (pr["w"], pr["h"]) != (2160, 3840): out.append(f"final export {pr['w']}x{pr['h']} != 2160x3840")
    cuts = detect_cuts(path); want = sorted({s["t0"] for s in plan["shots"] if s["t0"] > 0})
    missing = [c for c in want if not any(abs(c - x) <= 0.25 for x in cuts)]
    return dict(probe=pr, detected_cuts=cuts, planned_cuts=want, missing_cuts=missing, problems=out)

def reroll_decision(gen_id, judgement, attempts_so_far=0, log=True, context=""):
    """judgement: {failure: str, confidence: float, note: str}. D33: re-roll only on an ABSURD failure at >= 0.9 confidence,
    max 1 automatic re-roll per shot. Everything else ships and is logged."""
    f, conf = judgement.get("failure"), float(judgement.get("confidence", 0))
    absurd = f in REROLL["absurd_failures"]
    reroll = bool(REROLL["auto"] and absurd and conf >= REROLL["min_confidence"] and attempts_so_far < REROLL["max_auto_rerolls_per_shot"])
    cost = CREDITS["body_720p_4s"] if reroll else 0
    reason = ("absurd failure, certain" if reroll else "minor - ship and log" if f in REROLL["never_reroll"] or not absurd
              else "absurd but below confidence / re-roll cap - escalate to human")
    rec = dict(ts=datetime.datetime.now(__import__("zoneinfo").ZoneInfo("America/Los_Angeles")).isoformat(timespec="seconds"), context=context, gen=gen_id, failure=f, confidence=conf,
               reroll=reroll, reason=reason, credits=cost, note=judgement.get("note", ""))
    if log:
        p = os.path.join(REPO, "learning", "reroll_log.csv"); new = not os.path.exists(p)
        with open(p, "a", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rec)); 
            if new: w.writeheader()
            w.writerow(rec)
        if absurd and conf >= REROLL["min_confidence"]:   # D42: certain misgens go into the failure ledger too
            try:
                from . import gen_failures; gen_failures.log_attempt(context or "unknown", judgement.get("model", ""), judgement.get("prompt", ""),
                                                                    "misgen", cause=f"{f}: {judgement.get('note', '')}", source="qa.reroll_decision")
            except Exception: pass
    return rec

CHECKLIST = ("ABSURD-FAILURE CHECKLIST (D33; re-roll only if ONE is certain, >=0.9, max 1 per shot): "
             + ", ".join(REROLL["absurd_failures"]) + ". NEVER re-roll: " + ", ".join(REROLL["never_reroll"]) + ".")

# ================= media QA (gap audit G1/G2/G8) - wraps tools/preflight ===================================
import sys as _sys
_PF = os.path.join(REPO, "tools", "preflight")
if _PF not in _sys.path: _sys.path.insert(0, _PF)

# PROPOSED thresholds (PD-G2 / PD-G1) - calibrate on own data before they BLOCK
PDQ_BLOCK = 80.0      # q_match AND r_match >= 80 % vs any reference => Meta likely treats as the same video
PDQ_WARN = 20.0       # > 20 % either way => warn, change more axes
FIDELITY_RANK_ONLY = True   # product_fidelity ranks shots for the vision pass until calibrated (GAP_AUDIT G1)

def packed_cut_check(clip, window=(1.5, 2.5), threshold=27.0):
    """Packed body gen must contain EXACTLY ONE hard cut inside `window` (and none elsewhere). PySceneDetect ContentDetector."""
    from scenedetect import detect, ContentDetector
    scenes = detect(clip, ContentDetector(threshold=threshold), show_progress=False)
    cuts = [round(s[0].get_seconds(), 2) for s in scenes[1:]]
    inside = [c for c in cuts if window[0] <= c <= window[1]]
    ok = len(inside) == 1 and len(cuts) == 1
    return dict(clip=os.path.basename(clip), cuts=cuts, ok=ok,
                failure=None if ok else "hard_cut_missing_or_broken", confidence=0.95 if not cuts or len(cuts) > 2 else 0.7)

def raw_gen_checks(clip, product_img_dir=None, packed=True, out_dir=None):
    """Every raw generation: contact sheet (0.5 s) for the D33 vision pass, OCR for burned-in text (D14), packed-cut assert,
    product fidelity ranking. Returns findings mapped onto the D33 taxonomy (absurd vs minor)."""
    import preflight
    rep = preflight.run(clip, out_dir, ocr=True); finds = []
    if not rep["aspect_ok"]: finds.append(dict(failure="wrong_aspect_ratio", confidence=0.99, note=f"{rep['width']}x{rep['height']} not 9:16 (MP2-9, f90b878c)"))
    if rep.get("ocr_text"):
        finds.append(dict(failure="weird_text_on_display_or_signage", confidence=0.6, note=f"burned-in/hallucinated text: {str(rep['ocr_text'])[:120]}"))
    if packed:
        pc = packed_cut_check(clip); rep["packed_cut"] = pc
        if not pc["ok"]: finds.append(dict(failure=pc["failure"], confidence=pc["confidence"], note=f"cuts {pc['cuts']}"))
    if product_img_dir and os.path.isdir(product_img_dir):
        import product_fidelity
        pf = product_fidelity.score(clip, product_img_dir); rep["product_fidelity"] = {k: v for k, v in pf.items() if k != "per_frame"}
        if not FIDELITY_RANK_ONLY and pf.get("first", 1) < 0.2: finds.append(dict(failure="product_missing", confidence=0.9, note="CLIP"))
    rep["d33_findings"] = finds
    rep["contact_sheet_checklist"] = CHECKLIST
    return rep

def final_checks(path, out_dir=None, final=True, cards=None, dialogue_minus_music_lu=None, timeline=None, ai_shots=None, card_texts=None):
    """Every rule here maps to an entry in learning/OMAR_FEEDBACK_LOG.md (F##). Add the gate here AND a log row for each new Omar fix.
    Finished file: 9:16, 2160x3840 (final), loudness -14 LUFS / TP <= -1 (D7), text safe zones (WARN), and NO provenance/C2PA
    metadata (D44, Omar 2026-10-18: strip on final export via autoedit.clean_export)."""
    import preflight
    rep = preflight.run(path, out_dir, ocr=True); probs = []
    if not rep["aspect_ok"]: probs.append("BLOCK aspect not 9:16")
    if final and (rep["width"], rep["height"]) != (2160, 3840): probs.append(f"BLOCK {rep['width']}x{rep['height']} != 2160x3840 (D7)")
    if not rep["loudness_ok"]: probs.append(f"FIX loudness {rep['loudness']} (target -14 LUFS, TP <= -1)")
    for w in rep.get("safe_zone_warnings", []): probs.append(f"WARN safe zone: {w}")
    if final:  # D66: song audible from frame 0, no silent lead-in
        from hookforge.songlay import song_start_check
        sc = song_start_check(path); rep["song_at_t0"] = sc
        if not sc["ok"]: probs.append(f"BLOCK audio onset {sc['onset_s']}s > 0.1s (song must start on frame 0, D66)")
    if final:  # D-NOLOOP (Omar 2026-10-19): never loop/repeat footage to pad a shot
        from hookforge.repeat_detect import find_repeats
        rp = find_repeats(path); rep["repeated_footage"] = rp
        for h in rp: probs.append(f"BLOCK repeated/looped footage: {h['dup_t']}s repeats {h['src_t']}s for {h['len_s']}s (never loop; shorten, slow >=0.8x w/ interpolation, or hold last frame)")
    if final:  # D-NOSPLICE: no jump cut inside one source take (adjacent segments, same clip id)
        import json as _j, os as _o
        tl = timeline if isinstance(timeline, dict) else (_j.load(open(timeline)) if timeline and _o.path.exists(timeline) else None)
        if tl is None: probs.append("BLOCK no timeline passed - same-take splice gate cannot run (pass this variant's timeline; Omar t220)")
        else:
            from hookforge.splice_detect import find_same_take_splices
            sp = find_same_take_splices(tl.get("shots", []), path); rep["same_take_splices"] = sp
            for h in sp: probs.append(f"BLOCK jump cut inside one take {h['clip']} at {h['boundary_t']}s (trims {h['trim_a']} + {h['trim_b']}) - use one continuous take, speed it up instead")
            from hookforge import pacing as _pc   # Omar t2xx: no lingering shots; no same-looking frames across a cut
            for x in _pc.hold_violations(tl): probs.append(f"BLOCK linger: {x}")
            nd = _pc.near_duplicate_cuts(tl, path); rep["near_duplicate_cuts"] = nd
            for h in nd: probs.append(f"BLOCK cut at {h['cut_t']}s {h['a']}->{h['b']} looks like the same shot (corr {h['corr']}) - reads as a repeat; cut earlier/later or drop one")
    if final and card_texts:  # Omar t2xx: 'Vs.' never on card 1; 😔 paired, not lone 💔 (gates G14/G19)
        from hookforge import gates as _g
        pl = dict(text_cards=[dict(text=t) for t in card_texts])
        for r in _g.g14_vs_card(pl) + _g.g19_emoji(pl):
            if not r["ok"]: probs.append(f"BLOCK {r['msg']}")
            elif r.get("level") == "WARN": probs.append(f"WARN {r['msg']}")
    if final:  # D44b: no encoder fingerprint - any Encoder tag or Lavf string means a step skipped autoedit.clean_export/clean_remux
        import subprocess as _sp, re as _re
        ex = _sp.run(["exiftool","-a","-G1",path],capture_output=True,text=True).stdout
        bad = [l.strip() for l in ex.splitlines() if _re.search(r"^\[[^\]]+\]\s+Encoder\b|Lavf|Lavc|libx26", l)]
        rep["encoder_tags"] = bad
        if bad: probs.append(f"BLOCK encoder metadata present {bad} - finish with autoedit.clean_remux/clean_export (D44)")
    if final:  # D44d: same whitelist scan as the delivery chokepoint
        from hookforge import deliver as _dv
        dp = _dv.scan(path); rep["deliver_scan"] = dp
        for x in dp: probs.append(f"BLOCK trace: {x} (deliver.py would refuse)")
    if final and any(rep["provenance"].values()): probs.append(f"BLOCK provenance/C2PA metadata present {rep['provenance']} - run autoedit.clean_export (D44)")
    if final:  # D74: edit vs Omar (style.json); hard-rule misses BLOCK, low overall WARNs
        try:
            from hookforge import omar_style as OS
            ev = OS.compare(OS.timeline_from_final(path, cards=cards, dialogue_minus_music_lu=dialogue_minus_music_lu)); rep["edit_vs_omar"] = ev
            for r in ev["rows"]:
                if r["level"] == "FAIL": probs.append(f"BLOCK edit-vs-Omar {r['dim']}: got {r['got']}, Omar {r['omar']} (D74)")
            if ev["overall"] < 75: probs.append(f"WARN edit-vs-Omar overall {ev['overall']}/100 (D74)")
        except Exception as e: rep["edit_vs_omar"] = dict(error=str(e))
    if ai_shots:  # D75: AI-look reviewer per shot (absurd = BLOCK + reroll that shot only; else WARN)
        try:
            from hookforge import ai_look
            al = ai_look.review(ai_shots); rep["ai_look"] = al["results"]; probs += al["problems"]
        except Exception as e: rep["ai_look"] = dict(error=str(e))
    rep["problems"] = probs; rep["c2pa_policy"] = "D44: stripped on final export; preflight asserts none remains"
    return rep

def originality_gate(candidate, references):
    """PDQ/vPDQ near-duplicate gate for recreations, page variants and reposts (PD-G2, PROPOSED thresholds)."""
    import originality
    res = [originality.compare(candidate, r) for r in references]
    worst = max(res, key=lambda r: min(r.get("q_match", 0), r.get("r_match", 0))) if res else {}
    q, r = worst.get("q_match", 0), worst.get("r_match", 0)
    verdict = "BLOCK" if (q >= PDQ_BLOCK and r >= PDQ_BLOCK) else "WARN" if max(q, r) > PDQ_WARN else "PASS"
    return dict(verdict=verdict, worst=worst, all=res, thresholds=dict(block=PDQ_BLOCK, warn=PDQ_WARN, status="PROPOSED"))

AI_TELLS = ["product part changes between cuts (foot pockets, mask face, hood)", "unnatural packaging behaviour (bag rips wrongly, box morphs)",
            "unrealistic plug / fit (cable 'magically' fits, mask cutout floats)", "too-perfect store shelves / labels",
            "gibberish text on packaging or signage", "plastic skin / waxy faces", "extra or fused fingers"]

def ai_tells_log(gen_id, tells, context="", note=""):
    """V03/D49: log the AI tells viewers call out. NEVER triggers a re-roll (D33); feeds the next prompt (positive wording)."""
    p = os.path.join(REPO, "learning", "ai_tells_log.csv"); new = not os.path.exists(p)
    rec = dict(ts=datetime.datetime.now(__import__("zoneinfo").ZoneInfo("America/Los_Angeles")).isoformat(timespec="seconds"),
               context=context, gen=gen_id, tells="; ".join(tells), reroll=False, note=note)
    with open(p, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rec))
        if new: w.writeheader()
        w.writerow(rec)
    return rec

def judge_raw_gen(clip, product, gen_id="B", packed=True, context="", attempts_so_far=0, log=True):
    """D33 absurd-failure judge = vision_judge (CLIP fidelity vs own-reel banks + contact-sheet checks + raw_gen_checks), Omar 2026-10-18 10:35 PM PT."""
    from . import vision_judge
    return vision_judge.judge(clip, product, gen_id=gen_id, packed=packed, context=context, attempts_so_far=attempts_so_far, log=log)

# ---------------- D63 audio check (Omar 2026-10-19 PT) ----------------
FAKE_SFX_RX = r"\b(yay|whoosh\w*|swoosh\w*|boing|cartoon\w*|sound effects?|sfx|music)\b"
def audio_check(clip=None, prompt=None, transcript=None):
    """Natural clip sound must exist and contain no fake/added sounds.
    clip: ffmpeg probes for an audio stream and level (silent or missing = FAIL; clipping = WARN).
    prompt: LG3 lint (no SFX asked for). transcript (ASR/watch notes): an inserted 'yay', whoosh, cartoon sound or music = FAIL.
    A listen pass by the vision/watch judge is still required for stray sounds that don't match the action."""
    import subprocess
    out = dict(ok=True, findings=[])
    if clip:
        pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=codec_name", "-of", "csv=p=0", clip], capture_output=True, text=True)
        if not pr.stdout.strip(): out["findings"].append(("FAIL", "no audio stream: natural sound required (D63)"))
        else:
            v = subprocess.run(["ffmpeg", "-hide_banner", "-i", clip, "-af", "volumedetect", "-vn", "-f", "null", "-"], capture_output=True, text=True).stderr
            mean = re.search(r"mean_volume: (-?[\d.]+)", v); peak = re.search(r"max_volume: (-?[\d.]+)", v)
            mean = float(mean.group(1)) if mean else -91; peak = float(peak.group(1)) if peak else -91
            out.update(mean_db=mean, peak_db=peak)
            if mean < -60: out["findings"].append(("FAIL", f"clip is silent (mean {mean} dB)"))
            if peak >= -0.1: out["findings"].append(("WARN", "audio clips at 0 dB: check before boosting 2-4x"))
    if prompt:
        from . import logic
        out["findings"] += [("FAIL", f"prompt LG3: {r['text'][:80]}") for r in logic.lint_prompt(prompt, "video", dict(people=False)) if r["rule"] == "LG3"]
    if transcript:
        for m in re.finditer(FAKE_SFX_RX, transcript, re.I):
            if not re.search(r"\bno\s+$", transcript[max(0, m.start() - 4):m.start()], re.I): out["findings"].append(("FAIL", f"fake/added sound heard: '{m.group(0)}'"))
    out["ok"] = not any(s == "FAIL" for s, _ in out["findings"]); return out


def final_checks_variants(variants, **kw):
    """Run final_checks on EVERY song variant with its own timeline (Omar t220: A ACDC kept a jump cut the Free Bird fix removed).
    variants: [{name, path, timeline}]. A variant without a timeline BLOCKs."""
    out = {}
    for v in variants:
        r = final_checks(v["path"], timeline=v.get("timeline"), **kw); out[v.get("name") or v["path"]] = r
    from hookforge import pacing as _pc   # song variants of one video must share an identical video timeline
    same, hashes = _pc.variants_identical([v["path"] for v in variants]) if len(variants) > 1 else (True, {})
    ok = same and not any(p.startswith("BLOCK") for r in out.values() for p in r["problems"])
    return dict(ok=ok, variants_identical=same, video_hashes=hashes, reports=out)
