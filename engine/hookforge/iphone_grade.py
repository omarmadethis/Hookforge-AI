"""D75 iPhone-texture grade: applied to AI shots ONLY (never real footage, never text cards), kept subtle.
grain + light unsharp + mild lens vignette + phone-like tone (slight lifted blacks, rolled highlights, +sat 4%, warm 1%),
optional handheld micro-shake (sub-pixel-ish drift, ~2 px). Hard cuts unaffected (per-shot filter)."""
import os, subprocess
STRENGTH = {"light": dict(noise=0, sharp=0.0, vig="PI/9", shake=1.0), "subtle": dict(noise=5, sharp=0.35, vig="PI/7", shake=1.5), "medium": dict(noise=8, sharp=0.5, vig="PI/6", shake=2.5)}

def vf(strength="light", shake=False, w=None, h=None):
    s = STRENGTH[strength]
    chain = [
        "eq=contrast=1.03:saturation=1.04:gamma=1.01",
        "curves=all='0/0.025 0.5/0.5 0.92/0.9 1/0.96'",        # lifted blacks, rolled highlights (phone HDR-ish)
        "colorbalance=rs=0.01:bs=-0.01",
        *( [f"unsharp=5:5:{s['sharp']}:5:5:0"] if s['sharp'] else [] ),
        f"vignette=angle={s['vig']}",
        *( [f"noise=c0s={s['noise']}:c0f=t+u:c1s={max(1, s['noise']//3)}:c1f=t+u"] if s['noise'] else [] ),
    ]
    if shake:
        a = s["shake"]
        chain += [f"crop=iw-{int(4*a)}:ih-{int(4*a)}:{2*a}+{a}*sin(2*PI*t*1.3)+{a/2}*sin(2*PI*t*3.1):{2*a}+{a}*cos(2*PI*t*1.1)+{a/2}*sin(2*PI*t*2.7)",
                  "scale=trunc(iw/2)*2+%d:trunc(ih/2)*2+%d" % (int(4*a) - int(4*a) % 2, int(4*a) - int(4*a) % 2)]
    return ",".join(chain)

def should_grade(shot):
    """AI shots only: source == 'ai' (default for gens) and never 'real'/'card'."""
    return shot.get("source", "ai") == "ai" and shot.get("kind") != "card"

def grade(src, dst, strength="light", shake=False):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", vf(strength, shake), "-c:v", "libx264", "-crf", "16", "-preset", "veryfast",
                    "-pix_fmt", "yuv420p", "-c:a", "copy", dst], check=True)
    return dst

def before_after(src, out_dir, t=1.0, strength="light", shake=False):
    """Writes before.png / after.png / side_by_side.png at time t."""
    os.makedirs(out_dir, exist_ok=True); g = os.path.join(out_dir, "graded.mp4"); grade(src, g, strength, shake)
    b, a, sbs = (os.path.join(out_dir, n) for n in ("before.png", "after.png", "side_by_side.png"))
    for i, o in ((src, b), (g, a)):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", i, "-frames:v", "1", o], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", b, "-i", a, "-filter_complex", "[1][0]scale2ref[a][b];[b][a]hstack", sbs], check=True)
    return dict(before=b, after=a, side_by_side=sbs, graded=g)
