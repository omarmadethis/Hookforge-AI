"""Build voice/browser_queue.csv: FB/IG reels whose comments need a logged-in browser (READ ONLY).

Rows: (1) OUR reels ranked by views (all own pages; FB + IG), (2) competitor Instagram/Facebook reels per product from
the reference library + corpus (top by views), (3) TikTok targets the public collector could not read, (4) discovery
searches (find the top competitor reels for each product on IG/FB). Contains our reel URLs, so it is gitignored (D10).
Capture rules (also in README): open reel -> comments -> sort 'Most relevant' -> scroll until `max_comments` top-level
comments or the end -> for each comment record ONLY: comment_text, likes, reply_count, has_tag (1 if it @-mentions
someone), is_page_reply (1 if the reply is from our page/brand), age_text (e.g. '3w'). NEVER record names/handles/profile
links; never like, reply, follow, react, DM or report. Save rows to voice/inbox/browser_<date>.csv (header in README).
"""
import csv, glob, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from products import PRODUCTS, route, route_own
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.join(HERE, "..")
FIELDS = "comment_text|likes|reply_count|has_tag|is_page_reply|age_text"
rows = []
corpus = list(csv.DictReader(open(f"{REPO}/private/corpus/corpus.csv")))
own = sorted([x for x in corpus if x["source"] == "own" and x["url"]], key=lambda x: -float(x["views"] or 0))
for i, x in enumerate(own, 1):
    v = float(x["views"] or 0)
    rows.append({"priority": "P1" if i <= 30 or v >= 100000 else "P2", "row_type": "own_reel", "product_key": route_own(x["page_code"], x["product"]) or "",
                 "reel_ref": x["key"], "platform": x["platform"], "url": x["url"], "views": int(v), "max_comments": 150 if v >= 100000 else 80,
                 "capture_fields": FIELDS, "why": f"our reel #{i} by views; questions/objections/intent from our own audience"})
# competitor IG/FB reels (logged-out IG/FB comment lists are not readable from the box)
comp = []
LIB = "/workspace/research/reference_library"
for tier in ["index", "archive", "near_misses"]:
    for x in csv.DictReader(open(f"{LIB}/{tier}.csv")):
        k = route(x["product"])
        if k and x["platform"].lower() in ("instagram", "facebook"): comp.append((k, x["platform"], x["url"], float(x["views"] or 0), f"library:{tier}"))
for x in corpus:
    if x["source"] in ("external", "viral_research"):
        k = route(x["product"])
        if k and x["platform"].lower() in ("instagram", "facebook") and x["url"]: comp.append((k, x["platform"], x["url"], float(x["views"] or 0), x["key"]))
# TikTok targets the public collector failed on
raw = os.path.join(REPO, "private", "voice", "raw")
for x in csv.DictReader(open(f"{HERE}/targets.csv")):
    m = re.search(r"/video/(\d+)", x["url"])
    if x["platform"] == "tiktok" and m and not os.path.exists(f"{raw}/tiktok_{m.group(1)}.jsonl"):
        comp.append((x["product_key"], "TikTok", x["url"], float(x["views"] or 0), x["source_set"] + " (public fetch failed)"))
seen = set()
for k, plat, url, v, src in sorted(comp, key=lambda c: -c[3]):
    if url in seen: continue
    seen.add(url)
    rows.append({"priority": "P1" if v >= 1e6 else "P2", "row_type": "competitor_reel", "product_key": k, "reel_ref": src, "platform": plat,
                 "url": url, "views": int(v), "max_comments": 150, "capture_fields": FIELDS, "why": "competitor audience: questions, objections, complaints we can beat"})
# discovery: top competitor reels per product on IG + FB (search in-app, sort by views, keep >=300K views, max 3 per term)
for k, p in PRODUCTS.items():
    for term in p["search"][:3]:
        for plat in ("Instagram", "Facebook"):
            rows.append({"priority": "P2", "row_type": "discovery_search", "product_key": k, "reel_ref": "", "platform": plat,
                         "url": f"search reels: {term}", "views": "", "max_comments": 100, "capture_fields": "reel_url|views|post_date + " + FIELDS,
                         "why": "find top 3 competitor reels (>=300K views, last 90 d) for this product, then capture comments"})
with open(f"{HERE}/browser_queue.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
from collections import Counter
print(len(rows), Counter((r["row_type"], r["priority"]) for r in rows))
