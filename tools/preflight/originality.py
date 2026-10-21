"""Originality / near-duplicate check with Meta's own open-source PDQ hash (facebook/ThreatExchange, `pdqhash`).

Why: Meta reduces distribution of duplicate videos (Facebook, July 2025: "When Facebook detects duplicate videos, it will
reduce the distribution of the copies"). Meta's published video-matching (vPDQ) = PDQ per frame, match if Hamming
distance <= 31, frames with quality < 50 dropped. This re-implements that matching so Hookforge can score how
"duplicate-looking" a recreation / Ad Multiplier variant / repost is BEFORE posting.

Usage:  python3 originality.py CANDIDATE.mp4 REFERENCE.mp4 [REF2.mp4 ...] [--json]
Output per reference: q_match = % of candidate frames matching any reference frame, r_match = % of reference frames
matched (vPDQ reports both), min_dist (closest frame pair).
Interpretation (PROPOSED, calibrate on own data): >=80 % both ways = Meta would very likely treat as the same video;
<=20 % = distinct. Note Meta's real system is undisclosed beyond the open-source hashes; this is a proxy.
"""
import sys, json, numpy as np, pdqhash
from _frames import frames

THRESH, QMIN = 31, 50

def hashes(path, fps=2.0):
    fr, dur = frames(path, fps, 360)
    out = []
    for t, img in fr:
        h, q = pdqhash.compute(np.ascontiguousarray(img))
        if q >= QMIN: out.append((t, np.packbits(h.astype(np.uint8))))
    return out, dur

def _dist(A, B):
    a = np.stack([x for _, x in A]); b = np.stack([x for _, x in B])
    x = np.bitwise_xor(a[:, None, :], b[None, :, :])
    return np.unpackbits(x, axis=2).sum(2)

def compare(cand, ref):
    A, _ = hashes(cand); B, _ = hashes(ref)
    if not A or not B: return dict(ref=ref, error="no quality frames")
    D = _dist(A, B)
    return dict(ref=ref, q_match=round(100 * float((D.min(1) <= THRESH).mean()), 1),
                r_match=round(100 * float((D.min(0) <= THRESH).mean()), 1), min_dist=int(D.min()),
                n_cand=len(A), n_ref=len(B))

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    res = [compare(args[0], r) for r in args[1:]]
    print(json.dumps(res, indent=1) if "--json" in sys.argv else "\n".join(
        f"{r.get('q_match')}% cand / {r.get('r_match')}% ref  min_dist={r.get('min_dist')}  {r['ref']}" for r in res))
