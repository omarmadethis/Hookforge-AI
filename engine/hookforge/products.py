"""D117 product registry: config/products.json carries an `active` flag per product.
active() -> products that get new concepts, ranking, builds, e2e and routing. Retired products remain in the
learning corpus (music library, ab_log, results, POC hooks) as virality reference data; only new work skips them."""
import json, os
from .config import REPO
F = os.path.join(REPO, "config", "products.json")
def _cfg(): return json.load(open(F))["products"]
def all_products(): return list(_cfg())
def active(): return [k for k, v in _cfg().items() if v.get("active", True)]
def is_active(pk): return _cfg().get(pk, {}).get("active", True)
def retired(): return [k for k, v in _cfg().items() if not v.get("active", True)]
class Retired(Exception): pass
def require_active(pk):
    if not is_active(pk): raise Retired(f"{pk} is retired (config/products.json, D117); corpus use only, no new builds or routing")
