import numpy as np,pandas as pd,collections,re,sys,json
def load(f):
    z=np.load(f,allow_pickle=True);d=collections.defaultdict(dict)
    for p,e in zip(z['paths'],z['emb']):
        parts=p.split('/');d[parts[-2]][int(parts[-1][:4])-1]=e
    return {k:np.stack([v[i] for i in sorted(v)]) for k,v in d.items()}
man=pd.read_csv('/workspace/team/mac/out/manifest.csv')
rawk=set(man[man.kind.isin(['raw_generation','product_folder_clip','other_short','capcut_media'])].proxy_box_path.str.split('/').str[-1].str[:-4])
i2p=dict(zip(man.proxy_box_path.str.split('/').str[-1].str[:-4],man.mac_path))
pool={}
for k,v in load('/workspace/team/mac/emb_mac.npz').items():
    if k in rawk: pool['mac:'+i2p[k]]=v
for f,t in [('/workspace/hf_match/emb_hf.npz','hf'),('/workspace/hf_match/emb_team.npz','team')]:
    for k,v in load(f).items(): pool[t+':'+k]=v
names=list(pool);lens=[len(pool[n]) for n in names]
A=np.concatenate([pool[n] for n in names]);own=np.repeat(np.arange(len(names)),lens);fi=np.concatenate([np.arange(l) for l in lens])
reels=load('/workspace/hf_match/emb_reel.npz');reels.update(load('emb_own.npz'))
out=[]
for key in sys.argv[1:]:
    R=reels[key];S=R@A.T
    best=S.argmax(1);bs=S.max(1)
    segs=[];cur=None
    for t,(b,s) in enumerate(zip(best,bs)):
        c=own[b] if s>=0.88 else -1
        if cur and cur['c']==c: cur['t'].append(t);cur['f'].append(fi[b]);cur['s'].append(s)
        else:
            cur=dict(c=c,t=[t],f=[fi[b]],s=[s]);segs.append(cur)
    for g in segs:
        if g['c']<0: out.append(dict(reel=key,tgt_start=g['t'][0]/4,tgt_dur=len(g['t'])/4,clip='(unmatched)',src_in='',src_out='',speed_est='',raw_len='',sim=round(float(np.mean(g['s'])),3)));continue
        f=np.array(g['f']);t=np.array(g['t'])
        sp=np.polyfit(t,f,1)[0] if len(t)>=3 else 1.0
        out.append(dict(reel=key,tgt_start=t[0]/4,tgt_dur=len(t)/4,clip=names[g['c']],src_in=f.min()/4,src_out=(f.max()+1)/4,speed_est=round(sp,2),raw_len=lens[g['c']]/4,sim=round(float(np.mean(g['s'])),3)))
O=pd.DataFrame(out);O.to_csv('recon_'+('_'.join(sys.argv[1:]) if len(sys.argv)<3 else 'batch')+'.csv',index=False)
pd.set_option('display.width',250);pd.set_option('display.max_colwidth',70);print(O.to_string())
