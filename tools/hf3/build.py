"""hf3 (2026-10-21 PT): PV4 PurrVentures (RollyMew DeSyZivMTz- recreation) + TG4/TG5 TrumpGlow. Cut, cards (Apple emoji), song frame 0, zero metadata, gate spec."""
import json, os, subprocess, sys
R = "/workspace/hookforge"; C = f"{R}/out/hf3/clips"; O = f"{R}/out/hf3/final"; os.makedirs(O, exist_ok=True)
sys.path.insert(0, f"{R}/engine")
from hookforge.card_count import enforce
from hookforge import emoji_gate, original_song, textcards as TC, deliver
V = json.load(open(f"{R}/tools/hf3/plan.json"))
def build(k):
    v = V[k]; s = v["song"]
    if s.get("recreate_of"):
        sg = original_song.gate(dict(recreate_of=s["recreate_of"], song_key=s["key"], song_in_s=s["in_s"], song_start_t=0, song_loops=False)); assert not sg, sg
    enforce([{"text": c["text"]} for c in v["cards"]], v["hook"]["format"]); segs = []
    for i, (g, a, b, role) in enumerate(v["shots"]):
        sp = f"{O}/{k}_s{i}.mp4"
        subprocess.run(["ffmpeg","-y","-loglevel","error","-i",f"{C}/{g}.mp4","-filter_complex",
            f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS,scale=720:1280,fps=30,format=yuv420p[o];[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS[aa]",
            "-map","[o]","-map","[aa]","-c:v","libx264","-crf","16","-c:a","aac","-ar","48000",sp], check=True); segs.append((sp, b - a))
    t0s = [0.0]
    for _, d in segs: t0s.append(round(t0s[-1] + d, 3))
    dur = t0s[-1]; lst = f"{O}/{k}_list.txt"; open(lst, "w").write("".join(f"file '{p}'\n" for p, _ in segs))
    body = f"{O}/{k}_body.mp4"; subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",lst,"-c","copy",body], check=True)
    ins = ["-i", body, "-ss", str(s["in_s"]), "-i", f"{R}/{s['path']}"]; f = []; last = "0:v"; cards = []
    for j, c in enumerate(v["cards"]):
        png = f"{O}/{k}_card{j}.png"; sc = TC.fit_card(c["text"], 1.0); assert TC.caption_lines_gate([(c["text"], sc)])["ok"]
        emoji_gate.render(c["text"], 720, 1280, png, scale=sc); ins += ["-loop","1","-t",str(dur),"-i",png]
        a = t0s[c["shot"]]; b = t0s[v["cards"][j+1]["shot"]] if j + 1 < len(v["cards"]) else dur
        f.append(f"[{last}][{j+2}:v]overlay=0:0:enable='between(t,{a:.3f},{b - 0.001:.3f})'[c{j}]"); last = f"c{j}"
        cards.append(dict(text=c["text"], t0=a, t1=b, png=png, why=c["why"], shows=c["shows"], scale=sc, scale_max=1.0))
    f.append(f"[1:a]atrim=0:{dur},afade=t=out:st={dur-0.4}:d=0.4,volume=1.0[m];[0:a]volume=0.22[n];[m][n]amix=inputs=2:normalize=0[au]")
    out = f"{O}/{k}_final.mp4"
    subprocess.run(["ffmpeg","-y","-loglevel","error",*ins,"-filter_complex",";".join(f),"-map",f"[{last}]","-map","[au]","-t",str(dur),
        "-c:v","libx264","-crf","17","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-map_metadata","-1","-map_chapters","-1",
        "-fflags","+bitexact","-flags:v","+bitexact","-flags:a","+bitexact","-metadata","encoder=","-movflags","+faststart",out], check=True)
    clean = f"{O}/{k}_gate.mp4"; deliver.sanitize(out, clean); assert not deliver.scan(clean), deliver.scan(clean)
    shots = [dict(gen=f"{g}{'ab'[0] if False else ''}", t0=t0s[i], t1=t0s[i+1], role=role) for i, (g, a, b, role) in enumerate(v["shots"])]
    for i, sh in enumerate(shots): sh["gen"] = f"{v['shots'][i][0]}_{i}"
    gens = [dict(id=g, role=("hook" if g.endswith("_H") else "body"), res="720p", dur=4, model="seedance_2_5", shots=(["H"] if g.endswith("_H") else ["a","b"])) for g in v["gens"]]
    spec = dict(video_id=k, kind="video", product=v["product"], page=v["page"], hook=v["hook"], shots=shots, cards=cards,
        song=dict(key=s["key"], path=s["path"], in_s=s["in_s"], start_t=0, loops=False, **({"recreate_of": s["recreate_of"]} if s.get("recreate_of") else {})),
        gens=gens, frames=[dict(id=g, model="gpt_image_2", refs=v["refs"]) for g in v["gens"]],
        prompts=["...shot on iphone 12, no warm lighting, no blur, nothing cinematic"], spend=dict(cap=600, spent=v["spent"]), frames_shown=True,
        own_globs=[f"out/hf3/clips/{g}*" for g in v["gens"]] + [f"out/hf3/final/{k}_*", f"out/hf3/final/.mg_{k}*"],
        edit=dict(body=body, body_gain=0.22, W=720, H=1280), regen=dict(cap_remaining=v.get("cap_remaining", 0), cost_per_clip=28, approved_by="Omar", runner=None),
        caption=v["caption"], approved_caption=v["caption"], approved_cards=[c["text"] for c in v["cards"]], say_keyword=v["say"],
        approval=dict(by="Omar", quote="make a POC'd purrventures video and post it on this page. Make 2 POC'd trumpglow videos and post them on 1 page each ... dont ask me for any approvals just get it done"),
        poc=v["poc"])
    old = f"{clean}.gate.json"
    if os.path.exists(old): spec["confirm"] = json.load(open(old)).get("confirm", {})
    json.dump(spec, open(old, "w"), indent=1, ensure_ascii=False)
    return dict(out=clean, dur=dur, t0s=t0s)
if __name__ == "__main__":
    print(json.dumps({k: build(k) for k in (sys.argv[1:] or V)}, indent=1))
