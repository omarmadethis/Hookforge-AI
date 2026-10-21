"""Emoji catalogue: ours (corpus own hook+caption, CapCut text, CaptionBank) vs external (corpus external + research library tiers)."""
import pandas as pd, numpy as np, emoji, re, json, collections
REPO='/workspace/hookforge'
CTA=re.compile(r"\b(say|comment|link|get yours|get it|shop|tap|bio|caption below|order|grab)\b|👉|👇",re.I)
def ems(t): return [e['emoji'] for e in emoji.emoji_list(t or '')]
def cta_ems(t):
    out=[]
    for seg in re.split(r"\s/\s|\n|(?<=[.!?])\s",t or ''):
        if CTA.search(seg): out+=ems(seg)
    return out
c=pd.read_csv(f'{REPO}/private/corpus/corpus.csv')
rows=[]
for r in c[c.source.isin(['own','external','viral_research'])].itertuples():
    side='ours' if r.source=='own' else 'external'
    base=dict(side=side,src=r.source,key=r.key,views=r.views,platform=r.platform,format=r.format,category=r.category,product=r.product,page=r.page_code)
    rows.append(dict(base,where='hook_text',text=r.hook_text if isinstance(r.hook_text,str) else ''))
    cap=r.caption if isinstance(r.caption,str) else ''
    rows.append(dict(base,where='caption',text=cap)); rows.append(dict(base,where='cta',text=' '.join(cta_ems(cap)),_cta=True))
seen=set(c.url.dropna())
L=[]
for f,tier in [('index.csv','index'),('archive.csv','archive'),('near_misses.csv','near_miss')]:
    d=pd.read_csv(f'/workspace/research/reference_library/{f}'); d['tier']=tier; L.append(d)
L=pd.concat(L)
for r in L.itertuples():
    base=dict(side='external',src='lib_'+r.tier,key=r.id,views=pd.to_numeric(r.views,errors='coerce'),platform=r.platform,format=r.format,category=r.product_category,product=r.product,page=None,inclusion_rule=getattr(r,'inclusion_rule',None),post_date=r.post_date)
    rows.append(dict(base,where='hook_text',text=r.on_screen_hook_text if isinstance(r.on_screen_hook_text,str) else ''))
    cap=r.caption if isinstance(r.caption,str) else ''
    rows.append(dict(base,where='caption',text=cap)); rows.append(dict(base,where='cta',text=' '.join(cta_ems(cap)),_cta=True))
T=pd.read_csv(f'{REPO}/style/text_styles.csv')
for r in T.itertuples():
    rows.append(dict(side='ours',src='capcut',key=r.draft+'#'+str(r.seg),views=r.views if r.reel_key==r.reel_key else np.nan,format=None,category=None,where='hook_text' if r.text_index==0 else 'later_card',text=r.text))
cb=open('/workspace/team/mac/text/Documents/CaptionBank/CAPTION_BANK.md').read()
for line in cb.splitlines():
    m=re.match(r"\|\s*(\d+)\s*\|\s*(.*?)\s*\|",line)
    if m: rows.append(dict(side='ours',src='caption_bank',key='CB-'+m.group(1),views=np.nan,where='hook_text',text=m.group(2)))
R=pd.DataFrame(rows); R['emojis']=R.text.map(lambda t: ems(t) if not isinstance(t,float) else [])
R.drop(columns=[c for c in R.columns if c.startswith('_')]).assign(emojis=R.emojis.map(''.join)).to_csv(f'{REPO}/style/emoji_usage_rows.csv',index=False)
# performance units: one unit per reel (corpus/lib), per where
perf=R[R.src.isin(['own','external','viral_research','lib_index','lib_archive','lib_near_miss'])].copy()
# dedupe external reels appearing in both corpus external and library by key: keep as-is (different ids) — acceptable
def hit(r): 
    if r.side=='ours': return float(r.views>=50000) if r.views==r.views else np.nan
    return float(r.views>=1e6) if r.views==r.views else np.nan
perf['hit']=perf.apply(hit,axis=1)
out=[]
for (side,where),g in perf.groupby(['side','where']):
    n_reels=g.key.nunique(); base_hit=g.hit.mean(); base_med=g.views.median()
    cnt=collections.Counter(); reels=collections.defaultdict(set)
    for r in g.itertuples():
        for e in set(r.emojis): reels[e].add(r.key)
        for e in r.emojis: cnt[e]+=1
    gi=g.set_index('key')
    gi=gi[~gi.index.duplicated()]
    for e,ks in reels.items():
        sub=gi.loc[list(ks)]; rest=gi.drop(list(ks))
        out.append(dict(side=side,where=where,emoji=e,name=emoji.demojize(e).strip(':'),uses=cnt[e],n_reels=len(ks),share_of_reels=round(len(ks)/n_reels,3),
          median_views=sub.views.median(),hit_rate=round(sub.hit.mean(),3) if sub.hit.notna().any() else None,n_with_views=int(sub.views.notna().sum()),
          rest_hit_rate=round(rest.hit.mean(),3) if rest.hit.notna().any() else None,base_hit_rate=round(base_hit,3) if base_hit==base_hit else None,base_median=base_med,
          formats=';'.join(f"{k}:{v}" for k,v in sub.format.dropna().value_counts().head(4).items()),categories=';'.join(f"{k}:{v}" for k,v in sub.category.dropna().value_counts().head(4).items()),
          examples=' | '.join(sub.text.dropna().astype(str).str[:60].sort_values().unique()[:3])))
O=pd.DataFrame(out).sort_values(['side','where','n_reels'],ascending=[True,True,False])
O.to_csv(f'{REPO}/style/emojis.csv',index=False)
# usage-only counts (capcut, caption bank)
U=R[R.src.isin(['capcut','caption_bank'])]
uc=collections.Counter(e for l in U.emojis for e in l)
# emoji count per hook vs hit (ours)
H=perf[perf['where']=='hook_text'].copy()
H['n_em']=H.emojis.map(len)
cnt_tab=H.groupby(['side',H.n_em.clip(upper=3)]).agg(n=('key','nunique'),hit=('hit','mean'),med=('views','median')).round(3).reset_index()
cnt_tab.to_csv(f'{REPO}/style/emoji_count_vs_hit.csv',index=False)
print(cnt_tab.to_string()); print('capcut+bank usage',uc.most_common(25))
pd.set_option('display.width',250)
for (s,w),g in O.groupby(['side','where']):
    print('==',s,w); print(g.head(14)[['emoji','n_reels','share_of_reels','median_views','hit_rate','n_with_views','rest_hit_rate','base_hit_rate','categories']].to_string(index=False))
