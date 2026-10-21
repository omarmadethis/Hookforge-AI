"""Omar's CapCut editing style -> style.json + per-draft/per-shot CSVs. Read-only on drafts (box mirror of Mac
~/Movies/CapCut/User Data/Projects/com.lveditor.draft, refreshed copies in ./fresh override). Drafts that only wrap
Hookforge renders (trumpglow_/jollyglow_/HF_TEST) are excluded: they're our edits, not his."""
import json,glob,os,re,math,csv,statistics as st
HERE=os.path.dirname(os.path.abspath(__file__)); REPO=os.path.abspath(os.path.join(HERE,"..",".."))
ROOT="/workspace/team/mac/text/Movies/CapCut/User Data/Projects/com.lveditor.draft"
US=1e6; OURS=re.compile(r"trumpglow_|jollyglow_|HF_TEST|hookforge",re.I)
EMO=re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\u2300-\u23FF\uFE0F\u200D]")
def views_map():
    v={}
    try:
        for r in csv.DictReader(open(f"{REPO}/private/edits/edits.csv")):
            try: v[r['draft']]=float(r['views']) if r['views'] else None
            except: pass
    except FileNotFoundError: pass
    try:
        for r in csv.DictReader(open(f"{REPO}/learning/raw_vs_final/draft_features.csv")):
            if r['views'] and not v.get(r['draft']): v[r['draft']]=float(r['views'])
    except FileNotFoundError: pass
    return v
def kf_types(seg):
    return [k.get('property_type') for k in (seg.get('common_keyframes') or [])]
def parse(p,name,views):
    d=json.load(open(p)); m=d['materials']; W=d['canvas_config']['width']; H=d['canvas_config']['height']
    by={}
    for k,v in m.items():
        if isinstance(v,list):
            for x in v:
                if isinstance(x,dict) and 'id' in x: by[x['id']]=(k,x)
    vids=[];txt=[];aud=[];effects=0
    for tr in d['tracks']:
        for s in tr['segments']:
            k,x=by.get(s['material_id'],(tr['type'],{}))
            tt=s['target_timerange']; t0=tt['start']/US; du=tt['duration']/US
            refs=[by[r] for r in s.get('extra_material_refs',[]) if r in by]
            fade=[x2 for k2,x2 in refs if k2=='audio_fades']
            fin=fade[0]['fade_in_duration']/US if fade else 0; fout=fade[0]['fade_out_duration']/US if fade else 0
            if tr['type']=='video':
                if OURS.search(x.get('path','') or ''): return None
                st0=(s.get('source_timerange') or {}).get('start',0)/US
                cl=s.get('clip') or {}
                vids.append(dict(t0=t0,dur=du,speed=round(s.get('speed',1),3),vol=s.get('volume',1),src_in=st0,
                    mat=x.get('path','').split('/')[-1],mat_dur=(x.get('duration') or 0)/US,scale=(cl.get('scale') or {}).get('x',1),
                    kf=kf_types(s),track=tr.get('id'),main=not aud and len(vids)==0 or True))
            elif tr['type']=='text':
                try: c=json.loads(x['content']); text=c['text']; size=c['styles'][0].get('size',x.get('font_size')); sw=(c['styles'][0].get('strokes') or [{}])[0].get('width',0)
                except Exception: text=x.get('content',''); size=x.get('font_size'); sw=x.get('border_width',0)
                cl=s.get('clip') or {}
                txt.append(dict(t0=t0,dur=du,text=text,size=size,stroke=sw,font=os.path.basename(x.get('font_path','') or ''),
                    color=x.get('text_color'),stroke_color=x.get('border_color'),lmw=x.get('line_max_width'),align=x.get('alignment'),
                    y=(1-(cl.get('transform') or {}).get('y',0))/2,x=(1+(cl.get('transform') or {}).get('x',0))/2,scale=(cl.get('scale') or {}).get('x',1),
                    tmpl=bool(x.get('combo_info',{}).get('text_templates')) ))
            elif tr['type']=='audio':
                aud.append(dict(t0=t0,dur=du,vol=s.get('volume',1),src_in=(s.get('source_timerange') or {}).get('start',0)/US,
                    name=x.get('name',''),type=x.get('type'),fin=fin,fout=fout,kf=kf_types(s)))
    effects=len(m.get('effects',[]))+len(m.get('hsl',[]))
    if not vids: return None
    main_track=max({v['track'] for v in vids},key=lambda t:sum(v['dur'] for v in vids if v['track']==t))
    shots=sorted([v for v in vids if v['track']==main_track],key=lambda v:v['t0'])
    over=[v for v in vids if v['track']!=main_track]
    dur=d['duration']/US
    return dict(draft=name,views=views.get(name),W=W,H=H,dur=dur,shots=shots,overlays=len(over),texts=sorted(txt,key=lambda t:t['t0']),
                audio=aud,effects=effects,transitions=len(m.get('transitions',[])))
def roles(D):
    """hook = shot(s) under the first card / first shot; with >=2 cards: before = 1st card window after hook,
    reveal = first shot starting in the last card window, afters = rest; ending = last shot."""
    sh=D['shots']; tx=[t for t in D['texts'] if t['dur']<D['dur']-0.3]  # changing cards
    for s in sh: s['role']='body'
    sh[0]['role']='hook'
    if len(tx)>=2:
        last=tx[-1]['t0']
        rv=[s for s in sh[1:] if s['t0']>=last-0.15]
        for s in sh[1:]:
            if s['t0']<last-0.15: s['role']='before'
        if rv:
            rv[0]['role']='reveal'
            for s in rv[1:]: s['role']='after'
    if len(sh)>1: sh[-1]['role_end']=True
    return sh
def lines_est(t,W=1080):
    """explicit newlines + wrap estimate: px per char ~0.55em; em px = size/15*0.081*W*scale"""
    em=(t['size'] or 15)/15*0.081*W*(t['scale'] or 1); cap=max(1,int((t['lmw'] or .82)*W/(0.55*em)))
    n=0; cpl=0
    for ln in t['text'].split('\n'):
        L=len(EMO.sub('ww',ln)); n+=max(1,math.ceil(L/cap)); cpl=max(cpl,min(L,cap))
    return n,cpl,em/W
def wq(vals,ws,q):
    pr=sorted(zip(vals,ws)); tot=sum(w for _,w in pr); a=0
    for v,w in pr:
        a+=w
        if a>=q*tot: return v
    return pr[-1][0] if pr else None
def summ(vals,ws=None):
    vals=[v for v in vals if v is not None]
    if not vals: return None
    ws=ws or [1]*len(vals)
    return dict(n=len(vals),median=round(st.median(vals),3),wmedian=round(wq(vals,ws,.5),3),p10=round(wq(vals,ws,.1),3),p90=round(wq(vals,ws,.9),3),min=round(min(vals),3),max=round(max(vals),3))
def main():
    vm=views_map(); paths={}
    for p in glob.glob(f"{ROOT}/*/draft_info.json"): paths[p.split('/')[-2]]=p
    for p in glob.glob(f"{HERE}/fresh/*/draft_info.json"): paths[p.split('/')[-2]]=p
    Ds=[]
    for n,p in sorted(paths.items()):
        try: D=parse(p,n,vm)
        except Exception as e: print("skip",n,e); continue
        if D and D['dur']>3: roles(D); Ds.append(D)
    ALL=Ds; Ds_multi=[D for D in Ds if len(D['shots'])>=3]
    def w(D): return math.log10(max(D['views'] or 1000,1000))-2  # unjoined drafts weigh like 1K views
    TOP=50000
    S={'n_drafts':len(Ds),'n_joined':sum(1 for D in Ds if D['views']),'n_top':sum(1 for D in Ds if (D['views'] or 0)>=TOP),'top_threshold_views':TOP,
       'weighting':'log10(views)-2 per draft (unjoined = 1K); wmedian = weighted median'}
    _keep=Ds; Ds=Ds_multi
    sv=[];sw=[];rl={};sp=[];spr={};hook_sp=[]
    for D in Ds:
        for s in D['shots']:
            out=s['dur']; sv.append(out); sw.append(w(D)); rl.setdefault(s['role'],([],[])); rl[s['role']][0].append(out); rl[s['role']][1].append(w(D))
            spr.setdefault(s['role'],[0,0]); spr[s['role']][1]+=1
            if abs(s['speed']-1)>0.01: sp.append(s['speed']); spr[s['role']][0]+=1
            if s['role']=='hook': hook_sp.append(s['speed'])
    S['timing']=dict(total_duration=summ([D['dur'] for D in Ds],[w(D) for D in Ds]),
        total_duration_top=summ([D['dur'] for D in Ds if (D['views'] or 0)>=TOP]),
        shots_per_video=summ([len(D['shots']) for D in Ds],[w(D) for D in Ds]),
        opener=summ([D['shots'][0]['dur'] for D in Ds],[w(D) for D in Ds]),
        opener_top=summ([D['shots'][0]['dur'] for D in Ds if (D['views'] or 0)>=TOP]),
        shot_len=summ(sv,sw),shot_len_by_role={r:summ(*v) for r,v in rl.items()},
        ending_shot=summ([D['shots'][-1]['dur'] for D in Ds],[w(D) for D in Ds]))
    S['speed']=dict(share_shots_sped=round(len(sp)/max(1,len(sv)),3),values=summ(sp),
        common=sorted({round(x,2):sp.count(x) for x in sp}.items(),key=lambda kv:-kv[1])[:8],
        by_role={r:dict(sped=a,of=b,share=round(a/b,3)) for r,(a,b) in spr.items()},
        hook_speed=summ(hook_sp),share_drafts_any_speed=round(sum(1 for D in Ds if any(abs(s['speed']-1)>.01 for s in D['shots']))/len(Ds),3),
        curve_or_ramp='none seen (speed mode 0 only)')
    Ds=_keep; S['timing']['note']='timing/speed use the %d drafts with >=3 shots (1-2 shot drafts are pre-cut exports)'%len(Ds_multi)
    # cut-on-action proxy: head trim (src_in>0) means he cut into the clip mid-motion instead of from frame 0
    hi=[s['src_in'] for D in Ds for s in D['shots']]
    S['cuts']=dict(transitions_total=sum(D['transitions'] for D in Ds),hard_cuts_only=all(D['transitions']==0 for D in Ds),
        head_trim=summ(hi),share_shots_head_trimmed=round(sum(1 for x in hi if x>0.05)/len(hi),3),
        tail_left=summ([max(0,s['mat_dur']-s['src_in']-s['dur']*s['speed']) for D in Ds for s in D['shots'] if s['mat_dur']]),
        overlays_per_video=summ([D['overlays'] for D in Ds]),color_adjust_share=round(sum(1 for D in Ds if D['effects'])/len(Ds),3))
    T=[(D,t) for D in Ds for t in D['texts']]
    L=[lines_est(t,D['W']) for D,t in T]
    fonts={};
    for D,t in T: fonts[t['font']]=fonts.get(t['font'],0)+1
    persist=[t for D,t in T if t['dur']>=D['dur']-0.3]
    nem=[len(EMO.sub('',t['text'])) for D,t in T]
    emo=[len(re.findall("[\U0001F000-\U0001FAFF\u2600-\u27BF]",t['text'])) for D,t in T]
    S['text']=dict(n_cards=len(T),fonts=fonts,size=summ([t['size'] for D,t in T]),scale=summ([t['scale'] for D,t in T]),
        em_frac_of_width=summ([l[2] for l in L]),stroke_width=summ([t['stroke'] for D,t in T]),
        colors=sorted({f"{t['color']}/{t['stroke_color']}" for D,t in T}),line_max_width=summ([t['lmw'] for D,t in T]),
        y_center_frac_from_top=summ([t['y'] for D,t in T],[w(D) for D,t in T]),
        lines=summ([l[0] for l in L]),explicit_lines=summ([t['text'].count('\n')+1 for D,t in T]),share_explicit_le2=round(sum(1 for D,t in T if t['text'].count('\n')<2)/len(T),3),share_le2_lines=round(sum(1 for l in L if l[0]<=2)/len(L),3),
        chars_per_line=summ([l[1] for l in L]),chars_total=summ(nem),
        card_on_at=summ([t['t0'] for D,t in T if t['t0']<0.5]) and summ([t['t0'] for D,t in T]),
        first_card_starts_at_0=round(sum(1 for D in Ds if D['texts'] and D['texts'][0]['t0']<0.05)/max(1,sum(1 for D in Ds if D['texts'])),3),
        card_dur=summ([t['dur'] for D,t in T if t not in persist]),share_persistent_full_video=round(len(persist)/len(T),3),
        cards_per_video=summ([len(D['texts']) for D in Ds]),templates_used=sum(t['tmpl'] for D,t in T),
        emoji_per_card=summ(emo),emoji_at_end_share=round(sum(1 for D,t in T if EMO.search(t['text'].strip()[-2:] or ' '))/len(T),3),
        card_vs_cut_sync=round(sum(1 for D,t in T if t['t0']>0.05 and any(abs(s['t0']-t['t0'])<0.1 for s in D['shots']))/max(1,sum(1 for D,t in T if t['t0']>0.05)),3))
    songs=[(D,a) for D in Ds for a in D['audio'] if a['type']!='video_original_sound' and a['dur']>3]
    cv=[]
    for D in Ds:
        tot=sum(s['dur'] for s in D['shots']); cv.append(sum(s['vol']*s['dur'] for s in D['shots'])/tot if tot else None)
    db=lambda v:round(20*math.log10(v),2) if v and v>0 else None
    rel=[]
    for D in Ds:
        mus=[a['vol'] for a in D['audio'] if a['type']!='video_original_sound' and a['dur']>3]
        audible=[s['vol'] for s in D['shots'] if s['vol']>0.01]
        if mus and audible: rel.append(db(st.median(audible))-db(mus[0]) if mus[0]>0 else None)
    S['audio']=dict(has_song_share=round(sum(1 for D in Ds if any(a['type']!='video_original_sound' and a['dur']>3 for a in D['audio']))/len(Ds),3),
        song_starts_at=summ([a['t0'] for D,a in songs]),song_in_point=summ([a['src_in'] for D,a in songs]),
        song_volume=summ([a['vol'] for D,a in songs]),song_volume_db=summ([db(a['vol']) for D,a in songs]),
        clip_volume=summ(cv),share_shots_muted=round(sum(1 for D in Ds for s in D['shots'] if s['vol']<0.01)/len(sv),3),
        audible_clip_vs_song_db=summ(rel),boosted_clip_share=round(sum(1 for D in Ds for s in D['shots'] if s['vol']>1.01)/len(sv),3),
        boosted_by_role={r:sum(1 for D in Ds for s in D['shots'] if s['vol']>1.01 and s['role']==r) for r in ('hook','before','reveal','after','body')},
        boosted_clip_volume=summ([s['vol'] for D in Ds for s in D['shots'] if s['vol']>1.01]),
        fade_in=summ([a['fin'] for D,a in songs]),fade_out=summ([a['fout'] for D,a in songs]),
        share_fade_out=round(sum(1 for D,a in songs if a['fout']>0)/max(1,len(songs)),3),
        ducking_keyframes=sum(1 for D in Ds for a in D['audio'] for k in a['kf'] if 'olume' in str(k))+sum(1 for D in Ds for s in D['shots'] for k in s['kf'] if 'olume' in str(k)),
        song_ends_with_video=round(sum(1 for D,a in songs if abs(a['t0']+a['dur']-D['dur'])<0.2)/max(1,len(songs)),3),
        song_names=sorted({re.sub(r'\.(mp3|m4a|wav|mp4)$','',a['name'])[:60] for D,a in songs}))
    S['endings']=dict(last_shot_role=dict((r,sum(1 for D in Ds if D['shots'][-1]['role']==r)) for r in ('after','reveal','body','before')),
        last_card_covers_end=round(sum(1 for D in Ds if D['texts'] and D['texts'][-1]['t0']+D['texts'][-1]['dur']>=D['dur']-0.2)/max(1,sum(1 for D in Ds if D['texts'])),3),
        end_card_text=[t['text'] for D in sorted(Ds,key=lambda D:-(D['views'] or 0))[:12] for t in D['texts'][-1:]])
    TOPD=sorted([D for D in Ds if D['views']],key=lambda D:-D['views'])[:12]
    S['top_drafts']=[dict(draft=D['draft'],views=D['views'],dur=round(D['dur'],2),shots=len(D['shots']),opener=round(D['shots'][0]['dur'],2),
        speeds=[s['speed'] for s in D['shots'] if s['speed']!=1],cards=[t['text'] for t in D['texts']],
        song=[(a['name'][:40],round(a['src_in'],1),a['vol']) for a in D['audio'] if a['type']!='video_original_sound'][:1]) for D in TOPD]
    json.dump(S,open(f"{HERE}/stats.json","w"),indent=1,ensure_ascii=False)
    with open(f"{HERE}/shots.csv","w") as f:
        wr=csv.writer(f); wr.writerow(['draft','views','i','role','t0','dur','speed','vol','src_in','mat_dur'])
        for D in Ds:
            for i,s in enumerate(D['shots']): wr.writerow([D['draft'],D['views'],i,s['role'],round(s['t0'],3),round(s['dur'],3),s['speed'],round(s['vol'],3),round(s['src_in'],3),round(s['mat_dur'],3)])
    with open(f"{HERE}/cards.csv","w") as f:
        wr=csv.writer(f); wr.writerow(['draft','views','t0','dur','text','size','scale','y','lines_est','cpl_est','font'])
        for D in Ds:
            for t in D['texts']:
                l=lines_est(t,D['W']); wr.writerow([D['draft'],D['views'],round(t['t0'],2),round(t['dur'],2),t['text'].replace('\n',' / '),t['size'],round(t['scale'],3),round(t['y'],3),l[0],l[1],t['font']])
    print(json.dumps({k:S[k] for k in ('n_drafts','n_joined','n_top')}))
if __name__=="__main__": main()

def build_style(S):
    """Engine-facing defaults (style.json). Values = top-performer-weighted medians; ranges = weighted p10-p90."""
    T=S['timing'];X=S['text'];A=S['audio'];P=S['speed']
    r=lambda d:[d['p10'],d['p90']]
    return {"version":"2026-10-19","source":"Omar CapCut drafts (%d parsed, %d view-joined, %d >=50K); see OMAR_STYLE.md"%(S['n_drafts'],S['n_joined'],S['n_top']),
     "timing":{"total_s":T['total_duration_top']['wmedian'],"total_range_s":r(T['total_duration_top']),
        "shots":T['shots_per_video']['wmedian'],"shots_range":r(T['shots_per_video']),
        "opener_s":T['opener_top']['wmedian'],"opener_range_s":[1.5,T['opener']['p90']],"opener_max_s":4.1,
        "shot_s":T['shot_len']['wmedian'],"shot_range_s":r(T['shot_len']),
        "role_s":{k:{"median":v['wmedian'],"range":r(v)} for k,v in T['shot_len_by_role'].items()},
        "ending_s":T['ending_shot']['wmedian'],"ending_range_s":r(T['ending_shot'])},
     "speed":{"hook_fit_values":[1.1,1.15,1.2,1.3,1.5],"preferred_hook_speed":1.2,"max_hook_speed":1.5,"max_story_speed":1.5,
        "share_shots_sped":P['share_shots_sped'],"share_hooks_sped":P['by_role']['hook']['share'],
        "never_slow_story":True,"no_ramps":True,"rule":"if a hook's spoken line doesn't fit, speed the whole hook up (1.1-1.5, prefer 1.2) - never cut words"},
     "cuts":{"transitions":"none (hard cuts only, 0 of %d drafts use transitions)"%S['n_drafts'],"head_trim_s":S['cuts']['head_trim']['wmedian'],
        "share_head_trimmed":S['cuts']['share_shots_head_trimmed'],"zoom_overlays":"none"},
     "text":{"font":"CapCut system en.ttf (we render TikTok Sans/Montserrat matched via textcards.CAL)","preset":"white fill #FFFFFF, black stroke 0.09, no template/animation/background",
        "size":15,"stroke":0.09,"line_max_width":0.82,"scale":X['scale']['wmedian'],"scale_range":r(X['scale']),
        "em_frac_of_width":X['em_frac_of_width']['wmedian'],"y_center_frac_from_top":X['y_center_frac_from_top']['wmedian'],
        "y_range":r(X['y_center_frac_from_top']),"max_lines":2,"share_explicit_le2":X['share_explicit_le2'],
        "chars_per_line_max":24,"chars_per_line_median":X['chars_per_line']['median'],"chars_total_max":44,
        "first_card_at_s":0.0,"cards_change_on_cuts":X['card_vs_cut_sync'],"last_card_holds_to_end":True,
        "emoji":{"per_card":1,"max_per_card":2,"position":"end of card","share_at_end":X['emoji_at_end_share']}},
     "audio":{"song_from_frame0":True,"song_gain_db":0.0,"clip_gain_cap_db":20.0,
        "dialogue_over_music_lu":8.0,"dialogue_over_music_lu_range":[4.0,10.6],
        "dialogue_clip_gain_db_vs_song":14.0,"non_dialogue_clip":"keep at 1.0 (0 dB) or mute (13% of shots muted)",
        "ducking":"none (0 volume keyframes) - he lowers the whole song and boosts the dialogue clip instead",
        "fade_in_s":0.0,"fade_out_s":0.0,"song_ends_with_video":A['song_ends_with_video']},
     "endings":{"last_card_covers_end":S['endings']['last_card_covers_end'],"end_on":"after/reveal shot, no end card, no on-screen CTA/link","ending_s":T['ending_shot']['wmedian']},
     "qa_weights":{"total":1,"opener":2,"shot_len":1,"hook_speed":1,"text_lines":3,"text_size":1,"text_y":1,"emoji":1,"song_t0":3,"dialogue":3,"transitions":1,"ending":1}}
if __name__=="__main__":
    S=json.load(open(f"{HERE}/stats.json")); json.dump(build_style(S),open(f"{HERE}/style.json","w"),indent=1,ensure_ascii=False); print("style.json written")
