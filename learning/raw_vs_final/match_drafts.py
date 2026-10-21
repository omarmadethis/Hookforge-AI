import numpy as np,pandas as pd,os,collections
S=pd.read_csv('draft_segments.csv')
man=pd.read_csv('/workspace/team/mac/out/manifest.csv')
p2i={'/Users/omar/'+r.mac_path:os.path.basename(r.proxy_box_path)[:-4] for r in man.itertuples()}
def load(f,key=-2):
    z=np.load(f,allow_pickle=True);d=collections.defaultdict(dict)
    for p,e in zip(z['paths'],z['emb']):
        parts=p.split('/');d[parts[key]][int(parts[-1][:4])-1]=e
    return {k:np.stack([v[i] for i in sorted(v)]) for k,v in d.items()}
mac=load('/workspace/team/mac/emb_mac.npz')
reels=load('/workspace/hf_match/emb_reel.npz'); reels.update(load('emb_own.npz'))
import re
uu=re.compile(r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})')
U={}
for f in ['/workspace/hf_match/emb_hf.npz','/workspace/hf_match/emb_team.npz','/workspace/hf_match/emb_lib.npz']:
    for k,v in load(f).items():
        m=uu.search(k)
        if m: U.setdefault(m.group(1),v)
for p in S.path.dropna().unique():
    if p not in p2i:
        m=uu.search(p)
        if m and m.group(1) in U: mac['U'+m.group(1)]=U[m.group(1)]; p2i[p]='U'+m.group(1)
print(len(mac),len(reels))
out=[];cov=[]
for dr,g in S.groupby('draft'):
    v=g[g.ttype=='video'].sort_values('track')
    if not len(v): continue
    dur=(v.tgt_start+v.tgt_dur).max(); ts=np.arange(0,dur,0.25)
    seq=[];miss=0
    for t in ts:
        c=v[(v.tgt_start<=t+1e-6)&(t<v.tgt_start+v.tgt_dur)]
        if not len(c): seq.append(None);continue
        s=c.iloc[-1]; i=p2i.get(s.path)
        if i is None or i not in mac: seq.append(None);miss+=1;continue
        st=(s.src_start if s.src_start==s.src_start else 0)+(t-s.tgt_start)*s.speed
        k=min(int(round(st*4)),len(mac[i])-1); seq.append(mac[i][k])
    ok=[j for j,x in enumerate(seq) if x is not None]
    if len(ok)<len(ts)*0.4: out.append(dict(draft=dr,dur=dur,coverage=len(ok)/len(ts),best='',sim=np.nan,second='',sim2=np.nan));continue
    E=np.stack([seq[j] for j in ok]);res=[]
    for rk,R in reels.items():
        best=-1
        for off in range(-4,5):
            idx=[j+off for j in ok]; sel=[(a,b) for a,b in zip(range(len(ok)),idx) if 0<=b<len(R)]
            if len(sel)<len(ok)*0.6: continue
            a=np.array([x for x,_ in sel]);b=np.array([y for _,y in sel])
            sims=(E[a]*R[b]).sum(1); sc=np.median(sims)*0.5+np.mean(sims>0.9)*0.5
            best=max(best,sc)
        res.append((best,rk))
    res.sort(reverse=True)
    out.append(dict(draft=dr,dur=round(dur,2),coverage=round(len(ok)/len(ts),2),best=res[0][1],sim=round(res[0][0],3),second=res[1][1],sim2=round(res[1][0],3)))
O=pd.DataFrame(out);O.to_csv('draft_reel_match.csv',index=False)
pd.set_option('display.width',200);print(O.sort_values('sim',ascending=False).to_string())
