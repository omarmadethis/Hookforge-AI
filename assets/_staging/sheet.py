import sys, os, hashlib, json
from PIL import Image, ImageDraw, ImageFont
root=sys.argv[1]; tag=sys.argv[2]
files=sorted(os.path.join(dp,f) for dp,_,fs in os.walk(root) for f in fs if f.lower().endswith(('.png','.jpg','.jpeg','.webp')) or f=='main logo')
idx=[]
seen={}
for f in files:
    h=hashlib.md5(open(f,'rb').read()).hexdigest()
    try:
        im=Image.open(f); w,hh=im.size
    except Exception as e:
        w=hh=0
    idx.append(dict(i=len(idx),path=f,md5=h,w=w,h=hh,dup_of=seen.get(h)))
    seen.setdefault(h,len(idx)-1)
json.dump(idx,open(f'/workspace/hookforge/assets/_staging/sheets/{tag}_index.json','w'),indent=1)
uniq=[d for d in idx if d['dup_of'] is None]
T=300; cols=5; per=20
font=ImageFont.load_default(size=22) if hasattr(ImageFont,'load_default') else None
for s in range(0,len(uniq),per):
    chunk=uniq[s:s+per]; rows=(len(chunk)+cols-1)//cols
    sheet=Image.new('RGB',(cols*T,rows*(T+30)),'white'); d=ImageDraw.Draw(sheet)
    for k,it in enumerate(chunk):
        x=(k%cols)*T; y=(k//cols)*(T+30)
        try:
            im=Image.open(it['path']).convert('RGB'); im.thumbnail((T-6,T-6)); sheet.paste(im,(x+3,y+30))
        except Exception as e: pass
        d.text((x+4,y+2),f"#{it['i']} {it['w']}x{it['h']}",fill='red',font=font)
    sheet.save(f'/workspace/hookforge/assets/_staging/sheets/{tag}_{s//per:02d}.jpg',quality=80)
print(len(idx),len(uniq))
