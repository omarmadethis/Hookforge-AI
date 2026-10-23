"""LR7 (Barn Glow) / LR8 (MinionMask): own variants of LumaRein TikTok reels 7699551558337416468 (553.5K, concept/VS/product, Rock That Body)
and 7699507305489976596 (120K, 'Do NOT let an equestrian see this', Hey Baby). MR49: no trail pass (bloom only). Zero metadata.
usage: build_lr78.py LR7|LR8   (reads out/lumarein/lr78/<V>_shots.json = [[gen, a, b, lit], ...]; own files only: out/lumarein/lr78/*)"""
import json, os, subprocess, sys
R = "/workspace/hookforge"; C = f"{R}/out/lumarein/lr78/clips"; O = f"{R}/out/lumarein/lr78"
sys.path.insert(0, f"{R}/style"); sys.path.insert(0, f"{R}/engine")
from hookforge.card_count import enforce
from hookforge import original_song
GLOW_SPEC = dict(trail_decay=0.0, trail_opacity=0.0, trail_blur=0, bloom=True)
GLOW_SUBTLE = ("[v]format=gbrp,split=3[a][b][c];[a]eq=brightness=-0.04:saturation=1.3:gamma=0.92,format=gbrp[base];"
        "[c]curves=all='0/0 0.55/0 1/1',eq=saturation=1.6,gblur=sigma=7,format=gbrp[bloom];"
        "[b]nullsink;[base][bloom]blend=all_mode=screen,format=yuv420p[o]")
CFG = dict(
  LR7=dict(song=(f"{R}/music/rock_that_body_bep.m4a", 22.2), key="rock_that_body", reel="7699551558337416468", fmt="then-vs-now", y=None,
           cards=[("The idea... 😅💡", 0), ("VS... 😳", 1), ("The solution 😍🐴", 3)]),
  LR8=dict(song=(f"{R}/music/hey_baby_pitbull.m4a", 44.07), key="hey_baby_pitbull", reel="7699507305489976596", fmt="audience-callout", y=0.7,
           cards=[("Do NOT let an equestrian see this... 👀🐴", 0)]))
V = sys.argv[1]; K = CFG[V]; SONG = K["song"]; CARDS = K["cards"]
SHOTS = json.load(open(f"{O}/{V}_shots.json"))
def build():
    sg = original_song.gate(dict(recreate_of=dict(slug="lumarein", reel_id=K["reel"]), song_key=K["key"], song_in_s=SONG[1], song_start_t=0, song_loops=False))
    assert not sg, sg
    enforce([{"text": t} for t, _ in CARDS], K["fmt"]); segs = []
    for i, (g, a, b, lit, *ex) in enumerate(SHOTS):
        s = f"{O}/{V}_s{i}.mp4"
        z = ex[0] if ex else 1.0  # optional crop-zoom on the rider (raises measured side-tracking motion)
        zc = f"crop=iw/{z}:ih/{z}:(iw-iw/{z})*0.35:(ih-ih/{z})*0.55," if z != 1.0 else ""
        vf = f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS,{zc}scale=720:1280,fps=30,format=yuv420p[v];" + (GLOW_SUBTLE if lit else "[v]null[o]")
        subprocess.run(["ffmpeg","-y","-loglevel","error","-i",f"{C}/{g}.mp4","-filter_complex",vf+f";[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS[aa]",
                        "-map","[o]","-map","[aa]","-c:v","libx264","-crf","16","-c:a","aac","-ar","48000",s], check=True); segs.append((s, b - a))
    t0s = [0.0]
    for _, d in segs: t0s.append(t0s[-1] + d)
    dur = t0s[-1]
    lst = f"{O}/{V}_list.txt"; open(lst, "w").write("".join(f"file '{s}'\n" for s, _ in segs))
    body = f"{O}/{V}_body.mp4"; subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",lst,"-c","copy",body], check=True)
    ins = ["-i", body, "-ss", str(SONG[1]), "-i", SONG[0]]; f = []; last = "0:v"; pngs = []
    from hookforge import textcards as TC
    for j, (t, si) in enumerate(CARDS):
        png = f"{O}/{V}_card{j}.png"; sc = float(os.environ.get("CARD_SC", TC.fit_card(t, 1.0))); assert TC.caption_lines_gate([(t, sc)])["ok"]
        if K["y"] is None:
            from hookforge import emoji_gate; emoji_gate.render(t, 720, 1280, png, scale=sc)
        else: TC.render_card(t, 720, 1280, scale=sc, y=K["y"]).save(png)
        ins += ["-loop","1","-t",str(dur),"-i",png]
        a = t0s[si]; b = t0s[CARDS[j+1][1]] if j + 1 < len(CARDS) else dur; pngs.append(dict(text=t, t0=round(a,3), t1=round(b,3), png=png, scale=sc, y=K["y"]))
        f.append(f"[{last}][{j+2}:v]overlay=0:0:enable='between(t,{a:.3f},{b - 0.001:.3f})'[c{j}]"); last = f"c{j}"
    f.append(f"[1:a]atrim=0:{dur},afade=t=out:st={dur-0.4}:d=0.4,volume=1.0[m];[0:a]volume=0.22[n];[m][n]amix=inputs=2:normalize=0[au]")
    out = f"{O}/{V}_final.mp4"
    subprocess.run(["ffmpeg","-y","-loglevel","error",*ins,"-filter_complex",";".join(f),"-map",f"[{last}]","-map","[au]","-t",str(dur),
                    "-c:v","libx264","-crf","17","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-map_metadata","-1","-map_chapters","-1",
                    "-fflags","+bitexact","-flags:v","+bitexact","-flags:a","+bitexact","-metadata","encoder=","-movflags","+faststart",out], check=True)
    from hookforge import deliver
    clean = f"{O}/{V}_clean.mp4"; deliver.sanitize(out, clean); assert not deliver.scan(clean), deliver.scan(clean)
    bj = dict(out=clean, dur=round(dur, 3), shot_t0=[round(x, 3) for x in t0s], cards=pngs, glow=GLOW_SPEC)
    json.dump(bj, open(f"{O}/{V}_build.json", "w"), indent=1, ensure_ascii=False); return bj
if __name__ == "__main__": print(json.dumps(build(), indent=1, ensure_ascii=False))
