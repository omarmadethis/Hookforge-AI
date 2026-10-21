"""D145: the editor side of the lean plan. Builds each lean video with ffmpeg from its own 1080p hook clip plus the
product anchor's shared B1-B3 clips, re-ordered and re-trimmed per lean_plan.edit_plan. Also measures the result:
ordered-frame overlap between finished videos (perceptual frame hashes + LCS) and where the payoff reveal lands (D147).
Local only; generates nothing on Higgsfield."""
import json, os, subprocess, tempfile
from .config import EXPORT
from . import lean_plan, autoedit

HOOK_S = 4.0
MIN_LEAD_S = 0.25                   # and not a 1-frame flash of the pre-reveal shot
REVEAL_MAX_S = 1.5                  # D147: the reveal must land within the first 1.5 s of the payoff segment

def edit_cmd(hook_file, bodies, edit, out_path, hook_in=0.0, hook_s=HOOK_S):
    """hook_file: this video's own hook clip; bodies: {"B1": file, ...} (the anchor's clips); edit: [(clip, in_frame, out_frame)]."""
    fps = lean_plan.FPS; W, H = EXPORT["width"], EXPORT["height"]
    segs = [(hook_file, hook_in, hook_s)] + [(bodies[c], a / fps, (b - a) / fps) for c, a, b in edit]
    ins, f, parts = [], [], []
    for i, (fp, a, d) in enumerate(segs):
        ins += ["-i", fp]
        f.append(f"[{i}:v]trim=start={a:.4f}:duration={d:.4f},setpts=PTS-STARTPTS,scale={W}:{H}:flags=lanczos,fps={EXPORT['fps']},setsar=1[v{i}]")
        f.append(f"[{i}:a]atrim=start={a:.4f}:duration={d:.4f},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo[a{i}]")
        parts.append(f"[v{i}][a{i}]")
    f.append("".join(parts) + f"concat=n={len(segs)}:v=1:a=1[v][a]")
    return ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *ins, "-filter_complex", ";".join(f), "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", out_path]

def build(hook_file, bodies, edit, out_path, clean=True):
    """Render one lean video. clean=True ends in autoedit.clean_export (D44 provenance strip) like every final."""
    raw = out_path if not clean else tempfile.mktemp(suffix=".mp4")
    subprocess.run(edit_cmd(hook_file, bodies, edit, raw), check=True, timeout=900)
    if clean: autoedit.clean_export(raw, out_path); os.remove(raw)
    return dict(path=out_path, duration=probe_dur(out_path))

def probe_dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True).stdout)

def frame_hashes(p, size=16):
    """Average-hash per frame (8x8 gray, 24 fps). Lets us measure shared frames on the real renders."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-vf", f"fps={lean_plan.FPS},scale={size}:{size}:flags=area,format=gray", "-f", "rawvideo", "-"],
                         capture_output=True, check=True).stdout
    n = size * size; out = []
    for i in range(0, len(raw) - n + 1, n):
        fr = raw[i:i + n]; m = sum(fr) / n
        out.append(sum(1 << k for k, v in enumerate(fr) if v > m))
    return out

def measured_shared(pa, pb, max_bits=12):
    """Ordered shared-frame ratio between two finished videos: LCS where frames 'match' if their hashes differ by
    <= max_bits of 256 (survives re-encode/scale). Divided by the shorter video's frame count."""
    a, b = frame_hashes(pa), frame_hashes(pb)
    prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0]
        for j, y in enumerate(b):
            cur.append(prev[j] + 1 if bin(x ^ y).count("1") <= max_bits else max(prev[j + 1], cur[j]))
        prev = cur
    return prev[-1] / min(len(a), len(b))

# ---------------- D147: payoff reveal check ----------------
def _stats(clip):
    """Per-frame YAVG / SATAVG / YHIGH (8-bit, 24 fps) via ffmpeg signalstats."""
    import re
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", clip, "-vf", f"fps={lean_plan.FPS},scale=180:320,format=yuv420p,signalstats,metadata=print:file=-",
                        "-f", "null", "-"], capture_output=True, text=True, check=True).stdout
    g = lambda k: [float(x) for x in re.findall(k + r"=([\d.]+)", r)]
    return g("YAVG"), g("SATAVG"), g("YHIGH")

def _cut_s(clip, min_jump=2.5, min_ratio=3.0):
    """Hard-cut / flash reveal: biggest standout frame-to-frame change after 0.25 s, else None."""
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", clip, "-vf", f"fps={lean_plan.FPS},scale=64:114,format=gray", "-f", "rawvideo", "-"],
                       capture_output=True, check=True).stdout
    n = 64 * 114; fr = [r[i:i + n] for i in range(0, len(r) - n + 1, n)]
    d = [(i / lean_plan.FPS, sum(abs(x - y) for x, y in zip(fr[i][::7], fr[i - 1][::7])) / len(fr[i][::7])) for i in range(1, len(fr))]
    if not d: return None
    med = sorted(v for _, v in d)[len(d) // 2]
    t, best = max(((t, v) for t, v in d if t >= 0.25), key=lambda x: x[1], default=(None, 0))
    return round(t, 3) if best >= min_jump and best >= min_ratio * max(med, 0.1) else None

RAMP_WIN_S = 0.75; RAMP_MIN = 6.0   # 8-bit units of |dY| + |dSat| + 0.5|dYhigh| across the window

def _ramp(clip):
    """D150 slow reveal (lights rippling on, glow building): brightness + saturation ramp. Signals are smoothed over
    0.25 s; the strongest RAMP_WIN_S-window change wins if >= RAMP_MIN; the reveal frame = where that ramp is half done."""
    Y, S, H = _stats(clip); n = min(len(Y), len(S), len(H))
    if n < 12: return None
    k = max(1, int(0.25 * lean_plan.FPS)); sm = lambda v: [sum(v[max(0, i - k // 2):i + k // 2 + 1]) / len(v[max(0, i - k // 2):i + k // 2 + 1]) for i in range(n)]
    Y, S, H = sm(Y[:n]), sm(S[:n]), sm(H[:n]); w = int(RAMP_WIN_S * lean_plan.FPS)
    sig = lambda a, b: abs(Y[b] - Y[a]) + abs(S[b] - S[a]) + 0.5 * abs(H[b] - H[a])
    best = max(((sig(i, min(i + w, n - 1)), i) for i in range(0, n - 2)), default=(0, 0))
    if best[0] < RAMP_MIN: return None
    a = best[1]; b = min(a + w, n - 1)
    half = next((t for t in range(a, b + 1) if sig(a, t) >= best[0] / 2), b)
    return dict(t=round(half / lean_plan.FPS, 3), start=round(a / lean_plan.FPS, 3), strength=round(best[0], 1))

def reveal_info(clip):
    """Both detectors; the reveal = the slow ramp when there is one (lights coming on), else the hard cut/flash."""
    rp, ct = _ramp(clip), _cut_s(clip)
    t = rp["t"] if rp else ct
    return dict(reveal_s=t, kind="ramp" if rp else ("cut" if ct is not None else None), ramp=rp, cut_s=ct)

def reveal_frame_s(clip):
    return reveal_info(clip)["reveal_s"]

def reveal_check(edit, reveal_s, payoff=lean_plan.PAYOFF):
    """Flag when the payoff segment's reveal lands after REVEAL_MAX_S into the segment, or is trimmed away.
    reveal_s: reveal time in the payoff clip's own timeline (from reveal_frame_s or the plan's payoff_reveal_s)."""
    seg = next(((a / lean_plan.FPS, b / lean_plan.FPS) for c, a, b in edit if c == payoff), None)
    if seg is None: return dict(ok=False, flag="payoff clip missing")
    if reveal_s is None: return dict(ok=False, flag="reveal time unknown - human check")
    a, b = seg; at = reveal_s - a
    if reveal_s < a: return dict(ok=False, flag=f"reveal at {reveal_s:.2f}s is trimmed off (payoff starts {a:.2f}s)", at_s=round(at, 2))
    if reveal_s >= b: return dict(ok=False, flag=f"reveal at {reveal_s:.2f}s is after the payoff cut ({b:.2f}s)", at_s=round(at, 2))
    if at < MIN_LEAD_S: return dict(ok=False, flag=f"only {at:.2f}s of payoff before the reveal - reads as a flash frame (< {MIN_LEAD_S}s)", at_s=round(at, 2))
    if at > REVEAL_MAX_S: return dict(ok=False, flag=f"reveal lands {at:.2f}s into the payoff (> {REVEAL_MAX_S}s)", at_s=round(at, 2))
    return dict(ok=True, at_s=round(at, 2))


def gate_built(paths_by_page, limit=lean_plan.MAX_SHARED):
    """D142 on the finished renders: every same-page pair measured <= 50% ordered shared frames, else blocked."""
    import itertools
    bad = []
    for pg, paths in paths_by_page.items():
        for a, b in itertools.combinations(sorted(paths), 2):
            r = measured_shared(a, b)
            if r > limit: bad.append(dict(page=pg, a=os.path.basename(a), b=os.path.basename(b), measured=round(r, 3)))
    return dict(ok=not bad, violations=bad)
