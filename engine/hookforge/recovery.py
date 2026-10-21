"""D91 #2 RECOVERY for live runs (out/live/<run_id>/run.json). Never resubmits a job that may still be running.
  scan(run_id)      -> per-step state: ok | pending | STUCK (submitted, no result after TIMEOUT_S[kind]) | failed_retryable | failed_final
  stuck -> the action is to POLL the existing job id (Higgsfield jobs_wait / job_status) and record_result; NEVER resubmit
           (a transport timeout does not mean the job failed; resubmitting double-spends).
  retry(run_id, step) -> inserts ONE new step <step>_rN at the cursor for a result-failed step, only if the cause is retryable,
           retries < MAX_RETRIES, and the gate + credit cap still hold (runner.next_call re-checks both before any paid call).
           Refunded failures (record_refund) give the credits back to the run budget.
  resume(run_id)    -> repairs the cursor (first step without a job id), then returns runner.next_call(run_id)."""
import json, datetime
from . import runner
from .config import LIVE

TIMEOUT_S = {"still": 10 * 60, "video": 45 * 60}
MAX_RETRIES = 2
RETRYABLE = {"failed", "timeout_server", "server_error", "nsfw_false_flag"}   # ip/param/credits need a human/prompt fix
FINAL = {"ip", "param", "credits", "nsfw"}

def _ts(s): return datetime.datetime.fromisoformat(s)

def scan(run_id, now=None):
    st = runner._load(run_id); now = now or runner.now(); res = {}
    last = {}
    for e in st["log"]:
        if e["event"] in ("submitted", "result"): last.setdefault(e["step"], []).append(e)
    for c in st["calls"]:
        s = c["step"]; ev = last.get(s, []); r = [e for e in ev if e["event"] == "result"]
        if r:
            o = r[-1]["outcome"]
            res[s] = "ok" if o == "ok" else ("failed_final" if o in FINAL else "failed_retryable")
        elif s in st["jobs"]:
            sub = next(e for e in ev if e["event"] == "submitted")
            age = (now - _ts(sub["ts"])).total_seconds()
            res[s] = "STUCK" if age > TIMEOUT_S.get(c.get("kind", "video"), 2700) else "pending"
        else: res[s] = "not_submitted"
    actions = []
    for s, v in res.items():
        if v == "STUCK": actions.append(dict(step=s, action="poll_existing_job", job_id=st["jobs"][s], note="never resubmit"))
        if v == "failed_retryable": actions.append(dict(step=s, action="retry_possible"))
    return dict(states=res, actions=actions)

def record_refund(run_id, step, credits):
    st = runner._load(run_id)
    st["spent"] = round(max(0.0, st["spent"] - float(credits)), 2)
    st["log"].append(dict(ts=runner.now().isoformat(timespec="seconds"), step=step, event="refund", credits=float(credits)))
    runner._save(run_id, st); return st["spent"]

def retry(run_id, step):
    st = runner._load(run_id); sc = scan(run_id)["states"]
    if sc.get(step) != "failed_retryable": return dict(ok=False, reason=f"{step} is {sc.get(step)} - only result-failed retryable steps retry")
    base = step.split("_r")[0]; n = sum(1 for c in st["calls"] if c["step"].startswith(base + "_r"))
    if n >= MAX_RETRIES: return dict(ok=False, reason=f"max {MAX_RETRIES} retries for {base}")
    c = json.loads(json.dumps(next(x for x in st["calls"] if x["step"] == step)))
    if st["spent"] + c["expected_credits"] > st["cap"] + 1e-9: return dict(ok=False, reason=f"credit cap {st['cap']} would be exceeded (spent {st['spent']})")
    c["step"] = f"{base}_r{n + 1}"; c.pop("quoted", None); c["retry_of"] = step
    # a failed still means its video must use the retried still's job
    for later in st["calls"][st["cursor"]:]:
        later["params"] = json.loads(json.dumps(later["params"]).replace("{job:%s}" % step, "{job:%s}" % c["step"]))
    st["calls"].insert(st["cursor"], c)
    st["log"].append(dict(ts=runner.now().isoformat(timespec="seconds"), step=c["step"], event="retry_scheduled", of=step))
    runner._save(run_id, st)
    import os
    p = runner._approval_path(run_id)
    if os.path.exists(p):
        a = json.load(open(p))
        if a.get("consumed"): a["consumed"] = False; a["retry_reopened_pt"] = runner.now().isoformat(timespec="seconds"); json.dump(a, open(p, "w"), indent=1)
    return dict(ok=True, step=c["step"])

def resume(run_id, live=True):
    st = runner._load(run_id)
    cur = next((i for i, c in enumerate(st["calls"]) if c["step"] not in st["jobs"]), len(st["calls"]))
    if cur != st["cursor"]: st["log"].append(dict(ts=runner.now().isoformat(timespec="seconds"), step="-", event="cursor_repaired", old=st["cursor"], new=cur)); st["cursor"] = cur; runner._save(run_id, st)
    st = runner._load(run_id)
    if st.get("inflight"): return dict(call=None, reason="in-flight submit unrecorded - reconcile first (never resubmit blind)", inflight=st["inflight"])
    stuck = [a for a in scan(run_id)["actions"] if a["action"] == "poll_existing_job"]
    if stuck: return dict(call=None, reason="poll stuck jobs first (never resubmit)", stuck=stuck)
    return runner.next_call(run_id, live=live)

def clear_inflight(run_id, step, confirmed_by):
    """D128: only after a human/agent checked Higgsfield history and confirmed NO job exists for this step."""
    st = runner._load(run_id)
    if (st.get("inflight") or {}).get("step") != step: return dict(ok=False, reason="no in-flight marker for " + step)
    st.pop("inflight"); st["log"].append(dict(ts=runner.now().isoformat(timespec="seconds"), step=step, event="inflight_cleared", by=confirmed_by))
    runner._save(run_id, st); return dict(ok=True)
