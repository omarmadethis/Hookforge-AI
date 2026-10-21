"""Aggregate customer-support themes from Gmail search results (READ-ONLY connector output).

Input: JSON files saved from the user-Gmail `search_threads` tool (THREAD_VIEW_MINIMAL: subject + snippet only,
no bodies) placed in private/voice/gmail_tmp/. These raw files contain PII and are DELETED after this script runs
(pass --keep to keep them). Output (shareable, no PII):
  voice/support_themes.csv   store, product_key, theme, n_threads, share, first_seen, last_seen, example_1..3
  private/voice/support_rows.csv (theme per thread + short name-checked quote, no sender/date-time) for audit
Customer messages = consumer mail domains, Loox review notifications, Shopify contact-form messages.
Store notifications (order placed), vendors, ads, banks are excluded.
"""
import csv, glob, html, json, os, re, sys, collections
sys.path.insert(0, os.path.dirname(__file__))
from deid import deid
HERE = os.path.dirname(os.path.abspath(__file__)); PRIV = os.path.join(HERE, "..", "private", "voice")

CONSUMER = re.compile(r"^(gmail|googlemail|yahoo|hotmail|outlook|live|msn|icloud|me|mac|aol|att|comcast|verizon|roadrunner|charter|cox|sbcglobal|bellsouth|mail\.de|gmx|web\.de|t-online|orange|free|wanadoo|primacom|allbro|btinternet|sky|ymail|rocketmail|protonmail)\.")
THEMES = [  # (theme, regex) first match wins for primary; all matches counted as secondary. Word boundaries matter ('thin' in 'anything').
    ("missing_heat_controller", r"controll|heat ?control|heating cord|\bcord\b|no heat|not heat|isn.?t heat|doesn.?t heat|power ?bank|\bbattery\b|\busb\b|how (do i|can i) turn|aanzetten|temperatuur|controle|wärme|heiz"),
    ("wrong_item", r"wrong (item|robe|one|product)|santa one|not (solid )?grinch green|not the grinch|received the santa|just a bathrobe"),
    ("quality_defect", r"\bholes?\b|very thin|so thin|\btiny\b|ripped|\btorn\b|\bstain|\bsmell|\bbroke|broken|poor quality|piss poor|\bcheap\b"),
    ("not_as_pictured", r"not as advertised|not what i ordered|not (at all )?what i|not the (one|same)|not (the )?them on the picture|nicht der bestellten|\bdifferent\b|wrong (item|size|color|product)|\bcheap\b|look(s|ed)? (absolutely )?nothing like|didn.?t look anything like|anything like the picture|is not a heate"),
    ("never_received_or_late", r"not received|never (got|received|arrived)|haven.?t (received|gotten)|did not receive|didn.?t receive|where.?s my|where is (my )?order|still (have not|haven.?t|no)|no (movement|update|tracking)|lost in transit|tracking|hasent arivet|weeks|update on (my )?order|toujours pas|pas reçu|niet ontvangen|delay|when will"),
    ("refund_return_cancel", r"refund|\breturn|money back|cancel|chargeback|dispute|not paying|remboursement|geld terug"),
    ("scam_trust", r"scam|fraud|fake website|rip.?off|betrug|arnaque|attorney|report(ing)? (you|your company)|authorities"),
    ("sizing", r"\bsize|sizing|too (big|small|long|short)|\bfit\b|doesn.?t fit|\bx+l\b|petite|\btall\b"),
    ("presale_question", r"do you (ship|offer|have)|ship to|how many days|how long (does|will) (it|shipping)|is (it|this) (available|in stock)|\bprice\b|discount|\bcode\b"),
    ("positive", r"love (it|this|my)|amazing|great quality|so (warm|cozy|soft)|thank you so much|5 ?stars|\bperfect\b"),
]
PRODUCT = [("brickhood_mask", r"brick ?hood|ski mask|balaclava|mask"), ("merryglow_lights", r"merry ?glow|tree light|lights"),
           ("merryfire", r"merry ?fire|fire ?pit|fire bowl"), ("jollyglow_curtain", r"jolly ?glow|curtain"),
           ("grinchmelt_mug", r"grinch ?melt|mug"), ("grinch_robe", r"robe|jammies|grinch|mean one|heated|blanket|bademantel")]

def load(paths):
    th = {}
    for f in paths:
        s = open(f).read(); d = json.loads(s[s.find("{"):])
        for t in d.get("threads", []): th[t["id"]] = t
    return th

def is_customer(m):
    snd = m.get("sender", ""); dom = snd.split("@")[-1].strip("> ").lower(); subj = html.unescape(m.get("subject", ""))
    if dom == "loox.io" and re.search(r"review", subj, re.I): return "loox_review"
    if dom == "shopify.com" and "customer message" in subj.lower(): return "contact_form"
    if dom.startswith("g.shopifyemail") or "aliexpress" in dom: return None
    if CONSUMER.search(dom + "."): return "email"
    return None

def scrub(text, sender):
    t = html.unescape(text or "")
    t = re.split(r"\bOn (Mon|Tue|Wed|Thu|Fri|Sat|Sun)[a-z]*,|From: |Sendt fra|Sent from|Le .{3,40} a écrit|Am .{3,40} schrieb", t)[0]
    name = re.sub(r"<.*?>|\"", "", sender or "").strip()
    for tok in re.findall(r"[A-Za-zÀ-ÿ]{3,}", name): t = re.sub(rf"\b{re.escape(tok)}\b", "[name]", t, flags=re.I)
    t = re.sub(r"(?i)\b(hi|hello|dear|hey)\s+[A-Z][a-z]+", r"\1 [name]", t)
    t = re.sub(r"\b[A-Z][a-z]+ [A-Z]\.(?=\s|$)", "[name]", t)  # 'Leslie S.' style
    t = re.sub(r"\b\d{3,6}\b", "[n]", t)  # order numbers, zips, house numbers
    t = re.sub(r"\b[A-Z0-9]{8,}\b", "[id]", t)
    return deid(t)[0][:160]

OK_CAPS = {"Grinch", "Santa", "Merry", "Jammies", "Mean", "One", "Good", "Morning", "Thank", "You", "Christmas", "Hello", "Hi", "Dear", "Please", "Customer", "Service", "Team", "Review", "Text", "Rating", "USB", "The", "I", "My"}
def safe_quote(t):
    """Shareable quote: first 1-2 sentences, max 140 chars, rejected if it still looks like it carries a name/number."""
    if not t: return ""
    parts = re.split(r"(?<=[.!?])\s+", t); q = parts[0] if len(parts[0]) > 40 or len(parts) == 1 else parts[0] + " " + parts[1]
    q = q[:140]
    q = re.sub(r"[\s,]+[A-Z][a-z]+\W*$", "", q) if not re.search(r"[.!?]\W*$", q.split()[-1] if q.split() else "") else q   # trailing signature name
    for a, b in re.findall(r"\b([A-Z][a-zA-Z]+) ([A-Z][a-zA-Z]+)\b", q):
        if a not in OK_CAPS or b not in OK_CAPS: return ""
    if re.search(r"\[n\]-|ContactForm|Email:|Name:", q): return ""
    return q

def main(keep=False):
    paths = glob.glob(os.path.join(PRIV, "gmail_tmp", "*.txt"))
    th = load(paths); rows = []
    for t in th.values():
        m = t["messages"][0]; kind = is_customer(m)
        if not kind: continue
        subj = html.unescape(m.get("subject", "")); snip = html.unescape(m.get("snippet", "")); blob = (subj + " " + snip).lower()
        themes = [k for k, rx in THEMES if re.search(rx, blob)]
        if not themes: continue
        prod = next((k for k, rx in PRODUCT if re.search(rx, blob)), "grinch_robe" if "jammies" in blob or kind == "loox_review" else "merryjammies_store_unspecified")
        store = "MerryJammies" if prod == "grinch_robe" else prod
        rows.append({"kind": kind, "date": (m.get("date") or "")[:10], "product_key": prod, "store": store,
                     "theme": themes[0], "all_themes": "|".join(themes), "text": "" if kind == "contact_form" else scrub(snip, m.get("sender"))})
    for r in rows: r["text"] = safe_quote(r["text"])   # only short, name-checked quotes are ever stored
    with open(os.path.join(PRIV, "support_rows.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    agg = collections.defaultdict(list)
    for r in rows:
        for th_ in r["all_themes"].split("|"): agg[(r["product_key"], th_)].append(r)
    tot = collections.Counter(r["product_key"] for r in rows)
    out = []
    for (p, th_), rs in sorted(agg.items(), key=lambda kv: (kv[0][0], -len(kv[1]))):
        ex = [q for q in (safe_quote(r["text"]) for r in sorted(rs, key=lambda r: -len(r["text"]))) if len(q) > 25][:3]
        out.append({"product_key": p, "theme": th_, "n_threads": len(rs), "share_of_product_threads": round(len(rs) / tot[p], 3),
                    "first_seen": min(r["date"] for r in rs), "last_seen": max(r["date"] for r in rs),
                    "kinds": "|".join(sorted({r["kind"] for r in rs})), **{f"example_{i+1}": (ex[i] if i < len(ex) else "") for i in range(3)}})
    with open(os.path.join(HERE, "support_themes.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    print(len(th), "threads scanned;", len(rows), "customer threads classified;", dict(tot))
    if not keep:
        for p in paths: os.remove(p)
        print("deleted raw Gmail result files")

if __name__ == "__main__":
    main(keep="--keep" in sys.argv)
