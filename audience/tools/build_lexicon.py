"""Build audience/lexicon.csv from a curated list + measured counts (audience/data/lexicon_counts.csv).
Two separate evidence questions per row:
  reach_evidence  = does this phrasing appear in viral reels? (grounded = counted in our corpus / 1M+ library)
  geo_status      = does it skew audience toward tier-1? ALL rows are 'hypothesis' until EXP-AUD-* results land
                    (no public data links caption vocabulary to viewer country; Meta does not document it).
Run from hookforge/: nice -n 19 python3 audience/tools/build_lexicon.py"""
import csv
C = {r['term']: r for r in csv.DictReader(open('audience/data/lexicon_counts.csv', encoding='utf8'))}
# id, category, slot_use, us_term, uk_ie, au_nz, ca, region_signal, counts_key, note
L = [
 # --- recipient slot: "DON'T show this to your ___" / "Every ___ NEEDS this" ---
 ('LX001','recipient','dont_show|needs','mom','mum','mum','mom','US/CA spelling','mom','Top slot fill: 14 don\'t-show uses; own 2.7M, ext 26M/12.4M. "mum" is the UK/AU/IE spelling: use ONLY on a UK-targeted variant'),
 ('LX002','recipient','dont_show|needs','Christmas mom','Christmas mum','Christmas mum','Christmas mom','US/CA spelling','mom','"EVERY Christmas Mom NEEDS this" 5.2M ext; own 62.8K'),
 ('LX003','recipient','dont_show','cozy mom','cosy mum','cosy mum','cozy mom','US spelling (cozy vs cosy)','cozy (US sp.)','Caption bank #2; cozy (US) 24 rows vs cosy (UK) 2 rows in corpus'),
 ('LX004','recipient','dont_show','grandma','nan / gran','nan','grandma','US/CA','grandma','Own 183K "DONT show this to your Grandma ❄️😳". "nan/nana" reads UK/AU'),
 ('LX005','recipient','gift_outcome|best_gift','wife','wife','wife','wife','neutral English','wife','"I found the best gift for my wife" 13.5M ext; own 165K'),
 ('LX006','recipient','best_gift','husband','husband','hubby','husband','neutral English','husband','"The best Christmas gift for your husband" 1.1M + 1.0M ext'),
 ('LX007','recipient','dont_show|gift','your man','your fella','your bloke','your man','US slang (hypothesis)','your man','0 in corpus: HYPOTHESIS; test vs "your husband"'),
 ('LX008','recipient','gift','dad','dad','dad','dad','neutral English','dad','"Christmas gift ideas for Your dad!" 2.7M ext; own 98K'),
 ('LX009','recipient','dont_show','your KIDS','your kids','your kids','your kids','neutral English','kids','"DO NOT let your KIDS see this" 3.2M ext'),
 ('LX010','recipient','gift_difficulty','Women','Women','Women','Women','neutral English','women/girls','Own 6.6M "Women are hard to gift.."'),
 ('LX011','recipient','identity_callout','Christmas-aholics / Christmas lovers','same','same','same','neutral English','christmas-aholics','Own 1.4M; ext "Every Christmas lover Needs this" 1.2M/1.1M'),
 ('LX012','recipient','identity_callout','Cold-aholics','same','same','same','neutral English (cold-climate cue)','','ext 6.0M "Cold-aholics this is for you 🥹💕", 1.3M; cold-climate audiences skew northern US/CA/UK/DE (hypothesis)'),
 ('LX013','recipient','identity_callout','Princess mom','Princess mum','Princess mum','Princess mom','US spelling + Disney fandom','mom','26M + 15.8M library (90d_20m) "Do NOT let a Princess mom see this"'),
 ('LX014','recipient','dont_show','the HOA','(no equivalent: avoid)','(avoid)','the condo board','US-only institution (hypothesis)','HOA','0 in corpus: HYPOTHESIS. HOA = homeowners association, almost uniquely US: strongest US-only text cue we can find; test as F99 experiment'),
 ('LX015','recipient','dont_show','your neighbors','your neighbours','your neighbours','your neighbours','US spelling','neighbor (US sp.)','7 rows; ext "How to confuse your neighbors" 628K; own 62.8K'),
 ('LX016','recipient','dont_show|identity','your Costco-loving dad','(avoid)','(avoid)','your Costco-loving dad','US/CA retail','Costco','HYPOTHESIS combo of grounded Costco (2.2M) + dad (2.7M)'),
 ('LX017','recipient','identity','teachers / nurses','same','same','same','neutral English','teacher','teacher 2.4M ext (n=1); nurse 0: HYPOTHESIS'),
 ('LX018','recipient','identity','my sis / bestie','same','same','same','US Gen-Z register','sister','"me dragging my sis to Aerie at 6am" 1.5M; bestie 2.7M (n=1)'),
 # --- US retail (store-surprise formats; names only in overlay + JK flip per D4/D12/D26) ---
 ('LX020','retail','store_overlay','Walmart','(Asda: UK variant)','(Kmart AU / Big W)','Walmart','US/CA (Walmart Canada exists)','Walmart','Own 1.4M "RUN, dont walk to Walmart"; JK flip mandatory (D4)'),
 ('LX021','retail','store_overlay','Target','(no UK Target)','(Target AU is a different chain)','(Target CA closed 2015)','US-only','Target','Own 1.4M "Grinch X Target"; ext 834K. Strong US-only cue: Target exists only in the US'),
 ('LX022','retail','store_overlay','Costco','Costco','Costco','Costco','US/CA (also UK/AU)','Costco','"COSTCO X Navidad" 2.2M ext (but Spanish word: see AV003)'),
 ('LX023','retail','store_overlay','Aerie / Victoria\'s Secret / Five Below','(avoid)','(avoid)','(avoid)','US-only chains','','"sneaking out at 7am to VS" 3.5M; Aerie 1.5M/734K/649K; Five Below 657K: US-only mall chains in mega-viral "drop" format'),
 ('LX024','retail','store_overlay','Home Depot / Lowe\'s / Hobby Lobby / TJ Maxx / HomeGoods / Kohl\'s','(avoid)','(avoid)','(Home Depot exists in CA)','US-only','Home Depot','0 in corpus: HYPOTHESIS. US-only chains, good for decor/fire-pit store hooks'),
 ('LX025','retail','store_overlay','IKEA','IKEA','IKEA','IKEA','global (no geo skew)','IKEA','755K "IKEA X Christmas" near-miss: global brand, NO tier-1 targeting value'),
 ('LX026','retail','caption','Amazon','Amazon','Amazon','Amazon','global','Amazon','6.9M "amazon kitchen organization": global, no targeting value; also implies "cheaper on Amazon" objection'),
 # --- holidays / calendar ---
 ('LX030','holiday','hook|caption','Christmas','Christmas','Christmas','Christmas','neutral (global)','Christmas','203 rows: the base niche, no geo skew on its own'),
 ('LX031','holiday','hook|caption','Thanksgiving / Friendsgiving (4th Thu Nov)','(avoid)','(avoid)','(CA Thanksgiving = 2nd Mon Oct)','US-only date','Thanksgiving','0 in corpus: HYPOTHESIS. US Thanksgiving Nov 26 2026: strongest calendar-only US cue; "Thanksgiving table", "after Thanksgiving dinner"'),
 ('LX032','holiday','hook|caption','Black Friday / Cyber Monday','Black Friday','Black Friday','Black Friday','US-origin, now global','Black Friday','n=1 ext 705K; global now, weak geo value'),
 ('LX033','holiday','hook','4th of July','(avoid)','(avoid)','(Canada Day Jul 1)','US-only','4th of July','Off-season for Q4; summer products only. HYPOTHESIS'),
 ('LX034','holiday','hook','Super Bowl Sunday','(avoid)','(avoid)','Super Bowl','US/CA','Super Bowl','Feb only. HYPOTHESIS'),
 ('LX035','holiday','hook','Christmas Eve / Christmas morning','same','same','same','neutral','Christmas',''),
 ('LX036','holiday','hook','Boxing Day','Boxing Day','Boxing Day','Boxing Day','UK/IE/AU/NZ/CA (NOT US)','Boxing Day','AVOID on US-primary variants; OK on UK/AU variant'),
 ('LX037','holiday','hook','Halloween → Christmas switch (Nov 1)','same','same','same','US-heavy (hypothesis)','Halloween','n=1. Nov 1 "Mariah is defrosting" meme is US-origin pop culture'),
 ('LX038','holiday','hook','snow day','snow day','(avoid: AU Christmas is summer)','snow day','northern hemisphere','winter/snow','Snow/cold cues exclude AU/NZ summer Christmas: keep AU on a separate summer-Christmas variant if ever targeted'),
 ('LX039','holiday','hook','secret Santa / white elephant','Secret Santa','Kris Kringle','Secret Santa','"white elephant" = US-only term','secret santa','0 in corpus: HYPOTHESIS. "white elephant gift exchange" is a distinctly US phrase'),
 ('LX040','holiday','hook','stocking stuffer','stocking filler','stocking filler','stocking stuffer','US/CA vs UK/AU','stocking stuffer','0 in corpus: HYPOTHESIS. Clean dialect split'),
 # --- units, money, spelling ---
 ('LX050','unit','overlay','$ price ("under $50")','£','A$','C$','US (bare $ reads US first)','$ price','5 ext rows (3.5M); D6: price not a model predictor'),
 ('LX051','unit','overlay','°F (e.g. "heats to 120°F")','°C','°C','°C (CA uses °C)','US-only','°F','0 in corpus: HYPOTHESIS. Fahrenheit is used almost only by the US'),
 ('LX052','unit','overlay','inches / feet / lbs','cm / kg','cm / kg','mixed','US (imperial)','inches/feet','n=1 ext 5.5M'),
 ('LX053','spelling','all','color / favorite / cozy / neighbor / gray','colour / favourite / cosy / neighbour / grey','UK spelling','UK spelling mostly','US vs Commonwealth','cozy (US sp.)','Spelling is the most mechanical dialect signal; default US spelling everywhere'),
 ('LX054','spelling','all','mom','mum','mum','mom','US/CA','mom','see LX001'),
 ('LX055','spelling','all','apartment / yard / fall','flat / garden / autumn','flat / backyard / autumn','apartment / yard / fall','US vs UK','apartment (US)','apartment n=1 (1.2M) / flat n=1 (1.6M)'),
 # --- devices / register ---
 ('LX060','device','hook','RUN, don\'t walk','same','same','same','US internet register','RUN dont walk','Own 1.4M; ext 834K'),
 ('LX061','device','hook','POV:','same','same','same','global','POV','32 rows; global'),
 ('LX062','device','hook','NEEDS this','same','same','same','neutral','need this','27 rows; ext 5.8M/5.2M'),
 ('LX063','device','hook','y\'all','(avoid)','(avoid)','(avoid)','US-South/US-only','y\'all','0 in corpus: HYPOTHESIS; strong US marker but niche register: experiment only'),
 ('LX064','device','caption','Get yours👉 / SAY "<KEYWORD>"','same','same','same','neutral','Get yours','D5: SAY not COMMENT'),
 ('LX065','device','hook','obsessed','same','same','same','US register','obsessed','4 ext rows (1.8M)'),
 # --- words/cues to AVOID on tier-1 variants (they invite non-target or other-region test audiences) ---
 ('AV001','avoid','all','(avoid) mum / colour / favourite / cosy on US-primary','—','—','—','UK/Commonwealth spelling','cosy (UK sp.)','Use only on an explicitly UK-targeted variant'),
 ('AV002','avoid','all','(avoid) Boxing Day / Bonfire Night / Argos / Tesco / Bunnings on US-primary','—','—','—','UK/AU-only','Argos/Tesco/Asda/Primark (UK)',''),
 ('AV003','avoid','all','(avoid) Spanish/Portuguese words (Navidad, Feliz, regalo, Natal) and Spanish-language audio','—','—','—','Spanish/Portuguese-speaking regions','','"COSTCO X Navidad" 2.2M: reach yes, but language-matched audiences dominate LatAm; our non-target CR is 0.05% (Shopify). HYPOTHESIS until EXP-AUD-05'),
 ('AV004','avoid','all','(avoid) °C, €/£ prices, metric sizes on US-primary','—','—','—','non-US','£/€',''),
 ('AV005','avoid','all','(avoid) "cheap", "free shipping worldwide", "COD"/"cash on delivery"','—','—','—','price-sensitive / COD markets (hypothesis)','','COD language is standard in markets with low card penetration: HYPOTHESIS'),
 ('AV006','avoid','all','(avoid) global-only brands as the hook (IKEA, Amazon, Shein, Temu)','—','—','—','global','IKEA','Reach without targeting value'),
]
out = []
for (i, cat, use, us, uk, au, ca, sig, key, note) in L:
    c = C.get(key, {})
    n_own = int(c.get('n_own') or 0); n_ext = int(c.get('n_ext') or 0)
    reach = 'grounded' if (int(c.get('n_ext_1m') or 0) >= 1 or int(c.get('n_own_50k') or 0) >= 1) else ('seen' if n_own + n_ext else 'not_in_corpus')
    out.append(dict(id=i, category=cat, slot_use=use, term_us=us, uk_ie=uk, au_nz=au, ca=ca, region_signal=sig,
                    corpus_n_own=n_own, corpus_n_ext=n_ext, own_best_views=c.get('own_best_views', 0), ext_best_views=c.get('ext_best_views', 0),
                    n_ext_1m=c.get('n_ext_1m', 0), n_own_50k=c.get('n_own_50k', 0), reach_evidence=reach,
                    geo_status='hypothesis', note=note))
with open('audience/lexicon.csv', 'w', newline='', encoding='utf8') as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
from collections import Counter
print(len(out), Counter(o['reach_evidence'] for o in out), Counter(o['category'] for o in out))
