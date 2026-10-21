import subprocess, tempfile, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from hookforge.repeat_detect import find_repeats

def _mk(path, loop):
    src = "testsrc2=size=96x128:rate=30:duration=2"
    if loop:  # 2s of motion then the same 1s replayed = looped padding
        fc = f"{src},split[a][b];[b]trim=0.5:1.5,setpts=PTS-STARTPTS[c];[a][c]concat=n=2:v=1"
    else:
        fc = "testsrc2=size=96x128:rate=30:duration=3"
    subprocess.run(["ffmpeg","-v","error","-y","-f","lavfi","-i",fc,"-pix_fmt","yuv420p",path],check=True)

def test_loop_detected_and_clean_passes():
    d = tempfile.mkdtemp()
    a, b = os.path.join(d,"loop.mp4"), os.path.join(d,"clean.mp4")
    _mk(a, True); _mk(b, False)
    hits = find_repeats(a)
    assert hits and abs(hits[0]["dup_t"]-2.0) < 0.1 and abs(hits[0]["src_t"]-0.5) < 0.1
    assert find_repeats(b) == []
