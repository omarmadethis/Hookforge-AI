"""D124 approval-queue digest: one HTML page for Omar listing every PENDING item (status AWAITING_OMAR_APPROVAL, active
products only) with its credit cost, why, gate state and a Yes/No toggle. The page sends nothing: toggles build a reply
line Omar copies into chat ("YES: id1, id2 / NO: id3"); the parent then writes approval files per the normal gate.
  build(out=analytics/approval_digest.html) -> dict(n, total_credits, path)"""
import os, json, html, datetime
from zoneinfo import ZoneInfo
from .config import REPO
from . import approval_queue, products, credit_ledger

OUT = os.path.join(REPO, "analytics", "approval_digest.html")

def pending_items():
    out = []
    for it in approval_queue.pending():
        if it.get("status") != "AWAITING_OMAR_APPROVAL": continue
        if it.get("product") and not products.is_active(it["product"]): continue
        out.append(it)
    return sorted(out, key=lambda i: (not i.get("ready_for_approval"), -(i.get("rank_score") or 0), i.get("credits") or 0))

def _row(i):
    e = html.escape; ready = i.get("ready_for_approval")
    hook = ((i.get("plan") or {}).get("hook") or {}).get("text", "") if isinstance((i.get("plan") or {}).get("hook"), dict) else ""
    det = i.get("rationale") or i.get("why") or ""
    if i.get("kind") == "ai_look_fix": det += " - recommended: " + e(str(i.get("recommended")))
    blocks = (i.get("gates") or {}).get("blocks") or []
    return f"""<tr class="{'ready' if ready else 'blocked'}"><td><b>{e(i['id'])}</b><br><small>{e(i.get('kind',''))} · {e(i.get('product') or 'all active')}</small></td>
<td>{e(hook)}<br><small>{e(str(det))[:300]}</small>{'<br><small class=bl>BLOCKED: ' + e('; '.join(blocks)[:200]) + '</small>' if blocks else ''}</td>
<td class=num>{(i.get('credits') or 0):g}</td><td>{'ready' if ready else 'not ready'}</td>
<td><label><input type=radio name="{e(i['id'])}" value=yes {'disabled' if not ready else ''}> Yes</label> <label><input type=radio name="{e(i['id'])}" value=no> No</label></td></tr>"""

def build(out=OUT):
    items = pending_items(); now = datetime.datetime.now(ZoneInfo("America/Los_Angeles"))
    tot = sum(i.get("credits") or 0 for i in items if i.get("ready_for_approval")); day = credit_ledger.daily(now.date())
    page = f"""<!doctype html><meta charset=utf-8><title>Approval digest {now:%b %d}</title>
<style>body{{font:14px system-ui;margin:24px;max-width:1100px}}table{{border-collapse:collapse;width:100%}}td,th{{border-bottom:1px solid #ddd;padding:8px;vertical-align:top;text-align:left}}
.num{{text-align:right;font-variant-numeric:tabular-nums}}.blocked{{color:#888}}.bl{{color:#b00}}#reply{{width:100%;height:60px;font:13px monospace}}</style>
<h1>Approval digest</h1><p>{now:%a %b %d, %I:%M %p} PT · {len(items)} pending · {tot:g} credits if every ready item is approved · Higgsfield spent today (ledger): {day['total']:g} cr</p>
<p><small>Nothing on this page spends or sends. Tick Yes/No, then paste the reply line into chat.</small></p>
<table><tr><th>Item</th><th>Hook / why</th><th>Credits</th><th>State</th><th>Decision</th></tr>{''.join(_row(i) for i in items)}</table>
<h3>Reply line</h3><textarea id=reply readonly></textarea>
<script>function u(){{let y=[],n=[];document.querySelectorAll('input[type=radio]:checked').forEach(r=>(r.value=='yes'?y:n).push(r.name));
document.getElementById('reply').value='YES: '+(y.join(', ')||'-')+' / NO: '+(n.join(', ')||'-');}}document.addEventListener('change',u);u();</script>"""
    os.makedirs(os.path.dirname(out), exist_ok=True); open(out, "w").write(page)
    return dict(n=len(items), total_credits=tot, path=out, ids=[i["id"] for i in items])

if __name__ == "__main__": print(build())
