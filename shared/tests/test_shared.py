import sys, os
R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path[:0] = [os.path.join(R, "engine"), os.path.join(R, "shared", "server")]
from hookforge import telemetry as t
from promote import decide, rollback
def test_disabled(): assert t.send([{}], {"enabled": True, "opt_in": True, "endpoint": "x"}) == "disabled"
def test_whitelist_and_scrub():
    e = t.build_event("feedback", {"category": "realism", "summary": "TrumpGlow cat clips, mail a@b.com http://x.co", "store_url": "s"}, deny=["TrumpGlow"])
    assert "store_url" not in e["data"] and "a@b.com" not in e["data"]["summary"] and "TrumpGlow" not in e["data"]["summary"]
def test_promote():
    assert decide({"users_agree": 2, "users_exposed": 3, "niches": 1}) == "local"
    assert decide({"users_agree": 9, "users_exposed": 10, "niches": 3}) == "global"
    assert decide({"users_agree": 9, "users_exposed": 10, "niches": 1}) == "niche"
def test_rollback():
    assert rollback(0.3, 0.3, {"median": 1000}, {"median": 800, "n": 30})
    assert not rollback(0.3, 0.1, {"median": 1000}, {"median": 800, "n": 30})
from classify import classify, globally_eligible
def test_classify():
    assert globally_eligible(classify("the cat is literally phasing through the product"))
    assert not globally_eligible(classify("the Free Bird clip lingers too long"))
    assert not globally_eligible(classify("use 😔 emoji"))
    assert not globally_eligible(classify("weird cut but I prefer faster pacing"))
