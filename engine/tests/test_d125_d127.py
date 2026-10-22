import os, datetime
from hookforge import approval_queue as Q, credit_ledger as L, content_calendar as C, products

def test_queue_clean():
    ids = [i["id"] for i in Q.pending()]
    assert "pv_P2_payoff_redo" not in ids and all(products.is_active(i["product"]) for i in Q.pending())

@__import__("pytest").mark.owner_config
def test_log_job_requires_id_and_reconcile(tmp_path, monkeypatch):
    from hookforge import gates; monkeypatch.setattr(gates, "LEDGER", str(tmp_path / "l.csv"))
    import pytest
    with pytest.raises(ValueError): L.log_job("r", "", 5)
    L.log_job("r", "J1", 64, "G1"); assert L.log_job("r", "J1", 64, "G1")["dup"]
    t = datetime.datetime.now().astimezone().isoformat()
    r = L.reconcile([dict(display_name="Seedance", credits=-64, action="spend", created_at=t), dict(display_name="Sound Effects", credits=-1, action="spend", created_at=t)])
    assert r["matched"] == 1 and r["unledgered_credits"] == 1.0

@__import__("pytest").mark.owner_config
def test_calendar_rules():
    o = C.week(datetime.date(2026, 10, 21), write=False); s = o["slots"]
    assert {x["product"] for x in s} <= set(products.active()) and len({x["product"] for x in s}) == 3
    for pg in {x["page"] for x in s}:
        days = sorted((x["day"], x["product"]) for x in s if x["page"] == pg)
        for (d1, p1), (d2, p2) in zip(days, days[1:]):
            if (datetime.date.fromisoformat(d2) - datetime.date.fromisoformat(d1)).days == 1 and len({y["product"] for y in s if y["page"] == pg}) > 1: assert p1 != p2
    purr = [x["day"] for x in s if x["product"] == "purrventure_carrier"]; assert len(purr) == len(set(purr))
    tg = [x for x in s if x["product"] == "trumpglow"]; assert len(tg) == max(o["per_product"].values())
    for a in ("buffer1", "buffer2"): assert sum(1 for x in s if x["account"] == a) <= 10
