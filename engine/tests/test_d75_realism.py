import os, sys, subprocess, tempfile, copy
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from hookforge import motion_rules as MR, iphone_grade as IG, real_footage as RF, product_refs as PR, ai_look as A, gates as G, planner as P

def _clip(path, d=2, src="testsrc2=s=360x640"):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"{src}:d={d}", "-pix_fmt", "yuv420p", path], check=True); return path

def test_motion_simple_passes():
    assert not MR.lint("Shot 1 (0-2s, TOSS): hands toss the mask onto the couch. Motion: no fast camera moves.")
def test_motion_complex_warns_and_many_actions_block():
    h = MR.lint("Shot 1 (0-4s): she spins around, jumps, grabs the box, opens it, pulls the lights, waves and runs")
    assert any(l == "BLOCK" for l, _ in h) and any("complex" in m for _, m in h)
def test_negated_phrases_ignored():
    assert not MR.lint("a man hangs the lights. no fast camera moves, never a slow unbox, no rapid cuts")
def test_simplify_idempotent():
    p = MR.simplify_motion("a hand clips it on"); assert MR.simplify_motion(p) == p and "simple action" in p
def test_g13_in_run_all_and_planner_applies_rules():
    p = P.plan("jollyglow curtain 3-2-1 elves")
    assert any(r["gate"] == "G13" for r in p["gates"]["rows"])
    assert all("simple action" in g["prompt"] and g["grade"] == "iphone_subtle" for g in p["gens"] if g["source"] == "ai")
    assert p["gens"][0].get("reference_image_paths")
def test_g13_block():
    p = copy.deepcopy(P.plan("jollyglow curtain 3-2-1 elves")); p["gens"][0]["prompt"] = "he jumps, runs, grabs, throws, catches, kicks and climbs"
    assert [r for r in G.g13_motion(p) if not r["ok"]]
def test_grade_runs_and_before_after():
    d = tempfile.mkdtemp(); r = IG.before_after(_clip(os.path.join(d, "a.mp4")), d, t=0.5, shake=True)
    assert all(os.path.exists(r[k]) for k in ("before", "after", "side_by_side", "graded"))
def test_grade_ai_only():
    assert IG.should_grade({"source": "ai"}) and not IG.should_grade({"source": "real"}) and not IG.should_grade({"kind": "card"})
def test_real_footage_reveal():
    root = tempfile.mkdtemp(); os.makedirs(os.path.join(root, "x_prod")); _clip(os.path.join(root, "x_prod", "s.mp4"), 3)
    rs = RF.reveal_shot("x_prod", root=root); assert rs["source"] == "real" and rs["credits"] == 0
    plan = {"gens": [{"id": "R", "role": "reveal", "credits": 29}]}; RF.use_real_reveal(plan, "x_prod", root=root)
    assert plan["gens"][0]["credits"] == 0 and plan["gens"][0]["source"] == "real"
    assert RF.reveal_shot("none", root=root) is None
def test_product_refs_plan():
    r = PR.plan_refs("jollyglow", "JollyGlow curtain lights"); assert r["credits"] == 3 and r["calls"][0]["image_refs"]
    assert "iPhone" in r["calls"][0]["prompt"] and r["calls"][0]["model"] == "gpt_image_2"
def test_ai_look_skips_real_and_flags_absurd():
    assert A.review_shot("x", source="real")["severity"] == "ok"
    orig = A.review_shot; A.review_shot = lambda *a, **k: dict(shot="B1", severity="absurd", worst="warped_hands", worst_score=0.95)
    try: out = A.review([{"id": "B1", "path": "x"}])
    finally: A.review_shot = orig
    assert out["problems"][0].startswith("BLOCK AI-look")
def test_ai_look_on_clip_scores():
    d = tempfile.mkdtemp(); r = A.review_shot(_clip(os.path.join(d, "c.mp4")), "T")
    assert set(r["scores"]) >= {"text_gibberish", "melting_product"} and r["severity"] in ("ok", "warn", "absurd")

def test_curated_manifest_and_reframe():
    rs = RF.reveal_shot("jollyglow_curtain")
    if rs is None: return   # footage not on this box
    assert "jg04" in rs["path"] and rs["reframe"] == "9:16"
    assert RF.reveal_shot("trumpglow") is None and RF.reveal_shot("trumpglow", allow_composite=True)["needs_composite"]
    vf = RF.reframe_vf(3840, 2160, (0, 0, 1, 0.84)); w, h = map(int, vf.split(",")[0][5:].split(":")[:2])
    assert abs(w / h - 9 / 16) < 0.01 and h <= int(2160 * 0.84)

if __name__ == "__main__":
    fails = 0
    for k, f in list(globals().items()):
        if k.startswith("test_"):
            try: f(); print("PASS", k)
            except Exception as e: fails += 1; print("FAIL", k, repr(e))
    print("failures:", fails); sys.exit(fails)
