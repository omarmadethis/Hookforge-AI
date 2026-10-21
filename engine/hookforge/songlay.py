"""D64 SONG LAY-IN (Omar 2026-10-19: "final exports always include the chosen song at its proven in-point").
Every final export goes through lay_song(): the chosen song from music/songs.json starts at its proven in-point; if the song
has a sync_marker (e.g. AC/DC 'walls start shaking') and the plan gives a reveal time, the song is shifted so that marker
lands on the reveal. Real clip sound is kept but ducked under the song (sidechain), then the mix is loudness-normalised
(two-pass loudnorm, -14 LUFS, TP <= -1.5). find_in_point() cross-correlates a full track against a preview/reference clip.
edit_rules.lint FIXes a final plan with no song (ER19)."""
import json, os, subprocess, numpy as np
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SONGS = os.path.join(REPO, "music", "songs.json")

def songs(): return json.load(open(SONGS))

def _load(p, sr=8000):
    b = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"], capture_output=True).stdout
    return np.frombuffer(b, np.int16).astype(float)

def _feat(x, hop=80, n=1024):
    fr = np.lib.stride_tricks.sliding_window_view(x, n)[::hop] * np.hanning(n)
    S = np.log(np.abs(np.fft.rfft(fr))[:, :400].reshape(-1, 40, 10).sum(2) + 1e-6); S -= S.mean(1, keepdims=True)
    return S / (np.linalg.norm(S, axis=1, keepdims=True) + 1e-9)

def find_in_point(full, ref, ref_start_s=5.0, win_s=3.0):
    """Offset (s) in `full` where `ref` at ref_start_s occurs, minus ref_start_s -> where ref's 0 s sits in full."""
    Q = _feat(_load(ref)); T = _feat(_load(full)); a = int(ref_start_s * 100); W = int(win_s * 100); Q = Q[a:a + W]
    sc = np.array([np.sum(Q * T[o:o + W]) / W for o in range(len(T) - W)]); o = int(sc.argmax())
    return dict(offset_s=round(o / 100 - ref_start_s, 2), score=round(float(sc.max()), 3), median=round(float(np.median(sc)), 3))

def _loud(path_or_filter_args):
    r = subprocess.run(["ffmpeg", "-hide_banner", *path_or_filter_args, "-f", "null", "-"], capture_output=True, text=True).stderr
    j = r[r.rindex("{"):r.rindex("}") + 1]; return json.loads(j)

def _win_lufs(path, t0, t1):
    try: return float(_loud(["-ss", f"{t0:.3f}", "-t", f"{max(0.4, t1 - t0):.3f}", "-i", path, "-vn", "-af", "loudnorm=print_format=json"])["input_i"])
    except Exception: return None

def lay_song(video, out, song_key, reveal_t=None, clip_db=None, duck=True, lufs=-14.0, tp=-1.5, dialogue=None):
    """D74: clip_db=None -> Omar style. dialogue=[(t0,t1),...] video windows with speech (countdowns, lines): the clip is
    gained so speech sits style.audio.dialogue_over_music_lu (+8 LU, his 1011/0920(2) range +4..+10.6) above the song at
    its in-point; with no dialogue the clip stays at 0 dB (Omar keeps clip volume 1.0). Result reports the measured gap."""
    from . import omar_style as OS
    s = songs()[song_key]; start = s.get("in_point_s")
    if start is None:   # D92: seasonal proven in-point fallback
        from . import ly_season as _ly; _sp = _ly.song_in_point(s.get("title") or song_key); start = _sp["in_point_s"] if _sp else 0.0
    start = float(start); delay = 0.0; dmm = None; song_gain = float(s.get("music_gain_db", 0))
    if clip_db is None:
        clip_db = 0.0
        if dialogue:
            cl = [x for x in (_win_lufs(video, a, b) for a, b in dialogue) if x is not None and x > -60]
            sl = _win_lufs(s["file"], start, start + 8)
            if cl and sl is not None:
                g = OS.dialogue_gain_db(sorted(cl)[len(cl) // 2], sl, song_gain); clip_db = g["clip_gain_db"]; song_gain = g["song_gain_db"]
                dmm = round(sorted(cl)[len(cl) // 2] + clip_db - (sl + song_gain), 2)
        duck = duck and bool(dialogue)
    if reveal_t is not None and s.get("sync_marker"):
        m = s["markers"][s["sync_marker"]]; shift = reveal_t - m
        # D66 (Omar 2026-10-19): NEVER delay the song / leave a silent gap at t=0. Move the in-point instead:
        # shift>0 -> start earlier in the song; shift<0 -> start later. Song always plays from frame 0.
        start -= shift
        if start < 0: raise ValueError(f"sync needs song to start {-start:.2f}s before its beginning; pick another marker/reveal")
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video], capture_output=True, text=True).stdout)
    mus = f"[1:a]atrim=start={start:.3f}:duration={dur + 1:.3f},asetpts=PTS-STARTPTS,adelay={int(delay * 1000)}:all=1,volume={song_gain}dB,afade=t=out:st={dur - 0.6:.2f}:d=0.6,aresample=44100[m]"
    cl = f"[0:a]volume={clip_db}dB,aresample=44100[c]"
    if duck: mix = f"{mus};{cl};[m]asplit[m1][m2];[c][m2]sidechaincompress=threshold=0.05:ratio=4:attack=20:release=300[cd];[m1][cd]amix=inputs=2:normalize=0:duration=first[mx]"
    else: mix = f"{mus};{cl};[m][c]amix=inputs=2:normalize=0:duration=first[mx]"
    base = ["-i", video, "-i", s["file"]]
    meas = _loud([*base, "-filter_complex", mix + f";[mx]loudnorm=I={lufs}:TP={tp}:LRA=11:print_format=json", "-t", f"{dur}"])
    ln = (f"loudnorm=I={lufs}:TP={tp}:LRA=11:measured_I={meas['input_i']}:measured_TP={meas['input_tp']}:measured_LRA={meas['input_lra']}"
          f":measured_thresh={meas['input_thresh']}:offset={meas['target_offset']}:linear=true,aresample=44100")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *base, "-filter_complex", mix + f";[mx]{ln},alimiter=limit=0.84:level=false[aout]",
                    "-map", "0:v:0", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{dur}", out], check=True, timeout=900)
    return dict(out=out, song=s["song"], song_start_s=round(start, 3), song_delay_s=round(delay, 3), reveal_t=reveal_t,
                clip_db=clip_db, song_gain_db=song_gain, dialogue_minus_music_lu=dmm,
                marker=s.get("sync_marker"), marker_at_video_s=(round(delay + s["markers"][s["sync_marker"]] - (start - s["in_point_s"]), 3) if s.get("sync_marker") else None))

# D65: auto-fetch when a song is missing (fetch runs on Omar's Mac; see music/fetch_song.py)
class SongMissing(RuntimeError): pass
MAC_ID = "79feea1a-ffa0-4e22-a698-a8a772db5260"
def ensure_song(song_key, title=None, artist=None, machine=MAC_ID):
    import sys
    sys.path.insert(0, os.path.join(REPO, "music")); import fetch_song as F
    if not F.need_fetch(song_key): return songs()[song_key]
    e = songs().get(song_key, {}); title = title or e.get("title"); artist = artist or e.get("artist")
    if title and artist:   # D72: box-first fallback chain (YouTube default/alt clients, SoundCloud non-DRM, archive.org), Mac last
        r = F.auto(song_key, title, artist, log=lambda *x: None)
        if r["ok"]:
            from . import poc_library as L
            ip = e.get("in_point_s")
            if ip is None:
                cand = [x for x in L.load() if x["kind"] == "song" and x.get("key") == song_key and x.get("in_point_s") is not None and L.alive(x)]
                ip = cand[0]["in_point_s"] if cand else None
            if ip is None: raise SongMissing(f"{song_key}: track verified ({r['xcorr']}) but no POC in-point; add proof first")
            db = songs(); e.update(file=r["file"], source=r["source"], in_point_s=ip, song=e.get("song") or f"{artist} - {title}",
                                   verify=dict(preview=r["preview"], xcorr=r["xcorr"], preview_at_s=r["preview_at_s"], tempo_correction=1.0))
            db[song_key] = e; json.dump(db, open(SONGS, "w"), indent=1, ensure_ascii=False); return e
    raise SongMissing(json.dumps(dict(song_key=song_key, next="run on Mac, CopyToBox, then fetch_song.py register",
                                      search=F.plan_cmd(title, artist, machine)), indent=1))

_lay_song_raw = lay_song
def lay_song(video, out, song_key, *a, **k):
    ensure_song(song_key); return _lay_song_raw(video, out, song_key, *a, **k)

def onset_s(path, thresh_db=-35.0, win=0.05):
    """First time (s) the mix RMS exceeds thresh_db (50 ms windows)."""
    x = _load(path, 8000) / 32768.0; n = int(8000 * win)
    for i in range(0, len(x) - n, n):
        r = np.sqrt(np.mean(x[i:i + n] ** 2)) + 1e-12
        if 20 * np.log10(r) > thresh_db: return round(i / 8000, 3)
    return None

def song_start_check(path, max_onset=0.1, thresh_db=-35.0):
    """QA (D66): the song must be audible from frame 0; FAIL if audio onset > max_onset."""
    o = onset_s(path, thresh_db); return dict(check="song_at_t0", onset_s=o, ok=(o is not None and o <= max_onset))
