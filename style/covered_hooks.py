"""Covered-reveal hook audit (2026-10-18 PT). Builds covered_hooks.csv (one row per covered-reveal EDIT, max views across FB/IG copies)
and covered_stats.json (covered vs other hooks: shot-coded set, full own corpus, robe-only control).
Covered reveal = at 0 s the product is under/inside a cover (tray, muffin tin, cloth, drape, pot, blanket) or disguised as another object, and a 3-2-1 / pull reveal follows.
Coding is from frames at 0-5 s (_work/covered/*.jpg, _work/covered/igs/*.jpg) and shot midpoints (_work/covered/shots/*.jpg). Run from anywhere."""
import pandas as pd, numpy as np, json, re
from scipy.stats import fisher_exact, mannwhitneyu
W='/workspace/hookforge/'
# key, platform, page, views(max across copies), copies, posted(PT), product, cover, product_cue_at_0, cue_matches_product, reveal_s(approx), setting, camera, people, vo_321, source paths
C=[
("HJ-02","FB","HeatedJammies",2700000,"","2026-09-08","heated Grinch robe","robe folded into a 'baked loaf' on a tray","yes: lime fur + red Grinch heart fill 35% of frame","yes",3.0,"bedroom","static MS eye","1 woman, face","yes ('One, two, three. Let's see how it comes out')","/workspace/merryjammies/videos/fb_2.7M_1381141263599559.mp4"),
("HJ-05","FB","HeatedJammies",524000,"","2026-09-27","heated Grinch robe","muffin tin pressed on folded robe","yes: lime fur + red Santa trim, 40%","yes",2.6,"living room","static MS eye","1 teen boy, face","yes (3,2,1)","/workspace/merryjammies/videos/fb_524K_38670473745933796.mp4"),
("MJIG-17","IG","merry.jammies IG",240694,"","2026-09-10","heated Grinch robe","lime fur drape (the robe fabric itself) over a store pallet, staff line-up","yes: drape IS the product's fur/colour","yes",1.2,"warehouse store","static WS eye","staff crowd","no (music)","https://www.instagram.com/reel/DdGdL41KJo4/ ; box copy /workspace/hookforge/style/_work/covered/ig/DdGdL41KJo4.mp4"),
("HJ-10","FB","HeatedJammies",147000,"","2026-09-11","heated Grinch robe","Grinch-green drape over Target display, staff line-up","yes: drape in product colour","yes",2.3,"Target store","static WS eye","12 staff","yes (3,2,1)","/workspace/merryjammies/videos/fb_147K_1792686372082535.mp4"),
("HJ-14","FB","HeatedJammies",97000,"","2026-09-11","heated Grinch robe","muffin tin on Grinch-face robe","yes: Grinch face + fur, 60%","yes",3.0,"living room","static MS eye, torso only","1 woman, no face","yes (3,2,1)","/workspace/merryjammies/videos/fb_97K_1410783157651567.mp4"),
("IG-DdDqyRKqDQc","IG","merry.jammies IG",28900,"","2026-09-08","heated Grinch robe","huge green drape yanked off store shelving by a worker","partial: green drape, product colour","yes",3.5,"warehouse store","handheld WS eye","1 worker + shoppers","unknown","https://www.instagram.com/reel/DdDqyRKqDQc/ ; /workspace/hookforge/style/_work/covered/ig/DdDqyRKqDQc.mp4"),
("HJ-22","FB","HeatedJammies",16000,"","2026-09-16","heated Grinch robe","robe loaf on tray, SMALL in frame","yes but small (15%)","yes",2.5,"living room","static WS eye","1 woman, full body","yes ('Three, two, one...')","/workspace/merryjammies/videos/fb_16K_1655048449619269.mp4"),
("MJIG-04","IG","merry.jammies IG",9007,"MF-02 FB MerryFires 3,084 (same edit)","2026-10-11","MerryFire tabletop fire pit","green cloth loaf on tray (robe look) over a fire pit","no: cloth reads as the ROBE, no flame/glow","no (mismatch)",4.5,"bedroom","static MS eye","1 woman, face","yes ('One, two, three!')","/workspace/merryjammies/videos/ig_9K_DeYZse3q1Xl.mp4 ; /workspace/fb2/videos/merryfires_1101086242506423.mp4"),
("HJ-25","FB","HeatedJammies",6200,"","2026-09-08","heated Grinch robe","black cloth held up by couple in store","no: opaque black","no",2.8,"store","static MS eye","couple, faces","yes ('Three, two, one...')","/workspace/merryjammies/videos/fb_6.2K_28206279789000326.mp4"),
("HJ-26","FB","HeatedJammies",5900,"","2026-09-04","heated Grinch robe","black tray over coiled robe","yes: fur + white trim, 30%","yes",3.0,"living room (US flag)","static MS eye","1 woman, face","yes (3,2,1)","/workspace/merryjammies/videos/fb_5.9K_1606892301089465.mp4"),
("HJ-29","FB","HeatedJammies",4600,"","2026-09-10","heated Grinch robe","robe loaf on tray (near-copy of HJ-02 two days later)","yes: fur + heart, 30%","yes",4.0,"bedroom","static MS eye","1 woman, face","non-English VO","/workspace/merryjammies/videos/fb_4.6K_973615392415491.mp4"),
("IG-Dcw9GXbK6u7","IG","merry.jammies IG",3600,"","2026-09-01","heated Grinch robe","grey tray on folded robe","yes: fur + heart, 40%","yes",2.5,"living room","static MS eye","1 young man, face","unknown","https://www.instagram.com/reel/Dcw9GXbK6u7/ ; /workspace/hookforge/style/_work/covered/ig/Dcw9GXbK6u7.mp4"),
("MJIG-08","IG","merry.jammies IG",3256,"","2026-09-29","Smiley ski mask","plaid blanket over a pan","no: fully hidden","no",4.0,"ski slope","static MS eye","1 man, face","yes ('Three, two, one...')","/workspace/merryjammies/videos/ig_3.3K_Dd4imkOqOZY.mp4"),
("MJIG-09","IG","merry.jammies IG",2664,"","2026-09-29","Smiley ski mask","steel pot held over the mask","no: fully hidden","no",2.5,"ski slope","static MS eye","1 man, face","no","/workspace/merryjammies/videos/ig_2.7K_Dd3UwSRqGCC.mp4"),
("MJIG-12","IG","merry.jammies IG",1071,"","2026-10-02","Smiley ski mask","plaid blanket over a pan","no: fully hidden","no",4.0,"ski resort base","static MS eye","1 man, face","yes ('Three, two...')","/workspace/merryjammies/videos/ig_1.1K_DeAuCnPvBYP.mp4"),
("MGS-09","FB","Merry Glows",457,"","2026-10-08","fire pit","cream cloth over tray","no: fully hidden, no glow","no",3.2,"snowy outdoor","static MS eye","1 woman, face","yes ('One, two, three...')","/workspace/fb2/videos/mgs_3_455_28876831118647366.mp4"),
("PV-02","FB","Purrventure",np.nan,"","2026-10-18","pop-up cat carrier","navy cloth over display, pet-store staff line-up","no: opaque navy","no",2.8,"pet store","static WS eye","20 staff","yes ('Three, two, one!')","/workspace/purrventure/videos/pv_1422397339426383.mp4 (views unavailable; excluded from stats)"),
]
cols="reel_key platform page views other_copies posted product cover product_cue_at_0 cue_matches_product reveal_s setting camera people vo_321 source".split()
D=pd.DataFrame(C,columns=cols)
D['cue_visible']=D.product_cue_at_0.str.startswith(('yes','partial'))&(D.cue_matches_product=='yes')
D['grp']=np.where(D.views>=50000,'win',np.where(D.views<10000,'flop',np.where(D.views.notna(),'mid','na')))
D.to_csv(W+'style/covered_hooks.csv',index=False)
COV=set(D.reel_key)|{"MF-02"}
out={}
def rate(df,flag):
    a=df[df[flag]]; b=df[~df[flag]]
    t=[[int(a.hit.sum()),int(len(a)-a.hit.sum())],[int(b.hit.sum()),int(len(b)-b.hit.sum())]]
    return dict(covered=f"{t[0][0]}/{len(a)}",other=f"{t[1][0]}/{len(b)}",covered_median=float(a.views.median()),other_median=float(b.views.median()),
                fisher_p=round(fisher_exact(t)[1],3),mwu_p=round(mannwhitneyu(a.views,b.views)[1],3))
# 1) shot-coded set (ours), same edit counted once
R=pd.read_csv(W+'style/shots_by_reel.csv'); R=R[R.reel_key!='MF-02']
out['shot_coded']=rate(R,'covered')|dict(n=len(R))
# 2) full own corpus: features.csv own reels with views + merry.jammies IG reels not already in features (matched by views +-2%)
f=pd.read_csv(W+'data/features/features.csv',low_memory=False); o=f[(f.source=='own')&f.views.notna()][['corpus_key','views','product']].rename(columns={'corpus_key':'reel_key'})
o=o[o.reel_key!='MF-02']
txt=open('/workspace/team/instagram/merryjammies_ig_reels.md').read()
ig=[(c,int(v.replace(',',''))) for c,v in re.findall(r'^(\S{11}) \| \w+ \d+ \| ([\d,]+)',txt,re.M)]
ig+=[(c,int(float(v[:-1])*1000) if v.endswith('K') else int(v)) for c,v in re.findall(r'(\S{11}) \w+\d+ ([\d.]+K?)',txt)]
igkey={'DdGdL41KJo4':'MJIG-17','DdDqyRKqDQc':'IG-DdDqyRKqDQc','Dcw9GXbK6u7':'IG-Dcw9GXbK6u7'}
mj=o[o.reel_key.str.startswith('MJIG')]
add=[]
for c,v in ig:
    if ((mj.views-v).abs()/v<0.02).any(): continue
    add.append(dict(reel_key=igkey.get(c,'IG-'+c),views=v,product='heated Grinch robe' if c.startswith(('Dc','Dd')) else 'other'))
A=pd.concat([o,pd.DataFrame(add)],ignore_index=True)
A['covered']=A.reel_key.isin(COV); A['hit']=A.views>=50000
out['own_corpus']=rate(A,'covered')|dict(n=len(A),n_ig_added=len(add))
rob=A[A['product'].fillna('').str.contains('robe')]
out['robe_only']=rate(rob,'covered')|dict(n=len(rob))
rob2=rob[~rob.reel_key.isin(['HJ-26','IG-Dcw9GXbK6u7'])]  # sanity: drop page-launch-week covered posts
# 3) inside covered: what separates winners
d=D[D.views.notna()]
out['covered_split']=dict(
  cue_visible=f"{int(d[d.cue_visible].views.ge(50000).sum())}/{int(d.cue_visible.sum())} wins, median {int(d[d.cue_visible].views.median())}",
  fully_hidden_or_mismatch=f"{int(d[~d.cue_visible].views.ge(50000).sum())}/{int((~d.cue_visible).sum())} wins, median {int(d[~d.cue_visible].views.median())}",
  fisher_p=round(fisher_exact([[int(d[d.cue_visible].views.ge(50000).sum()),int((d.cue_visible&d.views.lt(50000)).sum())],[int(d[~d.cue_visible].views.ge(50000).sum()),int((~d.cue_visible&d.views.lt(50000)).sum())]])[1],3),
  reveal_s_wins=d[d.views>=50000].reveal_s.tolist(), reveal_s_rest=d[d.views<50000].reveal_s.tolist(),
  wins_reveal_le_3s=f"{int((d[d.views>=50000].reveal_s<=3.0).sum())}/{int((d.views>=50000).sum())}",
  rest_reveal_le_3s=f"{int((d[d.views<50000].reveal_s<=3.0).sum())}/{int((d.views<50000).sum())}")
json.dump(out,open(W+'style/covered_stats.json','w'),indent=1)
print(json.dumps(out,indent=1)); print(A[A.covered].sort_values('views',ascending=False).to_string())
