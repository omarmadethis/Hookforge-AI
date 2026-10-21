"""Count candidate audience-lexicon terms in audience/data/text_corpus.csv (hook text + caption).
Output: audience/data/lexicon_counts.csv  term,group,n_rows,n_own,n_ext,own_best_views,ext_best_views,sum_views,examples
Run from hookforge/: nice -n 19 python3 audience/tools/lexicon_counts.py"""
import csv, re
TERMS = {
 # recipients / identity slots
 'mom': r"\bmoms?\b|\bmommy\b|\bmama\b", 'mum (UK/AU)': r"\bmums?\b|\bmummy\b", 'wife': r"\bwife\b|\bwifey\b",
 'husband': r"\bhusband\b|\bhubby\b", 'your man': r"\byour man\b|\bmy man\b", 'boyfriend': r"\bboyfriend\b|\bbf\b",
 'girlfriend': r"\bgirlfriend\b|\bgf\b", 'grandma': r"\bgrandma\b|\bgranny\b|\bnana\b|\bgrandmother\b",
 'dad': r"\bdads?\b|\bdaddy\b|\bfather\b", 'grandpa': r"\bgrandpa\b|\bpapa\b", 'kids': r"\bkids?\b|\bchildren\b",
 'women/girls': r"\bwomen\b|\bgirls?\b|\bladies\b", 'men/guys': r"\bmen\b|\bguys?\b|\bbros?\b",
 'sister': r"\bsister\b|\bsis\b", 'bestie': r"\bbestie\b|\bbest friend\b|\bbff\b", 'teacher': r"\bteachers?\b",
 'nurse': r"\bnurses?\b", 'neighbor (US sp.)': r"\bneighbors?\b", 'neighbour (UK sp.)': r"\bneighbours?\b",
 'HOA': r"\bhoa\b", 'family': r"\bfamily\b", 'christmas-aholics': r"christmas.?(a)?holics?|christmas lovers?",
 'cozy (US sp.)': r"\bcozy\b", 'cosy (UK sp.)': r"\bcosy\b",
 # US retail / places
 'Walmart': r"walmart", 'Target': r"\btarget\b", 'Costco': r"costco", 'Home Depot': r"home depot", "Lowe's": r"\blowe'?s\b",
 'TJ Maxx/HomeGoods': r"tj ?maxx|homegoods", 'Hobby Lobby': r"hobby lobby", 'Amazon': r"amazon", 'Kohls': r"kohl'?s",
 'IKEA': r"ikea", 'Dollar Tree': r"dollar tree", 'Bath & Body Works': r"bath (and|&) body", 'Trader Joes': r"trader joe",
 # UK/AU/CA retail
 'Argos/Tesco/Asda/Primark (UK)': r"argos|tesco|asda|primark|b&m|aldi", 'Bunnings/Kmart AU': r"bunnings|kmart", 'Canadian Tire': r"canadian tire",
 # holidays / seasons
 'Christmas': r"christmas|xmas", 'Thanksgiving': r"thanksgiving|friendsgiving", 'Halloween': r"halloween|spooky",
 'Black Friday': r"black friday|cyber monday", '4th of July': r"4th of july|fourth of july|july 4", 'Super Bowl': r"super ?bowl",
 'holiday season': r"\bholidays?\b|holiday season", 'winter/snow': r"\bwinter\b|\bsnow", 'ski': r"\bski|slopes?\b|snowboard",
 'Boxing Day (UK/CA/AU)': r"boxing day", 'Grinch': r"grinch", 'Santa': r"santa", 'gift': r"\bgifts?\b|\bgifting\b",
 'stocking stuffer': r"stocking stuffer", 'secret santa': r"secret santa|white elephant",
 # US units / money
 '$ price': r"\$\s?\d", '°F': r"°f|\bfahrenheit\b", 'inches/feet': r"\binch(es)?\b|\bfeet\b|\bft\b",
 '£/€': r"£|€",
 # slang / devices
 'POV': r"\bpov\b", 'RUN dont walk': r"run.{0,6}(don'?t|dont) walk|\brun\b", "don't show/let see": r"(don'?t|dont|do not).{0,12}(show|let)",
 'y\'all': r"\by'?all\b", 'obsessed': r"obsessed", 'this is your sign': r"your sign", 'no way': r"\bno way\b",
 'jealous/envy': r"jealous", 'need this': r"\bneeds? (this|one)\b", 'TikTok made me buy it': r"made me buy",
 'Get yours': r"get yours", 'SAY keyword CTA': r"\bsay\s*[\"“']", 'Comment keyword CTA': r"\bcomment\b",
 'USA/America': r"\busa\b|america|\bus flag|\bamerican", 'cowboy/country': r"cowboy|country girl|southern",
 'football/tailgate': r"football|tailgate", 'porch/backyard': r"porch|backyard|yard\b", 'patio': r"patio",
 'garden (UK sense)': r"\bgarden\b", 'apartment (US)': r"apartment", 'flat (UK)': r"\bflat\b",
}
rows = list(csv.DictReader(open('audience/data/text_corpus.csv', encoding='utf8')))
out = []
for term, rx in TERMS.items():
    R = re.compile(rx, re.I)
    hits = [r for r in rows if R.search((r['hook'] or '') + ' \n ' + (r['caption'] or ''))]
    def v(r):
        try: return float(r['views'])
        except Exception: return 0.0
    own = [r for r in hits if r['src'] in ('own', 'capcut_draft', 'caption_bank')]
    ext = [r for r in hits if r['src'] not in ('own', 'capcut_draft', 'caption_bank')]
    ex = sorted(hits, key=v, reverse=True)[:3]
    out.append(dict(term=term, regex=rx, n_rows=len(hits), n_own=len(own), n_ext=len(ext),
                    own_best_views=int(max([v(r) for r in own] or [0])), ext_best_views=int(max([v(r) for r in ext] or [0])),
                    n_ext_1m=sum(1 for r in ext if v(r) >= 1e6), n_own_50k=sum(1 for r in own if v(r) >= 5e4),
                    examples=' || '.join(f"[{r['src']}:{int(v(r))}] {(r['hook'] or r['caption'])[:70]}" for r in ex)))
with open('audience/data/lexicon_counts.csv', 'w', newline='', encoding='utf8') as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
for o in sorted(out, key=lambda o: -o['n_rows']):
    print(f"{o['term'][:28]:28} n={o['n_rows']:3} own={o['n_own']:3}({o['n_own_50k']}≥50K best {o['own_best_views']}) ext={o['n_ext']:3}({o['n_ext_1m']}≥1M best {o['ext_best_views']})")
