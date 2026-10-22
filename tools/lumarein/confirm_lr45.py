import json,sys,hashlib
V=sys.argv[1];P=f'/workspace/hookforge/out/lumarein/lr45/{V}_clean.mp4';S=P+'.gate.json'
h=hashlib.sha256(open(P,'rb').read()).hexdigest();s=json.load(open(S))
BY="Grok Bot vision review 2026-10-22 11:30 AM PT"
common=dict(
MR08="Omar approved this build directly: make 2 POC'd barnglow videos and post them; frames reviewed before clips",
MR11="arena, pasture and barn shots read as handheld phone footage, realistic lighting",
MR12="no added grain or sharpening; bloom only on lit shots, trail pass fully off",
MR15="taping, tail swish, buckling and riding all move at natural speed; no frozen faces",
MR16="daytime failed duct-tape attempt, then dusk strap-on, then night rides: chronological",
MR20="adult women only, no casting by race, no minors",
MR22="duct-tape VS hook copied from LumaRein 2.6M reel 7698178513446128902 (idea / VS / result)",
MR24="not a 3-2-1 hook (then-vs-now duct tape VS), spec does not apply",
MR28="Seedance ambient at 0.22 under the original rock_that_body section from 22.2 s, no added SFX",
MR29="straight hard cuts between all shots; in-clip cut at 2 s trimmed around (segments end 1.9 / start 2.2)",
MR37="MR50 cards: The problem over the duct-tape fail, VS over strapping the kit on, The solution over glowing night rides",
MR51="horse arena, pasture and barn yard: places a horse light kit is actually used")
per={"LR4":dict(
MR13="flag on the post behind the arena fence 0-3.5 s and flags on the fence 5.3-9.5 s",
MR14="her hands touch the tape and leg band; she looks at the leg while taping; hooves land in sand, no phasing",
MR17="blue LED leg bands, headstall and Y breastplate like the refs; consistent blue in every lit shot",
MR23="from frame 0 she is wrapping duct tape and LED string on the leg; it peels off and drops by 2.5 s",
MR49="reviewed every lit shot 3.5-9.5 s frame by frame: LEDs bright with bloom, trail pass off, no light trails or streaks behind the horse"),
"LR5":dict(
MR13="large US flag on the red barn wall visible 0-3.5 s in the hook and lit on the barn at 7.5-9.5 s; the colour hint misses it under the card and night grade",
MR14="she watches the horse then facepalms; hands grip the breastplate buckle and remote; hooves stay planted in grass, no phasing",
MR17="LED breastplate and leg bands like the refs; red first then pink after the remote press shown in the VS shot, then pink stays consistent",
MR23="from frame 0 the tail swish is tearing the duct-taped lights loose and she reacts",
MR49="reviewed every lit shot frame by frame; rejected B2 0-2 s (fiber tail glow read as streaks) and rerolled B3; kept shots show sharp LEDs, trail pass off, no motion streaks; the dotted tail light in the leg close-up is the product, not a trail")}
s["confirm"]={k:dict(by=BY,note=v,sha256=h) for k,v in {**common,**per[V]}.items()}
json.dump(s,open(S,'w'),indent=1,ensure_ascii=False)
