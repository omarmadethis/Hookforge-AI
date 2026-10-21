"""D127 weekly content calendar (DRAFTS ONLY - nothing is scheduled or sent to Buffer).
week(start) -> learning/calendar/<start>.json + analytics/content_calendar.html: one slot per (day, page) with product,
posting window (posting_windows exploit hours PT), the queued concept id and a draft caption.
Rules: active products only (D117); per-page cadence CADENCE (posts/week); a shared page never carries the same product
on back-to-back days and rotates by weight; a product on two pages is never posted to both on the same day;
trumpglow weight ramps toward the Nov 3 2026 midterms (and stops after); each Buffer account stays <= its
max_scheduled (free plan) for the week - lowest-weight slots are dropped and listed."""
import os, json, datetime, html
from .config import REPO
from . import routing, products, approval_queue

CADENCE = {"jollyglow_fb": 4, "trumpglow_fb": 6, "patriotsglow_fb": 4, "purrventures_fb": 2, "purrventures2_fb": 3}   # D131: robe family retired, its slots redistributed
MIDTERMS = datetime.date(2026, 11, 3)
BASE_W = {"grinch_robe": 1.0, "heatjams": 1.0, "cozyjams": 0.9, "jollyglow_curtain": 1.0, "trumpglow": 1.0, "purrventure_carrier": 1.0}

def weight(product, day):
    w = BASE_W.get(product, 1.0)
    if product == "trumpglow":
        d = (MIDTERMS - day).days
        w *= 0.6 if d < 0 else 1.0 + max(0, 14 - d) / 7          # 1.0 two weeks out -> 3.0 on election day; drops after
    return round(w, 2)

def _days_for(n, start):
    """spread n posts over 7 days as evenly as possible"""
    return sorted({start + datetime.timedelta(days=round(i * 7 / n)) for i in range(n)}) if n else []

def week(start=None, write=True):
    start = start or datetime.date.today() + datetime.timedelta(days=1)
    c = routing.cfg(); act = set(products.active()); pages = {}
    for pk, keys in c["products"].items():
        if pk not in act: continue
        for k in keys: pages.setdefault(k, []).append(pk)
    queue = {i["product"]: i for i in approval_queue.pending() if i.get("status") == "AWAITING_OMAR_APPROVAL"}
    slots, last_on_page, product_day = [], {}, {}
    for pg, prods in sorted(pages.items()):
        p = c["pages"][pg]; n = CADENCE.get(pg, 3)
        if "trumpglow" in prods: n = min(7, n + (1 if (MIDTERMS - start).days <= 14 else 0))
        for day in _days_for(n, start):
            cands = [x for x in prods if not (len(prods) > 1 and last_on_page.get(pg) == (x, day - datetime.timedelta(days=1)))]
            def clash(x): return any(t["day"] == day.isoformat() and t["product"] == x and t["page"] != pg for t in slots) and not (x == "trumpglow" and (MIDTERMS - day).days <= 14)
            if len(prods) == 1 and clash(prods[0]):                   # same product on its other page that day -> shift a day
                day2 = next((day + datetime.timedelta(days=k) for k in (1, -1, 2) if start <= day + datetime.timedelta(days=k) < start + datetime.timedelta(days=7)
                             and not any(t["day"] == (day + datetime.timedelta(days=k)).isoformat() and t["page"] == pg for t in slots)
                             and not any(t["day"] == (day + datetime.timedelta(days=k)).isoformat() and t["product"] == prods[0] and t["page"] != pg for t in slots)), None)
                if day2 is None: continue
                day = day2
            cands = [x for x in cands if not clash(x)]
            if not cands: continue
            used = {x: sum(1 for s in slots if s["page"] == pg and s["product"] == x) for x in cands}
            pick = max(cands, key=lambda x: weight(x, day) / (1 + used[x]))
            hours = routing._windows(p.get("windows", "_default"))
            q = queue.get(pick)
            slots.append(dict(day=day.isoformat(), weekday=day.strftime("%a"), page=pg, account=p["account"], service=p["service"], product=pick,
                              window_pt=hours[0] if hours else "", weight=weight(pick, day), concept=q["id"] if q else None,
                              status="DRAFT - needs a rendered, Omar-approved video", midterms_days=(MIDTERMS - day).days if pick == "trumpglow" else None))
            last_on_page[pg] = (pick, day)
    dropped = []
    for acct, a in c["accounts"].items():
        mine = [s for s in slots if s["account"] == acct]
        if len(mine) > a["max_scheduled"]:
            while len(mine) > a["max_scheduled"]:                      # fairness: trim the product with the most slots (per weight) first
                cnt = {}
                for t in mine: cnt[t["product"]] = cnt.get(t["product"], 0) + 1
                pk = max(cnt, key=lambda x: cnt[x] / weight(x, start + datetime.timedelta(days=6)))
                t = min((t for t in mine if t["product"] == pk), key=lambda t: t["weight"])
                mine.remove(t); slots.remove(t); dropped.append(dict(t, why=f"{acct} free plan max {a['max_scheduled']} scheduled"))
    slots.sort(key=lambda s: (s["day"], s["page"]))
    from .e2e_dryrun import caption_for
    for s in slots:
        q = queue.get(s["product"])
        if q:
            try: s["caption_draft"] = caption_for(s["product"], q["plan"], s["service"], s["page"])["text"]
            except Exception as e: s["caption_draft"] = f"(caption error {type(e).__name__})"
    out = dict(start=start.isoformat(), end=(start + datetime.timedelta(days=6)).isoformat(), slots=slots, dropped=dropped,
               per_product={pk: sum(1 for s in slots if s["product"] == pk) for pk in sorted(act)}, drafts_only=True)
    from . import render_queue                                   # D130: every slot carries its video binding
    rq = render_queue.build(out, write=write); out["slots"] = rq["slots"]; out["render_summary"] = rq["summary"]
    for x in out["slots"]: x["status"] = "SCHEDULABLE (approved video bound)" if x["render_status"] == "READY" else f"DRAFT - {x['render_status']}"
    if write:
        d = os.path.join(REPO, "learning", "calendar"); os.makedirs(d, exist_ok=True); json.dump(out, open(os.path.join(d, f"{start}.json"), "w"), indent=1, ensure_ascii=False)
        rows = "".join(f"<tr><td>{s['weekday']} {s['day'][5:]}</td><td>{s['page']}</td><td><b>{s['product']}</b></td><td>{s['window_pt']} PT</td><td>{s['concept'] or '-'}<br><small>{s.get('render_status','')}</small></td><td>{html.escape(s.get('caption_draft') or '')}</td></tr>" for s in out["slots"])
        open(os.path.join(REPO, "analytics", "content_calendar.html"), "w").write(
            f"<!doctype html><meta charset=utf-8><title>Calendar {start}</title><style>body{{font:14px system-ui;margin:24px}}td,th{{border-bottom:1px solid #ddd;padding:6px;text-align:left}}</style>"
            f"<h1>Content calendar {start} - {out['end']} (drafts only)</h1><p>{json.dumps(out['per_product'])}</p><table><tr><th>Day</th><th>Page</th><th>Product</th><th>Window</th><th>Concept</th><th>Caption draft</th></tr>{rows}</table>"
            + (f"<p>Dropped (account caps): {len(dropped)}</p>" if dropped else ""))
    return out
