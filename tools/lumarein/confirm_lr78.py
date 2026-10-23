"""Reviewer confirm entries for LR7/LR8 (bound to the file sha256). Usage: confirm_lr78.py LR7|LR8"""
import json, hashlib, sys
V = sys.argv[1]
P = f'/workspace/hookforge/out/lumarein/lr78/{V}_clean.mp4'; S = P + '.gate.json'
h = hashlib.sha256(open(P, 'rb').read()).hexdigest(); s = json.load(open(S))
BY = "Grok Bot vision review 2026-10-23 PT (frames inspected one by one)"
COMMON = dict(
MR08="Omar approved building LR7 and LR8 as replicas of the LumaRein reels with a per-video credit cap; start frames were generated and inspected before any clip spend",
MR12="no added grain or sharpening in the grade; GLOW_SUBTLE bloom only on lit shots",
MR20="adult women only, no casting by race, no minors",
MR28="Seedance ambient audio at 0.22 under the original song section, no added SFX",
MR29="straight hard cuts only, no fades; in-clip cuts of the generations are trimmed around, each shot is a separate clean take",
MR49="reviewed every lit shot frame by frame: LEDs bright with bloom, trail pass off, no light trails or streaks behind the horses",
)
C = {
"LR7": dict(COMMON,
MR11="arena, VS leg-band close-up and remote shots, beach and field afters read as handheld iPhone footage, realistic lighting",
MR13="US flag on the fence in the hook, on the flag pole behind the white fence in the VS result shot",
MR14="she kneels and winds lights around the leg while the horse shifts; hands fasten the velcro band and press the remote; hooves land on sand/grass, no phasing",
MR15="winding, fastening, pressing the remote and the gallops all move at natural speed; no frozen faces",
MR16="golden-hour arena, dusk fence, then night beach, night field and dusk countryside: chronological, same order as the reference",
MR17="black Y chest strap, black velcro leg bands with grey strip and round black remote match the product refs; lit electric blue in the VS result and the afters",
MR22="whole edit replicates the 553.5K LumaRein reel 7699551558337416468 (concept / VS / product, Rock That Body section); only horse, rider and surface details differ",
MR23="in the first second she is already kneeling and winding tangled string lights and tape around the horse's leg while it shifts",
MR24="not a 3-2-1 hook (concept / VS format), spec does not apply",
MR37="'The idea...' over the homemade string-lights hack, 'VS...' over the leg band fastening and kit lighting up, 'The solution' on the glowing gallops: same joke as the reference",
MR51="arena, fence, beach, field: all places a horse and rider actually are",
MR53="the last after shot shows two galloping horses (blue and green kit), plus a green rider ahead in the POV shot",
MR56="exactly three fast back-to-back afters: beach side-tracking gallop, rider POV gallop, two-horse blue and green countryside tracking shot",
MR57="1 beach side-tracking, 2 first-person rider POV (neck, mane, ears, no hands or reins, green rider ahead), 3 two horses blue+green. Honest note: the third shot is a wide mid-height tracking shot, not strictly top-down high",
MR58="all clips are Seedance iPhone-look generations with phone-look prompts; they read as handheld phone video, not polished 3D"),
"LR8": dict(COMMON,
MR11="stable yard, arena, VS leg-band and remote shots and afters read as handheld iPhone footage in realistic light",
MR13="US flag on the pole over the barn in the hook, on the red barn in the VS result shot, and on the beach post in the afters",
MR14="two women react and point off-camera, hands fasten the velcro band and hold the remote, hooves land on sand/grass, no phasing",
MR15="gasping, pointing, fastening, remote press and gallops all move at natural speed",
MR16="dusk stable yard hook, dusk barn arena VS, then night beach, night field and dusk countryside afters: chronological, same order as the reference",
MR17="black Y chest strap, black velcro leg bands with grey strip and round remote match the product refs; lit electric blue in the VS result and in the afters",
MR22="replicates the 120K LumaRein reel 7699507305489976596 ('Do NOT let an equestrian see this', Hey Baby section): reaction-only hook, kit assembly, glowing afters",
MR23="two riders in helmets are mid-gasp and pointing at something off camera from frame 0, as in the reference",
MR24="not a 3-2-1 hook (audience callout meme), spec does not apply",
MR37="'Do NOT let an equestrian see this' over riders reacting to something, then the kit assembly and glowing horses: same meme logic as the reference. Honest note: the hook is reaction-only, no product shown, as in the reference",
MR51="stable yard, barn arena, beach, field: all real horse places",
MR53="the last after shot shows two galloping horses (dapple grey blue and bay green)",
MR56="exactly three fast back-to-back afters: beach side-tracking gallop, rider POV gallop, two-horse blue and green countryside tracking shot",
MR57="1 beach side-tracking, 2 first-person rider POV (neck, mane, ears, no hands or reins), 3 two horses blue+green. Honest note: the third shot is a wide dusk tracking shot, not strictly top-down high",
MR58="all clips are Seedance iPhone-look generations with phone-look prompts; they read as handheld phone video"),
}[V]
s["confirm"] = {k: dict(by=BY, note=v, sha256=h) for k, v in C.items()}
json.dump(s, open(S, 'w'), indent=1, ensure_ascii=False)
print("confirmed", V, len(C))
