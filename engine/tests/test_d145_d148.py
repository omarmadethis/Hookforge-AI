import os, subprocess, tempfile
from hookforge import lean_edit as E, lean_plan as L, runner, publish, planner, concept_lab as C

def _clip(path, vf):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", vf, "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                    "-t", "4", "-r", "24", "-s", "180x320", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", path], check=True)

def test_reveal_detect_and_check():
    d = tempfile.mkdtemp(); p = os.path.join(d, "b3.mp4")
    _clip(p, "color=c=black:s=180x320:d=4,drawbox=enable='gte(t,1.25)':c=white:t=fill")   # lights on at 1.25 s
    rv = E.reveal_frame_s(p); assert rv and abs(rv - 1.25) < 0.1
    assert E.reveal_check((("B1", 0, 48), ("B3", 0, 48)), rv)["ok"]
    assert not E.reveal_check((("B1", 0, 48), ("B3", 0, 48)), 1.8)["ok"]           # reveal 1.8 s into the payoff -> flagged
    assert not E.reveal_check((("B3", 48, 96),), rv)["ok"]                           # reveal trimmed off
    assert not E.reveal_check((("B3", 0, 48),), None)["ok"]                          # unknown -> human check

def test_build_reorder_trim_real_ffmpeg():
    d = tempfile.mkdtemp(); f = {}
    for k, c in (("H", "red"), ("B1", "green"), ("B2", "blue"), ("B3", "yellow")):
        f[k] = os.path.join(d, k + ".mp4"); _clip(f[k], f"color=c={c}:s=180x320:d=4")
    e = (("B2", 0, 48), ("B1", 24, 72), ("B3", 12, 60))
    r = E.build(f["H"], {k: f[k] for k in ("B1", "B2", "B3")}, e, os.path.join(d, "v.mp4"), clean=False)
    assert abs(r["duration"] - 10.0) < 0.1

def test_lean_calls_hook_only():
    p = planner.plan("3-2-1 video for the JollyGlow curtain", override={"format": "F01", "product_key": "jollyglow_curtain"}, mode="original")
    assert sum(c["expected_credits"] for c in runner.build_calls_lean(p, "extra")) == 70.5
    assert sum(c["expected_credits"] for c in runner.build_calls_lean(p, "anchor")) == 174.0

def test_edit_plan_respects_reveal():
    sm = [dict(page="p", product="x", video=f"x_V{i}") for i in (1, 2, 3)]
    ed, _ = L.edit_plan(sm, {"x": 1.54})
    assert all(E.reveal_check(e, 1.54)["ok"] for e in ed.values()) and not L.check(sm, ed)

def test_jolly_hook_and_say():
    p = planner.plan("Gift difficulty POV video for the JollyGlow curtain", override={"format": "F06", "product_key": "jollyglow_curtain"}, mode="original")
    assert "JEALOUS" in p["hook"]["text"] and "gift" not in p["hook"]["text"].lower()
    assert publish.ensure_say("Your neighbors are gonna be jealous... #christmasdecor", "LIGHTS") == 'Your neighbors are gonna be jealous... SAY "LIGHTS" #christmasdecor'
    caps = [m["caption"] for m in C.weekly(write=False)["slot_map"]]
    assert all('SAY "' in c for c in caps)
