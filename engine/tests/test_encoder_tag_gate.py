import subprocess, tempfile, os, sys, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from hookforge import autoedit

def _tags(p):
    ex = subprocess.run(["exiftool","-a","-G1",p],capture_output=True,text=True).stdout
    return [l for l in ex.splitlines() if re.search(r"^\[[^\]]+\]\s+Encoder\b|Lavf|Lavc|libx26", l)]

def test_plain_ffmpeg_has_lavf_and_clean_remux_strips_it():
    d = tempfile.mkdtemp(); a, b = os.path.join(d,"a.mp4"), os.path.join(d,"b.mp4")
    subprocess.run(["ffmpeg","-v","error","-y","-f","lavfi","-i","testsrc2=size=96x128:duration=1","-f","lavfi","-i","sine=duration=1",
                    "-c:v","libx265","-x265-params","log-level=error","-c:a","aac","-shortest",a],check=True)
    assert _tags(a)            # what a naive re-level produces -> gate would BLOCK
    autoedit.clean_remux(a, b)
    assert _tags(b) == []
