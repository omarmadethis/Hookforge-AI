"""D120 Higgsfield credit ledger. Source of truth = learning/spend_ledger.csv (gates.LEDGER, shared with the live
workers; this module only reads it and appends via gates.ledger_add). Caps = what Omar approved:
learning/approvals/<run>.json (credit_cap or video_cap_credits) or config/credit_caps.json for runs approved in chat.
  spent(run_id) / daily(day) -> running totals (PT days)
  status(run_id)  -> spent, cap, remaining, cap_source
  precheck(run_id, planned) -> {ok, warn[]}: warns at >= WARN_AT of cap, refuses (ok False) if spent+planned > cap
     or if no approved cap exists. runner.next_call calls it before every get_cost/submit.
  backfill(day)   -> learning/credit_ledger/<day>.json: every run that spent that day against its cap."""
import os, json, csv, glob, datetime
from collections import defaultdict
from .config import REPO
from . import gates

CAPS_F = os.path.join(REPO, "config", "credit_caps.json")
OUT = os.path.join(REPO, "learning", "credit_ledger")
WARN_AT = 0.8

def _rows():
    if not os.path.exists(gates.LEDGER): return []
    out = []
    for r in csv.DictReader(open(gates.LEDGER)):
        try: r["credits"] = float(r.get("credits") or 0)
        except ValueError: r["credits"] = 0.0
        out.append(r)
    return out

def caps():
    c = {}
    for f in glob.glob(os.path.join(REPO, "learning", "approvals", "*.json")):
        a = json.load(open(f)); rid = a.get("run_id")
        if not rid: continue
        cap = a.get("credit_cap", a.get("video_cap_credits"))
        if cap is not None: c[rid] = dict(cap=float(cap), source=os.path.relpath(f, REPO), approved_by=a.get("approved_by"), note=a.get("cap_note", ""))
    if os.path.exists(CAPS_F):
        cf = json.load(open(CAPS_F))
        for rid, v in cf.get("runs", {}).items(): c.setdefault(rid, dict(v, source="config/credit_caps.json"))
        for gid, g in cf.get("groups", {}).items():          # D121: one cap shared by several runs
            for rid in g["runs"]: c.setdefault(rid, dict(g, group=gid, source=f"config/credit_caps.json groups.{gid}"))
    return c

def _group_spent(c): return round(sum(spent(r) for r in c["runs"]), 2) if c.get("group") else None

def spent(run_id): return round(sum(r["credits"] for r in _rows() if r["run_id"] == run_id), 2)

def daily(day=None):
    day = (day or datetime.date.today()).isoformat(); by = defaultdict(float)
    for r in _rows():
        if r["ts_pt"].startswith(day): by[r["run_id"]] += r["credits"]
    return dict(day=day, total=round(sum(by.values()), 2), by_run={k: round(v, 2) for k, v in by.items()})

def status(run_id):
    c = caps().get(run_id); s = spent(run_id)
    if c and c.get("group"): s = _group_spent(c)                            # the cap is checked against the whole group
    if c and not s and c.get("reported_spent"): s = float(c["reported_spent"])
    return dict(run_id=run_id, spent=s, cap=c["cap"] if c else None, remaining=round(c["cap"] - s, 2) if c else None,
                cap_source=c["source"] if c else "NO APPROVED CAP ON FILE", over=bool(c and s > c["cap"] + 1e-9),
                group=(c or {}).get("group"), closed=(c or {}).get("status") == "closed", ledger_rows=sum(1 for r in _rows() if r["run_id"] == run_id))

def precheck(run_id, planned, cap=None):
    st = status(run_id); cap = cap if cap is not None else st["cap"]; warn = []
    if st.get("closed"): return dict(ok=False, warn=[f"{run_id}: run is closed out - new spend needs a new approval"], **st)
    if cap is None: return dict(ok=False, warn=[f"{run_id}: no approved cap on file - get Omar's approval of the plan and cap"], **st)
    after = st["spent"] + float(planned)
    if after > cap + 1e-9: return dict(ok=False, warn=[f"{run_id}: {st['spent']} spent + {planned} planned = {after} > approved cap {cap} - stop"], **st)
    if after >= WARN_AT * cap: warn.append(f"{run_id}: will reach {after}/{cap} ({after / cap:.0%}) of the approved cap")
    return dict(ok=True, warn=warn, after=after, **dict(st, cap=cap))

def backfill(day=None):
    d = daily(day); cs = caps(); runs = []
    for rid, s_day in d["by_run"].items():
        st = status(rid); st["spent_that_day"] = s_day
        if rid not in cs: st["flag"] = "no approved cap file (approval given in chat?) - add it to config/credit_caps.json"
        elif st["over"]: st["flag"] = "OVER CAP"
        runs.append(st)
    for rid, cv in cs.items():                 # approved runs with no ledger rows that day (reported-only spend)
        if rid not in d["by_run"] and cv.get("approved_pt", "").startswith(d["day"]):
            st = status(rid); st["spent_that_day"] = st["spent"]; st["flag"] = "no spend_ledger rows - spend is Omar-reported/unknown"; runs.append(st)
    rep = dict(d, runs=runs, generated_pt=datetime.datetime.now().isoformat(timespec="seconds"))
    os.makedirs(OUT, exist_ok=True); json.dump(rep, open(os.path.join(OUT, f"{d['day']}.json"), "w"), indent=1); return rep

# ---------------- D126: automatic job logging + reconciliation ----------------
def log_job(run_id, job_id, credits, item="", model="", kind=""):
    """The ONE write path for Higgsfield spend. runner.record_submit calls it for every submit; manual/worker MCP
    submits must call it too (hookforge.credit_ledger.log_job). Dedupes on job id; refuses an empty job id."""
    if not job_id or not str(job_id).strip(): raise ValueError("job id required - every Higgsfield spend is logged by job id")
    if any(str(job_id) in (r.get("job_ids") or "") for r in _rows()): return dict(ok=True, dup=True)
    gates.ledger_add(run_id, job_id, item, credits, model, kind)
    st = status(run_id); warn = []
    if st["cap"] is None: warn.append(f"{run_id}: spend logged with NO approved cap on file")
    elif st["over"]: warn.append(f"{run_id}: now OVER cap ({st['spent']}/{st['cap']})")
    return dict(ok=True, dup=False, warn=warn, **st)

def _pt(ts):
    from zoneinfo import ZoneInfo
    if ts.endswith("Z"): ts = ts[:-1] + "+00:00"
    d = datetime.datetime.fromisoformat(ts)
    return (d if d.tzinfo else d.replace(tzinfo=ZoneInfo("America/Los_Angeles"))).astimezone(ZoneInfo("America/Los_Angeles"))

def reconcile(transactions, day=None, window_min=15):
    """transactions = rows from the read-only Higgsfield `transactions` tool ({display_name, credits, action, created_at}).
    No job ids there, so spends are matched to ledger rows by amount within +-window_min; anything unmatched is
    UNLEDGERED spend (someone submitted outside the runner) -> report it, never guess a run."""
    day = day or datetime.date.today(); led = [dict(r, t=_pt(r["ts_pt"]), used=False) for r in _rows() if r["ts_pt"].startswith(day.isoformat()) and r["credits"] > 0]
    un, matched = [], 0
    for tx in transactions:
        if tx.get("action") != "spend": continue
        t = _pt(tx["created_at"])
        if t.date() != day: continue
        amt = abs(float(tx["credits"]))
        m = next((r for r in led if not r["used"] and abs(r["credits"] - amt) < 0.01 and abs((r["t"] - t).total_seconds()) <= window_min * 60), None)
        if m: m["used"] = True; matched += 1
        else: un.append(dict(when_pt=t.isoformat(timespec="seconds"), what=tx.get("display_name"), credits=amt, created_at=tx["created_at"]))
    return dict(day=day.isoformat(), matched=matched, unledgered=un, unledgered_credits=round(sum(u["credits"] for u in un), 2))
