"""LR3 (MinionMask): POC of LumaRein TikTok 7697804641928498433 (171.6K, 'Send this to a Horse girlie').
MR49 subtle trail: bloom kept bright, LED trail lagfun decay 0.55 / gblur 4 mixed at 12% opacity. Zero metadata.
Own files only: out/lumarein/lr3/*, out/lumarein/frames3/*."""
import json, os, subprocess, sys
R = "/workspace/hookforge"; C = f"{R}/out/lumarein/lr3"; O = C
sys.path.insert(0, f"{R}/style"); sys.path.insert(0, f"{R}/engine")
from hookforge.card_count import enforce
from hookforge import emoji_gate, original_song
GLOW_SPEC = dict(trail_decay=0.55, trail_opacity=0.12, trail_blur=4, bloom=True)
GLOW_SUBTLE = ("[v]format=gbrp,split=3[a][b][c];[a]eq=brightness=-0.04:saturation=1.3:gamma=0.92,format=gbrp[base];"
        "[c]curves=all='0/0 0.55/0 1/1',eq=saturation=1.6,gblur=sigma=7,format=gbrp[bloom];"
        f"[b]curves=all='0/0 0.62/0 0.85/0.6 1/1',lagfun=decay={GLOW_SPEC['trail_decay']},gblur=sigma={GLOW_SPEC['trail_blur']},"
        f"colorchannelmixer=rr={GLOW_SPEC['trail_opacity']}:gg={GLOW_SPEC['trail_opacity']}:bb={GLOW_SPEC['trail_opacity']},format=gbrp[trail];"
        "[base][bloom]blend=all_mode=screen[x];[x][trail]blend=all_mode=screen,format=yuv420p[o]")
SONG = (f"{R}/music/hey_baby_pitbull.m4a", 44.07); SONG_KEY = "hey_baby_pitbull"; REEL = "7697804641928498433"
SHOTS = json.load(open(f"{C}/shots.json"))   # [[gen, a, b, lit], ...]
CARDS = [("Send this to a Horse girlie 🙈✨", 0)]; FMT = "audience-callout"
def build():
    sg = original_song.gate(dict(recreate_of=dict(slug="lumarein", reel_id=REEL), song_key=SONG_KEY, song_in_s=SONG[1], song_start_t=0, song_loops=False))
    assert not sg, sg
    enforce([{"text": t} for t, _ in CARDS], FMT); segs = []
    for i, (g, a, b, lit) in enumerate(SHOTS):
        s = f"{O}/LR3_s{i}.mp4"
        vf = f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS,scale=720:1280,fps=30,format=yuv420p[v];" + (GLOW_SUBTLE if lit else "[v]null[o]")
        subprocess.run(["ffmpeg","-y","-loglevel","error","-i",f"{C}/{g}.mp4","-filter_complex",vf+f";[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS[aa]",
                        "-map","[o]","-map","[aa]","-c:v","libx264","-crf","16","-c:a","aac","-ar","48000",s], check=True); segs.append((s, b - a))
    t0s = [0.0]
    for _, d in segs: t0s.append(t0s[-1] + d)
    dur = t0s[-1]
    lst = f"{O}/LR3_list.txt"; open(lst, "w").write("".join(f"file '{s}'\n" for s, _ in segs))
    body = f"{O}/LR3_body.mp4"; subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",lst,"-c","copy",body], check=True)
    ins = ["-i", body, "-ss", str(SONG[1]), "-i", SONG[0]]; f = []; last = "0:v"; pngs = []
    from hookforge import textcards as TC
    for j, (t, si) in enumerate(CARDS):
        png = f"{O}/LR3_card{j}.png"; sc = TC.fit_card(t, 1.0); assert TC.caption_lines_gate([(t, sc)])["ok"]; emoji_gate.render(t, 720, 1280, png, scale=sc); ins += ["-loop","1","-t",str(dur),"-i",png]
        a = t0s[si]; b = t0s[CARDS[j+1][1]] if j + 1 < len(CARDS) else dur; pngs.append(dict(text=t, t0=round(a,3), t1=round(b,3), png=png, scale=sc))
        f.append(f"[{last}][{j+2}:v]overlay=0:0:enable='between(t,{a:.3f},{b - 0.001:.3f})'[c{j}]"); last = f"c{j}"
    f.append(f"[1:a]atrim=0:{dur},afade=t=out:st={dur-0.4}:d=0.4,volume=1.0[m];[0:a]volume=0.22[n];[m][n]amix=inputs=2:normalize=0[au]")
    out = f"{O}/LR3_final.mp4"
    subprocess.run(["ffmpeg","-y","-loglevel","error",*ins,"-filter_complex",";".join(f),"-map",f"[{last}]","-map","[au]","-t",str(dur),
                    "-c:v","libx264","-crf","17","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-map_metadata","-1","-map_chapters","-1",
                    "-fflags","+bitexact","-flags:v","+bitexact","-flags:a","+bitexact","-metadata","encoder=","-movflags","+faststart",out], check=True)
    from hookforge import deliver
    clean = f"{O}/LR3_clean.mp4"; deliver.sanitize(out, clean); assert not deliver.scan(clean), deliver.scan(clean)
    return dict(out=clean, dur=round(dur, 2), shot_t0=[round(x, 2) for x in t0s], cards=pngs, glow=GLOW_SPEC)
if __name__ == "__main__": print(json.dumps(build(), indent=1, ensure_ascii=False))
