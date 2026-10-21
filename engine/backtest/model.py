"""Hookforge virality model + validation (Phase B).

Target: log10(views) of OWN reels (FB + IG; insights-only rows without hook text excluded). Hit = views >= 50K.
Features (no leakage: every target encoding is recomputed inside each training fold):
  page prior      LOO-in-fold median log views of the same page (page burst / audience size)
  page_day        days since the page's first post (log1p) ; product_day likewise
  format prior    shrunk mean log views of the same format in the fold (k=3) + external evidence:
                  sum of recency weights of external 1M+ organic reels in the format (D28/D34 weighting)
  night           posted 18:00-04:00 PT (hypothesis, EXP-2026-10-19-01)
  psych flags     14 coded factors (taxonomy.code_psych)
  first frame     product visible at 0 s, product % at 0 s (coded), people count, multi-card text
  CapCut edit     duration, first cut, shot count, text y (from the team's drafts; NaN -> fold median + missing flag)
  platform IG
EXCLUDED on purpose: served resolution / codec (outcome of watch time, D7), link captions (D6), sales (outcome).
Validation: leave-one-out (LOO) and a temporal holdout (train < 2026-10-01, test >= 2026-10-01).
Metrics: Spearman(pred, views), AUC(hit), within-page AUC, top-quartile precision. Baselines: B0 page prior only,
B1 page + format prior, B2 full ridge. Output: engine/backtest/data/validation.json + private/backtest/loo_predictions.csv
"""
import os, sys, json, math
import numpy as np, pandas as pd
from scipy.stats import spearmanr
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from hookforge.config import REPO, HIT_ABS_VIEWS, recency_weight
from hookforge.taxonomy import PSYCH

ASOF = pd.Timestamp("2026-10-18")

def auc(y, s):
    y = np.asarray(y).astype(bool); s = np.asarray(s, float)
    pos, neg = s[y], s[~y]
    if len(pos) == 0 or len(neg) == 0: return np.nan
    gt = (pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum()
    return gt / (len(pos) * len(neg))

def load():
    c = __import__("hookforge.reels_db", fromlist=["x"]).load_reels()[0]
    own = c[(c.source == "own") & c.views.notna() & c.hook_text.notna()].copy()
    own["y"] = np.log10(own.views.astype(float)); own["hit"] = own.views >= HIT_ABS_VIEWS
    own["posted"] = pd.to_datetime(own.posted_pt.astype(str).str.slice(0, 16), errors="coerce")
    ed = pd.read_csv(f"{REPO}/private/edits/edits.csv")
    ed = ed[ed.reel_key.notna()].set_index("reel_key")
    for col, src in [("cc_duration", "duration"), ("cc_first_cut", "first_cut"), ("cc_shots", "n_shots"), ("cc_text_y", "text_y")]:
        own[col] = own.key.map(ed[src])
    ext = c[c.source.isin(["external", "viral_research", "reference_library"]) & (c.views >= 1e6)].copy()
    if "organic" in ext: ext = ext[ext.organic.fillna(1) == 1]
    ext["age"] = (ASOF - pd.to_datetime(ext.posted_pt.astype(str).str.slice(0, 10), errors="coerce")).dt.days
    ir = ext["inclusion_rule"] if "inclusion_rule" in ext else pd.Series(None, index=ext.index)
    ext["w"] = [recency_weight(a if pd.notna(a) else None, "external", inclusion_rule=r if isinstance(r, str) else None) for a, r in zip(ext.age, ir)]
    ext_w = ext.groupby("format").w.sum()
    return own.reset_index(drop=True), ext_w

BASE = ["night", "page_day_l", "product_day_l", "ig", "prod_vis0", "prod_pct0", "people_n", "multi_card"] + list(PSYCH)
CC = ["cc_duration", "cc_first_cut", "cc_shots", "cc_text_y"]

def featurize(tr, te, ext_w):
    g = tr.y.mean()
    def page_prior(df, ref):
        out = []
        for i, r in df.iterrows():
            m = ref[(ref.page_code == r.page_code) & (ref.key != r.key)].y
            out.append(m.median() if len(m) else g)
        return np.array(out)
    def fmt_prior(df, ref, k=3):
        out = []
        for i, r in df.iterrows():
            m = ref[(ref.format == r.format) & (ref.key != r.key)].y
            out.append((m.sum() + k * g) / (len(m) + k))
        return np.array(out)
    X = {}
    for name, df in (("tr", tr), ("te", te)):
        F = pd.DataFrame(index=df.index)
        F["page_prior"] = page_prior(df, tr); F["fmt_prior"] = fmt_prior(df, tr)
        F["fmt_ext"] = np.log1p(df.format.map(ext_w).fillna(0).values)
        F["night"] = df.post_hour.map(lambda h: np.nan if pd.isna(h) else float(h >= 18 or h < 4))
        F["page_day_l"] = np.log1p(df.page_day.astype(float)); F["product_day_l"] = np.log1p(df.product_day.astype(float))
        F["ig"] = (df.platform == "IG").astype(float)
        F["prod_vis0"] = df.product_visible_0_coded.astype(float); F["prod_pct0"] = df.product_pct_0_coded.astype(float)
        F["people_n"] = df.people_n.astype(float); F["multi_card"] = df.multi_card.astype(float)
        for p in PSYCH: F[p] = df[p].astype(float)
        for cc in CC:
            F[cc] = df[cc].astype(float); F[cc + "_na"] = df[cc].isna().astype(float)
        X[name] = F
    med = X["tr"].median(numeric_only=True)
    for k in X: X[k] = X[k].fillna(med).fillna(0)
    return X["tr"], X["te"]

def ridge_fit_predict(Xtr, ytr, Xte, alpha=8.0):
    mu, sd = Xtr.mean(), Xtr.std().replace(0, 1)
    A = ((Xtr - mu) / sd).values; B = ((Xte - mu) / sd).values
    ym = ytr.mean()
    w = np.linalg.solve(A.T @ A + alpha * np.eye(A.shape[1]), A.T @ (ytr - ym))
    return B @ w + ym, pd.Series(w, index=Xtr.columns)

MODELS = {
    "B0_page_prior": ["page_prior"],
    "B1_page+format": ["page_prior", "fmt_prior", "fmt_ext"],
    "B2_full": None,   # all features
    "B3_full_no_capcut": "nocc",
}

def cols_for(m, X):
    spec = MODELS[m]
    if spec is None: return list(X.columns)
    if spec == "nocc": return [c for c in X.columns if not c.startswith("cc_")]
    return spec

def predict_split(tr, te, ext_w, m):
    Xtr, Xte = featurize(tr, te, ext_w); cols = cols_for(m, Xtr)
    if m == "B0_page_prior": return Xte["page_prior"].values, None
    p, w = ridge_fit_predict(Xtr[cols], tr.y.values, Xte[cols]); return p, w

def metrics(df, pred):
    d = df.assign(pred=pred)
    wp = [auc(g.hit, g.pred) for _, g in d.groupby("page_code") if g.hit.nunique() == 2]
    wsp = [spearmanr(g.y, g.pred).correlation for _, g in d.groupby("page_code") if len(g) >= 5]
    q = d.pred >= d.pred.quantile(0.75)
    return dict(n=int(len(d)), hits=int(d.hit.sum()), spearman=round(float(spearmanr(d.y, d.pred).correlation), 3),
                auc_hit=round(float(auc(d.hit, d.pred)), 3), within_page_auc_mean=round(float(np.nanmean(wp)), 3) if wp else None,
                within_page_spearman_mean=round(float(np.nanmean(wsp)), 3) if wsp else None,
                top_quartile_hit_rate=round(float(d[q].hit.mean()), 3), base_hit_rate=round(float(d.hit.mean()), 3),
                mae_log10=round(float((d.y - d.pred).abs().mean()), 3))

def validate():
    own, ext_w = load()
    out = {"asof": str(ASOF.date()), "n_own": int(len(own)), "hits": int(own.hit.sum()), "loo": {}, "holdout": {}}
    loo_preds = {}
    for m in MODELS:
        preds = np.zeros(len(own))
        for i in range(len(own)):
            tr = own.drop(index=i); te = own.loc[[i]]
            preds[i] = predict_split(tr, te, ext_w, m)[0][0]
        loo_preds[m] = preds; out["loo"][m] = metrics(own, preds)
    cut = pd.Timestamp("2026-10-01")
    tr, te = own[own.posted < cut], own[own.posted >= cut]
    for m in MODELS:
        p = predict_split(tr, te, ext_w, m)[0]
        out["holdout"][m] = metrics(te, p)
    out["holdout"]["split"] = f"train posted < {cut.date()} (n={len(tr)}, hits={int(tr.hit.sum())}); test >= (n={len(te)}, hits={int(te.hit.sum())})"
    _, w = predict_split(own, own.head(1), ext_w, "B2_full")
    out["full_model_coefficients_std"] = w.round(3).sort_values(key=abs, ascending=False).head(15).to_dict()
    os.makedirs(f"{REPO}/private/backtest", exist_ok=True)
    own.assign(**{f"pred_{k}": v for k, v in loo_preds.items()})[["key", "page_code", "format", "views", "hit"] + [f"pred_{k}" for k in loo_preds]].to_csv(
        f"{REPO}/private/backtest/loo_predictions.csv", index=False)
    json.dump(out, open(f"{REPO}/engine/backtest/data/validation.json", "w"), indent=1)
    print(json.dumps(out, indent=1))
    return out

if __name__ == "__main__":
    validate()
