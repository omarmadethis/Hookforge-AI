"""MR59 (Omar 2026-10-23): EVERY finished video is upscaled to 4K in Higgsfield as the FINAL workflow step - after the master gate passes,
immediately before posting. The file that is posted / hosted is that 4K output (2160x3840 for vertical), never the 720p master.

  plan(src, provider="bytedance")      -> the exact Higgsfield `upscale_video` params (no job is run here)
  finish(src, raw_download, out=None)  -> re-strips ALL metadata (MR01), verifies audio / length / card text / visuals unchanged vs the gated
                                          source, writes <out>.UPSCALE.json (binding to the gated source's sha-bound PASS report) and returns `out`
  record_cost(src, credits)            -> note the measured credits in the sidecar + spec (replaces the provisional reserve)

Workflow (see docs/PLAYBOOK.md section 3b):
  build -> master_gate.ensure PASS (720x1280) -> media_upload the gated mp4 (Higgsfield) -> upscale_video(**plan) -> job_status/jobs_wait ->
  download the result -> upscale4k.finish(...) -> publish.prepare(<4K file>) (master_gate.require refuses anything below 4K).
Cost: upscale_video has NO cost preflight (Higgsfield shows the price only on its button). Reserve UPSCALE_RESERVE_CREDITS per video in the spend
cap (spec.spend.upscale_credits; MR09 counts it) and replace it with the measured transactions delta after the first job (record_cost)."""
import json, os, re, subprocess, shutil
from . import master_gate as MG, deliver

UPSCALE_RESERVE_CREDITS = 30      # PROVISIONAL: ByteDance 4K / Topaz 2160p of a ~13 s 720x1280 clip; Higgsfield publishes ranges only (ByteDance 3-277, Topaz 4-96). Replace after the first measured job.
LEN_TOL_S = 0.10                  # upscaled length must match the gated video within this
AUDIO_MIN_CORR = 0.97
SSIM_MIN = 0.80                   # luma structure vs the gated master scaled to the same size: the upscaler must not re-imagine the video

def plan(src, provider="bytedance", fps=None):
    """Exact tool call for the Higgsfield connector. `video_id` = the media_id of the gated mp4 uploaded with media_upload/media_confirm
    (the file must be the PASS-gated file, byte for byte). ByteDance 'ugc' preset (enhance, no invented detail - Higgsfield advises against the
    diffusion model for text-heavy / approved deliverables) with fps pinned to the source rate (24 default would retime the video; 60 doubles the cost)."""
    w, h = MG.video_dims(src)
    if fps is None:
        r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=avg_frame_rate", "-of", "csv=p=0", src], capture_output=True, text=True).stdout.strip()
        try: a, b = r.split("/"); fps = round(float(a) / float(b))
        except Exception: fps = 30
        fps = min((24, 30, 60), key=lambda x: abs(x - fps))
    if provider == "topaz":
        params = dict(provider="topaz", video_id="<media_id of the gated mp4>", aspect_ratio="9:16" if h > w else "auto", resolution="2160p")
    else:
        params = dict(provider="bytedance", video_id="<media_id of the gated mp4>", width=w, height=h, fps=fps, resolution="4k", preset="ugc")
    return dict(connector="user-Higgsfield--new-account", tool="upscale_video", params=params, reserve_credits=UPSCALE_RESERVE_CREDITS,
                source=src, source_sha256=MG.sha(src), expects=f"{MG.UP_SHORT}x{MG.UP_LONG} (vertical)")

def _dur(p): return MG._dur(p)
def _has_audio(p): return any(s.get("codec_type") == "audio" for s in MG._ffprobe(p).get("streams", []))
def _pcm(p, sr=8000):
    import numpy as np
    b = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-vn", "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"], capture_output=True).stdout
    return np.frombuffer(b, dtype="<i2").astype("float32")
def audio_unchanged(src, up):
    import numpy as np
    if _has_audio(src) != _has_audio(up): return False, "audio stream present in only one file"
    if not _has_audio(src): return True, "no audio in either"
    a, b = _pcm(src), _pcm(up); n = min(len(a), len(b))
    if n < 1000: return False, "audio too short"
    if abs(len(a) - len(b)) / 8000.0 > LEN_TOL_S: return False, f"audio length differs {abs(len(a) - len(b)) / 8000.0:.3f}s"
    a, b = a[:n], b[:n]; na, nb = float(np.linalg.norm(a)), float(np.linalg.norm(b))
    if (na == 0) != (nb == 0): return False, "audio went silent (or appeared)"
    c = float(np.dot(a, b) / (na * nb)) if na and nb else 1.0
    return c >= AUDIO_MIN_CORR, f"waveform correlation {c:.4f}"
def visuals_ssim(src, up):
    w, h = MG.video_dims(src)
    o = subprocess.run(["ffmpeg", "-v", "info", "-i", up, "-i", src, "-filter_complex",
                        f"[0:v]scale={w}:{h}:flags=area,format=gray[a];[1:v]format=gray[b];[a][b]ssim", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.search(r"All:([0-9.]+)", o); return float(m.group(1)) if m else 0.0
def cards_unchanged(src, up, spec):
    """Card text must read the same after the upscale: the MR39 OCR check (frames scaled back to 720x1280) on the upscaled file."""
    sp = json.loads(json.dumps(spec)); sp.pop("_hints", None)
    f = MG.CHECKS["card_ocr"](up, sp, "final")
    return not f, [x["msg"] for x in f] or [(h["card"], h["ocr"]) for h in sp.get("_hints", {}).get("ocr", [])]

def verify(src, up, spec=None):
    spec = spec if spec is not None else MG.load_spec(src)
    v = {}; why = {}
    w, h = MG.video_dims(up); v["dims_4k"] = MG.is_4k(up); why["dims"] = f"{w}x{h}"
    ds, du = _dur(src), _dur(up); v["length_unchanged"] = abs(ds - du) <= LEN_TOL_S; why["length_s"] = [round(ds, 3), round(du, 3)]
    v["audio_unchanged"], why["audio"] = audio_unchanged(src, up)
    v["cards_unchanged"], why["cards"] = cards_unchanged(src, up, spec)
    ss = visuals_ssim(src, up); v["visuals_unchanged"] = ss >= SSIM_MIN; why["ssim"] = round(ss, 4)
    v["metadata_clean"] = not deliver.scan(up); why["metadata"] = deliver.scan(up)
    return v, why

def finish(src, raw_download, out=None, provider="bytedance", resolution="4k", job_id=None, credits=None, spec=None):
    """Step after Higgsfield returns: strip ALL metadata from the download (MR01), verify against the gated source, bind, return the postable 4K path."""
    if not MG.sha(src) == json.load(open(MG.report_paths(src)[0]))["sha256"] or json.load(open(MG.report_paths(src)[0]))["status"] != "PASS":
        raise MG.GateRefused(f"{src}: not master-gate PASS - the upscale is the step AFTER the gate (MR59)")
    out = out or re.sub(r"\.mp4$", "_4k.mp4", src)
    tmp = out + ".tmp.mp4"; deliver.sanitize(raw_download, tmp); os.replace(tmp, out)      # clean_remux + blank SEI, same as every final
    spec = spec if spec is not None else MG.load_spec(src)
    v, why = verify(src, out, spec)
    rec = dict(source=src, source_sha256=MG.sha(src), upscaled=out, upscaled_sha256=MG.sha(out), provider=provider, resolution=resolution,
               higgsfield_job_id=job_id, credits=credits, at=MG.now_pt(), rule="MR59", verify=v, why=why)
    json.dump(rec, open(MG.upscale_record_path(out), "w"), indent=1, ensure_ascii=False, default=str)
    if os.path.exists(src + ".gate.json"): shutil.copyfile(src + ".gate.json", out + ".gate.json")   # same spec travels with the 4K file (caption/page/approval)
    bad = [k for k, x in v.items() if x is not True]
    if bad: raise MG.GateRefused(f"{out}: 4K upscale failed verification {bad} {why} - do not post; retry the upscale (other preset/provider) or investigate")
    return out

def record_cost(src_or_out, credits):
    """Replace the provisional reserve with the measured cost (Higgsfield `transactions` delta of the upscale job)."""
    for p in (src_or_out + ".gate.json", MG.upscale_record_path(src_or_out)):
        if os.path.exists(p):
            d = json.load(open(p))
            if "spend" in d: d["spend"]["upscale_credits"] = float(credits)
            else: d["credits"] = float(credits)
            json.dump(d, open(p, "w"), indent=1, ensure_ascii=False)
