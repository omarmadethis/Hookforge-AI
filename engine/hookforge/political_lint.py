"""D114 political-content safety lint (G25) for political products (trumpglow / patriotglow / trumpglow_projector).
Runs on every on-screen card, hook variant, post caption, SAY keyword line and every gen prompt / start frame.
BLOCK rules:
  PL1 misinformation / election process: no claims or instructions about voting, ballots, counts, fraud, dates, eligibility.
  PL2 candidate claims: no other politician named; no claims about Trump (won/lost/said/endorses/official/approved).
      The product name and the badge image ('Trump badge', 'Trump fans') are fine.
  PL3 hate / insults / violence: no slurs, dehumanising or violent words; "liberal" only in the playful banter already
      proven in our corpus (BANTER_OK, with evidence) - any other partisan jab blocks.
  PL4 race-based hooks: config.race_targeted (same rule as every product).
WARN rule:
  PL5 the word VOTE as a SAY keyword (own page_variants caption) - not an election claim, but near the 2026-11-03 midterms
      it can read as a voting call; shown to Omar, does not block.
"""
import re
from .config import race_targeted

POLITICAL = {"trumpglow", "patriotglow", "trumpglow_projector"}
PL1 = re.compile(r"(?i)\b(rigged|stolen election|election (was|is|got) (stolen|rigged)|steal the election|election fraud|voter fraud|fake ballots?|ballot|voting machines?|"
                 r"mail[- ]in|absentee|polls? (open|close)|polling (place|station)|election day is|vote (on|by|early|twice)|"
                 r"don'?t (bother )?vote|(go|get out( and)?|remember to) vote|illegals? vot|register(ed)? to vote|count(ing)? the votes?|"
                 r"won (the )?20(20|24)|(20(20|24)|midterms?) (was|were|is) (stolen|rigged))\b")
PL2_OTHER = re.compile(r"(?i)\b(biden|harris|kamala|obama|newsom|pelosi|schumer|aoc|ocasio|bernie|sanders|walz|clinton|hillary|"
                       r"vance|desantis|haley|rfk|kennedy|mamdani|democrats?|republicans?|gop|dnc|rnc)\b")
PL2_TRUMP = re.compile(r"(?i)\btrump\b.{0,40}\b(won|lost|wins|will win|said|says|endorse[sd]?|approved|official|authori[sz]ed|campaign|"
                       r"president[- ]elect|third term|2028)\b|\b(official|endorsed|approved|licensed) (by )?trump\b")
PL3 = re.compile(r"(?i)\b(libtards?|demon-?rats?|commies?|communists?|traitors?|groomers?|scum|vermin|subhuman|retard(ed)?|idiots?|morons?|"
                 r"kill|hang|shoot|lock (them|her|him) up|deport (them|all)|go back to|snowflakes?)\b")
LIBERAL = re.compile(r"(?i)\blib(eral)?s?\b|\blefties?\b|\bwoke\b")
BANTER_OK = [   # playful banter already in our corpus (exact patterns), with its evidence
    (re.compile(r"(?i)^\s*don'?t show this to a liberal\b"), "own TrumpGlow B v3 'Dont Show Liberal' (Omar-approved hook, DECISIONS D79/D101) + patriotglow caption_proof 'Don't show this to a ____' 183K"),
    (re.compile(r"(?i)^\s*pov: your buddy found out you'?re a liberal\b"), "research/trumpglow RESEARCH.md concept C (Lumi POV 1.2M format)"),
]
PL6 = re.compile(r"(?i)\b(fake|fraud|so-called|wannabe|pretend|bandwagon)\s+(\w+\s+)?(fans?|patriots?|supporters?|americans?|conservatives?)\b")   # D137: derogatory label (WARN)
SAY_VOTE = re.compile(r"(?i)\bsay\s+\W?vote\W?")

def texts(plan):
    out = []
    for c in plan.get("text_cards") or []: out.append(("card", c.get("text", "")))
    h = plan.get("hook") or {}
    if h.get("text"): out.append(("hook", h["text"]))
    for v in plan.get("hook_variants") or []:
        if isinstance(v, dict): out.append(("hook_variant", v.get("text", "")))
    for k in ("caption", "post_caption"):
        c = plan.get(k); t = c.get("text") if isinstance(c, dict) else c
        if t: out.append((k, t))
    for g in plan.get("gens") or []:
        out.append((f"gen {g.get('id')} prompt", g.get("prompt", ""))); out.append((f"gen {g.get('id')} still", (g.get("start_frame") or {}).get("prompt", "")))
    return out

def lint_text(t):
    """[(rule, level, msg)] for one text."""
    hits = []
    if not t: return hits
    for m in PL1.finditer(t): hits.append(("PL1", "BLOCK", f"election-process / misinformation term '{m.group(0)}'"))
    for m in PL2_OTHER.finditer(t): hits.append(("PL2", "BLOCK", f"names a politician / party '{m.group(0)}'"))
    for m in PL2_TRUMP.finditer(t): hits.append(("PL2", "BLOCK", f"claim about Trump '{m.group(0)}'"))
    for m in PL3.finditer(t): hits.append(("PL3", "BLOCK", f"insult / hate / violence '{m.group(0)}'"))
    if LIBERAL.search(t) and not any(rx.search(t) for rx, _ in BANTER_OK):
        hits.append(("PL3", "BLOCK", f"partisan jab outside the proven banter: '{t[:60]}'"))
    if race_targeted(t): hits.append(("PL4", "BLOCK", "race-based hook"))
    for m in PL6.finditer(t): hits.append(("PL6", "WARN", f"derogatory group label '{m.group(0)}' - mocks a group; keep it off captions"))
    if SAY_VOTE.search(t): hits.append(("PL5", "WARN", "SAY \"VOTE\" keyword near the midterms can read as a voting call (not a claim)"))
    return hits

def check(plan, product=None):
    pk = product or ((plan.get("product") or {}).get("key") if isinstance(plan.get("product"), dict) else plan.get("product_key"))
    if pk not in POLITICAL: return dict(applies=False, ok=True, rows=[])
    rows = [dict(where=w, rule=r, level=l, msg=m, text=t[:120]) for w, t in texts(plan) for r, l, m in lint_text(t)]
    return dict(applies=True, ok=not any(r["level"] == "BLOCK" for r in rows), rows=rows)
