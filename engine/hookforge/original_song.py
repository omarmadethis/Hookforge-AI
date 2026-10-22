"""D190 / F108: a recreation of a competitor/reference reel MUST use the original reel's song, at the original's section
(in-point), starting at frame 0, no loops. Verified songs live in refs/<slug>/songs_verified.json (Shazam + flux xcorr)."""
import json, os
from .config import REPO
def verified(slug, reel_id):
    p = os.path.join(REPO, "refs", slug, "songs_verified.json")
    return json.load(open(p)).get(str(reel_id)) if os.path.exists(p) else None
def gate(plan):
    r = plan.get("recreate_of")
    if not r: return []
    v = verified(r["slug"], r["reel_id"])
    if not v: return [f"BLOCK recreation of {r['reel_id']} has no verified original song (D190): fingerprint it first"]
    f = []
    if plan.get("song_key") != v["song_key"]: f.append(f"BLOCK recreation uses '{plan.get('song_key')}' but the original used '{v['song_key']}' (D190)")
    if abs(float(plan.get("song_in_s", -99)) - v["in_point_s"]) > 0.25: f.append(f"BLOCK song in-point {plan.get('song_in_s')} != original section {v['in_point_s']} (D190)")
    if plan.get("song_start_t", 0) != 0: f.append("BLOCK song must start at frame 0 (D190)")
    if plan.get("song_loops"): f.append("BLOCK no song loops/splices (D190)")
    return f
