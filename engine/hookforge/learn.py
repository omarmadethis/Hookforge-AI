"""Learning loop (Phase E). update() re-derives everything after new posts / drafts / gens:
corpus -> CapCut edits -> posting_time (Holm, D36) -> music library -> product profiles -> arm posteriors -> experiments
-> (optional) model re-validation -> dashboard. schedule() turns posteriors into the next day's 5 videos per product
with a 20% innovation budget and the page's best posting windows (+ explore windows).
"""
import os, sys, json, random, subprocess, datetime
import numpy as np, pandas as pd
from .config import REPO, HIT_ABS_VIEWS, INNOVATION_SHARE, POSTS_PER_PRODUCT_PER_DAY
from .worlds import WORLDS
from . import profiles, music, fit

ENG = os.path.join(REPO, "engine")

def _run(mod, timeout=900, cwd=ENG):
    t = datetime.datetime.now()
    r = subprocess.run([sys.executable, "-m", mod] if not mod.endswith(".py") else [sys.executable, mod], cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return dict(step=mod, ok=r.returncode == 0, s=round((datetime.datetime.now() - t).total_seconds(), 1), err=r.stderr[-400:] if r.returncode else "")

def arms():
    """Beta posterior per (product, format): prior from fit score (pseudo-counts), likelihood = own hits/flops on this product."""
    rows = []
    for pk in WORLDS:
        prof = profiles.load(pk)
        for f in fit.FORMATS:
            a = fit.assess(prof, f)
            if a["verdict"] == "REJECT": continue
            own = next((x for x in prof["proven_formats"] if x["format"] == f), None)
            prior_mean = min(0.9, max(0.05, 0.15 + 0.08 * a["score"])); k = 2.0
            al, be = prior_mean * k, (1 - prior_mean) * k
            if own: al += own["hits"]; be += own["n"] - own["hits"]
            rows.append(dict(product=pk, format=f, verdict=a["verdict"], fit_score=a["score"], n=own["n"] if own else 0,
                             hits=own["hits"] if own else 0, alpha=round(al, 2), beta=round(be, 2), mean=round(al / (al + be), 3)))
    # hook-option arms (D53): (format, option) per product; robe covered_reveal prior from the style re-code (robe-only 5/11)
    from .worlds import ADAPTATIONS
    cs = {}
    try: cs = json.load(open(os.path.join(REPO, "style", "covered_stats.json")))
    except Exception: pass
    for (f, pk, opt), ad in ((k, v) for k, v in ADAPTATIONS.items() if len(k) == 3):
        h, n = 0, 0
        if pk == "grinch_robe" and opt in ("covered_reveal", "covered_drape") and cs.get("robe_only"):
            h, n = map(int, cs["robe_only"]["covered"].split("/"))
        al, be = 0.3 * 2 + h, 0.7 * 2 + (n - h)
        rows.append(dict(product=pk, format=f, option=opt, verdict="WEAK" if ad.get("experiment_only") else "OK", fit_score=None, n=n, hits=h,
                         alpha=round(al, 2), beta=round(be, 2), mean=round(al / (al + be), 3)))
    df = pd.DataFrame(rows)
    if "option" not in df: df["option"] = None
    df.to_csv(os.path.join(REPO, "learning", "arms.csv"), index=False); return df

def schedule(pk, date=None, n=POSTS_PER_PRODUCT_PER_DAY, seed=None):
    rng = np.random.default_rng(seed); ar = pd.read_csv(os.path.join(REPO, "learning", "arms.csv"))
    ar = ar[ar["product"] == pk]; prof = profiles.load(pk)
    pw = json.load(open(os.path.join(REPO, "learning", "posting_windows.json"))); win = pw.get(prof["pages"][0], pw.get("default", {}))
    n_explore = max(1, int(round(n * INNOVATION_SHARE))); out = []
    core = ar[ar.verdict.isin(["STRONG", "OK"])]
    for i in range(n - n_explore):
        cnt = pd.Series([o["format"] for o in out]).value_counts() if out else pd.Series(dtype=int)
        cc = core[~core.format.isin(cnt[cnt >= 2].index)] if len(core[~core.format.isin(cnt[cnt >= 2].index)]) else core   # max 2 per format per day
        s = rng.beta(cc.alpha, cc.beta); r = cc.iloc[int(np.argmax(s))]
        out.append(dict(slot="core", format=r.format, option=r.get("option") if isinstance(r.get("option"), str) else None, window_pt=(win.get("exploit") or ["18-21"])[i % len(win.get("exploit") or ["18-21"])], p_hit=round(float(r["mean"]), 2)))
    exp = ar[(ar.verdict == "WEAK") | (ar.n == 0)]
    for i in range(n_explore):
        r = exp.sample(1, weights=exp["mean"], random_state=int(rng.integers(1e9))).iloc[0] if len(exp) else core.iloc[0]
        out.append(dict(slot="experiment", format=r.format, option=r.get("option") if isinstance(r.get("option"), str) else None, window_pt=(win.get("explore") or ["12-15"])[i % len(win.get("explore") or ["12-15"])], p_hit=round(float(r["mean"]), 2),
                        note="innovation budget: new format/hook/song allowed (unproven music OK here only)"))
    from zoneinfo import ZoneInfo
    today_pt = datetime.datetime.now(ZoneInfo("America/Los_Angeles")).date()   # explicit PT; box clock may be BST
    return dict(product=pk, date=str(date or (today_pt + datetime.timedelta(days=1))), tz="America/Los_Angeles", plan=out)

def _diversify(p, prof, used):
    """Pick the first unused alternative on each originality axis (song+offset, caption, hook text, setting)."""
    more, _ = music.select(prof, p["brief"]["format"], p["fit"].get("video_energy", 2), p["brief"]["slot"], n=8)
    alts = [p["music"]["pick"]] + list(p["music"].get("alternatives") or []) + list(more or [])
    alts = [a for a in alts if a] or [p["music"]["pick"]]
    pick = next((a for a in alts if a and a.get("song") not in used["song"]), None)
    if pick is None:   # all proven songs used: same song, new offset (+4 s per reuse)
        pick = dict(alts[0], offset_s=round((alts[0].get("offset_s") or 0) + 4.0 * used["song"].count(alts[0].get("song")), 1), why=(alts[0].get("why") or "") + "; offset shifted for originality")
    p["music"]["pick"] = pick; used["song"].append(pick.get("song"))
    caps = [p["caption"]["text"]] + [c["caption"] for c in (prof.get("proven_captions") or [])]
    cap = next((c for c in caps if c not in used["caption"]), caps[0]); p["caption"] = dict(p["caption"], text=cap); used["caption"].append(cap)
    from .psych import callout_primary
    hv = [p["hook"]["text"]] + sorted([h["text"] for h in p.get("hook_variants", [])], key=callout_primary)
    h = next((x for x in hv if x not in used["hook"]), hv[0])
    if h != p["hook"]["text"]:
        for c in p["text_cards"]:
            if c["text"] == p["hook"]["text"]: c["text"] = h
        p["hook"] = dict(p["hook"], text=h, why=p["hook"].get("why", "") + "; rotated for originality")
    used["hook"].append(h)
    used.setdefault("page", [])
    if p["brief"]["format"] in used["fmt"] or p.get("page") in used["page"]:
        sets = [x for x in prof["settings"] if x not in used["setting"]]
        if sets: p["setting"] = sets[0]
        p["shots"] = p["shots"][:2] + list(reversed(p["shots"][2:4])) + p["shots"][4:] if len(p["shots"]) > 4 else p["shots"]
        p["duration"] = round(p["duration"] + 0.3 * (1 + used["page"].count(p.get("page"))), 2); p["variant_of_format"] = True
    used["setting"].append(p["setting"]); used["fmt"].append(p["brief"]["format"]); used["page"].append(p.get("page"))

def build_day(pk, date=None, seed=1, out_root=None):
    """Tomorrow's package for one product: schedule -> one plan per slot -> QA + D42 pre-flight lint + credits -> page assignment
    (round-robin over active pages) -> pairwise originality check (D41). Writes out/daily/<date>/<product>/. Never generates."""
    from . import planner, qa, runner, pages as PG, variants as V
    sc = schedule(pk, date=date, seed=seed); pgs = PG.pages_for(pk) or [dict(code="PAGE_1")]
    d = os.path.join(out_root or os.path.join(REPO, "out", "daily"), sc["date"], pk); os.makedirs(d, exist_ok=True)
    items = []; prof = profiles.load(pk); used = dict(song=[], caption=[], hook=[], setting=[], fmt=[])
    for i, s in enumerate(sc["plan"]):
        p = planner.plan(f"{s['format']} video for {pk}", override=dict(product_key=pk, format=s["format"], hook_option=s.get("option"), slot=s["slot"]), mode="original")
        if p["status"] == "REJECTED": items.append(dict(slot=s, status="REJECTED")); continue
        p["page"] = pgs[i % len(pgs)]["code"]
        pw_ = json.load(open(os.path.join(REPO, "learning", "posting_windows.json"))).get(p["page"], {})
        k_ = sum(1 for x in items if x.get("page") == p["page"] and x["slot"]["slot"] == s["slot"])
        wl = (pw_.get("exploit") if s["slot"] == "core" else pw_.get("explore")) or [s["window_pt"]]
        s = dict(s, window_pt=wl[k_ % len(wl)])   # per-page window rotation (no two posts in one window on one page)
        _diversify(p, prof, used)          # D41: rotate song / caption / hook / setting across the day; repeats of a format become variants
        lint = runner.submit(p)
        items.append(dict(slot=s, page=p["page"], format=s["format"], option=s.get("option"), hook=p["hook"]["text"], song=(p["music"]["pick"] or {}).get("song"),
                          credits=p["credits"]["total"], qa=[x for x in qa.plan_checks(p) if x.startswith(("BLOCK", "FIX"))], lint_ok=lint["preflight"]["ok"], plan=p))
    ok_items = [x for x in items if x.get("plan")]
    sims = []
    for a in range(len(ok_items)):
        for b in range(a + 1, len(ok_items)):
            if ok_items[a]["page"] == ok_items[b]["page"] or ok_items[a]["format"] == ok_items[b]["format"]:
                s_, parts = V.similarity(ok_items[a]["plan"], ok_items[b]["plan"]); sims.append(dict(a=a, b=b, sim=s_, ok=s_ <= V.MAX_SIM, parts=parts))
    summary = dict(product=pk, date=sc["date"], tz="America/Los_Angeles", n=len(items), credits_total=round(sum(x.get("credits") or 0 for x in items), 1),
                   slots=[{k: v for k, v in x.items() if k != "plan"} for x in items], originality=sims)
    json.dump(summary, open(os.path.join(d, "day.json"), "w"), indent=1, default=str, ensure_ascii=False)
    md = [f"# {pk} - {sc['date']} (PT) - {len(items)} videos, est. {summary['credits_total']} credits (NOT generated)", "",
          "| # | slot | page | window PT | format | option | hook | song | credits | QA | lint |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, x in enumerate(items):
        s = x["slot"]; md.append(f"| {i+1} | {s['slot']} | {x.get('page','')} | {s['window_pt']} | {s['format']} | {x.get('option') or ''} | {x.get('hook','REJECTED')} | {x.get('song','')} | {x.get('credits','')} | {'; '.join(x.get('qa') or []) or 'ok'} | {'ok' if x.get('lint_ok') else 'FIX'} |")
    md += ["", "Originality (same page or same format): " + (", ".join(f"{o['a']+1}-{o['b']+1} sim {o['sim']} {'ok' if o['ok'] else 'TOO SIMILAR'}" for o in sims) or "n/a")]
    open(os.path.join(d, "DAY.md"), "w").write("\n".join(md) + "\n")
    return summary

def evaluate_experiments():
    """Fill posted results from the corpus (reel_key -> views) and decide arms with both sides posted (>=1.5x = winner)."""
    p = os.path.join(REPO, "learning", "experiments.csv")
    if not os.path.exists(p): return []
    ex = pd.read_csv(p); c = pd.read_csv(os.path.join(REPO, "private", "corpus", "corpus.csv"), low_memory=False).set_index("key")
    for i, r in ex.iterrows():
        if isinstance(r.reel_key, str) and r.reel_key in c.index and pd.notna(c.at[r.reel_key, "views"]):
            ex.at[i, "views_7d"] = c.at[r.reel_key, "views"]; ex.at[i, "status"] = "posted"
    out = []
    for eid, g in ex[ex.is_example == 0].groupby("experiment_id"):
        if (g.status == "posted").all() and len(g) >= 2:
            ctl = g[g.arm == "control"].views_7d.max(); var = g[g.arm != "control"].views_7d.max()
            dec = "variant wins" if var >= 1.5 * ctl else "control wins" if ctl >= 1.5 * var else "inconclusive (<1.5x)"
            ex.loc[g.index, "decision"] = dec; out.append(dict(experiment=eid, decision=dec))
        else: out.append(dict(experiment=eid, decision="waiting for posts", posted=int((g.status == "posted").sum()), arms=len(g)))
    ex.to_csv(p, index=False); return out

def experiments_status():
    p = os.path.join(REPO, "learning", "experiments.csv")
    return pd.read_csv(p).to_dict("records") if os.path.exists(p) else []

def update(model=False, dashboard=True):
    steps = [_run("backtest.corpus"), _run("hookforge.reels_db"), _run("backtest.capcut_drafts"), _run("analysis.posting_time"), _run("hookforge.gen_failures")]
    from . import reels_db as _rdb
    steps.append(dict(step="data source", ok=True, source=_rdb.load_reels()[1], db_review_passed=_rdb.db_is_default()))
    try:   # D86: results feed (CSV inbox + Graph API if META_TOKEN) -> outcomes.csv, velocity, backtest_eval
        from . import results_feed as _rf; steps.append(_rf.run())
    except Exception as e: steps.append(dict(step="results_feed", ok=False, error=str(e)[:300]))
    try:   # D88: refresh last-season prior tier
        from . import ly_season as _ly; steps.append(dict(step="ly_season", ok=True, rows=len(_ly.build())))
    except Exception as e: steps.append(dict(step="ly_season", ok=False, error=str(e)[:300]))
    music.build(); profiles.build(); arms()
    steps += [dict(step="music+profiles+arms", ok=True), dict(step="experiments", ok=True, result=evaluate_experiments())]
    if model: steps.append(_run("backtest.model", timeout=1800))
    if dashboard and os.path.exists(os.path.join(REPO, "analytics", "build_dashboard.py")):
        steps.append(_run(os.path.join(REPO, "analytics", "build_dashboard.py"), cwd=os.path.join(REPO, "analytics")))
    from zoneinfo import ZoneInfo
    log = dict(ts_pt=datetime.datetime.now(ZoneInfo("America/Los_Angeles")).isoformat(timespec="seconds"), steps=steps)
    with open(os.path.join(REPO, "learning", "update_log.jsonl"), "a") as fh: fh.write(json.dumps(log) + "\n")
    return log

if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "schedule": arms(); print(json.dumps(schedule(a[1], seed=1), indent=1))
    elif a and a[0] == "day": arms(); print(json.dumps(build_day(a[1]), indent=1, default=str, ensure_ascii=False)[:3000])
    else: print(json.dumps(update(model="--model" in a, dashboard="--no-dashboard" not in a), indent=1))
