import os, sys, json, tempfile, datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from hookforge import profiles, planner, runner, audience_fit, concept_lab as CL, approval_queue as AQ, ref_sanity as R, deliver
REPO = os.path.join(os.path.dirname(__file__), "..", "..")
NEW = ["heatjams", "cozyjams", "minionmask", "trumpglow"]
DAY = datetime.date(2026, 10, 20)

def test_new_profiles_and_audiences():
    for pk in NEW:
        p = profiles.load(pk); assert p["poc_sources"] and p["poc_hooks"], pk
        assert audience_fit.load(pk)["slug"] in (pk, "patriotglow"), pk
    assert "man" in profiles.load("trumpglow")["subject"]                      # F94 Trump -> man
    assert "woman" in profiles.load("heatjams")["subject"] and "woman" in profiles.load("cozyjams")["subject"]
    assert not any("minion" in str(v).lower() for k, v in profiles.load("minionmask").items() if k in ("product_look", "subject", "payoff_scene"))
    assert profiles.resolve("Minion Mask reel") == "minionmask" and profiles.resolve("TrumpGlow door projector") == "trumpglow"

def test_new_products_plan_clean():
    for pk, f in [("heatjams", "F07"), ("cozyjams", "F17"), ("minionmask", "F16"), ("trumpglow", "F04"), ("trumpglow", "F09")]:
        p = planner.plan("video", override={"format": f, "product_key": pk}, mode="original")
        assert p["gates"]["ok"], (pk, f, p["gates"]["blocks"]); assert runner.preflight(p)["ok"], (pk, f)
    p = planner.plan("video", override={"format": "F04", "product_key": "trumpglow"}, mode="original")
    t = [c["text"] for c in p["text_cards"]]                                          # D188/D191: then-vs-now = 2 cards, no 'Vs' on card 1
    assert len(t) == 2 and not t[0].lower().startswith("vs") and "ACTUALLY Sell" not in " ".join(t)   # F101 rejected copy never returns

def test_blockers_fixed_in_planner_not_gates():
    tmp = tempfile.mkdtemp(); AQ.DIR = os.path.join(tmp, "q")
    for pk in ["brickhood_mask", "merryfire", "merryglow_lights", "jollyglow_curtain"]:
        i = CL.propose(pk, DAY); assert i["ready_for_approval"], (pk, i["gates"].get("blocks"), i["preflight"].get("fix"))
        txt = " ".join(g["prompt"] + g["start_frame"]["prompt"] for g in i["plan"]["gens"]).lower()
        assert "cartoon" not in txt and "whoosh" not in txt and "hands on the tree lights" not in txt and "hero wide of the whole effect" not in txt
    from hookforge import gen_failures as GF, gates as G
    assert any(r["rule_id"] == "GF-Q5" and r["status"] == "promoted" for r in GF.rules())              # rules untouched
    assert "cartoon" in G.FAKE_SFX

def test_rank_and_rationale():
    tmp = tempfile.mkdtemp(); AQ.DIR = os.path.join(tmp, "q")
    appr = os.path.join(REPO, "learning", "approvals"); before = set(os.listdir(appr))
    r = CL.daily(DAY, products=["jollyglow_curtain", "trumpglow", "purrventure_carrier"])   # D131
    rk = r["ranking"]; assert len(rk) == 3 and all(x["rationale"].count("POC") and "season" in x["rationale"] and "page gap" in x["rationale"] for x in rk)
    assert [x["score"] for x in rk] == sorted([x["score"] for x in rk], reverse=True)
    top = next(i for i in r["items"] if i["id"] == rk[0]["id"])
    assert r["recommended_credits"] <= r["innovation_budget"] and r["recommended"] == [rk[0]["id"]] and r["recommended_options"][rk[0]["id"]] == ("full" if top["credits"] <= r["innovation_budget"] else "lean_1_still")   # D143: lean auto when full > budget       # budget fits one -> the top-ranked
    assert set(os.listdir(appr)) == before
    assert CL.season_fit("trumpglow", DAY)[0] == 1.0 and CL.season_fit("purrventure_carrier", DAY)[0] == 0.5

def test_resourced_cast_refs():
    import cv2, numpy as np
    want = {("grinchmelt", "cast_woman_top.png"): "5d76a5f8-f114-40d3-b538-dc67601caa01", ("merryfire", "cast_woman_top.png"): "56c3c058-f349-4042-9f2d-66b7ceada0a0",
            ("merryfire", "cast_woman_family_top.png"): "4c03390a-389c-4778-bb6d-3cc7443d2618", ("merryglow", "cast_woman_top.png"): "1854b860-9539-4331-a492-e6cf52fefd77"}
    for (s, f), mid in want.items():
        p = os.path.join(REPO, "refs", s, "cast", f)
        assert R.check(p, "a woman")["ok"] and deliver.scan(p) == [], (s, f)
        assert json.load(open(os.path.join(REPO, "refs", s, "higgsfield_new_account_media_ids.json")))["cast/" + f] == mid
        e = [r for r in json.load(open(os.path.join(REPO, "refs", s, "manifest.json")))["refs"] if r["path"].endswith("cast/" + f)][0]
        assert e["higgsfield_media_id_new_account"] == mid and "D112 re-sourced" in e["source"]
        c = cv2.imread(p); g = cv2.cvtColor(c, cv2.COLOR_BGR2GRAY)
        assert int(((c.min(axis=2) > 240) & (np.abs(cv2.Laplacian(g, cv2.CV_64F)) > 60)).sum()) <= 40, (s, f)   # no burned-in caption
        assert os.path.exists(os.path.join(REPO, "refs", "_superseded", f"{s}_{f[:-4]}_d104blurcrop.png"))

if __name__ == "__main__":
    test_new_profiles_and_audiences(); test_new_products_plan_clean(); test_blockers_fixed_in_planner_not_gates(); test_rank_and_rationale(); test_resourced_cast_refs()
    print("PASS test_d109_d112")
