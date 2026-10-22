import json,sys,subprocess
R='/workspace/hookforge'; V=sys.argv[1]; D=f'{R}/out/lumarein/lr45'; P=f'{D}/{V}_clean.mp4'
b=json.loads(open(f'{D}/{V}_build.json').read()); sh=json.load(open(f'{D}/{V}_shots.json')); t0=b['shot_t0']
roles=["hook","vs"]+["after"]*(len(sh)-2)
NT="no light trails, no motion streaks, no long-exposure effect"
H={"LR4":dict(first_second_action="rider crouches duct-taping a white LED string around a chestnut's front leg; the tape peels off and the lights flop into the sand",
   conflict="the makeshift duct-tape light job falls apart on the leg",page="Barn Glow",
   cap="DON'T show this to an Equestrian 😳🏇🇺🇸\nSAY \"GLOW\" and we'll send you the link\n#equestrian #horsegirl #horses",kw="GLOW",
   quote="make 2 POC'd barnglow videos, upload 1 to the barnglow page and 1 to the minion mask page"),
   "LR5":dict(first_second_action="a dapple grey swishes its tail and rips off duct-taped Christmas lights while the rider facepalms by the red barn",
   conflict="the tail tears the duct-taped lights off and she facepalms",page="MinionMask",
   cap="Every Equestrian needs this for night rides 😍🐴🇺🇸\nSAY \"SHINE\" and we'll send you the link\n#equestrianlife #horselove #barnlife",kw="SHINE",
   quote="make 2 POC'd barnglow videos, upload 1 to the barnglow page and 1 to the minion mask page")}[V]
gens=sorted({g for g,*_ in sh})
seen={};sg=[]
for g,*_ in sh:
    n=seen.get(g,0);seen[g]=n+1;sg.append(g if g.endswith("_H") else g+"ab"[n])
s=dict(video_id=V,kind="video",product="lumarein",page=H["page"],
 hook=dict(format="then-vs-now",first_second_action=H["first_second_action"],conflict=H["conflict"],conflict_t_s=0.5),
 shots=[dict(gen=sg[i],t0=t0[i],t1=t0[i+1],role=roles[i]) for i in range(len(sh))],
 cards=[dict(text=c["text"],t0=c["t0"],t1=c["t1"],png=c["png"],scale=c["scale"],scale_max=1.0,
   why="MR50 problem / VS / solution cards on the 2.6M duct-tape VS structure",shows="duct tape lights vs LED kit strapped on then glowing ride") for c in b["cards"]],
 song=dict(key="rock_that_body",path="music/rock_that_body_bep.m4a",in_s=22.2,start_t=0,loops=False,recreate_of=dict(slug="lumarein",reel_id="7698178513446128902")),
 gens=[dict(id=g,role="hook" if g.endswith("_H") else "body",res="720p",dur=4,model="seedance_2_5",shots=[x for x in sg if x.startswith(g)]) for g in gens],
 frames=[dict(id=g,model="gpt_image_2",refs=["refs/lumarein/product"]) for g in gens],
 prompts=["...shot on iphone, realistic, "+NT],
 spend=dict(cap=300,spent=float(sys.argv[2])),frames_shown=True,
 own_globs=["out/lumarein/lr45/*"],
 edit=dict(body=f"{D}/{V}_body.mp4",body_gain=0.22,W=720,H=1280),
 regen=dict(cap_remaining=300-float(sys.argv[2]),cost_per_clip=28,approved_by="Omar",runner=None,note="parent cap 300 credits"),
 glow=dict(trail_decay=0.0,trail_opacity=0.0,trail_blur=0,bloom=True,prompts=["LEDs glowing bright neon with bloom, "+NT]),
 caption=H["cap"],approved_caption=H["cap"],say_keyword=H["kw"],
 approval=dict(by="Omar",quote=H["quote"]),confirm={})
try: s["confirm"]=json.load(open(P+'.gate.json')).get("confirm",{})
except Exception: pass
for g in s["gens"]:
    if g["id"]=="LR5_B2": g["shots"]=["LR5_B2a (generated, rejected: fiber tail glow read as streaks)","LR5_B2b"]
for x in s["shots"]:
    if x["gen"]=="LR5_B2a": x["gen"]="LR5_B2b"
json.dump(s,open(P+'.gate.json','w'),indent=1,ensure_ascii=False)
