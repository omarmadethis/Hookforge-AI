import pandas as pd,numpy as np,re,json,os
pd.set_option('display.width',250);pd.set_option('display.max_colwidth',50)
inv=pd.read_csv('/workspace/hookforge/data/features/inventory.csv')
o=inv[inv.source=='own'].copy()
o['stem']=o.file.fillna('').str.split('/').str[-1].str.replace('.mp4','',regex=False)
o['code']=o.url.fillna('').str.extract(r'reel/([^/]+)/')[0]
# merge IG duplicates (ig_ig_X_code and ig_code) -> keep max-info row
aud=pd.read_csv('/workspace/hookforge/audience/ig_reel_audience.csv');aud['code']=aud.url.str.extract(r'reel/([^/]+)/')[0]
o=o.merge(aud[['code','reach','likes','comments','shares','saves','follows']].add_prefix('a_'),left_on='code',right_on='a_code',how='left')
for c in ['shares','saves','follows','reach','comments']:
    o[c]=o[c].fillna(o['a_'+c])
o['likes']=o['a_likes'].fillna(o.reactions)
o['keys']=o.apply(lambda r:{r.stem,r.uid},axis=1)
g=o.sort_values('saves',na_position='last').groupby(o.code.fillna(o.uid))
rows=[]
for code,x in g:
    r=x.iloc[0].copy(); r['keys']=set().union(*x['keys']); 
    for c in ['views','shares','saves','follows','reach','likes','comments']: r[c]=x[c].max()
    r['dup_rows']=len(x); rows.append(r)
P=pd.DataFrame(rows)
P=P[P.views.notna()].sort_values('views',ascending=False).reset_index(drop=True)
P['share_rate']=P.shares/P.views*1000; P['follow_rate']=P.follows/P.views*1000
P['rank']=np.arange(1,len(P)+1)
P.to_pickle('perf.pkl')
cols=['rank','platform','page','product','views','reach','likes','shares','saves','follows','share_rate','follow_rate','posted','hook_text_ref','caption','url']
P[cols+['uid']].to_csv('performance_all.csv',index=False)
print(len(P));print(P[cols[:13]].head(12).to_string());print(P[cols[:13]].tail(8).to_string())
