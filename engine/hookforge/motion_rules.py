"""D75 motion rules: AI shots look real when the motion is SHORT and SIMPLE (one subject, one action, <=4-6 s, slow camera).
Used by planner (simplify_motion) and gates (G13)."""
import re
MAX_ACTIONS = 2          # one main action (+ one natural follow-through)
MAX_SUBJECTS_MOVING = 2
COMPLEX_RX = r"(?i)\b(spins? around|backflip|cartwheel|juggl\w*|dances? (wildly|choreograph\w*)|crowd (runs|dances)|transforms?|morph\w*|explod\w*|360|orbit\w*|whip ?pan|crash zoom|rapid\w*|fast camera|hyperlapse|timelapse|multiple people (run|jump))\b"
ACTION_VERBS = r"(?i)\b(toss|throw|catch|snap|click|stick|press|install|peel|pull|open|plug|drop|slap|clip|swing|walk|run|jump|turn|pick|grab|hang|wave|point|laugh|hug|reach|lift|place|put|spin|dance|kick|climb|unbox|rip|tear)\w*\b"
CAMERA_OK = "handheld iPhone, slight natural sway, no fast camera moves"
RULE_TEXT = ("one subject, one simple action (plus at most one natural follow-through), short and slow, "
             "real-world physics, handheld iPhone framing with slight natural sway, no fast camera moves")

def _clean(prompt):
    p = (prompt or "").split("Motion: ")[0]
    return re.sub(r"(?i)\b(no|never|not|without)\b[^.,;)]*", " ", p)       # ignore negated phrases

def shot_texts(prompt):
    """Per-shot action text: 'Shot N (...): ...' segments if present, else the whole prompt."""
    p = _clean(prompt); segs = re.findall(r"(?is)shot \d+\s*\([^)]*\):(.*?)(?=shot \d+\s*\(|HARD CUT|$)", p)
    if segs: segs = [re.split(r"(?i)the product always looks|background details", x)[0] for x in segs]
    return segs or [p]

def count_actions(text): return len(re.findall(ACTION_VERBS, text or ""))

def lint(prompt, dur=None):
    hits = []; c = _clean(prompt); m = re.search(COMPLEX_RX, c)
    if m: hits.append(("WARN", f"complex motion '{m.group(0)}' - AI looks fake; keep it simple"))
    for i, t in enumerate(shot_texts(prompt), 1):
        n = count_actions(t)
        if n > MAX_ACTIONS + 2: hits.append(("BLOCK", f"shot {i}: {n} actions - split or simplify (max ~{MAX_ACTIONS})"))
        elif n > MAX_ACTIONS: hits.append(("WARN", f"shot {i}: {n} actions (max ~{MAX_ACTIONS})"))
    if dur and float(dur) > 6: hits.append(("WARN", f"{dur}s AI shot - keep AI shots <= 6 s"))
    return hits

def simplify_motion(prompt):
    """Append the camera/motion rule once (positive wording, D49)."""
    if "simple action" in (prompt or "") or "no fast camera moves" in (prompt or ""): return prompt
    return (prompt or "").rstrip(". ") + ". Motion: " + RULE_TEXT + "."
