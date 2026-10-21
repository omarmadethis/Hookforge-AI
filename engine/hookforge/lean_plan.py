"""D140/D142 lean weekly plan: same slots, fewer credits. Quote + edit plan only - spends nothing, generates nothing.
Per product: 1 full 'anchor' video (H 1080p + B1-B3 720p, 1 start-frame still each); every extra video re-uses the
anchor's B1-B3 bodies and generates only a NEW 1080p hook (Omar's rule: hooks are always 1080p - D141, no 720p option).
D142 near-duplicate guard: each video gets its own order + trim of the shared bodies so that no two videos on the
same page share more than 50% of their frames in the same order (frame-level LCS / shorter video)."""
import json, os, collections, itertools
from . import gates

P = gates.PRICES
FPS = 24; CLIP = 4 * FPS            # every gen is a 4 s clip
MAX_SHARED = 0.50
HOOK_RES = "1080p"                  # Omar: 1080p hooks only

def costs(still_variants=1):
    st = P["still_gpt_image_2"] * still_variants
    hook = P[f"seedance_2_5_{HOOK_RES}_4s"] + st
    body = P["seedance_2_5_720p_4s"] + st
    return {"anchor": hook + 3 * body, "extra": hook}

def frames(edit, vid):
    """Frame ids of an edit: hook frames are unique to the video; body frames are (clip, frame) shared per product."""
    out = [("H", vid, i) for i in range(CLIP)]
    for clip, a, b in edit: out += [(clip, i) for i in range(a, b)]
    return out

def lcs(x, y):
    prev = [0] * (len(y) + 1)
    for xi in x:
        cur = [0]
        for j, yj in enumerate(y):
            cur.append(prev[j] + 1 if xi == yj else max(prev[j + 1], cur[j]))
        prev = cur
    return prev[-1]

def shared(fa, fb): return lcs(fa, fb) / min(len(fa), len(fb))

def seg_shared(ea, eb):
    """Same as shared(frames...) but O(segments^2): each clip appears at most once per edit and frames within a clip run
    forward, so ordered overlap = max-weight common subsequence of segments, weight = window intersection."""
    W = [[max(0, min(b1, b2) - max(a1, a2)) if c1 == c2 else 0 for c2, a2, b2 in eb] for c1, a1, b1 in ea]
    D = [[0] * (len(eb) + 1) for _ in range(len(ea) + 1)]
    for i in range(len(ea)):
        for j in range(len(eb)):
            D[i + 1][j + 1] = max(D[i][j + 1], D[i + 1][j], D[i][j] + W[i][j])
    la = CLIP + sum(b - a for _, a, b in ea); lb = CLIP + sum(b - a for _, a, b in eb)
    return D[-1][-1] / min(la, lb)

PAYOFF = "B3"                       # the payoff clip always closes the video - only the build-up is re-ordered
MIN_BODY = 6 * FPS                  # keep >= 6 s of body so the payoff still lands

def _candidates():
    wins = [(0, CLIP)] + [(o, o + L) for L in (72, 60, 48) for o in range(0, CLIP - L + 1, 12)]
    out = []
    for k in (3, 2):
        for perm in itertools.permutations(("B1", "B2", "B3"), k):
            for w in itertools.product(wins, repeat=k):
                e = tuple((c, a, b) for c, (a, b) in zip(perm, w))
                if sum(b - a for _, a, b in e) >= MIN_BODY and e[-1][0] == PAYOFF: out.append(e)
    out.sort(key=lambda e: -sum(b - a for _, a, b in e))           # longest bodies first
    return out

def _reveal_ok(e, rv):
    if rv is None: return True                       # unknown -> lean_edit.reveal_check flags it for a human
    a, b = next((a, b) for c, a, b in e if c == PAYOFF); r = rv * FPS
    return a + 0.25 * FPS <= r < b and (r - a) <= 1.5 * FPS       # D147: lands by 1.5 s, but not a sub-0.25 s pre-reveal flash

def edit_plan(slot_map, reveal_s=None):
    """Greedy: anchor V1 = B1-B3 full, in order; each next video takes the longest order/trim whose frame overlap with
    every earlier same-product video on a shared page is <= 50%."""
    vids = collections.defaultdict(list); pages = collections.defaultdict(set)
    for m in slot_map:
        if m["video"] not in vids[m["product"]]: vids[m["product"]].append(m["video"])
        pages[m["video"]].add(m["page"])
    cands = _candidates(); edits = {}; worst = {}
    for pk, vs in vids.items():
        vs = sorted(vs, key=lambda v: int(v.rsplit("_V", 1)[1]))
        for v in vs:
            peers = [u for u in edits if u in vs and pages[u] & pages[v]]
            best = None                            # lowest overlap first (leaves room for later videos), then longest body
            for e in cands:
                if not _reveal_ok(e, (reveal_s or {}).get(pk)): continue
                r = max((seg_shared(e, edits[u]) for u in peers), default=0.0)
                if r <= MAX_SHARED and (best is None or (r, -sum(b - a for _, a, b in e)) < best[0]): best = ((r, -sum(b - a for _, a, b in e)), e)
            if not peers: best = ((0.0, 0), next(e for e in cands if _reveal_ok(e, (reveal_s or {}).get(pk))))
            edits[v] = best[1] if best else None; worst[v] = round(best[0][0], 3) if best else None
    return edits, worst

def check(slot_map, edits):
    """D142 gate: every same-page pair of videos <= 50% shared ordered frames. Returns list of violations."""
    by_page = collections.defaultdict(set)
    for m in slot_map: by_page[m["page"]].add(m["video"])
    bad = []
    for pg, vs in by_page.items():
        for a, b in itertools.combinations(sorted(vs), 2):
            if edits.get(a) is None or edits.get(b) is None: bad.append((pg, a, b, "no edit")); continue
            r = shared(frames(edits[a], a), frames(edits[b], b))     # exact frame-level LCS for the gate
            if r > MAX_SHARED: bad.append((pg, a, b, round(r, 3)))
    return bad

def quote(weekly=None, still_variants=1, reveal_s=None):
    from . import concept_lab
    w = weekly or concept_lab.weekly(write=False)
    n = collections.Counter(p for p, _ in {(m["product"], m["video"]) for m in w["slot_map"]})
    c = costs(still_variants)
    per = {p: c["anchor"] + (k - 1) * c["extra"] for p, k in n.items()}
    edits, worst = edit_plan(w["slot_map"], reveal_s); bad = check(w["slot_map"], edits)
    return {"option": "lean_1080p_hook", "hook_res": HOOK_RES, "still_variants": still_variants, "videos": sum(n.values()),
            "slots": len(w["slot_map"]), "per_product": per, "total_credits": round(sum(per.values()), 1),
            "standard_total": w["total_credits"],
            "edits": {v: [dict(clip=cl, in_s=round(a / FPS, 2), out_s=round(b / FPS, 2)) for cl, a, b in e] if e else None for v, e in edits.items()},
            "max_shared_vs_samepage_peer": worst, "near_duplicate_violations": bad, "near_duplicate_ok": not bad,
            "note": "every video keeps its own hook clip + caption (D139); bodies re-ordered/re-trimmed per video (D142)"}

def write(weekly=None):
    from . import concept_lab
    from .config import REPO
    w = weekly or concept_lab.weekly(write=False)
    out = {"standard": w["total_credits"], "lean": quote(w)}
    d = os.path.join(REPO, "learning", "weekly_batch"); os.makedirs(d, exist_ok=True)
    json.dump(out, open(os.path.join(d, f"{w['start']}_lean.json"), "w"), indent=1, ensure_ascii=False, default=str, sort_keys=True)   # D166 deterministic
    return out
