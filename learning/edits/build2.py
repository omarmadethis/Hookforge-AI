"""D182-D187 build: one segment per shot (hard cuts), cards at scale 1.0 starting on shot first frames,
song from frame 0, separate clip-audio track (allows the 3-2-1 count to run continuously under a split-second flash),
voice gain so the count sits ~+8 LU over the song (D187)."""
import subprocess, sys, json, os
sys.path.insert(0,'/workspace/hookforge/engine')
from hookforge import textcards, autoedit
R='/workspace/hookforge/out/live/trumpglow_AB/'; C=R+'clips/'; O=R+'edit/'
SONGS=json.load(open('/workspace/hookforge/music/songs.json'))
def lufs(args):
    out=subprocess.run(['ffmpeg','-nostats',*args,'-af','ebur128','-f','null','-'],capture_output=True,text=True).stderr
    import re; return float(re.findall(r'I:\s+(-?[\d.]+) LUFS',out)[-1])
def build(name, P, out):
    shots, cards, aud = P['shots'], P['cards'], P['audio']
    ins=[]; f=[]; vparts=''; t=0; tl=[]
    for i,s in enumerate(shots):
        sp=s.get('speed',1); a,b=s['src']; d=(b-a)/sp
        ins+=['-i',C+s['gen']+'.mp4']; tl.append(dict(gen=s['gen'],t0=round(t,3),t1=round(t+d,3),role=s.get('role')))
        f.append(f"[{i}:v]trim={a}:{b},setpts=(PTS-STARTPTS)/{sp},scale=1080:1920:flags=lanczos,fps=30,format=yuv420p[v{i}]"); vparts+=f"[v{i}]"; t+=d
    n=len(shots); tot=round(t,3)
    f.append(vparts+f"concat=n={n}:v=1:a=0[cv]"); last='cv'; k0=n
    for k,c in enumerate(cards):
        png=O+f'{name}_card{k}.png'; textcards.render_card(c['text'],1080,1920,scale=1.0).save(png)
        ins+=['-loop','1','-t',str(tot),'-i',png]
        f.append(f"[{last}][{k0+k}:v]overlay=0:0:enable='between(t,{c['t0']},{c['t1']}-0.001)'[o{k}]"); last=f'o{k}'
    f.append(f"[{last}]scale=2160:3840:flags=lanczos,format=yuv420p[v]")
    # clip-audio track
    j0=k0+len(cards); amix=[]
    song=SONGS[P['song']]; s_l=lufs(['-ss',str(song['in_point_s']),'-t',str(tot),'-i',song['file']])
    for m,x in enumerate(aud):
        ins+=['-i',C+x['gen']+'.mp4']; a,b=x['src']; sp=x.get('speed',1)
        g=x.get('gain_db',-6.0)
        if x.get('vo_over_song_lu') is not None:
            v_l=lufs(['-ss',str(a),'-t',str(b-a),'-i',C+x['gen']+'.mp4'])
            g=(s_l+P['song_gain_db'])+x['vo_over_song_lu']-v_l
        at=f",atempo={sp}" if sp!=1 else ""
        f.append(f"[{j0+m}:a]atrim={a}:{b},asetpts=PTS-STARTPTS{at},aresample=48000,aformat=channel_layouts=stereo,volume={g:.2f}dB,adelay={int(x['at']*1000)}|{int(x['at']*1000)}[c{m}]"); amix.append(f'[c{m}]')
    si=j0+len(aud); ins+=['-ss',str(song['in_point_s']),'-i',song['file']]
    f.append(f"[{si}:a]atrim=0:{tot},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,volume={P['song_gain_db']}dB,afade=t=out:st={tot-0.3}:d=0.3[s]")
    f.append(''.join(amix)+f"[s]amix=inputs={len(amix)+1}:duration=longest:normalize=0,atrim=0:{tot}[a]")
    subprocess.run(['ffmpeg','-y','-v','error',*ins,'-filter_complex',';'.join(f),'-map','[v]','-map','[a]','-t',str(tot),'-c:v','libx264','-crf','18','-preset','medium','-c:a','aac','-b:a','192k',O+name+'_master.mp4'],check=True)
    autoedit.clean_export(O+name+'_master.mp4',O+name+'_clean.mp4'); autoedit.relevel_audio(O+name+'_clean.mp4',out)
    os.remove(O+name+'_master.mp4'); os.remove(O+name+'_clean.mp4')
    return dict(name=name,dur=tot,timeline=tl,out=out,song_lufs=s_l)
if __name__=='__main__':
    P=json.load(open(sys.argv[1]))[sys.argv[2]]; r=build(sys.argv[2],P,sys.argv[3]); json.dump(r,open(O+sys.argv[2]+'_timeline.json','w'),indent=1); print(json.dumps(r))
