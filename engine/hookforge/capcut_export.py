"""Export a Hookforge edit plan as an editable CapCut (Mac, desktop 9.x) draft project.

Approach (DECISIONS D29): clone a REAL draft made by the team's own CapCut build (draft_info.json, new_version 185) and
rebuild its tracks from the plan, deep-copying a template segment + its material + every extra material it references
(speeds, canvases, sound-channel mappings, colors, animations, vocal separations, placeholder infos) with fresh UUIDs.
This keeps the exact schema the installed CapCut writes. pyJianYingDraft (0.3.1) was evaluated as the alternative: it
works but writes a JianYing-5.9/Windows `draft_content.json` (new_version 110), which the Mac CapCut 9.4 build may
or may not upgrade; see docs/CAPCUT_EXPORT.md.

Plan schema (engine edit_plan.json -> "capcut" block):
{ "name": "HF_<run_id>", "canvas": [1080, 1920], "fps": 30,
  "shots": [{"file": "/abs/path/clip.mp4", "clip_start": 0.0, "dur": 3.5, "speed": 1.0, "clip_dur": 4.04, "w": 1080, "h": 1920}],
  "texts": [{"t": 0.0, "dur": 12.0, "text": "DO NOT let your mom see this ❄️😳", "y": 0.62}],
  "music": {"file": "/abs/path/song.mp3", "offset": 0.1, "dur_total": 180.0, "volume": 1.0},
  "clip_audio_volume": 0.0, "media_root_map": ["/workspace/hookforge/runs", "/Users/omar/Movies/Hookforge"] }
CapCut text y = transform.y in [-1, 1], +up; text centre from top = (1 - y) / 2 of the height. Team median y 0.62 = 19 % from top.
Only ever write to a throwaway folder unless Omar approves writing into the Mac drafts folder.
"""
import copy, json, os, time, uuid, shutil

US = 1_000_000
TEMPLATE_DIR = ("/workspace/team/mac/text/Movies/CapCut/User Data/Projects/com.lveditor.draft/1009 (5)")  # MC-02 62.8K: 6 shots, 1 text, 1 song

def _uid(): return str(uuid.uuid4()).upper()

def _index(mats):
    idx = {}
    for k, v in mats.items():
        if isinstance(v, list):
            for m in v:
                if isinstance(m, dict) and "id" in m: idx[m["id"]] = k
    return idx

def _clone_with_refs(seg, tmats, tidx, out_mats):
    """Deep-copy a segment + its main material + extra refs into out_mats with fresh ids. Returns (seg, main_material)."""
    s = copy.deepcopy(seg); s["id"] = _uid()
    mk = tidx[seg["material_id"]]; mm = copy.deepcopy(next(m for m in tmats[mk] if m["id"] == seg["material_id"]))
    mm["id"] = _uid(); s["material_id"] = mm["id"]; out_mats.setdefault(mk, []).append(mm)
    refs = []
    for r in seg.get("extra_material_refs", []):
        k = tidx.get(r)
        if not k: continue
        em = copy.deepcopy(next(m for m in tmats[k] if m["id"] == r)); em["id"] = _uid()
        out_mats.setdefault(k, []).append(em); refs.append(em["id"])
    s["extra_material_refs"] = refs
    return s, mm

def _map(path, rmap):
    if rmap and path.startswith(rmap[0]): return rmap[1] + path[len(rmap[0]):]
    return path

def export(plan, out_root, template_dir=TEMPLATE_DIR):
    t = json.load(open(os.path.join(template_dir, "draft_info.json")))
    meta = json.load(open(os.path.join(template_dir, "draft_meta_info.json")))
    tmats, tidx = t["materials"], _index(t["materials"])
    tv = next(tr for tr in t["tracks"] if tr["type"] == "video"); tt = next(tr for tr in t["tracks"] if tr["type"] == "text")
    ta = next(tr for tr in t["tracks"] if tr["type"] == "audio")
    d = copy.deepcopy(t); d["id"] = _uid(); d["name"] = plan["name"]
    mats = {k: ([] if isinstance(v, list) else v) for k, v in tmats.items()}
    rmap = plan.get("media_root_map")
    # video
    vtrack = copy.deepcopy(tv); vtrack["id"] = _uid(); vtrack["segments"] = []; cur = 0
    for sh in plan["shots"]:
        s, m = _clone_with_refs(tv["segments"][0], tmats, tidx, mats)
        dur = int(round(sh["dur"] * US)); spd = float(sh.get("speed", 1.0))
        s["target_timerange"] = {"start": cur, "duration": dur}
        s["source_timerange"] = {"start": int(round(sh.get("clip_start", 0) * US)), "duration": int(round(dur * spd))}
        s["speed"] = spd; s["volume"] = float(sh.get("audio_gain", plan.get("clip_audio_volume", 1.0)))   # D63: keep natural sound; key real sound 2-4x; s["last_nonzero_volume"] = 1.0
        p = _map(sh["file"], rmap); m.update(path=p, material_name=os.path.basename(p), duration=int(round(sh.get("clip_dur", sh["dur"] + sh.get("clip_start", 0)) * US)),
                                             width=sh.get("w", 1080), height=sh.get("h", 1920), local_material_id="", unique_id="")
        for k in ("speeds",):
            for em in mats.get(k, []):
                if em["id"] in s["extra_material_refs"]: em["speed"] = spd
        vtrack["segments"].append(s); cur += dur
    total = cur
    # text
    ttrack = copy.deepcopy(tt); ttrack["id"] = _uid(); ttrack["segments"] = []
    for tx in plan.get("texts", []):
        s, m = _clone_with_refs(tt["segments"][0], tmats, tidx, mats)
        st = int(round(tx["t"] * US)); du = min(int(round(tx["dur"] * US)), total - st)
        s["target_timerange"] = {"start": st, "duration": du}
        s["clip"]["transform"]["y"] = float(tx.get("y", 0.62))
        if tx.get("scale"): s["clip"]["scale"] = {"x": float(tx["scale"]), "y": float(tx["scale"])}
        c = json.loads(m["content"]); txt = tx["text"]; c["text"] = txt
        n16 = len(txt.encode("utf-16-le")) // 2
        for sty in c.get("styles", []): sty["range"] = [0, n16]
        c["styles"] = c["styles"][:1]; m["content"] = json.dumps(c, ensure_ascii=False)
        ttrack["segments"].append(s)
    # audio
    atrack = copy.deepcopy(ta); atrack["id"] = _uid(); atrack["segments"] = []
    mu = plan.get("music")
    if mu:
        s, m = _clone_with_refs(ta["segments"][0], tmats, tidx, mats)
        s["target_timerange"] = {"start": 0, "duration": total}
        s["source_timerange"] = {"start": int(round(mu.get("offset", 0) * US)), "duration": total}
        s["volume"] = mu.get("volume", 1.0)
        p = _map(mu["file"], rmap); m.update(path=p, name=os.path.basename(p), duration=int(round(mu.get("dur_total", 240) * US)), music_id=_uid().lower(), local_material_id="", unique_id="")
        atrack["segments"].append(s)
    d["tracks"] = [vtrack, ttrack] + ([atrack] if mu else [])
    d["materials"] = mats; d["duration"] = total
    d["canvas_config"].update(width=plan.get("canvas", [1080, 1920])[0], height=plan.get("canvas", [1080, 1920])[1]); d["fps"] = float(plan.get("fps", 30))
    for k in ("cover", "retouch_cover", "static_cover_image_path"):
        if k in d: d[k] = None if k != "static_cover_image_path" else ""
    # write folder: draft_info.json + Timelines/<id>/draft_info.json (team drafts keep identical copies) + draft_meta_info.json
    out = os.path.join(out_root, plan["name"]); 
    if os.path.exists(out): shutil.rmtree(out)
    tl = _uid(); os.makedirs(os.path.join(out, "Timelines", tl))
    for p in (os.path.join(out, "draft_info.json"), os.path.join(out, "Timelines", tl, "draft_info.json")):
        json.dump(d, open(p, "w"), ensure_ascii=False)
    now = int(time.time() * US)
    meta.update(draft_id=d["id"], draft_name=plan["name"], draft_fold_path=plan.get("mac_draft_root", out_root) + "/" + plan["name"],
                tm_draft_create=now, tm_draft_modified=now, tm_duration=total, draft_timeline_materials_size_=0)
    for k in ("draft_cover", "draft_root_path"):
        if k in meta and k == "draft_root_path": meta[k] = plan.get("mac_draft_root", out_root)
    json.dump(meta, open(os.path.join(out, "draft_meta_info.json"), "w"), ensure_ascii=False)
    return out

def verify(folder):
    """Structural check: every segment material/extra ref resolves; timeline contiguous; returns list of problems."""
    d = json.load(open(os.path.join(folder, "draft_info.json"))); idx = _index(d["materials"]); probs = []; vlen = 0
    for tr in d["tracks"]:
        cur = 0
        for s in tr["segments"]:
            if s["material_id"] not in idx: probs.append(f"{tr['type']} seg missing material")
            probs += [f"{tr['type']} missing ref {r}" for r in s.get("extra_material_refs", []) if r not in idx]
            if tr["type"] == "video":
                if s["target_timerange"]["start"] != cur: probs.append("video gap/overlap")
                cur = s["target_timerange"]["start"] + s["target_timerange"]["duration"]; vlen = cur
    ids = [m["id"] for v in d["materials"].values() if isinstance(v, list) for m in v if isinstance(m, dict) and "id" in m]
    if len(ids) != len(set(ids)): probs.append("duplicate material ids")
    if d["duration"] != vlen: probs.append("duration != video length")
    return probs
