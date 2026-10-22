"""D191 master pre-delivery gate: rules registry, checks, auto-fix loop, wiring (deliver/publish/render refuse w/o PASS)."""
import json, os, re, subprocess, tempfile
import numpy as np, pytest
from hookforge import master_gate as MG, deliver, publish

@pytest.fixture(autouse=True)
def _no_bypass(monkeypatch, tmp_path):
    monkeypatch.delenv("HOOKFORGE_GATE_TEST_BYPASS", raising=False)
    monkeypatch.setattr(MG, "REGISTRY", str(tmp_path / "reg.json")); monkeypatch.setattr(MG, "HASH_CACHE", str(tmp_path / "hc.json"))
    monkeypatch.setattr(MG, "CANDIDATE_ROOTS", [str(tmp_path / "corpus")])
    monkeypatch.setattr(MG, "PUBLISH_LOG", str(tmp_path / "plog")); os.makedirs(tmp_path / "plog")

def _ff(*a): subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)
def _song(path, sr=8000, secs=20, seed=3):
    rng = np.random.default_rng(seed); x = (0.03 * np.sin(np.arange(sr * secs) * 2 * np.pi * 110 / sr)).astype(np.float32)   # bed: never silent
    for t in np.cumsum(rng.uniform(0.12, 0.45, 200)):                      # irregular clicks = unique onset fingerprint
        i = int(t * sr)
        if i + 400 < len(x): x[i:i + 400] += rng.uniform(0.3, 0.9) * np.sin(np.arange(400) * rng.uniform(0.2, 1.2)) * np.hanning(400)
    raw = path + ".f32"; x.tofile(raw); _ff("-f", "f32le", "-ar", str(sr), "-ac", "1", "-i", raw, "-c:a", "aac", path); os.remove(raw)

def _manual_ok(path, spec):
    h = MG.sha(path)
    spec["confirm"] = {r["id"]: dict(by="test reviewer", note="checked frames and audio carefully here", sha256=h) for r in MG.rules() if r["check"] in ("manual", "auto+manual")}

def test_every_rule_documented_and_checkable():
    rs = MG.rules(); ids = [r["id"] for r in rs]
    assert len(ids) == len(set(ids)) and len(rs) >= 45
    assert all(r["fn"] in MG.CHECKS for r in rs if r["check"] in ("auto", "auto+manual"))
    md = open(os.path.join(MG.REPO, "rules", "MASTER_RULES.md")).read()
    assert all(f"| {i} |" in md for i in ids)
    for must in ("Apple", "exact song", "ONE on-screen card", "first frame", "conflict", "3-2-1", "2 pages", "720p", "Zero metadata", "faces", "SAY", "Drive"):
        assert must.lower() in md.lower(), must

def test_image_metadata_autofixed_on_require(tmp_path):
    from PIL import Image
    p = str(tmp_path / "pfp.jpg"); im = Image.new("RGB", (64, 64), "red"); ex = Image.Exif(); ex[0x0131] = "Higgsfield AI"; im.save(p, exif=ex)
    assert deliver.scan(p)
    assert MG.require(p) and not deliver.scan(p)                      # auto-stripped, verified, PASS report written
    assert json.load(open(p + ".PASS.json"))["status"] == "PASS"

def test_any_file_metadata(tmp_path):
    p = str(tmp_path / "notes.txt"); open(p, "w").write("plain text")
    assert MG.require(p)

def test_card_rules_and_free_text_fixes():
    spec = dict(hook=dict(format="statement-needs-store"), shots=[dict(gen="a", t0=0, t1=2), dict(gen="b", t0=2, t1=4), dict(gen="c", t0=4, t1=6)],
                cards=[dict(text="VS this one is way too many words for one card 😏", t0=0, t1=2), dict(text="Get yours now", t0=2, t1=4), dict(text="Third 🎄", t0=4, t1=6)])
    fails = [f for fn in ("card_count", "card_words", "vs_position", "no_get_yours") for f in MG.CHECKS[fn](None, spec, "final")]
    assert {f["rule"] for f in fails} == {"MR31", "MR32", "MR33", "MR34"}
    MG.repair_cards(spec, fails)
    after = [f for fn in ("card_count", "card_words", "vs_position", "no_get_yours") for f in MG.CHECKS[fn](None, spec, "final")]
    assert not after and len(spec["cards"]) == 1 and spec["cards"][0]["t1"] == 6

def test_vs_two_cards_allowed_three_blocked():
    two = dict(hook=dict(format="then-vs-now"), cards=[dict(text="The idea... 😭💡"), dict(text="The result 😍🙈")])
    assert not MG.CHECKS["card_count"](None, two, "final")
    three = dict(hook=dict(format="then-vs-now"), cards=[dict(text="Then"), dict(text="Vs..."), dict(text="Now")])
    assert MG.CHECKS["card_count"](None, three, "final")

def test_caption_fixes_say_and_dedupe(tmp_path):
    open(os.path.join(MG.PUBLISH_LOG, "x.md"), "w").write("Jolly Glow post\nCaption (exact payload): Our street was NOT ready for this 😏🇺🇸 / #x\n")
    spec = dict(page="Jolly Glow", caption='Our street was NOT ready for this 😏🇺🇸\nComment "MOM" for the link', say_keyword="MOM")
    fails = MG.CHECKS["caption_say"](None, spec, "publish") + MG.CHECKS["caption_fresh"](None, spec, "publish")
    assert {f["rule"] for f in fails} == {"MR40", "MR42"}
    MG.fix_caption(spec, fails)
    assert "Comment" not in spec["caption"] and 'SAY "MOM"' in spec["caption"] and "NOT ready" not in spec["caption"]

def test_resolution_and_gen_packing_plan():
    spec = dict(gens=[dict(id="H", role="hook", res="1080p", dur=4, shots=["H"]), dict(id="B1", role="body", res="720p", dur=8, shots=["a", "b", "c"])])
    rules = {f["rule"] for fn in ("res_720", "gen_packing", "gen_len") for f in (MG.CHECKS[fn](None, spec, "final") if fn != "res_720" else [x for x in MG.c_res_720.__wrapped__(spec)] if hasattr(MG.c_res_720, "__wrapped__") else [])}
    rules |= {f["rule"] for f in MG.CHECKS["gen_packing"](None, spec, "final") + MG.CHECKS["gen_len"](None, spec, "final")}
    assert {"MR04", "MR05"} <= rules
    with pytest.raises(MG.GateRefused): MG.pre_render(spec | dict(hook=dict(format="statement-needs-store", first_second_action="x grabs", conflict="fight", conflict_t_s=0.3)))

def test_321_spec_enforced():
    h = dict(format="321-prop-reveal", first_second_action="all count", conflict="covered box", count321=dict(covered_cue_at_0="", all_count=False))
    assert len(MG.CHECKS["count321"](None, dict(hook=h), "final")) >= 3

def test_song_continuity_detects_loop(tmp_path):
    ref = str(tmp_path / "song.m4a"); _song(ref)
    good = str(tmp_path / "good.m4a"); _ff("-ss", "3", "-t", "8", "-i", ref, good)
    looped = str(tmp_path / "loop.m4a"); a = str(tmp_path / "a.m4a"); _ff("-ss", "3", "-t", "4", "-i", ref, a)
    _ff("-i", a, "-i", a, "-filter_complex", "[0:a][1:a]concat=n=2:v=0:a=1", looped)
    assert not MG.song_continuity(good, ref, 3.0)[1]
    assert MG.song_continuity(looped, ref, 3.0)[1]

def test_footage_hash_identical_and_distinct(tmp_path):
    a = str(tmp_path / "a.mp4"); b = str(tmp_path / "b.mp4")
    _ff("-f", "lavfi", "-i", "testsrc2=s=180x320:d=2", a); _ff("-f", "lavfi", "-i", "mandelbrot=s=180x320:r=25", "-t", "2", b)
    assert MG.shared_ratio(MG._hashes(a), MG._hashes(a)) == 1.0
    assert MG.shared_ratio(MG._hashes(a), MG._hashes(b)) < 0.02

def _video(tmp_path):
    body = str(tmp_path / "V9_body.mp4"); song = str(tmp_path / "song.m4a"); _song(song)
    _ff("-f", "lavfi", "-i", "testsrc2=s=720x1280:r=30:d=2", "-f", "lavfi", "-i", "smptehdbars=s=720x1280:r=30:d=1", "-f", "lavfi", "-i", "mandelbrot=s=720x1280:r=30",
        "-f", "lavfi", "-i", "rgbtestsrc=s=720x1280:r=30:d=1.5", "-f", "lavfi", "-i", "anoisesrc=d=6:a=0.01", "-filter_complex",
        "[2:v]trim=0:1.5,setpts=PTS-STARTPTS[m];[0:v][1:v][m][3:v]concat=n=4:v=1:a=0,format=yuv420p,drawbox=x=0:y=0:w=200:h=120:color=red@1:t=fill,drawbox=x=520:y=0:w=200:h=120:color=blue@1:t=fill[v]", "-map", "[v]", "-map", "4:a",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", body)
    draft = str(tmp_path / "V9_final.mp4")
    spec = dict(video_id="V9", product="jollyglow", hook=dict(format="statement-needs-store", first_second_action="two moms grab the last box", conflict="tug of war", conflict_t_s=0.3),
                shots=[dict(gen="H", t0=0, t1=2, role="hook"), dict(gen="Ba", t0=2, t1=3, role="after"), dict(gen="Bb", t0=3, t1=4.5, role="after"), dict(gen="Bc", t0=4.5, t1=6, role="after")],
                cards=[dict(text="EVERY Christmas Mom NEEDS this 🎄😱", t0=0.4, t1=3), dict(text="Get yours now 👇", t0=3, t1=4.5), dict(text="third card", t0=4.5, t1=6)],
                song=dict(key="test", path=song, in_s=2.0), gens=[dict(id="H", role="hook", res="720p", dur=4, shots=["H"])],
                edit=dict(body=body, W=720, H=1280), regen=dict(cap_remaining=0), spend=dict(cap=10, spent=5), frames_shown=True)
    shutil = __import__("shutil"); shutil.copyfile(body, draft)          # draft = body with NO song, NO cards -> must fail then auto-fix
    return draft, spec

def test_autofix_loop_reaches_pass_and_wiring(tmp_path, monkeypatch):
    draft, spec = _video(tmp_path)
    with pytest.raises(deliver.Refused): deliver.stage(draft)          # no PASS report -> nothing leaves
    r1 = MG.run(draft, spec, "final"); assert r1["status"] == "FAIL"
    MG.recompose(draft, spec); MG.repair_cards(spec, r1["failures"])   # (ensure does this itself; prime sha for confirmations)
    real_ensure = MG.ensure(draft, spec, "final")
    _manual_ok(draft, spec)
    r = MG.ensure(draft, spec, "final")
    assert r["status"] == "PASS", r["failures"]
    assert len(spec["cards"]) == 1 and spec["cards"][0]["t0"] == 0 and "Get yours" not in json.dumps(spec)
    assert os.path.exists(draft + ".PASS.json") and MG.require(draft)
    open(draft, "ab").write(b"\0")                                     # any change after PASS -> stale report -> refused
    with pytest.raises(MG.GateRefused): MG.require(draft)

def test_publish_refuses_repost_and_two_pages(tmp_path):
    draft, spec = _video(tmp_path)
    MG.ensure(draft, spec, "final"); _manual_ok(draft, spec); assert MG.ensure(draft, spec, "final")["status"] == "PASS"
    MG.register(draft, "V9", page="Jolly Glow", posted=True)
    spec.update(page="PatriotsGlow", caption='Wow 😍 SAY "MOM" for the link', approved_caption='Wow 😍 SAY "MOM" for the link', approval=dict(by="Omar", quote="post it"))
    assert any(f["rule"] == "MR19" for f in MG.run(draft, spec, "publish")["failures"])
    with pytest.raises(MG.GateRefused): MG.require(draft, "publish", spec)

def test_render_refuses_bad_plan():
    from hookforge import autoedit
    with pytest.raises(MG.GateRefused):
        autoedit.final_cmd({}, dict(shots=[], cards=[dict(text="a"), dict(text="b"), dict(text="c")], gens=[dict(id="H", role="hook", res="1080p", dur=4)]), "/tmp/x.mp4")

def test_planner_defaults_one_card():
    from hookforge import format_defaults as FD
    src = open(FD.__file__).read()
    tc = " ".join(re.findall(r"text_cards=\[[^\n]*?\]", src))
    assert "JK" not in tc and "Vs" not in tc and all(len(re.findall(r"\(", m)) <= 2 for m in re.findall(r"text_cards=\[[^\n]*?\]", src))
