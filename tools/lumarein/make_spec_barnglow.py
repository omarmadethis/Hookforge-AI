"""Generic Barn Glow gate-spec template (supersedes make_spec_lr6.py for new builds; LR6 files are frozen/posted).
    python3 tools/lumarein/make_spec_barnglow.py <config.json>
config.json: video_id, dir (abs out dir with <ID>_build.json incl. shot_t0 + cards), hook{format,first_second_action,conflict}, caption, say_keyword,
  song{key,path,in_s,reel_id}, spend{cap,spent}, n_pre (number of non-after shots before the 3 afters), pre_roles (list of roles for them),
  pre_gens (shot gen ids for them), after_gens (3 ids), swap{rider,horse1,glow1,horse2,glow2,beach,field,country} (characters/colours/settings only),
  settings{side,pov,two}, approval_quote, reference{assembly_s}, pre_prompts (one scene text per pre shot, hook/assembly/body; the MR58 phone-video suffix is appended),
  frame_prompts {gen_id: still scene text} (MR58 phone-photo suffix appended).
MR59: spend.upscale_credits (reserve 5 cr, provisional, Omar: <=5 cr/video; see upscale4k.UPSCALE_RESERVE_CREDITS) is counted against the cap; the final step after the gate is tools/lumarein/upscale_4k.py (Higgsfield 4K).
The 3 afters come from barnglow_afters.after_shots (MR53/55/56/57 fields + fast prompts), MR49 glow block and MR10 suffix are included."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from barnglow_afters import after_shots, phone_prompt, phone_still, NT
c = json.load(open(sys.argv[1])); D = c["dir"]; V = c["video_id"]; P = f"{D}/{V}_clean.mp4"
b = json.load(open(f"{D}/{V}_build.json")); t0 = b["shot_t0"]; n = len(c["pre_roles"])
assert len(t0) >= n + 4, "shot_t0 must hold n_pre + 3 after starts + end"
pre = [dict(gen=c["pre_gens"][i], t0=t0[i], t1=t0[i + 1], role=c["pre_roles"][i]) for i in range(n)]
afters = after_shots(t0[n:n + 3], t0[n + 3], c["after_gens"], settings=c.get("settings"), **c.get("swap", {}))
for sh_, tx in zip(pre, c["pre_prompts"]): sh_["prompt"] = phone_prompt(tx)       # MR58: hook / assembly / body prompts too
shots = pre + afters
# MR60 (Omar 2026-10-23): ALL videos generated with Kling 4.0 (Higgsfield id kling4_0), 1080p 9:16, 3-30 s (5 s is enough). Cost ESTIMATE ~1 cr/s (only data point: 10 cr for 10 s).
DEFAULT_MODEL, DEFAULT_RES, DEFAULT_DUR, KLING_CR_PER_S_EST = "kling4_0", "1080p", 5, 1.0
gens = [dict(id=g, role="hook" if g.endswith("_H") else "body", res=DEFAULT_RES, dur=DEFAULT_DUR, model=DEFAULT_MODEL, shots=[s["gen"] for s in shots if s["gen"].startswith(g)]) for g in dict.fromkeys(s["gen"].rstrip("ab") for s in shots)]
s = dict(video_id=V, kind="video", product="lumarein", page="Barn Glow", hook=dict(c["hook"], conflict_t_s=c["hook"].get("conflict_t_s", 0.5)), shots=shots,
 cards=[dict(text=k["text"], t0=k["t0"], t1=k["t1"], png=k["png"], scale=k["scale"], y=k.get("y"), scale_max=1.0, why="reference overlay", shows="hook then glowing afters") for k in b["cards"]],
 song=dict(key=c["song"]["key"], path=c["song"]["path"], in_s=float(c["song"]["in_s"]), start_t=0, loops=False, recreate_of=dict(slug="lumarein", reel_id=c["song"]["reel_id"])),
 gens=gens, frames=[dict(id=g["id"], model="gpt_image_2", refs=["refs/lumarein/product"], prompt=phone_still(c["frame_prompts"][g["id"]])) for g in gens],
 prompts=[x["prompt"] for x in shots], phone_look=dict(handheld=True, vertical=True, sensor_noise=True, imperfect_autofocus=True, imperfect_exposure=True, real_lighting=True, no_gimbal=True, no_ai_sheen=True, no_plastic_skin=True, no_3d_glow=True), spend=dict(cap=float(c["spend"]["cap"]), spent=float(c["spend"]["spent"]), upscale_credits=float(c["spend"].get("upscale_credits", 30))), upscale_4k=dict(required=True, rule="MR59", provider="bytedance", preset="ugc", resolution="4k", tool="tools/lumarein/upscale_4k.py"), frames_shown=True,
 own_globs=[f"out/lumarein/{os.path.basename(D)}/*", f"out/lumarein/{os.path.basename(D)}/*/*", f"out/lumarein/{os.path.basename(D)}/*/*/*"],
 edit=dict(body=f"{D}/{V}_body.mp4", body_gain=0.22, W=720, H=1280),
 glow=dict(trail_decay=0.0, trail_opacity=0.0, trail_blur=0, bloom=True, prompts=["LEDs glowing bright neon with bloom, " + NT]),   # MR49
 caption=c["caption"], approved_caption=c["caption"], say_keyword=c["say_keyword"], reference=c.get("reference", {}),
 approval=dict(by="Omar", quote=c["approval_quote"]), confirm={})
try: s["confirm"] = json.load(open(P + ".gate.json")).get("confirm", {})
except Exception: pass
json.dump(s, open(P + ".gate.json", "w"), indent=1, ensure_ascii=False)
print(P + ".gate.json")
