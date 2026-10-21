"""Build a light text corpus (on-screen hook text + caption + CapCut text cards) with views and source,
for lexicon grounding. Output: audience/data/text_corpus.csv (no IDs, no URLs).
Run: nice -n 19 python3 audience/tools/text_corpus.py   (from hookforge/)"""
import csv, json, os, re
from collections import Counter
W = '/workspace'
OUT = f'{W}/hookforge/audience/data/text_corpus.csv'
rows = []
def num(x):
    try: return float(str(x).replace(',', ''))
    except Exception: return None
def add(**k): rows.append(k)
for tier in ('index', 'archive', 'near_misses'):
    p = f'{W}/research/reference_library/{tier}.csv'
    if os.path.exists(p):
        for r in csv.DictReader(open(p, encoding='utf8')):
            add(src='library_' + tier, platform=r.get('platform', ''), views=num(r.get('views')), post_date=r.get('post_date', ''),
                inclusion_rule=r.get('inclusion_rule', ''), product=r.get('product_category', ''),
                hook=r.get('on_screen_hook_text') or '', caption=r.get('caption') or '', audio=r.get('audio') or '')
p = f'{W}/team/external/external_reels.csv'
if os.path.exists(p):
    for r in csv.DictReader(open(p, encoding='utf8')):
        add(src='external', platform=r.get('platform', ''), views=num(r.get('views')), post_date=r.get('posted', ''),
            inclusion_rule='', product=r.get('product_category', ''), hook=r.get('hook_text') or '',
            caption=r.get('caption') or '', audio=r.get('audio') or '')
p = f'{W}/hookforge/private/corpus/corpus.csv'
if os.path.exists(p):
    for r in csv.DictReader(open(p, encoding='utf8')):
        if r.get('source') != 'own': continue
        add(src='own', platform=r.get('platform', ''), views=num(r.get('views')), post_date=r.get('posted_pt', ''),
            inclusion_rule='', product=r.get('product', ''), hook=r.get('hook_text') or '',
            caption=re.sub(r'https?://\S+', '', r.get('caption') or ''), audio=r.get('audio') or r.get('song') or '')
p = f'{W}/hookforge/private/edits/edits.csv'
if os.path.exists(p):
    for r in csv.DictReader(open(p, encoding='utf8')):
        try: cards = ' → '.join(c.get('text', '') for c in json.loads(r.get('text_cards') or '[]'))
        except Exception: cards = r.get('hook_text') or ''
        add(src='capcut_draft', platform='', views=num(r.get('views')), post_date=r.get('created', ''),
            inclusion_rule='', product='', hook=cards, caption='', audio=r.get('song') or '')
p = f'{W}/team/mac/text/Documents/CaptionBank/CAPTION_BANK.md'
if os.path.exists(p):
    for line in open(p, encoding='utf8'):
        m = re.match(r'\|\s*\d+\s*\|\s*(.+?)\s*\|', line)
        if m: add(src='caption_bank', platform='', views=None, post_date='', inclusion_rule='', product='',
                  hook=m.group(1), caption='', audio='')
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w', newline='', encoding='utf8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(len(rows), Counter(r['src'] for r in rows))
