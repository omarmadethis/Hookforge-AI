"""D129 hourly unlogged-spend watch (READ-ONLY, messages nobody).
Each hour the agent calls the read-only Higgsfield `transactions` tool (size 100, both accounts it uses) and passes the
raw text/rows to check(). check() reconciles against the spend ledger (credit_ledger.reconcile), remembers every
transaction it has already seen (learning/alerts/spend_watch_state.json), and when NEW unlogged spend since the last
check exceeds THRESHOLD credits it raises a flag:
  learning/alerts/unledgered_spend.json   latest status (flag true/false, new + cumulative unlogged, items)  <- surface this
  learning/alerts/unledgered_spend.jsonl  one line per check (history)
No Buffer/Slack/email/chat is ever sent from here.
D161: every spend is tagged by spend_attrib (hookforge / hookforge_unaccounted / external). Only
hookforge_unaccounted (a Hookforge model with no ledger row to cover it) counts toward the flag. External spend
from other users of the shared account is reported per model in new_by_model, but it never raises the flag."""
import os, re, json, datetime
from zoneinfo import ZoneInfo
from .config import REPO
from . import credit_ledger, spend_attrib

PT = ZoneInfo("America/Los_Angeles")
THRESHOLD = 20.0
DIR = os.path.join(REPO, "learning", "alerts")
STATE, STATUS, HIST = (os.path.join(DIR, n) for n in ("spend_watch_state.json", "unledgered_spend.json", "unledgered_spend.jsonl"))
ROW = re.compile(r'^\s+(.+?),(-?[\d.]+),(\w+),"(.+?)"\s*$')

def parse(text):
    """rows from the transactions tool's text form ('display_name,credits,action,created_at' lines)."""
    return [dict(display_name=m[1], credits=float(m[2]), action=m[3], created_at=m[4]) for m in map(ROW.match, text.splitlines()) if m]

def _key(t, account): return f"{account}|{t['created_at']}|{t['display_name']}|{t['credits']}"

def check(transactions, account="user-Higgsfield--new-account", now=None):
    now = now or datetime.datetime.now(PT); os.makedirs(DIR, exist_ok=True)
    rows = parse(transactions) if isinstance(transactions, str) else list(transactions)
    st = json.load(open(STATE)) if os.path.exists(STATE) else dict(seen=[], baseline_pt=None)
    seen = set(st["seen"]); days = sorted({credit_ledger._pt(r["created_at"]).date() for r in rows if r.get("action") == "spend"})
    att = spend_attrib.attribute(rows)
    unl = [r for r in att["rows"] if r["tag"] != "hookforge"]
    keyed = {f"{account}|{u['created_at']}|{u['what']}|{u['credits']}": u for u in unl}
    new = {k: v for k, v in keyed.items() if k not in seen}
    first = st["baseline_pt"] is None
    unacc = {k: v for k, v in new.items() if v["tag"] == "hookforge_unaccounted"}
    new_cr = round(sum(v["credits"] for v in unacc.values()), 2)
    ext_cr = round(sum(v["credits"] for v in new.values() if v["tag"] == "external"), 2)
    flag = (not first) and new_cr > THRESHOLD
    by = {}
    for v in new.values(): by[v["what"]] = round(by.get(v["what"], 0) + v["credits"], 2)
    status = dict(checked_pt=now.isoformat(timespec="seconds"), account=account, flag=flag, threshold=THRESHOLD,
                  new_unledgered_credits=new_cr, new_unaccounted_credits=new_cr, new_external_credits=ext_cr, new_by_type=by,
                  new_by_model=spend_attrib.breakdown(list(new.values())), window_by_model=att["by_model"],
                  new_items=sorted(unacc.values(), key=lambda v: v["when_pt"])[-50:],
                  new_external_items=sorted((v for v in new.values() if v["tag"] == "external"), key=lambda v: v["when_pt"])[-20:],
                  cumulative_unledgered_in_window=round(sum(v["credits"] for v in keyed.values()), 2),
                  baseline=first, note=("baseline: existing unlogged spend recorded, not flagged" if first else
                                        ("NEW HOOKFORGE-MODEL SPEND NOT IN LEDGER > %g cr since last check - surface to Omar" % THRESHOLD if flag else "ok")))
    st["seen"] = sorted(seen | set(keyed)); st["baseline_pt"] = st["baseline_pt"] or now.isoformat(timespec="seconds"); st["last_pt"] = now.isoformat(timespec="seconds")
    json.dump(st, open(STATE, "w"), indent=1); json.dump(status, open(STATUS, "w"), indent=1)
    with open(HIST, "a") as fh: fh.write(json.dumps({k: status[k] for k in ("checked_pt", "account", "flag", "new_unledgered_credits", "new_external_credits", "new_by_type")}) + "\n")
    return status
