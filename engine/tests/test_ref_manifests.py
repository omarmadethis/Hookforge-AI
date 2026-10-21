"""D84: every product config has a per-product ref manifest; manifest refs are clean (F87) and attach to plans."""
import json, os, glob, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from hookforge import refs_lib
from hookforge.config import REPO

def test_every_product_config_has_manifest():
    keys = [os.path.basename(f)[:-5] for f in glob.glob(os.path.join(REPO, "product_profiles", "*.json"))]
    assert keys
    missing = [k for k in keys if k not in refs_lib.SLUGS or refs_lib.manifest(k) is None]
    assert not missing, f"no refs/<slug>/manifest.json for {missing} (python3 -m hookforge.refs_lib)"

def test_manifest_fields_and_clean_copies():
    for k in refs_lib.SLUGS:
        m = refs_lib.manifest(k)
        if m is None: continue
        for f in ("slug", "product_keys", "approved_cast_status", "refs"): assert f in m, (k, f)
        for r in m["refs"]:
            if r.get("use_for_generation"): assert r["clean"], f"{k}: {r['path']} carries metadata"

def test_attach_adds_refs():
    g = refs_lib.attach({"id": "B1", "start_frame": {"prompt": "x"}}, "grinch_robe")
    assert g["start_frame"].get("refs") and g["reference_image_paths"]

def test_purrventure_poc_defaults():
    d = json.load(open(os.path.join(REPO, "config", "poc_defaults.json")))["purrventure_carrier"]
    assert "get yours" not in json.dumps(d).lower() and "{url}" not in json.dumps(d)
    assert d["music"][0]["song"] == "mambo_no_5" and "PURR" in d["caption"]["text"]

def test_g23_say_not_comment():
    from hookforge import gates, publish
    bad = gates.g23_say_not_comment({"caption": {"text": 'Comment "PURR" if you want one!'}})
    good = gates.g23_say_not_comment({"caption": {"text": 'SAY "PURR" if you want one!'}})
    assert not bad[0]["ok"] and good[0]["ok"]
    assert any("SAY" in p for p in publish._caption_checks('Comment "X" now'))
    d = json.load(open(os.path.join(REPO, "config", "poc_defaults.json")))["purrventure_carrier"]
    assert d["caption"]["text"].startswith("SAY ")
