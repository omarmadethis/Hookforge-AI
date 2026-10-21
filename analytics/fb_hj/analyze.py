import pandas as pd, numpy as np, sqlite3, re, json
d=pd.read_csv('audience/fb_heatedjammies_insights.csv')
d['rid']=d['Permalink'].str.extract(r'/reel/(\d+)')[0]; d['uid']='fb_'+d['rid']
d['cap']=d['Description'].fillna(d['Title']).fillna('').astype(str)
d['t']=pd.to_datetime(d['Publish time'],format='%m/%d/%Y %H:%M')
d['hour']=d.t.dt.hour; d['wd']=d.t.dt.day_name().str[:3]
for c in ['Views','Reach','Reactions','Comments','Shares','Link Clicks','Average Seconds viewed','Duration (sec)']: d[c]=pd.to_numeric(d[c],errors='coerce')
d['LC']=d['Link Clicks'].fillna(0)
d['ret']=d['Average Seconds viewed']/d['Duration (sec)']
d['sh1k']=d.Shares/d.Views*1e3; d['lc1k']=d.LC/d.Views*1e3; d['re1k']=d.Reactions/d.Views*1e3
d['lv']=np.log10(d.Views.clip(lower=1))
low=d.cap.str.lower()
d['get_yours']=low.str.contains('get yours'); d['has_url']=low.str.contains('http')
for h in ['mom','wife','grandma','girl','gift','christmas','viral','grinch']: d['#'+h]=low.str.contains('#'+h+r'\b')
d['n_emoji']=d.cap.apply(lambda s: len(re.findall(r'[\U0001F300-\U0001FAFF\u2600-\u27BF]',s)))
d['hook']=d.cap.str.split('#').str[0].str.split('http').str[0].str.strip()
con=sqlite3.connect('data/hookforge.db'); r=pd.read_sql('select uid,corpus_key,audio_label,hook_text_ref,avg_watch_s from reels',con)
d=d.merge(r,on='uid',how='left')
p=pd.read_csv('learning/raw_vs_final/performance_all.csv')[['uid','rank','hook_text_ref']].rename(columns={'hook_text_ref':'perf_hook','rank':'perf_rank'})
d=d.merge(p,on='uid',how='left')
pr=pd.read_csv('learning/raw_vs_final/pairs.csv',low_memory=False)
pa=pr.groupby('reel_uid').agg(draft=('draft','first'),n_clips=('clip_order','nunique'),kept=('kept_frac','mean')).reset_index().rename(columns={'reel_uid':'uid'})
d=d.merge(pa,on='uid',how='left')
df=pd.read_csv('learning/raw_vs_final/draft_features.csv')[['draft','cards','song','song_in','shots','avg_shot']]
d=d.merge(df,on='draft',how='left')
s=pd.read_csv('style/shots.csv'); sa=s.groupby('reel_key').agg(n_shots_style=('shot','count'),fmt=('format_id','first')).reset_index()
d=d.merge(sa,left_on='corpus_key',right_on='reel_key',how='left')
d=d.sort_values('Views',ascending=False).reset_index(drop=True); d['rank']=d.index+1
cols=['rank','uid','Views','Reach','sh1k','lc1k','re1k','Average Seconds viewed','Duration (sec)','ret','t','hook','get_yours','n_emoji','audio_label','cards','song','corpus_key','fmt','draft']
d[cols].to_csv('analytics/fb_hj/ranked.csv',index=False)
pd.set_option('display.width',250,'display.max_colwidth',40,'display.max_rows',60)
print(d[cols].drop(columns=['uid']).round(2).to_string())
print('join coverage: db',d.corpus_key.notna().sum() if 'corpus_key' in d else 0,'perf',d.perf_rank.notna().sum(),'pairs',d.draft.notna().sum(),'shots',d.fmt.notna().sum())
print('corr lv vs', {c:round(d.lv.corr(d[c],method='spearman'),2) for c in ['Average Seconds viewed','ret','Duration (sec)','sh1k','lc1k','n_emoji','hour']})
for f in ['get_yours','has_url','#mom','#wife','#grandma','#girl','#gift','#viral']:
  g=d.groupby(f).agg(n=('Views','size'),med_views=('Views','median'),lc1k=('lc1k','median'),LCsum=('LC','sum'),Vsum=('Views','sum'),sh1k=('sh1k','median'));g['pooled_lc1k']=g.LCsum/g.Vsum*1e3;print(f);print(g.round(2))
print(d.groupby(pd.cut(d['Duration (sec)'],[0,12,14,17,60])).agg(n=('Views','size'),med=('Views','median'),ret=('ret','median')))
print(d.groupby(pd.cut(d.hour,[-1,5,11,17,23])).agg(n=('Views','size'),med=('Views','median'),mean_lv=('lv','mean')))
print(d.groupby('wd').agg(n=('Views','size'),med=('Views','median'),mean_lv=('lv','mean')))
print('top8 ret',d.head(8).ret.median(),'rest',d.iloc[8:].ret.median(),'avgsec top',d.head(8)['Average Seconds viewed'].median(),'rest',d.iloc[8:]['Average Seconds viewed'].median())
print('emoji groups');print(d.groupby(d.n_emoji.clip(upper=3)).agg(n=('Views','size'),med=('Views','median')))
d.to_pickle('analytics/fb_hj/joined.pkl')
