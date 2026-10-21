"""Engine panels for the dashboard (Phase E, 2026-10-18 PT): arm posteriors + tomorrow's schedule, generation failure memory
(D42), views-model validation (advisory, D35), posting windows (D36), dry-run QA summary. Each panel reads files only."""
import os, json, glob, html
import pandas as pd

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
def _t(df, max_rows=40):
    if df is None or not len(df): return "<p class='note'>no data yet</p>"
    return df.head(max_rows).to_html(index=False, escape=True, classes="tbl", border=0, na_rep="")

def _pub(df, public):
    """Public build: product -> category label, no hook text / brief / prompt evidence (Omar 10:35 PM PT)."""
    if not public or df is None or not len(df): return df
    import public_scrub as PS
    pl = PS.product_labels(); df = df.copy()
    if "product" in df: df["product"] = [pl.get(str(x).lower(), "Other product") for x in df["product"]]
    if "hook" in df: df["hook"] = [f"{f} · {t}" for f, t in zip(df.get("format", ""), df.get("hook_type", df.get("option", "")))]
    return df.drop(columns=[c for c in ("brief", "hook_type", "fix", "evidence", "block") if c in df])

def sections(public=False):
    out = []
    # 1. arms + schedule
    p = os.path.join(REPO, "learning", "arms.csv")
    if os.path.exists(p):
        a = pd.read_csv(p).sort_values(["product", "mean"], ascending=[True, False])
        top = a.groupby("product").head(6)[["product", "format", "option", "verdict", "n", "hits", "mean"]]
        days = sorted(glob.glob(os.path.join(REPO, "out", "daily", "*", "*", "day.json")))
        sched = []
        for dj in days[-8:]:
            d = json.load(open(dj))
            for i, s in enumerate(d["slots"]):
                sched.append(dict(date=d["date"], product=d["product"], n=i + 1, slot=s["slot"]["slot"], page=("" if public else s.get("page", "")),
                                  window_pt=s["slot"]["window_pt"], format=s.get("format"), option=s.get("option") or "", hook=s.get("hook", ""), hook_type=s.get("hook_family") or s.get("option") or "proven-own",
                                  credits=s.get("credits"), qa="; ".join(s.get("qa") or []) or "ok", lint="ok" if s.get("lint_ok") else "FIX"))
        out.append(("engine_arms", "Engine: format arms and next-day schedule",
                    "<h4>Top arms per product (Beta posterior mean of a 50K+ hit; priors from fit, likelihood = own hits)</h4>" + _t(_pub(top, public), 60)
                    + "<h4>Next-day packages (planned, NOT generated; learning/update.py day &lt;product&gt;)</h4>" + _t(_pub(pd.DataFrame(sched), public), 60),
                    "Core slots sample STRONG/OK arms (Thompson); 20% innovation slots sample WEAK/untested arms and innovation hook options (e.g. covered_glow)."))
    # 2. failure memory
    d = os.path.join(REPO, "learning", "gen_failures")
    if os.path.exists(os.path.join(d, "rules.csv")):
        fr = pd.read_csv(os.path.join(d, "failure_rate.csv")); ru = pd.read_csv(os.path.join(d, "rules.csv")).fillna("")
        ru = ru[ru.status != "candidate"][["rule_id", "family", "block", "status", "fix", "evidence"]]
        led = pd.read_csv(os.path.join(d, "ledger.csv"), usecols=["outcome", "family"])
        out.append(("engine_failures", "Engine: generation failure memory (D42)",
                    f"<p>{len(led)} attempts in the ledger; outcomes: {html.escape(json.dumps(led.outcome.value_counts().to_dict()))}</p>"
                    + "<h4>Failure rate by model family</h4>" + _t(fr) + "<h4>Linted rules (promoted = FIX before generation; hypothesis = INFO)</h4>" + _t(_pub(ru, public), 30),
                    "Backfilled from the Higgsfield generation export; live attempts and certain misgens append via gen_failures.log_attempt / qa.reroll_decision. Candidates (1-pair auto words) are stored but not linted."))
    # 3. model validation
    p = os.path.join(REPO, "engine", "backtest", "data", "validation.json")
    if os.path.exists(p):
        v = json.load(open(p)); rows = []
        for split in ("loo", "holdout"):
            for m, r in (v.get(split) or {}).items():
                if isinstance(r, dict): rows.append(dict(split=split, model=m, **{k: r.get(k) for k in ("n", "hits", "spearman", "auc_hit", "within_page_auc_mean", "mae_log10")}))
        out.append(("engine_model", "Engine: views-model validation (ADVISORY, D35)", _t(pd.DataFrame(rows)),
                    f"Retrained {v.get('asof', '')}. The model is weak (within-page AUC ~0.5); the backtest gate uses rule checks, the model is shown as information only."))
    # 4. posting windows
    p = os.path.join(REPO, "learning", "posting_windows.json")
    if os.path.exists(p):
        pw = json.load(open(p)); rows = [dict(page=("page" if public else k), exploit=", ".join(v.get("exploit", [])), explore=", ".join(v.get("explore", [])), explore_share=v.get("explore_share"))
                                          for k, v in pw.items() if isinstance(v, dict)]
        out.append(("engine_windows", "Engine: posting windows (PT, D36)", _t(pd.DataFrame(rows)), "Night/weekend effects are supported hypotheses after Holm correction; 20% of slots explore other windows."))
    # 5. dry runs
    rows = []
    for pj in sorted(glob.glob(os.path.join(REPO, "out", "dryrun", "*", "plan.json"))):
        pl = json.load(open(pj)); pl = pl.get("plan", pl); mq = os.path.join(os.path.dirname(pj), "media_qa.json"); m = json.load(open(mq)) if os.path.exists(mq) else {}
        rows.append(dict(brief=pl["brief"]["brief"], format=pl["brief"]["format"], option=(pl.get("hook_option") or {}).get("option") or "", slot=pl["brief"]["slot"],
                         product=pl["brief"].get("product_key", ""), hook=pl["hook"]["text"], hook_type=((pl.get("hook_option") or {}).get("option") or ("hook-type " + str(pl["hook"].get("tag") or "?"))), credits=pl["credits"]["total"], lint="ok" if (pl.get("preflight_lint") or {}).get("preflight", {}).get("ok") else "FIX",
                         export_provenance=("clean" if (m.get("export_clean_test") or {}).get("provenance") is not None and not any(m["export_clean_test"]["provenance"].values()) else "n/a")))
    out += publishing_panel(public)
    out.append(("engine_dryruns", "Engine: dry-run packages (out/dryrun)", _t(_pub(pd.DataFrame(rows), public)), "Plans, prompts, credit estimates, animatics and CapCut drafts. No generation."))
    return out


def publishing_panel(public=False):
    """D103: per-page Buffer queue, approvals pending, caption swaps pending, routing map. Reads files only
    (config/buffer_routing.json, learning/publish_queue/*.json, learning/publish_queue/caption_swaps/*.json)."""
    rc = json.load(open(os.path.join(REPO, "config", "buffer_routing.json")))
    qd = os.path.join(REPO, "learning", "publish_queue"); sd = os.path.join(qd, "caption_swaps")
    items = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(qd, "*.json")))]
    swaps = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(sd, "*.json")))]
    ch2page = {p["channel"]: k for k, p in rc["pages"].items()}
    act = ("AWAITING_OMAR_APPROVAL", "APPROVED", "BUFFER_DRAFT_CREATED")
    rows = []
    for k, p in rc["pages"].items():
        a = rc["accounts"][p["account"]]; mine = [i for i in items if i.get("payload", {}).get("channelId") == p["channel"]]
        used = sum(1 for i in items if i.get("status") in act and ch2page.get(i.get("payload", {}).get("channelId")) in [kk for kk, pp in rc["pages"].items() if pp["account"] == p["account"]])
        rows.append(dict(page=p["name"], service=p["service"], account=p["account"], status="LOCKED: " + p.get("lock_reason", "") if p.get("locked") else ("not connected" if not a["connected"] else "active"),
                         products=", ".join(pr for pr, ks in rc["products"].items() if k in ks), awaiting_approval=sum(i["status"] == "AWAITING_OMAR_APPROVAL" for i in mine),
                         approved=sum(i["status"] == "APPROVED" for i in mine), buffer_drafts=sum(i["status"] == "BUFFER_DRAFT_CREATED" for i in mine),
                         account_slots_left=f"{max(0, a['max_scheduled'] - used)}/{a['max_scheduled']}",
                         next_slot_pt=min([i.get("suggested_slot_pt") or "" for i in mine if i["status"] in act] or [""]),
                         **({} if public else dict(namespace=a["namespace"] or "", channel=p["channel"]))))
    for acc, a in rc["accounts"].items():
        if not any(p["account"] == acc for p in rc["pages"].values()):
            rows.append(dict(page="(reserved slot)", service="", account=acc, status="not connected" if not a["connected"] else "no pages", products=""))
    tgt = rc["target"]; have = {s: sum(p["service"] == s for p in rc["pages"].values()) for s in tgt}
    pend = pd.DataFrame([dict(id=i["id"], page=i.get("page"), product=i.get("product"), created=i.get("created"), slot_pt=i.get("suggested_slot_pt"),
                              needs=", ".join(i.get("needs") or []), **({} if public else dict(caption=(i.get("caption") or "")[:90])))
                         for i in items if i.get("status") == "AWAITING_OMAR_APPROVAL"])
    sw = pd.DataFrame([dict(id=x["id"], page=x.get("page"), product=x.get("product"), reason=x.get("reason"), status=x.get("status"),
                            blocked=x.get("blocked") or "", **({} if public else dict(new_caption=(x.get("new_caption") or "")[:90])))
                       for x in swaps if x.get("status") in ("AWAITING_OMAR_APPROVAL", "APPROVED")])
    routes = pd.DataFrame([dict(product=pr, pages=", ".join(rc["pages"][k]["name"] + (" (locked)" if rc["pages"][k].get("locked") else "") for k in ks) or "(no page yet)") for pr, ks in rc["products"].items()])
    body = (f"<p class='note'>Pages mapped: FB {have.get('facebook', 0)}/{tgt.get('facebook')} · IG {have.get('instagram', 0)}/{tgt.get('instagram')}. "
            "Every item is a Buffer DRAFT that waits for Omar's approval; nothing here posts.</p>"
            "<h4>Per-page queue</h4>" + _t(pd.DataFrame(rows)) + f"<h4>Approvals pending ({len(pend)})</h4>" + _t(pend) +
            f"<h4>Caption swaps pending ({len(sw)})</h4>" + _t(sw) + "<h4>Routing map (product → pages)</h4>" + _t(routes))
    return [("engine_publishing", "Publishing: Buffer queue, approvals, caption swaps, routing (D94-D103)", body,
             "Reads config/buffer_routing.json and learning/publish_queue. Free Buffer plan: 10 scheduled posts per account (drafts counted).")]

if __name__ == "__main__":   # standalone: python3 analytics/engine_panels.py -> analytics/publishing_panel.html
    sid, title, body, note = publishing_panel()[0]
    open(os.path.join(REPO, "analytics", "publishing_panel.html"), "w").write(
        f"<html><head><meta charset='utf-8'><title>{title}</title><style>body{{font-family:-apple-system,sans-serif;margin:24px}}"
        f".tbl{{border-collapse:collapse;font-size:13px}}.tbl td,.tbl th{{border:1px solid #ddd;padding:4px 8px}}.note{{color:#555}}</style></head>"
        f"<body><h2>{title}</h2>{body}<p class='note'>{note}</p></body></html>")
    print("analytics/publishing_panel.html")
