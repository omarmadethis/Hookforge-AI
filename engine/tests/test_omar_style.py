"""D74 Omar style defaults + edit-vs-Omar QA. Run: PYTHONPATH=engine python3 engine/tests/test_omar_style.py"""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from hookforge import omar_style as O, edit_rules as E
F = []
def ok(n, c):
    print(("PASS " if c else "FAIL ") + n); (None if c else F.append(n))
S = O.style()
ok("style.json loads with timing/text/audio", all(k in S for k in ("timing", "text", "audio", "speed")))
ok("max 2 text rows", S["text"]["max_lines"] == 2)
ok("hook that fits stays 1.0x", O.hook_speed(3.0, 4.1)["speed"] == 1.0)
h = O.hook_speed(4.8, 4.1); ok("4.8 s hook -> 1.2x (speed up, never cut)", h["speed"] == 1.2 and h["fits"])
ok("too-long hook caps at 1.5x and flags", O.hook_speed(9.0, 4.1) == dict(speed=1.5, fits=False, out_s=6.0))
g = O.dialogue_gain_db(clip_lufs=-24.0, song_lufs=-11.0); ok("dialogue sits +8 LU over song", g["clip_gain_db"] == 21.0 - 1.0 and g["song_gain_db"] == -1.0)
ok("dialogue gain small when already loud", O.dialogue_gain_db(-2, -14)["clip_gain_db"] == -4.0)
ok("edit_rules picks up Omar target length", E.D["target_len_s"] == tuple(S["timing"]["total_range_s"]) and E.hook_fit is not None)
good = dict(dur=12.5, transitions=0, song=dict(onset_s=0.0), dialogue_minus_music_lu=8.0,
            shots=[dict(dur=2.4, speed=1.2, role="hook")] + [dict(dur=1.4) for _ in range(6)] + [dict(dur=1.9)],
            cards=[dict(text="POV: the whole street is\nJEALOUS.. 🤭🏠", t0=0, dur=12.5, lines=2, scale=0.8, y=0.2)])
r = O.compare(good); ok(f"Omar-like edit passes ({r['overall']})", r["ok"] and r["overall"] >= 90)
bad = json.loads(json.dumps(good)); bad["cards"][0].update(text="Get yours👉 jollyglow.com\nline two\nline three", lines=3)
bad["song"]["onset_s"] = 0.6; bad["dialogue_minus_music_lu"] = -3.0; bad["shots"][0]["dur"] = 6.5
rb = O.compare(bad); dims = {x["dim"] for x in rb["rows"] if x["level"] == "FAIL"}
ok("3 rows / link / late song / buried voices BLOCK", rb["level"] == "BLOCK" and {"text_lines", "onscreen_link", "song_t0", "dialogue"} <= dims)
ok("slow opener scores low", [x for x in rb["rows"] if x["dim"] == "opener"][0]["score"] < 60)
ok("slow-mo story shot FAILs", any(x["dim"] == "story_slowmo" for x in O.compare(dict(good, shots=good["shots"] + [dict(dur=1, speed=0.7)]))["rows"]))
lay = O.card_layout("Christmas moms, don't\nwalk RUN to Walmart 🤩"); ok(f"card_layout <=2 rows ({lay})", lay["ok"] and lay["lines"] <= 2)
print("FAILS:", F or "none"); sys.exit(1 if F else 0)
