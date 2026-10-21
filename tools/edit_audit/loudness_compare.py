import sys, subprocess, re, json, glob, os, pandas as pd
def lufs(p):
    o = subprocess.run(["ffmpeg","-hide_banner","-nostats","-i",p,"-af","ebur128=peak=true","-f","null","-"],capture_output=True,text=True).stderr
    I = re.findall(r"I:\s+(-?[\d.]+) LUFS", o); TP = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", o); LRA=re.findall(r"LRA:\s+([\d.]+) LU",o)
    return (float(I[-1]) if I else None, float(TP[-1]) if TP else None, float(LRA[-1]) if LRA else None)
ours = [f for f in glob.glob("out/deliver/*.mp4") if re.search(r"v7|v4|v3\.mp4",f)]
c = pd.read_csv("private/corpus/corpus.csv", low_memory=False); c["views"]=pd.to_numeric(c.views,errors="coerce")
own = c[(c.source=="own")&c.file.notna()&(c.views>=50000)].sort_values("views",ascending=False)
own = [f for f in own.file if os.path.exists(f)][:15]
res = {"ours":{os.path.basename(f):lufs(f) for f in ours}, "omar":{os.path.basename(f):lufs(f) for f in own}}
json.dump(res, open("tools/edit_audit/loudness_2026-10-20.json","w"), indent=1); print(json.dumps(res,indent=1))
