"""Small, dependency-light statistics used by every dashboard panel (numpy/scipy only)."""
import numpy as np
from scipy import stats as st

RNG = np.random.default_rng(7)  # fixed seed -> regenerable dashboard

def wilson(k, n, z=1.96):
    """95% Wilson interval for a hit rate. Returns (p, lo, hi); NaNs when n == 0."""
    if n == 0: return (np.nan, np.nan, np.nan)
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0.0, c - h), min(1.0, c + h)

def boot_median(v, b=4000, q=(5, 95)):
    """Median with a bootstrap 90% CI, computed on log10(views) and returned in views."""
    v = np.asarray([x for x in v if np.isfinite(x) and x > 0], float)
    if len(v) == 0: return (np.nan, np.nan, np.nan)
    lv = np.log10(v)
    if len(v) == 1: return (v[0], np.nan, np.nan)
    meds = np.median(RNG.choice(lv, (b, len(lv)), replace=True), axis=1)
    return 10 ** np.median(lv), 10 ** np.percentile(meds, q[0]), 10 ** np.percentile(meds, q[1])

def spearman_perm(x, y, n_perm=5000, groups=None):
    """Spearman rho + two-sided permutation p. With groups, permutes within group (within-page test)."""
    x = np.asarray(x, float); y = np.asarray(y, float); m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]; g = None if groups is None else np.asarray(groups)[m]
    n = len(x)
    if n < 4 or np.nanstd(x) == 0 or np.nanstd(y) == 0: return np.nan, np.nan, n
    if g is not None:  # within-group ranks, then pooled correlation of centred ranks
        rx = np.zeros(n); ry = np.zeros(n)
        for k in np.unique(g):
            i = g == k
            if i.sum() < 2: continue
            rx[i] = st.rankdata(x[i]) - st.rankdata(x[i]).mean(); ry[i] = st.rankdata(y[i]) - st.rankdata(y[i]).mean()
        if rx.std() == 0 or ry.std() == 0: return np.nan, np.nan, n
        rho = np.corrcoef(rx, ry)[0, 1]; cnt = 0
        for _ in range(n_perm):
            rp = ry.copy()
            for k in np.unique(g):
                i = np.where(g == k)[0]; rp[i] = ry[RNG.permutation(i)]
            cnt += abs(np.corrcoef(rx, rp)[0, 1]) >= abs(rho) - 1e-12
        return rho, (cnt + 1) / (n_perm + 1), n
    rho = st.spearmanr(x, y).statistic
    ry = st.rankdata(y); rx = st.rankdata(x)
    perms = np.array([np.corrcoef(rx, RNG.permutation(ry))[0, 1] for _ in range(n_perm)])
    return rho, (np.sum(np.abs(perms) >= abs(rho) - 1e-12) + 1) / (n_perm + 1), n

def fisher(k1, n1, k2, n2):
    if min(n1, n2) == 0: return np.nan
    return st.fisher_exact([[k1, n1 - k1], [k2, n2 - k2]]).pvalue

def fmt_views(v):
    if v is None or not np.isfinite(v): return "–"
    return f"{v/1e6:.2f}M" if v >= 1e6 else f"{v/1e3:.1f}K" if v >= 1e3 else f"{v:.0f}"

def fmt_p(p):
    return "–" if p is None or not np.isfinite(p) else ("<0.001" if p < 0.001 else f"{p:.3f}")
