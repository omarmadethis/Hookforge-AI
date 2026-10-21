"""De-identification applied to EVERY text before it is written anywhere (raw caches included).

Removes: @handles (counted as n_tags), emails, phone numbers, URLs, order / tracking numbers,
street addresses (simple US pattern), 'my name is X' / signatures. Truncates to MAX_CHARS.
We never store commenter usernames, user ids, avatars or profile links.
"""
import re

MAX_CHARS = 280
_RX = [
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[email]"),
    (re.compile(r"https?://\S+|www\.\S+"), "[link]"),
    (re.compile(r"(?<!\w)(\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}(?!\w)"), "[phone]"),
    (re.compile(r"(?i)\b(order|tracking|invoice|confirmation)\b\s*(no\.?|number|#|id)?\s*[:#]?\s*(?=[A-Z0-9-]*\d)[A-Z0-9-]{4,}"), r"\1 [id]"),
    (re.compile(r"#\d{4,}"), "[id]"),
    (re.compile(r"\b\d{1,5}\s+\w+(\s\w+)?\s(st|street|ave|avenue|rd|road|blvd|dr|drive|ln|lane|ct|court|way)\b\.?", re.I), "[address]"),
    (re.compile(r"\b((?i:my name is|my name's))\s+[A-Za-z]+(\s[A-Z][a-z]+)?"), r"\1 [name]"),
    (re.compile(r"(?i)\b(thanks|thank you|regards|best|sincerely|cheers),?\s*\n\s*[A-Z][a-z]+.*$", re.S), r"\1, [name]"),
]
_HANDLE = re.compile(r"@(?!friend\b)\S+")
_AFTER = re.compile(r"(@friend)\s+([A-Z][\w'.-]*)(\s+[A-Z][\w'.-]*)?")
_LONE = re.compile(r"^((?:@friend\W*)+)[A-Za-z][\w'.-]{1,20}\W*$")

def deid(text):
    """Return (clean_text, n_tags). n_tags = number of @mentions removed (tag-a-friend signal)."""
    t = (text or "").replace("\r", " ")
    t = _RX[0][0].sub("[email]", t)
    n_tags = len(re.findall(r"@\S+", t))
    t = re.sub(r"\S*[\U0001D400-\U0001D7FF\u24B6-\u24E9\U00016900-\U00016A3F]\S*", "", t)   # fancy-unicode display names
    t = _HANDLE.sub("@friend", t)
    t = _AFTER.sub(r"\1", t)            # '@friend Leigh Smith' -> '@friend' (display names with spaces)
    t = _LONE.sub(r"\1", t)             # '@friend meyer' (only a name after the tag) -> '@friend'
    t = re.sub(r"(@friend[\s.,]*){2,}", "@friend @friend ", t)
    t = re.sub(r"\s@(\s|$)", " ", t)
    for rx, rep in _RX: t = rx.sub(rep, t)
    t = re.sub(r"\s+", " ", t).strip()
    if len(t) > MAX_CHARS: t = t[:MAX_CHARS - 1].rstrip() + "…"
    return t, n_tags

if __name__ == "__main__":
    for s in ["@jane.doe look!! email me at a@b.com", "my order #123456 never came, call 555-123-4567",
              "I'm Sarah and I live at 12 Oak Street", "Order number: AB12345 where is it"]:
        print(deid(s))
