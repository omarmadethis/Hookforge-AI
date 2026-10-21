import json, datetime, glob
from hookforge import gates, political_lint, fb_caption, worlds, profiles

def test_g24_blocks_brickhood_store_aisle():
    prof = profiles.load("brickhood_mask")
    assert worlds.world_conflicts(prof, "woman in a store aisle holding the mask")

def test_political_lint():
    from hookforge import political_lint as P
    assert any(l == "BLOCK" for _, l, _ in P.lint_text("The election was stolen"))
    assert not any(l == "BLOCK" for _, l, _ in P.lint_text("Don't show this to a liberal 😂"))
    assert any(l == "BLOCK" for _, l, _ in P.lint_text("liberals are idiots"))
    assert P.check({"product_key":"grinch_robe"})["applies"] is False

def test_queue_current():
    q = [json.load(open(f)) for f in glob.glob("/workspace/hookforge/learning/approval_queue/concept_2026-10-20_*")]
    live = {d["product"]: d for d in q if d.get("status") != "SUPERSEDED"}
    arch = json.load(open("/workspace/hookforge/learning/approval_queue/_archive/concept_2026-10-20_brickhood_mask_F01.json"))
    assert arch["format"] == "F01" and arch["status"] == "RETIRED"          # D125: retired items moved to _archive
    assert live["trumpglow"]["format"] == "F09" and live["trumpglow"]["ready_for_approval"]

def test_no_fake_say():
    t = fb_caption.generate("grinchmelt_mug", {}, platform="facebook")["text"]
    assert "SAY about" not in t

def test_e2e_summary():
    s = json.load(open("/workspace/hookforge/learning/e2e_dryrun/2026-10-20/SUMMARY.json"))
    assert len(s["products"]) == 3 and all(v.startswith("OK") for v in s["products"].values())
    for f in glob.glob("/workspace/hookforge/learning/e2e_dryrun/2026-10-20/*/buffer_payloads.json"):
        assert "{url}" not in open(f).read()
