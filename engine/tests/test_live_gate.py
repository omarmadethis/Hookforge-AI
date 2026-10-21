"""Live Higgsfield gate test: proves the default build submits nothing and that the gate opens only for a valid Omar approval.
Uses a temp approvals/runs dir; the engine has no network path, so nothing can reach Higgsfield from here."""
import os, sys, json, tempfile, datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from hookforge import planner, runner, config

def main():
    res = []; ok = lambda n, c, d="": res.append((n, bool(c), d))
    p = planner.plan("3-2-1 video for the grinch robe", mode="original"); rid = "gate-test"
    ok("default_disabled", config.LIVE["enabled"] is False)
    r = runner.submit(p, live=True, approved=True, run_id=rid); ok("default_submits_nothing", not r.get("started") and r.get("submitted") is False, r.get("gate"))
    ok("plan_total_matches_quote", sum(c["expected_credits"] for c in runner.build_calls(p)) == 200.0)   # D115: 2 still variants, = quote
    tmp = tempfile.mkdtemp(); saved = dict(config.LIVE)
    try:
        config.LIVE.update(enabled=True, approvals_dir=os.path.relpath(os.path.join(tmp, "ap"), config.REPO), runs_dir=os.path.relpath(os.path.join(tmp, "runs"), config.REPO))
        os.makedirs(os.path.join(tmp, "ap"))
        ok("enabled_no_file_refused", not runner.check_gate(p, rid, live=True)[0])
        a = runner.approval_template(p, rid); path = os.path.join(tmp, "ap", rid + ".json")
        for bad, why in ((dict(approved_by="someone"), "approved_by"), (dict(plan_sha256="x"), "sha"), (dict(credit_cap=100), "cap"),
                         (dict(expires_pt="2020-01-01T00:00:00-08:00"), "expired"), (dict(account="user-Higgsfield"), "account"), (dict(consumed=True), "consumed")):
            json.dump(dict(a, **bad), open(path, "w")); ok("refuse_" + why, not runner.check_gate(p, rid, live=True)[0])
        json.dump(a, open(path, "w")); ok("no_frame_approval_refused_G8", not runner.check_gate(p, rid, live=True)[0])
        from hookforge import gates; gates.LEDGER = os.path.join(tmp, "ledger.csv")
        json.dump(gates.frames_template(rid, {g["id"]: "v1" for g in p["gens"]}), open(gates.frames_path(rid), "w"))
        json.dump(a, open(path, "w")); ok("valid_opens", runner.check_gate(p, rid, live=True)[0], runner.check_gate(p, rid, live=True)[1])
        ok("live_false_refused", not runner.check_gate(p, rid, live=False)[0])
        s = runner.start_run(p, rid, live=True, product_media_id="11111111-2222-3333-4444-555555555555", cast_media_ids=["66666666-7777-8888-9999-000000000000"]); ok("start_run", s.get("started"), s)
        n = runner.next_call(rid); ok("first_is_get_cost", n["phase"] == "get_cost" and n["call"]["arguments"]["params"]["get_cost"] is True)
        ok("cost_mismatch_stops", not runner.record_cost(rid, "H_still", 9)["ok"])
        runner.record_cost(rid, "H_still", runner._load(rid)["calls"][0]["expected_credits"]); n = runner.next_call(rid); ok("then_submit", n["phase"] == "submit" and "get_cost" not in n["call"]["arguments"]["params"])
        runner.GF.log_attempt = lambda *x, **k: "test"     # keep the real ledger clean
        runner.record_submit(rid, "H_still", "JOB-STILL"); n = runner.next_call(rid)
        ok("video_uses_still_job", "JOB-STILL" in json.dumps(n["call"]))
        ok("advances_to_next_step", runner.next_call(rid)["phase"] == "get_cost")
        st = runner._load(rid); st["spent"] = 170; runner._save(rid, st); ok("cap_enforced", runner.next_call(rid)["call"] is None)
    finally:
        config.LIVE.clear(); config.LIVE.update(saved)
    ok("restored_disabled", config.LIVE["enabled"] is False)
    for n, c, d in res: print(("PASS " if c else "FAIL ") + n, "" if c else d)
    print(f"{sum(c for _, c, _ in res)}/{len(res)} passed"); sys.exit(0 if all(c for _, c, _ in res) else 1)

if __name__ == "__main__": main()
