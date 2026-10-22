"""Brief -> plan (Phase D). parse_brief() resolves product + format; plan() builds the full production plan:
fit verdict + why-this-format, world-adapted hook, packed body gens, prompts (suffix/flag/casting checked), text cards,
proven music + caption, posting slot, credit estimate vs budget, mock-source map for the animatic.
"""
import os, re, json, glob
import pandas as pd
from .config import REPO, CREDITS, CREDIT_BUDGET_PER_VIDEO, CREDIT_BUDGET_VARIANT, HIT_ABS_VIEWS, JK_FLIPS, BANNED_CTA_WORDS, PACK_CUT_WINDOW, race_targeted
from .format_defaults import FORMATS
from .bodies import body_for
from .worlds import ADAPTATIONS
from . import profiles, fit, music, prompts as P, plugins, season, recreate, cues as CUES, style as STY

COVER_OPTIONS = [("covered_drape", "F03", r"drape|store unveil"), ("covered_glow", "F01", r"glow.{0,12}cloth|glow under"),
                 ("covered_reveal", "F05", r"covered|tray reveal|muffin tin|under (a|the) (cloth|tray|tin)")]
FORMAT_KEYWORDS = [("F01", r"3-2-1|321|countdown"), ("F04", r"then.?vs.?now|last year|then and now"), ("F02", r"pallet|fake store|fake-store"),
                   ("F03", r"crowd unveil|unveil"), ("F05", r"don'?t show|do not show"), ("F06", r"hard to gift|gift.?difficulty"),
                   ("F16", r"friend|dare|squad"), ("F07", r"callout|calling all"), ("F12", r"cozy ritual|movie night"), ("F14", r"cut.?off"),
                   ("F15", r"pov envy|jealous"), ("F17", r"store shock|run dont walk"), ("F18", r"idea vs|the idea"), ("F10", r"silent")]

def parse_brief(text):
    t = text.lower()
    fmt = next((f for f, rx in FORMAT_KEYWORDS if re.search(rx, t)), None)
    pk = profiles.resolve(t)
    opt = next(((o, f) for o, f, rx in COVER_OPTIONS if re.search(rx, t)), None)
    if opt:
        o, f = opt
        if o == "covered_reveal" and pk != "grinch_robe" and re.search(r"glow|cloth", t): o, f = "covered_glow", "F01"
        if o == "covered_reveal" and pk != "grinch_robe": o, f = "covered_glow", "F01"     # tray/tin reveal is a robe option; others get the innovation glow
        fmt = fmt if (fmt, pk, o) in ADAPTATIONS else f
        opt = o if (fmt, pk, o) in ADAPTATIONS else None
    return dict(brief=text, product_key=pk, format=fmt, variant=bool(re.search(r"variant|multiplier", t)), hook_option=opt,
                slot="experiment" if re.search(r"experiment|explore|test", t) else "core")

def _cut_for(d1, d2):
    cut = 2.0
    if d1 > cut: cut = min(PACK_CUT_WINDOW[1], d1)
    if d2 > 4 - cut: cut = max(PACK_CUT_WINDOW[0], 4 - d2)
    return round(cut, 2)

def _pick_hook(profile, fmt, ad):
    """D149: only <= 8-word lines are eligible (Omar's hard rule, no exceptions) - longer reference lines stay as data."""
    from .gates import HOOK_MAX_WORDS
    from .hook_variants import words as _w
    ok8 = lambda t: _w((t or "").split("→")[0]) <= HOOK_MAX_WORDS
    profile = dict(profile, proven_hooks=[h for h in profile.get("proven_hooks", []) if ok8(h["hook"])],
                   poc_hooks={k: v for k, v in (profile.get("poc_hooks") or {}).items() if ok8(v[0])})
    if ad: ad = dict(ad, hook_lines=[h for h in (ad.get("hook_lines") or []) if ok8(h[0])])
    return _pick_hook_raw(profile, fmt, ad)

def _pick_hook_raw(profile, fmt, ad):
    from .psych import callout_primary
    from .gates import HOOK_MAX_WORDS
    from .hook_variants import words as _w
    if ad and ad.get("hook_lines_first") and ad.get("hook_lines"):
        h = ad["hook_lines"][0]; return dict(text=h[0], tag=h[1], why=h[2])
    own = [h for h in profile["proven_hooks"] if h["format"] == fmt]
    own = sorted(own, key=lambda h: (callout_primary(h["hook"]), -h["views"]))     # PS09: pure audience callouts rank last
    if own:
        h = own[0]; cc = h.get("capcut_cards")
        return dict(text=h["hook"], tag="P", why=f"own winner on this product: {h['reel']} {h['views']:,} views", cards=cc,
                    cards_source=f"CapCut draft of {h['reel']}" if cc else None)
    ph = (profile.get("poc_hooks") or {}).get(fmt)        # D109: corpus-POC hook for products without own winners yet
    if ph:
        parts = [x.strip() for x in ph[0].split("→")]
        return dict(text=parts[0], tag=ph[1], why=ph[2], cards=parts if len(parts) > 1 else None, cards_source="poc_hooks (worlds.py)" if len(parts) > 1 else None)
    if ad and ad.get("hook_lines"):
        h = sorted([x for x in ad["hook_lines"] if not race_targeted(x[0])] or [("", "T", "")], key=lambda x: callout_primary(x[0]))[0]
        if h[0]: return dict(text=h[0], tag=h[1], why=h[2])
    pk = profile["product_key"]
    bad = [w for o, ws in OTHER_WORLD_WORDS.items() if o != pk for w in ws if w not in OTHER_WORLD_WORDS.get(pk, [])] + profile.get("copy_forbidden", [])
    lines = [h for h in FORMATS[fmt]["hook_lines"] if _w(h[0]) <= HOOK_MAX_WORDS and not any(re.search(r"\b" + re.escape(w.lower()) + r"\b", h[0].lower()) for w in bad) and not race_targeted(h[0])]
    lines = sorted(lines, key=lambda h: (h[1] != "P", callout_primary(h[0])))     # off-world copy dropped (e.g. robe 'mom' lines on a fire pit)
    if lines: h = lines[0]; return dict(text=h[0], tag=h[1], why=h[2] + ("" if h[1] == "P" else " (format formula, product-neutral)"))
    return dict(text=f"{profile['display']} 😳", tag="T", why="no on-world proven line for this format: product-name fallback (experiment)")

OTHER_WORLD_WORDS = {"grinch_robe": ["robe", "mom", "wife", "grandma", "cold", "grinch"], "brickhood_mask": ["ski", "mask", "slope"],
                     "merryfire": ["fire", "s'mores", "smores", "movie night"], "grinchmelt_mug": ["mug", "cocoa", "chocolate", "grinch"],
                     "merryglow_lights": ["lights", "tree", "decor"], "jollyglow_curtain": ["curtain", "street", "house"], "purrventure_carrier": ["cat", "pet", "🐾"]}

def hook_variants(profile, fmt, ad, main, k=4):
    """3-4 ranked hook texts for FB's caption/thumbnail test + IG Trial Reels (gap G4). Same video, 0 extra credits."""
    pk = profile["product_key"]; bad = [w for o, ws in OTHER_WORLD_WORDS.items() if o != pk for w in ws if w not in OTHER_WORLD_WORDS.get(pk, [])] + profile.get("copy_forbidden", [])
    pool = [dict(text=h["hook"], tag="P", why=f"own {h['reel']} {h['views']:,}") for h in profile["proven_hooks"] if h["format"] == fmt]
    pool += [dict(text=h[0], tag=h[1], why=h[2]) for h in (ad.get("hook_lines") or [])]
    pool += [dict(text=h[0], tag=h[1], why=h[2]) for h in FORMATS[fmt]["hook_lines"] if h[1] in ("P", "F", "T")]
    norm = lambda t: re.sub(r"[^a-z0-9 ]", "", re.sub(r"\s+", " ", t.lower().replace("→", " ").replace("vs..", "vs").replace("vs...", "vs"))).split()
    pool = [x for x in pool if not race_targeted(x["text"])]   # neutral recipient framing only
    key = lambda t: " ".join(w for w in norm(t) if w not in ("vs",))
    mt = " → ".join(main["cards"]) if main.get("cards") and len(main["cards"]) > 1 else main["text"]
    seen, out = {key(mt)}, [dict(main, text=mt, rank=1, role="control (proven)")]
    for tag in ("P", "F", "T"):
        for h in pool:
            t = h["text"]; tl = t.lower()
            if len(out[0]["text"].split("→")) > 1 and "→" not in t: continue
            if h["tag"] != tag or key(t) in seen or "{" in t or any(re.search(r"\b" + re.escape(w) + r"\b", tl) for w in bad): continue
            if tag == "P" and h not in pool[:len(profile["proven_hooks"])] and pk not in ("grinch_robe",) and "HJ" in h["why"]: continue
            seen.add(key(t)); out.append(dict(h, rank=len(out) + 1, role="experiment (transfer)" if tag == "T" else "variant",
                                              share_cta=bool(re.search(r"\bsend this\b", tl))))
            if len(out) >= k: return out
    return out

def cover_frames(shots, cards, fmt, body, k=3):
    """2-4 cover candidates: hook frame with product legible (not F04), activation, payoff/reveal."""
    bd = body if isinstance(body, dict) else {}
    pick = []
    if fmt != "F04": pick.append(("hook", shots[0][1] + 0.3, "product legible at 0 s + hook text"))
    for role, code in (("activation", bd.get("activation_shot")), ("payoff", bd.get("payoff_shot"))):
        s = next((x for x in shots if x[0] == code), None)
        if s: pick.append((role, round((s[1] + s[2]) / 2, 2), f"{code} mid-shot"))
    if fmt == "F04" and cards: pick.append(("now_reveal", round(cards[-1]["t"] + 0.5, 2), "'now' card over the reveal"))
    return [dict(role=r, t=round(t, 2), why=w) for r, t, w in pick[:k]]

def _mock_source(profile, fmt):
    c = pd.read_csv(f"{REPO}/private/corpus/corpus.csv", low_memory=False)
    g = c[(c.source == "own") & c["product"].isin(profile["corpus_products"]) & c.file.notna()].copy()
    if g.empty: return None          # D109: new products with no own reels (an empty object mask selected columns -> KeyError 'views')
    g = g[g.file.map(lambda f: os.path.exists(str(f))).astype(bool)]
    g["views"] = pd.to_numeric(g["views"], errors="coerce")
    same = g[g.format == fmt].sort_values("views", ascending=False, na_position="last")
    pick = same.iloc[0] if len(same) else (g.sort_values("views", ascending=False, na_position="last").iloc[0] if len(g) else None)
    if pick is None: return None
    v = pd.to_numeric(pick.views, errors="coerce")   # NaN-crash fix (PurrVenture own reels have no view counts yet)
    return dict(key=pick.key, file=pick.file, views=(None if pd.isna(v) else int(v)), same_format=bool(len(same)))

def _plan_core(brief, force=False, override=None, mode=None):
    """mode: 'recreate' (DEFAULT, D61) when refs/recreate/<product>.json exists, else 'original'. Pass mode='original' to force the
    format-template planner (that path is now the 20 % innovation slot only)."""
    b = parse_brief(brief)
    if override: b.update({k: v for k, v in override.items() if v is not None})
    if not b["product_key"]: raise ValueError(f"unknown product in brief: {brief}")
    if mode != "original":
        from . import recreate_mode
        rp = recreate_mode.build(b["product_key"])
        if rp is not None:
            rp.update(status="OK", brief=b); return rp
        if mode == "recreate": raise ValueError(f"no recreate spec for {b['product_key']} (refs/recreate/{b['product_key']}.json)")
    prof = profiles.load(b["product_key"])
    if not b["format"]:
        b["format"] = fit.rank(prof, 1)[0]["format"]; b["format_auto"] = True
    fmt = b["format"]; F = FORMATS[fmt]
    a = fit.assess(prof, fmt)
    alts = [dict(format=r["format"], title=r["title"], verdict=r["verdict"], score=r["score"]) for r in fit.rank(prof, 4) if r["format"] != fmt][:3]
    if a["verdict"] == "REJECT" and not force:
        return dict(status="REJECTED", brief=b, fit=a, alternatives=alts)
    if a["verdict"] == "WEAK": b["slot"] = "experiment"
    ad = ADAPTATIONS.get((fmt, prof["product_key"], b.get("hook_option"))) or ADAPTATIONS.get((fmt, prof["product_key"])) or {}
    if ad.get("experiment_only"): b["slot"] = "experiment"          # innovation-slot hook options (20% budget)
    ctx = {k: v for k, v in prof.items() if isinstance(v, str)}
    ctx.update(room=ad.get("room", prof["room"]))
    body = (F.get("body_override") or {}).get(prof["category"]) or body_for(prof["category"])
    shots = body if isinstance(body, list) else body["shots"]
    shots = [list(s) for s in shots]
    bo = prof.get("body_override") or {}
    for sh in shots:
        if sh[0] in bo: sh[0], sh[3] = bo[sh[0]][0], bo[sh[0]][1]
    if isinstance(body, dict):
        body = dict(body); body["activation_shot"] = bo.get(body.get("activation_shot"), (body.get("activation_shot"),))[0]
        body["payoff_shot"] = bo.get(body.get("payoff_shot"), (body.get("payoff_shot"),))[0]
    has_proof = any(sh[0] == "PROOF" for sh in shots)
    shots = STY.ensure_hands_on(shots, prof.get("hands_word") or prof["product"])   # D110: merryglow "hands on the tree lights" = GF-Q5 generic install
    # --- gens
    gens, hook_shots = [], [s for s in shots if s[4] == "H"]
    setting = ad.get("setting") or prof["settings"][0]
    us_cues = CUES.for_world(prof["product_key"], setting)
    hook_prompt = P.finish(P.fill(ad.get("hook_prompt") or F["hook_prompt_original"], ctx), us_cues[:1])
    hook_still = P.still(P.fill(ad.get("startframe") or F["startframe_prompt"], ctx), us_cues)
    gens.append(dict(id="H", model="seedance_2_5", res="1080p", dur=4, shots=[s[0] for s in hook_shots], prompt=hook_prompt,
                     start_frame=dict(model="gpt_image_2", prompt=hook_still), credits=CREDITS["body_720p_4s"] + CREDITS["still_gpt_image_2"]))
    for gid in sorted({s[4] for s in shots if s[4] != "H"}):
        ss = [s for s in shots if s[4] == gid]
        d1, d2 = ss[0][2] - ss[0][1], ss[1][2] - ss[1][1]
        cut = _cut_for(d1, d2)
        gp = P.body_gen([(ss[0][0], d1, ss[0][3]), (ss[1][0], d2, ss[1][3])], cut, ctx, prof["sounds"], us_cues[:1])
        # D60: gens that start before the reveal shot get an UNLIT start frame (activation products only)
        rv = next((i for i, s in enumerate(shots) if ctx.get("activation_result") and (s[0].startswith("LIT") or s[0] == (body.get("payoff_shot") if isinstance(body, dict) else None))), None)
        unlit = rv is not None and shots.index(ss[0]) < rv
        gs = P.body_still(ss[0][3], ctx, setting, us_cues, unlit=unlit)
        gens.append(dict(id=gid, model="seedance_2_5", res="720p", dur=4, cut=cut, shots=[ss[0][0], ss[1][0]], prompt=gp,
                         start_frame=dict(model="gpt_image_2", prompt=gs), credits=CREDITS["body_720p_4s"] + CREDITS["still_gpt_image_2"],
                         trims={ss[0][0]: [round(cut - d1, 2), cut], ss[1][0]: [cut, round(cut + d2, 2)]}))
    # MP2-2: proven recreate workhorse as the hook alternative when we own the winning source video (robe today)
    if prof["product_key"] == "grinch_robe":
        rp = recreate.p1("grinch_robe", source_object="grey robe" if fmt != "F01" else "folded blanket on the tray",
                         bg_object="couch" if fmt != "F01" else "kitchen", action="sitting and relaxing on the couch" if fmt != "F01" else "holding the tray",
                         subj="she", pos="her", hood=(fmt != "F01"))
        gens[0]["alt_recreate"] = dict(prompt=rp, source=recreate.P1_SOURCE, refs=dict(video_1=f"own winner source clip ({(_mock_source(prof, fmt) or {}).get('key')})",
                                       image_1="product photo", image_2="background still (GPT Image 2 start frame)"),
                                       checks=recreate.check(rp, "grinch_robe")["problems"], rolls=1,
                                       note="video-reference billing may differ from 64 cr; confirm on first live run")
    if prof.get("poc_sources") and not _mock_source(prof, fmt):     # D109: no own reel to cite -> each shot cites the corpus POC it adapts
        for g in gens: g.setdefault("poc", "; ".join(prof["poc_sources"][:2]))
    for g in gens:
        rc = recreate.check(g["prompt"], prof["product_key"])
        if rc["slot"] == "experiment": b["slot"] = "experiment"
        g["recreate_checks"] = rc["problems"]
    hook_end = max(s[2] for s in hook_shots)
    for s in hook_shots: pass
    # --- text cards
    hook = _pick_hook(prof, fmt, ad)
    end = shots[-1][2]
    bd = body if isinstance(body, dict) else {}
    act = next((s[1] for s in shots if s[0] == bd.get("activation_shot")), shots[len(shots) * 2 // 3][1])
    pay = next((s[1] for s in shots if s[0] == bd.get("payoff_shot")), shots[-1][1])
    anchors = dict(activation=act, end=end, first_body_cut=hook_end, payoff_reveal=pay, end_or_activation=end)
    parts = [x.strip() for x in hook["text"].split("→")]
    if hook.get("cards") and len(hook["cards"]) >= len(F["text_cards"]):
        parts = hook["cards"][:len(F["text_cards"])] if len(F["text_cards"]) > 1 else [hook["cards"][0]]
    cards = []
    for i, (t0, t1, tpl) in enumerate(F["text_cards"]):
        s0 = anchors.get(t0, t0) if not isinstance(t0, (int, float)) else t0
        s1 = anchors.get(t1, t1) if not isinstance(t1, (int, float)) else t1
        txt = {"{hook}": parts[0] if hook.get("cards") else hook["text"], "{then_card}": parts[0], "{now_card}": parts[-1]}.get(tpl, tpl)
        if tpl == "Vs.." and len(parts) > 1: txt = parts[1]
        if tpl.startswith("JK") and hook.get("cards") and len(hook["cards"]) > 1: txt = hook["cards"][1]
        cards.append(dict(t=round(float(s0), 2), dur=round(float(s1) - float(s0), 2), text=txt, scale=STY.text_scale(txt)))
    if fmt == "F04" and len(hook.get("cards") or []) >= 2:   # D188/D191: then-vs-now = max 2 cards (then | now), never 3+
        ai = next((i for i, s in enumerate(shots) if s[0] == bd.get("activation_shot")), None)
        st = [s[1] for s in shots]; reveal = st[ai + 1] if ai is not None and ai + 1 < len(st) else pay
        two = [hook["cards"][0], hook["cards"][-1]]; bounds = [0, reveal, end]
        cards = [dict(t=round(float(bounds[i]), 2), dur=round(float(bounds[i + 1] - bounds[i]), 2), text=two[i], scale=STY.text_scale(two[i])) for i in range(2)]
    if fmt in ("F04", "F06") and isinstance(hook, dict): hook.setdefault("format", "then-vs-now")
    from .card_count import enforce as _cc_enforce
    _cc_enforce(cards, "then-vs-now" if fmt in ("F04", "F06") else fmt)   # D191: planner can never emit >1 card by default
    style = plugins.text_preset()
    hooks_v = hook_variants(prof, fmt, ad, hook)
    covers = cover_frames(shots, cards, fmt, body)
    import datetime as _dt
    from zoneinfo import ZoneInfo
    post_date = _dt.datetime.now(ZoneInfo("America/Los_Angeles")).date() + _dt.timedelta(days=1)   # explicit PT (box clock may be BST)
    seas = season.phase(post_date, prof)
    # --- music, caption
    tracks, rejected = music.select(prof, fmt, a["video_energy"], b["slot"])
    song = tracks[0] if tracks else None
    caps = prof["proven_captions"]
    if not caps:   # D38 niche rule: a caption proven on a sibling product of the same page (same audience), if it has no off-world words
        from .worlds import WORLDS as _W
        badw = [w for o, ws in OTHER_WORLD_WORDS.items() if o != prof["product_key"] for w in ws if w not in OTHER_WORLD_WORDS.get(prof["product_key"], [])]
        for opk in [k for k, v in _W.items() if k != prof["product_key"] and set(v.get("pages", [])) & set(prof.get("pages", []))]:
            oc = [c for c in (profiles.load(opk).get("proven_captions") or []) if not any(re.search(r"\b" + re.escape(w) + r"\b", c["caption"].lower()) for w in badw)]
            if oc:
                caption = dict(text=oc[0]["caption"], why=f"proven caption on sibling product {opk} of the same page ({oc[0]['views']:,} views) - niche-proven"); break
        else:
            caption = dict(text=F["captions"][0], why="format default (no proven caption on this product) - experiment")
    else:
        caption = dict(text=caps[0]["caption"], why=f"proven caption on this product ({caps[0]['views']:,} views)")
    bad_cta = [w for w in BANNED_CTA_WORDS if w in (caption["text"] + " ".join(c["text"] for c in cards)).lower()]
    # --- slot + credits
    pw = json.load(open(f"{REPO}/learning/posting_windows.json"))
    page = prof["pages"][0]; win = pw.get(page, pw.get("default", {}))
    total = round(sum(g["credits"] for g in gens), 1)
    budget = CREDIT_BUDGET_VARIANT if b["variant"] else CREDIT_BUDGET_PER_VIDEO
    reroll_reserve = round(max(g["credits"] - CREDITS["still_gpt_image_2"] for g in gens), 1)
    checks = []
    for g in gens:
        checks += P.check(g["prompt"], f"{'hook' if g['id']=='H' else 'body'} {g['id']}")
        checks += P.check(g["start_frame"]["prompt"], f"still {g['id']}")
    out = dict(status="PLANNED", brief=b, product=dict(key=prof["product_key"], display=prof["display"], energy=prof["energy"], world=prof["world"]),
               fit=a, why_this_format=a["reasons"], alternatives=alts, setting=setting, adaptation=ad.get("why", "none (format native)"),
               hook_options_available=[dict(format=k[0], option=k[2], experiment_only=bool(v.get("experiment_only")), refs=v.get("refs"), why=v.get("why"))
                                       for k, v in ADAPTATIONS.items() if len(k) == 3 and k[1] == prof["product_key"]],
               hook_option=dict(option=ad.get("option"), refs=ad.get("refs"), reveal_s=ad.get("reveal_s"), cover=ad.get("cover"),
                                cover_variants=ad.get("cover_variants"), experiment_only=bool(ad.get("experiment_only"))) if ad.get("option") else None,
               hook=hook, text_cards=cards, text_style=style,
               shots=[dict(code=s[0], t0=s[1], t1=s[2], desc=P.fill(s[3], ctx), gen=s[4]) for s in shots],
               gens=gens, duration=end, hook_s=hook_end,
               music=dict(pick=song, alternatives=tracks[1:], rejected=rejected[:8]), caption=caption, banned_cta_found=bad_cta,
               posting=dict(page=page, exploit_windows_pt=win.get("exploit"), explore_windows_pt=win.get("explore"), explore_share=win.get("explore_share", 0.2)),
               credits=dict(total=total, budget=budget, within_budget=total <= budget, reroll_reserve_max_1_shot=reroll_reserve,
                            breakdown=[(g["id"], g["res"], g["credits"]) for g in gens], source=CREDITS["source"]),
               prompt_checks=checks, us_cues=us_cues, proof_shot=dict(present=has_proof, spec=prof.get("proof_shot")),
               hook_variants=hooks_v, covers=covers, season=seas,
               posting_checklist=["FB: run the caption/thumbnail test with the hook variants + covers (up to 4)",
                                  "IG: post experiment slots as Trial Reels", "Final file: exported via autoedit.clean_export (metadata/C2PA stripped, D44); preflight asserts none remains"],
               mock_source=_mock_source(prof, fmt), provenance=plugins.provenance())
    # D62 mandatory AUDIENCE-FIT stage: song, every emoji, every card + caption must fit the buyer audience with evidence
    from . import audience_fit
    out["audience_fit"], af_rows = audience_fit.lint_rows(out)
    out["prompt_checks"] = checks + [f"AUDIENCE-FIT {r['rule']}: {r['text']}" for r in af_rows]
    from . import edit_rules                         # EDIT_RULES.md editor defaults + lint
    out["edit_defaults"] = edit_rules.default_timeline(gens); out["edit_lint"] = edit_rules.lint(out)
    out["prompt_checks"] += [f"EDIT {r['rule']} [{r['severity']}]: {r['text']}" for r in out["edit_lint"]["rows"] if r["severity"] == "FIX"]
    return out


def plan(brief, force=False, override=None, mode=None):
    """D69: every plan leaves the planner with G4 resolution enforced (every gen 720p, D181), a per-output quote (G5)
    and the G1-G7 gate report attached. plan['gates']['ok'] False = cannot proceed to quote/approval."""
    from . import product_poc                         # D84 POC defaults (format/world) before planning
    override = product_poc.prepare(brief, override)
    out = _plan_core(brief, force=force, override=override, mode=mode)
    from . import gates
    if out.get("gens"):
        d75(out)
        product_poc.apply(out)                        # D84 POC hook/cards/caption/song + suffix re-check
        out["resolution_fixes"] = gates.enforce_resolution(out)
        out["quote"] = gates.quote(out)
    out["gates"] = gates.run_all(out)
    return out


def d75(out):
    """D75 realism: simple-motion rule on every AI prompt, product refs on start frames + Seedance refs,
    real supplier footage for the reveal when Viral Research has delivered it, and the iPhone grade flag on AI shots."""
    from . import motion_rules, product_refs, real_footage
    from .config import ensure_suffix
    prof = out.get("product") or out.get("profile") or {}
    key = prof.get("key") if isinstance(prof, dict) else str(prof)
    brand = (prof.get("brand") if isinstance(prof, dict) else None) or (key.split("_")[0] if key else None)
    for g in out["gens"]:
        g.setdefault("source", "ai")
        if g["source"] == "ai":
            g["prompt"] = ensure_suffix(motion_rules.simplify_motion(g.get("prompt", ""))); g["grade"] = "iphone_subtle"   # D84: D32 suffix must stay LAST
            if brand:
                try: product_refs.attach_to_gen(g, brand)
                except Exception: pass
            if key:                                   # D84 per-product ref library (refs/<slug>/manifest.json)
                from . import refs_lib; refs_lib.attach(g, key)
    if key: real_footage.use_real_reveal(out, key)
    return out
