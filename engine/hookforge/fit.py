"""Product x format fit (D37). Every plan passes through assess(); the brief parser warns on WEAK and refuses REJECT
(unless forced into an experiment slot). The verdict + reasons are printed in every plan / dry-run report.
"""
from .format_defaults import FORMATS
from .worlds import FORMAT_ENERGY, FORMAT_NATIVE_SETTING, ADAPTATIONS
from .config import HIT_ABS_VIEWS

def assess(profile, fmt):
    f = FORMATS[fmt]; pk = profile["product_key"]; reasons = []; score = 0.0; hard = False
    ad = ADAPTATIONS.get((fmt, pk))
    own = next((x for x in profile["proven_formats"] if x["format"] == fmt), None)
    # 1. evidence on THIS product
    if own and own["hits"] >= 1:
        score += 3 + min(own["hits"], 5) * 0.4; reasons.append(f"PROVEN on this product: {own['hits']}/{own['n']} reels >=50K, best {own['best_views']:,} ({', '.join(own['reels'][:3])})")
    elif own and own["n"] >= 2 and own["best_views"] < 10000:
        score -= 2; reasons.append(f"FLOPPED on this product: {own['n']} reels, best {own['best_views']:,}")
    elif own:
        score += 0.5; reasons.append(f"tried on this product without a hit: {own['n']} reel(s), best {own['best_views']:,}")
    else:
        reasons.append("no own evidence on this product (transfer)")
    # 2. world / setting
    native = FORMAT_NATIVE_SETTING.get(fmt)
    from . import proof_guard as PG   # D68: drop bans contradicted by own >=50K reels unless Omar banned it
    from .worlds import world_forbidden
    forb = [s.lower() for s in world_forbidden(profile) if not PG.setting_proof(s, profile.get("corpus_products")) or PG.omar_banned(profile, s)]   # D113: + 'never a X' world clauses
    if native and any(native in s for s in forb) and not ad:
        hard = True; reasons.append(f"WORLD CONFLICT: format is natively set in a {native}; '{profile['display']}' lives in: {profile['world']}")
    if ad:
        score += 1; reasons.append(f"world adaptation: {ad['setting']} ({ad['why']})")
    # 3. energy
    ve = max(1, min(5, profile["energy"] + FORMAT_ENERGY.get(fmt, 0)))
    if profile["energy"] >= 4 and FORMAT_ENERGY.get(fmt, 0) < 0:
        hard = True; reasons.append(f"ENERGY CONFLICT: calm format on a hype product (energy {profile['energy']})")
    if profile["energy"] <= 2 and FORMAT_ENERGY.get(fmt, 0) >= 2 and not (own and own["hits"]):
        score -= 1.5; reasons.append(f"energy jump {profile['energy']}->{ve} (hype format on a calm product) without own proof")
    # 4. category coverage + external tier
    if profile["category"] not in f["categories"]:
        if not ad and not own:
            hard = True; reasons.append(f"NO EVIDENCE + NO WORLD ADAPTATION: category {profile['category']} has no proof for this format and no adaptation exists")
        else:
            score -= 1; reasons.append(f"category {profile['category']} not in the format's evidence categories (kept via adaptation/own evidence)")
    score += {"A": 1.0, "B": 0.5, "C": 0.0, "X": -2.0}.get(f["tier"], 0); reasons.append(f"format tier {f['tier']} ({f['title']})")
    verdict = "REJECT" if hard else ("STRONG" if score >= 3.5 else "OK" if score >= 1.0 else "WEAK")
    return dict(format=fmt, title=f["title"], verdict=verdict, score=round(score, 2), video_energy=ve, reasons=reasons)

def rank(profile, k=5):
    rs = [assess(profile, f) for f in FORMATS]
    rs = [r for r in rs if r["verdict"] != "REJECT"]
    return sorted(rs, key=lambda r: -r["score"])[:k]
