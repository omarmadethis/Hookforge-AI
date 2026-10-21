import os
"""D69 AUTOMATIC GATES from Omar's 2026-10-19 corrections. Every gate returns rows {gate, ok, level, msg, poc}.
level: BLOCK (plan cannot proceed) | WARN (shown to Omar, explicit weak-proof flag) | INFO.
G1 song from t=0 at proven in-point (D66)   G2 hook <=8 words, proven formats preferred (D67)
G3 profiles can't ban own-proven items (D68) G4 only hook gens 1080p, rest 720p (planner + quote)
G5 quote counts every image/output; spend tracked from OUR job ids only (shared enterprise account)
G6 no phonk / iOS emoji only / real ambient sound only   G7 every element carries a POC citation; weak proof flagged
G8 start frames approved by Omar before any video call.   G9 camera gaze follows scene type (D70)."""
import csv, datetime, json, os, re
from . import poc_library as L
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PT = __import__("zoneinfo").ZoneInfo("America/Los_Angeles")
LEDGER = os.path.join(REPO, "learning", "spend_ledger.csv")
APPROVALS = os.path.join(REPO, "learning", "approvals")
HOOK_MAX_WORDS = 8
from .config import CREDITS as _CR
PRICES = {"still_gpt_image_2": _CR["still_gpt_image_2"],   # D140: tier price (2k high = 6.5); was 1.0 =  # billed 1 credit per IMAGE (transactions 2026-10-19: 8 images = 8 x -1); old 6.5/3.5 get_cost figures were wrong
           "seedance_2_5_1080p_4s": 64, "seedance_2_5_720p_4s": 28,
          "per_s_1080p": 16, "per_s_720p": 7}
FAKE_SFX = r"(?i)\b(sfx|sound effects?|whoosh|swoosh|boom|riser|sparkle sound|magic chime|ding|cartoon|laser|bass drop|impact hit)\b"
PHONK = r"(?i)phonk|slowed\s*\+?\s*reverb|super slowed|brazilian funk|funk (mandelao|automotivo)|montagem"
def R(gate, ok, msg, level=None, poc=None): return dict(gate=gate, ok=ok, level=level or ("INFO" if ok else "BLOCK"), msg=msg, poc=poc)
def words(t): return len(re.sub(r"[^\w\s'-]", " ", re.sub(r"\{url\}|https?://\S+", "", t or "")).split())
def _songs(): return json.load(open(os.path.join(REPO, "music/songs.json")))
def _song_key(plan):
    m = plan.get("music") or {}; pk = m.get("pick") if isinstance(m.get("pick"), dict) else m
    k = (pk or {}).get("song") or m.get("song_key")
    if k and k not in _songs():
        try:
            from . import music; k = music.canon(k) or k
        except Exception: pass
    return k

# G1
def g1_song(plan, final_video=None, stage="plan"):
    k = _song_key(plan); s = _songs().get(k)
    out = []
    if not k: return [R("G1", False, "no song picked (D64/D66)")]
    if not s:
        lib = [e for e in L.load() if e["kind"] == "song" and e.get("key") == k and e.get("in_point_s") is not None]
        if not lib: out.append(R("G1", False, f"song '{k}' has no proven in-point anywhere (songs.json / music_library.csv)"))
        else:  # in-point known from own drafts; full track must be fetched (music/fetch_song.py on the Mac) before the final export
            fin = stage == "final"
            out.append(R("G1", not fin, f"song '{k}' in-point {lib[0]['in_point_s']}s from own drafts; full track NOT fetched/verified yet -> run music/fetch_song.py before export",
                         level="BLOCK" if fin else "WARN"))
    else:
        v = (s.get("verify") or {}).get("xcorr", 0)
        out.append(R("G1", s.get("in_point_s") is not None and v >= 0.9, f"in-point {s.get('in_point_s')}s ({s.get('in_point_label','')[:50]}), verify xcorr {v}", poc=s.get("source")))
    if float((plan.get("music") or {}).get("delay_s", 0) or 0) > 0: out.append(R("G1", False, "music.delay_s > 0: song must start on frame 0 (move in-point back instead)"))
    if final_video:
        from . import songlay
        sc = songlay.song_start_check(final_video); out.append(R("G1", sc["ok"], f"final audio onset {sc['onset_s']}s (max 0.1)"))
    return out

# G2
def g2_hook(plan):
    hk = (plan.get("hook") or {}).get("text") or ""
    n = words(hk); fm = L.fmt_of(hk); c = L.cite(hk) if hk else None
    # D149: Omar's hard rule - max 8 words, NO exceptions (own past winners included; the D67 own-line WARN is removed)
    out = [R("G2", n <= HOOK_MAX_WORDS and bool(hk), f"hook '{hk}' = {n} words (max {HOOK_MAX_WORDS}, no exceptions)")]
    out.append(R("G2", True, f"proven format {fm}" if fm else "hook not in a proven format (Don't show this to a ___ / POV street JEALOUS / don't walk RUN to [store])",
                 level="INFO" if fm else "WARN"))
    for c in plan.get("text_cards") or []:
        if words(c.get("text")) > HOOK_MAX_WORDS: out.append(R("G2", False, f"card too long ({words(c['text'])} words): {c['text']}"))
    return out

# G3
def g3_profiles(product_profile=None, audience_profile=None):
    from . import proof_guard as PG
    v = PG.audit(product_profile, audience_profile)
    return [R("G3", x["level"] != "BLOCK", f"profile ban on own-proven item: {x}", level=x["level"]) for x in v] or [R("G3", True, "no profile bans contradict own data")]

# G4
def is_hook_gen(g): return g.get("id") == "H" or g.get("role") == "hook" or str(g.get("id", "")).startswith("H")
def expected_res(g): return "1080p" if is_hook_gen(g) else "720p"
def enforce_resolution(plan):
    """Planner-side: force the rule onto the plan (returns list of changes)."""
    ch = []
    for g in plan.get("gens") or []:
        if g.get("res") != expected_res(g): ch.append((g["id"], g.get("res"), expected_res(g))); g["res"] = expected_res(g)
    return ch
def g4_resolution(plan):
    bad = [(g["id"], g.get("res")) for g in plan.get("gens") or [] if g.get("res") != expected_res(g)]
    return [R("G4", not bad, f"resolution violations {bad}" if bad else "hook 1080p, rest 720p")]

# G5
def video_cost(g):
    res, d = g.get("res"), int(g.get("dur", 4))
    if d == 4: return PRICES[f"seedance_2_5_{res}_4s"]
    return PRICES["per_s_1080p" if res == "1080p" else "per_s_720p"] * d
DEFAULT_VARIANTS = 2  # Omar reviews 2 variants per start frame
def quote(plan, variants_per_frame=DEFAULT_VARIANTS, still_price="still_gpt_image_2"):
    """Counts EVERY output: each start-frame variant image is billed, each video clip is billed. Uses expected_res (G4)."""
    lines = []
    for g in plan.get("gens") or []:
        nv = int(g.get("start_frame", {}).get("n") or variants_per_frame or 1) if g.get("start_frame") else 0
        if nv: lines.append(dict(gen=g["id"], item=f"start frame x{nv} images", credits=round(PRICES[still_price] * nv, 2)))
        gg = dict(g, res=expected_res(g)); lines.append(dict(gen=g["id"], item=f"video {gg['res']} {gg.get('dur',4)}s", credits=video_cost(gg)))
    st = sum(l["credits"] for l in lines if "start frame" in l["item"]); vid = sum(l["credits"] for l in lines if "video" in l["item"])
    return dict(lines=lines, stills=round(st, 2), video=round(vid, 2), total=round(st + vid, 2), basis=PRICES)
def g5_quote(plan, **kw):
    q = quote(plan, **kw); pc = plan.get("credits")
    pc = pc.get("total") if isinstance(pc, dict) else pc
    out = [R("G5", True, f"quote {q['total']} credits (stills {q['stills']} counted per image, video {q['video']})")]
    if isinstance(pc, (int, float)) and abs(pc - q["total"]) > 0.5: out.append(R("G5", True, f"plan.credits {pc} differs from per-output quote {q['total']}; use the quote", level="WARN"))
    return out
LEDGER_COLS = ["ts_pt", "run_id", "item", "job_ids", "credits"]   # shared schema (also written by the live workers)
def ledger_add(run_id, job_id, step, credits, model="", kind=""):
    new = not os.path.exists(LEDGER)
    with open(LEDGER, "a", newline="") as f:
        w = csv.writer(f)
        if new: w.writerow(LEDGER_COLS)
        w.writerow([datetime.datetime.now(PT).isoformat(timespec="minutes")[:16], run_id, " ".join(x for x in (model, step, kind) if x), job_id, credits])
def ledger_rows():
    if not os.path.exists(LEDGER): return []
    return list(csv.DictReader(open(LEDGER)))
def our_spend(run_id=None):
    """Spend from OUR job ids only (dedup by job_ids). Account balance deltas are NOT used (shared enterprise workspace)."""
    seen, t = set(), 0.0
    for r in ledger_rows():
        j = r.get("job_ids") or r.get("job_id")
        if (run_id and r["run_id"] != run_id) or j in seen: continue
        seen.add(j); t += float(r["credits"] or 0)
    return round(t, 2)

# G6
def g6_bans(plan):
    from . import audience_fit as AF
    out = []; k = _song_key(plan) or ""; s = _songs().get(k, {})
    blob = f"{k} {s.get('song','')} {json.dumps(plan.get('music') or {}, default=str)}"
    out.append(R("G6", not re.search(PHONK, blob), "no phonk" if not re.search(PHONK, blob) else f"phonk detected in music: {k}"))
    rend = (plan.get("text_style") or {}).get("emoji_render", "apple_ios")
    out.append(R("G6", rend == "apple_ios", f"emoji render {rend} (Apple iOS PNGs only)"))
    bad = []
    for g in plan.get("gens") or []:
        pr = g.get("prompt", "") or ""
        for m in re.finditer(FAKE_SFX, pr):   # negative phrasing ("no whoosh", "no SFX") is allowed
            if not re.search(r"(?i)\b(no|without|never|avoid|zero)\b[^.]{0,40}$", pr[:m.start()]): bad.append((g["id"], m.group(0)))
    out += [R("G6", False, f"gen {i} prompt asks for fake SFX '{w}' (real ambient only)") for i, w in bad] or [R("G6", True, "prompts ask for real ambient sound only")]
    return out

# G7
def g7_poc(plan):
    """Every element must cite POC. Elements: hook, caption, song, format (why_this_format), each gen (shot from a reference)."""
    out = []
    hk = (plan.get("hook") or {}).get("text") or ((plan.get("text_cards") or [{}])[0].get("text"))
    c = L.cite(hk) if hk else None
    if hk and not c and plan.get("references"): c = _ref_cite(plan, list(plan["references"]))
    if hk and not c and re.search(r"own|EXT-|views|proven", str((plan.get("hook") or {}).get("why"))): c = dict(source=plan["hook"]["why"], strength="ok")
    out.append(_cite("hook", hk, c))
    cap = plan.get("caption"); ct = cap.get("text") if isinstance(cap, dict) else cap
    cc = L.cite(ct) if ct else None
    if ct and not cc and isinstance(cap, dict) and re.search(r"views|proven|own", str(cap.get("why"))): cc = dict(source=cap["why"], strength="ok")
    if ct: out.append(_cite("caption", ct, cc))
    k = _song_key(plan); se = [e for e in L.load() if e["kind"] == "song" and e.get("key") == k and L.alive(e)]
    out.append(_cite("song", k, max(se, key=lambda e: (e.get("strength") == "strong", e.get("views") or 0)) if se else None))
    wf = plan.get("why_this_format") or (plan.get("provenance") or {}).get("source") or \
        ("recreate of " + ", ".join(f"{k} ({v.get('views') or v.get('what', '')[:40]})" for k, v in plan["references"].items()) if plan.get("references") else None)
    out.append(_cite("format", str(wf)[:60] if wf else None, dict(source=str(wf), strength="ok") if wf and re.search(r"\d|own|ref|views", str(wf)) else None))
    shots = plan.get("shots") or []
    for sh in shots:   # per-shot citation wherever the shot carries reference timestamps
        if isinstance(sh, dict) and sh.get("ref"):
            out.append(_cite(f"shot {sh.get('code')}", sh.get("code"), _ref_cite(plan, sh["ref"])))
    for g in plan.get("gens") or []:
        gs = [sh for sh in shots if isinstance(sh, dict) and sh.get("gen") == g["id"]]
        if gs and all(sh.get("ref") for sh in gs): continue   # covered per shot
        src = g.get("poc") or g.get("ref") or (plan.get("provenance") or {}).get("source") or plan.get("mock_source")
        out.append(_cite(f"gen {g['id']}", g["id"], dict(source=str(src)[:120], strength=g.get("poc_strength", "ok")) if src else None))
    return out
def _ref_cite(plan, ref):
    """ref: {ref_key: [t0, t1]} or [ref_key,...] -> citation naming reference, timestamps and views."""
    R_ = plan.get("references") or {}; parts, best = [], 0
    for k in ref:
        meta = R_.get(k) or {}; v = float(meta.get("views") or 0); best = max(best, v)
        ts = ref[k] if isinstance(ref, dict) else None
        own = "omar" in str(meta.get("what", "")).lower() or k.startswith("OMAR")
        parts.append(f"{k}{f' @{ts[0]}-{ts[1]}s' if ts else ''} ({int(v) if v else ('own reel' if own else '?')} views) {meta.get('file') or meta.get('url') or ''}")
        if own: best = max(best, 100_000)   # Omar's own reference reel = proven by his say-so
    return dict(source="; ".join(parts), strength=L.strength(best)) if parts else None
def _cite(el, item, c):
    if not item: return R("G7", False, f"{el}: missing")
    if not c: return R("G7", False, f"{el} '{item}': NO POC citation")
    weak = c.get("strength") == "weak"
    return R("G7", True, f"{el} '{str(item)[:50]}' <- {str(c.get('source'))[:90]}" + (" [WEAK PROOF]" if weak else ""), level="WARN" if weak else "INFO", poc=c.get("id") or c.get("source"))

# G8
def frames_path(run_id):
    from .config import LIVE  # same dir as the video approval file (tests can redirect it)
    return os.path.join(REPO, LIVE.get("approvals_dir", "learning/approvals"), f"{run_id}_frames.json")
def frames_template(run_id, picks):
    """picks: {gen_id: chosen frame file/variant}. Written by the parent ONLY after Omar okays the frames in chat."""
    return dict(run_id=run_id, approved_by="Omar", approval_quote="<Omar's words>", approved_at_pt="<ISO>", picks=picks)
def g8_frames(plan, run_id):
    p = frames_path(run_id)
    if not os.path.exists(p): return [R("G8", False, f"start frames not approved by Omar ({os.path.relpath(p, REPO)} missing); show contact sheet first")]
    a = json.load(open(p)); miss = [g["id"] for g in plan.get("gens") or [] if g["id"] not in (a.get("picks") or {})]
    ok = a.get("approved_by") == "Omar" and not miss and a.get("run_id") == run_id
    return [R("G8", ok, "start frames approved" if ok else f"frame approval invalid (by={a.get('approved_by')}, missing picks {miss})")]

# G9
def g9_gaze(plan):
    from .logic import camera_allowed, CAMERA_RX
    out = []
    for g in plan.get("gens", []):
        shot = dict(allow_camera=g.get("allow_camera"), scene_type=g.get("scene_type", "organic"))
        hits = [m.group(0) for m in CAMERA_RX.finditer(g.get("prompt", ""))]
        if hits and not camera_allowed(shot):
            out.append(R("G9", False, f"{g.get('id')}: camera gaze in an organic scene ({hits[0]}); only staged/planned scenes may look into the lens (D70)"))
        else:
            out.append(R("G9", True, f"{g.get('id')}: gaze OK for scene_type={shot['scene_type']}"))
    return out


# G10-G12 (D72, Omar 2026-10-19 9:25 PM PT)
CTA_URL_RX = r"(?i)(\{url\}|https?://|www\.|\.com\b|get (yours|it|one)\b|link in (bio|comments?)|shop now|order now|buy now)"
CTA_OK_RX = r"(?i)(jk!? ?we sell them|^comment\s+[\"\u201c']?[A-Z]+)"
def g10_onscreen_cta(plan):
    out = []
    for c in (plan.get("text_cards") or []) + ([plan["hook"]] if plan.get("hook") else []):
        t = c.get("text") or ""
        if re.search(CTA_URL_RX, t) and not re.search(CTA_OK_RX, t):
            out.append(R("G10", False, f"on-screen URL/'Get yours' CTA not allowed: '{t}'. Link goes in the post caption/bio only; use 'JK! We sell them' or a comment CTA (Comment \"VOTE\" ...)"))
    return out or [R("G10", True, "no on-screen URL CTA")]
OPENER_MAX_S = 2.0
SHOWCASE_RX = r"(?i)\b(hold(s|ing)? (up|out)|show(s|ing|case)?|display(s|ed)?|close-?up of|rotat\w*[^.]{0,25}(toward|to) the light|turn(s|ing) (it )?to the light|static product)\b"
ACTION_RX = r"(?i)\b(toss|throw|catch|snap|click|stick|press|install|peel|pull|open|plug|drop|slap|clip|swing)\w*\b"
def _shots(plan): return plan.get("shots") or plan.get("timeline") or []
def g11_opener(plan):
    sh = _shots(plan)
    if not sh: return [R("G11", True, "no timeline yet (opener length checked at edit)", level="INFO")]
    s0 = sh[0]; gen = s0.get("gen"); d = 0.0
    for s in sh:
        if s.get("gen") != gen: break
        d += float(s.get("dur") or (float(s.get("t1", 0)) - float(s.get("t0", 0))))
    return [R("G11", True, f"opener {gen} runs {d:.2f}s on screen" + ("" if d <= OPENER_MAX_S + 0.2 else f" > ~{OPENER_MAX_S}s: trim/speed up (Omar: B peel 'way too slow, long and boring')"),
              level="INFO" if d <= OPENER_MAX_S + 0.2 else "WARN")]
def g12_showcase(plan):
    out = []
    for g in plan.get("gens", []):
        pr = g.get("prompt", "")
        if re.search(SHOWCASE_RX, pr) and not re.search(ACTION_RX, pr):
            out.append(R("G12", True, f"{g.get('id')}: product-showcase shot with no action; prefer a toss, snap-on or install", level="WARN"))
    return out or [R("G12", True, "every product shot has an action")]

def g13_motion(plan):
    """D75: AI shots look real only with short, simple motion."""
    from . import motion_rules as MR
    out = []
    for g in plan.get("gens", []):
        if g.get("source") == "real": continue
        for lvl, msg in MR.lint(g.get("prompt", ""), g.get("dur")):
            out.append(R("G13", lvl != "BLOCK", f"{g.get('id')}: {msg}", level=lvl))
    return out or [R("G13", True, "all AI motions short and simple")]


# G14-G19 (Omar feedback log backfill, 2026-10-19 ~11:30 PM PT; see learning/OMAR_FEEDBACK_LOG.md)
VS_RX = r"(?i)(^|\s)vs\.?(\.|\s|$)"
def g14_vs_card(plan):
    """t220: 'Vs..' only in the mid card, never in the first card/hook."""
    cards = plan.get("text_cards") or []
    first = [plan["hook"]] if plan.get("hook") else cards[:1]
    bad = [c.get("text", "") for c in first if re.search(VS_RX, c.get("text") or "")]
    return [R("G14", False, f"'Vs' in the first card '{t}': Vs belongs only in the mid card") for t in bad] or [R("G14", True, "Vs not in first card")]
LINGER_WARN_S, LINGER_BLOCK_S = 2.5, 3.2
KEY_ROLES = {"hook", "opener", "reveal", "payoff", "countdown", "dialogue", "proof"}
def g15_linger(plan):
    """t220: no clip lingers; befores/afters ~1.25 s, reveal ~2.2 s (D74)."""
    out = []
    for i, s in enumerate(_shots(plan)):
        if i == 0 or (s.get("role") or "").lower() in KEY_ROLES or s.get("dialogue"): continue
        d = float(s.get("dur") or (float(s.get("t1", 0)) - float(s.get("t0", 0))))
        if d > LINGER_BLOCK_S: out.append(R("G15", False, f"shot {i} ({s.get('gen')}) lingers {d:.2f}s > {LINGER_BLOCK_S}s; trim to ~1.25-2.2s"))
        elif d > LINGER_WARN_S: out.append(R("G15", True, f"shot {i} ({s.get('gen')}) {d:.2f}s may linger", level="WARN"))
    return out or [R("G15", True, "no lingering shots")]
BANNED_MODEL_RX = r"(?i)\b(kling|seedream|sunburst|veo|sora|wan ?2|hailuo|midjourney|flux)\b"
def g16_models(plan):
    """R11/R12/R13: Seedance 2.5 video only, GPT Image 2 stills only, never end frames."""
    out = []
    for g in plan.get("gens") or []:
        m = f"{g.get('model','')} {(g.get('start_frame') or {}).get('model','')}"
        if re.search(BANNED_MODEL_RX, m): out.append(R("G16", False, f"{g.get('id')}: banned model '{m.strip()}' (Seedance 2.5 + GPT Image 2 only)"))
        if g.get("end_frame") or g.get("end_image") or g.get("last_frame"): out.append(R("G16", False, f"{g.get('id')}: end frame set; never use end frames"))
    return out or [R("G16", True, "Seedance 2.5 / GPT Image 2 only, no end frames")]
DEFAULT_BUDGET = 200
def g17_budget(plan):
    """R15/D18: list cost, stay under budget (default 200 cr unless Omar set plan.budget)."""
    b = plan.get("budget") or DEFAULT_BUDGET; t = quote(plan)["total"]
    return [R("G17", t <= b, f"quote {t} cr vs budget {b}" + ("" if t <= b else ": over budget, needs Omar's OK"))]
GEN_MAX_S = 5
def _long_ok(plan, g):
    if g.get("omar_ok_long"): return True
    try: ap = json.load(open(os.path.join(APPROVALS, "long_gens.json")))["approved"]
    except Exception: return False
    return f"{plan.get('run_id','')}/{g.get('id')}" in ap
def g18_gen_len(plan):
    """R09/D25: every gen <=5 s ('that can be done in 5 tops'); Omar-approved exceptions in learning/approvals/long_gens.json."""
    out = [R("G18", False, f"{g.get('id')}: gen {g.get('dur')}s > {GEN_MAX_S}s") for g in plan.get("gens") or []
           if float(g.get("dur", 4)) > GEN_MAX_S and not _long_ok(plan, g)]
    return out or [R("G18", True, "all gens <=5s")]
EMOJI_RX = r"[\U0001F1E6-\U0001F1FF]{2}|[\U0001F300-\U0001FAFF\u2600-\u27BF]\uFE0F?"
SAD_RX = r"[\U0001F614\U0001F494\U0001F622\U0001F62D\U0001F97A\U0001F61E\U0001F625\U0001F641\u2639\u2764]"
def _emoji_proof():
    """emoji -> best (views, text) across Omar's cards.csv and the POC library (hooks/cards)."""
    import csv, json as _j
    best = {}
    def add(t, v):
        for e in re.findall(EMOJI_RX, t or ""):
            e = e.replace("\uFE0F", "")
            if v and v > best.get(e, (0, ""))[0]: best[e] = (v, t)
    base = os.path.join(os.path.dirname(__file__), "..", "..")
    try:
        for c in csv.DictReader(open(os.path.join(base, "learning", "editing_style", "cards.csv"))): add(c.get("text"), float(c.get("views") or 0))
    except Exception: pass
    try:
        for x in _j.load(open(os.path.join(base, "poc", "poc_library.json"))):
            if x.get("kind") in ("hook", "card", "caption"): add(x.get("text"), float(x.get("views") or 0))
    except Exception: pass
    return best
def g19_emoji(plan):
    """Omar t2xx (corrected 23:30): emoji on a sad/problem card is chosen by POC; 😔 was only a suggestion, never forced.
    WARN when a card's emoji has no viral proof in cards.csv/POC library, or when a sad emoji stands alone (pair it)."""
    out = []; proof = None
    for c in (plan.get("text_cards") or []) + ([plan["hook"]] if plan.get("hook") else []):
        t = c.get("text") or ""; ems = [e.replace("\uFE0F", "") for e in re.findall(EMOJI_RX, t)]
        if not ems: continue
        proof = proof if proof is not None else _emoji_proof()
        for e in ems:
            if e not in proof: out.append(R("G19", True, f"'{t}': emoji {e} has no viral proof (cards.csv/POC) - pick a proven one", level="WARN"))
        if re.search(SAD_RX, t) and len(ems) < 2: out.append(R("G19", True, f"'{t}': lone sad emoji - pair it (e.g. with 🇺🇸)", level="WARN"))
    return out or [R("G19", True, "card emojis proven and paired")]


# G20-G22 (restored 2026-10-19 23:40 PT after an accidental overwrite during the G19 POC rewrite; behaviour per tests/test_feedback_gates.py)
AFTER_RX = r"(?i)\b(animat\w*|cycl\w*|chang\w*|wipe|flicker\w*|moves?|moving|fly|flies|scroll\w*|twinkl\w*|transition\w*)\b"
def g20_afters(plan):
    """Afters are ANIMATED on the product and each after design differs."""
    out = []; seen = {}
    for g in plan.get("gens") or []:
        if "after" not in f"{g.get('role','')} {g.get('id','')}".lower(): continue
        pr = g.get("prompt", "") or ""
        if not re.search(AFTER_RX, pr): out.append(R("G20", False, f"{g.get('id')}: after is static; the design must animate on the product"))
        d = (g.get("design") or "").strip().lower()
        if d and d in seen: out.append(R("G20", False, f"{g.get('id')}: same after design '{d}' as {seen[d]}; afters must differ"))
        if d: seen[d] = g.get("id")
    return out or [R("G20", True, "afters animated and distinct")]
def g21_vs_structure(plan):
    """Then-vs-now: one caption per problem scene, then 'Vs...', then 'Christmas 2026' (or proven 'this year') on the afters."""
    fmt = f"{plan.get('format','')}".lower()
    if not any(k in fmt for k in ("vs", "then_vs_now", "f04")): return [R("G21", True, "not a vs format", level="INFO")]
    t = [c.get("text", "") for c in plan.get("text_cards") or []]
    vi = [i for i, x in enumerate(t) if re.search(VS_RX, x)]
    ok = len(vi) == 1 and 0 < vi[0] < len(t) - 1 and re.search(r"(?i)christmas 2026|this year", t[-1] if t else "")
    return [R("G21", bool(ok), "vs card order OK" if ok else f"vs cards must be problem card(s) -> 'Vs...' -> 'Christmas 2026' on afters; got {t}")]
def g22_post_caption(plan):
    """Every video ships with a proven-converting post caption (POC-cited)."""
    c = plan.get("post_caption") or plan.get("caption")
    txt = c.get("text") if isinstance(c, dict) else c
    if not txt: return [R("G22", False, "no post caption; send a proven-converting caption with each video")]
    poc = c.get("poc") if isinstance(c, dict) else None
    return [R("G22", True, f"post caption '{txt}'" + ("" if poc else " [WEAK PROOF: no POC cite]"), level="INFO" if poc else "WARN")]

def g23_say_not_comment(plan):
    """F93 (Omar 2026-10-20): FB captions use SAY "<KEYWORD>", never "Comment" (engagement-bait demotion). Checks the
    post caption, hook variants and on-screen cards. BLOCK."""
    c = plan.get("post_caption") or plan.get("caption"); txt = c.get("text") if isinstance(c, dict) else (c or "")
    texts = [txt] + [x.get("text", "") for x in plan.get("text_cards") or []] + [v.get("text", "") for v in plan.get("hook_variants") or [] if isinstance(v, dict)]
    bad = [t for t in texts if re.search(r"(?i)\bcomment(ing|s)?\b", t or "")]
    return [R("G23", not bad, f"'Comment' CTA found, use SAY \"<KEYWORD>\": {bad[:2]}" if bad else "CTA uses SAY (no 'Comment')")]

def g24_world(plan, product_profile=None):
    """D113: every gen prompt + start frame must stay inside the product's world (worlds.py forbidden settings + 'never X' clauses).
    D68 respected: a forbidden setting that own >=50K reels prove (and Omar didn't ban) is not enforced."""
    from .worlds import world_conflicts
    from . import proof_guard as PG
    prof = product_profile
    if prof is None or "world" not in prof:
        pk = (plan.get("product") or {}).get("key") if isinstance(plan.get("product"), dict) else plan.get("product_key")
        if not pk: return [R("G24", True, "no product key: world check skipped", level="INFO")]
        from . import profiles; prof = profiles.load(pk)
    out = []
    for g in plan.get("gens") or []:
        for kind, txt in (("video", g.get("prompt")), ("still", (g.get("start_frame") or {}).get("prompt"))):
            for setting, hit in world_conflicts(prof, txt):
                if PG.setting_proof(setting, prof.get("corpus_products")) and not PG.omar_banned(prof, setting): continue
                out.append(R("G24", False, f"{g.get('id')} {kind}: '{hit}' puts {prof['display']} in a {setting}; its world is: {prof['world']}"))
    return out or [R("G24", True, "all settings inside the product world")]

def g25_political(plan):
    """D114: political-content safety lint for TrumpGlow / PatriotGlow (political_lint.py)."""
    from . import political_lint as PLT
    r = PLT.check(plan)
    if not r["applies"]: return [R("G25", True, "not a political product", level="INFO")]
    out = [R("G25", x["level"] != "BLOCK", f"{x['rule']} {x['where']}: {x['msg']}", level=x["level"]) for x in r["rows"]]
    return out or [R("G25", True, "political lint clean (PL1-PL5)")]

def g26_card_count(plan):
    """D188/F106: 1 card by default; 2 only for VS/then-vs-now or a closing caption-below card; never 3+."""
    from .card_count import gate
    fmt = (plan.get("hook") or {}).get("format") or plan.get("format")
    f = gate(plan.get("text_cards") or plan.get("cards") or [], fmt)
    return [R("G26", False, x) for x in f] or [R("G26", True, "card count ok (D188)")]

def run_all(plan, run_id=None, stage="plan", final_video=None, product_profile=None, audience_profile=None):
    """stage: plan (G1-G7) | video (adds G8) | final (adds final audio onset)."""
    rows = g1_song(plan, final_video if stage == "final" else None, stage) + g2_hook(plan) + g3_profiles(product_profile, audience_profile) \
        + g4_resolution(plan) + g5_quote(plan) + g6_bans(plan) + g7_poc(plan) + g9_gaze(plan) + g10_onscreen_cta(plan) + g11_opener(plan) + g12_showcase(plan) + g13_motion(plan) \
        + g14_vs_card(plan) + g15_linger(plan) + g16_models(plan) + g17_budget(plan) + g18_gen_len(plan) + g19_emoji(plan) \
        + g20_afters(plan) + g21_vs_structure(plan) + g22_post_caption(plan) + g23_say_not_comment(plan) + g24_world(plan, product_profile) + g25_political(plan) + g26_card_count(plan)
    if stage in ("video", "final"): rows += g8_frames(plan, run_id or "")
    return dict(ok=all(r["ok"] for r in rows), blocks=[r for r in rows if not r["ok"]], warns=[r for r in rows if r["level"] == "WARN"], rows=rows)
