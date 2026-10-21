"""D106 approval queue for GENERATION plans (concepts, redos). Items live in learning/approval_queue/<id>.json with
status AWAITING_OMAR_APPROVAL. Nothing here writes into learning/approvals/ (that file opens the live gate); the item
only carries the would-be approval file with approved_by EMPTY. Omar approves in chat -> the parent writes the real
approval file from item['approval_file_draft'] (approved_by="Omar", his quote, cap) -> runner.start_run. No spend here."""
import os, json, datetime
from zoneinfo import ZoneInfo
from .config import REPO
from . import runner, gates

PT = ZoneInfo("America/Los_Angeles")
DIR = os.path.join(REPO, "learning", "approval_queue")

def queue(item_id, kind, plan, why, poc, product, extra=None, cap=None):
    pf = runner.preflight(plan) if plan.get("gens") else dict(ok=False, rows=[])
    gr = plan.get("gates") or gates.run_all(plan)
    quote = plan.get("quote") or gates.quote(plan)
    tmpl = runner.approval_template(plan, item_id, credit_cap=cap or quote["total"])
    tmpl.update(approved_by="", approved_at_pt="", approval_quote="")
    it = dict(id=item_id, kind=kind, product=product, status="AWAITING_OMAR_APPROVAL", created_pt=datetime.datetime.now(PT).isoformat(timespec="seconds"),
              why=why, poc=poc, credits=quote["total"], credit_cap=tmpl["credit_cap"], quote=quote,
              gates=dict(ok=gr["ok"], blocks=[f"{b['gate']}: {b['msg']}" for b in gr["blocks"]], warns=[f"{w['gate']}: {w['msg']}" for w in gr["warns"]][:12]),
              preflight=dict(ok=pf["ok"], fix=[r for r in pf.get("rows", []) if not r["ok"]]),
              ready_for_approval=bool(gr["ok"] and pf["ok"] and quote["total"] <= tmpl["credit_cap"]), approval_file_draft=tmpl, plan=plan, **(extra or {}))
    os.makedirs(DIR, exist_ok=True); preserve(it, os.path.join(DIR, item_id + ".json")); json.dump(it, open(os.path.join(DIR, item_id + ".json"), "w"), indent=1, ensure_ascii=False, default=str)
    return it

KEEP = ("created_pt", "expires_pt")
_ORIG = {}
def preserve(it, path):
    """D168: rebuilding a still-pending item keeps its ORIGINAL created_pt / expires_pt (at every nesting level), so
    regen never extends a 24 h approval window. Items that are not pending (approved/rejected/expired) are rebuilt fresh."""
    if path not in _ORIG:                       # first sight in this process = the file as it was BEFORE this regen rewrote it
        try: _ORIG[path] = json.load(open(path)) if os.path.exists(path) else None
        except Exception: _ORIG[path] = None
    old = _ORIG[path]
    if not old: return it
    if old.get("status") != "AWAITING_OMAR_APPROVAL": return it
    def walk(n, o):
        if isinstance(n, dict) and isinstance(o, dict):
            for k in n:
                if k in KEEP and k in o and o[k]: n[k] = o[k]
                elif k in o: walk(n[k], o[k])
        elif isinstance(n, list) and isinstance(o, list):
            for a, b in zip(n, o): walk(a, b)
    walk(it, old); return it

def pending():
    if not os.path.isdir(DIR): return []
    return [json.load(open(os.path.join(DIR, f))) for f in sorted(os.listdir(DIR)) if f.endswith(".json")]
