"""D122 auto-reroll planner for AI-look warnings (ai_look: melting_product, warped_hands, plastic_skin, physics_error,
text_gibberish). For a flagged shot it proposes the CHEAPEST fix that clears it and queues it for Omar:
  1. retrim      0 cr  - a clean window inside the same clip that still covers the length the edit needs
  2. take_swap   0 cr  - an already-generated alternate take/variant of the same gen that reviews clean
  3. frame_swap  0 cr  - hold a clean frame as a still (only for very short beats <= HOLD_MAX_S)
  4. reroll      quoted - same gen re-submitted with a prompt patch for the tell; cost = runner pricing (still + video
                 if a new start frame is needed), approval_file_draft carries the cap. Nothing is ever submitted here.
propose(...) -> item dict; queue(item) -> learning/approval_queue/<id>.json (status AWAITING_OMAR_APPROVAL)."""
import os, json, datetime
import numpy as np
from zoneinfo import ZoneInfo
from . import ai_look, approval_queue, runner

PT = ZoneInfo("America/Los_Angeles")
HOLD_MAX_S = 0.8
PATCH = {
  "melting_product": "the product keeps one rigid, solid shape the whole shot - no bending, morphing or melting; slow, simple motion",
  "warped_hands":    "hands stay out of close-up or hold the product with five normal fingers; minimal hand motion",
  "plastic_skin":    "natural phone-camera skin texture, visible pores, no beauty filter",
  "physics_error":   "everything obeys gravity; no objects floating or merging; one simple action",
  "text_gibberish":  "no readable text, logos or labels anywhere in frame",
}

def locate(path, n=16, cuts=()):
    """Per-sample temporal jump (morph/melt locator, no model needed): returns [(t0, t1, jump)] between samples."""
    fr = ai_look.frames(path, n, size=224); out = []
    a = [(t, np.asarray(i.convert("L").resize((64, 112)), np.float32).ravel()) for t, i in fr]
    for (t0, x), (t1, y) in zip(a, a[1:]):
        if any(t0 <= c <= t1 for c in cuts): continue
        x, y = x - x.mean(), y - y.mean(); out.append((round(t0, 2), round(t1, 2), round(1 - float(x @ y / (np.linalg.norm(x) * np.linalg.norm(y) + 1e-6)), 3)))
    return out, (fr[-1][0] if fr else 0)

def clean_window(jumps, need_s, thr=0.35):
    """Longest run between bad jumps; returns (in, out) covering need_s or None."""
    if not jumps: return None
    bad = [(t0, t1) for t0, t1, j in jumps if j > thr]
    if not bad: return None
    edges = [jumps[0][0]] + [x for b in bad for x in b] + [jumps[-1][1]]
    best = max(((edges[i], edges[i + 1]) for i in range(0, len(edges) - 1, 2)), key=lambda w: w[1] - w[0])
    return best if best[1] - best[0] >= need_s else None

def propose(run_id, gen, review, clip_path, need_s, product, alt_takes=(), still_needed=False, plan=None):
    """gen = plan gen dict (id, prompt, res, dur, ...); review = ai_look.review_shot result; alt_takes = [{path, review}]."""
    tell = review.get("worst"); opts = []
    if tell == "melting_product" and clip_path and os.path.exists(clip_path):
        w = clean_window(locate(clip_path)[0], need_s)
        if w: opts.append(dict(fix="retrim", credits=0, detail=f"use {w[0]:.2f}-{w[1]:.2f}s of the same clip (needs {need_s}s; melt sits outside)", trim=dict(in_s=w[0], out_s=w[1])))
    for t in alt_takes:
        if (t.get("review") or {}).get("severity") == "ok":
            opts.append(dict(fix="take_swap", credits=0, detail=f"swap in already-generated take {os.path.basename(t['path'])} (reviews clean)", path=t["path"])); break
    if need_s <= HOLD_MAX_S and review.get("frames"):
        opts.append(dict(fix="frame_swap", credits=0, detail=f"hold a clean frame for {need_s}s (beat too short to read as a still)"))
    cost = runner._vid_cost(gen) + (runner.CREDITS["still_gpt_image_2"] if still_needed else 0)
    patch = PATCH.get(tell, "")
    rg = dict(gen, id=f"{gen['id']}_rr", prompt=(gen["prompt"].rstrip(". ") + ". " + patch) if patch else gen["prompt"])
    opts.append(dict(fix="reroll", credits=float(cost), detail=f"re-submit {gen['id']} ({gen.get('res')} {gen.get('dur')}s{' + new start frame' if still_needed else ''}) with patch: {patch}", gen=rg))
    opts.sort(key=lambda o: (o["credits"], ["retrim", "take_swap", "frame_swap", "reroll"].index(o["fix"])))
    rec = opts[0]; iid = f"aifix_{run_id}_{gen['id']}"
    it = dict(id=iid, kind="ai_look_fix", product=product, status="AWAITING_OMAR_APPROVAL", created_pt=datetime.datetime.now(PT).isoformat(timespec="seconds"),
              why=f"{gen['id']}: AI-look {tell} {review.get('worst_score')} ({review.get('severity')})", poc="ai_look D75; cheapest-fix policy D122",
              credits=rec["credits"], credit_cap=rec["credits"], recommended=rec["fix"], options=opts, ready_for_approval=True, run_id=run_id, gen=gen["id"])
    if rec["fix"] == "reroll":
        mini = dict(product_key=product, gens=[rec["gen"]]); it["plan"] = mini
        try: it["approval_file_draft"] = dict(runner.approval_template(mini, iid + "_run", credit_cap=rec["credits"]), approved_by="", approved_at_pt="", approval_quote="")
        except Exception as e: it["approval_file_draft"] = dict(error=f"{type(e).__name__}: {e}", credit_cap=rec["credits"])
    return it

def queue(it, dir_=None):
    d = dir_ or approval_queue.DIR; os.makedirs(d, exist_ok=True)
    json.dump(it, open(os.path.join(d, it["id"] + ".json"), "w"), indent=1, ensure_ascii=False, default=str); return it

def from_review(run_id, plan, review_out, clips, need_s, alt_takes=None, dir_=None):
    """review_out = ai_look.review(...) result; clips/need_s/alt_takes keyed by gen id. Queues one item per warned/absurd AI shot."""
    gens = {g["id"]: g for g in plan["gens"]}; items = []
    for r in review_out["results"]:
        if r.get("severity") not in ("warn", "absurd") or r["shot"] not in gens: continue
        it = propose(run_id, gens[r["shot"]], r, clips.get(r["shot"]), need_s.get(r["shot"], 1.5), plan.get("product_key"),
                     (alt_takes or {}).get(r["shot"], ()), plan=plan)
        items.append(queue(it, dir_))
    return items
