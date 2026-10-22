"""ffmpeg auto-edit. animatic(): mock edit from existing clips (no generation) with shot labels + text cards at the
CapCut position. final(): same assembly from generated clips at 2160x3840 (EXPORT spec) - used once gens exist.
Text cards are rendered with style/render_text.py (colour emoji kept); shot labels stay ffmpeg drawtext.
"""
import os, re, subprocess
from .config import TEXT, EXPORT, REPO

FONT = next((f for f in TEXT["font_candidates"] if os.path.exists(f)), "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
EMOJI_RX = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u200d\u2B00-\u2BFF\u2300-\u23FF]+")

def _esc(s): return EMOJI_RX.sub("", s).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\u2019").replace("%", " pct").replace(",", "\\,").strip()

def animatic_cmd(plan, out_path, w=720, h=1280):
    src = plan["mock_source"]["file"] if plan.get("mock_source") else None
    shots = plan["shots"]; f = []; parts = []
    inputs = ["-i", src] if src else ["-f", "lavfi", "-i", f"color=c=gray:s={w}x{h}:r=30:d={plan['duration']}"]
    for i, s in enumerate(shots):
        d = s["t1"] - s["t0"]
        if src:
            f.append(f"[0:v]trim=start={s['t0']}:duration={d},setpts=PTS-STARTPTS,scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps=30,setsar=1[v{i}]")
            f.append(f"[0:a]atrim=start={s['t0']}:duration={d},asetpts=PTS-STARTPTS[a{i}]")
        else:
            f.append(f"[0:v]trim=start=0:duration={d},setpts=PTS-STARTPTS[v{i}]"); f.append(f"anullsrc=r=44100:cl=stereo,atrim=duration={d}[a{i}]")
        parts.append(f"[v{i}][a{i}]")
    f.append("".join(parts) + f"concat=n={len(shots)}:v=1:a=1[cv][ca]")
    dt = []
    fs_lab = int(h * 0.022); fs_txt = int(h * TEXT["height_frac"] * 1.2)
    for s in shots:
        lab = _esc(f"{s['code']} [{s['gen']}] {s['t0']:.1f}-{s['t1']:.1f}s MOCK")
        dt.append(f"drawtext=fontfile={FONT}:text='{lab}':x=20:y=h-{int(h*0.06)}:fontsize={fs_lab}:fontcolor=yellow:box=1:boxcolor=black@0.6:enable='between(t,{s['t0']},{s['t1']})'")
        desc = _esc(s["desc"][:70])
        dt.append(f"drawtext=fontfile={FONT}:text='{desc}':x=20:y=h-{int(h*0.035)}:fontsize={int(fs_lab*0.8)}:fontcolor=white:box=1:boxcolor=black@0.6:enable='between(t,{s['t0']},{s['t1']})'")
    dt.append(f"drawtext=fontfile={FONT}:text='ANIMATIC - mock clips from {_esc(plan['mock_source']['key'] if plan.get('mock_source') else 'placeholder')} - not for posting':x=(w-text_w)/2:y=20:fontsize={fs_lab}:fontcolor=red:box=1:boxcolor=white@0.7")
    f.append("[cv]" + ",".join(dt) + "[ov0]")
    # Text cards: style/render_text.py (Montserrat Medium ~ CapCut System font, size 15, white, black stroke 0.09, wrap 82%,
    # block centre ~19% from top, colour emoji) at the plan's per-card scale. No animations/transitions (STYLE_GUIDE).
    import sys; sys.path.insert(0, os.path.join(REPO, "style")); import render_text
    cdir = os.path.join(os.path.dirname(os.path.abspath(out_path)), "cards"); os.makedirs(cdir, exist_ok=True)
    from .card_count import enforce as _cc; _cc(plan["text_cards"], (plan.get("hook") or {}).get("format") or plan.get("format"))   # D188
    last = "ov0"
    for k, c in enumerate(plan["text_cards"]):
        png = os.path.join(cdir, f"card{k}.png"); from . import emoji_gate as _EG; _EG.render(c["text"], w, h, png, scale=c.get("scale") or 1.0)   # D189 Apple emoji only
        inputs += ["-loop", "1", "-t", str(plan["duration"]), "-i", png]
        f.append(f"[{last}][{k + 1}:v]overlay=0:0:enable='between(t,{c['t']},{c['t'] + c['dur']})'[ov{k + 1}]"); last = f"ov{k + 1}"
    f.append(f"[{last}]null[ov]")
    return ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs, "-filter_complex", ";".join(f), "-map", "[ov]", "-map", "[ca]",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "28", "-c:a", "aac", "-b:a", "96k", "-t", str(plan["duration"]), out_path]

def _grade(s, plan):
    """D75: subtle iPhone-texture grade on AI shots only (real footage / cards untouched); plan['grade']='off' disables."""
    from . import iphone_grade as IG
    if plan.get("grade") == "off" or not IG.should_grade(s): return ""
    return "," + IG.vf(s.get("grade_strength", "subtle"), shake=bool(s.get("shake")))

def final_cmd(clips, plan, out_path):
    """clips: {shot_code: (file, in_s)} from generated gens (trims from plan['gens'][*]['trims']). Music is added in CapCut."""
    if plan.get("cards") is not None or plan.get("hook"):   # D191: render refuses unless the plan-level master gate passes
        from . import master_gate
        master_gate.pre_render(plan)
    ins, f, parts = [], [], []
    for i, s in enumerate(plan["shots"]):
        fpath, a = clips[s["code"]]; ins += ["-i", fpath]; d = s["t1"] - s["t0"]
        f.append(f"[{i}:v]trim=start={a}:duration={d},setpts=PTS-STARTPTS,scale={EXPORT['width']}:{EXPORT['height']}:flags=lanczos,fps={EXPORT['fps']},setsar=1{_grade(s, plan)}[v{i}]")
        g = float(s.get("audio_gain", 1.0))   # D63: natural clip sound kept; key real sound boosted 2-4x
        f.append(f"[{i}:a]atrim=start={a}:duration={d},asetpts=PTS-STARTPTS,aresample=48000,volume={g},aformat=channel_layouts=stereo[a{i}]")
        parts.append(f"[v{i}][a{i}]")
    f.append("".join(parts) + f"concat=n={len(plan['shots'])}:v=1:a=1[v][a]")
    return ["ffmpeg", "-y", *ins, "-filter_complex", ";".join(f), "-map", "[v]", "-map", "[a]", "-c:v", EXPORT["vcodec"], "-b:v", EXPORT["vbitrate"],
            "-pix_fmt", EXPORT["pix_fmt"], "-c:a", EXPORT["acodec"], "-b:a", EXPORT["abitrate"], *CLEAN_FLAGS, out_path]

# D44 (Omar 2026-10-18 21:39 PT): strip C2PA / provenance metadata from ALL final exports.
CLEAN_FLAGS = ["-map_metadata", "-1", "-map_metadata:s:v", "-1", "-map_metadata:s:a", "-1", "-map_chapters", "-1",
               "-fflags", "+bitexact", "-flags:v", "+bitexact", "-flags:a", "+bitexact", "-movflags", "+faststart"]

def clean_export_cmd(src, out_path):
    """Re-encode into a fresh container with no global/stream metadata, chapters, c2pa/jumbf/uuid boxes (only v+a mapped)."""
    return ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", src, "-map", "0:v:0", "-map", "0:a:0?", "-dn", "-sn",
            "-c:v", EXPORT["vcodec"], "-b:v", EXPORT["vbitrate"], "-pix_fmt", EXPORT["pix_fmt"], "-tag:v", "hvc1", "-x265-params", "log-level=error:info=0",
            "-c:a", EXPORT["acodec"], "-b:a", EXPORT["abitrate"], "-ar", str(EXPORT["ar"]), *CLEAN_FLAGS, out_path]

def clean_export(src, out_path):
    import subprocess, sys, os
    import tempfile
    tmp = tempfile.mktemp(suffix=".mp4")
    subprocess.run(clean_export_cmd(src, tmp), check=True, timeout=1800)
    clean_remux(tmp, out_path); os.remove(tmp)   # D44c: stream-copy pass blanks stsd compressor name ("Lavc libx265")
    pf = os.path.join(os.path.dirname(__file__), "..", "..", "tools", "preflight")
    if pf not in sys.path: sys.path.insert(0, pf)
    import preflight
    prov = preflight.provenance(out_path)
    assert not any(prov.values()), f"provenance metadata remains after clean export: {prov}"
    return dict(path=out_path, provenance=prov)

def clean_remux(src, out_path):
    """Lossless metadata strip (stream copy) for post-export fixes such as audio re-levels: same CLEAN_FLAGS/bitexact
    as clean_export so no Lavf encoder tag / C2PA survives. Any step that touches a final MUST end here or in clean_export."""
    import subprocess
    vc = subprocess.run(["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=codec_name","-of","csv=p=0",src],
                        capture_output=True,text=True).stdout.strip()
    tag = ["-tag:v","hvc1"] if vc == "hevc" else []
    subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error","-i",src,"-map","0:v:0","-map","0:a:0?","-dn","-sn",
                    "-c","copy",*tag,*CLEAN_FLAGS,out_path],check=True,timeout=600)
    return out_path

def relevel_audio(src, out_path, lufs=-14.0, tp=-2.0):
    """Re-level audio only (video copied), then clean_remux. Replaces ad-hoc loudnorm one-liners."""
    import subprocess, tempfile, os
    tmp = tempfile.mktemp(suffix=".mp4")
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",src,"-map","0:v:0","-map","0:a:0","-c:v","copy","-af",
                    f"loudnorm=I={lufs}:TP={tp}:LRA=11,aresample={EXPORT['ar']}","-c:a",EXPORT["acodec"],"-b:a",EXPORT["abitrate"],"-flags:a","+bitexact","-fflags","+bitexact",tmp],check=True)
    clean_remux(tmp, out_path); os.remove(tmp); return out_path
