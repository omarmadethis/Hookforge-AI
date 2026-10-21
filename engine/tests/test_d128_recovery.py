"""D128 crash-recovery / resume for a half-finished generation run (temp dirs; nothing can reach Higgsfield)."""
import os, json, datetime, pytest
from hookforge import planner, runner, recovery, config, gates, credit_ledger

@pytest.fixture
def run(tmp_path, monkeypatch):
    LV = runner.LIVE; saved = dict(LV)
    LV.update(enabled=True, approvals_dir=os.path.relpath(tmp_path / "ap", config.REPO), runs_dir=os.path.relpath(tmp_path / "runs", config.REPO))
    os.makedirs(tmp_path / "ap"); monkeypatch.setattr(gates, "LEDGER", str(tmp_path / "ledger.csv"))
    monkeypatch.setattr(runner.GF, "log_attempt", lambda *a, **k: "test")
    p = planner.plan("3-2-1 video for the grinch robe", mode="original"); rid = "crash-test"
    a = runner.approval_template(p, rid); a["approval_quote"] = "test"; json.dump(a, open(tmp_path / "ap" / (rid + ".json"), "w"))
    gates.LEDGER = str(tmp_path / "ledger.csv")
    json.dump(gates.frames_template(rid, {g["id"]: "v1" for g in p["gens"]}), open(gates.frames_path(rid), "w"))
    s = runner.start_run(p, rid, live=True, product_media_id="11111111-2222-3333-4444-555555555555", cast_media_ids=["66666666-7777-8888-9999-000000000000"])
    assert s.get("started"), s
    yield rid
    LV.clear(); LV.update(saved)
    try: os.remove(gates.frames_path(rid))
    except OSError: pass

def _step(rid, job):
    n = runner.next_call(rid); assert n["phase"] == "get_cost"
    runner.record_cost(rid, n["step"], runner._load(rid)["calls"][runner._load(rid)["cursor"]]["expected_credits"])
    n = runner.next_call(rid); assert n["phase"] == "submit"; runner.record_submit(rid, n["step"], job); return n["step"]

def test_crash_after_submit_before_record_never_double_submits(run):
    n = runner.next_call(run); runner.record_cost(run, n["step"], runner._load(run)["calls"][0]["expected_credits"])
    assert runner.next_call(run)["phase"] == "submit"           # handed out -> process "crashes" here
    r = recovery.resume(run); assert r["call"] is None and "in-flight" in r["reason"]
    assert runner.next_call(run)["call"] is None                 # still refuses
    runner.record_submit(run, n["step"], "JOB-FOUND-IN-HISTORY")  # job id found -> recorded, run continues
    assert recovery.resume(run).get("phase") in ("get_cost", None)

def test_clear_inflight_only_when_confirmed(run):
    n = runner.next_call(run); runner.record_cost(run, n["step"], runner._load(run)["calls"][0]["expected_credits"]); runner.next_call(run)
    assert recovery.clear_inflight(run, n["step"], "checked Higgsfield history: no job")["ok"]
    assert runner.next_call(run)["phase"] == "submit"

def test_cursor_repair_after_torn_progress(run):
    s1 = _step(run, "JOB-1"); st = runner._load(run); st["cursor"] = 0; runner._save(run, st)   # crash rolled the cursor back
    recovery.resume(run); assert runner._load(run)["cursor"] == 1

def test_stuck_job_is_polled_not_resubmitted(run):
    s1 = _step(run, "JOB-1"); st = runner._load(run)
    for e in st["log"]:
        if e["event"] == "submitted": e["ts"] = (runner.now() - datetime.timedelta(hours=2)).isoformat(timespec="seconds")
    runner._save(run, st)
    r = recovery.resume(run); assert r["call"] is None and r["stuck"][0]["job_id"] == "JOB-1"

def test_failed_retryable_retry_and_ledger_dedupe(run):
    s1 = _step(run, "JOB-1"); runner.record_result(run, s1, "failed", "server_error")
    assert recovery.retry(run, s1)["ok"]
    assert credit_ledger.log_job(run, "JOB-1", 1.0, s1)["dup"]   # re-logging the same job after a crash never double-counts
    assert credit_ledger.spent(run) == runner._load(run)["spent"]

def test_atomic_save_leaves_no_torn_file(run):
    st = runner._load(run); runner._save(run, st)
    d = runner._rd(run); assert not os.path.exists(os.path.join(d, "run.json.tmp")); json.load(open(os.path.join(d, "run.json")))
