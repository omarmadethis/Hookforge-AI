"""D106 autonomous concept testing (DRY RUN). Daily: one NEW concept per product = the 20 % innovation slot
(posting.explore_share / D36). New = the format this product has tried least (learning/arms.csv n, lowest first;
never tier X), POC = the format's own evidence list (format_defaults.FORMATS[f]['evidence']) + planner G7 per hook.
Each concept is a full planner plan (G1-G23 gates + D42 lint + G5 quote) placed in approval_queue; nothing generates.
Budget line: innovation credits/day vs 20 % of scheduler.DAILY_CREDIT_CAP (reported, not enforced - Omar picks)."""
import os, datetime
import pandas as pd
from zoneinfo import ZoneInfo
from .config import REPO
from . import planner, approval_queue, fb_caption
from .format_defaults import FORMATS

PT = ZoneInfo("America/Los_Angeles")
INNOVATION_SHARE = 0.20
from . import products as _products
PRODUCTS = _products.active()   # D117: retired products excluded; see config/products.json

def _tried(product):
    p = os.path.join(REPO, "learning", "arms.csv")
    if not os.path.exists(p): return {}
    a = pd.read_csv(p); a = a[a["product"] == product]
    return a.groupby("format")["n"].sum().to_dict()

def candidates(product, day):
    tried = _tried(product)
    fs = [f for f, v in FORMATS.items() if v["tier"] != "X"]
    try:                                                      # D109: products with corpus-POC hooks only test POC-backed formats
        from . import profiles
        ph = profiles.load(product).get("poc_hooks")
        if ph: fs = [f for f in fs if f in ph] or fs
    except Exception: pass
    fs.sort(key=lambda f: (tried.get(f, 0), "ABC".index(FORMATS[f]["tier"]) if FORMATS[f]["tier"] in "ABC" else 9, f))
    k = day.toordinal() % max(1, min(3, len(fs)))          # rotate among the 3 least-tried so days differ
    return fs[k:] + fs[:k]

def propose(product, day=None, max_tries=6):
    day = day or datetime.datetime.now(PT).date()
    name = fb_caption.PRODUCTS.get(product, {}).get("name", product.replace("_", " "))
    if not os.path.exists(os.path.join(REPO, "product_profiles", f"{product}.json")):
        return dict(product=product, error=f"no product_profiles/{product}.json - the planner cannot plan this product yet (build the profile first)")
    best = None
    for f in candidates(product, day)[:max_tries]:
        try: p = planner.plan(f"{FORMATS[f]['title']} video for the {name}", override={"format": f, "product_key": product}, mode="original")   # innovation = original mode (D61)
        except Exception as e: continue
        if not p.get("gens"): continue
        from . import runner
        pf_ok = runner.preflight(p)["ok"]
        score = (p["gates"]["ok"] and pf_ok, p["gates"]["ok"], -len(p["gates"]["blocks"]))
        if best is None or score > best[0]: best = (score, f, p)
        if p["gates"]["ok"] and pf_ok: break
    if best is None: return dict(product=product, error="planner produced no plan")
    _, f, p = best
    iid = f"concept_{day.isoformat()}_{product}_{f}"
    return approval_queue.queue(iid, "concept_test", p, why=f"innovation slot: {f} {FORMATS[f]['title']} is this product's least-tried format (arms n={_tried(product).get(f, 0)})",
                                poc=FORMATS[f]["evidence"][:3], product=product, extra=dict(format=f, day=day.isoformat()))

def daily(day=None, products=None):
    from .scheduler import DAILY_CREDIT_CAP
    items = [propose(p, day) for p in (products or PRODUCTS) if _products.is_active(p)]
    budget = INNOVATION_SHARE * DAILY_CREDIT_CAP; left = budget; rec = []
    ranked = rank(items, day or datetime.datetime.now(PT).date())      # D111: POC x season x page-gap order, not cheapest-first
    import copy
    from . import gates, runner
    for i in items:                                   # D143: lean option = 1 start-frame still per gen, same 1080p hook + clips
        if i.get("plan") and i.get("ready_for_approval"):
            lp = copy.deepcopy(i["plan"])
            for g in lp.get("gens") or []:
                if g.get("start_frame"): g["start_frame"]["n"] = 1
            lq = gates.quote(lp)
            lp["quote"] = lq
            i["lean"] = dict(option="lean_1_still", still_variants=1, credits=lq["total"], plan=lp,
                             approval_file_draft=dict(runner.approval_template(lp, i["id"] + "_lean", credit_cap=lq["total"]), approved_by="", approved_at_pt="", approval_quote=""))
    opt = {}
    for i in ranked:                                  # full if it fits, else the lean option automatically (D143)
        if not i.get("ready_for_approval"): continue
        if i["credits"] <= left: rec.append(i["id"]); opt[i["id"]] = "full"; left -= i["credits"]
        elif i.get("lean") and i["lean"]["credits"] <= left: rec.append(i["id"]); opt[i["id"]] = "lean_1_still"; left -= i["lean"]["credits"]
    for i in items:
        if i.get("id"):
            i["recommended_today"] = i["id"] in rec; i["recommended_option"] = opt.get(i["id"])
            path = os.path.join(approval_queue.DIR, i["id"] + ".json"); import json; json.dump(i, open(path, "w"), indent=1, ensure_ascii=False, default=str)
    tot = sum(i.get("credits", 0) for i in items)
    return dict(items=items, ranking=[dict(id=i["id"], score=i["rank_score"], rationale=i["rationale"]) for i in ranked], proposed_credits=tot, innovation_budget=budget, recommended=rec, recommended_options=opt, recommended_credits=budget - left,
                ready=sum(1 for i in items if i.get("ready_for_approval")))

# ---------------- D111: cross-product ranking (when the 20 % budget only fits one or a few) ----------------
import re as _re, math as _math
_NUM = _re.compile(r"(\d+(?:\.\d+)?)\s*([KM])\b")
CHRISTMAS = {"grinch_robe", "heatjams", "cozyjams", "grinchmelt_mug", "merryfire", "merryglow_lights", "jollyglow_curtain"}
SKI = {"brickhood_mask", "minionmask"}
W_POC, W_SEASON, W_GAP = 0.5, 0.3, 0.2

def _views(texts):
    best = 0
    for t in texts:
        for n, u in _NUM.findall(str(t)): best = max(best, float(n) * (1e6 if u == "M" else 1e3))
    return best

def poc_strength(item):
    """0-1: log-scaled best cited views (format evidence + product poc_sources + own proven reels of that format)."""
    from . import profiles
    pr = profiles.load(item["product"]); f = item.get("format")
    own = max([x["best_views"] for x in pr.get("proven_formats", []) if x["format"] == f] or [0])
    hook_why = ((item.get("plan") or {}).get("hook") or {}).get("why", "")
    v = max(own, _views([hook_why]), _views(pr.get("poc_sources") or []))      # this product's own / cited POC first
    if not v: v = 0.5 * _views(item.get("poc") or [])                          # generic format evidence only, half weight
    return (min(1.0, max(0.0, (_math.log10(v) - 4) / 3)) if v > 1 else 0.0), v      # 10K -> 0, 10M -> 1

def season_fit(product, day):
    """0-1 timing score + reason. Christmas ramps Oct 1 -> Dec 15 peak; US midterms 2026-11-03 for TrumpGlow;
    ski season opens ~Nov 15; pets evergreen."""
    d = day
    if product in CHRISTMAS:
        peak = datetime.date(d.year, 12, 15); start = datetime.date(d.year, 10, 1)
        s = 0.2 if d < start or d > datetime.date(d.year, 12, 24) else min(1.0, 0.4 + 0.6 * (d - start).days / (peak - start).days)
        return round(s, 2), f"{(datetime.date(d.year, 12, 25) - d).days} days to Christmas"
    if product == "trumpglow":
        k = (datetime.date(2026, 11, 3) - d).days
        return (1.0 if 0 <= k <= 21 else 0.5), (f"{k} days to the Nov 3 midterms" if k >= 0 else "post-election")
    if product in SKI:
        k = (datetime.date(d.year, 11, 15) - d).days
        return (round(max(0.3, 1 - k / 60), 2) if k > 0 else 1.0), (f"{k} days to ski-season opening" if k > 0 else "ski season on")
    return 0.5, "evergreen"

def page_gap(product, day):
    """0-1: days since the product's last own post (features.csv 'posted'), 14+ days = 1.0; never posted = 1.0."""
    from . import profiles
    names = set(profiles.load(product).get("corpus_products") or [])
    p = os.path.join(REPO, "data", "features", "features.csv"); last = None
    if os.path.exists(p):
        f = pd.read_csv(p, usecols=["source", "product", "posted"], low_memory=False)
        ts = pd.to_datetime(f[(f.source == "own") & f["product"].isin(names)].posted, errors="coerce").dropna()
        if len(ts): last = ts.max().date()
    if last is None: return 1.0, "never posted"
    g = (day - last).days
    return round(min(1.0, max(0.0, g / 14)), 2), f"last own post {g} days ago"

W_REF = 0.15                 # D134 bonus on top of the 0.5/0.3/0.2 blend (transfer from all 11 products' corpus)

def rank(items, day):
    """Score every concept; best first (ready ones before blocked) with a one-line rationale each."""
    out = []
    for i in items:
        if not i.get("id"): continue
        if not _products.is_active(i.get("product")): continue   # D117
        ps, v = poc_strength(i)
        from . import perf_feedback as _pf; hw = _pf.weight(i["product"], "hook", i.get("format")); ps = min(1.0, ps * hw)   # D119
        ss, sr = season_fit(i["product"], day); gs, gr = page_gap(i["product"], day)
        from . import ref_miner as _rm; rb = _rm.boost(i["product"], i.get("format"))          # D134: cross-product transfer evidence
        sc = round(W_POC * ps + W_SEASON * ss + W_GAP * gs + W_REF * rb, 3)
        i["rank_score"] = sc; i["rank_parts"] = dict(poc=round(ps, 2), poc_views=int(v), season=ss, gap=gs, ref=rb)
        i["rationale"] = (f"{i['product']} {i.get('format')}: {sc} = POC {ps:.2f} (best cited {int(v):,} views) + season {ss} ({sr}) "
                          f"+ page gap {gs} ({gr}) + ref {rb}; {i['credits']} cr" + (f"; perf weight x{hw}" if hw != 1.0 else "") + ("" if i.get("ready_for_approval") else "; NOT READY (gate/lint block)"))
        out.append(i)
    return sorted(out, key=lambda i: (not i.get("ready_for_approval"), -i["rank_score"], i["credits"]))

# ---------------- D135 weekly batch ----------------
import json, re
def weekly(start=None, write=True):
    """Fill every calendar slot with the FEWEST new videos: one video per product serves one slot on each of its pages
    (same footage, distinct caption per page); a page never gets the same video twice. Videos needed per product =
    max slots that product has on any one page. Concepts are the product's passing formats ranked by rank()
    (POC/season/gap/ref transfer); if fewer pass than needed, the best format repeats with a different hook variant.
    Output learning/weekly_batch/<start>.json + ONE approval-queue item (kind weekly_batch) quoting total credits.
    Nothing is generated."""
    from . import content_calendar, hook_variants, runner, worlds
    from .e2e_dryrun import caption_for
    import collections
    cal = content_calendar.week(start, write=False); start_d = datetime.date.fromisoformat(cal["start"])
    per = collections.defaultdict(lambda: collections.defaultdict(list))
    for s in cal["slots"]: per[s["product"]][s["page"]].append(s)
    batch, total, slot_map = [], 0.0, []
    for pk, pages in per.items():
        need = max(len(v) for v in pages.values())
        name = fb_caption.PRODUCTS.get(pk, {}).get("name", pk.replace("_", " ")); plans = []
        for f in candidates(pk, start_d):
            try: p = planner.plan(f"{FORMATS[f]['title']} video for the {name}", override={"format": f, "product_key": pk}, mode="original")
            except Exception: continue
            if p.get("gens") and p["gates"]["ok"] and runner.preflight(p)["ok"]:
                plans.append(dict(id=f"wk_{start_d}_{pk}_{f}", product=pk, format=f, plan=p, credits=p["quote"]["total"], ready_for_approval=True))
        ranked = rank(plans, start_d)
        if not ranked: batch.append(dict(product=pk, error="no passing concept")); continue
        from . import ref_miner
        norm = lambda t: " ".join(re.findall(r"[a-z0-9']+", t.lower()))
        hook_pool, seen_h = [], set()
        def addh(c, text, src):
            if text and norm(text) not in seen_h and not hook_variants.gate(text, pk) or (text and c is not None and norm(text) not in seen_h and src == "concept"):
                seen_h.add(norm(text)); hook_pool.append((c, text, src))
        for c in ranked: addh(c, c["plan"]["hook"]["text"], "concept")
        for h in hook_variants.for_concept(dict(product=pk, plan=ranked[0]["plan"]), n=10)["hooks"]: addh(ranked[0], h["text"], "hook_variant")
        vids = []
        for k in range(need):
            c, hook, src = hook_pool[k] if k < len(hook_pool) else (hook_pool[k % len(hook_pool)][0], hook_pool[k % len(hook_pool)][1], "REUSED hook")
            vids.append(dict(video=f"{pk}_V{k + 1}", concept=c["id"], format=c["format"], hook_override=hook, hook_source=src,
                             credits=c["credits"], rank_score=c["rank_score"], rationale=c["rationale"]))
            total += c["credits"]
        # caption pool: each page's own variant first, then fb_caption ranks + gated text variants; one caption is never
        # used twice on a page, and the same video never carries the same caption on two pages
        pool = []
        for pg in pages:
            sv = pages[pg][0]["service"]
            for r in range(4):
                try:
                    t = caption_for(pk, ranked[0]["plan"], sv, pg)["text"] if r == 0 else fb_caption.generate(pk, ranked[0]["plan"], platform=sv, rank=r)["text"]
                    if t and t not in pool: pool.append(t)
                except Exception: pass
        for cpt in hook_variants.for_concept(dict(product=pk, plan=ranked[0]["plan"]), n=10)["captions"]:
            if cpt["text"] not in pool: pool.append(cpt["text"])
        for t in (worlds.WORLDS.get(pk) or {}).get("caption_extra", []):     # D144: curated product-fit winners (adapted POC)
            if t not in pool: pool.insert(0, t)
        cta = hook_variants.CTA.get(pk)
        for v in vids:                                           # each video's own hook doubles as a caption line
            t = v["hook_override"] + (f" {cta}" if cta and cta.split()[1] not in v["hook_override"] else "")
            if hook_variants.words(t) <= 12 and t not in pool: pool.append(t)
        from . import publish as _pub, political_lint as _pl
        ownv = {caption_for(pk, ranked[0]["plan"], pages[pg][0]["service"], pg)["text"] for pg in pages}
        pool = [t for t in pool if (t in ownv or hook_variants.words(t.split("#")[0]) <= 12) and not any(re.search(rx, t, re.I) for rx in (worlds.WORLDS.get(pk) or {}).get("caption_forbidden", []))
                and not _pub.is_listing(t)                                                         # D138
                and not (pk in _pl.POLITICAL and any(r == "PL6" for r, _, _ in _pl.lint_text(t)))]     # D137: no group-mocking captions
        def ctext(t):                          # D139: the caption's own line - hashtags, emoji and the SAY CTA don't make it distinct
            b = t.split("#")[0]; pre = " ".join(re.findall(r"[a-z0-9']+", re.split(r"(?i)\bSAY\b", b)[0].lower()))
            return pre or " ".join(re.findall(r"[a-z0-9']+", b.lower()))
        own = {pg: caption_for(pk, ranked[0]["plan"], pages[pg][0]["service"], pg)["text"] for pg in pages}
        used_pg = collections.defaultdict(set); used_vid = collections.defaultdict(set)
        for pg, sl in pages.items():
            for k, sx in enumerate(sorted(sl, key=lambda s: s["day"])):
                v = vids[k]
                order = [own[pg]] + [t for t in pool if t != own[pg]]
                txt = next((t for t in order if ctext(t) not in used_pg[pg] and ctext(t) not in used_vid[v["video"]]), None) or f"(NEEDS A NEW CAPTION - pool exhausted)"
                used_pg[pg].add(ctext(txt)); used_vid[v["video"]].add(ctext(txt))
                if not txt.startswith("(NEEDS"): txt = _pub.ensure_say(txt, (worlds.WORLDS.get(pk) or {}).get("keyword"))   # D148
                slot_map.append(dict(day=sx["day"], page=pg, product=pk, video=v["video"], caption=txt))
        batch.append(dict(product=pk, videos_needed=need, slots=sum(len(v) for v in pages.values()), videos=vids))
    # distinct caption per page per day/video check
    def _ct(t):
        b = t.split("#")[0]; pre = " ".join(re.findall(r"[a-z0-9']+", re.split(r"(?i)\bSAY\b", b)[0].lower()))
        return pre or " ".join(re.findall(r"[a-z0-9']+", b.lower()))
    seen = collections.Counter((m["page"], _ct(m["caption"])) for m in slot_map)
    out = dict(start=cal["start"], slots=len(cal["slots"]), new_videos=sum(b.get("videos_needed", 0) for b in batch), total_credits=total,
               per_video_credits=sorted({v["credits"] for b in batch for v in b.get("videos", [])}), batch=batch, slot_map=sorted(slot_map, key=lambda m: (m["day"], m["page"])),
               repeated_captions_on_a_page=[k for k, n in seen.items() if n > 1], nothing_generated=True)
    if write:
        d = os.path.join(REPO, "learning", "weekly_batch"); os.makedirs(d, exist_ok=True)
        json.dump(out, open(os.path.join(d, f"{cal['start']}.json"), "w"), indent=1, ensure_ascii=False, default=str)
        it = dict(id=f"weekly_batch_{cal['start']}", kind="weekly_batch", product=None, status="AWAITING_OMAR_APPROVAL",
                  created_pt=datetime.datetime.now(PT).isoformat(timespec="seconds"), credits=total, credit_cap=total, ready_for_approval=True,
                  why=f"{out['new_videos']} new videos fill all {out['slots']} calendar slots ({cal['start']} week); each video reused across its product's pages with distinct captions",
                  rationale="; ".join(f"{b['product']}: {b.get('videos_needed')} videos" for b in batch), batch_file=f"learning/weekly_batch/{cal['start']}.json",
                  note="approve per video or the whole batch; each video still goes through its own approval file + runner gate")
        from . import lean_plan                       # D143: the lean 1080p-hook plan is the recommended option when it passes D142
        lw = lean_plan.write(out)["lean"]
        if lw["near_duplicate_ok"]:
            it.update(recommended_option="lean_1080p_hook", credits=lw["total_credits"], credit_cap=lw["total_credits"], standard_credits=total,
                      lean_file=f"learning/weekly_batch/{cal['start']}_lean.json")
        else: it.update(recommended_option="standard", lean_blocked=lw["near_duplicate_violations"])
        json.dump(it, open(os.path.join(approval_queue.DIR, it["id"] + ".json"), "w"), indent=1, ensure_ascii=False)
    return out
