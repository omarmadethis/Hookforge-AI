import pandas as pd,os,glob
from PIL import Image,ImageDraw,ImageFont
X=pd.read_csv('pairs.csv');man=pd.read_csv('/workspace/team/mac/out/manifest.csv')
p2i={'/Users/omar/'+r.mac_path:os.path.basename(r.proxy_box_path)[:-4] for r in man.itertuples()}
font=ImageFont.load_default()
def rawframe(path,t):
    if path.startswith('mac:'): path='/Users/omar/'+path[4:]
    if path.startswith(('hf:','team:')):
        k=path.split(':',1)[1];d=f"/workspace/hf_match/fr_{'hf' if path.startswith('hf') else 'team'}/{k}";fps=2
    else:
        i=p2i.get(path); d=f"/workspace/team/mac/fr_mac/{i}" if i else None;fps=4
    if not d or not os.path.isdir(d):
        import re;m=re.search(r'([0-9a-f]{8}-[0-9a-f-]{27})',path)
        if m:
            c=glob.glob(f'/workspace/hf_match/fr_*/*{m.group(1)}*');
            if c: d=c[0];fps=2
    if not d or not os.path.isdir(d): return None
    fs=sorted(os.listdir(d)); k=min(max(int(t*fps),0),len(fs)-1); return Image.open(os.path.join(d,fs[k]))
def reelframe(key,uid,t):
    for d in [f'/workspace/hf_match/fr_reel/{key}',f'fr_own/{uid}',f'fr_own/{key}']:
        if os.path.isdir(d):
            fs=sorted(os.listdir(d));return Image.open(os.path.join(d,fs[min(int(t*4),len(fs)-1)]))
W,H=128,228
def sheet(key,draft,title,out):
    g=X[(X.reel_key==key)&(X.draft==draft)&(X.track==0)].sort_values('tgt_start')
    g=g[~g.raw_file.str.endswith(('png','webp'))]
    im=Image.new('RGB',(W*5+260,(H+16)*len(g)+40),'white');dr=ImageDraw.Draw(im)
    dr.text((5,5),title,fill='black',font=font);dr.text((5,20),'cols: FINAL@mid | RAW start(0s) | RAW in | RAW out | RAW end  -> notes',fill='gray',font=font)
    y=40
    for r in g.itertuples():
        uid=r.reel_uid
        fr=[reelframe(key,uid,r.tgt_start+r.tgt_dur/2)]+[rawframe(r.raw_path,t) for t in [0,r.src_in,max(r.src_out-0.1,0),float(r.raw_dur)-0.1]]
        for j,f in enumerate(fr):
            if f: im.paste(f.convert('RGB').resize((W,H)),(j*W,y))
            else: dr.rectangle([j*W,y,j*W+W-2,y+H],outline='red')
        txt=f"#{r.clip_order} t={r.tgt_start:.2f}+{r.tgt_dur:.2f}s\nraw {str(r.raw_file)[:28]}\nlen {float(r.raw_dur):.2f}s keep {r.src_in:.2f}-{r.src_out:.2f}\nhead cut {r.cut_head:.2f} tail cut {r.cut_tail}\nspeed {r.speed} vol {r.volume}\nmodel {r.model}"
        dr.multiline_text((5*W+6,y+4),txt,fill='black',font=font,spacing=3);y+=H+16
    im.save(out,quality=85);print(out,len(g))
sheet('ig_Ddii6mOKO2G','0920 (1)','#2 IG 4.63M views - draft 0920 (1) vs raw Seedance clips','contact_sheets/01_ig_4.6M_Ddii6mOKO2G.jpg')
sheet('fb_6.6M_1624473615929591','(no draft: reconstructed from frames)','#1 FB HeatedJammies 6.6M - reconstructed (no CapCut draft survives)','contact_sheets/02_fb_6.6M.jpg')
sheet('fb_2.7M_1381141263599559','(no draft: reconstructed from frames)','#3 FB HeatedJammies 2.7M - reconstructed','contact_sheets/03_fb_2.7M.jpg')
sheet('fb_1.4M_2121138075159387','(no draft: reconstructed from frames)','#5 FB HeatedJammies 1.4M (Target/Walmart) - reconstructed','contact_sheets/04_fb_1.4M_2121.jpg')
sheet('ig_DdQw1jyKI63','0913 (1)','#6 IG 687K - draft 0913 (1)','contact_sheets/05_ig_687K_DdQw1jyKI63.jpg')
