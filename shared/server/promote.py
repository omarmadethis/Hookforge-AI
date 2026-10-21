"""Server-side feedback promotion logic (scaffold, local only). Rule signature = (category, gate_id, normalized rule_sig)."""
import math
def wilson_lower(k, n, z=1.96):
    if n == 0: return 0.0
    p = k / n; d = 1 + z*z/n
    return (p + z*z/(2*n) - z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))) / d

def decide(sig_stats, min_users=5, min_niches=2, min_conf=0.55):
    """sig_stats: {'users_agree': k, 'users_exposed': n, 'niches': m, 'contradict': c}
    -> 'global' | 'niche' | 'candidate' | 'local'"""
    k, n = sig_stats["users_agree"], sig_stats["users_exposed"]
    conf = wilson_lower(k, n)
    if k >= min_users and conf >= min_conf and sig_stats.get("contradict", 0) <= k * 0.2:
        return "global" if sig_stats.get("niches", 1) >= min_niches else "niche"
    if k >= 3: return "candidate"
    return "local"

def rollback(before_repeat, after_repeat, before_views, after_views, min_n=20):
    """True if rule should be rolled back: no reduction in repeat mistakes AND results worse."""
    if after_views["n"] < min_n: return False
    return after_repeat >= before_repeat and after_views["median"] < before_views["median"] * 0.9
