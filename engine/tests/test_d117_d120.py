import json, os, datetime, pytest
from hookforge import products, routing, concept_lab, perf_feedback as P, ab_log, credit_ledger as L, gates

RET = {"brickhood_mask", "merryglow_lights", "merryfire", "grinchmelt_mug", "minionmask"}

def test_active_flags():
    assert set(products.retired()) == RET | {"grinch_robe", "heatjams", "cozyjams"} and products.active() == ["jollyglow_curtain", "trumpglow", "purrventure_carrier"]   # D131
    assert not RET & set(concept_lab.PRODUCTS)

def test_retired_not_routable_and_corpus_kept():
    with pytest.raises(products.Retired): routing.route("merryfire")
    assert os.path.exists("/workspace/hookforge/product_profiles/merryfire.json")       # data kept

def test_no_duplicate_channels_and_spare_purr_routed():
    assert routing.duplicate_channels() == []
    assert [p["page"] for p in routing.route("purrventure_carrier")["pages"]] == ["purrventures_fb", "purrventures2_fb"]
    c = routing.cfg(); c["pages"]["x"] = dict(c["pages"]["purrventures_fb"]); assert routing.duplicate_channels(c)

def test_perf_loop(tmp_path, monkeypatch):
    # D169: monkeypatch, not plain assignment. The old version leaked fixture perf weights (trumpglow F09 x1.5) into every later test, including regen.
    monkeypatch.setattr(P, "DIR", str(tmp_path)); monkeypatch.setattr(ab_log, "LOG", str(tmp_path / "ab.csv"))
    rows = json.load(open(os.path.join(os.path.dirname(__file__), "fixtures", "perf_stats.json")))
    assert P.ingest(rows, "fixture")["new"] == 24 and P.ingest(rows, "fixture")["new"] == 0
    w = P.reweight()
    assert "brickhood_mask" not in w and "brickhood_mask" in w["_meta"]["reference_products"]
    assert w["trumpglow"]["hook"]["F09"]["weight"] > w["trumpglow"]["hook"]["F04"]["weight"]
    assert P.weight("trumpglow", "hook", "F09") > 1 and P.weight("trumpglow", "hook", "nope") == 1.0

def test_credit_ledger(tmp_path):
    old = gates.LEDGER; gates.LEDGER = str(tmp_path / "l.csv")
    try:
        gates.ledger_add("runX", "job1", "s1", 100, "m", "still")
        assert L.spent("runX") == 100 and L.daily()["total"] == 100
        assert not L.precheck("runX", 10)["ok"]                         # no cap on file
        assert L.precheck("runX", 50, cap=175)["warn"] and L.precheck("runX", 50, cap=175)["ok"]
        assert not L.precheck("runX", 80, cap=175)["ok"]
    finally: gates.LEDGER = old

def test_backfill_today():
    day = datetime.date(2026, 10, 20)
    exp = round(sum(r["credits"] for r in L._rows() if r["ts_pt"].startswith(day.isoformat())), 2)   # derived from the ledger, not a stale snapshot
    r = L.backfill(day); assert r["total"] == exp and exp >= 645.5
    assert L.daily()["day"] == L.today_pt().isoformat()                                           # 'today' is PT, not the box clock
