"""D91 #3 CAPCUT LEARNING LOOP: diff Omar's edited CapCut draft against the draft we exported, log the differences,
and learn pacing/cut corrections. Read-only on drafts (Omar's Mac drafts are copied to the box first).
  d = capcut_learn.diff(our_draft_dir, omar_draft_dir, run_id="...")  -> dict, appended to learning/capcut_diffs.jsonl
  capcut_learn.learned()  -> learning/capcut_learned.json: median shot-duration ratio by position (hook/body/end),
     cut add/remove rate, speed changes, text edits; a correction becomes a SUGGESTED rule once seen in >= MIN_N runs
     with a consistent direction (>= 75 %). Suggestions are never auto-applied to edit_rules; Omar/agent promotes them."""
import os, json, statistics as S
from .config import REPO
US = 1_000_000
LOG = os.path.join(REPO, "learning", "capcut_diffs.jsonl")
OUT = os.path.join(REPO, "learning", "capcut_learned.json")
MIN_N, AGREE = 3, 0.75

def read(folder):
    d = json.load(open(os.path.join(folder, "draft_info.json")))
    mats = {m["id"]: m for v in d["materials"].values() if isinstance(v, list) for m in v if isinstance(m, dict) and "id" in m}
    shots, texts, music = [], [], []
    for tr in d["tracks"]:
        for s in sorted(tr["segments"], key=lambda s: s["target_timerange"]["start"]):
            t0, du = s["target_timerange"]["start"] / US, s["target_timerange"]["duration"] / US
            m = mats.get(s["material_id"], {})
            if tr["type"] == "video":
                src = s.get("source_timerange") or {}
                shots.append(dict(t=t0, dur=du, speed=float(s.get("speed", 1.0)), src=os.path.basename(m.get("path", "")), src_start=(src.get("start") or 0) / US))
            elif tr["type"] == "text":
                try: txt = json.loads(m.get("content", "{}")).get("text", "")
                except Exception: txt = ""
                texts.append(dict(t=t0, dur=du, text=txt, y=(s.get("clip") or {}).get("transform", {}).get("y")))
            elif tr["type"] == "audio": music.append(dict(t=t0, dur=du, src_start=((s.get("source_timerange") or {}).get("start") or 0) / US, volume=s.get("volume")))
    return dict(shots=shots, texts=texts, music=music, total=sum(s["dur"] for s in shots))

def _pos(i, n): return "hook" if i == 0 else ("end" if i == n - 1 else "body")

def diff(ours, omars, run_id="", log=True):
    a, b = read(ours), read(omars)
    pairs, used = [], set()
    for i, s in enumerate(a["shots"]):   # match by source clip, nearest timeline position
        cand = [(abs(o["t"] - s["t"]), j) for j, o in enumerate(b["shots"]) if o["src"] == s["src"] and j not in used]
        if cand: j = min(cand)[1]; used.add(j); pairs.append((i, j))
    n = len(a["shots"])
    shots = [dict(pos=_pos(i, n), ours=a["shots"][i]["dur"], omar=b["shots"][j]["dur"], ratio=round(b["shots"][j]["dur"] / max(a["shots"][i]["dur"], 1e-3), 3),
                  trim_in=round(b["shots"][j]["src_start"] - a["shots"][i]["src_start"], 3), speed=(a["shots"][i]["speed"], b["shots"][j]["speed"])) for i, j in pairs]
    r = dict(run_id=run_id, total=(round(a["total"], 3), round(b["total"], 3)), n_shots=(n, len(b["shots"])),
             removed=[a["shots"][i]["src"] for i in range(n) if i not in {p[0] for p in pairs}],
             added=[b["shots"][j]["src"] for j in range(len(b["shots"])) if j not in used],
             reordered=[p[1] for p in pairs] != sorted(p[1] for p in pairs), shots=shots,
             speed_changes=sum(1 for s in shots if abs(s["speed"][0] - s["speed"][1]) > 1e-3),
             text_changes=[(x.get("text"), y.get("text")) for x, y in zip(a["texts"], b["texts"]) if x.get("text") != y.get("text")] + [(None, y["text"]) for y in b["texts"][len(a["texts"]):]],
             music_offset_delta=round(b["music"][0]["src_start"] - a["music"][0]["src_start"], 3) if a["music"] and b["music"] else None)
    if log:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, "a") as fh: fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        learned()
    return r

def learned(path=None):
    path = path or LOG; rows = [json.loads(l) for l in open(path)] if os.path.exists(path) else []
    by = {}
    for r in rows:
        for s in r["shots"]: by.setdefault(s["pos"], []).append(s["ratio"])
    out = dict(n_runs=len(rows), pacing={}, suggestions=[])
    for pos, rs in by.items():
        med = S.median(rs); out["pacing"][pos] = dict(n=len(rs), median_ratio=round(med, 3))
        runs_dir = [S.median([s["ratio"] for s in r["shots"] if s["pos"] == pos]) for r in rows if any(s["pos"] == pos for s in r["shots"])]
        for sign, word in ((1, "longer"), (-1, "shorter")):
            agree = sum(1 for x in runs_dir if (x - 1) * sign > 0.05) / max(1, len(runs_dir))
            if len(runs_dir) >= MIN_N and agree >= AGREE:
                out["suggestions"].append(dict(rule=f"{pos} shots {word}: x{round(med, 2)}", runs=len(runs_dir), agree=round(agree, 2), status="SUGGESTED (not auto-applied)"))
    if rows:
        out["cuts"] = dict(added_per_run=round(S.mean(len(r["added"]) for r in rows), 2), removed_per_run=round(S.mean(len(r["removed"]) for r in rows), 2),
                           speed_changes_per_run=round(S.mean(r["speed_changes"] for r in rows), 2), total_ratio=round(S.median(r["total"][1] / max(r["total"][0], 1e-3) for r in rows), 3))
        if len(rows) >= MIN_N and sum(len(r["removed"]) > 0 for r in rows) / len(rows) >= AGREE:
            out["suggestions"].append(dict(rule="Omar removes shots in most runs: plan fewer shots", runs=len(rows), status="SUGGESTED (not auto-applied)"))
    if path == LOG: json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)
    return out
