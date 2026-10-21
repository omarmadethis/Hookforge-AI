import os, sys, subprocess, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from hookforge import pacing as P

def test_hold_gate():
    tl = dict(reveal_t=4.0, shots=[dict(gen="G1", t0=0, t1=2.0), dict(gen="G2", t0=2.0, t1=3.3),
             dict(gen="G5", t0=3.3, t1=7.0), dict(gen="G3", t0=7.0, t1=10.0), dict(gen="G4", t0=10.0, t1=11.5)])
    v = P.hold_violations(tl)
    assert len(v) == 1 and v[0].startswith("G3 (after)")          # 3.0s after > p90 1.82; reveal 3.7s allowed
    tl["shots"][3]["proven"] = True; assert P.hold_violations(tl) == []

def test_near_duplicate_and_variants():
    d = tempfile.mkdtemp(); a, b, c = (os.path.join(d, x) for x in ("a.mp4", "b.mp4", "c.mp4"))
    # A: two "different clips" with the same framing back to back (static same image) -> near-duplicate cut
    subprocess.run(["ffmpeg","-v","error","-y","-f","lavfi","-i","testsrc2=size=96x128:rate=30:duration=2","-vf","trim=0:2,setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration=0","-pix_fmt","yuv420p",a],check=True)
    tl = dict(shots=[dict(gen="X", t0=0, t1=1.0), dict(gen="Y", t0=1.0, t1=2.0)])
    assert P.near_duplicate_cuts(tl, a)                      # continuous motion across 1.0 looks the same
    subprocess.run(["ffmpeg","-v","error","-y","-f","lavfi","-i","testsrc2=size=96x128:rate=30:duration=1","-f","lavfi","-i","mandelbrot=size=96x128:rate=30","-filter_complex","[1]trim=0:1,setpts=PTS-STARTPTS[m];[0][m]concat=n=2:v=1","-pix_fmt","yuv420p",b],check=True)
    assert P.near_duplicate_cuts(tl, b) == []
    subprocess.run(["ffmpeg","-v","error","-y","-i",a,"-c","copy",c],check=True)
    assert P.variants_identical([a, c])[0] and not P.variants_identical([a, b])[0]

if __name__ == "__main__": test_hold_gate(); test_near_duplicate_and_variants(); print("PASS")
