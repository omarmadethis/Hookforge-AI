"""D72 one-off: backfill learning/spend_ledger.csv with OUR 2026-10-19 Higgsfield outputs found in out/live (read-only scan).
job_id = Higgsfield output id from urls.txt / video_prompts.json / CLIP_PLAN short ids; when a file names no id, a stable
'noid:<run>/<item>' key is used and id_source says so. Credits: images 1 each (billed), clips from CLIP_PLAN get_cost/billed."""
import csv, json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "engine"))
from hookforge import gates as G
L = os.path.join(G.REPO, "out/live")
def rows():
    out = []
    for run in ("trumpglow_A", "trumpglow_B", "trumpglow_C"):
        f = os.path.join(L, run, "start_frames/urls.txt")
        for u in open(f).read().split():
            m = re.search(r"hf_(\d{8})_(\d{6})_([0-9a-f-]{36})", u)
            out.append((run, m.group(3), "start_frame", "gpt_image_2", "image", 1.0, f"output id from {run}/start_frames/urls.txt"))
    for run in ():   # Jolly Glow frames + clips were already logged live by the Jolly Glow worker (shared ledger)
        d = os.path.join(L, run, "start_frames"); ids = dict(re.findall(r"(F\d+_v\d+) \(([0-9a-f]{8})\)", open(os.path.join(L, run, "CLIP_PLAN.md")).read()))
        for fn in sorted(os.listdir(d)):
            k = fn[:-4]; out.append((run, ids.get(k) or f"noid:{run}/{k}", k, "gpt_image_2", "image", 1.0,
                                     f"short id from {run}/CLIP_PLAN.md" if k in ids else f"no id in files; {run}/start_frames/{fn}"))
    vp = json.load(open(os.path.join(L, "trumpglow_A/video_prompts.json")))
    cost = {"G1": 64, "G2": 28, "G3": 28, "G4": 28}
    for g, v in vp.items(): out.append(("trumpglow_A", f"noid:trumpglow_A/{g}", g, "seedance_2_5", "video", cost[g], f"clip {v['res']}; start frame {v['sf']}; no clip job id in files"))
    out.append(("trumpglow_A", "noid:trumpglow_A/G5", "G5", "seedance_2_5", "video", 28, "G5 continuous door->reveal fix, 28 billed; no job id in files"))
    for run in ("trumpglow_B", "trumpglow_C"):
        for m in re.finditer(r"^\| ([BC]G\d)[^|]*\|[^|]*\| (\d) s / (\d+p)[^\n]*\| (\d+) \|\s*$", open(os.path.join(L, run, "CLIP_PLAN.md")).read(), re.M):
            if os.path.exists(os.path.join(L, run, "clips", m.group(1) + ".mp4")):
                out.append((run, f"noid:{run}/{m.group(1)}", m.group(1), "seedance_2_5", "video", float(m.group(4)), f"{m.group(2)}s {m.group(3)} per CLIP_PLAN get_cost; clip exists; no job id in files"))
    return out
if __name__ == "__main__":
    have = set()
    if os.path.exists(G.LEDGER): have = {r["job_ids"] for r in G.ledger_rows()}
    n = 0
    for run, jid, step, model, kind, cr, src in rows():
        if jid in have: continue
        G.ledger_add(run, jid, step, cr, model, f"{kind}; backfill; {src}"); n += 1
    print("added", n); 
    for r in sorted({x[0] for x in rows()}): print(r, G.our_spend(r))
    print("total", G.our_spend())
