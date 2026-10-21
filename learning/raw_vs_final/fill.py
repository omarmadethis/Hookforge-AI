import re,pandas as pd,collections,os
t=open('/workspace/agent-tools/b1780eb6-f4f0-4438-998f-785192d0e3cf.txt').read();mm={}
for b in t.split('- index:')[1:]:
    u=re.search(r'job_id: (\S+)',b);m=re.search(r'model: (\S+)',b)
    if u and m: mm[u.group(1)]=m.group(1)
X=pd.read_csv('pairs.csv')
X['model']=X.model.fillna(X.gen_uuid.map(mm))
X.loc[X.prompt_src.isna()&X.gen_uuid.isin(mm),'prompt_src']='higgsfield_new_account(model only)'
C=pd.read_csv('/workspace/team/mac/out/clip_prompts.csv');P=pd.read_csv('/workspace/team/mac/out/project_reel_matches.csv');cm={}
for r in P.itertuples(): cm[os.path.basename(r.mac_path)]=(r.model,r.prompt)
for r in C.itertuples(): cm.setdefault(os.path.basename(str(r.clip)).strip(),(r.model,r.prompt))
f=X.model.isna()&X.raw_file.isin(cm)
X.loc[f,'model']=X.loc[f,'raw_file'].map(lambda k:cm[k][0]);X.loc[f,'prompt']=X.loc[f,'raw_file'].map(lambda k:str(cm[k][1])[:1500]);X.loc[f,'prompt_src']='mac_project_clip'
X.to_csv('pairs.csv',index=False)
