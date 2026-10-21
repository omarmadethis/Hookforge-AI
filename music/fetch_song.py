"""D65 AUTONOMOUS SONG FETCH. The box IP is bot-blocked by YouTube, so the fetch runs on Omar's Mac (residential IP) through the
agent's machine-targeted Shell, and the file comes back through CopyToBox. No browser cookies, no credentials, ever.

Mac toolchain (all under ~/HookforgeTools, nothing global): bin/yt-dlp (standalone yt-dlp_macos), bin/deno (YouTube JS
challenge runtime), bin/ffmpeg (symlink to imageio-ffmpeg in venv/), songs/ (downloads), tmp/ (TMPDIR).

Usage, as three steps the agent runs (the box can't reach the Mac itself):
  1) python3 music/fetch_song.py plan  --title T --artist A --machine M [--prefer-channel C]  -> the Mac search command
  2) python3 music/fetch_song.py fetch --id VIDEO_ID --name SLUG                             -> the Mac download command
     (agent runs 1 and 2 with Shell(machineId=M), then CopyToBox ~/HookforgeTools/songs/SLUG.m4a -> music/SLUG.m4a)
  3) python3 music/fetch_song.py register --key K --file music/SLUG.m4a --preview REF --song "A - T" [--tempo-search]
     [--in-ref-s X] [--marker name=sec ...] -> xcorr against the store preview, optional atempo correction (official videos
     are often time-stretched: AC/DC 4K video = 1.3 % fast), writes in_point_s + evidence into songs.json. Rejects score < 0.9.
Candidate pick rule: channel == artist or '<artist> - Topic', exact title match, prefer '(Audio)'/Topic over video, live/cover/
Hz/lyrics/sped excluded; the preview xcorr is the final judge (a 'Topic' upload that scores < 0.9 is rejected).
songlay.ensure_song() calls need_fetch() and raises SongMissing with the plan when a song file is absent."""
import argparse, json, os, re, shlex, subprocess, sys, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); SONGS = os.path.join(HERE, "songs.json")
sys.path.insert(0, HERE); import xcorr as X
import numpy as np
MAC = "~/HookforgeTools"; ENV = f"export PATH={MAC}/bin:$PATH TMPDIR={MAC}/tmp; mkdir -p {MAC}/tmp {MAC}/songs; cd {MAC}/songs"
BAD = re.compile(r"live|cover|hz|lyric|sped|slowed|remix|karaoke|8d|reverb|instrumental", re.I)

def plan_cmd(title, artist, machine):
    q = shlex.quote(f"ytsearch12:{artist} {title} official audio")
    q2 = shlex.quote(f"ytsearch12:{title} {artist} Topic")
    fmt = "%(id)s|%(channel)s|%(title)s|%(duration)s"
    return dict(machineId=machine, command=f"{ENV}; for q in {q} {q2}; do yt-dlp --no-cache-dir --no-warnings --flat-playlist --print '{fmt}' \"$q\"; done | sort -u")

def pick(lines, title, artist):
    c = []
    for l in lines:
        p = l.split("|")
        if len(p) < 4: continue
        vid, ch, t, d = p[0], p[1], p[2], p[3]
        if BAD.search(t): continue
        if title.lower() not in t.lower(): continue
        if ch.lower() not in (artist.lower(), f"{artist.lower()} - topic") and not ch.lower().endswith(" - topic"): continue
        s = (2 if "audio" in t.lower() else 0) + (2 if ch.lower().endswith("topic") else 0) + (1 if ch.lower() == artist.lower() else 0)
        c.append((s, vid, ch, t, d))
    return [dict(id=v, channel=ch, title=t, dur=d, prio=s) for s, v, ch, t, d in sorted(c, reverse=True)]

def fetch_cmd(vid, name):
    return (f"{ENV}; yt-dlp --no-cache-dir --no-playlist -q --no-warnings -f 'bestaudio[ext=m4a]/bestaudio' -x --audio-format m4a "
            f"--ffmpeg-location {MAC}/bin -o {shlex.quote(name)}'.%(ext)s' -- 'https://www.youtube.com/watch?v={vid}' && ls -la {shlex.quote(name)}.m4a; rm -rf {MAC}/tmp/*")

def _score(full, preview, tempo=1.0, W=2800):
    P = X.feat(X.load(preview))[:W]
    if tempo == 1.0: T = X.feat(X.load(full))
    else:
        b = subprocess.run(["ffmpeg", "-v", "error", "-i", full, "-af", f"atempo={tempo}", "-ac", "1", "-ar", "8000", "-f", "s16le", "-"], capture_output=True).stdout
        T = X.feat(np.frombuffer(b, np.int16).astype(float))
    W = min(W, len(P)); sc = np.array([np.sum(P[:W] * T[o:o + W]) / W for o in range(len(T) - W)])
    return int(sc.argmax()) / 100, float(sc.max()), float(np.median(sc))

def register(key, file, preview, song, tempo_search=False, in_ref_s=0.0, markers=None, source="", min_score=0.9, extra=None):
    best = (1.0, *_score(file, preview))
    if tempo_search:
        for r in (0.98, 0.985, 0.987, 0.99, 1.01, 1.013, 1.02):
            o, s, m = _score(file, preview, r)
            if s > best[2] + 0.02: best = (r, o, s, m)
    r, off, s, med = best
    if s < min_score: raise SystemExit(f"REJECT {file}: preview xcorr {s:.3f} < {min_score} (not the same recording)")
    out = file
    if r != 1.0:
        out = re.sub(r"\.m4a$", "_tc.m4a", file)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", file, "-af", f"atempo={r}", "-c:a", "aac", "-b:a", "256k", out], check=True)
        off, s, med = _score(out, preview)
    db = json.load(open(SONGS)) if os.path.exists(SONGS) else {}
    e = db.get(key, {}); e.update(dict(song=song, file=os.path.abspath(out), in_point_s=round(off + in_ref_s, 2),
        source=source, verify=dict(preview=preview, xcorr=round(s, 3), median=round(med, 3), tempo_correction=r, preview_at_s=round(off, 2),
        checked=datetime.datetime.now().strftime("%Y-%m-%d %H:%M PT"))))
    if markers: e["markers"] = markers
    if extra: e.update(extra)
    db[key] = e; json.dump(db, open(SONGS, "w"), indent=1, ensure_ascii=False); return e

def need_fetch(key):
    e = json.load(open(SONGS)).get(key)
    return e is None or not os.path.exists(e.get("file", "")) or "verify" not in e

def _main():
    ap = argparse.ArgumentParser(); ap.add_argument("step", choices=["plan", "pick", "fetch", "register", "auto"])
    for a in ("title", "artist", "machine", "id", "name", "key", "file", "preview", "song", "source"): ap.add_argument("--" + a)
    ap.add_argument("--tempo-search", action="store_true"); ap.add_argument("--in-ref-s", type=float, default=0.0); ap.add_argument("--marker", action="append", default=[])
    a = ap.parse_args()
    if a.step == "plan": print(json.dumps(plan_cmd(a.title, a.artist, a.machine), indent=1))
    elif a.step == "pick": print(json.dumps(pick(sys.stdin.read().splitlines(), a.title, a.artist), indent=1))
    elif a.step == "fetch": print(fetch_cmd(a.id, a.name))
    elif a.step == "auto": print(json.dumps(auto(a.key, a.title, a.artist), indent=1, default=str))
    else:
        mk = {m.split("=")[0]: float(m.split("=")[1]) for m in a.marker} or None
        print(json.dumps(register(a.key, a.file, a.preview, a.song, a.tempo_search, a.in_ref_s, mk, a.source or ""), indent=1))

# ---------------- D72 BOX-FIRST FALLBACK CHAIN ----------------
# Runs entirely on the box. Order: (1) Apple preview via iTunes Search API (the reference), (2) YouTube via yt-dlp default
# client, (3) YouTube alt player clients (no cookies), (4) SoundCloud (non-DRM uploads only), (5) Internet Archive
# (advancedsearch API), (6) Mac last resort (returns the plan_cmd/fetch commands for machine-targeted Shell).
# Every candidate must score >= 0.9 against the Apple preview (same recording). No cookies, tokens or logins, ever.
import urllib.request, urllib.parse, tempfile, shutil
YT_CLIENTS = [None, "web_safari", "mweb", "tv_simply", "android_vr"]
def _http_json(url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30))
def apple_preview(title, artist, out):
    q = urllib.parse.quote(f"{artist} {title}")
    VER = re.compile(r"(?i)\bmix\b|edition|re-?record|version\)|extended|acoustic|demo|duet", re.I)
    res = [r for r in _http_json(f"https://itunes.apple.com/search?term={q}&entity=song&limit=15&country=us")["results"]
           if artist.lower().split()[0] in r["artistName"].lower() and title.lower().split("(")[0].strip() in r["trackName"].lower() and not BAD.search(r["trackName"]) and not VER.search(r["trackName"])]
    res.sort(key=lambda r: (r["trackName"].lower() != title.lower(), "&" in r["artistName"] or "," in r["artistName"]))  # exact original title first
    for r in res:
            urllib.request.urlretrieve(r["previewUrl"], out); return dict(file=out, track=r["trackName"], album=r["collectionName"], ms=r["trackTimeMillis"])
    return None
def _ytdlp(args, timeout=180):
    return subprocess.run(["yt-dlp", "--no-warnings", "--no-cache-dir", *args], capture_output=True, text=True, timeout=timeout)
def _search(prefix, q, n=6):
    r = _ytdlp(["--flat-playlist", "--print", "%(id)s|%(uploader)s|%(title)s|%(duration)s|%(webpage_url)s", f"{prefix}{n}:{q}"], 90)
    return [l.split("|") for l in r.stdout.splitlines() if l.count("|") >= 4]
def _ok_title(t, title): return title.lower().split("(")[0].strip() in t.lower() and not BAD.search(t) and not re.search(r"(?i)\bmix\b|edition|extended|re-?record", t)
def candidates(title, artist):
    q = f"{artist} {title}"
    for i, up, t, d, url in _search("ytsearch", q + " official audio", 8):
        if _ok_title(t, title) and (artist.split()[0].lower() in up.lower()): yield ("youtube", url, f"{up} | {t}")
    for i, up, t, d, url in _search("scsearch", q, 5):
        if _ok_title(t, title) and artist.split()[0].lower() in up.lower(): yield ("soundcloud", url, f"{up} | {t}")
    try:
        a = _http_json("https://archive.org/advancedsearch.php?" + urllib.parse.urlencode({"q": f'title:("{title}") AND creator:("{artist}") AND mediatype:audio', "fl[]": "identifier,title,creator", "rows": 5, "output": "json"}))
        for d in a["response"]["docs"]: yield ("archive.org", f"https://archive.org/details/{d['identifier']}", f"{d.get('creator')} | {d.get('title')}")
    except Exception: pass
def _download(src, url, out_base):
    tries = [[]] if src != "youtube" else [[] if c is None else ["--extractor-args", f"youtube:player_client={c}"] for c in YT_CLIENTS]
    for extra in tries:
        r = _ytdlp([*extra, "--no-playlist", "-q", "-f", "bestaudio[ext=m4a]/bestaudio", "-x", "--audio-format", "m4a", "-o", out_base + ".%(ext)s", url], 240)
        if os.path.exists(out_base + ".m4a"): return out_base + ".m4a", (extra[-1] if extra else "default")
        if "DRM" in r.stderr: return None, "DRM"
    return None, (r.stderr.strip().splitlines() or ["fail"])[-1][:120]
def auto(key, title, artist, min_score=0.9, max_tries=6, machine="79feea1a-ffa0-4e22-a698-a8a772db5260", log=print):
    """Box-first fetch + verify. Returns dict(ok, file, source, xcorr, preview_at_s, tried=[...]) or, if every box source fails,
    ok=False with mac_fallback commands (plan_cmd) for the agent to run on the Mac."""
    prev = os.path.join(HERE, f"{key}_preview.m4a")
    pv = apple_preview(title, artist, prev) if not os.path.exists(prev) else dict(file=prev)
    if not pv: return dict(ok=False, reason="no Apple preview found (cannot verify)", tried=[])
    tried, tmp = [], tempfile.mkdtemp()
    for n, (src, url, label) in enumerate(candidates(title, artist)):
        if n >= max_tries: break
        f, how = _download(src, url, os.path.join(tmp, f"c{n}"))
        if not f: tried.append(dict(src=src, url=url, label=label, result=how)); log(f"  {src} {label}: {how}"); continue
        off, s, med = _score(f, prev)
        tried.append(dict(src=src, url=url, label=label, client=how, xcorr=round(s, 3))); log(f"  {src} {label}: xcorr {s:.3f}")
        if s >= min_score:
            dst = os.path.join(HERE, f"{key}_{src.replace('.', '')}.m4a"); shutil.move(f, dst)
            return dict(ok=True, file=dst, source=f"{src} {url} ({label}, client {how}) from the box", xcorr=round(s, 3), preview_at_s=off, preview=prev, tried=tried)
    return dict(ok=False, reason="no box source passed >= 0.9", tried=tried, mac_fallback=plan_cmd(title, artist, machine))

if __name__ == "__main__": _main()
