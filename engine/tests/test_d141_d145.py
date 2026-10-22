import json, os
from hookforge import pv_p2_redo as P2, lean_plan as L, concept_lab as C, approval_queue as AQ
def test_p2_stays_archived():
    it = P2.queue(); assert it["status"] == "ARCHIVED_STALE" and not it["ready_for_approval"]
    assert "pv_P2_payoff_redo.json" not in os.listdir(AQ.DIR)
def test_lean_reuse_and_1080p_hook_removed():          # D180/D181/D192
    import pytest, inspect
    with pytest.raises(RuntimeError): L.write({})
    assert L.HOOK_RES == "720p"
    assert "lean_1080p_hook" not in inspect.getsource(C) and "lean_1_still" not in inspect.getsource(C)
def test_dup_gate_catches_identical():
    sm = [dict(page="p", product="x", video="x_V1"), dict(page="p", product="x", video="x_V2")]
    e = (("B1", 0, 96), ("B2", 0, 96), ("B3", 0, 96))
    assert L.check(sm, {"x_V1": e, "x_V2": e})
def test_daily_recommends_full_plans_only():
    d = C.daily(); assert d["recommended_credits"] <= d["innovation_budget"]
    assert all(i.get("recommended_option") in (None, "full") for i in d.get("items", []))
    assert all(o in ("full", "lean_1_still") for o in d["recommended_options"].values())
def test_jolly_caption():
    caps = [m["caption"] for m in C.weekly(write=False)["slot_map"] if m["product"] == "jollyglow_curtain"]
    assert not any("hard to gift" in c.lower() for c in caps) and any("window is boring" in c.lower() for c in caps)
