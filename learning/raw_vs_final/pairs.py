import pandas as pd,numpy as np,re,json,os,collections
P=pd.read_pickle('perf.pkl')
k2r={}
for i,r in P.iterrows():
    for k in r['keys']: k2r[k]=r.uid
S=pd.read_csv('draft_segments.csv')
DM=pd.read_csv('draft_reel_match.csv')
links=[]
for r in DM.itertuples():
    if r.sim==r.sim and r.sim>=0.7 and r.sim-r.sim2>=0.15:
        links.append((r.draft,r.best,'clip-timeline CLIP match sim=%.2f (2nd %.2f)'%(r.sim,r.sim2),'high' if r.sim>=0.85 else 'medium'))
# BrickHood drafts whose raws were deleted: exact-duration match to proven BH finals
links+= [('0928','bh_post122094812265500948','duration 10.733s == finished vid 2.mp4 (proven final)','medium'),
         ('0928 (2)','bh_post122094925563500948','duration 12.433s == use for ad multi.mp4 / RIP THIS (proven final); earliest of 4 same-length drafts','medium'),
         ('0928 (3)','bh_post122094852045500948','duration 11.8s == BANGER 2.mp4 (proven final)','medium')]
links+=[('1007','mgs_6_67K_1703965718404034','CLIP sim 0.92; same edit cross-posted to IG 40.3K','high'),('1007','ig_ig_40.3K_DePucbFyXdY','CLIP sim 0.95; cross-post of mgs_6','high'),('1007 (3)','merryfires_1101086242506423','CLIP sim 0.93; cross-posted to IG 9K','high'),('1007 (3)','ig_ig_9K_DeYZse3q1Xl','CLIP sim 0.95','high')]
L=pd.DataFrame(links,columns=['draft','reel_key','evidence','confidence']);L['uid']=L.reel_key.map(k2r)
# prompt lookup
uu=re.compile(r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})')
PR={}
H=pd.read_csv('/workspace/hf_match/matches.csv')
for r in H.itertuples():
    for u in uu.findall(str(r.output_url))+[str(r.generation_id)]: PR.setdefault(u,(r.model,str(r.prompt),str(r.start_frame_image),'hf_match'))
for k,v in json.load(open('/workspace/hf_match/prompts_all.json')).items():
    for u in uu.findall(str(v.get('url','')))+[k]: PR.setdefault(u,(v.get('model',''),v.get('prompt',''),str(v.get('start_frame') or v.get('image','')),'prompts_all'))
C=pd.read_csv('/workspace/team/mac/out/clip_prompts.csv')
for r in C.itertuples():
    for u in [str(r.result_uuid),str(r.job_id)]: PR.setdefault(u,(r.model,str(r.prompt),'','mac_clip_prompts'))
PP=pd.read_csv('/workspace/team/mac/out/prompts.csv')
for r in PP.itertuples():
    for u in uu.findall(str(r.job_ids))+uu.findall(str(r.result_file)): PR.setdefault(u,(r.model,str(r.prompt),str(r.refs),'mac_prompts'))
man=pd.read_csv('/workspace/team/mac/out/manifest.csv');dur={'/Users/omar/'+r.mac_path:r.duration_s for r in man.itertuples()}
rows=[]
for l in L.itertuples():
    g=S[S.draft==l.draft]
    for s in g[g.ttype=='video'].sort_values(['track','tgt_start']).itertuples():
        m=uu.search(str(s.path)); u=m.group(1) if m else ''
        pr=PR.get(u,('','','',''))
        md=s.mat_dur if s.mat_dur else dur.get(s.path,np.nan)
        src_in=s.src_start if s.src_start==s.src_start else 0; src_out=src_in+(s.src_dur if s.src_dur==s.src_dur else s.tgt_dur*s.speed)
        rows.append(dict(reel_uid=l.uid,reel_key=l.reel_key,draft=l.draft,match_confidence=l.confidence,match_evidence=l.evidence,
            track=s.track,clip_order=None,raw_path=s.path,raw_file=os.path.basename(str(s.path)),gen_uuid=u,raw_dur=round(md,3) if md==md else '',
            src_in=round(src_in,3),src_out=round(src_out,3),cut_head=round(src_in,3),cut_tail=round(md-src_out,3) if md==md else '',
            kept_frac=round((src_out-src_in)/md,3) if md==md and md else '',tgt_start=round(s.tgt_start,3),tgt_dur=round(s.tgt_dur,3),speed=s.speed,
            volume=s.volume,scale=s.scale,tx=s.tx,ty=s.ty,crop=s.crop,model=pr[0],prompt=str(pr[1])[:1500],start_frame=pr[2],prompt_src=pr[3]))
X=pd.DataFrame(rows)
X['clip_order']=X.groupby(['draft','track']).cumcount()+1
# reuse across reels
X['used_in_n_reels']=X.groupby('raw_file').reel_uid.transform('nunique')
X.to_csv('pairs.csv',index=False)
L.to_csv('draft_to_reel.csv',index=False)
print(len(L),L.uid.nunique(),len(X),'prompts:',(X.prompt!='').sum())
print(L.merge(P[['uid','views','rank']],on='uid').sort_values('views',ascending=False).to_string())
