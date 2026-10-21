import os, json, datetime, subprocess
from hookforge import credit_ledger as L, reroll_planner as R, approval_digest as D, e2e_dryrun as E, caption_variants as C

def test_caps_closed():
    s = L.status("purrventure_video"); assert s["cap"] == 650 and s["closed"] and s["group"] == "purrventure_3videos"
    assert not L.precheck("purrventure_video", 1)["ok"]
    assert L.status("purrventure_p2_addshot")["spent"] == 34.5 and L.status("purrventure_branding_v2")["cap"] == 40

def _melt(p):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=s=180x320:d=2:r=15", "-f", "lavfi", "-i", "smptebars=s=180x320:d=1:r=15",
                    "-filter_complex", "[0][1]concat=n=2[v]", "-map", "[v]", p], check=True)

def test_reroll_cheapest(tmp_path):
    p = str(tmp_path / "m.mp4"); _melt(p)
    g = dict(id="G3", prompt="woman sets the cat ball on the grass", res="720p", dur=4, start_frame=dict(n=1))
    it = R.propose("t", g, dict(worst="melting_product", worst_score=0.7, severity="warn", frames=[0.1]), p, 1.5, "purrventure_carrier")
    assert it["recommended"] == "retrim" and it["credits"] == 0
    it = R.propose("t", g, dict(worst="warped_hands", worst_score=0.7, severity="warn"), p, 2.5, "purrventure_carrier")
    assert it["recommended"] == "reroll" and it["credits"] == 28.0 and "five normal fingers" in it["options"][0]["gen"]["prompt"]
    R.queue(it, str(tmp_path)); assert json.load(open(tmp_path / (it["id"] + ".json")))["status"] == "AWAITING_OMAR_APPROVAL"

def test_purr2_caption():
    v = C.for_page("purrventure_carrier", "purrventures2_fb")
    assert "explore outside" in v["caption"] and "rushing" not in v["caption"] and 'SAY "PURR"' in v["caption"]

def test_digest(tmp_path):
    r = D.build(str(tmp_path / "d.html")); h = open(r["path"]).read()
    assert r["n"] >= 1 and "Yes" in h and "brickhood" not in " ".join(r["ids"])
