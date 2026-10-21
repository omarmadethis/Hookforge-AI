import numpy as np,subprocess,sys
def load(p):
    b=subprocess.run(['ffmpeg','-v','error','-i',p,'-ac','1','-ar','8000','-f','s16le','-'],capture_output=True).stdout
    return np.frombuffer(b,np.int16).astype(float)
def feat(x,hop=80,n=1024):
    fr=np.lib.stride_tricks.sliding_window_view(x,n)[::hop]*np.hanning(n)
    S=np.abs(np.fft.rfft(fr))[:, :400]+1e-6
    S=np.log(S.reshape(len(S),40,10).sum(2)); S=S-S.mean(1,keepdims=True); return S/(np.linalg.norm(S,axis=1,keepdims=True)+1e-9)
def find(query,target,qs=0,W=300):
    Q=feat(load(query))[qs:qs+W]; T=feat(load(target))
    sc=np.array([np.sum(Q*T[o:o+W])/W for o in range(0,len(T)-W)]); o=int(sc.argmax()); return o/100, sc.max(), np.median(sc)
if __name__=='__main__':
    q,t=sys.argv[1],sys.argv[2]
    for qs in (0,500,1500):
        print(q,'@',qs/100,'->',t,find(q,t,qs))
