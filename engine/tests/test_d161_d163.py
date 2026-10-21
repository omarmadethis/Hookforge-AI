import os, json, subprocess, sys
from hookforge import spend_attrib as A, spend_watch as W, gates

def _led(tmp_path, monkeypatch, rows):
    p = tmp_path / "l.csv"; p.write_text("ts_pt,run_id,item,job_ids,credits\n" + "".join(r + "\n" for r in rows))
    monkeypatch.setattr(gates, "LEDGER", str(p))

def tx(name, cr, ts): return dict(display_name=name, credits=-cr, action="spend", created_at=ts)

def test_attribution_tags(tmp_path, monkeypatch):
    _led(tmp_path, monkeypatch, ["2026-10-20T10:00,jollyglow_frames,gpt_image_2 x3 frames,a;b;c,3", "2026-10-20T10:00,purrventure_video,P1_G1,j1,64"])
    r = A.attribute([tx("GPT Image 2.0", 1, f"2026-10-20T17:0{i}:00Z") for i in range(4)] + [tx("Seedance 2.5", 64, "2026-10-20T17:20:00Z"),
                    tx("GPT Image 2.5 Flare", 1.5, "2026-10-20T17:01:00Z"), tx("Seedance 2.5", 28, "2026-10-20T23:00:00Z")])
    tags = [x["tag"] for x in r["rows"]]
    assert tags.count("hookforge") == 4 and tags.count("external") == 1 and tags.count("hookforge_unaccounted") == 2   # 4th image exceeds the 3-credit pool
    b = r["by_model"]; assert b["GPT Image 2.0"]["hookforge"] == 3 and b["GPT Image 2.0"]["hookforge_unaccounted"] == 1
    assert b["GPT Image 2.5 Flare"]["external"] == 1.5 and b["Seedance 2.5"]["hookforge_unaccounted"] == 28
    assert next(x for x in r["rows"] if x["credits"] == 64)["job_ids"] == "j1"

def test_external_never_flags(tmp_path, monkeypatch):
    _led(tmp_path, monkeypatch, [])
    for n, f in (("STATE", "s.json"), ("STATUS", "st.json"), ("HIST", "h.jsonl")): monkeypatch.setattr(W, n, str(tmp_path / f))
    W.check([tx("Sound Effects", 1, "2026-10-20T20:00:00Z")])
    s = W.check([tx("Text to Music", 300, "2026-10-20T21:00:00Z")])
    assert not s["flag"] and s["new_external_credits"] == 300 and s["new_by_model"]["Text to Music"]["external"] == 300

def test_ci_workflow_and_markers():
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    y = open(os.path.join(root, ".github/workflows/test.yml")).read()
    assert "not needs_data" in y and "push" in y
    assert "needs_data" in open(os.path.join(root, "engine/pytest.ini")).read()

def test_restore_plan_dry_run_only(tmp_path):
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    o = tmp_path / "plan.json"
    r = subprocess.run([sys.executable, os.path.join(root, "automation/restore_assets.py"), "--out", str(o)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    p = json.load(open(o)); assert p["dry_run"] is True and p["items"] and all(i["action"] in ("download", "present", "unresolved", "manual_only") for i in p["items"])
    r = subprocess.run([sys.executable, os.path.join(root, "automation/restore_assets.py"), "--execute"], capture_output=True, text=True)
    assert r.returncode != 0
