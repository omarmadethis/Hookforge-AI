"""LumaRein LR1/LR2 edit: cut clips, free LED bloom + LED-only light-trail pass on lit shots, D188 cards, song from frame 0, zero metadata."""
import json, os, subprocess, sys
R = "/workspace/hookforge"; C = f"{R}/out/lumarein/clips"; O = f"{R}/out/lumarein/final"; os.makedirs(O, exist_ok=True)
sys.path.insert(0, f"{R}/style"); sys.path.insert(0, f"{R}/engine"); import render_text
from hookforge.card_count import enforce
GLOW = ("[v]format=gbrp,split=3[a][b][c];[a]eq=brightness=-0.05:saturation=1.3:gamma=0.92,format=gbrp[base];"
        "[b]curves=all='0/0 0.62/0 0.85/0.6 1/1',lagfun=decay=0.90,gblur=sigma=14,format=gbrp[trail];"
        "[c]curves=all='0/0 0.55/0 1/1',eq=saturation=1.6,gblur=sigma=7,format=gbrp[bloom];"
        "[base][bloom]blend=all_mode=screen[x];[x][trail]blend=all_mode=screen,format=yuv420p[o]")
V = {
 "LR1": dict(song=(f"{R}/music/hey_baby_djotzi.m4a", 17.9),
   shots=[("LR1_H",0.0,4.0,0),("LR1_B1",1.0,2.5,0),("LR1_B1",2.7,4.0,0),("LR1_B2",0.2,1.7,1),("LR1_B2",1.8,3.3,1),("LR1_B3",0.6,2.1,1),("LR1_B3",2.5,4.0,1)],
   cards=[("The idea... 😭💡",0),("The result 😍🙈",4)], fmt="then-vs-now"),
 "LR2": dict(song=(f"{R}/music/mambo_no5_youtube.m4a", 0.0),
   shots=[("LR2_H",0.0,4.0,0),("LR2_B1",0.0,1.5,0),("LR2_B1",2.0,3.5,0),("LR2_B2",0.1,1.6,0),("LR2_B2",2.4,3.9,1),("LR2_B3",0.2,1.7,1),("LR2_B3",2.1,3.6,1)],
   cards=[("Do NOT show this to an equestrian... 😏",0)], fmt="dont-show-recipient"),
}
def build(k):
    v = V[k]; enforce([{"text": t} for t, _ in v["cards"]], v["fmt"]); segs = []
    for i, (g, a, b, lit) in enumerate(v["shots"]):
        s = f"{O}/{k}_s{i}.mp4"
        vf = f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS,scale=720:1280,fps=30,format=yuv420p[v];" + (GLOW if lit else "[v]null[o]")
        subprocess.run(["ffmpeg","-y","-loglevel","error","-i",f"{C}/{g}.mp4","-filter_complex",vf+f";[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS[aa]",
                        "-map","[o]","-map","[aa]","-c:v","libx264","-crf","16","-c:a","aac","-ar","48000",s], check=True); segs.append((s, b - a))
    t0s = [0.0]
    for _, d in segs: t0s.append(t0s[-1] + d)
    dur = t0s[-1]
    lst = f"{O}/{k}_list.txt"; open(lst, "w").write("".join(f"file '{s}'\n" for s, _ in segs))
    body = f"{O}/{k}_body.mp4"; subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",lst,"-c","copy",body], check=True)
    ins = ["-i", body, "-ss", str(v["song"][1]), "-i", v["song"][0]]; f = []; last = "0:v"
    for j, (t, si) in enumerate(v["cards"]):
        png = f"{O}/{k}_card{j}.png"; render_text.render_card(t, 720, 1280).save(png); ins += ["-loop","1","-t",str(dur),"-i",png]
        a = t0s[si]; b = t0s[v["cards"][j+1][1]] if j + 1 < len(v["cards"]) else dur
        f.append(f"[{last}][{j+2}:v]overlay=0:0:enable='between(t,{a:.3f},{b - 0.001:.3f})'[c{j}]"); last = f"c{j}"
    f.append(f"[1:a]atrim=0:{dur},afade=t=out:st={dur-0.4}:d=0.4,volume=1.0[m];[0:a]volume=0.22[n];[m][n]amix=inputs=2:normalize=0[au]")
    out = f"{O}/{k}_final.mp4"
    subprocess.run(["ffmpeg","-y","-loglevel","error",*ins,"-filter_complex",";".join(f),"-map",f"[{last}]","-map","[au]","-t",str(dur),
                    "-c:v","libx264","-crf","17","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-map_metadata","-1","-map_chapters","-1",
                    "-fflags","+bitexact","-flags:v","+bitexact","-flags:a","+bitexact","-metadata","encoder=","-movflags","+faststart",out], check=True)
    from hookforge import deliver
    clean = out.replace("_final.mp4", "_clean.mp4"); deliver.sanitize(out, clean); assert not deliver.scan(clean), deliver.scan(clean)
    return dict(out=clean, dur=round(dur, 2), shot_t0=[round(x, 2) for x in t0s])
if __name__ == "__main__":
    print(json.dumps({k: build(k) for k in (sys.argv[1:] or V)}, indent=1))
