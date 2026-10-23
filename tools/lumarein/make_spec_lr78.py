"""Spec maker for LR7 (Barn Glow) / LR8 (MinionMask): python3 make_spec_lr78.py LR7|LR8 <spent_credits>  (wraps make_spec_barnglow.py, then patches gens)."""
import json, os, subprocess, sys
R = "/workspace/hookforge"; D = f"{R}/out/lumarein/lr78"; V = sys.argv[1]; spent = float(sys.argv[2])
Q = "lets make a video to post on minion mask and barnglow please. both barnglow videos obviously. POC'd to the max, can you do research on lumiglows page or wahtever again?"
C = {
 "LR7": dict(page="Barn Glow", hook=dict(format="then-vs-now", first_second_action="young woman kneels beside a palomino winding tangled white string lights and duct tape around its front leg in a sand arena",
     conflict="the homemade string-light and tape job is a tangled mess on the horse"),
   caption="Skip the tangled string lights, your equestrian night rides deserve better 🌙🐴🇺🇸\nSAY \"IDEA\" and we'll send you the link\n#equestrian #horsegirl #nightride", say_keyword="IDEA",
   song=dict(key="rock_that_body", path="music/rock_that_body_bep.m4a", in_s=22.2, reel_id="7699551558337416468"), reference=dict(assembly_s=4.9),
   pre_gens=["LR7_H", "LR7_Ba", "LR7_Bb"], after_gens=["LR7_A1a", "LR7_A1b", "LR7_A2a"],
   swap=dict(rider="a rider in a black riding helmet", horse1="palomino horse", glow1="electric blue", horse2="black horse", glow2="neon green"),
   settings=dict(side="beach", pov="dark rolling field", two="twilight countryside"),
   pre_prompts=["handheld iPhone video at golden hour in a sand riding arena with a US flag on the fence, a young woman in a black riding helmet kneels beside a palomino horse awkwardly winding tangled plain white string lights and silver duct tape around its front leg, only homemade string lights and tape, no product anywhere in frame",
                "first-person POV close-up of two hands in light grey hoodie sleeves with a pink scrunchie fastening the black velcro LED leg band with a grey reflective strip around the front leg of a palomino horse, string lights softly blurred behind",
                "handheld wide shot at dusk of the palomino horse by a white wooden fence wearing the black Y chest strap and four leg bands, a hand in the foreground presses a small round black remote and the kit lights up bright electric blue with soft bloom, US flag on a pole behind the fence"],
   frame_prompts={"LR7_H": "outdoor sand riding arena at golden-hour dusk with a US flag on the fence, a young woman in a black riding helmet kneels beside a palomino horse winding tangled white string lights and silver duct tape around its front leg, only homemade lights and tape, no product anywhere in frame",
     "LR7_B": "first-person POV close-up, two hands in light grey sleeves fastening a black velcro LED leg band on a palomino horse's front leg",
     "LR7_A1": "side view at night on a beach, rider galloping a palomino horse in a glowing electric-blue LED kit with a US flag on a driftwood post",
     "LR7_A2": "high angle twilight countryside, palomino horse in blue LED kit and black horse in green LED kit galloping side by side, red barn with US flag"}),
 "LR8": dict(page="MinionMask", hook=dict(format="audience-callout", first_second_action="two women in riding helmets beside a black and a dapple grey horse gasp and point off-camera at dusk by a red barn with a US flag",
     conflict="they are stunned and gasp at something off-camera"),
   caption="Do NOT let an equestrian see this before her next night ride 👀🐴🇺🇸\nSAY \"GALLOP\" and we'll send you the link\n#equestrian #horsegirl #barnlife", say_keyword="GALLOP",
   song=dict(key="hey_baby_pitbull", path="music/hey_baby_pitbull.m4a", in_s=44.07, reel_id="7699507305489976596"), reference=dict(assembly_s=4.6),
   pre_gens=["LR8_H", "LR8_Ba", "LR8_Bb"], after_gens=["LR8_A1a", "LR8_A1b", "LR8_A2a"],
   swap=dict(rider="a rider in a black riding helmet", horse1="dapple grey horse", glow1="electric blue", horse2="bay horse", glow2="neon green"),
   settings=dict(side="beach", pov="dark rolling field", two="twilight countryside"),
   pre_prompts=["handheld iPhone video at blue-hour dusk in a farm paddock, two women in black riding helmets beside a black horse and a dapple grey horse gasp and point off-camera, red barn with a US flag behind them, no product anywhere in frame",
                "first-person POV close-up of two hands in mint green sleeves with a white scrunchie fastening the black velcro LED leg band with a grey reflective strip around the front leg of a dapple grey horse, stable string lights softly blurred behind",
                "handheld wide shot at dusk of the dapple grey horse by a white wooden fence wearing the black Y chest strap and four leg bands, a hand in the foreground presses a small round black remote and the kit lights up bright electric blue with soft bloom, large US flag on the red barn behind"],
   frame_prompts={"LR8_H": "blue-hour farm paddock, two women in black riding helmets with amazed open-mouth expressions beside a black horse and a dapple grey horse, red barn with a US flag, no product anywhere in frame",
     "LR8_B": "first-person POV close-up, two hands in mint green sleeves fastening a black velcro LED leg band on a dapple grey horse's front leg",
     "LR8_A1": "side view at night on a beach, rider galloping a dapple grey horse in a glowing electric-blue LED kit with a US flag on a driftwood post",
     "LR8_A2": "high angle twilight countryside, dapple grey horse in blue LED kit and bay horse in green LED kit galloping side by side, farmhouse with US flag"})}[V]
cfg = dict(video_id=V, dir=D, hook=C["hook"], caption=C["caption"], say_keyword=C["say_keyword"], song=C["song"], spend=dict(cap=160, spent=spent), n_pre=3,
           pre_roles=["hook", "vs", "vs"], pre_gens=C["pre_gens"], after_gens=C["after_gens"], swap=C["swap"], settings=C["settings"], approval_quote=Q,
           reference=C["reference"], pre_prompts=C["pre_prompts"], frame_prompts=C["frame_prompts"])
cp = f"{D}/{V}_spec_cfg.json"; json.dump(cfg, open(cp, "w"), indent=1, ensure_ascii=False)
subprocess.run([sys.executable, f"{R}/tools/lumarein/make_spec_barnglow.py", cp], check=True)
P = f"{D}/{V}_clean.mp4.gate.json"; s = json.load(open(P))
s["page"] = C["page"]
for g in s["gens"]:
    if g["id"] == f"{V}_B": g["dur"] = 5
    if g["id"] == f"{V}_A2": g["shots"] = [f"{V}_A2a", f"{V}_A2b (generated spare, not used)"]
s["regen"] = dict(cap_remaining=max(0, 160 - spent), cost_per_clip=28, approved_by="Omar", runner=None, note="LR7/LR8 cap ~160 credits per video (about 320 total) approved in chat pt409u")
json.dump(s, open(P, "w"), indent=1, ensure_ascii=False); print(P)
