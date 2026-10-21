"""What drives US (tier-1) audience share? Per-reel analysis.
Input : audience/ig_reel_audience.csv (browser task; one row per reel; flexible headers, see ALIASES)
        + private/corpus/corpus.csv (format, hook, audio, caption, post time, product, psych flags)
        + private/evidence/prompts_ledger.csv (us_flag in prompts, by reel_key)
        + audience/data/reel_cues.csv (optional manual coding: reel_key or url, featured_person, american_creator, recognizable_face, us_store, us_home, notes)
Output: audience/data/us_share_features.csv (private-safe: reel_key only) + audience/US_SHARE_ANALYSIS.md
Stats : per binary feature Fisher exact on high-US vs low-US (split at median pct_us, ties -> low) + median pct_us difference;
        per numeric feature Spearman rho with permutation p (2,000 perms, seed 7). n is printed everywhere; n<5 per cell -> 'n-limited'.
Run from hookforge/: nice -n 19 python3 audience/tools/us_share_drivers.py"""
import csv, os, re, random, statistics as st, sys
from math import comb
AUD = os.environ.get('HF_AUD', 'audience/ig_reel_audience.csv')
OUTD = os.environ.get('HF_OUTD', 'audience')
ALIASES = {
 'url': ['url', 'reel_url', 'permalink', 'link'], 'shortcode': ['shortcode', 'code', 'reel_id', 'media_id', 'id'],
 'pct_us': ['pct_us', 'us_pct', 'united_states', 'us', 'us_share', '%_us', 'united states', 'top_country_us_pct'],
 'pct_tier1': ['pct_tier1', 'tier1_pct'], 'views': ['views', 'plays', 'reach', 'accounts_reached'],
 'page': ['page', 'account', 'handle'], 'featured_person': ['featured_person', 'influencer', 'creator', 'talent'],
 'notes': ['notes', 'note', 'caption'],
}
T1 = ['united states', 'canada', 'united kingdom', 'australia', 'new zealand', 'ireland', 'switzerland', 'netherlands', 'germany', 'norway']
def norm(h): return re.sub(r'[^a-z0-9%]+', '_', h.strip().lower()).strip('_')
def pct(x):
    try:
        x = str(x).replace('%', '').replace(',', '').strip(); v = float(x)
        return v / 100 if v > 1 else v
    except Exception: return None
def sc_from_url(u):
    m = re.search(r'/(?:reel|reels|p)/([A-Za-z0-9_-]+)', u or ''); return m.group(1) if m else None
if not os.path.exists(AUD): sys.exit(f'{AUD} not found yet (browser task still running).')
raw = list(csv.DictReader(open(AUD, encoding='utf8')))
H = {norm(h): h for h in raw[0].keys()}
def col(r, k):
    for a in ALIASES.get(k, [k]):
        if norm(a) in H: return r[H[norm(a)]]
    return ''
corpus = {}
if os.path.exists('private/corpus/corpus.csv'):
    for r in csv.DictReader(open('private/corpus/corpus.csv', encoding='utf8')):
        s = sc_from_url(r.get('url', '')) or re.sub(r'^ig_[^_]+_', '', r.get('reel_id') or '')
        if s: corpus[s] = r
        if r.get('views'): corpus.setdefault(('views', r.get('platform'), r['views']), r)
flags = {}
if os.path.exists('private/evidence/prompts_ledger.csv'):
    for r in csv.DictReader(open('private/evidence/prompts_ledger.csv', encoding='utf8')):
        if r.get('reel_key') and r.get('us_flag') not in (None, ''):
            flags.setdefault(r['reel_key'], []).append(r['us_flag'] in ('1', 'True', 'true'))
cues = {}
if os.path.exists('audience/data/reel_cues.csv'):
    for r in csv.DictReader(open('audience/data/reel_cues.csv', encoding='utf8')):
        cues[r.get('reel_key') or sc_from_url(r.get('url', ''))] = r
rows = []
for r in raw:
    sc = col(r, 'shortcode') or sc_from_url(col(r, 'url'))
    us = pct(col(r, 'pct_us'))
    if us is None:  # wide format: one column per country
        us = pct(r.get(H.get('united_states', ''), ''))
    t1 = pct(col(r, 'pct_tier1'))
    if t1 is None:
        vals = [pct(r[H[norm(c)]]) for c in T1 if norm(c) in H]
        t1 = sum(v for v in vals if v) if any(vals) else None
    c = corpus.get(sc) or {}
    if not c and col(r, 'views'):  # fallback: unique IG view-count match
        try: c = corpus.get(('views', 'IG', str(float(str(col(r, 'views')).replace(',', '')))), {})
        except Exception: c = {}
    key = c.get('key', '') or sc
    cu = cues.get(key) or cues.get(sc) or {}
    person = (cu.get('featured_person') or col(r, 'featured_person') or '').strip()
    text = ' '.join([c.get('hook_text', ''), c.get('caption', ''), col(r, 'notes')]).lower()
    hr = c.get('post_hour') or ''
    try: hr = float(hr)
    except Exception: hr = None
    rows.append(dict(
        reel_key=key, matched=int(bool(c)), pct_us=us, pct_tier1=t1, views=c.get('views') or col(r, 'views'),
        product=c.get('product', ''), format=c.get('format', ''), hook_family=c.get('hook_family', ''),
        song=(c.get('song') or c.get('audio') or '')[:60],
        american_creator=int(str(cu.get('american_creator', '')).strip() in ('1', 'yes', 'True') or bool(re.search(r'jordan', person, re.I))),
        person_on_screen=int((c.get('people_n') or '0') not in ('', '0', '0.0') or bool(person)),
        us_flag_prompt=int(any(flags.get(key, []))) if key in flags else '',
        us_store_text=int(bool(re.search(r'walmart|target|costco|home depot|aerie', text))),
        us_spelling_mom=int(bool(re.search(r'\bmoms?\b', text))),
        thanksgiving_or_us_holiday=int(bool(re.search(r'thanksgiving|4th of july|super ?bowl', text))),
        spanish_words=int(bool(re.search(r'navidad|feliz|regalo', text))),
        post_hour_pt=hr, us_prime_post=int(hr is not None and 14 <= hr <= 19),  # 5-10 PM ET
        night_pt_post=int(hr is not None and (hr >= 18 or hr < 4)),
        **{f'psych_{k}': c.get(k, '') for k in ('forbidden', 'recipient', 'store_surprise', 'gift_framing', 'humor')}))
rows = [r for r in rows if r['pct_us'] is not None]
os.makedirs(f'{OUTD}/data', exist_ok=True)
with open(f'{OUTD}/data/us_share_features.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
n = len(rows); med = st.median(r['pct_us'] for r in rows)
def fisher(a, b, c, d):  # two-sided
    n1, n2, m1, N = a + b, c + d, a + c, a + b + c + d
    def p(x): return comb(n1, x) * comb(n2, m1 - x) / comb(N, m1)
    p0 = p(a); return min(1.0, sum(p(x) for x in range(max(0, m1 - n2), min(n1, m1) + 1) if p(x) <= p0 + 1e-12))
def spearman(x, y):
    def rank(v):
        o = sorted(range(len(v)), key=lambda i: v[i]); rk = [0] * len(v); i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[o[j + 1]] == v[o[i]]: j += 1
            for k in range(i, j + 1): rk[o[k]] = (i + j) / 2
            i = j + 1
        return rk
    rx, ry = rank(x), rank(y); mx, my = st.mean(rx), st.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry)); den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return num / den if den else 0.0
random.seed(7)
lines = [f'# What drives US audience share (IG reels): n={n}, median %US={med:.1%}', '',
         'High-US = above the median %US. Fisher exact (two-sided); n-limited if any cell <5. Treat everything as SUPPORTED at best (D36: proven needs Holm p<0.05, n>=30, >=2 pages).', '',
         '| feature | n with | median %US with | median %US without | high-US with/without | low-US with/without | Fisher p | note |', '|---|---|---|---|---|---|---|---|']
for k in ['american_creator', 'person_on_screen', 'us_flag_prompt', 'us_store_text', 'us_spelling_mom', 'thanksgiving_or_us_holiday', 'spanish_words', 'us_prime_post', 'night_pt_post'] + [k for k in rows[0] if k.startswith('psych_')]:
    R = [r for r in rows if r[k] not in ('', None)]
    if not R: continue
    w1 = [r['pct_us'] for r in R if str(r[k]) in ('1', '1.0')]; w0 = [r['pct_us'] for r in R if str(r[k]) not in ('1', '1.0')]
    a = sum(1 for v in w1 if v > med); b = len(w1) - a; c = sum(1 for v in w0 if v > med); d = len(w0) - c
    p = fisher(a, c, b, d) if w1 and w0 else float('nan')
    lim = 'n-limited' if min(a, b, c, d) < 5 else ''
    lines.append(f"| {k} | {len(w1)} | {st.median(w1):.1%} | {st.median(w0):.1%} | {a}/{c} | {b}/{d} | {p:.3f} | {lim} |" if w1 and w0 else f'| {k} | {len(w1)} | - | - | - | - | - | no contrast |')
lines += ['', '## Categorical (median %US by level, n)']
for k in ['product', 'format', 'hook_family', 'song']:
    g = {}
    for r in rows: g.setdefault(r[k] or '(unknown)', []).append(r['pct_us'])
    lines.append(f'- **{k}**: ' + '; '.join(f'{lv} {st.median(v):.0%} (n={len(v)})' for lv, v in sorted(g.items(), key=lambda x: -st.median(x[1]))))
num = [(r['post_hour_pt'], r['pct_us']) for r in rows if r['post_hour_pt'] is not None]
vw = []
for r in rows:
    try: vw.append((float(r['views']), r['pct_us']))
    except Exception: pass
for name, pairs in (('post_hour_pt', num), ('views', vw)):
    if len(pairs) >= 6:
        x, y = zip(*pairs); rho = spearman(list(x), list(y)); ys = list(y); cnt = 0
        for _ in range(2000):
            random.shuffle(ys); cnt += abs(spearman(list(x), ys)) >= abs(rho)
        lines.append(f'- Spearman %US vs {name}: rho={rho:.2f}, perm p={(cnt + 1) / 2001:.3f}, n={len(pairs)}')
lines += ['', '## Rows (reel_key, %US, %tier-1, views, american_creator, product, format)'] + \
         [f"- {r['reel_key']}: {r['pct_us']:.0%} / {'' if r['pct_tier1'] is None else format(r['pct_tier1'], '.0%')} / {r['views']} / {r['american_creator']} / {r['product']} / {r['format']}" for r in sorted(rows, key=lambda r: -r['pct_us'])]
open(f'{OUTD}/US_SHARE_ANALYSIS.md', 'w').write('\n'.join(lines) + '\n')
print('\n'.join(lines[:40]))
