"""D69 ONE-COMMAND ORDER -> PACKAGE runner.  python3 -m hookforge.order "<one-line order>" [--run-id ID]
Chains research (POC library lookup) -> plan (planner, G1-G7) -> quote (per output, G4/G5) -> STOPS at the approval gates:
  STOP-1 plan+start-frame quote needs Omar's OK (approval file learning/approvals/<run_id>.json, written by parent only)
  STOP-2 start frames need Omar's OK (learning/approvals/<run_id>_frames.json)  -> G8
  STOP-3 video quote OK -> live runner (runner.next_call); final export -> songlay + G1 final onset check.
Never submits anything, never spends: it writes out/orders/<run_id>/ (plan.json, quote.json, gates.json, research.json, ORDER.md)."""
import argparse, datetime, json, os, re
from . import planner, gates, poc_library as L
REPO = gates.REPO; PT = gates.PT
def research(plan):
    hk = (plan.get("hook") or {}).get("text", ""); pk = plan.get("product_key") or (plan.get("product") or {}).get("key") or ""
    return dict(hook_citation=L.cite(hk), proven_formats=L.search(kind="format", min_views=50_000, limit=8),
                top_hooks=L.search(kind="hook", min_views=50_000, limit=10), product_hits=L.search(str(pk).split("_")[0], min_views=10_000, limit=10))
def stage_of(run_id, plan):
    a = os.path.exists(os.path.join(gates.APPROVALS, f"{run_id}.json")); f = os.path.exists(gates.frames_path(run_id))
    if not plan["gates"]["ok"]: return "BLOCKED_AT_GATES"
    if not a: return "STOP-1 awaiting Omar: approve plan + start-frame spend"
    if not f: return "STOP-2 awaiting Omar: approve start frames (contact sheet)"
    return "READY-VIDEO: runner.check_gate(live=True) -> next_call"
def run(order, run_id=None, write=True):
    run_id = run_id or re.sub(r"\W+", "_", order.lower()).strip("_")[:40] + "_" + datetime.datetime.now(PT).strftime("%m%d%H%M")
    p = planner.plan(order); rs = research(p); q = p.get("quote") or gates.quote(p)
    st = stage_of(run_id, p)
    res = dict(run_id=run_id, order=order, stage=st, ok=p["gates"]["ok"], quote=q, blocks=p["gates"]["blocks"], warns=p["gates"]["warns"])
    if write:
        d = os.path.join(REPO, "out", "orders", run_id); os.makedirs(d, exist_ok=True)
        for n, o in (("plan", p), ("quote", q), ("gates", p["gates"]), ("research", rs)): json.dump(o, open(os.path.join(d, f"{n}.json"), "w"), indent=1, ensure_ascii=False, default=str)
        md = [f"# Order {run_id}", f"Order: {order}", f"Stage: **{st}**", f"Hook: {(p.get('hook') or {}).get('text')}",
              f"Quote: {q['total']} credits (stills {q['stills']} per image, video {q['video']})", "## BLOCKS"] + [f"- {r['gate']}: {r['msg']}" for r in res["blocks"]] \
             + ["## WARN (weak proof / exceptions)"] + [f"- {r['gate']}: {r['msg']}" for r in res["warns"]]
        open(os.path.join(d, "ORDER.md"), "w").write("\n".join(md) + "\n"); res["dir"] = d
    return res
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("order"); ap.add_argument("--run-id"); a = ap.parse_args()
    r = run(a.order, a.run_id); print(json.dumps({k: r[k] for k in ("run_id", "stage", "ok", "dir")}, indent=1))
    print("quote", r["quote"]["total"]); [print("BLOCK", b["gate"], b["msg"]) for b in r["blocks"]]; [print("WARN ", w["gate"], w["msg"][:120]) for w in r["warns"]]
