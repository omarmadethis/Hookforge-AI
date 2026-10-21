"""Parse the team's CapCut drafts (draft_info.json) into edit tables joined to posted reels + Higgsfield clips.

Outputs (private, contain file names / reel ids):
  private/edits/edits.csv          one row per draft (timeline): duration, canvas, text cards, song + offset, joins
  private/edits/edit_segments.csv  one row per segment (video/text/audio) with exact timeline + source times
Public aggregate: engine/backtest/data/capcut_stats.json (cut fractions, text timing, song offsets; no names)

CapCut times are microseconds. Video segment: target_timerange (timeline), source_timerange (in the clip), speed.
Audio segment source start = the song section offset. Text: materials.texts[].content JSON -> text + style.
"""
import os, re, json, glob, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from hookforge.config import REPO

ROOT = "/workspace/team/mac/text/Movies/CapCut/User Data/Projects/com.lveditor.draft"
US = 1e6

def parse(path):
    d = json.load(open(path))
    mats = d.get("materials", {})
    by_id = {}
    for k, v in mats.items():
        if isinstance(v, list):
            for m in v:
                if isinstance(m, dict) and "id" in m: by_id[m["id"]] = (k, m)
    segs = []
    for ti, t in enumerate(d.get("tracks", [])):
        for s in t.get("segments", []):
            kind, m = by_id.get(s.get("material_id"), (t.get("type"), {}))
            tt = s.get("target_timerange") or {}; st = s.get("source_timerange") or {}
            row = dict(track=ti, track_type=t.get("type"), kind=kind, t_start=tt.get("start", 0) / US,
                       t_dur=tt.get("duration", 0) / US, src_start=(st or {}).get("start", 0) / US if st else None,
                       src_dur=(st or {}).get("duration", 0) / US if st else None, speed=s.get("speed", 1.0),
                       volume=s.get("volume"), y=((s.get("clip") or {}).get("transform") or {}).get("y"),
                       scale=((s.get("clip") or {}).get("scale") or {}).get("x"))
            if kind == "videos":
                p = m.get("path", ""); row.update(file=os.path.basename(p), mtype=m.get("type"),
                                                  w=m.get("width"), h=m.get("height"), clip_dur=m.get("duration", 0) / US)
            elif kind == "texts":
                try:
                    c = json.loads(m.get("content", "{}")); txt = c.get("text", ""); sty = (c.get("styles") or [{}])[0]
                    row.update(text=txt.replace("\n", " ").strip(), font_size=sty.get("size"),
                               stroke=(sty.get("strokes") or [{}])[0].get("width") if sty.get("strokes") else None)
                except Exception:
                    row.update(text=str(m.get("content", ""))[:200])
            elif kind == "audios":
                row.update(file=os.path.basename(m.get("path", "") or m.get("name", "")), audio_name=m.get("name"), mtype=m.get("type"))
            segs.append(row)
    return d, segs

def hf_id(fn):
    m = re.search(r"hf_(\d{8}_\d{6})_([0-9a-f-]{36})", fn or ""); return m.group(0) if m else None

def build():
    paths = sorted(p for p in glob.glob(f"{ROOT}/*/draft_info.json"))
    drafts, allsegs = [], []
    for p in paths:
        proj = os.path.basename(os.path.dirname(p)); recycled = ".recycle_bin" in p
        try:
            d, segs = parse(p)
        except Exception as e:
            print("fail", p, e); continue
        dur = d.get("duration", 0) / US
        vids = sorted([s for s in segs if s["kind"] == "videos" and s["t_dur"] > 0.05], key=lambda s: s["t_start"])
        cuts = sorted(set(round(s["t_start"], 2) for s in vids if 0.15 < s["t_start"] < dur - 0.15))
        texts = sorted([s for s in segs if s["kind"] == "texts"], key=lambda s: s["t_start"])
        auds = [s for s in segs if s["kind"] == "audios"]
        music = [a for a in auds if a.get("mtype") in ("extract_music", "music") or (a.get("audio_name") or "").lower().endswith((".mp3", ".m4a", ".wav"))]
        cname = d.get("canvas_config", {})
        meta = {}
        mp = os.path.join(os.path.dirname(p), "draft_meta_info.json")
        if os.path.exists(mp):
            try: meta = json.load(open(mp))
            except Exception: meta = {}
        tc = meta.get("tm_draft_create") or 0; tm = meta.get("tm_draft_modified") or tc
        row = dict(draft=proj, recycled=recycled, created=pd.to_datetime(tc, unit="us", utc=True).tz_convert("America/Los_Angeles"),
                   updated=pd.to_datetime(tm, unit="us", utc=True).tz_convert("America/Los_Angeles"),
                   duration=round(dur, 3), width=cname.get("width"), height=cname.get("height"), fps=d.get("fps"),
                   n_shots=len(cuts) + 1, first_cut=cuts[0] if cuts else dur, cuts=json.dumps(cuts),
                   cut_fracs=json.dumps([round(c / dur, 3) for c in cuts]) if dur else "[]",
                   last_shot_start_frac=round(cuts[-1] / dur, 3) if cuts and dur else None,
                   n_hf_clips=sum(1 for v in vids if hf_id(v.get("file"))), hf_clips=json.dumps([hf_id(v.get("file")) for v in vids]),
                   speed_changes=sum(1 for v in vids if abs((v.get("speed") or 1) - 1) > 0.01),
                   text_cards=json.dumps([{"t": round(t["t_start"], 2), "dur": round(t["t_dur"], 2), "text": t.get("text"), "y": t.get("y"), "size": t.get("font_size")} for t in texts], ensure_ascii=False),
                   hook_text=texts[0].get("text") if texts else "", n_text=len(texts),
                   text_change_times=json.dumps([round(t["t_start"], 2) for t in texts[1:]]),
                   text_y=texts[0].get("y") if texts else None, text_size=texts[0].get("font_size") if texts else None,
                   song=music[0].get("audio_name") if music else (auds[0].get("audio_name") if auds else None),
                   song_offset_s=round(music[0]["src_start"], 2) if music and music[0]["src_start"] is not None else None,
                   song_t_start=round(music[0]["t_start"], 2) if music else None,
                   clip_audio_volume=np.mean([v.get("volume") or 0 for v in vids]) if vids else None)
        drafts.append(row)
        for s in segs: s["draft"] = proj; allsegs.append(s)
    ed = pd.DataFrame(drafts); sg = pd.DataFrame(allsegs)
    ed = join_reels(ed)
    os.makedirs(f"{REPO}/private/edits", exist_ok=True)
    ed.to_csv(f"{REPO}/private/edits/edits.csv", index=False); sg.to_csv(f"{REPO}/private/edits/edit_segments.csv", index=False)
    stats(ed)
    return ed, sg

def _norm(t):
    return re.sub(r"[^a-z0-9 ]", "", (t if isinstance(t, str) else "").lower()).split()

def join_reels(ed):
    """Join draft -> posted reel by hook-text similarity + date proximity (draft created <= posted <= +3 d) + duration."""
    c = pd.read_csv(f"{REPO}/private/corpus/corpus.csv")
    own = c[(c.source == "own") & c.posted_pt.notna()].copy()
    own["posted"] = pd.to_datetime(own.posted_pt.str.replace(" PT", ""), errors="coerce").dt.tz_localize("America/Los_Angeles")
    out = []
    ed["created"] = pd.to_datetime(ed.created); ed["updated"] = pd.to_datetime(ed.updated)
    for r in ed.itertuples():
        a = set(_norm(r.hook_text)); best = (0, None, None)
        for o in own.itertuples():
            b = set(_norm(o.hook_text))
            if not a or not b: continue
            j = len(a & b) / len(a | b)
            REC = {"mom", "dad", "wife", "husband", "grandma", "grandpa", "sister", "brother", "mum", "girlfriend", "boyfriend"}
            if (a & REC) != (b & REC): j *= 0.5      # different recipient => different video (HJ-13 mom vs dad draft, style review)
            dt = (o.posted - r.created).total_seconds() / 86400 if pd.notna(o.posted) else 99
            dm = (o.posted - r.updated).total_seconds() / 86400 if pd.notna(o.posted) else 99
            if dt < -0.5 or dm > 4: continue
            sc = j - 0.03 * max(dt, 0)
            if sc > best[0]: best = (sc, o.key, dt)
        out.append(dict(reel_key=best[1] if best[0] >= 0.45 else None, join_score=round(best[0], 3), days_to_post=best[2]))
    j = pd.DataFrame(out)
    ed = pd.concat([ed.reset_index(drop=True), j], axis=1)
    # one draft per posted reel: best join score, then latest modified; the rest are variants
    ed["primary"] = False
    for k, g in ed[ed.reel_key.notna()].groupby("reel_key"):
        best = g.sort_values(["join_score", "updated"], ascending=[False, False]).index[0]
        ed.loc[best, "primary"] = True
    ed.loc[~ed.primary & ed.reel_key.notna(), "variant_of"] = ed.loc[~ed.primary & ed.reel_key.notna(), "reel_key"]
    ed.loc[~ed.primary, "reel_key"] = None
    v = c.set_index("key")["views"]
    ed["views"] = ed.reel_key.map(v)
    return ed

def stats(ed):
    e = ed[~ed.recycled]
    def q(s): s = pd.Series(s).dropna(); return {k: round(float(s.quantile(p)), 3) for k, p in [("p25", .25), ("med", .5), ("p75", .75)]} if len(s) else {}
    fr = [f for x in e.cut_fracs for f in json.loads(x)]
    w = e[e.views >= 50000]; f = e[(e.views < 10000) & e.views.notna()]
    out = {"n_drafts": int(len(ed)), "n_active": int(len(e)), "n_joined": int(e.reel_key.notna().sum()),
           "duration": q(e.duration), "first_cut": q(e.first_cut), "n_shots": q(e.n_shots), "last_shot_start_frac": q(e.last_shot_start_frac),
           "canvas": e.groupby(["width", "height"]).size().astype(int).to_dict().__repr__(), "speed_change_share": round(float((e.speed_changes > 0).mean()), 3),
           "text_y": q(e.text_y), "text_size": q(e.text_size), "n_text": q(e.n_text),
           "song_counts": e.song.fillna("none").str[:50].value_counts().head(12).to_dict(),
           "song_offsets": {s: q(g.song_offset_s) for s, g in e.groupby(e.song.fillna("none").str[:50]) if len(g) >= 3},
           "winners_vs_flops": {"n_w": int(len(w)), "n_f": int(len(f)),
                                "dur_w": q(w.duration), "dur_f": q(f.duration), "first_cut_w": q(w.first_cut), "first_cut_f": q(f.first_cut),
                                "shots_w": q(w.n_shots), "shots_f": q(f.n_shots)}}
    json.dump(out, open(f"{REPO}/engine/backtest/data/capcut_stats.json", "w"), indent=1, default=str, ensure_ascii=False)
    print(json.dumps(out, indent=1, default=str, ensure_ascii=False)[:3500])



def gen_index():
    """generation id -> {model, prompt, account, created} from hf_match logs + Claude-history prompt log."""
    idx = {}
    for f in glob.glob("/workspace/hf_match/generations_*.jsonl"):
        for l in open(f):
            d = json.loads(l)
            idx.setdefault(d["id"], dict(model=d.get("model"), gen_type=d.get("type"), account=d.get("account"),
                                         created_utc=d.get("created_utc"), prompt=d.get("prompt")))
    hp = "/workspace/claude-history/hf_generations.csv"
    if os.path.exists(hp):
        h = pd.read_csv(hp)
        for r in h.itertuples():
            for j in str(r.job_ids).split(";"):
                j = j.strip()
                if not j or j == "nan": continue
                e = idx.setdefault(j, {})
                if not e.get("prompt"): e["prompt"] = r.prompt
                e.update(resolution=r.resolution, duration=r.duration, tool_model=r.model, project=r.project)
    return idx

def clips():
    """One row per placed hf_ clip: which generation went into which slot of which posted reel."""
    ed = pd.read_csv(f"{REPO}/private/edits/edits.csv"); sg = pd.read_csv(f"{REPO}/private/edits/edit_segments.csv")
    idx = gen_index(); rows = []
    for d, g in sg[sg.kind == "videos"].groupby("draft"):
        e = ed[ed.draft == d].iloc[0]
        for i, s in enumerate(g.sort_values("t_start").itertuples()):
            hid = hf_id(s.file); gid = hid.split("_")[-1] if hid else None; gi = idx.get(gid, {}) if gid else {}
            rows.append(dict(draft=d, reel_key=e.reel_key, variant_of=e.get("variant_of"), views=e.views, slot=i, t_start=s.t_start, t_dur=s.t_dur,
                             src_start=s.src_start, src_dur=s.src_dur, clip_dur=s.clip_dur, speed=s.speed, w=s.w, h=s.h, file=s.file, gen_id=gid,
                             gen_found=bool(gi), model=gi.get("model") or gi.get("tool_model"), resolution=gi.get("resolution"),
                             prompt=(gi.get("prompt") or "")[:4000] if isinstance(gi.get("prompt"), str) else None))
    c = pd.DataFrame(rows); c.to_csv(f"{REPO}/private/edits/edit_clips.csv", index=False)
    print("clips", len(c), "hf", c.gen_id.notna().sum(), "found in gen logs", c.gen_found.sum(), "with prompt", c.prompt.notna().sum(),
          "in posted reels", c.reel_key.notna().sum())
    return c

if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "clips":
    clips()

if __name__ == "__main__" and len(sys.argv) == 1:
    build(); clips()
