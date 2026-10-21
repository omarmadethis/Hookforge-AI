"""EDIT_RULES.md editor defaults + lint. Run: PYTHONPATH=engine python3 engine/tests/test_edit_rules.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from hookforge import edit_rules as E, planner
F = []
def ok(n, c):
    print(("PASS " if c else "FAIL ") + n); (None if c else F.append(n))
tl = E.default_timeline([dict(id="H", dur=4), dict(id="B1", dur=4, role="box"), dict(id="B2", dur=4)])
ok("first clip keeps head", tl[0]["src_in"] == 0.0)
ok("later clips head 1.05 / tail 1.2", all(x["src_in"] >= 1.05 for x in tl[1:]) and max(x["src_out"] for x in tl if x["gen"] == "B2") == 2.8)
ok("each later gen split in 2 with 0.4 s gap", [x["gen"] for x in tl].count("B2") == 2 and round([x for x in tl if x["gen"] == "B2"][1]["src_in"] - [x for x in tl if x["gen"] == "B2"][0]["src_out"], 2) == 0.4)
ok("action beat sped 1.2x, others 1.0x", all(x["speed"] == 1.2 for x in tl if x["gen"] == "B1") and all(x["speed"] == 1.0 for x in tl if x["gen"] == "B2"))
base = dict(shots=[dict(code=f"S{i}", t0=i * 1.6, t1=(i + 1) * 1.6, gen=f"G{i//2}", trim=[0 if i == 0 else 1.05, 2], audio_gain=3.0 if i == 5 else 1.0) for i in range(10)],
            text_cards=[dict(text="a"), dict(text="Vs..."), dict(text="b")], music=dict(pick=dict(song="last_christmas", offset_s=170.5)), gens=[dict(id="G0", generate_audio=True)])
ok("clean timeline passes with no rows", E.lint(base)["rows"] == [])
z = dict(base, shots=[dict(base["shots"][0], scale=1.2)] + base["shots"][1:]); ok("zoom = FIX", not E.lint(z)["ok"])
s = dict(base, shots=base["shots"][:3] + [dict(base["shots"][3], speed=0.8)] + base["shots"][4:]); ok("slow-mo story shot = FIX", not E.lint(s)["ok"])
a = dict(base, gens=[dict(id="G0", generate_audio=False)]); ok("D63: generate_audio off = FIX (keep natural sound)", not E.lint(a)["ok"])
nb = dict(base, shots=[dict(s, audio_gain=1.0) for s in base["shots"]]); ok("D63: no key-sound boost warned", any(r["rule"] == "ER17" for r in E.lint(nb)["rows"]))
from hookforge import qa, prompts
ok("prompt audio line = natural ambient", "Natural ambient sound only" in prompts.silent("A man cuts paper.") and "Silent clip" not in prompts.silent("x. Silent clip: no dialogue, no voices, no sound effects, no music."))
ok("QA audio: transcript with inserted YAY / whoosh fails", not qa.audio_check(transcript="scissors snip, then a cartoon whoosh and YAY")["ok"])
ok("QA audio: real sounds pass", qa.audio_check(transcript="scissors snipping, tape tearing, man laughs, door thunk")["ok"])
ok("QA audio: prompt asking for SFX fails", not qa.audio_check(prompt="He opens the door, whoosh sound effect. Natural ambient sound only: real voices, no added sound effects, no music.")["ok"])
i = dict(base, music=dict(pick=dict(song="let_it_snow", offset_s=0.9))); ok("song at intro warned", any(r["rule"] == "ER15" for r in E.lint(i)["rows"]))
ok("holly jolly intro exception", not any(r["rule"] == "ER15" for r in E.lint(dict(base, music=dict(pick=dict(song="holly_jolly", offset_s=0.1))))["rows"]))
ok("1 card warned (3-card default)", any(r["rule"] == "ER11" for r in E.lint(dict(base, text_cards=[dict(text="x")]))["rows"]))
p = planner.plan("3-2-1 video for the grinch robe", mode="original"); ok("planner attaches edit defaults + lint", p["edit_defaults"] and "edit_lint" in p)
print("FAILS:", F or "none"); sys.exit(1 if F else 0)
