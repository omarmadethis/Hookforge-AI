import json,os,glob,csv,re
R="/workspace/team/mac/text/Movies/CapCut/User Data/Projects/com.lveditor.draft"
out=[];segs=[]
for p in sorted(glob.glob(R+"/*/draft_info.json")):
    name=p.split('/')[-2]
    try:d=json.load(open(p))
    except Exception as e: continue
    m=d['materials']; mats={}
    for k in ('videos','audios','texts'):
        for x in m.get(k,[]): mats[x['id']]=(k,x)
    spd={x['id']:x.get('speed',1) for x in m.get('speeds',[])}
    for ti,t in enumerate(d['tracks']):
        for s in t['segments']:
            k,x=mats.get(s['material_id'],(t['type'],{}))
            st=s.get('source_timerange') or {}; tt=s['target_timerange']
            row=dict(draft=name,track=ti,ttype=t['type'],tgt_start=tt['start']/1e6,tgt_dur=tt['duration']/1e6,
              src_start=(st.get('start') or 0)/1e6 if st else '',src_dur=(st.get('duration') or 0)/1e6 if st else '',
              speed=s.get('speed',1),volume=s.get('volume',''),
              scale=(s.get('clip') or {}).get('scale',{}).get('x',''),tx=(s.get('clip') or {}).get('transform',{}).get('x',''),ty=(s.get('clip') or {}).get('transform',{}).get('y',''),
              path=x.get('path',''),mat_dur=(x.get('duration') or 0)/1e6,w=x.get('width',''),h=x.get('height',''),text='',font_size='',stroke='')
            if k=='texts':
                try:
                    c=json.loads(x['content']);row['text']=c['text'].replace('\n',' / ')
                    stl=c['styles'][0];row['font_size']=stl.get('size');row['stroke']=(stl.get('strokes') or [{}])[0].get('width','')
                except: row['text']=x.get('content','')[:200]
            if k=='audios': row['path']=x.get('path') or x.get('name')
            crop=x.get('crop') if k=='videos' else None
            row['crop']='' if not crop or crop.get('upper_left_x',0)==0 and crop.get('lower_right_x',1)==1 and crop.get('upper_left_y',0)==0 and crop.get('lower_right_y',1)==1 else json.dumps(crop)
            segs.append(row)
    out.append(dict(draft=name,duration=d['duration']/1e6,n_tracks=len(d['tracks'])))
with open('draft_segments.csv','w') as f:
    w=csv.DictWriter(f,list(segs[0].keys()));w.writeheader();w.writerows(segs)
print(len(out),len(segs))
