"""D62 AUDIENCE-FIT stage. Run: PYTHONPATH=engine python3 engine/tests/test_audience_fit.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from hookforge import audience_fit as A, planner, gen_failures as GF
F = []
def ok(n, c):
    print(("PASS " if c else "FAIL ") + n); (None if c else F.append(n))
need = ["merryglow", "grinch_robe", "merryfire", "brickhood", "minionmask", "grinchmelt", "jollyglow", "purrventure", "patriotglow"]
ok("all 9 profiles exist + load", all(A.load(s)["slug"] == s for s in need))
ok("trumpglow alias -> patriotglow", A.slug_for("trumpglow") == "patriotglow" and A.load("patriotglow")["main_platform"] == "facebook")
ok("phonk globally banned (any product, even with evidence)", all(not A.check_song(s, dict(song="ESSE CARA (Super Slowed)", genre="phonk", in_point="0:00", tier="a", evidence=["https://x"]))["ok"] for s in need))
ok("song without evidence fails", not A.check_song("patriotglow", dict(song="Kid Rock American Bad Ass", genre="southern rock", in_point="0:00", tier="b", evidence=[]))["ok"])
ok("song without in-point fails", not A.check_song("patriotglow", dict(song="x", genre="southern rock", in_point="", tier="a", evidence=["https://x"]))["ok"])
ok("christmas song fails on brickhood (wrong niche)", not A.check_song("brickhood", dict(song="last_christmas", genre="christmas pop", in_point="2:50", tier="a", evidence=["own:x"]))["ok"])
slot = A.song_slot("patriotglow")
ok("TrumpGlow song slot filled from SONGS.md, tier a first", slot["status"] == "FILLED" and slot["pick"] and "Free Bird" in slot["pick"]["song"] and slot["pick"]["tier"] == "a")
ok("tier ordering a > b", [t for _, t, _ in slot["ranked"]][:2] == ["a", "b"] if len(slot["ranked"]) > 1 else True)
ok("android/noto render fails", not A.check_emoji("merryglow", "🤩", render="noto")["ok"])
ok("off-niche emoji fails (🎄 on TrumpGlow)", not A.check_emoji("patriotglow", "🎄")["ok"] and A.check_emoji("patriotglow", "🇺🇸")["ok"])
ok("UK spelling caption fails", not A.check_text("grinch_robe", "Every mum needs this 🎁")["ok"])
ok("unproven caption fails", not A.check_text("patriotglow", "Buy now cheap lights")["ok"])
tg = dict(product_key="patriotglow", mode="recreate", music=dict(audience_fit_song=slot["pick"]), caption=dict(text="Get yours 👉 {url} 🇺🇸", why="-"),
          text_cards=[dict(t=0, dur=3, text="Fake Trump Fans.. 🤢👎"), dict(t=3, dur=2, text="Vs... ⏳"), dict(t=5, dur=5, text="What We ACTUALLY Sell... 😎🇺🇸")])
r = A.check_plan(tg, log=False); ok("TrumpGlow cards + Free Bird pass", r["ok"])
bad = dict(tg, music=dict(audience_fit_song=dict(song="ESSE CARA (Super Slowed)", genre="phonk", in_point="0:00", tier="c", evidence=["https://www.tiktok.com/x"])))
ok("POST-MORTEM: reference-reel phonk on TrumpGlow fails", not A.check_plan(bad, log=False)["ok"])
p = planner.plan("3-2-1 video for the grinch robe", mode="original")
ok("planner runs AUDIENCE-FIT and passes grinch robe", p["audience_fit"]["ok"] and p["audience_fit"]["slug"] == "grinch_robe")
pm = planner.plan("then vs now video for MerryGlow tree lights")
ok("recreate checks include audience_fit", "audience_fit" in pm and pm["checks"]["ok"])
pm2 = dict(pm, text_cards=pm["text_cards"] + [dict(t=13, dur=1, text="Innit bruv 🇬🇧")])
from hookforge import recreate_mode
ok("linter: unproven card -> plan check FAIL (AF3/AF2)", not recreate_mode.check(pm2)["ok"] and any(x["rule"] in ("AF2", "AF3") for x in recreate_mode.check(pm2)["rows"]))
ok("failure memory has GF-AF1..3 and phonk prompt trips", {"GF-AF1", "GF-AF2", "GF-AF3"} <= {x["rule_id"] for x in GF.rules()} and not GF.lint("music: phonk drift edit")["ok"])
from hookforge import runner
import copy; q = copy.deepcopy(p); q["caption"] = dict(text="Every mum needs this", why="-")
ok("live gate refuses an AUDIENCE-FIT failure", any("AUDIENCE-FIT" in w for w in runner.check_gate(q, "af-test", live=True)[1]))
print("FAILS:", F or "none"); sys.exit(1 if F else 0)
