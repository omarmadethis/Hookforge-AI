"""Rank countries for organic targeting and assign tiers.
Inputs (cited in audience/README.md §Sources):
  CR  = online-shopper conversion rate, Statista (Salesforce Shopping Index), avg of Q4'25..Q2'26 [S5]
  AOV = average order value index, ECDB 2025 (EUR) [S6] / Adtraction Q2'25 index [S7] (where available)
  PPP = GDP per capita PPP 2024, IMF WEO via Worldometer [S8]
  EN  = English is the majority first language (our captions/hooks are English-only)
  OWN = pooled Merry Glow + Brick Hood Shopify sessions->orders by country, 2026-08-01..10-18 (private/audience)
Output: audience/data/country_tiers.csv (no absolute $; own data as rates + Wilson CI)
Run from hookforge/: nice -n 19 python3 audience/tools/country_tiers.py"""
import csv, math
EXT = {  # country: (CR_pct or None, AOV_EUR or None, PPP_k, EN)
 'United States': (1.73, 137, 86.4, 1), 'United Kingdom': (2.13, 106, 63.5, 1), 'Canada': (1.57, None, 64.9, 1),
 'Australia': (1.60, None, 69.8, 1), 'New Zealand': (1.47, None, 54.6, 1), 'Ireland': (None, None, 135.3, 1),
 'Switzerland': (2.33, None, 99.2, 0), 'Netherlands': (2.13, 76, 81.5, 0), 'Germany': (1.63, 120, 72.8, 0),
 'Belgium': (1.33, None, 73.9, 0), 'Austria': (None, None, 73.6, 0), 'Denmark': (1.30, None, 82.7, 0),
 'Norway': (1.30, None, 108.1, 0), 'Sweden': (1.30, 107, 72.3, 0), 'Finland': (1.30, None, 64.9, 0),
 'France': (1.20, 104, 64.5, 0), 'Japan': (1.00, None, 54.7, 0), 'Spain': (1.07, None, 54.8, 0), 'Italy': (0.80, None, 61.5, 0),
 'Poland': (1.0, None, 52.4, 0), 'Romania': (1.0, None, 46.9, 0), 'Hungary': (1.0, None, 46.7, 0), 'Greece': (None, None, 42.9, 0),
 'Portugal': (None, None, 48.4, 0), 'Brazil': (0.93, None, 22.0, 0), 'Mexico': (0.93, None, 25.1, 0),
 'Colombia': (0.93, None, 21.0, 0), 'Philippines': (0.6, None, 11.0, 0), 'India': (0.6, None, 10.2, 0),
}
# Nordics/Eastern Europe/LatAm/APAC use the Statista regional row (Nordics, Eastern Europe, LAM, APAC-EANZJ).
# PPP for BR/CO/PH/IN approximate from the same IMF table (rounded); used only for ordering.
own_s, own_o, own_ck = {}, {}, {}
for r in csv.DictReader(open('private/audience/shopify_sessions_by_country.csv')):
    if r['country'] == 'ALL': continue
    c = r['country']; own_s[c] = own_s.get(c, 0) + int(r['sessions']); own_o[c] = own_o.get(c, 0) + int(r['sessions_converted'])
    own_ck[c] = own_ck.get(c, 0) + int(r['sessions_checkout'])
def wilson(k, n, z=1.96):
    if n == 0: return (None, None)
    p = k / n; d = 1 + z*z/n; c = p + z*z/(2*n); h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))
    return ((c-h)/d, (c+h)/d)
us_cr = 1.73
rows = []
for c, (cr, aov, ppp, en) in EXT.items():
    n = own_s.get(c, 0); k = own_o.get(c, 0); lo, hi = wilson(k, n)
    # external composite: CR index x PPP index (US = 1.0). AOV only where cited.
    cr_i = (cr / us_cr) if cr else None
    ext = (cr_i if cr_i else 0.75) * (ppp / 86.4) ** 0.5
    rows.append(dict(country=c, ext_cr_pct=cr or '', ext_aov_eur=aov or '', ppp_k_intl=ppp, english=en,
                     ext_score=round(ext, 3), own_sessions_bucket=('≥500' if n >= 500 else '100-499' if n >= 100 else '<100'),
                     own_session_cr_pct=round(100*k/n, 2) if n else '', own_cr_ci95=f"{100*lo:.2f}-{100*hi:.2f}" if n else '',
                     own_checkout_reach_pct=round(100*own_ck.get(c, 0)/n, 2) if n else ''))
def tier(r):
    c = r['country']
    if c == 'United States': return 'T1-PRIMARY'
    if r['english'] and r['ext_score'] >= 0.6: return 'T1-EN'
    if r['ext_score'] >= 0.75 and r['ppp_k_intl'] >= 70: return 'T1-WEST'
    if r['ext_score'] >= 0.45: return 'T2'
    return 'NON-TARGET'
for r in rows: r['tier'] = tier(r)
rows.sort(key=lambda r: (['T1-PRIMARY', 'T1-EN', 'T1-WEST', 'T2', 'NON-TARGET'].index(r['tier']), -r['ext_score']))
with open('audience/data/country_tiers.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
for r in rows: print(r)
# group-level own CR
G = {}
for r in rows:
    c = r['country']; G.setdefault(r['tier'], [0, 0]); G[r['tier']][0] += own_o.get(c, 0); G[r['tier']][1] += own_s.get(c, 0)
tot_s = sum(own_s.values()); tot_o = sum(own_o.values())
listed = sum(v[1] for v in G.values()); listed_o = sum(v[0] for v in G.values())
G['UNLISTED(other)'] = [tot_o - listed_o, tot_s - listed]
for t, (k, n) in G.items():
    lo, hi = wilson(k, n); print(t, f"orders={k} sessions={n} CR={100*k/max(n,1):.2f}% CI {100*(lo or 0):.2f}-{100*(hi or 0):.2f}")
