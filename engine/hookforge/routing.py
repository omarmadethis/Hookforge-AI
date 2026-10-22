"""D94 Buffer multi-account routing (config/buffer_routing.json). Pure planning: no network, no posting.
  routing.route(product)           -> [{page, name, service, namespace, org, channel, account}] routable pages, with
                                       `refused` for locked / unconnected / over-limit ones (never silently dropped)
  routing.capacity(account, live_count=None) -> remaining scheduled slots (free plan 10). live_count = number of
                                       scheduled+draft posts the agent read from Buffer (preferred); else our queue count.
  routing.slots()                  -> target 8 FB + 1 IG vs mapped pages (shows the empty slots incl. reserved buffer3)
  routing.next_window(page, after) -> next PT posting-window start for that page (learning/posting_windows.json),
                                       keeping posting.MIN_GAP_H from the page's last queued item.
  routing.check_originality(files_by_page, plans_by_page) -> variants.py rules: no identical file on two pages,
                                       never a file already queued on another page, plan similarity <= variants.MAX_SIM."""
import os, json, datetime, itertools
from zoneinfo import ZoneInfo
from .config import REPO

from .userconfig import cfg_path
CFG_F = cfg_path("buffer_routing")   # config/buffer_routing.json (gitignored) or the .example.json
WIN_F = os.path.join(REPO, "learning", "posting_windows.json")
PT = ZoneInfo("America/Los_Angeles")
ACTIVE = ("AWAITING_OMAR_APPROVAL", "APPROVED", "BUFFER_DRAFT_CREATED")

class RouteRefused(Exception): pass

def cfg(): return json.load(open(CFG_F))

def page(key):
    c = cfg(); p = dict(c["pages"][key]); a = c["accounts"][p["account"]]
    return dict(p, page=key, namespace=a["namespace"], org=a["org"], connected=a["connected"])

def page_by_channel(channel_id):
    for k, p in cfg()["pages"].items():
        if p["channel"] == channel_id: return page(k)
    return None

def _queue():
    from . import publish
    return publish.pending()

def capacity(account, live_count=None, queue=None):
    a = cfg()["accounts"][account]
    if not a["connected"]: return 0
    if live_count is None:
        chans = {p["channel"] for p in cfg()["pages"].values() if p["account"] == account}
        live_count = sum(1 for it in (queue if queue is not None else _queue()) if it["status"] in ACTIVE and it["payload"]["channelId"] in chans)
    return max(0, a["max_scheduled"] - int(live_count))

def assert_routable(channel_id, live_count=None, queue=None):
    p = page_by_channel(channel_id)
    if p is None: raise RouteRefused(f"channel {channel_id} is not in config/buffer_routing.json")
    if p.get("locked"): raise RouteRefused(f"{p['name']} is locked: {p.get('lock_reason')}")
    if not p["connected"] or not p["namespace"]: raise RouteRefused(f"{p['name']}: account {p['account']} not connected")
    if capacity(p["account"], live_count, queue) <= 0: raise RouteRefused(f"{p['account']} is at its scheduled-post limit ({cfg()['accounts'][p['account']]['max_scheduled']})")
    return p

def duplicate_channels(c=None):
    """D118: a channel id or external page may appear under only one page key, except pages explicitly marked
    stale/locked (old merryjammies_ig is superseded by merryjammies_ig_b2 and kept only for history)."""
    c = c or cfg(); seen, dups = {}, []
    for k, p in c["pages"].items():
        if p.get("lock_reason") and "stale" in str(p.get("lock_reason")).lower() and k not in sum(c["products"].values(), []): continue
        for f in ("channel", "external_page"):
            v = p.get(f)
            if not v: continue
            if (f, v) in seen: dups.append(dict(field=f, value=v, pages=[seen[(f, v)], k]))
            else: seen[(f, v)] = k
    return dups

def route(product, live_counts=None, queue=None):
    from . import products as _products
    _products.require_active(product)     # D117: no routing for retired products
    c = cfg(); keys = c["products"].get(product)
    d = duplicate_channels(c)
    if d: raise RouteRefused(f"duplicate channel/page in buffer_routing.json: {d}")
    if keys is None: raise RouteRefused(f"product {product} has no page mapping")
    ok, refused = [], []
    for k in keys:
        p = page(k)
        try: assert_routable(p["channel"], (live_counts or {}).get(p["account"]), queue); ok.append(p)
        except RouteRefused as e: refused.append(dict(page=k, reason=str(e)))
    return dict(product=product, pages=ok, refused=refused)

def slots():
    c = cfg(); have = {"facebook": [], "instagram": []}
    for k, p in c["pages"].items(): have[p["service"]].append(k)
    return {s: dict(target=n, mapped=len(have[s]), pages=have[s], open=max(0, n - len(have[s])),
                    reserved_account="buffer3 (not connected)" if not c["accounts"]["buffer3"]["connected"] else None) for s, n in c["target"].items()}

def _windows(code):
    w = json.load(open(WIN_F)); return (w.get(code) or w["_default"])["exploit"]

def next_window(page_key, after=None, queue=None):
    from .posting import MIN_GAP_H
    p = page(page_key); after = (after or datetime.datetime.now(PT)).astimezone(PT)
    last = [datetime.datetime.fromisoformat(it["suggested_slot_pt"]) for it in (queue if queue is not None else _queue())
            if it.get("suggested_slot_pt") and it["payload"]["channelId"] == p["channel"] and it["status"] in ACTIVE]
    earliest = max([after] + [t + datetime.timedelta(hours=MIN_GAP_H) for t in last])
    starts = sorted(int(w.split("-")[0]) for w in _windows(p["windows"]))
    for d in range(0, 8):
        day = (earliest + datetime.timedelta(days=d)).date()
        for h in starts:
            t = datetime.datetime(day.year, day.month, day.day, h % 24, tzinfo=PT)
            if t >= earliest: return t
    return earliest

def check_originality(files_by_page, plans_by_page=None, queue=None):
    from . import deliver, variants
    probs = []; shas = {k: deliver._sha(f) for k, f in files_by_page.items()}
    for a, b in itertools.combinations(shas, 2):
        if shas[a] == shas[b]: probs.append(f"same rendered file on {a} and {b} (variants.py: never reuse a file across pages)")
    for it in (queue if queue is not None else _queue()):
        for k, s in shas.items():
            if it["sha256"] == s and it["payload"]["channelId"] != page(k)["channel"] and it["status"] in ACTIVE:
                probs.append(f"{k}: file already queued on another page ({it['id']})")
    if plans_by_page:
        for a, b in itertools.combinations(plans_by_page, 2):
            s, _ = variants.similarity(plans_by_page[a], plans_by_page[b])
            if s > variants.MAX_SIM: probs.append(f"{a} vs {b}: plan similarity {s} > {variants.MAX_SIM}")
    return probs
