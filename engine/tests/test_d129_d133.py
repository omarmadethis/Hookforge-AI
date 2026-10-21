import os, json, datetime, pytest
from hookforge import spend_watch as W, render_queue as RQ, content_calendar as CC, hook_variants as H, gates, audience_fit, products

def test_spend_watch_flags_only_new_over_20(tmp_path, monkeypatch):
    for n in ("DIR",): monkeypatch.setattr(W, n, str(tmp_path))
    monkeypatch.setattr(W, "STATE", str(tmp_path / "s.json")); monkeypatch.setattr(W, "STATUS", str(tmp_path / "st.json")); monkeypatch.setattr(W, "HIST", str(tmp_path / "h.jsonl"))
    monkeypatch.setattr(gates, "LEDGER", str(tmp_path / "l.csv"))
    t0 = '  Seedance 2.5,-64,spend,"2026-10-20T20:00:00.000001Z"\n'
    assert W.check(t0)["baseline"] and not W.check(t0)["flag"]                      # baseline, then nothing new
    s = W.check(t0 + '  Seed Audio 1.0,-25,spend,"2026-10-20T21:00:00.000001Z"\n'); assert not s["flag"] and s["new_external_credits"] == 25   # D161 external
    s = W.check(t0 + '  Seedance 2.5,-28,spend,"2026-10-20T21:10:00.000001Z"\n'); assert s["flag"] and s["new_unledgered_credits"] == 28     # Hookforge model, no ledger row
    s = W.check(t0 + '  Seed Audio 1.0,-25,spend,"2026-10-20T21:00:00.000001Z"\n  Sound Effects,-5,spend,"2026-10-20T21:30:00.000001Z"\n  Seedance 2.5,-5,spend,"2026-10-20T21:31:00.000001Z"\n'); assert not s["flag"]   # 5 <= 20
    assert os.path.exists(W.STATUS)

def test_render_queue_blocks_slots_without_video():
    o = CC.week(datetime.date(2026, 10, 21), write=False)
    assert all(s["render_status"] in ("READY", "NEEDS_URL", "NEEDS_VIDEO") for s in o["slots"])
    for s in o["slots"]:
        if s["render_status"] != "READY":
            with pytest.raises(RQ.NotSchedulable): RQ.schedulable(s)
            assert s["status"].startswith("DRAFT")

def test_hook_variants_gated():
    q = [json.load(open(os.path.join("/workspace/hookforge/learning/approval_queue", f))) for f in os.listdir("/workspace/hookforge/learning/approval_queue") if f.endswith(".json")]
    for it in [x for x in q if x.get("kind") == "concept_test"]:   # D135: weekly_batch items have no single product
        v = H.for_concept(it)
        assert len(v["hooks"]) == 3 and len(v["captions"]) == 3 and v["credits"] == 0
        for x in v["hooks"] + v["captions"]:
            assert H.words(x["text"]) <= 8 and "comment" not in x["text"].lower() and x["poc"]
    assert H.gate("one two three four five six seven eight nine", "trumpglow") and H.gate("The election was stolen 🇺🇸", "trumpglow")

def test_yaml_cache_is_copy():
    a = audience_fit.load("trumpglow"); a["x"] = 1; assert "x" not in audience_fit.load("trumpglow")
