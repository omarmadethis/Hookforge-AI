"""D188 / F106 (Omar 2026-10-21 4:21 PM PT, permanent): ONE on-screen card per video by default.
A 2nd card is allowed ONLY for (a) a problem-vs-solution / then-vs-now hook (e.g. 1998 vs 2026, 'The idea... VS... The result')
or (b) a closing 'get it from the caption below 👇' card. Never 3+ cards. BLOCK gate on plans and on every edit."""
import re
VS_FORMATS = {"then-vs-now", "problem-solution", "F04", "F06"}
CLOSING_RE = re.compile(r"(?i)caption below|(link|it) (is )?(in|from) the caption|👇")
VS_RE = re.compile(r"(?i)\bvs\.?\b|\bversus\b")

class TooManyCards(Exception): pass

def _texts(cards): return [(c.get("text") if isinstance(c, dict) else str(c)) or "" for c in cards or []]

def allowed(cards, hook_format=None):
    t = _texts(cards)
    if len(t) <= 1: return True, ""
    if len(t) == 3 and VS_RE.search(t[1]) and not VS_RE.search(t[0]) and not VS_RE.search(t[2]):
        return True, "3 cards ok: MR52 idea / VS / result structure"
    if len(t) >= 3: return False, f"{len(t)} cards; never 3+ (D188) except MR52 idea/VS/result"
    vs = (hook_format in VS_FORMATS) or any(VS_RE.search(x) for x in t)
    closing = bool(CLOSING_RE.search(t[-1]))
    if vs or closing: return True, "2nd card ok: " + ("VS/then-vs-now format" if vs else "closing caption-below card")
    return False, "2 cards but not a VS/then-vs-now hook nor a closing 'get it from the caption below 👇' card (D188)"

def gate(cards, hook_format=None):
    ok, why = allowed(cards, hook_format)
    return [] if ok else [f"BLOCK card count: {why}"]

def enforce(cards, hook_format=None):
    f = gate(cards, hook_format)
    if f: raise TooManyCards(f[0])
