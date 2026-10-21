import subprocess, tempfile, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from hookforge.splice_detect import find_same_take_splices

def test_same_take_splice_blocked_other_passes():
    d = tempfile.mkdtemp(); v = os.path.join(d, "v.mp4")
    # take X: 0-1 and 1.3-2.3 spliced back to back
    fc = "testsrc2=size=96x128:rate=30:duration=3,split[a][b];[a]trim=0:1,setpts=PTS-STARTPTS[x];[b]trim=1.3:2.3,setpts=PTS-STARTPTS[y];[x][y]concat=n=2:v=1"
    subprocess.run(["ffmpeg","-v","error","-y","-f","lavfi","-i",fc,"-pix_fmt","yuv420p",v],check=True)
    bad = [dict(gen="X",t0=0,t1=1,trim=[0,1]), dict(gen="X",t0=1,t1=2,trim=[1.3,2.3])]
    hits = find_same_take_splices(bad, v)
    assert len(hits) == 1 and hits[0]["visual_confirmed"] and hits[0]["boundary_t"] == 1
    ok = [dict(gen="X",t0=0,t1=1), dict(gen="Y",t0=1,t1=2), dict(gen="X",t0=2,t1=3)]
    assert find_same_take_splices(ok, v) == []
