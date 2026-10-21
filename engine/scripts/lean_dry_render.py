"""D151 end-to-end lean-plan dry render on existing LOCAL clips (no Higgsfield calls, no credits, nothing delivered).
Uses this week's real slot map (pages/videos) from concept_lab.weekly(write=False); anchor bodies + stand-in hooks
come from earlier local runs. Draft x264 renders (clean=False) - a live run still finishes through clean_export.
Checks: reveal detection on the payoff clip -> reveal-aware edit_plan -> render -> reveal_check per edit ->
gate_built (measured ordered shared frames <= 50% per page) on the actual files."""
import json, os, sys, collections, datetime
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from hookforge import concept_lab, lean_plan as L, lean_edit as E
from hookforge.config import REPO
O = os.path.join(REPO, "out")
SRC = {
 "trumpglow": dict(bodies={"B1": "live/trumpglow_A/clips/G3.mp4", "B2": "live/trumpglow_A/clips/G4.mp4", "B3": "live/trumpglow_A/clips/G5.mp4"},
                   hooks=["live/trumpglow_A/clips/G1.mp4", "live/trumpglow_B/clips/BG1.mp4", "live/trumpglow_C/clips/CG1.mp4", "live/trumpglow_A/clips/G2.mp4",
                          "live/trumpglow_B/clips/BG2.mp4", "live/trumpglow_C/clips/CG2.mp4", "live/trumpglow_B/clips/BG3.mp4"]),
 "purrventure_carrier": dict(bodies={"B1": "pv_clips/P3_G2.mp4", "B2": "pv_clips/P3_G3.mp4", "B3": "pv_clips/P3_G4.mp4"},
                   hooks=["pv_clips/P3_G1.mp4", "pv_clips/P1_G1.mp4", "pv_clips/P2_G1.mp4"]),
}
def main(products=("trumpglow", "purrventure_carrier")):
    day = datetime.date.today().isoformat(); out_dir = os.path.join(O, "lean_dryrun", day); os.makedirs(out_dir, exist_ok=True)
    sm = [m for m in concept_lab.weekly(write=False)["slot_map"] if m["product"] in products]
    res = dict(day=day, note="DRY RENDER - stand-in hooks, local clips, x264 draft; nothing generated/sent", products={})
    for pk in products:
        src = SRC[pk]; bodies = {k: os.path.join(O, v) for k, v in src["bodies"].items()}
        info = E.reveal_info(bodies["B3"]); rv = info["reveal_s"]
        psm = [m for m in sm if m["product"] == pk]
        vids = sorted({m["video"] for m in psm}, key=lambda v: int(v.rsplit("_V", 1)[1]))
        edits, worst = L.edit_plan(psm, {pk: rv}); paths = {}; vres = {}
        for i, v in enumerate(vids):
            e = edits[v]; hook = os.path.join(O, src["hooks"][i % len(src["hooks"])]); p = os.path.join(out_dir, f"{v}.mp4")
            rc = E.reveal_check(e, rv) if e else dict(ok=False, flag="no edit")
            if e and rc["ok"]:
                b = E.build(hook, bodies, e, p, clean=False); paths[v] = p
            vres[v] = dict(hook_standin=os.path.relpath(hook, O), edit=[(c, a / L.FPS, b_ / L.FPS) for c, a, b_ in e] if e else None,
                           planned_max_shared=worst.get(v), reveal=rc, duration=round(E.probe_dur(p), 3) if v in paths else None)
        by_page = collections.defaultdict(list)
        for m in psm:
            if m["video"] in paths and paths[m["video"]] not in by_page[m["page"]]: by_page[m["page"]].append(paths[m["video"]])
        g = E.gate_built(by_page)
        pairs = {}
        import itertools
        for pg, ps in by_page.items():
            for a, b in itertools.combinations(sorted(ps), 2):
                pairs[f"{pg}:{os.path.basename(a)[:-4]}~{os.path.basename(b)[:-4]}"] = round(E.measured_shared(a, b), 3)
        res["products"][pk] = dict(payoff_reveal=info, videos=vres, measured_pairs=pairs, max_measured=max(pairs.values(), default=0),
                                   overlap_gate=g, reveal_all_ok=all(x["reveal"]["ok"] for x in vres.values()))
    json.dump(res, open(os.path.join(out_dir, "report.json"), "w"), indent=1, default=str)
    return res
if __name__ == "__main__":
    r = main()
    for pk, x in r["products"].items():
        print(pk, "reveal", x["payoff_reveal"]["reveal_s"], x["payoff_reveal"]["kind"], "| videos", len(x["videos"]), "| reveal ok", x["reveal_all_ok"],
              "| max measured", x["max_measured"], "| overlap gate", x["overlap_gate"]["ok"], x["overlap_gate"]["violations"])
