import json,hashlib
P='/workspace/hookforge/out/lumarein/lr6/LR6_clean.mp4';S=P+'.gate.json'
h=hashlib.sha256(open(P,'rb').read()).hexdigest();s=json.load(open(S))
BY="Grok Bot vision review 2026-10-22 6:20 PM PT"
c=dict(
MR08="Omar approved this build directly: build LR6 as a replica; start frames inspected before any clip spend",
MR11="tack shop, stable, barn yard, beach and pasture read as handheld phone footage and cinematic afters, realistic lighting",
MR12="no added grain or sharpening; bloom only on lit shots, trail pass fully off",
MR13="large US flag on the tack shop wall 0-2.5 s, flag on the driftwood post at the beach, and flag on the red barn in the pasture and hills shots",
MR14="she looks off-camera then points at the endcap; hands touch strap, band and remote; hooves land on sand and grass, no phasing",
MR15="walk, gasp, point, whip-pan, wrapping, riding all move at natural speed; no frozen faces",
MR16="day tack shop, dusk stable and barn yard, then night beach, dusk pasture and sunset hills: same order as the reference",
MR17="blue Lumarein Y chest strap, leg bands, tail light and round remote like the product refs; boxes and kit on the endcap match; lit colours consistent per shot",
MR20="adult women only, no casting by race, no minors",
MR22="hook and whole edit replicate Omar's supplied reference reel 2588845368227613 (tack shop gasp, endcap whip-pan, kit assembly, remote, glowing afters)",
MR23="she is striding in with the drink from frame 0 and reacts within 1.5 s; the reference opens the same way",
MR24="not a 3-2-1 hook (audience callout meme), spec does not apply",
MR28="Seedance ambient at 0.22 under the original hey_baby_pitbull section, no added SFX",
MR29="straight hard cuts between all shots; in-clip cuts trimmed around; only a camera whip-pan inside the hook, no fades",
MR37="meme caption over a woman discovering a stack of glow kits then glowing horses, same joke as the reference",
MR49="reviewed every lit shot frame by frame: LEDs bright with bloom, trail pass off, no light trails or streaks behind the horses; the dotted tail strands are the product",
MR51="human-only in the tack shop; horses only in stable, barn yard, beach and pasture",
MR53="the last after shot shows two galloping horses both wearing glowing green and blue gear",
MR56="exactly three back-to-back cinematic afters: beach gallop, barn pasture gallop, two riders on farm hills with a barn")
s["confirm"]={k:dict(by=BY,note=v,sha256=h) for k,v in c.items()}
json.dump(s,open(S,'w'),indent=1,ensure_ascii=False)
