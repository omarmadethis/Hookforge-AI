"""Posting-time virality analysis (first-class factor; Omar 2026-10-18).

Factors (PT): hour of day, day of week, hours since the page's previous post, posts that day on the page,
page age at posting (days since the page's first post), holiday/seasonal proximity (days to Halloween,
Thanksgiving, Black Friday, Christmas). Outcomes: views (log10), hit (>=50K), 3-s rate, shares, orders/1K.
Scope: per page and per product, pooled with page fixed effects; format/hook controlled by stratified
permutation (shuffle the factor within page x format strata when each stratum has >=2 reels; else within page).
External reels: post date (+ TikTok upload time decoded from the video id: id >> 32 = unix seconds) from the
research library (index/archive/near_misses) + team external CSV, recency/inclusion weighted (D28/D34). They're
reported separately (platform audiences differ; TikTok hour != FB hour).

Outputs (recomputed after every new post via learning loop `learning/update.py` -> run()):
  engine/backtest/data/posting_time.json      factor tables + tests (public: no ids)
  learning/rules_learned.csv                  rows with rule_type=posting_time, status hypothesis|promoted|demoted
  learning/posting_windows.json               current best window per page + explore slots for the scheduler
Promotion threshold: Holm-corrected within-page permutation p<0.05 across all factors tested in the run,
format-controlled p<0.10, n>=30, same direction on >=2 pages. Raw p<0.05 without Holm = "supported" (still a
hypothesis, used for scheduling exploit slots but not as a hard rule).
"""
import os, sys, json, math, datetime as dt
import numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from hookforge.config import REPO, HIT_ABS_VIEWS, recency_weight

W = "/workspace"
HOLIDAYS = {"halloween": "2026-10-31", "thanksgiving": "2026-11-26", "black_friday": "2026-11-27", "christmas": "2026-12-25"}
EVIDENCE = {"p": 0.05, "n": 30, "pages": 2, "perms": 2000}
SLOTS = [(18, 21), (21, 24), (0, 4), (4, 8), (8, 12), (12, 15), (15, 18)]   # PT hour bins (start, end)
EXPLORE_SHARE = 0.2

def slot_of(h):
    if pd.isna(h): return None
    h = int(h)
    for a, b in SLOTS:
        if a <= h < b: return f"{a:02d}-{b:02d}"
    return None

def load_own():
    c = __import__("hookforge.reels_db", fromlist=["x"]).load_reels()[0]
    o = c[(c.source == "own") & c.views.notna()].copy()
    o["ts"] = pd.to_datetime(o.posted_pt.astype(str).str.slice(0, 16), errors="coerce")
    o = o[o.ts.notna()].copy()
    o["has_time"] = o.posted_pt.astype(str).str.len() >= 16
    o["hour"] = np.where(o.has_time, o.ts.dt.hour, np.nan)
    o["slot"] = o.hour.map(slot_of)
    o["night"] = o.hour.map(lambda h: np.nan if pd.isna(h) else float(h >= 18 or h < 4))
    o["dow"] = o.ts.dt.day_name().str[:3]
    o = o.sort_values("ts")
    o["gap_h"] = o.groupby("page_code").ts.diff().dt.total_seconds() / 3600
    o["date"] = o.ts.dt.date
    o["posts_that_day"] = o.groupby(["page_code", "date"]).key.transform("count")
    o["page_age_d"] = (o.ts - o.groupby("page_code").ts.transform("min")).dt.days
    for k, d in HOLIDAYS.items(): o[f"days_to_{k}"] = (pd.Timestamp(d) - o.ts).dt.days
    o["y"] = np.log10(o.views.astype(float)); o["hit"] = (o.views >= HIT_ABS_VIEWS).astype(float)
    o["shares_per_1k"] = o.shares / o.views * 1000 if "shares" in o else np.nan
    return o

def load_external():
    rows = []
    for tier in ("index", "archive", "near_misses"):
        p = f"{W}/research/reference_library/{tier}.csv"
        if not os.path.exists(p): continue
        r = pd.read_csv(p)
        for x in r.itertuples():
            ts = None
            if str(x.platform).lower() == "tiktok":
                try: ts = pd.Timestamp(int(str(x.id).split("_")[-1]) >> 32, unit="s", tz="UTC").tz_convert("America/Los_Angeles")
                except Exception: ts = None
            age = (pd.Timestamp("2026-10-18") - pd.to_datetime(x.post_date, errors="coerce")).days if pd.notna(x.post_date) else None
            rows.append(dict(tier=tier, platform=x.platform, views=x.views, post_date=x.post_date, hour=ts.hour if ts is not None else np.nan,
                             dow=(ts or pd.to_datetime(x.post_date, errors="coerce")).day_name()[:3] if (ts is not None or pd.notna(x.post_date)) else None,
                             w=recency_weight(age, "external", inclusion_rule=getattr(x, "inclusion_rule", None))))
    return pd.DataFrame(rows)

def perm_test(df, col, outcome="y", strata=("page_code",), perms=None, seed=7):
    """Difference in mean outcome (level==1 vs 0) with the factor shuffled within strata."""
    perms = perms or EVIDENCE["perms"]
    d = df[[col, outcome] + list(strata)].dropna()
    if d[col].nunique() < 2 or len(d) < 8: return None
    obs = d[d[col] == 1][outcome].mean() - d[d[col] == 0][outcome].mean()
    rng = np.random.default_rng(seed); cnt = 0
    groups = [g.index.values for _, g in d.groupby(list(strata))]
    vals = d[col].values.copy(); idx_pos = {ix: i for i, ix in enumerate(d.index)}
    for _ in range(perms):
        v = vals.copy()
        for g in groups:
            pos = [idx_pos[i] for i in g]; v[pos] = rng.permutation(v[pos])
        diff = d[outcome].values[v == 1].mean() - d[outcome].values[v == 0].mean()
        cnt += abs(diff) >= abs(obs) - 1e-12
    return dict(n=int(len(d)), n1=int((d[col] == 1).sum()), diff=round(float(obs), 3), p=round((cnt + 1) / (perms + 1), 4))

def table(df, col):
    g = df.groupby(col)
    t = pd.DataFrame(dict(n=g.size(), median_views=g.views.median(), hit_rate=g.hit.mean(),
                          three_sec=g.three_sec_rate.median() if "three_sec_rate" in df else np.nan,
                          shares_per_1k=g.shares_per_1k.median(), orders_per_1k=g.orders_per_1k.median() if "orders_per_1k" in df else np.nan))
    return t.reset_index().round(3).to_dict(orient="records")

def best_windows(o):
    """Per page: rank slots by shrunk hit rate (beta prior from the page's overall rate, k=4) -> exploit + explore slots."""
    out = {}
    for pg, g in o[o.slot.notna()].groupby("page_code"):
        base = g.hit.mean(); k = 4; ranks = []
        for s in [f"{a:02d}-{b:02d}" for a, b in SLOTS]:
            x = g[g.slot == s]; ranks.append((s, (x.hit.sum() + k * base) / (len(x) + k), int(len(x))))
        ranks.sort(key=lambda r: -r[1])
        out[pg] = dict(exploit=[r[0] for r in ranks[:2]], explore=[r[0] for r in ranks[2:] if r[2] < 3] or [r[0] for r in ranks[-2:]],
                       scores={r[0]: dict(score=round(r[1], 3), n=r[2]) for r in ranks}, explore_share=EXPLORE_SHARE)
    pooled_night = o.night.mean()
    out["_default"] = dict(exploit=["18-21", "21-24", "00-04"], explore=["08-12", "12-15"], explore_share=EXPLORE_SHARE,
                           note="default for new pages: 18:00-04:00 PT (hypothesis EXP-2026-10-19-01) + 20% explore in day slots")
    return out

def run(write=True):
    o = load_own()
    o["gap_lt12"] = o.gap_h.map(lambda x: np.nan if pd.isna(x) else float(x < 12))
    o["multi_post_day"] = (o.posts_that_day >= 2).astype(float)
    o["young_page"] = o.page_age_d.map(lambda x: float(x <= 7))
    o["weekend"] = o.dow.isin(["Sat", "Sun"]).astype(float)
    o["xmas_lt70"] = o.days_to_christmas.map(lambda x: float(x < 70))
    o["strat_fmt_ok"] = o.groupby(["page_code", "format"]).key.transform("count") >= 2
    tests, rules = {}, []
    for f, label in [("night", "posted 18:00-04:00 PT"), ("weekend", "posted Sat/Sun"), ("gap_lt12", "<12 h since page's previous post"),
                     ("multi_post_day", ">=2 posts that day on the page"), ("young_page", "page age <=7 days at posting"),
                     ("xmas_lt70", "<70 days to Christmas")]:
        res = {}
        for outcome in ("y", "hit"):
            res[outcome] = perm_test(o, f, outcome)
        sub = o[o.strat_fmt_ok]
        res["y_ctrl_format"] = perm_test(sub, f, "y", strata=("page_code", "format"))
        per_page = {}
        for pg, g in o.groupby("page_code"):
            if g[f].nunique() == 2 and len(g) >= 6:
                per_page[pg] = round(float(g[g[f] == 1].y.mean() - g[g[f] == 0].y.mean()), 3)
        res["per_page_diff_log10"] = per_page
        tests[f] = res
        r = res["y"]
        if r:
            same_dir = sum(1 for v in per_page.values() if np.sign(v) == np.sign(r["diff"]) and v != 0)
            promoted = r["p"] < EVIDENCE["p"] and r["n"] >= EVIDENCE["n"] and same_dir >= EVIDENCE["pages"]
            rules.append(dict(rule_id=f"PT-{f}", rule_type="posting_time", rule=f"{label}: {'+' if r['diff'] > 0 else '-'}{abs(r['diff']):.2f} log10 views (x{10 ** r['diff']:.2f})",
                              status="promoted" if promoted else "hypothesis", n=r["n"], p_within_page=r["p"],
                              p_within_page_format=(res["y_ctrl_format"] or {}).get("p"), pages_same_direction=same_dir,
                              evidence_source="own reels (full weight, D28)", updated=str(dt.date.today())))
    # Holm correction across factors
    ps = sorted([(r["p_within_page"], i) for i, r in enumerate(rules)])
    m = len(ps)
    for rank, (pv, i) in enumerate(ps):
        rules[i]["p_holm"] = round(min(1.0, max(pv * (m - rank), max([rules[j].get("p_holm", 0) for _, j in ps[:rank]] or [0]))), 4)
    for r in rules:
        pf = r["p_within_page_format"] if r["p_within_page_format"] is not None else 1
        if r["p_holm"] < EVIDENCE["p"] and pf < 0.10 and r["n"] >= EVIDENCE["n"] and r["pages_same_direction"] >= EVIDENCE["pages"]: r["status"] = "promoted"
        elif r["p_within_page"] < EVIDENCE["p"] and r["pages_same_direction"] >= EVIDENCE["pages"]: r["status"] = "supported-hypothesis"
        else: r["status"] = "hypothesis"
    out = dict(n_own=int(len(o)), n_with_hour=int(o.hour.notna().sum()), tests=tests,
               by_slot=table(o[o.slot.notna()], "slot"), by_dow=table(o, "dow"),
               by_page_slot={pg: table(g[g.slot.notna()], "slot") for pg, g in o.groupby("page_code") if g.slot.notna().sum() >= 5},
               by_product_slot={pr: table(g[g.slot.notna()], "slot") for pr, g in o.groupby("product") if g.slot.notna().sum() >= 5},
               threshold=EVIDENCE)
    ex = load_external()
    if len(ex):
        out["external"] = dict(n=int(len(ex)), n_with_hour=int(ex.hour.notna().sum()),
                               by_dow=ex.groupby("dow").apply(lambda g: dict(n=int(len(g)), w=round(float(g.w.sum()), 2))).to_dict(),
                               by_hour_tiktok=ex[ex.hour.notna()].groupby("hour").size().astype(int).to_dict(),
                               note="external = 1M+ reels only (no flops), TikTok/IG audiences; descriptive, not a test")
    win = best_windows(o)
    if write:
        json.dump(out, open(f"{REPO}/engine/backtest/data/posting_time.json", "w"), indent=1, default=str)
        json.dump(win, open(f"{REPO}/learning/posting_windows.json", "w"), indent=1)
        p = f"{REPO}/learning/rules_learned.csv"
        old = pd.read_csv(p) if os.path.exists(p) else pd.DataFrame()
        if len(old) and "rule_type" in old: old = old[old.rule_type != "posting_time"]
        pd.concat([old, pd.DataFrame(rules)], ignore_index=True).to_csv(p, index=False)
    return out, rules, win

if __name__ == "__main__":
    out, rules, win = run()
    for r in rules: print(r["rule_id"], r["status"], r["rule"], "n", r["n"], "p", r["p_within_page"], "p|fmt", r["p_within_page_format"], "pages", r["pages_same_direction"])
    print(json.dumps(out["by_slot"], indent=0)[:1500])
    print({k: v["exploit"] for k, v in win.items()})
