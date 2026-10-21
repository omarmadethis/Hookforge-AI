"""D61: recreate default, LOGIC lint, card rule, audio off, Apple emoji. Run: PYTHONPATH=engine python3 engine/tests/test_recreate_logic.py"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from hookforge import planner, logic, textcards, config, recreate_mode
F = []
def ok(n, c):
    print(("PASS " if c else "FAIL ") + n); (None if c else F.append(n))
p = planner.plan("then vs now video for MerryGlow tree lights")
ok("recreate is default for merryglow", p.get("mode") == "recreate")
ok("recreate plan passes LOGIC + failure memory + prompt checks", p["checks"]["ok"])
ok("then-cards == problem scenes", textcards.check_cards(p["text_cards"], p["problem_scenes"]) == [])
ok("2 then-cards for 1 problem scene is caught", textcards.check_cards([dict(text="Christmas 2024.. 😬", scale=1.0), dict(text="And Christmas 2025.. 🤕", scale=1.0), dict(text="Vs... ⏰", scale=1.0)], [[0, 4]]) != [])
ok("D63 generate_audio on + natural ambient line", config.LIVE["video"]["generate_audio"] is True and all(g["generate_audio"] is True and "Natural ambient sound only" in g["prompt"] for g in p["gens"]))
ok("camera stare caught", any(r["rule"] == "LG1" for r in logic.lint_prompt("The family sits on the couch looking at the camera. Natural ambient sound only, no added sound effects, no music.")))
ok("fake SFX / inserted YAY caught", any(r["rule"] == "LG3" for r in logic.lint_prompt("He yells YAY, cartoon whoosh. Natural ambient sound only: real voices, no added sound effects, no music.")))
ok("real cheering/gasps allowed", not any(r["rule"] == "LG3" for r in logic.lint_prompt("The kids gasp and cheer as the lights come on. Natural ambient sound only: real voices and action sounds that match what happens on screen, no added sound effects, no music.", "video", dict(people=False))))
ok("static after caught", any(r["rule"] == "LG4" for r in logic.lint_prompt("The tree is lit. Natural ambient sound only, no added sound effects, no music.", "video", dict(role="after"))))
ok("afters distinct", len({frozenset(logic.designs(s["animation"])) for s in p["shots"] if s["role"] == "after"}) == 3)
ok("apple emoji png exists", os.path.exists(textcards.apple_png("🤩")))
ok("install = ladder drop + slow unfold", "ladder" in p["gens"][2]["start_frame"]["prompt"] and "unfolds slowly" in p["gens"][2]["prompt"])
print("FAILS:", F or "none"); sys.exit(1 if F else 0)
