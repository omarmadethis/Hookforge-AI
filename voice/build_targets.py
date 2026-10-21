"""Build voice/targets.csv: competitor/reference videos routed to our products.
Sources: research/reference_library/{index,archive,near_misses}.csv + corpus external/viral_research rows
(+ youtube rows appended by collect_youtube.py). Public URLs only (competitor posts); no own reels here."""
import csv, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from products import route
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.join(HERE, "..")
LIB = "/workspace/research/reference_library"
rows, seen = [], set()
for tier in ["index", "archive", "near_misses"]:
    for x in csv.DictReader(open(f"{LIB}/{tier}.csv")):
        k = route(x["product"])
        if k and x["url"] and x["url"] not in seen:
            seen.add(x["url"]); rows.append({"product_key": k, "source_set": f"library:{tier}", "platform": x["platform"].lower(),
                "views": x["views"], "post_date": x["post_date"], "inclusion_rule": x.get("inclusion_rule", ""),
                "product": x["product"], "url": x["url"]})
for x in csv.DictReader(open(f"{REPO}/private/corpus/corpus.csv")):
    if x["source"] in ("external", "viral_research"):
        k = route(x["product"])
        if k and x["url"] and x["url"] not in seen:
            seen.add(x["url"]); rows.append({"product_key": k, "source_set": f"corpus:{x['source']}:{x['key']}", "platform": x["platform"].lower(),
                "views": x["views"], "post_date": (x["posted_pt"] or "")[:10], "inclusion_rule": "", "product": x["product"], "url": x["url"]})
with open(f"{HERE}/targets.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(len(rows), "targets")
