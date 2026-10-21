"""D160: (re)build docs/RESUME.md from the repo's own sources so anyone can resume cold.
Run: cd engine && PYTHONPATH=. python3 scripts/build_resume.py   (also called at the end of hookforge.regen)."""
import csv, glob, json, os, re, datetime
from zoneinfo import ZoneInfo
R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
P = lambda *a: os.path.join(R, *a)
now = datetime.datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%Y-%m-%d %-I:%M %p PT")
L = []; w = L.append
w(f"# RESUME — Hookforge (read this first)\nGenerated {now} by `engine/scripts/build_resume.py` from DECISIONS, OMAR_FEEDBACK_LOG, rules_core, config and the queues. "
  "Do not hand-edit; fix the sources and rerun.\n")
w("## 0. Start of every session\n```\n/workspace/hookforge/automation/ensure.sh          # snapshot supervisor (idempotent)\n"
  "cd /workspace/hookforge/engine && PYTHONPATH=. python3 -m hookforge.regen   # calendar, concepts, weekly+lean, render queue, Buffer preflight, digest\n"
  "PYTHONPATH=. python3 -m pytest -q tests   # + script tests: test_recreate_logic, test_audience_fit, test_edit_rules, test_omar_style (python3 <file>)\n```\n"
  "Full history: [docs/DECISIONS.md](DECISIONS.md) · [docs/HANDOFF.md](HANDOFF.md) · [learning/OMAR_FEEDBACK_LOG.md](../learning/OMAR_FEEDBACK_LOG.md) · audit: [docs/BLUEPRINT_2026-10-20.md](BLUEPRINT_2026-10-20.md) · excluded assets: [docs/MANIFEST_EXCLUDED.md](MANIFEST_EXCLUDED.md)\n")
w("## 1. Hard safety constraints (Omar, standing — override everything)\n" + "\n".join("- " + x for x in [
 "No Higgsfield credit spend without Omar's explicit approval of the exact plan and cap (approval record in learning/approvals/<run>.json; runner gate, LIVE disabled by default).",
 "Post nothing, send nothing: every external message/post needs a draft card and Omar's okay. Buffer = saveToDraft drafts only, mode addToQueue, never shareNow.",
 "FB/IG read-only (no likes, comments, posts, ads). Shopify read-only, aggregates only, no PII, don't switch stores. Gmail read-only.",
 "Never ask for or see passwords (Secure Form / box handoff). No tokens in files or chat. No scraping browser cookies/credentials to get around blocks. Never print presigned URLs.",
 "Exclude: FEMBOY child content entirely; never sexualize minors. Bank statements, Ecomstein/IMG_5172.PNG, rental applications, IDs, tax/financial docs, credentials, the LLC folder, the \"vids w isaac\" folder.",
 "No race-based casting or hooks. Cast: default women; Trump/car/patriotic products a man; cat products a woman.",
 "On-screen text (hooks + text cards) ≤ 8 words, NO exceptions (D149). FB post captions follow proven winners (not word-capped).",
 "Captions use SAY \"<KEYWORD>\", never \"Comment\" (D5/F93); the SAY rule always applies (D148).",
 "Hooks are 1080p (D141). Seedance 2.5 video only, GPT Image 2 stills only, no end frames (D22).",
 "Every file leaves the box via deliver.stage / verify_staged (D44d). Leave the shared-learning server deployment alone; don't touch the other worker's PurrVenture files unless asked.",
 "Report times in PT. Log every decision as a D-number in docs/DECISIONS.md."]) + "\n")
# products
pj = json.load(open(P("config", "products.json")))["products"]; urls = json.load(open(P("config", "product_urls.json")))
act = [k for k, v in pj.items() if v.get("active")]; ret = [k for k, v in pj.items() if not v.get("active")]
w("## 2. Products\n**Active (D117/D131):** " + ", ".join(f"`{k}`" for k in act) + "\n\n**Retired (FULL reference data — cuts, tags, captions, stats, sounds, hooks — no new content):** " + ", ".join(f"`{k}`" for k in ret) + "\n")
w("| active product | product URL status |\n|---|---|")
for k in act: u = (urls.get(k) or {}).get("url", ""); w(f"| {k} | {'PLACEHOLDER (blocks caption swaps)' if (not u or 'PLACEHOLDER' in u.upper()) else u} |")
# IDs
br = json.load(open(P("config", "buffer_routing.json"))); live = None
try:
    import sys; sys.path.insert(0, P("engine")); from hookforge.config import LIVE as live
except Exception: pass
w("\n## 3. Account and channel IDs (IDs only — no secrets; auth is host-connector OAuth)\n| Buffer account | MCP namespace | org id | plan | connected |\n|---|---|---|---|---|")
for k, a in br["accounts"].items(): w(f"| {k} | {a.get('namespace')} | {a.get('org')} | {a.get('plan')} (max {a.get('max_scheduled')} scheduled) | {a.get('connected')} |")
w("\n| page | service | account | channel id | products |\n|---|---|---|---|---|")
inv = {pg: [p for p, pgs in br["products"].items() if pg in pgs] for pg in br["pages"]}
for k, p in br["pages"].items(): w(f"| {k} | {p['service']} | {p['account']} | {p['channel']} | {', '.join(inv[k]) or ('LOCKED' if p.get('locked') else '-')} |")
w(f"\n**Higgsfield:** MCP namespaces `user-Higgsfield` (old account) and `user-Higgsfield--new-account` (live account: `{(live or {}).get('account')}`). Live runs: LIVE.enabled = `{(live or {}).get('enabled')}`. "
  "Prices (get_cost): seedance_2_5 1080p 4 s = 64, 720p 4 s = 28; gpt_image_2 2k high = 6.5 / 1k high = 3.5 / 1k medium = 1.0.\n"
  "Other connectors: user-Shopify / user-Shopify--brickhood (read-only), user-Gmail (read-only), user-Google-drive, user-Slack, user-Buffer / user-Buffer--buffer2.\n")
# approval queue
w("## 4. Approval queue (learning/approval_queue — all AWAITING_OMAR_APPROVAL, nothing approved)\n| id | kind | credits | recommended option | ready |\n|---|---|---|---|---|")
for f in sorted(glob.glob(P("learning", "approval_queue", "*.json"))):
    i = json.load(open(f)); w(f"| {i.get('id')} | {i.get('kind')} | {i.get('credits')} | {i.get('recommended_option') or ('lean_1_still ' + str((i.get('lean') or {}).get('credits')) if i.get('recommended_today') and i.get('lean') else '-')} | {i.get('ready_for_approval')} |")
w("\nArchived (never re-queue): " + ", ".join(os.path.basename(f)[:-5] for f in sorted(glob.glob(P("learning", "approval_queue", "_archive", "*.json")))) + "\n")
w("**Approval records on file (learning/approvals):** " + ", ".join(sorted(os.path.basename(f)[:-5] for f in glob.glob(P("learning", "approvals", "*.json")))) + "\n")
# open decisions
w("## 5. Open decisions for Omar\n" + "\n".join("- " + x for x in [
 "Weekly batch 2026-10-21: approve lean 1080p-hook plan (1,227 cr) vs standard (2,600 cr), or per video.",
 "Daily innovation budget 175 cr < 200 cr full concept; lean (174) auto-recommended — raise budget or keep lean?",
 "298.15 cr unledgered spend on the new Higgsfield account (10-20) — needs job rows; purrventure_branding_v2 spend unknown.",
 "trumpglow + purrventure product URLs are PLACEHOLDER (blocks traction caption swaps) — read-only Shopify lookup or Omar to supply.",
 "SAY \"VOTE\" near the midterms carries a PL5 WARN — keep the keyword or switch (e.g. SAY \"USA\")?",
 "JollyGlow captions now carry SAY \"LIGHTS\" (D148) — confirm wording.",
 "No public video host for Buffer asset URLs yet (needed before the first real draft push).",
 "GitHub: push once auth exists; repo should be PRIVATE (config/buffer_routing.json carries org/channel IDs, D10)."]) + "\n")
w("## 6. Next steps\n" + "\n".join(f"{n}. {x}" for n, x in enumerate([
 "Get Omar's decision on the weekly batch (lean vs standard) and today's concept; write learning/approvals/<run>.json from the chat approval (runner gate needs plan sha256 + cap).",
 "Live run via runner (anchor = build_calls_lean 'anchor' 174 cr; extras = 'extra' 70.5 cr), then lean_edit.build + gate_built + reveal check per video.",
 "Stage renders with deliver.stage/verify_staged, get public URLs, rerun buffer_preflight with real URLs, then publish.prepare → Omar approve → Buffer drafts.",
 "Fill PLACEHOLDER product URLs; reconcile the 298.15 cr; set META_TOKEN via a Secure Form/handoff so the snapshot loop gets data.",
 "Migration plan: docs/BLUEPRINT_2026-10-20.md (commit → container → read-only jobs → approvals UI → Buffer → generation)."], 1)) + "\n")
# standing rules verbatim
w("## 7. Omar's standing decisions (verbatim table from docs/DECISIONS.md D1–D34)\n")
dec = open(P("docs", "DECISIONS.md")).read(); tbl = [l for l in dec.splitlines() if re.match(r"^\| (D\d+|#|---)", l)]
w("\n".join(tbl) + "\n\nLater decisions D35–D160 (incl. amendments) are sections in docs/DECISIONS.md; index:\n")
w(", ".join(f"{m.group(1)} {m.group(2)[:60].strip()}" for m in re.finditer(r"(?m)^## (D\d+[a-z]?)[\s:—-]*(.*)$", dec)) + "\n")
w("## 8. Omar's rules in his words (learning/rules_core.csv)\n| id | rule | status | resolution |\n|---|---|---|---|")
for r in csv.DictReader(open(P("learning", "rules_core.csv"))): w(f"| {r['id']} | {r['rule'].replace('|','/')} | {r['status']} | {(r.get('hookforge_resolution') or '').replace('|','/')[:160]} |")
w("\n## 9. OMAR_FEEDBACK_LOG (verbatim copy of learning/OMAR_FEEDBACK_LOG.md)\n")
w(open(P("learning", "OMAR_FEEDBACK_LOG.md")).read())
# D166: rewrite only when something other than the "Generated <time>" line changed, so regen and tests make no churn
new = "\n".join(L) + "\n"; old = open(P("docs", "RESUME.md")).read() if os.path.exists(P("docs", "RESUME.md")) else ""
_body = lambda t: "\n".join(x for x in t.splitlines() if not x.startswith("Generated "))
if _body(new) != _body(old): open(P("docs", "RESUME.md"), "w").write(new)
print("docs/RESUME.md", sum(1 for _ in L), "blocks")
