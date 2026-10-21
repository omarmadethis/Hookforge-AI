"""D44 check: a source WITH C2PA/AI-provenance goes through autoedit.clean_export and comes out with none;
qa.final_checks BLOCKs the raw source and passes the clean file on provenance. Run: cd engine && python3 -m tests.test_c2pa_strip"""
import os, sys, json, subprocess
from hookforge import autoedit, qa
from hookforge.config import REPO
sys.path.insert(0, os.path.join(REPO, "tools", "preflight")); import preflight

import struct
def make_fixture(dst):
    """Synthetic 3 s clip + a C2PA uuid box (JUMBF 'c2pa' manifest stub) + XMP with trainedAlgorithmicMedia, appended
    as top-level boxes like real Higgsfield/Sora/Adobe exports carry them."""
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "testsrc2=s=720x1280:r=30:d=3", "-f", "lavfi", "-i",
                    "sine=f=440:d=3", "-c:v", "libx264", "-c:a", "aac", "-shortest", dst], check=True)
    jumd = b"jumd" + b"c2pa\x00\x11\x00\x10\x80\x00\x00\xaa\x00\x38\x9b\x71" + b"\x03c2pa\x00"
    jumbf = struct.pack(">I", 8 + 8 + len(jumd) + 32) + b"jumb" + struct.pack(">I", 8 + len(jumd)) + jumd + b"c2pa.claim c2pa.signature pad"[:32]
    uuid_box = struct.pack(">I", 8 + 16 + len(jumbf)) + b"uuid" + preflight.C2PA_UUID + jumbf
    xmp = b'<x:xmpmeta><rdf:Description Iptc4xmpExt:DigitalSourceType="http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia"/></x:xmpmeta>'
    xmp_box = struct.pack(">I", 8 + 16 + len(xmp)) + b"uuid" + bytes.fromhex("be7acfcb97a942e89c71999491e3afac") + xmp
    with open(dst, "ab") as f: f.write(uuid_box + xmp_box)
    return dst
def main():
    tmp = "/tmp/c2pa_test"; os.makedirs(tmp, exist_ok=True)
    src = make_fixture(os.path.join(tmp, "src.mp4"))
    real = os.path.join(REPO, "data", "features", "proxies", "ref_tiktok_7693569018929630478.mp4")
    if os.path.exists(real): assert not preflight.provenance(real)["c2pa"], "detector false positive on the random-'c2pa' TikTok proxy"
    before = preflight.provenance(src)
    out = autoedit.clean_export(src, os.path.join(tmp, "clean.mp4"))      # asserts internally
    fc_src = qa.final_checks(src, os.path.join(tmp, "pf_src"), final=True)
    fc_out = qa.final_checks(out["path"], os.path.join(tmp, "pf_out"), final=True)
    prov_block = lambda fc: [p for p in fc["problems"] if "provenance" in p.lower() or "c2pa" in p.lower()]
    res = dict(before=before, after=out["provenance"], src_block=prov_block(fc_src), clean_block=prov_block(fc_out))
    assert any(before.values()), "fixture has no provenance"
    assert not any(out["provenance"].values()) and res["src_block"] and not res["clean_block"], res
    print(json.dumps(dict(res, verdict="PASS"), indent=1)); return res
if __name__ == "__main__": main()
