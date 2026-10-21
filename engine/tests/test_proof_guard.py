import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from hookforge import proof_guard as PG, audience_fit as AF
def test_emoji_proven_passes():
    assert PG.emoji_proof("😳")
def test_store_ban_flagged():
    assert PG.audit({"product_key": "x", "forbidden_settings": ["store aisle"]})
def test_omar_say_so_respected():
    assert not PG.audit({"product_key": "x", "forbidden_settings": ["store aisle"], "omar_bans": [{"item": "store aisle"}]})
def test_jollyglow_clean():
    j = json.load(open(os.path.join(PG.ROOT, "product_profiles/jollyglow_curtain.json")))
    assert not [v for v in PG.audit(j) if v["level"]=="BLOCK"]
    assert AF.check_emoji("jollyglow", "😳")["ok"] and AF.check_emoji("jollyglow", "🎅")["ok"]
def test_same_product_block():
    j = json.load(open(os.path.join(PG.ROOT, "product_profiles/jollyglow_curtain.json"))); j["forbidden_settings"] = ["store aisle"]
    assert PG.audit(j)[0]["level"] == "BLOCK"
