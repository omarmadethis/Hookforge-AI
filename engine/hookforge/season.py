"""Season calendar (gap G5): phase + levers for the posting date, gift cutoff per product, and the delivery-claim guard.
Source: tools/preflight/season_calendar_2026.json (USPS 2026 dates). gift_cutoff = Dec 25 - (processing_days + ship_days) - 1.
If either field is unknown the planner must NOT claim pre-Christmas delivery (BLOCK).
"""
import os, re, json, datetime as dt
from .config import REPO

CAL = os.path.join(REPO, "tools", "preflight", "season_calendar_2026.json")
CLAIM_RX = re.compile(r"(arriv\w* (by|before|in time for) (christmas|xmas|dec)|in time for (christmas|xmas)|before christmas|by christmas|guaranteed (delivery|by)|order by \w+ \d+)", re.I)

def _d(s): return dt.date.fromisoformat(s)

def gift_cutoff(profile):
    p, s = profile.get("processing_days"), profile.get("ship_days")
    if p is None or s is None: return None
    return _d("2026-12-25") - dt.timedelta(days=int(p) + int(s) + 1)

def phase(date, profile):
    r = _phase(date, profile)
    try:   # D88: last season's 1M+ tier as a 0.5-weighted prior (never above own data; use ly_season.blend)
        from . import ly_season
        r["ly_season_prior"] = dict(format=ly_season.prior(r["phase"], "format"), music=ly_season.prior(r["phase"], "music"), weight=ly_season.WEIGHT)
    except Exception as e: r["ly_season_prior"] = dict(error=str(e)[:120])
    return r

def _phase(date, profile):
    cal = json.load(open(CAL)); date = date if isinstance(date, dt.date) else _d(str(date))
    gc = gift_cutoff(profile)
    for ph in cal["phases"]:
        fr, to = ph["from"], ph["to"]
        if "gift_cutoff" in fr: fr = (gc + dt.timedelta(days=1)).isoformat() if gc else "2026-12-18"
        if "gift_cutoff" in to: to = gc.isoformat() if gc else "2026-12-17"
        if _d(fr) <= date <= _d(to):
            return dict(phase=ph["id"], levers=ph["levers"], gift_cutoff=gc.isoformat() if gc else None,
                        delivery_claims_allowed=bool(gc and date <= gc), date=date.isoformat())
    return dict(phase="off_season", levers=[], gift_cutoff=gc.isoformat() if gc else None, delivery_claims_allowed=False, date=date.isoformat())

def claim_problems(texts, profile, date):
    ph = phase(date, profile); out = []
    for t in texts:
        if CLAIM_RX.search(t or "") and not ph["delivery_claims_allowed"]:
            out.append(f"BLOCK delivery claim '{CLAIM_RX.search(t).group(0)}': ship time unknown or past gift cutoff ({ph['gift_cutoff']})")
    if ph["phase"] == "post_christmas":
        out.append("WARN post-Christmas phase: stop Christmas songs / gift hooks")
    return out
