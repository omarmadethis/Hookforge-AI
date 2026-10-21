"""D91 #1 SCHEDULER: at most 5 generation jobs per PT day, inside the credit caps. QUEUE + DISPATCH CHECK ONLY.
It never calls Higgsfield and never writes approval files. A job is dispatchable only when runner.check_gate passes
(Omar's approval file: approved_by Omar, plan sha256, gen ids, account, credit cap, not expired/consumed) AND the job
fits every cap: per-video cap (config.CREDIT_BUDGET_PER_VIDEO / _VARIANT), the approval's credit_cap, and the daily cap
(DAILY_CREDIT_CAP minus today's learning/spend_ledger.csv spend minus credits reserved by jobs already dispatched today).
Dispatch only hands the run_id to runner.start_run / next_call, which re-check the gate on every paid call.
  scheduler.enqueue(run_id, plan_path, product, kind="video")   -> queued for the next day with a free slot
  scheduler.dispatchable(date=None)   -> [(job, ok, reasons)] for that day; ok jobs are marked 'dispatched' (reserve credits)
  scheduler.mark(run_id, status)      -> done | failed | cancelled (frees nothing already spent)"""
import os, json, csv, datetime
from zoneinfo import ZoneInfo
from .config import REPO, CREDIT_BUDGET_PER_VIDEO, CREDIT_BUDGET_VARIANT
from . import runner

PT = ZoneInfo("America/Los_Angeles")
MAX_PER_DAY = 5
DAILY_CREDIT_CAP = 5 * CREDIT_BUDGET_PER_VIDEO          # 875; Omar can lower it, never raised by the engine
DIR = os.path.join(REPO, "learning", "schedule")
LEDGER = os.path.join(REPO, "learning", "spend_ledger.csv")
today = lambda: datetime.datetime.now(PT).date()

def _p(d): return os.path.join(DIR, f"{d.isoformat()}.json")
def _load(d): return json.load(open(_p(d))) if os.path.exists(_p(d)) else []
def _save(d, jobs): os.makedirs(DIR, exist_ok=True); json.dump(jobs, open(_p(d), "w"), indent=1, ensure_ascii=False)

def plan_cost(plan): return sum(c["expected_credits"] for c in runner.build_calls(plan))

def spent_on(d, ledger=None):
    ledger = ledger or LEDGER; tot = 0.0
    if not os.path.exists(ledger): return 0.0
    for r in csv.DictReader(open(ledger)):
        if (r.get("ts_pt") or "")[:10] == d.isoformat():
            try: tot += float(r.get("credits") or 0)
            except ValueError: pass
    return tot

def enqueue(run_id, plan_path, product, kind="video", start=None, horizon_days=14):
    plan = json.load(open(plan_path)); cost = plan_cost(plan)
    cap = CREDIT_BUDGET_VARIANT if kind == "variant" else CREDIT_BUDGET_PER_VIDEO
    if cost > cap: raise ValueError(f"{run_id}: plan costs {cost} > per-{kind} cap {cap}; rework the plan")
    d = start or today()
    for i in range(horizon_days):
        day = d + datetime.timedelta(days=i); jobs = _load(day)
        if any(j["run_id"] == run_id for j in jobs): return dict(day=day.isoformat(), dup=True)
        live = [j for j in jobs if j["status"] != "cancelled"]
        if len(live) < MAX_PER_DAY and sum(j["est_credits"] for j in live) + cost <= DAILY_CREDIT_CAP:
            jobs.append(dict(run_id=run_id, plan_path=os.path.abspath(plan_path), product=product, kind=kind, est_credits=cost,
                             status="queued", queued_pt=datetime.datetime.now(PT).isoformat(timespec="seconds")))
            _save(day, jobs); return dict(day=day.isoformat(), slot=len(live) + 1, est_credits=cost)
    raise ValueError("no free slot in the horizon")

def dispatchable(d=None, ledger=None, live=True):
    d = d or today(); jobs = _load(d); out = []
    reserved = sum(j["est_credits"] for j in jobs if j["status"] == "dispatched")
    base = spent_on(d, ledger)
    n_active = sum(j["status"] in ("dispatched", "done", "failed") for j in jobs)
    for j in jobs:
        if j["status"] != "queued": continue
        why = []
        if n_active >= MAX_PER_DAY: why.append(f"daily job limit {MAX_PER_DAY} reached")
        if base + reserved + j["est_credits"] > DAILY_CREDIT_CAP: why.append(f"daily credit cap {DAILY_CREDIT_CAP}: spent {base} + reserved {reserved} + {j['est_credits']}")
        plan = json.load(open(j["plan_path"]))
        ok, g = runner.check_gate(plan, j["run_id"], live=live)
        if not ok: why += ["NO SPEND: " + x for x in g]
        if not why:
            j["status"] = "dispatched"; j["dispatched_pt"] = datetime.datetime.now(PT).isoformat(timespec="seconds")
            reserved += j["est_credits"]; n_active += 1
        out.append((j, not why, why))
    _save(d, jobs); return out

def mark(run_id, status, d=None):
    assert status in ("done", "failed", "cancelled", "queued")
    for day in ([d] if d else [today() + datetime.timedelta(days=i) for i in range(-3, 15)]):
        jobs = _load(day)
        for j in jobs:
            if j["run_id"] == run_id: j["status"] = status; _save(day, jobs); return j
    raise KeyError(run_id)
