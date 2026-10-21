"""D132 text-only hook + caption variants (0 credits): for every queued concept of an ACTIVE product, 3 on-screen hook
variants and 3 caption variants drawn from winning patterns, each gated to <= MAX_WORDS words.
Sources (ranked by cited views): the product's own/competitor POC hooks+captions (poc/poc_library.json, product
match), the profile's poc_hooks, and cross-product winning GRAMMARS (incl. retired products = reference corpus) filled
for this product. Each variant cites its POC. Gates: <= 8 words (emoji/punctuation not counted), no 'Comment'
(SAY rule), no links/'link in bio', US spelling, world caption_forbidden + world_conflicts, political_lint for
trumpglow, not a repeat of the concept's own hook. Writes item['text_variants'] + learning/hook_variants/<day>.json."""
import os, re, json, datetime, glob
from .config import REPO
from . import products, approval_queue, political_lint, worlds

MAX_WORDS = 8
POC_RX = {"jollyglow_curtain": r"jollyglow|curtain", "trumpglow": r"trump|patriot", "purrventure_carrier": r"cat playpen|purrventure"}
NOT_TEXT = re.compile(r"(?i)backyard-cam|repost|\bedit\b|re-edit|variant|→|identical cuts|\(.*(man|woman) .*\)|\breel\b|=|\bFB \d|\d+M\b")
BAD = [(re.compile(r"(?i)\bcomment"), "Comment (SAY rule)"), (re.compile(r"(?i)link in (our )?bio|https?://|\.store|👉"), "link"),
       (re.compile(r"(?i)\b(cosy|colour|favourite|mum|jumper|customise)\b"), "UK spelling")]
GRAMMARS = [   # cross-product winners -> (template per product, views, poc)
  ("POV: {pov} 😂", {"jollyglow_curtain": "the whole street is JEALOUS", "trumpglow": "your wife got this for your truck",
                    "purrventure_carrier": "your cat finally gets outside"}, 2_400_000, "Lumi Door 'POV: ur wife got this' 1.2M (POC-0258) / JollyGlow own 63K POV"),
  ("{a}.. VS... {b}", {"jollyglow_curtain": ("Your lights", "my curtain"), "trumpglow": ("Their porch", "my porch 🇺🇸"),
                       "purrventure_carrier": ("The problem 😕", "the solution 😊")}, 22_000_000, "RollyMew 'The problem / VS / The solution' 22M + Lumi Door 'His last day.. VS...' 2.4M (POC-0255)"),
  ("If you buy one, I'll buy one too 😂", {"jollyglow_curtain": 1, "trumpglow": 1, "purrventure_carrier": 1}, 61_290, "own Brick Hood BH-01 61.3K (retired product, reference)"),
  ("Every {aud} NEEDS this 😏", {"jollyglow_curtain": "Christmas mom", "trumpglow": "Trump fan", "purrventure_carrier": "cat mom"}, 62_813, "JollyGlow own 62.8K 'Every Christmas mom NEEDS this'"),
  ("Don't show this to {who} 😂", {"jollyglow_curtain": "your neighbors", "trumpglow": "a liberal", "purrventure_carrier": "your cat"}, 183_145, "HeatedJammies FB 'DONT show this to your Grandma' 183K (retired, reference) + own TrumpGlow B"),
  ("Who needs one for the front porch? 🇺🇸", {"trumpglow": 1}, 0, "own PatriotsGlow page caption (D115 variant)"),
  ("They'll be asking where you got it.. 🤣", {"jollyglow_curtain": 1, "trumpglow": 1, "purrventure_carrier": 1}, 63_320, "JollyGlow own caption 63.3K"),
]
CTA = {"jollyglow_curtain": 'SAY "LIGHTS"',   # D148: the SAY rule always applies (Omar)
        "trumpglow": 'SAY "VOTE"', "purrventure_carrier": 'SAY "PURR"'}

def words(t): return len(re.findall(r"[A-Za-z0-9'’]+", t))

def gate(text, product, avoid=()):
    why = []
    if words(text) > MAX_WORDS: why.append(f"{words(text)} words > {MAX_WORDS}")
    if words(text) < 3: why.append("fragment (< 3 words)")
    why += [w for rx, w in BAD if rx.search(text)]
    prof = {"product_key": product}
    try:
        from . import profiles; prof = profiles.load(product)
    except Exception: pass
    if worlds.world_conflicts(prof, text): why.append("world conflict")
    for rx in (worlds.WORLDS.get(product) or {}).get("caption_forbidden", []):
        if re.search(rx, text, re.I): why.append("caption_forbidden")
    if product in political_lint.POLITICAL:
        why += [f"{r} {m}" for r, l, m in political_lint.lint_text(text) if l == "BLOCK"]
    norm = lambda t: " ".join(re.findall(r"[a-z0-9']+", t.lower()))
    if any(norm(a) and (norm(text) == norm(a) or norm(a) in norm(text)) for a in avoid): why.append("repeat (concept hook or another variant)")
    return why

def candidates(product):
    L = json.load(open(os.path.join(REPO, "poc", "poc_library.json"))); rx = POC_RX.get(product, product)
    out = {"hook": [], "caption": []}
    for e in L:
        if e.get("kind") in out and re.search(rx, str(e.get("product")), re.I) and not NOT_TEXT.search(e["text"]):
            for part in [p.strip() for p in e["text"].split(" / ")] if e["kind"] == "hook" else [e["text"].split("#")[0].strip()]:
                if e["kind"] == "hook" and not re.search(r"[^\x00-\x7F]|\.\.|[!?]|\bPOV\b|\bVS\b", part): continue   # stage description, not on-screen text
                if part: out[e["kind"]].append(dict(text=part, views=e.get("views") or 0, poc=f"{e['id']} {e.get('source', '')[:60]}"))
    for g, fills, v, poc in GRAMMARS:
        f = fills.get(product)
        if f is None: continue
        t = g if f == 1 else g.format(a=f[0], b=f[1]) if isinstance(f, tuple) else g.format(pov=f, aud=f, who=f)
        out["hook"].append(dict(text=t, views=v, poc=poc + " (grammar, filled for " + product + ")"))
        if CTA.get(product) and words(t) + words(CTA[product]) + 4 <= MAX_WORDS + 4:
            out["caption"].append(dict(text=f"{t} {CTA[product]}", views=v * 0.5, poc=poc + " + CTA"))
        else: out["caption"].append(dict(text=t, views=v * 0.5, poc=poc))
    out["hook"].sort(key=lambda c: -c["views"])
    out["caption"].sort(key=lambda c: (not c["poc"].startswith("POC-"), -c["views"]))   # real proven captions before filled grammars
    return out

def for_concept(item, n=3):
    pk = item["product"]; hook = ((item.get("plan") or {}).get("hook") or {}).get("text", "")
    cands = candidates(pk); res = {}; rejected = []; used = [hook]
    for kind in ("hook", "caption"):
        picked, seen = [], set()
        for c in cands[kind]:
            k = c["text"].lower()
            if k in seen: continue
            seen.add(k); why = gate(c["text"], pk, avoid=used if kind == "caption" else (hook,))
            if why: rejected.append(dict(kind=kind, text=c["text"], why=why)); continue
            picked.append(dict(text=c["text"], words=words(c["text"]), views_cited=int(c["views"]), poc=c["poc"])); used.append(c["text"])
            if len(picked) == n: break
        res[kind + "s"] = picked
    return dict(res, rejected=rejected[:20], credits=0, max_words=MAX_WORDS)

def run(day=None):
    day = day or datetime.date.today(); out = {}
    for f in sorted(glob.glob(os.path.join(approval_queue.DIR, "*.json"))):
        it = json.load(open(f))
        if it.get("status") != "AWAITING_OMAR_APPROVAL" or not products.is_active(it.get("product")) or it.get("kind") != "concept_test": continue
        v = for_concept(it); it["text_variants"] = v; json.dump(it, open(f, "w"), indent=1, ensure_ascii=False, default=str); out[it["id"]] = v
    d = os.path.join(REPO, "learning", "hook_variants"); os.makedirs(d, exist_ok=True); json.dump(out, open(os.path.join(d, f"{day}.json"), "w"), indent=1, ensure_ascii=False)
    return out
