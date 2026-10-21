"""Per-video backtest (gate before anything is shown/posted).

Input: a feature dict for a planned/draft video (from the edit plan + measure.py on the rendered draft).
Output: report dict + markdown:
  - nearest neighbours: 5 most similar OWN winners, 5 most similar OWN flops, 3 most similar EXTERNAL 1M+ reels
    (distance on format, category, psych flags, timing; external weighted by recency/inclusion_rule, D28/D34)
  - deviations that matter: checks vs winner ranges (CapCut drafts + body/hooks reports) and hard rules
  - predicted view band: ridge model B3 (validated: see data/validation.json) + empirical LOO residual quantiles
  - verdict: PASS / FIX / BLOCK and a fix-list
Gate policy (D35): the model is weak (LOO AUC ~0.65, temporal holdout loses to page prior), so it is a SOFT score.
BLOCK only on hard-rule violations or format-proof failure; FIX on deviations; the view band is informational.
"""
import os, sys, json, math
import numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from hookforge.config import REPO, HIT_ABS_VIEWS, EDIT, TEXT, HOOK_MAX_S, recency_weight
from hookforge.taxonomy import PSYCH
from backtest import model as M

WIN_RANGES = {   # from CapCut primary drafts of 50K+ reels (n=11-13) + body REPORT winners; see capcut_stats.json
    "duration": (11.5, 14.5), "first_cut": (2.0, 3.5), "shot_len_med": (0.9, 1.9), "n_shots": (6, 10),
    "text_y_frac": TEXT["center_y_ok"], "hook_s": (0, HOOK_MAX_S),
}

def _vec(r):
    v = [1.0 if r.get("category") == c else 0.0 for c in ["wearable_gift", "decor_light", "decor_fire", "decor_mug", "accessory", "pet", "gadget"]]
    v += [2.0 * float(bool(r.get(p))) for p in PSYCH]
    return np.array(v)

def neighbours(feat, k=5):
    c = __import__("hookforge.reels_db", fromlist=["x"]).load_reels()[0]
    c = c[c.views.notna() & (c.get("insights_only", 0).fillna(0) != 1)].copy()
    c["fmt_match"] = (c.format == feat.get("format")).astype(float)
    fv = _vec(feat)
    c["dist"] = [np.linalg.norm(_vec(r) - fv) + 3.0 * (1 - m) for r, m in zip(c.to_dict("records"), c.fmt_match)]
    own = c[c.source == "own"]; ext = c[c.source != "own"].copy()
    ext["age"] = (pd.Timestamp("2026-10-18") - pd.to_datetime(ext.posted_pt.astype(str).str.slice(0, 10), errors="coerce")).dt.days
    ext["w"] = [recency_weight(a if pd.notna(a) else None, "external", inclusion_rule=r if isinstance(r, str) else None)
                for a, r in zip(ext.age, ext.get("inclusion_rule", pd.Series([None] * len(ext), index=ext.index)))]
    ext["wdist"] = ext.dist / ext.w.clip(lower=0.05) ** 0.5
    cols = ["key", "format", "category", "views", "hook_text"]
    return dict(own_winners=own[own.views >= HIT_ABS_VIEWS].nsmallest(k, "dist")[cols + ["dist"]].round(2).to_dict("records"),
                own_flops=own[own.views < 10000].nsmallest(k, "dist")[cols + ["dist"]].round(2).to_dict("records"),
                external=ext[ext.views >= 1e6].nsmallest(3, "wdist")[cols + ["w"]].round(2).to_dict("records"))

def deviations(feat):
    out = []
    def chk(name, val, rng, sev="FIX", why=""):
        if val is None or (isinstance(val, float) and math.isnan(val)): return
        if not (rng[0] <= val <= rng[1]): out.append(dict(check=name, value=round(val, 2), target=rng, severity=sev, why=why))
    chk("duration_s", feat.get("duration"), WIN_RANGES["duration"], why="winners 11.9-13.4 s (CapCut primaries), body REPORT 12.7-13.8")
    chk("first_cut_s", feat.get("first_cut"), WIN_RANGES["first_cut"], why="winners median 2.37 s (IQR 2.17-3.17)")
    chk("shot_len_median_s", feat.get("shot_len_med"), WIN_RANGES["shot_len_med"], why="post-hook shot IQR 0.9-1.9 s")
    chk("text_centre_y_frac", feat.get("text_y_frac"), WIN_RANGES["text_y_frac"], why="CapCut y 0.62 -> 19% from top (D30)")
    chk("hook_gen_s", feat.get("hook_s"), WIN_RANGES["hook_s"], sev="BLOCK", why="hooks <=5 s (D25)")
    if feat.get("format") not in ("F04",) and feat.get("product_visible_0") is False:
        out.append(dict(check="product_at_0s", value=False, target=True, severity="FIX", why="2.7M vs 16K pair; transplants fail when product not legible at 0 s"))
    if feat.get("format") == "F05" and feat.get("category", "").startswith("decor") and not feat.get("is_experiment"):
        out.append(dict(check="decor_dont_show", value="core slot", target="experiment slot only", severity="BLOCK", why="D19"))
    for p in feat.get("prompts", []):
        if not p.rstrip().endswith(feat.get("_suffix", "")):
            out.append(dict(check="iphone12_suffix", value="missing", target="every prompt", severity="BLOCK", why="D32")); break
    return out

def predict_band(feat):
    own, ext_w = M.load()
    row = pd.DataFrame([{**{c: np.nan for c in own.columns}, **feat, "key": "_NEW_", "y": np.nan, "hit": False}])
    Xtr, Xte = M.featurize(own, row, ext_w); cols = M.cols_for("B3_full_no_capcut", Xtr)
    p, _ = M.ridge_fit_predict(Xtr[cols], own.y.values, Xte[cols])
    lp = pd.read_csv(f"{REPO}/private/backtest/loo_predictions.csv")
    res = np.log10(lp.views) - lp["pred_B3_full_no_capcut"]
    q = np.quantile(res, [0.1, 0.5, 0.9])
    return dict(point=int(10 ** p[0]), p10=int(10 ** (p[0] + q[0])), p50=int(10 ** (p[0] + q[1])), p90=int(10 ** (p[0] + q[2])),
                note="80% band from LOO residuals; model LOO AUC 0.65 / Spearman 0.23 - informational, not a gate")

def run(feat):
    dev = deviations(feat)
    rep = dict(features={k: v for k, v in feat.items() if k not in ("prompts", "_suffix")}, neighbours=neighbours(feat), deviations=dev)
    try: rep["band"] = predict_band(feat)
    except Exception as e: rep["band"] = dict(error=str(e))
    rep["verdict"] = "BLOCK" if any(d["severity"] == "BLOCK" for d in dev) else ("FIX" if dev else "PASS")
    rep["fix_list"] = [f"{d['check']}: {d['value']} -> {d['target']} ({d['why']})" for d in dev]
    return rep

def validate_knn():
    """LOO: share of winners among the 5 nearest own neighbours (excluding self + same page-day dupes) as a score."""
    c = __import__("hookforge.reels_db", fromlist=["x"]).load_reels()[0]
    own = c[(c.source == "own") & c.views.notna() & c.hook_text.notna()].reset_index(drop=True)
    V = np.stack([_vec(r) for r in own.to_dict("records")]); hit = (own.views >= HIT_ABS_VIEWS).values
    sc = []
    for i in range(len(own)):
        d = np.linalg.norm(V - V[i], axis=1) + 3.0 * (own.format.values != own.format.values[i])
        d[i] = np.inf
        nn = np.argsort(d)[:5]; sc.append(hit[nn].mean())
    sc = np.array(sc)
    wp = [M.auc(hit[g.index], sc[g.index]) for _, g in own.groupby("page_code") if len(set(hit[g.index])) == 2]
    return dict(n=int(len(own)), auc=round(float(M.auc(hit, sc)), 3), within_page_auc=round(float(np.nanmean(wp)), 3))

if __name__ == "__main__":
    print("kNN LOO:", validate_knn())
