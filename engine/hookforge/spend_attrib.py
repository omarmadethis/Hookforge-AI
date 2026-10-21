"""D161 Attribution heuristics for the shared Higgsfield account.
The transactions tool gives no job IDs (only display_name, credits, action, created_at), so each spend is tagged
by MODEL TYPE against Hookforge's known jobs, which are the spend_ledger rows with job_ids/items.
  1. exact: same amount within +-EXACT_MIN of a ledger row (credit_ledger.reconcile rule)       -> hookforge
  2. pool:  same Hookforge model, within +-POOL_MIN of a ledger row, and that row still has
            unallocated credits (batch rows such as "x28 start frames" log one total)           -> hookforge
  3. a model Hookforge uses with no ledger row to cover it                                  -> hookforge_unaccounted (ALERT)
  4. a model Hookforge never submits (Flare, Sound Effects, Seed Audio, Text to Music ...)   -> external (no alert)
Rules 3-4 are heuristic: if another user runs a Hookforge model (e.g. Seedance) it shows up under rule 3 and gets
flagged, so the watch fails safe and Hookforge spend is never hidden."""
import re
from . import credit_ledger

# transaction display_name -> Hookforge model key. Only these models are submitted by Hookforge (gates/runner).
HOOKFORGE_MODELS = {"gpt image 2.0": "gpt_image_2", "seedance 2.5": "seedance_2_5"}
EXACT_MIN, POOL_MIN = 15, 45

def tx_model(name):
    return HOOKFORGE_MODELS.get((name or "").strip().lower())

def row_model(r):
    s = f"{r.get('item', '')} {r.get('run_id', '')}".lower()
    if "gpt_image" in s or "frame" in s: return "gpt_image_2"
    if "seedance" in s or "video" in s or re.search(r"\bp\d_g\d", s): return "seedance_2_5"
    return None

def attribute(transactions):
    """returns rows with tag/model/matched_ts plus a per-model breakdown. Read-only, uses only the ledger CSV."""
    led = [dict(r, t=credit_ledger._pt(r["ts_pt"]), left=float(r["credits"]), model=row_model(r)) for r in credit_ledger._rows() if r["credits"] > 0]
    out = []
    spends = sorted((t for t in transactions if t.get("action") == "spend"), key=lambda t: t["created_at"])
    for tx in spends:
        t = credit_ledger._pt(tx["created_at"]); amt = abs(float(tx["credits"])); m = tx_model(tx.get("display_name"))
        rec = dict(when_pt=t.isoformat(timespec="seconds"), what=tx.get("display_name"), credits=amt, created_at=tx["created_at"], model=m or "other")
        near = lambda r, w: abs((r["t"] - t).total_seconds()) <= w * 60
        hit = next((r for r in led if r["left"] + 1e-9 >= amt and abs(r["credits"] - amt) < 0.01 and near(r, EXACT_MIN)), None)
        how = "exact"
        if not hit and m:
            hit = next((r for r in sorted(led, key=lambda r: abs((r["t"] - t).total_seconds())) if r["model"] == m and r["left"] + 1e-9 >= amt and near(r, POOL_MIN)), None); how = "pool"
        if hit:
            hit["left"] = round(hit["left"] - amt, 4)
            rec.update(tag="hookforge", match=how, run_id=hit["run_id"], ledger_ts=hit["ts_pt"], job_ids=hit.get("job_ids", ""))
        else:
            rec.update(tag="hookforge_unaccounted" if m else "external")
        out.append(rec)
    return dict(rows=out, by_model=breakdown(out))

def breakdown(rows):
    b = {}
    for r in rows:
        k = r["what"]; d = b.setdefault(k, dict(model=r["model"], hookforge=0.0, hookforge_unaccounted=0.0, external=0.0, n=0))
        d[r["tag"]] = round(d[r["tag"]] + r["credits"], 2); d["n"] += 1
    return b
