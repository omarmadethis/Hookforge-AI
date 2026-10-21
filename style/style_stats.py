import pandas as pd, numpy as np, json
T=pd.read_csv('style/text_styles.csv'); S=pd.read_csv('style/segments.csv')
c=pd.read_csv('private/corpus/corpus.csv',usecols=['key','format','category','product','page_code','views']).set_index('key')
T=T[~T.recycled]; S=S[~S.recycled]
T['format']=T.reel_key.map(c.format); T['category']=T.reel_key.map(c.category); T['page']=T.reel_key.map(c.page_code)
T['grp']=np.where(T.views>=50000,'win',np.where(T.views<10000,'flop',np.where(T.views.notna(),'mid',None)))
out={}
q=lambda s:{k:round(float(s.quantile(p)),3) for k,p in [('p10',.1),('p25',.25),('med',.5),('p75',.75),('p90',.9)]} if s.notna().sum() else {}
out['all']=dict(n_text=len(T),n_drafts=int(T.draft.nunique()),scale=q(T.scale),pct_from_top=q(T.pct_from_top),y=q(T.y),stroke=T.stroke_width.value_counts().to_dict(),
  n_lines=T.n_lines.value_counts().to_dict(),max_chars_line=q(T.max_chars_line),n_words=q(T.n_words),n_emojis=T.n_emojis.value_counts().to_dict(),
  ends_with_emoji=round(float(T.text.str.strip().map(lambda t: not t[-1].isascii() if t else False).mean()),3),
  has_ellipsis=round(float(T.text.str.contains(r'\.\.').mean()),3), quoted=round(float(T.text.str.startswith('"').mean()),3),
  cards_per_draft=T.groupby('draft').size().value_counts().to_dict(), x_nonzero=int((T.x.abs()>0.01).sum()))
first=T.sort_values('t_start').groupby('draft').head(1)
out['hook_card']=dict(scale=q(first.scale),pct_from_top=q(first.pct_from_top),dur=q(first.t_dur),n_words=q(first.n_words),max_chars_line=q(first.max_chars_line),n_lines=first.n_lines.value_counts().to_dict(),n_emojis=first.n_emojis.value_counts().to_dict())
J=T[T.grp.notna()]; Jf=J.sort_values('t_start').groupby('draft').head(1)
wf={}
for g,d in Jf.groupby('grp'):
    allc=J[J.grp==g]
    wf[g]=dict(n_reels=int(len(d)),scale=q(d.scale),pct_from_top=q(d.pct_from_top),n_words=q(d.n_words),n_lines_2plus=round(float((d.n_lines>1).mean()),2),
      n_emojis=round(float(d.n_emojis.mean()),2),max_chars_line=q(d.max_chars_line),hook_dur=q(d.t_dur),cards_per_reel=round(float(allc.groupby('draft').size().mean()),2),
      quoted=round(float(d.text.str.startswith('"').mean()),2),ellipsis=round(float(d.text.str.contains(r'\.\.').mean()),2),upper=q(d.upper_ratio),
      stroke_009=round(float((d.stroke_width==0.09).mean()),2))
out['win_vs_flop_hookcard']=wf
out['by_format']={f:dict(n=int(len(d)),scale_med=round(float(d.scale.median()),3),top_med=round(float(d.pct_from_top.median()),1),cards_per_reel=round(float(d.groupby('draft').size().mean()),2)) for f,d in T[T.format.notna()].groupby('format')}
out['by_page']={f:dict(n=int(len(d)),scale_med=round(float(d.scale.median()),3),top_med=round(float(d.pct_from_top.median()),1)) for f,d in T[T.page.notna()].groupby('page')}
out['outliers']=T[(T.stroke_width!=0.09)|(T.pct_from_top>30)|(T.fill!='#ffffff')][['draft','reel_key','text','fill','stroke_color','stroke_width','pct_from_top','scale','bg_style']].to_dict('records')
v=S[S.kind=='videos']; a=S[S.kind=='audios']; ad=S[S.kind=='adjust']
out['video']=dict(n=len(v),speed_ne1=round(float((v.speed.sub(1).abs()>.01).mean()),3),speed_vals=v.speed.round(2).value_counts().head(10).to_dict(),
  muted_share=round(float((v.volume==0).mean()),3),boosted_share=round(float((v.volume>1.01).mean()),3),zoomed=int((v.scale.sub(1).abs()>.01).sum()),
  transitions=int(v.transition.fillna('').ne('').sum()),keyframes=int(v.keyframes.sum()),cropped=int(v.cropped.sum()),reverse=int(v.reverse.fillna(False).sum()),
  adjust_layers=int(len(ad)),adjust_drafts=int(ad.draft.nunique()))
mus=a[a.audio_name.str.contains('Christmas|Wham|Bubl|Mariah|Boombastic|Free Bird|Snow|Chestnut|memory|Rockin|Sean Paul|Holly',case=False,na=False)]
out['music']={n:dict(n=int(len(d)),in_point_med=round(float(d.src_start.median()),2),vol_med=round(float(d.volume.median()),2)) for n,d in mus.groupby('audio_name')}
out['adjust_typical']=ad.adjust.value_counts().head(3).to_dict()
json.dump(out,open('style/style_stats.json','w'),indent=1,default=str,ensure_ascii=False)
print(json.dumps({k:out[k] for k in ['all','hook_card','win_vs_flop_hookcard','video']},indent=0,default=str,ensure_ascii=False)[:6000])
