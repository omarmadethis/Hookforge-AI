import os, sys, subprocess, tempfile, zlib, struct
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from hookforge import deliver as D

def _mp4(p, extra=()):
    subprocess.run(["ffmpeg","-v","error","-y","-f","lavfi","-i","testsrc2=size=96x128:duration=1","-f","lavfi","-i","sine=duration=1",
                    "-c:v","libx265","-x265-params","log-level=error","-c:a","aac","-shortest",*extra,p],check=True)

def _png(p, text=False):
    def chunk(t, d): return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    raw = b"".join(b"\x00" + b"\x80\x80\x80" * 4 for _ in range(4))
    data = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 4, 4, 8, 2, 0, 0, 0))
    if text: data += chunk(b"tEXt", b"Software\x00Higgsfield")
    data += chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")
    open(p, "wb").write(data)

def test_refusals_and_clean_pass():
    d = tempfile.mkdtemp(); D.OUT_DIR = os.path.join(d, "out"); D.MANIFEST = os.path.join(D.OUT_DIR, "manifest.json")
    lavf = os.path.join(d, "lavf.mp4"); _mp4(lavf)
    assert any("Lavf" in x or "Encoder" in x for x in D.scan(lavf))
    c2 = os.path.join(d, "c2pa.mp4"); _mp4(c2); open(c2, "ab").write(b"\x00\x00\x00\x18uuidc2pa-manifest-jumbf!")
    assert any("c2pa" in x or "uuid" in x for x in D.scan(c2))
    png = os.path.join(d, "t.png"); _png(png, text=True)
    assert any("tEXt" in x for x in D.scan(png))
    for p in (lavf, c2, png):            # no override: stage without sanitize must refuse
        try: D.stage(p, auto_sanitize=False); assert False
        except D.Refused: pass
    ok = os.path.join(d, "ok.png"); _png(ok); assert D.scan(ok) == []
    st = D.stage(ok); assert D.verify_staged(st)
    st2 = D.stage(lavf, "lavf_clean.mp4")      # sanitizer -> clean copy must then pass
    assert D.scan(st2) == [] and D.verify_staged(st2)
    open(st2, "ab").write(b"Lavf")             # tampering after staging is refused
    try: D.verify_staged(st2); assert False
    except D.Refused: pass

if __name__ == "__main__": test_refusals_and_clean_pass(); print("PASS")
