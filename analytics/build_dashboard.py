"""Build the Hookforge analytics dashboard: one self-contained static HTML file.

    python analytics/build_dashboard.py            # -> analytics/dashboard.html (+ PNG screenshots)
    python analytics/build_dashboard.py --public   # -> analytics/dashboard_public.html (no absolute sales,
                                                   #    page codes instead of names) for the shareable repo
    python analytics/build_dashboard.py --no-png   # skip PNG export (needs kaleido + Chrome)

Rules: every number is computed from a file listed in the Provenance panel; nothing is typed in.
Every chart shows n; medians carry bootstrap 90% CIs, hit rates carry Wilson 95% CIs, and groups
with n < 5 are greyed and labelled "low n". Correlational only, see caveats per panel.
"""
import os, sys, json, argparse, html, datetime as dt
import numpy as np, pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import hf_load as L
from hf_stats import wilson, boot_median, spearman_perm, fisher, fmt_views, fmt_p

sys.path.insert(0, os.path.join(L.REPO, "engine"))
try:
    from hookforge.config import HIT_ABS_VIEWS, INNOVATION_SHARE
except Exception:
    HIT_ABS_VIEWS, INNOVATION_SHARE = 50_000, 0.20
LOW_N = 5
PAL = ["#1f77b4", "#d62728", "#2ca02c", "#ff7f0e", "#9467bd", "#8c564b", "#e377c2", "#17becf", "#7f7f7f", "#bcbd22"]
# Cross-checks: figures quoted in the team reports, re-computed here from the raw files at build time.
EXPECTED = [  # (label, store, metric, expected, tolerance, report)
    ("Merry Glow orders", "Merry Glow", "orders", 33, 0, "team/shopify/merryglow_REPORT.md"),
    ("Merry Glow net sales ($)", "Merry Glow", "net", 3225, 1, "team/shopify/merryglow_REPORT.md"),
    ("Merry Glow sessions", "Merry Glow", "sessions", 14039, 0, "team/shopify/merryglow_REPORT.md"),
    ("Brick Hood orders", "Brick Hood", "orders", 22, 0, "team/shopify/brickhood_REPORT.md"),
    ("Brick Hood net sales ($)", "Brick Hood", "net", 912, 1, "team/shopify/brickhood_REPORT.md"),
    ("Brick Hood sessions (raw ShopifyQL daily)", "Brick Hood", "raw:shopify/brickhood/raw/daily_sessions.txt", 958, 0, "team/shopify/brickhood_REPORT.md"),
    ("Brick Hood sessions in PT-hourly file (info)", "Brick Hood", "sessions", 958, None, "hourly sessions export ends Oct 8 16:00 PT"),
    ("Merry Jammies orders (analytics)", "Merry Jammies", "orders", 948, 0, "team/shopify/merryjammies_REPORT.md"),
    ("Merry Jammies net sales ($)", "Merry Jammies", "net", 91672, 1, "team/shopify/merryjammies_REPORT.md"),
    ("Merry Jammies sessions", "Merry Jammies", "sessions", 126309, 0, "team/shopify/summary_numbers.json"),
]
EXPECTED_IG = [("IG Ddii6mOKO2G plays", "Ddii6mOKO2G", "plays", 4626610), ("IG Ddii6mOKO2G shares", "Ddii6mOKO2G", "shares", 15140),
               ("IG DdK34IiqRx4 profile visits", "DdK34IiqRx4", "profile_visits", 2676), ("IG reels with full Insights", None, "n", 6)]

FIGS = {}  # name -> figure (for PNG export)

def layout(fig, title, h=430, **kw):
    fig.update_layout(title=dict(text=title, x=0.01, font=dict(size=15)), height=h, template="plotly_white",
                      margin=dict(l=60, r=20, t=60, b=50), legend=dict(font=dict(size=10)), font=dict(size=11), **kw)
    return fig

def group_stats(df, key, min_n=1):
    rows = []
    for k, g in df.groupby(key):
        v = g["views"].dropna(); n = len(v)
        if n < min_n: continue
        hits = int((v >= HIT_ABS_VIEWS).sum()); p, lo, hi = wilson(hits, n); med, mlo, mhi = boot_median(v)
        rows.append(dict(group=k, n=n, hits=hits, hit_rate=p, hit_lo=lo, hit_hi=hi, median=med, med_lo=mlo, med_hi=mhi,
                         best=v.max(), pages=", ".join(sorted(g["page"].dropna().astype(str).unique())),
                         categories=", ".join(sorted(g["category"].dropna().astype(str).unique()))))
    return pd.DataFrame(rows).sort_values(["hit_lo", "median"], ascending=False) if rows else pd.DataFrame()

def leaderboard_fig(gs, title, label_map=None, ext=None):
    gs = gs.copy(); gs["label"] = [f"{label_map.get(g, g) if label_map else g}  (n={n})" for g, n in zip(gs.group, gs.n)]
    gs = gs.iloc[::-1]; col = ["#bbbbbb" if n < LOW_N else "#1f77b4" for n in gs.n]
    ncol = 3 if ext is not None else 2
    titles = [f"Median views, 90% bootstrap CI", f"Hit rate (≥{fmt_views(HIT_ABS_VIEWS)}), Wilson 95% CI"]
    if ext is not None: titles.append("Ext. proof: n ≥1M")
    fig = make_subplots(rows=1, cols=ncol, shared_yaxes=True, horizontal_spacing=0.03, subplot_titles=titles,
                        column_widths=[0.42, 0.38, 0.2][:ncol])
    fig.add_trace(go.Scatter(x=gs["median"], y=gs.label, mode="markers", marker=dict(size=10, color=col),
                             error_x=dict(type="data", symmetric=False, array=(gs.med_hi - gs["median"]).fillna(0),
                                          arrayminus=(gs["median"] - gs.med_lo).fillna(0), color="#888"),
                             customdata=np.c_[gs.best, gs.pages], hovertemplate="%{y}<br>median %{x:,.0f}<br>best %{customdata[0]:,.0f}<br>%{customdata[1]}<extra></extra>",
                             showlegend=False), 1, 1)
    fig.add_trace(go.Scatter(x=gs.hit_rate, y=gs.label, mode="markers+text", marker=dict(size=10, color=col, symbol="diamond"),
                             text=[f" {h}/{n}" for h, n in zip(gs.hits, gs.n)], textposition="middle right",
                             error_x=dict(type="data", symmetric=False, array=gs.hit_hi - gs.hit_rate, arrayminus=gs.hit_rate - gs.hit_lo, color="#888"),
                             showlegend=False, hovertemplate="%{y}<br>hit rate %{x:.0%}<extra></extra>"), 1, 2)
    if ext is not None:
        e = gs.group.map(ext).fillna(0)
        fig.add_trace(go.Bar(x=e, y=gs.label, orientation="h", marker_color="#2ca02c", showlegend=False, text=e.astype(int), textposition="outside"), 1, 3)
    fig.update_xaxes(type="log", row=1, col=1); fig.update_xaxes(range=[0, 1.15], tickformat=".0%", row=1, col=2)
    return layout(fig, title, h=max(380, 26 * len(gs) + 140))

def scatter_grid(df, feats, title, labels, cols=3, logy=True):
    rows = int(np.ceil(len(feats) / cols)); stats = {}
    for f in feats:
        rho, p, n = spearman_perm(df[f], np.log10(df["views"]), groups=df["page"], n_perm=3000)
        stats[f] = (rho, p, n)
    fig = make_subplots(rows=rows, cols=cols, subplot_titles=[f"{labels.get(f, f)}<br><sub>within-page ρ={stats[f][0]:.2f}, p={fmt_p(stats[f][1])}, n={stats[f][2]}</sub>" for f in feats],
                        vertical_spacing=0.16, horizontal_spacing=0.06)
    pages = sorted(df.page.dropna().unique()); cmap = {p: PAL[i % len(PAL)] for i, p in enumerate(pages)}
    for i, f in enumerate(feats):
        r, c = i // cols + 1, i % cols + 1
        for pg in pages:
            g = df[(df.page == pg) & df[f].notna() & df.views.notna()]
            if g.empty: continue
            fig.add_trace(go.Scatter(x=g[f], y=g.views, mode="markers", name=pg, legendgroup=pg, showlegend=(i == 0),
                                     marker=dict(color=cmap[pg], size=7, opacity=0.75), text=g.hook_text.astype(str),
                                     hovertemplate="%{text}<br>x=%{x}<br>views %{y:,.0f}<extra>" + pg + "</extra>"), r, c)
        if logy: fig.update_yaxes(type="log", row=r, col=c)
    return layout(fig, title, h=300 * rows + 80), stats

def table(df, cols, fmt=None, max_rows=200, cls=""):
    fmt = fmt or {}
    th = "".join(f"<th>{html.escape(str(c))}</th>" for c in cols.values())
    trs = []
    for _, r in df.head(max_rows).iterrows():
        tds = []
        for c in cols:
            v = r.get(c); f = fmt.get(c)
            s = f(v) if f else ("–" if v is None or (isinstance(v, float) and not np.isfinite(v)) else str(v))
            tds.append(f"<td>{html.escape(str(s)) if not str(s).startswith('<') else s}</td>")
        trs.append("<tr>" + "".join(tds) + "</tr>")
    return f'<table class="t {cls}"><thead><tr>{th}</tr></thead><tbody>{"".join(trs)}</tbody></table>'

pct = lambda v: "–" if v is None or not np.isfinite(v) else f"{v:.0%}"
ci_pct = lambda r: f"{r.hit_rate:.0%} ({r.hit_lo:.0%}–{r.hit_hi:.0%})"

def build(public=False, png=True):
    reels, reel_src = L.load_reels()
    titles = L.taxonomy()
    own = L.enrich(reels)
    own["hit"] = own.views >= HIT_ABS_VIEWS
    if public:
        import public_scrub as PS
        own = PS.scrub_reels(own); reels = PS.scrub_reels(reels)
    ext = reels[(reels.source != "own") & reels.views.notna()].copy()
    ext_org = ext[ext.get("organic", 1).fillna(1).astype(int) == 1] if "organic" in ext else ext
    sections, warn = [], []
    if reel_src != "hookforge.db": warn.append(f"hookforge.db not found/readable: reels read from {reel_src}. The loader switches automatically when the DB exists.")
    owv = own[own.views.notna()]
    fbv = owv[owv.platform == "FB"]  # leaderboards use FB only (hooks REPORT: IG kept for cross-platform pairs; many IG files are re-posts)

    # ---------- 1. Per-page / product performance over time ----------
    pages = sorted(owv.page.unique()); cmap = {p: PAL[i % len(PAL)] for i, p in enumerate(pages)}
    fig = go.Figure(); pg_rows_extra = []
    for pg in pages:
        g = owv[owv.page == pg].sort_values("posted_dt")
        fig.add_trace(go.Scatter(x=g.posted_dt, y=g.views, mode="markers", name=f"{pg} (n={len(g)})", marker=dict(color=cmap[pg], size=8,
                                 symbol=["star" if h else "circle" for h in g.hit], line=dict(width=0.5, color="#333")),
                                 text=g.hook_text.astype(str), customdata=np.c_[g["format"].astype(str), g["product"].astype(str), g["key"].astype(str)],
                                 hovertemplate="<b>%{customdata[2]}</b> %{text}<br>%{customdata[1]} · %{customdata[0]}<br>%{x|%b %d %H:%M} PT<br>views %{y:,.0f}<extra></extra>"))
    ins = L.load_insights()
    if public and ins is not None: ins = PS.scrub_reels(ins)
    ins_only = pd.DataFrame()
    if ins is not None:  # pages ingested from Insights but not yet in the corpus/DB (e.g. a new page) still show up here
        ins_only = ins[~ins.page_code.isin(owv.page_code.unique()) & ins.views.notna()].copy()
        if public: ins_only["page"] = ins_only.page_code
        for i, (pg, g) in enumerate(ins_only.groupby("page")):
            fig.add_trace(go.Scatter(x=g.posted_dt, y=g.views, mode="markers", name=f"{pg} [Insights only] (n={len(g)})",
                                     marker=dict(size=8, symbol="diamond-open", color=PAL[(len(pages) + i) % len(PAL)]),
                                     text=g.caption.astype(str).str[:80], hovertemplate="%{text}<br>%{x|%b %d %H:%M} PT<br>views %{y:,.0f}<extra></extra>"))
            med, lo, hi = boot_median(g.views); hits = int((g.views >= HIT_ABS_VIEWS).sum()); p_, wl, wh = wilson(hits, len(g))
            pg_rows_extra.append(dict(page=f"{pg} [Insights only]", products="(not in corpus yet)", n=len(g), hits=hits, hit=f"{p_:.0%} ({wl:.0%}–{wh:.0%})",
                                      median=f"{fmt_views(med)} ({fmt_views(lo)}–{fmt_views(hi)})", best=fmt_views(g.views.max()),
                                      first=g.posted_dt.min().strftime("%b %d"), last=g.posted_dt.max().strftime("%b %d"), total=fmt_views(g.views.sum())))
    fig.add_hline(y=HIT_ABS_VIEWS, line_dash="dot", line_color="#999", annotation_text=f"hit line {fmt_views(HIT_ABS_VIEWS)}")
    fig.update_yaxes(type="log", title="views (log)"); fig.update_xaxes(title="posted (PT)")
    layout(fig, f"Own reels over time, by page (n={len(owv)}; ★ = hit)", h=470); FIGS["timeline"] = fig
    pg_rows = []
    for pg, g in owv.groupby("page"):
        med, lo, hi = boot_median(g.views); p, wl, wh = wilson(int(g.hit.sum()), len(g))
        pg_rows.append(dict(page=pg, products=", ".join(sorted(g["product"].dropna().astype(str).unique())), n=len(g), hits=int(g.hit.sum()),
                            hit=f"{p:.0%} ({wl:.0%}–{wh:.0%})", median=f"{fmt_views(med)} ({fmt_views(lo)}–{fmt_views(hi)})", best=fmt_views(g.views.max()),
                            first=g.posted_dt.min().strftime("%b %d"), last=g.posted_dt.max().strftime("%b %d"), total=fmt_views(g.views.sum())))
    pg_tbl = pd.concat([pd.DataFrame(pg_rows).sort_values("n", ascending=False), pd.DataFrame(pg_rows_extra)], ignore_index=True)
    # product age decay
    fig2 = go.Figure(); dec = []
    pdcol = "product_day" if owv["product_day"].notna().any() else "ff_product_day"
    for pg in pages:
        g = fbv[(fbv.page == pg) & fbv[pdcol].notna()]
        if len(g) < 4: continue
        rho, p, n = spearman_perm(g[pdcol], np.log10(g.views), n_perm=2000); dec.append((pg, rho, p, n))
        fig2.add_trace(go.Scatter(x=g[pdcol], y=g.views, mode="markers", name=f"{pg}: ρ={rho:.2f} (n={n}, p={fmt_p(p)})",
                                  marker=dict(color=cmap[pg], size=8), text=g.hook_text.astype(str)))
    fig2.update_yaxes(type="log", title="views (log)"); fig2.update_xaxes(title="days since this product's first post on the page")
    layout(fig2, "Product age vs views (freshness decay), FB pages with n≥4", h=420)
    sections.append(("perf", "Per-page & per-product performance",
        f'<div class="fig">{fig.to_html(False, include_plotlyjs=False)}</div>' +
        table(pg_tbl, dict(page="Page", products="Product(s)", n="n reels", hits="hits", hit="hit rate (95% CI)", median="median views (90% CI)", best="best", total="total views", first="first", last="last")) +
        f'<div class="fig">{fig2.to_html(False, include_plotlyjs=False)}</div>',
        f"Source: {reel_src} (own reels). Views are as captured on 2026-10-18 (lifetime to date). Note the confounds the hooks report found: served resolution (an OUTCOME of watch time, D7, never a lever) and product age overlap; a page's late posts are older-product posts."))

    # ---------- 2. Views vs shares vs profile visits vs sales per 1K ----------
    daily = L.load_store_daily(); fam = L.load_family_per1k(); ig = L.load_ig_note()
    parts = []
    s1k = owv[owv.get("orders_per_1k").notna()] if "orders_per_1k" in owv else pd.DataFrame()
    if len(s1k):
        fig = go.Figure()
        sname = {"MJ": "Merry Jammies store (HJ page)", "MG": "Merry Glow store", "BH": "Brick Hood store"}
        for st_, g in s1k.groupby("sales_store"):
            fig.add_trace(go.Scatter(x=g.views, y=g.orders_per_1k, mode="markers", name=f"{sname.get(st_, st_)} (n={len(g)})", text=g.hook_text.astype(str),
                                     customdata=np.c_[g.net_per_1k, g.sessions_per_1k], marker=dict(size=9),
                                     hovertemplate="%{text}<br>views %{x:,.0f}<br>orders/1K %{y:.3f}<br>net $/1K %{customdata[0]:.2f}<br>sessions/1K %{customdata[1]:.1f}<extra></extra>"))
        rho, p, n = spearman_perm(s1k.views, s1k.orders_per_1k, n_perm=3000)
        fig.update_xaxes(type="log", title="reel views (log)"); fig.update_yaxes(title="allocated orders per 1K views")
        layout(fig, f"Sales per 1K views by reel (allocation model; n={n}, Spearman ρ={rho:.2f}, p={fmt_p(p)})", h=420); FIGS["sales1k"] = fig
        parts.append(f'<div class="fig">{fig.to_html(False, include_plotlyjs=False)}</div>')
    if fam is not None:
        f2 = fam.sort_values(["store", "orders_per_1k"]).copy()
        f2["label"] = f2.store + " · " + f2.family.astype(str) + " (reels=" + f2.n_reels.astype(int).astype(str) + ")"
        fig = go.Figure(go.Scatter(x=f2.orders_per_1k, y=f2.label, mode="markers", marker=dict(size=10, color=["#bbb" if n < 3 else "#d62728" for n in f2.n_reels]),
                                   error_x=dict(type="data", symmetric=False, array=(f2.hi - f2.orders_per_1k).clip(lower=0).fillna(0), arrayminus=(f2.orders_per_1k - f2.lo).clip(lower=0).fillna(0)),
                                   customdata=np.c_[f2.views, f2.net_per_1k], hovertemplate="%{y}<br>orders/1K %{x:.3f}<br>views %{customdata[0]:,.0f}<br>net $/1K %{customdata[1]:.2f}<extra></extra>"))
        fig.update_xaxes(title="orders per 1K views (interval = store-specific model range)")
        layout(fig, "Orders per 1K views by hook family and store (grey = fewer than 3 reels)", h=max(380, 24 * len(f2) + 120))
        parts.append(f'<div class="fig">{fig.to_html(False, include_plotlyjs=False)}</div>')
    eng = []
    if ig is not None and len(ig):
        for r in ig.itertuples():
            for m in ("shares", "saves", "profile_visits", "likes", "comments"):
                eng.append(dict(source=f"IG @merry.jammies (n={len(ig)})", metric=m, per1k=getattr(r, m) / r.plays * 1000, views=r.plays))
    if ins is not None:
        fb = ins[ins.views >= 1000]
        for m in ("shares", "follows", "link_clicks", "clicks", "comments"):
            g = fb[fb[m].notna()]
            for r in g.itertuples(): eng.append(dict(source="FB Insights (own pages, ≥1K views)", metric=m, per1k=getattr(r, m) / r.views * 1000, views=r.views))
    if len(ext):
        for m in ("shares", "likes"):
            g = ext[ext[m].notna() & (ext.views > 0)] if m in ext else pd.DataFrame()
            for r in g.itertuples(): eng.append(dict(source="External viral (TikTok/IG/FB)", metric=m, per1k=getattr(r, m) / r.views * 1000, views=r.views))
    if eng:
        e = pd.DataFrame(eng); e = e[np.isfinite(e.per1k)]
        cnt = e.groupby(["source", "metric"]).size()
        fig = go.Figure()
        for i, (src, g) in enumerate(e.groupby("source")):
            fig.add_trace(go.Box(x=g.metric + "<br>n=" + g.metric.map(lambda m: str(cnt.get((src, m), 0))) if False else g.metric, y=g.per1k, name=src,
                                 boxpoints="all", jitter=0.4, pointpos=0, marker=dict(size=5, color=PAL[i]), line=dict(color=PAL[i])))
        fig.update_layout(boxmode="group"); fig.update_yaxes(type="log", title="per 1K views (log)")
        ann = "; ".join(f"{s.split(' (')[0]} {m}: n={c}" for (s, m), c in cnt.items())
        layout(fig, "Engagement per 1K views: shares, saves, profile visits, follows, link clicks", h=440)
        med = e.groupby(["source", "metric"]).per1k.agg(["size", "median", "min", "max"]).reset_index()
        parts.append(f'<div class="fig">{fig.to_html(False, include_plotlyjs=False)}</div>' +
                     table(med, dict(source="Source", metric="Metric", size="n", median="median /1K", min="min /1K", max="max /1K"),
                           {c: (lambda v: f"{v:.2f}") for c in ("median", "min", "max")}))
    if daily is not None and not public:
        fig = make_subplots(rows=1, cols=2, subplot_titles=["Orders per day (PT)", "Sessions per day (PT)"])
        for i, (st_, g) in enumerate(daily.groupby("store")):
            g = g[g.day >= g[g.sessions > 0].day.min() - pd.Timedelta(days=1)]
            fig.add_trace(go.Bar(x=g.day, y=g.orders, name=st_, marker_color=PAL[i], legendgroup=st_), 1, 1)
            fig.add_trace(go.Scatter(x=g.day, y=g.sessions, name=st_, line=dict(color=PAL[i]), legendgroup=st_, showlegend=False), 1, 2)
        layout(fig, "Store outcomes over time (Shopify aggregates, no customer data)", h=380)
        parts.insert(0, f'<div class="fig">{fig.to_html(False, include_plotlyjs=False)}</div>')
    sections.append(("sales", "Views vs shares vs profile visits vs sales per 1K", "".join(parts),
        "Per-reel sales are <b>allocations</b>, not tracked attribution. The Shopify workstream split each store's orders across reels by time window and views (team/shopify/attrib.py, mg_attrib.py, brickhood/analyze.py), so treat them as model estimates. Link captions are excluded as a cause, because links were added after reels took off. Engagement metrics come from different platforms and pages: compare within a source, not across."))

    # ---------- 3. Hook family leaderboard ----------
    hf = group_stats(fbv, "hook_family")
    figH = leaderboard_fig(hf, f"Hook family leaderboard: own FB reels (n={len(fbv)}; grey = n<{LOW_N})"); FIGS["hook_family"] = figH
    sections.append(("hooks", "Hook family leaderboard", f'<div class="fig">{figH.to_html(False, include_plotlyjs=False)}</div>' +
        table(hf, dict(group="Hook family", n="n", hits="hits", hit_rate="hit rate", median="median views", best="best", pages="pages", categories="categories"),
              dict(hit_rate=pct, median=fmt_views, best=fmt_views)),
        "Ranked by the Wilson lower bound of hit rate (rewards hit rate AND sample size). The hooks report found text wording on its own has no detectable effect once page, product age and resolution are controlled. Families mostly stand in for the footage and opening that come with them."))

    # ---------- 4. Format leaderboard ----------
    fs = group_stats(fbv, "format")
    ext1m = ext_org[ext_org.views >= 1e6].groupby("format").size().to_dict()
    figF = leaderboard_fig(fs, f"Format leaderboard: own FB reels (n={len(fbv)}) + external organic proof (≥1M reels, n={sum(ext1m.values())})",
                           label_map={k: f"{k} {v}" for k, v in titles.items()}, ext=ext1m); FIGS["format"] = figF
    es = group_stats(ext_org.assign(page=ext_org.get("page_code", "ext")), "format")
    fs_out = fs.copy(); fs_out["title"] = fs_out.group.map(titles)
    sections.append(("formats", "Format leaderboard", f'<div class="fig">{figF.to_html(False, include_plotlyjs=False)}</div>' +
        "<h4>Own reels</h4>" + table(fs_out, dict(group="Format", title="Title", n="n", hits="hits", hit_rate="hit rate", median="median", best="best", categories="categories hit/posted on"),
                                     dict(hit_rate=pct, median=fmt_views, best=fmt_views)) +
        f"<h4>External / research organic reels (n={len(ext_org)}; all are viral by selection, so this is proof of reach, not a hit rate)</h4>" +
        table(es.sort_values("n", ascending=False), dict(group="Format", n="n", median="median views", best="best", categories="categories"), dict(median=fmt_views, best=fmt_views)),
        "Formats are assigned by engine/hookforge/taxonomy.py:format_of(). External reels were picked because they went viral (survivorship), so they show that a format can reach 1M+, not how often it does. Our own hit rate is the only real rate."))

    # ---------- 5. First-frame / visual features ----------
    fsc = L.load_feature_screen(); parts = []
    if fsc is not None:
        d = fsc.sort_values("mult").copy()
        lab = {"contrast_0": "first-frame contrast (per SD)", "product_pct_0": "product % of frame at 0 s (per SD)", "night_18_04": "posted 18:00–04:00 PT",
               "flow_1_3": "motion 1–3 s (per SD)", "product_visible_0": "product visible at 0 s", "people_n": "people in frame (per SD)",
               "face_visible_0": "face visible at 0 s", "first_cut_s": "first cut time (per SD)", "bright_0": "brightness (per SD)", "sat_0": "saturation (per SD)"}
        d["label"] = d.feature.map(lambda f: lab.get(f, f)) + "  (p=" + d.perm_p.astype(str) + ")"
        fig = go.Figure(go.Scatter(x=d.mult, y=d.label, mode="markers", marker=dict(size=9, color=["#d62728" if p < 0.05 else "#999" for p in d.perm_p]),
                                   error_x=dict(type="data", symmetric=False, array=d.hi - d.mult, arrayminus=d.mult - d.lo, color="#bbb")))
        fig.add_vline(x=1, line_dash="dot"); fig.update_xaxes(type="log", title="× views (adjusted multiplier, 95% CI, log)")
        layout(fig, f"First 3 s features: adjusted effect on views (team model, census pages n={int(d.n.max())}; red = permutation p<0.05)", h=820); FIGS["first_frame"] = fig
        parts.append(f'<div class="fig">{fig.to_html(False, include_plotlyjs=False)}</div>')
    ffe = owv[owv.platform == "FB"].copy()
    feats = [f for f in ["ff_product_pct_0", "ff_contrast_0", "ff_people_n", "ff_flow_1_3", "ff_first_cut_s", "ff_bright_0"] if f in ffe]
    if feats:
        figS, _ = scatter_grid(ffe, feats, f"Raw first-frame features vs views, FB own reels (n={ffe[feats[0]].notna().sum()})",
                               {"ff_product_pct_0": "product % of frame at 0 s", "ff_contrast_0": "contrast at 0 s", "ff_people_n": "people in opening",
                                "ff_flow_1_3": "optical flow 1–3 s", "ff_first_cut_s": "first cut (s)", "ff_bright_0": "brightness at 0 s"})
        parts.append(f'<div class="fig">{figS.to_html(False, include_plotlyjs=False)}</div>')
    sections.append(("visual", "First-frame & visual features vs views", "".join(parts),
        "Top chart: multipliers from the hooks workstream's adjusted model (page fixed effects + product age + served resolution; caution: served resolution is post-treatment (an outcome of watch time), so adjusting for it can bias these multipliers toward zero). Nothing is refitted here, the values are read from team/hooks/feature_screen_census.csv. Only contrast survives at p<0.01, and none survive a 32-feature FDR correction (hooks REPORT §7). Bottom: raw data with a within-page permutation test. It is unadjusted, so use it to sanity-check the model, not to set rules."))

    # ---------- 6. Shot timing ----------
    parts = []; sh_feats = [f for f in ["sh_dur", "sh_n_shots", "sh_avg_shot", "sh_first_cut", "sh_last_shot_dur", "sh_tempo"] if f in owv]
    if sh_feats:
        figT, _ = scatter_grid(fbv, sh_feats, f"Edit timing vs views, own FB reels (n={fbv[sh_feats[0]].notna().sum()})",
                               {"sh_dur": "reel length (s)", "sh_n_shots": "number of shots", "sh_avg_shot": "average shot length (s)",
                                "sh_first_cut": "first cut = hook length (s)", "sh_last_shot_dur": "payoff shot length (s)", "sh_tempo": "music tempo (BPM)"})
        FIGS["timing"] = figT; parts.append(f'<div class="fig">{figT.to_html(False, include_plotlyjs=False)}</div>')
    shots = L.load_shots()
    if shots is not None:
        shots["hit"] = shots.views >= HIT_ABS_VIEWS
        fig = go.Figure()
        for hit, colr in ((True, "#d62728"), (False, "#1f77b4")):
            g = shots[shots.hit == hit]
            fig.add_trace(go.Box(x=g.role, y=g.dur, name=f"{'hits' if hit else 'non-hits'} ({g.key.nunique()} reels, {len(g)} shots)", marker_color=colr, boxpoints="outliers"))
        fig.update_layout(boxmode="group"); fig.update_yaxes(title="shot duration (s)")
        layout(fig, "Shot durations by role: hits vs non-hits (team/body/shots.csv)", h=400)
        rs = shots.groupby(["role", "hit"]).dur.agg(["size", "median"]).reset_index()
        rs["hit"] = rs.hit.map({True: "hit", False: "non-hit"})
        parts.append(f'<div class="fig">{fig.to_html(False, include_plotlyjs=False)}</div>' +
                     table(rs, dict(role="role", hit="group", size="n shots", median="median s"), dict(median=lambda v: f"{v:.2f}")))
    sections.append(("timing", "Shot timing vs views", "".join(parts),
        "Edit measurements are from the body workstream (ffmpeg scene detection plus hand review). Each panel title gives the within-page Spearman ρ and permutation p, since every page has its own house edit. Read medians together with the engine's EDIT spec (engine/hookforge/config.py)."))

    # ---------- 7. Retention ----------
    parts = []
    if ins is not None:
        R = ins[ins.views >= 100].copy()
        if public: R["page"] = R.page_code
        fig = make_subplots(rows=1, cols=2, subplot_titles=["Average watch time (s) vs views", "3-second view rate vs views"])
        rp = sorted(R.page.unique())
        for i, pg in enumerate(rp):
            g = R[R.page == pg]
            for j, m in enumerate(("avg_watch_s", "three_sec_rate")):
                gg = g[g[m].notna()]
                rho, p, n = spearman_perm(gg[m], np.log10(gg.views), n_perm=2000) if len(gg) >= 4 else (np.nan, np.nan, len(gg))
                rtxt = f"ρ_watch={rho:.2f}" if np.isfinite(rho) else "ρ n/a"
                fig.add_trace(go.Scatter(x=gg[m], y=gg.views, mode="markers", marker=dict(color=PAL[i], size=8), legendgroup=pg,
                                         name=f"{pg}: {rtxt} (n={n})" if j == 0 else pg, showlegend=(j == 0),
                                         text=gg.caption.astype(str).str[:70], hovertemplate="%{text}<br>%{x}<br>views %{y:,.0f}<extra>" + pg + "</extra>"), 1, j + 1)
        rho_w, p_w, n_w = spearman_perm(R.avg_watch_s, np.log10(R.views), groups=R.page, n_perm=3000)
        rho_3, p_3, n_3 = spearman_perm(R.three_sec_rate, np.log10(R.views), groups=R.page, n_perm=3000)
        fig.update_yaxes(type="log"); fig.update_xaxes(tickformat=".0%", row=1, col=2)
        layout(fig, f"Retention vs reach, FB Insights (reels ≥100 views). Within-page ρ: watch {rho_w:.2f} (p={fmt_p(p_w)}, n={n_w}); 3-s rate {rho_3:.2f} (p={fmt_p(p_3)}, n={n_3})", h=440)
        FIGS["retention"] = fig; parts.append(f'<div class="fig">{fig.to_html(False, include_plotlyjs=False)}</div>')
        bench = []
        for pg, g in R.groupby("page"):
            for hit in (True, False):
                gg = g[(g.views >= HIT_ABS_VIEWS) == hit]
                if len(gg): bench.append(dict(page=pg, group="hit" if hit else "non-hit", n=len(gg), three=gg.three_sec_rate.median(), watch=gg.avg_watch_s.median(),
                                              pctw=gg.avg_pct_watched.median(), comp=gg.completion_rate.median(), drop=gg.biggest_dropoff_s.median()))
        parts.append("<h4>Retention benchmarks: hits vs non-hits per page (medians)</h4>" + table(pd.DataFrame(bench),
            dict(page="Page", group="group", n="n", three="3-s rate", watch="avg watch s", pctw="avg % watched (n small)", comp="completion %", drop="biggest drop-off at s"),
            dict(three=pct, watch=lambda v: "–" if not np.isfinite(v) else f"{v:.0f}", pctw=lambda v: "–" if not np.isfinite(v) else f"{v:.0f}%",
                 comp=lambda v: "–" if not np.isfinite(v) else f"{v:.1f}%", drop=lambda v: "–" if not np.isfinite(v) else f"{v:.0f}")))
        top = R[R.avg_pct_watched.notna()].sort_values("views", ascending=False)
        parts.append("<h4>Reels with full retention detail</h4>" + table(top, dict(page="Page", posted_pt="posted (PT)", views="views", avg_watch_s="avg watch s",
            avg_pct_watched="avg % watched", completion_rate="completion %", biggest_dropoff_s="biggest drop-off (s)", shares="shares", follows="follows"),
            dict(views=lambda v: f"{v:,.0f}")))
    hjr = owv[(owv.page_code == "HJ") & owv.three_sec_rate.notna()] if "three_sec_rate" in owv else pd.DataFrame()
    if len(hjr) >= 4:
        rho, p, n = spearman_perm(hjr.three_sec_rate, np.log10(hjr.views), n_perm=3000)
        parts.append(f"<p class='note'>HeatedJammies reels with a 3-s rate in the corpus: n={n}, Spearman ρ(3-s rate, log views)={rho:.2f}, p={fmt_p(p)}. Full HJ retention will appear here after <code>ingest_insights.py --page HeatedJammies --code HJ</code>.</p>")
    sections.append(("retention", "Retention insights", "".join(parts) or "<p>No Insights data ingested yet.</p>",
        "Source: analytics/data/insights/*.csv, built by ingest_insights.py from the team's logged-in Insights captures. FB reports watch time in whole seconds, and % watched, completion and drop-off only for each page's top reels, so n is small there. Pooled across pages the correlation is misleading (hooks REPORT §6), so ρ is computed within page."))

    # ---------- 8. Posting hour ----------
    fbo = owv[owv.platform == "FB"].copy(); fbo["hb"] = (fbo.post_hour // 3 * 3).astype("Int64")
    hs = group_stats(fbo.assign(hb=fbo.hb.map(lambda h: f"{int(h):02d}–{int(h)+3:02d}")), "hb").sort_values("group")
    fig = make_subplots(rows=1, cols=2, subplot_titles=["Own FB reels: median views by posting hour (PT), 90% CI", "Hit rate by posting hour, Wilson 95% CI"])
    colr = ["#bbb" if n < LOW_N else "#1f77b4" for n in hs.n]; xl = [f"{g}<br>n={n}" for g, n in zip(hs.group, hs.n)]
    fig.add_trace(go.Scatter(x=xl, y=hs["median"], mode="markers", marker=dict(size=11, color=colr), error_y=dict(type="data", symmetric=False,
                  array=(hs.med_hi - hs["median"]).fillna(0), arrayminus=(hs["median"] - hs.med_lo).fillna(0)), showlegend=False), 1, 1)
    fig.add_trace(go.Scatter(x=xl, y=hs.hit_rate, mode="markers", marker=dict(size=11, color=colr, symbol="diamond"),
                  error_y=dict(type="data", symmetric=False, array=hs.hit_hi - hs.hit_rate, arrayminus=hs.hit_rate - hs.hit_lo), showlegend=False), 1, 2)
    fig.update_yaxes(type="log", row=1, col=1); fig.update_yaxes(tickformat=".0%", range=[0, 1.05], row=1, col=2)
    layout(fig, f"Posting hour effects (FB own reels, n={len(fbo)})", h=400); FIGS["hour"] = fig
    hourly = L.load_store_hourly(); parts = [f'<div class="fig">{fig.to_html(False, include_plotlyjs=False)}</div>']
    night = fbo.post_hour.apply(lambda h: h >= 18 or h < 4)
    kn, nn, kd, nd = int(fbo[night].hit.sum()), int(night.sum()), int(fbo[~night].hit.sum()), int((~night).sum())
    parts.append(f"<p class='note'>Night (18:00–04:00 PT) vs day, raw: hits {kn}/{nn} ({pct(kn/nn if nn else np.nan)}) vs {kd}/{nd} ({pct(kd/nd if nd else np.nan)}), Fisher p={fmt_p(fisher(kn, nn, kd, nd))}. Adjusted for page, product age and served resolution, the hooks model gives ×3.4 views (95% CI 1.2–10.3, p=0.03). Served resolution is post-treatment, so treat this as a hypothesis (EXP-2026-10-19-01), not a rule.</p>")
    if hourly is not None:
        hourly["h"] = hourly.t.dt.hour; fig = go.Figure()
        for i, (st_, g) in enumerate(hourly.groupby("store")):
            o = g.groupby("h").orders.sum(); tot = o.sum()
            fig.add_trace(go.Scatter(x=o.index, y=o / tot, mode="lines+markers", name=(st_ if public else f"{st_} (orders n={int(tot)})"), line=dict(color=PAL[i])))
        fig.update_xaxes(title="hour of day (PT)", dtick=2); fig.update_yaxes(tickformat=".0%", title="share of the store's orders")
        layout(fig, "When buyers buy: share of orders by hour of day (Shopify, PT)", h=380); parts.append(f'<div class="fig">{fig.to_html(False, include_plotlyjs=False)}</div>')
    sections.append(("hour", "Posting-hour effects", "".join(parts),
        "Posting hour is confounded with page and with which posts the team treated as 'main' posts. The order curve shows when buyers check out. Combined with the views evidence, this gives the config.POST_WINDOW_PT default (post 22:00–02:00 PT)."))

    # ---------- 9. Experiments ----------
    ex, is_example = L.load_experiments()
    if public: ex = ex.drop(columns=[c for c in ("notes", "variable_changed", "proof_keys", "hook", "caption", "brief") if c in ex])
    exr = ex[ex.get("is_example", 0).fillna(0).astype(int) == 0] if "is_example" in ex else ex
    parts = []
    if is_example: parts.append("<div class='banner'>EXAMPLE SCHEMA ONLY: learning/experiments.csv does not exist yet. The rows below are placeholders (is_example=1, no outcomes) that show the format. Stats ignore them.</div>")
    parts.append(table(ex, {c: c for c in ["experiment_id", "is_example", "arm", "is_innovation", "format", "variable_changed", "proof_keys", "status", "views_24h", "views_7d", "decision", "notes"] if c in ex.columns}))
    done = exr[pd.to_numeric(exr.get("views_7d"), errors="coerce").notna()] if len(exr) else exr
    if len(done):
        rows = []
        for eid, g in done.groupby("experiment_id"):
            c = g[g.arm == "control"]
            if len(c) != 1: continue
            for r in g[g.arm != "control"].itertuples(): rows.append(dict(exp=f"{eid}:{r.arm}", ratio=float(r.views_7d) / float(c.views_7d.iloc[0]), innov=r.is_innovation))
        if rows:
            d = pd.DataFrame(rows); fig = go.Figure(go.Bar(x=d.exp, y=d.ratio, marker_color=["#ff7f0e" if i else "#1f77b4" for i in d.innov]))
            fig.add_hline(y=1, line_dash="dot"); fig.update_yaxes(type="log", title="variant / control views (7 d)")
            parts.append(f'<div class="fig">{layout(fig, f"Experiment results (n={len(d)} variant arms; orange = innovation budget)").to_html(False, include_plotlyjs=False)}</div>')
    n_innov = int(pd.to_numeric(exr.get("is_innovation"), errors="coerce").fillna(0).sum()) if len(exr) else 0
    parts.append(f"<p class='note'>Innovation budget target: {INNOVATION_SHARE:.0%} of output (engine/hookforge/config.py). Real arms logged: {len(exr)}; innovation arms: {n_innov}. Schema: analytics/schemas/experiments.schema.md.</p>")
    sections.append(("experiments", "Experiment tracker", "".join(parts), "Reads learning/experiments.csv once the learning loop writes it. One variable per arm; every arm cites proof_keys, the viral reels it was derived from."))

    # ---------- 10. What to make next (computed) ----------
    rows = []
    allf = sorted(set(fs.group if len(fs) else []) | set(ext1m))
    for f in allf:
        r = fs[fs.group == f]; n = int(r.n.iloc[0]) if len(r) else 0; hits = int(r.hits.iloc[0]) if len(r) else 0
        p, lo, hi = wilson(hits, n); e = int(ext1m.get(f, 0))
        cat_hits = fbv[fbv.format == f].groupby("category").agg(h=("hit", "sum"), n=("hit", "size"))
        cats = "; ".join(f"{c} {int(x.h)}/{int(x.n)}" for c, x in cat_hits.iterrows())
        if n >= 3 and lo >= 0.15: tier, why = "EXPLOIT", f"own hit rate {hits}/{n}, 95% lower bound {lo:.0%}"
        elif n >= 3 and hits == 0: tier, why = "AVOID as lead", f"0/{n} own hits"
        elif e >= 2 and n < 3: tier, why = "EXPLORE (innovation budget)", f"{e} external organic reels ≥1M; own n={n}"
        elif n >= 3: tier, why = "WATCH", f"own {hits}/{n}, lower bound {lo:.0%} < 15%"
        else: tier, why = "INSUFFICIENT DATA", f"own n={n}, external ≥1M n={e}"
        rows.append(dict(format=f, title=titles.get(f, ""), tier=tier, why=why, own=f"{hits}/{n}", lb=lo, ext=e, cats=cats,
                         median=float(r["median"].iloc[0]) if len(r) else np.nan))
    order = {"EXPLOIT": 0, "EXPLORE (innovation budget)": 1, "WATCH": 2, "INSUFFICIENT DATA": 3, "AVOID as lead": 4}
    nx = pd.DataFrame(rows); nx["o"] = nx.tier.map(order); nx = nx.sort_values(["o", "lb", "ext"], ascending=[True, False, False])
    catrows = []
    for cat, g in fbv.groupby("category"):
        r = group_stats(g, "format")
        r = r[r.n >= 2]
        catrows.append(dict(category=cat, n=len(g), hits=int(g.hit.sum()),
                            ranked="; ".join(f"{x.group} {titles.get(x.group, '')} {x.hits}/{x.n} (LB {x.hit_lo:.0%})" for x in r.itertuples()) or "no format with n≥2"))
    guard = []
    def arm(mask, label, src):
        a = ffe[mask.fillna(False)]; b = ffe[(~mask).fillna(False) & mask.notna()]
        ka, kb = int(a.hit.sum()), int(b.hit.sum()); pa, la, ha = wilson(ka, len(a)); pb, lb_, hb_ = wilson(kb, len(b))
        guard.append(dict(rule=label, yes=f"{ka}/{len(a)} = {pct(pa)} ({pct(la)}–{pct(ha)})", no=f"{kb}/{len(b)} = {pct(pb)} ({pct(lb_)}–{pct(hb_)})",
                          p=fmt_p(fisher(ka, len(a), kb, len(b))), src=src))
    if "ff_res_1440plus" in ffe: arm(ffe.ff_res_1440plus.map(lambda v: np.nan if pd.isna(v) else v == 1), "Served ≥1440p (vs 1080p): REVERSE CAUSATION, NOT A LEVER. FB only builds high-res copies after watch time (body REPORT §5; DECISIONS D7). Exports stay 2160×3840 regardless", "hook_features.res_1440plus (served copy = outcome)")
    if "ff_product_visible_0" in ffe: arm(ffe.ff_product_visible_0.map(lambda v: np.nan if pd.isna(v) else v == 1), "Product visible at 0.0 s", "hook_features.product_visible_0")
    arm(ffe.post_hour.map(lambda h: np.nan if pd.isna(h) else (h >= 18 or h < 4)), "Posted 18:00–04:00 PT", "corpus post_hour")
    if "ff_shock_face_0" in ffe: arm(ffe.ff_shock_face_0.map(lambda v: np.nan if pd.isna(v) else v == 1), "Shock face at 0 s", "hook_features.shock_face_0")
    fresh = []
    for pg, rho, p, n in dec: fresh.append(f"{pg}: ρ(product age, views)={rho:.2f} (n={n}, p={fmt_p(p)})")
    nxt = ("<div class='banner ok'>Computed from the data on every build. Tiers use fixed rules: EXPLOIT = own n≥3 and hit-rate Wilson lower bound ≥15%; "
           f"EXPLORE = ≥2 external organic reels ≥1M and own n&lt;3, which fills the {INNOVATION_SHARE:.0%} innovation budget; AVOID = own n≥3 with 0 hits. "
           "Check the per-category record before using a format on a different product category (transplants failed when the product wasn't legible at 0 s, per hooks REPORT §8).</div>" +
           table(nx, dict(format="Format", title="Title", tier="Tier", why="Evidence", own="own hits/n", ext="ext ≥1M n", median="own median", cats="own hits by category"),
                 dict(median=fmt_views)) +
           "<h4>Per product category: formats with n≥2, ranked by hit-rate lower bound (FB own reels)</h4>" +
           table(pd.DataFrame(catrows).sort_values("n", ascending=False), dict(category="Category", n="n reels", hits="hits", ranked="formats ranked (hits/n, Wilson LB)")) +
           "<h4>Production guardrails measured in our FB reels (raw hit rates, ≥50K)</h4>" +
           table(pd.DataFrame(guard), dict(rule="Condition", yes="with: hits/n (95% CI)", no="without", p="Fisher p", src="field")) +
           "<p class='note'>Freshness (within-page decay of views with product age): " + "; ".join(fresh) + ". A falling ρ means new products or angles beat re-posting an aging product.</p>")
    sections.insert(0, ("next", "What to make next", nxt, "This is a ranking aid, not an oracle. Hooks REPORT §1: identical files swing up to 300× between posts, so judge a format by hit rate over 3+ fresh renders."))

    # ---------- 11. Provenance + cross-checks ----------
    checks = []
    if daily is not None:
        tot = daily.groupby("store")[["orders", "net", "sessions"]].sum()
        for label, store, m, exp, tol, rep in EXPECTED:
            if store not in tot.index: continue
            if m.startswith("raw:"):
                got = L.shopify_raw_total(m[4:], "sessions"); srcf = m[4:]
            else:
                got = float(tot.loc[store, m]); srcf = L.STORES[store][0]
            ok = abs(round(got) - exp) <= tol if tol is not None else None
            checks.append(dict(check=label, computed=("hidden (public build)" if public else f"{got:,.2f}"), expected=("hidden" if public else f"{exp:,}"),
                               result=("PASS" if ok else "MISMATCH") if ok is not None else "INFO (known gap)", source=f"{srcf} vs {rep}"))
    if ig is not None:
        for label, code, m, exp in EXPECTED_IG:
            got = len(ig) if m == "n" else float(ig.loc[ig.code == code, m].iloc[0]) if (ig.code == code).any() else np.nan
            checks.append(dict(check=label, computed=f"{got:,.0f}", expected=f"{exp:,}", result="PASS" if got == exp else "MISMATCH", source="team/instagram/merryjammies_ig_reels.md parse"))
    for label, m, exp in (("Own reels in corpus", len(own), 78), ("Own FB reels with views", int((own.platform == "FB").sum() - own[(own.platform == "FB") & own.views.isna()].shape[0]), None)):
        checks.append(dict(check=label, computed=str(m), expected=str(exp) if exp else "info", result=("PASS" if m == exp else "MISMATCH") if exp else "INFO", source="hooks REPORT: 78 posted reels"))
    ck = pd.DataFrame(checks); ck.to_csv(os.path.join(HERE, "data", "crosschecks_public.csv" if public else "crosschecks.csv"), index=False)
    pv = pd.DataFrame(L.PROVENANCE).drop_duplicates(["data", "path"])
    try:
        import engine_panels; sections += [(a, b, c, d) for a, b, c, d in engine_panels.sections(public)]
    except Exception as e: warn.append(f"engine panels failed: {e}")
    sections.append(("prov", "Data provenance & cross-checks",
        "<h4>Cross-checks (recomputed on every build)</h4>" + table(ck, dict(check="Check", computed="computed", expected="expected (report)", result="result", source="source")) +
        "<h4>Every input file</h4>" + table(pv, dict(data="Data", path="File", rows="rows", modified="modified", note="note")),
        "If a check shows MISMATCH, the source file changed after the report was written, or the report used a different definition. The README explains the known definition differences."))

    # ---------- assemble ----------
    kpi = [("own reels (views known)", f"{len(owv)}"), ("own pages", f"{owv.page.nunique()}"), (f"own hits ≥{fmt_views(HIT_ABS_VIEWS)}", f"{int(owv.hit.sum())}"),
           ("external/research reels", f"{len(ext)}"), ("external ≥1M", f"{int((ext.views >= 1e6).sum())}"),
           ("reels with Insights watch time", f"{0 if ins is None else int(ins.avg_watch_s.notna().sum())}"),
           ("date range (PT)", f"{owv.posted_dt.min():%b %d}–{owv.posted_dt.max():%b %d}")]
    built = dt.datetime.now().strftime("%Y-%m-%d %H:%M PT")
    nav = "".join(f'<a href="#{sid}">{html.escape(t)}</a>' for sid, t, _, _ in sections)
    body = "".join(f'<section id="{sid}"><h2>{html.escape(t)}</h2>{content}<p class="cav"><b>How to read / caveats:</b> {cav}</p></section>' for sid, t, content, cav in sections)
    css = """body{font-family:-apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#f6f7f9;color:#222}header{background:#111;color:#fff;padding:14px 24px}
    header h1{margin:0;font-size:20px}header .sub{color:#bbb;font-size:12px;margin-top:4px}nav{position:sticky;top:0;background:#fff;border-bottom:1px solid #ddd;padding:8px 24px;z-index:9;overflow-x:auto;white-space:nowrap}
    nav a{margin-right:14px;color:#1f77b4;text-decoration:none;font-size:13px}main{padding:10px 24px;max-width:1500px;margin:auto}section{background:#fff;border:1px solid #e3e3e3;border-radius:8px;padding:14px 18px;margin:16px 0}
    h2{margin:4px 0 10px;font-size:18px}h4{margin:14px 0 6px}.kpis{display:flex;flex-wrap:wrap;gap:10px;margin:12px 0}.kpi{background:#fff;border:1px solid #e3e3e3;border-radius:8px;padding:8px 14px}
    .kpi b{display:block;font-size:20px}.kpi span{font-size:11px;color:#666}table.t{border-collapse:collapse;font-size:12px;margin:8px 0;width:100%}table.t th{background:#f0f2f5;text-align:left}
    table.t td,table.t th{border:1px solid #e5e5e5;padding:4px 6px;vertical-align:top}.cav{font-size:12px;color:#555;background:#fafafa;border-left:3px solid #ccc;padding:6px 10px}
    .note{font-size:12.5px}.banner{background:#fff3cd;border:1px solid #e0c36c;padding:8px 12px;border-radius:6px;margin:8px 0;font-size:13px}.banner.ok{background:#eef6ff;border-color:#9cc3ef}.warn{color:#a15c00;font-size:12px}"""
    warn_html = "".join(f"<div class='warn'>⚠ {html.escape(w)}</div>" for w in warn)
    doc = f"""<!doctype html><html><head><meta charset="utf-8"><title>Hookforge analytics</title><style>{css}</style>
<script type="text/javascript">{plotly.offline.get_plotlyjs()}</script></head><body>
<header><h1>HOOKFORGE · Analytics{' (public build)' if public else ''}</h1><div class="sub">Built {built} by analytics/build_dashboard.py · reels source: {html.escape(reel_src)} · hit = ≥{HIT_ABS_VIEWS:,} views · every number traces to the Provenance panel</div></header>
<nav>{nav}</nav><main>{warn_html}<div class="kpis">{''.join(f'<div class="kpi"><b>{v}</b><span>{k}</span></div>' for k, v in kpi)}</div>{body}</main></body></html>"""
    if public:   # last line of defence: deny-list audit over the finished HTML (no brand/product/page names, no hook text)
        import public_scrub as PS
        doc, found = PS.audit_html(doc, fix=True); _, left = PS.audit_html(doc, fix=False)
        json.dump(dict(redacted_in_final_pass=found, remaining=left), open(os.path.join(HERE, "data", "public_audit.json"), "w"), indent=1, ensure_ascii=False)
        assert not left, f"public dashboard still contains names/hook text: {list(left)[:5]}"
    out = os.path.join(HERE, "dashboard_public.html" if public else "dashboard.html")
    open(out, "w").write(doc); print("wrote", out, f"{os.path.getsize(out)/1e6:.1f} MB")
    print(ck.to_string(index=False))
    if png and not public:
        sd = os.path.join(HERE, "screenshots"); os.makedirs(sd, exist_ok=True)
        for name in ("format", "first_frame", "retention", "hook_family", "timeline"):
            if name in FIGS:
                try:
                    FIGS[name].write_image(os.path.join(sd, f"{name}.png"), width=1300, height=FIGS[name].layout.height or 500, scale=1.5); print("png", name)
                except Exception as e:
                    print("PNG export skipped:", e); break
    return out

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--public", action="store_true"); ap.add_argument("--no-png", action="store_true")
    a = ap.parse_args(); build(public=a.public, png=not a.no_png)
