"""Rebuild shots_by_reel.csv from shots.csv (ours only). grp: win>=50K, flop<10K, else mid. hit = views>=50K.
covered = hook motion is covered_reveal. chaos_then = hook motion in chaos/fail/cozy_dim/competitor_fail."""
import pandas as pd
S=pd.read_csv('/workspace/hookforge/style/shots.csv')
S=S[S.side=='ours']
rows=[]
for k,d in S.groupby('reel_key'):
    h=d.sort_values('shot').iloc[0]; v=int(h.views)
    rows.append(dict(reel_key=k,views=v,grp='win' if v>=50000 else ('flop' if v<10000 else 'mid'),fmt=h.format_id,world=h.world,n=len(d),
      pov=(d.angle=='pov').mean(),high=(d.angle=='high').mean(),face=d.face_visible.mean(),cu=d.distance.isin(['ECU','CU','MCU']).mean(),
      handheld=(d.camera=='handheld').mean(),ps=d.product_share.mean(),person=(d.subject=='person').mean(),
      hook_motion=h.motion,hook_subject=h.subject,hook_ps=h.product_share,hook_face=h.face_visible,hook_angle=h.angle,hook_cam=h.camera,
      covered=h.motion=='covered_reveal',chaos_then=h.motion in ('chaos','fail','cozy_dim','competitor_fail'),hit=v>=50000))
out=pd.DataFrame(rows).sort_values('reel_key')
if __name__=='__main__':
    out.to_csv('/workspace/hookforge/style/shots_by_reel.csv',index=False); print(len(out))
