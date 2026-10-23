import json,sys,hashlib
R='/workspace/hookforge'; V='LR6'; D=f'{R}/out/lumarein/lr6'; P=f'{D}/LR6_clean.mp4'
b=json.load(open(f'{D}/LR6_build.json')); t0=b['shot_t0']
NT="no light trails, no motion streaks, no long-exposure effect"
CAP="Tell your equestrian bestie before her next night ride 🌙🐴🇺🇸\nSAY \"TWILIGHT\" and we'll send you the link\n#equestrian #horsegirl #nightride"
sg=["LR6_H","LR6_B1a","LR6_B1b","LR6_B2a","LR6_B2b","LR6_A1a","LR6_A1b","LR6_A2a"]
roles=["hook","body","body","body","body","after","after","after"]
extra={5:dict(horses=1,setting="beach",action="galloping"),6:dict(horses=1,setting="barn pasture",action="galloping"),7:dict(horses=2,setting="farm hills with barn",action="galloping")}
shots=[dict(gen=sg[i],t0=t0[i],t1=t0[i+1],role=roles[i],**extra.get(i,{})) for i in range(8)]
gens=[dict(id="LR6_H",role="hook",res="720p",dur=4,model="seedance_2_5",shots=["LR6_H"])]+[dict(id=g,role="body",res="720p",dur=4,model="seedance_2_5",shots=[g+"a",g+"b"]) for g in ("LR6_B1","LR6_B2","LR6_A1","LR6_A2")]
gens[-1]["shots"]=["LR6_A2a","LR6_A2b (generated spare, not used)"]
s=dict(video_id=V,kind="video",product="lumarein",page="Barn Glow",
 hook=dict(format="audience-callout",first_second_action="woman in a tack shop sips an iced latte, looks off to the side and gasps, then points as the camera whip-pans to a Lumarein endcap",conflict="she is shocked by the sight of a stack of glow kits and points at them",conflict_t_s=0.5),
 shots=shots,
 cards=[dict(text=c["text"],t0=c["t0"],t1=c["t1"],png=c["png"],scale=c["scale"],y=c["y"],scale_max=1.0,why="reference LR6 meme overlay held on screen for the whole reel; single card",shows="woman discovering glow kit endcap then glowing horses") for c in b["cards"]],
 song=dict(key="hey_baby_pitbull",path="music/hey_baby_pitbull.m4a",in_s=float(sys.argv[1]),start_t=0,loops=False,recreate_of=dict(slug="lumarein",reel_id="2588845368227613")),
 gens=gens,
 frames=[dict(id=g,model="gpt_image_2",refs=["refs/lumarein/product"]) for g in ("LR6_H","LR6_B1","LR6_B2","LR6_A1","LR6_A2")],
 prompts=["...shot on iphone, realistic, "+NT],
 spend=dict(cap=float(sys.argv[2]) if len(sys.argv)>2 else 150,spent=173.0),frames_shown=True,
 own_globs=["out/lumarein/lr6/*","out/lumarein/lr6/*/*","out/lumarein/lr6/*/*/*"],
 edit=dict(body=f"{D}/LR6_body.mp4",body_gain=0.22,W=720,H=1280),
 regen=dict(cap_remaining=0,cost_per_clip=28,approved_by="Omar",runner=None,note="LR6 cap about 150 credits; 173 used incl. one B2 reroll"),
 glow=dict(trail_decay=0.0,trail_opacity=0.0,trail_blur=0,bloom=True,prompts=["LEDs glowing bright neon with bloom, "+NT]),
 caption=CAP,approved_caption=CAP,say_keyword="TWILIGHT",
 reference=dict(assembly_s=3.1),
 approval=dict(by="Omar",quote="Build LR6 now as a PERFECT replica ... When it passes the gate, post it to Barn Glow (Buffer3) as an FB reel"),confirm={})
try: s["confirm"]=json.load(open(P+'.gate.json')).get("confirm",{})
except Exception: pass
json.dump(s,open(P+'.gate.json','w'),indent=1,ensure_ascii=False)
