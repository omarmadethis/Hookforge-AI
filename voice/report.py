"""Render voice/INSIGHTS.md and voice/voice_rules.csv.

Data sections come from voice_stats.json (pipeline.py) + support_themes.csv (gmail_themes.py).
Recommendations are curated in voice/recommendations.json (human/AI-editable; every item cites the counts it rests on).
  python3 voice/report.py
"""
import csv, json, os, collections
HERE = os.path.dirname(os.path.abspath(__file__))
NAMES = {"grinch_robe": "Grinch robe (HeatedJammies / MerryJammies)", "grinchmelt_mug": "GrinchMelt mug", "merryfire": "MerryFire tabletop fire pit",
         "brickhood_mask": "Brick Hood ski mask", "merryglow_lights": "MerryGlow tree lights (+ Christmas projector competitors)",
         "jollyglow_curtain": "JollyGlow curtain / window lights", "purrventure_carrier": "PurrVenture cat carrier"}
LABEL = {"q_where_buy": "Where to buy / link / name", "q_price": "Price", "q_shipping": "Shipping / arrive by Christmas", "q_sizing": "Size / fit",
         "q_how_it_works": "How it works (power, battery, app, noise)", "q_material_safety": "Material / safety", "q_other": "Other question",
         "objection": "Objection", "skeptic": "Disbelief ('no way that works')", "ai_callout": "AI call-out", "too_early": "'Too early for Christmas'",
         "desire": "Purchase intent / desire", "tag_friend": "Tag-a-friend", "complaint": "Complaint (owners)", "comparison": "Comparison",
         "humor": "Humor", "praise": "Praise", "emotional": "Emotional story (not quoted)", "other": "Uncoded"}

def q(t): return t.replace("|", "/").replace("\n", " ")

def main():
    st = json.load(open(os.path.join(HERE, "voice_stats.json")))
    recs = json.load(open(os.path.join(HERE, "recommendations.json")))
    sup = list(csv.DictReader(open(os.path.join(HERE, "support_themes.csv")))) if os.path.exists(os.path.join(HERE, "support_themes.csv")) else []
    P = st["products"]; L = []
    tot = sum(s["n_comments"] for s in P.values()); nv = sum(s["n_videos"] for s in P.values())
    L += [f"# Hookforge customer-voice INSIGHTS", f"Generated {st['generated']} by `voice/report.py` from `voice/comments.csv` "
          f"({tot:,} de-identified comments on {nv} videos) + `voice/support_themes.csv` (Gmail support inbox, aggregated). "
          "Counts = comments carrying the code (multi-label); 'liked share' weights each comment by 1+ln(1+likes). Recommendations live in "
          "`voice/recommendations.json` and feed `voice/voice_rules.csv`.", ""]
    L += ["## 0. Critical alerts (read first)"] + [f"- **{a['title']}** {a['body']} _Evidence: {a['evidence']}_" for a in recs.get("alerts", [])] + [""]
    L += ["## 1. Cross-product findings"] + [f"- {x}" for x in recs.get("cross_product", [])] + [""]
    L += ["## 2. Does comment mix track views? (`voice/engagement_correlation.csv`)", "| dataset | x | rho (Spearman vs log10 views) | n |", "|---|---|---|---|"]
    for c in st["correlations"]: L.append(f"| {c['dataset']} | {c['x']} | {c['spearman_rho']} | {c['n']} |")
    L += ["", recs.get("correlation_read", ""), ""]
    order = ["grinch_robe", "merryfire", "brickhood_mask", "merryglow_lights", "jollyglow_curtain", "grinchmelt_mug", "purrventure_carrier"]
    for i, p in enumerate(order, 3):
        s = P.get(p); r = recs["products"].get(p, {})
        L += [f"## {i}. {NAMES.get(p, p)}"]
        if s:
            L += [f"Base: {s['n_comments']:,} comments on {s['n_videos']} videos; sources {s['sources']}; audience {s['audience']}.", "",
                  "| code | n | share | liked share | videos | top phrases |", "|---|---|---|---|---|---|"]
            for code, v in sorted(s["codes"].items(), key=lambda kv: -kv[1]["n"]):
                L.append(f"| {LABEL.get(code, code)} | {v['n']} | {v['share']:.1%} | {v['like_weighted_share']:.1%} | {v['n_videos']} | "
                         + q(", ".join(f"{g} ({n})" for g, n in v["subtopics"] if "friend" not in g)[:200]) + " |")
            for title, codes in [("Top questions", [c for c in s["codes"] if c.startswith("q_")]), ("Objections, disbelief, AI call-outs", ["objection", "skeptic", "ai_callout", "too_early", "complaint"]),
                                 ("Purchase-intent language", ["desire"])]:
                codes = sorted([c for c in codes if c in s["codes"]], key=lambda c: -s["codes"][c]["n"])
                if not codes: continue
                L += ["", f"**{title}**"]
                for c in codes[:5]:
                    exs = [e for e in s["codes"][c]["examples"] if len(e["text"].replace("@friend", "").strip(" .!")) > 12][:3]
                    ex = " · ".join(f"\"{q(e['text'])}\" ({e['likes']} likes)" for e in exs)
                    L.append(f"- {LABEL.get(c, c)}: {s['codes'][c]['n']} ({s['codes'][c]['share']:.1%}). {ex}")
        else:
            L.append("No public comment data yet (see browser_queue.csv).")
        sp = [x for x in sup if x["product_key"] in ((p, "merryjammies_store_unspecified") if p == "grinch_robe" else (p,))]
        if sp:
            L += ["", "**Our own customers (support inbox, read-only, aggregated)**", "| theme | threads | share | first-last | example |", "|---|---|---|---|---|"]
            hdr = len(L) - 3
            agg = collections.defaultdict(lambda: [0, "9", "0", ""])
            for x in sp:
                a = agg[x["theme"]]; a[0] += int(x["n_threads"]); a[1] = min(a[1], x["first_seen"]); a[2] = max(a[2], x["last_seen"]); a[3] = a[3] or x["example_1"]
            # prefer an example whose PRIMARY theme is this theme (private/voice/support_rows.csv holds only short name-checked quotes)
            prow = os.path.join(HERE, "..", "private", "voice", "support_rows.csv")
            if os.path.exists(prow):
                keys = {x["product_key"] for x in sp}
                prs = [x for x in csv.DictReader(open(prow)) if x["product_key"] in keys]
                for x in sorted(prs, key=lambda x: -len(x["text"])):
                    if x["theme"] in agg and len(x["text"]) > 25 and not agg[x["theme"]][3].startswith("*"):
                        agg[x["theme"]][3] = "*" + x["text"]
                n_thr = len(prs)
            else: n_thr = 0
            L[hdr] = f"**Our own customers (support inbox, read-only, aggregated; {n_thr} customer threads, multi-label)**"
            for th, a in sorted(agg.items(), key=lambda kv: -kv[1][0]):
                share = f"{a[0] / n_thr:.0%}" if n_thr else ""
                L.append(f"| {th} | {a[0]} | {share} | {a[1]}..{a[2]} | {q(a[3].lstrip('*'))} |")
        for sec, key in [("Competitor weaknesses / gaps we can beat", "gaps"), ("Recommended VIDEO moves", "video"), ("Recommended WEBSITE / product-page fixes", "site")]:
            items = r.get(key, [])
            if items:
                L += ["", f"**{sec}**"] + [f"- {it['text']} _({it.get('evidence', '')})_" for it in items]
        L.append("")
    L += ["## Method and limits"] + [f"- {x}" for x in recs.get("limits", [])]
    open(os.path.join(HERE, "INSIGHTS.md"), "w").write("\n".join(L) + "\n")
    # rules in learning/rules_core.csv format (+ 3 machine columns)
    cols = ["id", "rule", "verbatim_quote", "date_PT", "source_session_or_file", "scope", "evolution_or_superseded_by", "playbook_conflict_or_note",
            "status", "hookforge_resolution", "freshness_scope", "rule_type", "engine_slot", "evidence_n",
            "rule_id", "product", "type", "text", "evidence"]   # last 5 = engine/hookforge/plugins.voice() schema
    rows = []
    for r_ in recs.get("rules", []):
        rows.append({"id": r_["id"], "rule": r_["rule"], "verbatim_quote": r_.get("quote", ""), "date_PT": st["generated"][:16], "source_session_or_file": "voice/comments.csv; voice/support_themes.csv",
                     "scope": r_["scope"], "evolution_or_superseded_by": "", "playbook_conflict_or_note": r_.get("note", ""), "status": r_.get("status", "proposed"),
                     "hookforge_resolution": r_.get("resolution", ""), "freshness_scope": "customer-voice (product truth; own+competitor comments, re-run weekly; no recency decay)",
                     "rule_type": r_["rule_type"], "engine_slot": r_["engine_slot"], "evidence_n": r_.get("evidence_n", ""),
                     "rule_id": r_["id"], "product": r_["scope"] if r_["scope"] in NAMES else "ALL",
                     "type": r_.get("plugin_type") or {"hook_line": "hook", "onscreen_text": "objection", "shot": "objection", "block": "avoid", "qa_check": "avoid", "site_fix": "site"}.get(r_["rule_type"], "objection"),
                     "text": r_["rule"], "evidence": r_.get("evidence_n", "")})
    with open(os.path.join(HERE, "voice_rules.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    print("INSIGHTS.md lines", len(L), "| rules", len(rows))

if __name__ == "__main__":
    main()
