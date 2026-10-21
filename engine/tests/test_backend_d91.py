import os, sys, json, tempfile, datetime, shutil, copy
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import pandas as pd
from hookforge import scheduler as SC, recovery as RC, runner as RN, capcut_learn as CL, ab_log as AB

def _plan(n=2):   # 2 gens: 1 + 64 + 1 + 28 = 94 credits
    return dict(gens=[dict(id=f"G{i}", model="seedance_2_5", res="1080p" if i == 0 else "720p", dur=4, prompt="p", start_frame=dict(prompt="s")) for i in range(n)])

def test_scheduler():
    tmp = tempfile.mkdtemp(); SC.DIR = os.path.join(tmp, "sched"); led = os.path.join(tmp, "ledger.csv")
    open(led, "w").write("ts_pt,run_id,item,job_ids,credits\n")
    pp = os.path.join(tmp, "plan.json"); json.dump(_plan(), open(pp, "w"))
    d = datetime.date(2026, 11, 2)
    days = [SC.enqueue(f"r{i}", pp, "x", start=d)["day"] for i in range(7)]
    assert days.count(d.isoformat()) == 5 and days[5] == "2026-11-03"                      # 5 per day, overflow rolls over
    real = RN.check_gate
    out = SC.dispatchable(d, ledger=led)                                                  # LIVE disabled / no approval -> NO spend
    assert all(not ok and any("NO SPEND" in w for w in why) for _, ok, why in out)
    RN.check_gate = lambda plan, run_id, live=False, account=None: (True, [])
    try:
        open(led, "a").write(f"{d.isoformat()}T09:00,x,y,z,700\n")                         # 700 already spent today
        out = SC.dispatchable(d, ledger=led)
        oks = [j["run_id"] for j, ok, _ in out if ok]
        assert len(oks) == 1 and any("daily credit cap" in w for _, ok, why in out for w in why)   # 700+94 ok, +94 > 875
    finally: RN.check_gate = real
    big = os.path.join(tmp, "big.json"); json.dump(_plan(4), open(big, "w"))             # 1+64+3*(1+28)=152 > variant cap 100
    try: SC.enqueue("v", big, "x", kind="variant", start=d); raise AssertionError
    except ValueError: pass

def test_recovery():
    tmp = tempfile.mkdtemp(); RN.LIVE = dict(RN.LIVE, runs_dir=os.path.relpath(tmp, RN.REPO)); rid = "rec_test"
    calls = RN.build_calls(_plan(1), "PM", cast_media_ids=("C",))
    t0 = RN.now() - datetime.timedelta(hours=2)
    st = dict(run_id=rid, cap=100, spent=65.0, calls=calls, cursor=2, jobs={"G0_still": "j1", "G0_video": "j2"}, rerolls={},
              log=[dict(ts=t0.isoformat(), step="G0_still", event="submitted"), dict(ts=t0.isoformat(), step="G0_still", event="result", outcome="ok"),
                   dict(ts=t0.isoformat(), step="G0_video", event="submitted")])
    RN._save(rid, st); json.dump(_plan(1), open(os.path.join(RN._rd(rid), "plan.json"), "w"))
    sc = RC.scan(rid); assert sc["states"]["G0_video"] == "STUCK" and sc["actions"][0]["action"] == "poll_existing_job"
    r = RC.resume(rid); assert r["call"] is None and "never resubmit" in r["reason"]           # stuck -> poll, not resubmit
    st = RN._load(rid); st["log"].append(dict(ts=RN.now().isoformat(), step="G0_video", event="result", outcome="failed")); RN._save(rid, st)
    assert RC.retry(rid, "G0_video")["ok"] is False                                           # 65 + 64 > cap 100
    RC.record_refund(rid, "G0_video", 64)
    r = RC.retry(rid, "G0_video"); assert r["ok"] and r["step"] == "G0_video_r1"
    st = RN._load(rid); st["log"].append(dict(ts=RN.now().isoformat(), step="G0_video_r1", event="result", outcome="ip")); RN._save(rid, st)
    assert RC.retry(rid, "G0_video_r1")["ok"] is False                                        # ip = final, needs a human fix
    r = RC.resume(rid); assert r["call"] is None and "gate" in r["reason"]                    # LIVE disabled -> no paid call
    shutil.rmtree(RN._rd(rid))

def test_capcut_learn():
    tmp = tempfile.mkdtemp(); CL.LOG = os.path.join(tmp, "d.jsonl"); CL.OUT = os.path.join(tmp, "l.json")
    src = "/workspace/hookforge/out/capcut_test/HF_TEST_01"
    for k in range(3):
        a = os.path.join(tmp, f"a{k}"); b = os.path.join(tmp, f"b{k}"); shutil.copytree(src, a); shutil.copytree(src, b)
        d = json.load(open(os.path.join(b, "draft_info.json"))); v = next(t for t in d["tracks"] if t["type"] == "video")
        v["segments"][0]["target_timerange"]["duration"] = int(v["segments"][0]["target_timerange"]["duration"] * 0.7)   # Omar shortens the hook
        if len(v["segments"]) > 2: v["segments"].pop(1)                                    # and drops a shot
        json.dump(d, open(os.path.join(b, "draft_info.json"), "w"))
        r = CL.diff(a, b, run_id=f"t{k}")
    assert abs(r["shots"][0]["ratio"] - 0.7) < 0.01 and r["n_shots"][1] == r["n_shots"][0] - 1 and len(r["removed"]) == 1
    L = json.load(open(CL.OUT)); assert L["n_runs"] == 3 and any("hook shots shorter" in s["rule"] for s in L["suggestions"])

def test_ab_log():
    tmp = tempfile.mkdtemp(); AB.LOG = os.path.join(tmp, "ab.csv")
    AB.log_variant("T1", "vA", "song", "ACDC"); AB.log_variant("T1", "vB", "song", "FreeBird")
    try: AB.log_variant("T1", "vC", "hook", "x"); raise AssertionError
    except ValueError: pass
    o = pd.DataFrame(dict(video_id=["vA", "vB", "vA"], views=[300, 900, 400], avg_watch_s=[3.0, 4.0, 3.5], views_d1=[100, 500, 50]))
    s = pd.DataFrame(dict(video_id=["vA", "vB"], shop_sessions=[10, 5], shop_orders=[2, 0], shop_net_sales=[60.0, 0.0]))
    r = AB.results("T1", outcomes=o, sales=s); t = r["table"].set_index("video_id")
    assert t.loc["vA", "views"] == 700 and r["verdict"]["by_sales"] == "vA" and r["verdict"]["by_views"] == "vB"
    o.loc[1, "views"] = 100; assert AB.results("T1", outcomes=o, sales=s)["verdict"] == "insufficient data"

if __name__ == "__main__":
    test_scheduler(); test_recovery(); test_capcut_learn(); test_ab_log(); print("PASS test_backend_d91")
