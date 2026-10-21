"""D188 edit-level check: count burned-in cards in an edit spec (json with text_cards/cards) and exit 1 if over the limit.
usage: python3 tools/preflight/card_count_check.py <edit_or_plan.json> [...]"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "engine"))
from hookforge.card_count import gate
bad = 0
for p in sys.argv[1:]:
    d = json.load(open(p))
    for v in (d.get("videos") or [d]):
        cards = v.get("text_cards") or v.get("cards") or []
        f = gate(cards, (v.get("hook") or {}).get("format") if isinstance(v.get("hook"), dict) else v.get("format"))
        print(p, v.get("id", ""), len(cards), "cards:", f[0] if f else "ok"); bad += bool(f)
sys.exit(1 if bad else 0)
