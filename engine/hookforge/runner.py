"""Generation runner front door. EVERY generation goes through this module: the D42 pre-flight linter runs first, then the live path,
which is behind an explicit approval gate and DISABLED by default (config.LIVE["enabled"] = False).

Live path design (Higgsfield is reached through its MCP tools, which only the agent can call, so the engine never talks to the network):
  start_run(plan, run_id)   -> lint + gate check, writes out/live/<run_id>/run.json with the ordered call list (still -> video per gen)
  next_call(run_id)         -> re-checks the gate, then returns the NEXT exact MCP call {namespace, tool, arguments}: first the get_cost
                               preflight for a step, then (after record_cost) the paid submission. Refuses when the cumulative cost would
                               pass the approved credit cap or the quoted cost differs from the plan estimate by more than the tolerance.
  record_cost / record_submit / record_result(run_id, ...)  -> the agent reports each MCP result back; attempts go to gen_failures.log_attempt.
  judge(run_id, step, clip) -> vision_judge (D33 absurd-failure judge); at most 1 re-roll per shot and only inside the credit cap.
Gate (all must hold): LIVE.enabled, live=True, approval file learning/approvals/<run_id>.json with approved_by == "Omar", matching
plan sha256 and gen ids, account == the namespace used, credit_cap >= the plan total, not expired, not already consumed.
No automatic resubmission on a transport timeout (Higgsfield guidance): the run stops and waits for the job id."""
import os, json, hashlib, datetime
from zoneinfo import ZoneInfo
from . import gen_failures as GF
from . import ref_gate
from .config import REPO, LIVE, CREDITS, REROLL

PT = ZoneInfo("America/Los_Angeles")
now = lambda: datetime.datetime.now(PT)

def preflight(plan):
    """Lint every prompt in the plan (video + start-frame still + recreate alt). Returns rows + overall ok."""
    rows = []
    for g in plan["gens"]:
        items = [("video", g["prompt"], g["model"]), ("still", g["start_frame"]["prompt"], "gpt_image_2")]
        if g.get("alt_recreate"): items.append(("recreate", g["alt_recreate"]["prompt"], g["model"]))
        for kind, pr, model in items:
            r = GF.lint(pr, model=model)
            rows.append(dict(gen=g["id"], kind=kind, model=model, ok=r["ok"], hits=r["hits"]))
    return dict(ok=all(r["ok"] for r in rows), rows=rows, n_rules=len(GF.rules()))

def plan_sha(plan):
    core = [dict(id=g["id"], model=g["model"], res=g["res"], dur=g["dur"], prompt=g["prompt"], still=g["start_frame"]["prompt"]) for g in plan["gens"]]
    return hashlib.sha256(json.dumps(core, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

def _vid_cost(g): return CREDITS["hook_1080p_4s"] if g["res"] == "1080p" and g["dur"] == 4 else (CREDITS["per_s_1080p"] if g["res"] == "1080p" else CREDITS["per_s_720p"]) * g["dur"]

def build_calls(plan, product_media_id="<PRODUCT_MEDIA_ID>", account=None, cast_media_ids=()):
    """Exact MCP payloads, in order. Video start_image = the still's job id ({job:<step>} is filled in from record_submit)."""
    ns = account or LIVE["account"]; calls = []
    for g in plan["gens"]:
        sid = f"{g['id']}_still"
        no_prod = "no product anywhere in frame" in g["prompt"].lower()   # e.g. F04 THEN hook: product ref would leak the product into the 'before'
        pm = ([] if no_prod else [dict(value=product_media_id, role="image")]) + [dict(value=c, role="image") for c in cast_media_ids]
        pr = ([] if no_prod else [dict(value=product_media_id, role="image_references")]) + [dict(value=c, role="image_references") for c in cast_media_ids]
        from .gates import DEFAULT_VARIANTS   # D115: same variant count the G5 quote bills (Omar reviews 2 per start frame)
        nv = int(g["start_frame"].get("n") or DEFAULT_VARIANTS)
        calls.append(dict(step=sid, gen=g["id"], kind="still", namespace=ns, tool="generate_image", expected_credits=CREDITS["still_gpt_image_2"] * nv,
                          params=dict(model=LIVE["still"]["model"], prompt=g["start_frame"]["prompt"], aspect_ratio=LIVE["still"]["aspect_ratio"],
                                      resolution=LIVE["still"]["resolution"], quality=LIVE["still"]["quality"], count=nv, use_unlim=False,
                                      medias=pm), refs=dict(product=[] if no_prod else [product_media_id], cast=list(cast_media_ids))))
        calls.append(dict(step=f"{g['id']}_video", gen=g["id"], kind="video", namespace=ns, tool="generate_video", expected_credits=_vid_cost(g),
                          params=dict(model=g["model"], prompt=g["prompt"], mode=LIVE["video"]["mode"], resolution=g["res"], duration=g["dur"],
                                      aspect_ratio=LIVE["video"]["aspect_ratio"], generate_audio=LIVE["video"]["generate_audio"], count=1, use_unlim=False,
                                      medias=[dict(value="{job:%s}" % sid, role="start_image")] + pr), refs=dict(product=[] if no_prod else [product_media_id], cast=list(cast_media_ids))))
    return calls

def build_calls_lean(plan, role, product_media_id="<PRODUCT_MEDIA_ID>", account=None, cast_media_ids=()):
    """D145: lean plan calls. role="anchor": all gens (H + B1-B3), 1 start-frame still each. role="extra": ONLY the new
    1080p hook (H) - the bodies come from the product's anchor run and are re-ordered/trimmed by lean_edit.build."""
    from .unique_footage import SharedFootage
    raise SharedFootage("BLOCK D180: lean clip reuse is permanently banned (supersedes D142/D145); plan every video in full")
    import copy
    p = copy.deepcopy(plan)
    p["gens"] = [g for g in p["gens"] if role == "anchor" or g["id"] == "H"]
    for g in p["gens"]:
        if g.get("start_frame"): g["start_frame"]["n"] = 1
    assert all(g["res"] == "1080p" for g in p["gens"] if g["id"] == "H"), "Omar: hooks are 1080p (D141)"
    return build_calls(p, product_media_id, account, cast_media_ids)

def assemble_lean(hook_file, anchor_bodies, edit, out_path, payoff_reveal_s=None):
    """D145/D147: render one lean video locally and refuse it if the payoff reveal check fails."""
    from .unique_footage import SharedFootage
    raise SharedFootage("BLOCK D180: lean assembly from shared anchor bodies is permanently banned")
    from . import lean_edit
    rv = payoff_reveal_s if payoff_reveal_s is not None else lean_edit.reveal_frame_s(anchor_bodies["B3"])
    rc = lean_edit.reveal_check(edit, rv)
    if not rc["ok"]: return dict(ok=False, reveal=rc)
    return dict(ok=True, reveal=rc, **lean_edit.build(hook_file, anchor_bodies, edit, out_path))

# ---------------- gate ----------------
def _approval_path(run_id): return os.path.join(REPO, LIVE["approvals_dir"], f"{run_id}.json")

def check_gate(plan, run_id, live=False, account=None):
    """Returns (ok, reasons). Pure check: reads files, never submits."""
    why = []
    if not LIVE["enabled"]: why.append("LIVE disabled in config (LIVE['enabled'] = False)")
    if not live: why.append("live=False")
    from . import audience_fit                      # D62: no live run unless song, emoji and captions pass AUDIENCE-FIT with evidence
    af = audience_fit.check_plan(plan, log=False)
    if not af["ok"]: why.append("AUDIENCE-FIT fail (D62): " + "; ".join(f"{r['kind']} {r['item']}: {r['reason']}" for r in af["rows"] if not r["ok"])[:400])
    from . import gates                              # D69: G1-G8 (incl. Omar's start-frame approval) before any video call
    gr = gates.run_all(plan, run_id=run_id, stage="video")
    why += [f"GATE {r['gate']}: {r['msg']}" for r in gr["blocks"]]
    p = _approval_path(run_id)
    if not os.path.exists(p): return False, why + [f"no approval file {os.path.relpath(p, REPO)}"]
    a = json.load(open(p)); total = sum(c["expected_credits"] for c in build_calls(plan))
    if a.get("approved_by") != "Omar": why.append("approval not by Omar")
    if a.get("run_id") != run_id: why.append("approval run_id mismatch")
    if a.get("plan_sha256") != plan_sha(plan): why.append("plan changed since approval (sha256 mismatch)")
    if sorted(a.get("gens") or []) != sorted(g["id"] for g in plan["gens"]): why.append("approved gen ids differ from the plan")
    if a.get("account") != (account or LIVE["account"]): why.append("approved account differs")
    if float(a.get("credit_cap", 0)) < total: why.append(f"credit cap {a.get('credit_cap')} < plan total {total}")
    try:
        if datetime.datetime.fromisoformat(a["expires_pt"]) < now(): why.append("approval expired")
    except Exception: why.append("approval has no valid expires_pt")
    if a.get("consumed"): why.append("approval already consumed (single use)")
    return (not why), why

def approval_template(plan, run_id, credit_cap=None, hours=24):
    """What the approval file must contain. Written ONLY by the parent after Omar approves in chat; this function just returns the dict."""
    total = sum(c["expected_credits"] for c in build_calls(plan))
    return dict(approved_by="Omar", approved_at_pt="<ISO time of Omar's message>", approval_quote="<Omar's exact approval words>", run_id=run_id,
                plan_sha256=plan_sha(plan), gens=[g["id"] for g in plan["gens"]], account=LIVE["account"],
                credit_cap=credit_cap or total, expires_pt=(now() + datetime.timedelta(hours=hours)).isoformat(timespec="seconds"), consumed=False)

# ---------------- run state machine ----------------
def _rd(run_id): return os.path.join(REPO, LIVE["runs_dir"], run_id)
def _load(run_id): return json.load(open(os.path.join(_rd(run_id), "run.json")))
def _save(run_id, st):                       # D128: atomic write - a crash mid-save can never leave a torn run.json
    os.makedirs(_rd(run_id), exist_ok=True); p = os.path.join(_rd(run_id), "run.json"); tmp = p + ".tmp"
    with open(tmp, "w") as fh: json.dump(st, fh, indent=1, ensure_ascii=False); fh.flush(); os.fsync(fh.fileno())
    os.replace(tmp, p)

def submit(plan, live=False, approved=False, run_id=None, product_media_id=None):
    """Back-compatible front door. Lint first; without the full gate it is a dry run and nothing is written or submitted."""
    pf = preflight(plan)
    if not pf["ok"]: return dict(submitted=False, reason="pre-flight linter FIX hits - fix prompts first", preflight=pf)
    if not (live and approved and run_id):
        return dict(submitted=False, reason="dry run (live submission needs LIVE enabled, live=True, run_id and Omar's approval file)", preflight=pf,
                    calls_preview=[dict(step=c["step"], tool=c["tool"], expected_credits=c["expected_credits"]) for c in build_calls(plan)])
    return start_run(plan, run_id, live=True, product_media_id=product_media_id)

def start_run(plan, run_id, live=False, product_media_id=None, cast_media_ids=()):
    pf = preflight(plan)
    if not pf["ok"]: return dict(submitted=False, reason="pre-flight linter FIX hits", preflight=pf)
    ok, why = check_gate(plan, run_id, live=live)
    if not ok: return dict(submitted=False, reason="approval gate closed", gate=why)
    if not product_media_id: return dict(submitted=False, reason="product_media_id required (upload the reviewed product photo first)")
    if not cast_media_ids: return dict(submitted=False, reason="cast_media_ids required (F88: cast reference images on every generation)")
    st = dict(run_id=run_id, plan_sha256=plan_sha(plan), started_pt=now().isoformat(timespec="seconds"), account=LIVE["account"],
              cap=json.load(open(_approval_path(run_id)))["credit_cap"], spent=0.0, calls=build_calls(plan, product_media_id, cast_media_ids=cast_media_ids), cursor=0, jobs={}, rerolls={}, log=[])
    _save(run_id, st); json.dump(plan, open(os.path.join(_rd(run_id), "plan.json"), "w"), indent=1, ensure_ascii=False)
    return dict(started=True, run_id=run_id, steps=[c["step"] for c in st["calls"]], cap=st["cap"])

def _fill(params, jobs):
    s = json.dumps(params)
    for k, v in jobs.items(): s = s.replace("{job:%s}" % k, v)
    return json.loads(s)

def next_call(run_id, live=True):
    """Exact next MCP call for the agent, or a refusal. Gate is re-checked on EVERY call."""
    st = _load(run_id); plan = json.load(open(os.path.join(_rd(run_id), "plan.json")))
    ok, why = check_gate(plan, run_id, live=live)
    if not ok: return dict(call=None, reason="approval gate closed", gate=why)
    if st["cursor"] >= len(st["calls"]): return dict(call=None, reason="run complete", spent=st["spent"])
    c = st["calls"][st["cursor"]]
    if c["step"] in st["jobs"]: return dict(call=None, reason=f"{c['step']} already submitted ({st['jobs'][c['step']]}); wait for its result, never resubmit")
    if "{job:" in json.dumps(_fill(c["params"], st["jobs"])): return dict(call=None, reason="waiting for the start-frame job id (record_submit)")
    if st["spent"] + c["expected_credits"] > st["cap"] + 1e-9: return dict(call=None, reason=f"credit cap: spent {st['spent']} + {c['expected_credits']} > cap {st['cap']}")
    from . import credit_ledger as _cl                                   # D120: running ledger warning before each call
    _pc = _cl.precheck(run_id, st["spent"] - _cl.spent(run_id) + c["expected_credits"], cap=st["cap"])
    if not _pc["ok"]: return dict(call=None, reason="credit ledger: " + "; ".join(_pc["warn"]))
    st.setdefault("ledger_warnings", []).extend(w for w in _pc["warn"] if w not in st.get("ledger_warnings", []))
    params = _fill(c["params"], st["jobs"])
    try: ref_gate.check(params, c.get("refs"))   # F88 HARD GATE, re-checked on every call
    except ref_gate.RefMissing as e: return dict(call=None, reason=f"REF GATE (F88): {e}")
    if c.get("quoted") is None:
        return dict(call=dict(namespace=c["namespace"], tool=c["tool"], arguments=dict(params=dict(params, get_cost=True), context="cost preflight, nothing submitted")),
                    phase="get_cost", step=c["step"])
    if (st.get("inflight") or {}).get("step") == c["step"]:      # D128: handed out before and never recorded - may already be spent
        return dict(call=None, reason=f"{c['step']} submit may be in flight (handed out {st['inflight']['ts']}); find its job id in Higgsfield history and record_submit, or recovery.clear_inflight after confirming none - never resubmit blind")
    st["inflight"] = dict(step=c["step"], ts=now().isoformat(timespec="seconds")); _save(run_id, st)
    return dict(call=dict(namespace=c["namespace"], tool=c["tool"], arguments=dict(params=params, context="approved Hookforge live run " + run_id)),
                phase="submit", step=c["step"], expected_credits=c["expected_credits"])

def record_cost(run_id, step, credits):
    st = _load(run_id); c = st["calls"][st["cursor"]]; assert c["step"] == step, f"cursor is at {c['step']}"
    c["quoted"] = float(credits)
    if abs(c["quoted"] - c["expected_credits"]) > LIVE["cost_tolerance"]:
        st["log"].append(dict(ts=now().isoformat(timespec="seconds"), step=step, event="cost_mismatch", quoted=credits, expected=c["expected_credits"]))
        c["quoted"] = None; _save(run_id, st)
        return dict(ok=False, reason=f"quoted {credits} != expected {c['expected_credits']} - stop and re-approve")
    _save(run_id, st); return dict(ok=True)

def record_submit(run_id, step, job_id, prompt_model=None):
    st = _load(run_id); c = st["calls"][st["cursor"]]; assert c["step"] == step and c.get("quoted") is not None, "get_cost must come first"
    st["jobs"][step] = job_id; st["spent"] = round(st["spent"] + c["quoted"], 2); st["cursor"] += 1; st.pop("inflight", None)
    from . import credit_ledger as _cl                                     # D126: single logging path, dedup + cap warnings
    _lg = _cl.log_job(run_id, job_id, c["quoted"], step, c["params"].get("model", ""), c.get("kind", ""))
    if _lg.get("warn"): st.setdefault("ledger_warnings", []).extend(_lg["warn"])
    st["log"].append(dict(ts=now().isoformat(timespec="seconds"), step=step, event="submitted", job=job_id, credits=c["quoted"]))
    GF.log_attempt(run_id, c["params"]["model"], c["params"]["prompt"], "pending", mode=c["params"].get("mode", ""), resolution=c["params"].get("resolution", ""),
                   duration=c["params"].get("duration", ""), source="runner.live", job_id=job_id)
    if st["cursor"] >= len(st["calls"]):
        p = _approval_path(run_id); a = json.load(open(p)); a["consumed"] = True; a["consumed_pt"] = now().isoformat(timespec="seconds"); json.dump(a, open(p, "w"), indent=1)
    _save(run_id, st); return dict(ok=True, spent=st["spent"])

def record_result(run_id, step, outcome, cause="", url=""):
    """outcome: ok | nsfw | ip | param | credits | failed. Failures go to the D42 ledger with the cause."""
    st = _load(run_id); c = next(x for x in st["calls"] if x["step"] == step)
    st["log"].append(dict(ts=now().isoformat(timespec="seconds"), step=step, event="result", outcome=outcome, cause=cause, url=url)); _save(run_id, st)
    GF.log_attempt(run_id, c["params"]["model"], c["params"]["prompt"], outcome, cause=cause, source="runner.live", job_id=st["jobs"].get(step, ""))
    return dict(ok=True)

def judge(run_id, step, clip, product):
    """D33 via vision_judge. A certain absurd failure inserts ONE re-roll of that step (still inside the cap and the approval)."""
    from . import vision_judge
    st = _load(run_id); n = st["rerolls"].get(step, 0)
    r = vision_judge.judge(clip, product, gen_id="H" if step.startswith("H") else "B", context=run_id, attempts_so_far=n)
    if r["decision"]["reroll"]:
        c = dict(next(x for x in st["calls"] if x["step"] == step)); c["step"] = step + "_r1"; c.pop("quoted", None)
        st["calls"].insert(st["cursor"], c); st["rerolls"][step] = n + 1
        if st["cursor"] >= len(st["calls"]) - 1:   # approval was consumed at the last step; re-roll stays covered by the same approval
            p = _approval_path(run_id); a = json.load(open(p)); a["consumed"] = False; a["reroll_reopened_pt"] = now().isoformat(timespec="seconds"); json.dump(a, open(p, "w"), indent=1)
        _save(run_id, st)
    return r
