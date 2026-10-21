"""One-line brief -> plan -> QA (incl. logic check) -> backtest gate -> animatic + CapCut draft (dry run, no generation).
Live mode (Phase F) inserts: generate stills/gens (credit-gated) -> per-gen QA judgement -> reroll_decision -> final_cmd.
python3 -m hookforge.pipeline "3-2-1 video for the Grinch robe" [--force] [--no-render]
"""
import os, sys, re, json, shutil, subprocess, copy
import numpy as np
from .config import REPO, IPHONE12_SUFFIX
from . import planner, qa, profiles, autoedit, capcut_export
from .format_defaults import FORMATS

def slug(s): return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")[:48]

def gate_features(plan):
    F = FORMATS[plan["brief"]["format"]]; shots = plan["shots"]
    lens = [s["t1"] - s["t0"] for s in shots[1:]]
    feat = dict(format=plan["brief"]["format"], category=profiles.load(plan["product"]["key"])["category"], duration=plan["duration"],
                first_cut=plan["hook_s"], shot_len_med=float(np.median(lens)), text_y_frac=plan["text_style"].get("center_y_frac", 0.19),
                hook_s=plan["hook_s"], product_visible_0=(plan["brief"]["format"] != "F04"), is_experiment=plan["brief"]["slot"] == "experiment",
                prompts=[g["prompt"] for g in plan["gens"]] + [g["start_frame"]["prompt"] for g in plan["gens"]], _suffix=IPHONE12_SUFFIX.strip(),
                multi_card=int(len(plan["text_cards"]) > 1), night=1, people_n=2)
    for p in F["psych"]: feat[p] = 1
    return feat

def md(plan, lc, pc, bt):
    L = [f"# Dry run: {plan['brief']['brief']}", "", f"**Product:** {plan['product']['display']} (energy {plan['product']['energy']}/5)  ",
         f"**World:** {plan['product']['world']}  ", f"**Format:** {plan['brief']['format']} {plan['fit']['title']} - fit **{plan['fit']['verdict']}** (score {plan['fit']['score']}, video energy {plan['fit']['video_energy']})  ",
         f"**Slot:** {plan['brief']['slot']}  ", "", "## Why this format for this product"] + [f"- {r}" for r in plan["why_this_format"]] + \
        [f"- Setting: **{plan['setting']}** - adaptation: {plan['adaptation']}", "", "Alternatives considered: " + ", ".join(f"{a['format']} {a['title']} ({a['verdict']} {a['score']})" for a in plan["alternatives"]), "",
         "## Hook + text cards", f"Hook: **{plan['hook']['text']}** [{plan['hook']['tag']}] - {plan['hook']['why']}" + (f" (cards from {plan['hook'].get('cards_source')})" if plan['hook'].get('cards_source') else ""), ""] + \
        [f"- {c['t']:.2f}-{c['t']+c['dur']:.2f}s: {c['text']}" for c in plan["text_cards"]] + \
        [f"Text style: {plan['text_style']['source']} (CapCut y {plan['text_style']['capcut_y']}, size {plan['text_style']['size']}, stroke {plan['text_style']['stroke']})", "",
         "## Shot list", "| shot | time | gen | description |", "|---|---|---|---|"] + \
        [f"| {s['code']} | {s['t0']:.1f}-{s['t1']:.1f} | {s['gen']} | {s['desc']} |" for s in plan["shots"]] + \
        ["", "## Generations + credit estimate", "| gen | model | res | dur | cut | credits |", "|---|---|---|---|---|---|"] + \
        [f"| {g['id']} | {g['model']} + still gpt_image_2 | {g['res']} | {g['dur']}s | {g.get('cut','-')} | {g['credits']} |" for g in plan["gens"]] + \
        [f"| **total** | | | | | **{plan['credits']['total']}** / budget {plan['credits']['budget']} ({'OK' if plan['credits']['within_budget'] else 'OVER'}) |",
         f"Re-roll reserve (worst case 1 shot, D33): +{plan['credits']['reroll_reserve_max_1_shot']} cr. Costs: {plan['credits']['source']}.", "", "## Prompts (verbatim)"]
    for g in plan["gens"]:
        L += [f"### {g['id']} start frame (GPT Image 2)", "```", g["start_frame"]["prompt"], "```", f"### {g['id']} video (Seedance 2.5 {g['res']} 4 s)", "```", g["prompt"], "```"]
    ar = plan["gens"][0].get("alt_recreate")
    if ar:
        L += [f"### H alternative: recreate workhorse (MP2-2, {ar['source']})", f"Refs: {ar['refs']}; rolls: {ar['rolls']} (D45); checks: {ar['checks'] or 'PASS'}; {ar['note']}", "```", ar["prompt"], "```"]
    rc = [f"{g['id']}: {g['recreate_checks']}" for g in plan["gens"] if g.get("recreate_checks")]
    if rc: L += ["Recreate checks: " + "; ".join(rc)]
    m = plan["music"]
    L += ["", "## Music + caption", f"Song: **{m['pick']['song']}** - {m['pick']['version']}, start {m['pick']['offset_s']} s - {m['pick']['why']}" if m["pick"] else "Song: NONE PROVEN",
          "Alternatives: " + ", ".join(f"{x['song']} ({x['why']})" for x in m["alternatives"]),
          "Rejected: " + "; ".join(f"{x['song']}: {x['reason']}" for x in m["rejected"]),
          f"Caption: `{plan['caption']['text']}` - {plan['caption']['why']}",
          f"Posting: page {plan['posting']['page']}, exploit {plan['posting']['exploit_windows_pt']} PT, explore {plan['posting']['explore_windows_pt']} ({int(plan['posting']['explore_share']*100)}%)", "",
          "## Hook option", (f"**{plan['hook_option']['option']}** ({'INNOVATION SLOT' if plan['hook_option']['experiment_only'] else 'core-eligible'}), cover={plan['hook_option']['cover']}, reveal by {plan['hook_option']['reveal_s']} s; refs: {plan['hook_option']['refs']}; cover variants: {plan['hook_option']['cover_variants']}"
                             if plan.get("hook_option") else "default (format native)") + f" - options for this product: {[(o['format'], o['option']) for o in plan.get('hook_options_available', [])]}", "",
          "## QA", f"Plan checks: {'PASS' if not pc else pc}", f"Logic check: {'PASS' if lc['passed'] else 'FAIL'} - issues {lc['issues']}; notes {lc['notes']}", f"Reviewer question: {lc['reviewer_question']}",
          qa.CHECKLIST, "",
          "## Pre-flight prompt linter (D42 failure memory)",
          f"Result: {'CLEAN' if plan['preflight_lint']['preflight']['ok'] else 'FIX'} - {plan['preflight_lint']['reason']} ({plan['preflight_lint']['preflight']['n_rules']} rules)",
          *[f"- {r['gen']} {r['kind']}: " + "; ".join(f"[{h['severity']}] {h['rule_id']} '{h['trigger'][:40]}' -> {h['fix'][:120]}" for h in r["hits"]) for r in plan["preflight_lint"]["preflight"]["rows"] if r["hits"]],
          "", "## Backtest gate (D35)", f"Verdict: **{bt['verdict']}**", "Fix-list: " + ("; ".join(bt["fix_list"]) or "none"),
          f"Predicted views (informational, LOO AUC 0.65): {bt.get('band')}",
          f"Psych codebook score (ADVISORY, D35): {json.dumps(bt.get('psych_advisory', {}).get('score'))} - codes on: {[k for k, v in bt.get('psych_advisory', {}).get('codes', {}).items() if v]}; notes {bt.get('psych_advisory', {}).get('notes')}",
          f"Tier-1 audience score (ADVISORY, never blocks): {json.dumps(bt.get('tier1_advisory'), ensure_ascii=False, default=str)[:600]}", "Nearest own winners: " + ", ".join(f"{x['key']} {int(x['views']):,}" for x in bt["neighbours"]["own_winners"]),
          "Nearest own flops: " + ", ".join(f"{x['key']} {int(x['views']):,}" for x in bt["neighbours"]["own_flops"]),
          "Nearest external 1M+: " + ", ".join(f"{x['key']} {int(x['views']):,} (w {x['w']})" for x in bt["neighbours"]["external"]), "",
          f"Plug-ins used: {plan['provenance']}", "", "Files: plan.json, animatic.mp4 (mock clips, NOT for posting), capcut/<draft>/ (mock clips, text cards; music added in CapCut)."]
    return "\n".join(L)

def run(brief, out_root=None, force=False, render=True):
    from backtest import backtest as BT
    out_root = out_root or os.path.join(REPO, "out", "dryrun")
    p = planner.plan(brief, force=force)
    if p.get("mode") == "recreate":   # D61 default: recreate an existing winning reel
        from . import recreate_mode
        r = recreate_mode.dry_run(os.path.join(out_root, "recreate_" + slug(brief)), p["product_key"])
        return dict(status="OK", mode="recreate", dir=os.path.dirname(r["sheet"]), sheet=r["sheet"], checks=r["plan"]["checks"]["ok"])
    d = os.path.join(out_root, slug(brief)); os.makedirs(d, exist_ok=True)
    if p["status"] == "REJECTED":
        txt = (f"# REJECTED: {brief}\n\nFit verdict {p['fit']['verdict']} (score {p['fit']['score']}).\n\n" + "\n".join(f"- {r}" for r in p["fit"]["reasons"])
               + "\n\nUse instead: " + ", ".join(f"{a['format']} {a['title']} ({a['verdict']})" for a in p["alternatives"]) + "\n")
        open(os.path.join(d, "REJECTED.md"), "w").write(txt); return dict(status="REJECTED", dir=d, plan=p)
    prof = profiles.load(p["product"]["key"])
    lc = qa.logic_check(p, prof); pc = qa.plan_checks(p)
    from . import runner
    p["preflight_lint"] = runner.submit(p)          # D42: linter runs before any generation (dry: never submits)
    bt = BT.run(gate_features(p))
    try:   # advisory tier-1 audience score (audience/tools/tier1_score.py) - never blocks, never changes the verdict (D35)
        sys.path.insert(0, os.path.join(REPO, "audience", "tools")); import tier1_score
        ex = (p["posting"]["exploit_windows_pt"] or ["18-21"])[0]
        bt["tier1_advisory"] = tier1_score.score(dict(hook_text=p["hook"]["text"], caption=p["caption"]["text"], text_cards=[c["text"] for c in p["text_cards"]],
                                                      prompts=[g["prompt"] for g in p["gens"]], song=(p["music"]["pick"] or {}).get("version", ""),
                                                      post_hour_pt=int(ex.split("-")[0]), presenter="none", collab_us_creator=False, product_world=p["product"]["world"]))
    except Exception as e: bt["tier1_advisory"] = dict(error=str(e)[:200])
    try:
        from . import psych; bt["psych_advisory"] = psych.score(p)
    except Exception as e: bt["psych_advisory"] = dict(error=str(e)[:200])
    pub = copy.deepcopy(p); src = pub.get("mock_source") or {}; src.pop("file", None)
    json.dump(dict(plan=pub, qa=dict(plan_checks=pc, logic=lc), backtest=bt), open(os.path.join(d, "plan.json"), "w"), indent=1, ensure_ascii=False, default=str)
    open(os.path.join(d, "PLAN.md"), "w").write(md(p, lc, pc, bt))
    # CapCut draft (mock media) for review in CapCut
    name = "DRY_" + slug(brief)[:24].upper()
    if p.get("mock_source"):
        mdir = os.path.join(d, "capcut_media"); os.makedirs(mdir, exist_ok=True)
        mf = os.path.join(mdir, "mock_source.mp4")
        if not os.path.exists(mf): shutil.copy(p["mock_source"]["file"], mf)
        pr = qa.probe(mf)
        mac = "/Users/omar/Movies/CapCut/User Data/Projects/com.lveditor.draft"
        cplan = dict(name=name, canvas=[1080, 1920], fps=30, clip_audio_volume=1.0, mac_draft_root=mac,
                     media_root_map=(mdir, f"{mac}/{name}/media"),
                     shots=[dict(file=mf, clip_start=s["t0"], dur=s["t1"] - s["t0"], speed=1.0, clip_dur=pr["dur"], w=pr["w"], h=pr["h"]) for s in p["shots"]],
                     texts=[dict(t=c["t"], dur=c["dur"], text=c["text"], y=p["text_style"]["capcut_y"], scale=c.get("scale")) for c in p["text_cards"]])
        cdir = capcut_export.export(cplan, os.path.join(d, "capcut"))
        os.makedirs(os.path.join(cdir, "media"), exist_ok=True); shutil.move(mf, os.path.join(cdir, "media", "mock_source.mp4")); shutil.rmtree(mdir, ignore_errors=True)
        probs = capcut_export.verify(cdir)
    else: probs = ["no mock source"]
    cmd = autoedit.animatic_cmd(p, os.path.join(d, "animatic.mp4"))
    open(os.path.join(d, "render_animatic.sh"), "w").write("#!/bin/sh\n" + " ".join("'" + c.replace("'", "'\\''") + "'" for c in cmd) + "\n")
    media = {}
    if render:
        subprocess.run(["nice", "sh", os.path.join(d, "render_animatic.sh")], timeout=900)
        an = os.path.join(d, "animatic.mp4")
        if os.path.exists(an):
            cdir_ = os.path.join(d, "covers"); os.makedirs(cdir_, exist_ok=True)
            for c in p["covers"]:
                subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(c["t"]), "-i", an, "-frames:v", "1", os.path.join(cdir_, f"cover_{c['role']}_{c['t']}s.jpg")], timeout=60)
            try:
                fc = qa.final_checks(an, os.path.join(d, "preflight"), final=False)
                media["preflight_preview"] = dict(aspect_ok=fc["aspect_ok"], size=f"{fc['width']}x{fc['height']}", loudness=fc["loudness"], problems=fc["problems"],
                                                  contact_sheet=os.path.relpath(fc["contact_sheet"], d), provenance=fc["provenance"])
            except Exception as e: media["preflight_preview"] = dict(error=str(e)[:200])
            if p.get("mock_source"):
                try:
                    og = qa.originality_gate(an, [p["mock_source"]["file"]])
                    media["originality_sanity"] = dict(verdict=og["verdict"], q_match=og["worst"].get("q_match"), r_match=og["worst"].get("r_match"),
                                                       note="animatic vs its own mock source: expected HIGH match (proves the PDQ gate detects re-uses)")
                except Exception as e: media["originality_sanity"] = dict(error=str(e)[:200])
            try:   # D44 export path test: the same clean re-encode every final export uses, then the provenance assert
                ce = autoedit.clean_export(an, os.path.join(d, "export_test_clean.mp4"))
                fcc = qa.final_checks(ce["path"], os.path.join(d, "preflight_export"), final=True)
                media["export_clean_test"] = dict(file="export_test_clean.mp4", provenance=ce["provenance"],
                                                  provenance_blocks=[x for x in fcc["problems"] if "provenance" in x.lower()],
                                                  note="animatic run through autoedit.clean_export (D44); not a postable file")
            except Exception as e: media["export_clean_test"] = dict(error=str(e)[:300])
        json.dump(media, open(os.path.join(d, "media_qa.json"), "w"), indent=1, default=str)
        with open(os.path.join(d, "PLAN.md"), "a") as fh:
            fh.write("\n\n## Media QA on the animatic (preview, not a final)\n```\n" + json.dumps(media, indent=1, default=str)[:3000] + "\n```\n")
    return dict(status="OK", dir=d, fit=p["fit"]["verdict"], logic=lc["passed"], plan_checks=pc, gate=bt["verdict"], fix=bt["fix_list"],
                credits=p["credits"]["total"], capcut_problems=probs)

if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    print(json.dumps(run(a[0], force="--force" in sys.argv, render="--no-render" not in sys.argv), indent=1, default=str))
