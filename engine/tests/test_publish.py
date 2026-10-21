import os, sys, subprocess, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from hookforge import publish

def raises(fn, *a, **k):
    try: fn(*a, **k)
    except publish.NotAllowed: return True
    raise AssertionError("expected NotAllowed")

def main():
    tmp = tempfile.mkdtemp(); publish.QUEUE_DIR = os.path.join(tmp, "q")
    import json; from hookforge import routing
    c = json.load(open(routing.CFG_F)); c["pages"]["test_ig"] = dict(name="T", service="instagram", account="buffer1", channel="a"*24, windows="_default", family="t")
    routing.CFG_F = os.path.join(tmp, "routing.json"); json.dump(c, open(routing.CFG_F, "w"))
    v = os.path.join(tmp, "pubtest_clip.mp4")
    subprocess.run(["ffmpeg","-y","-loglevel","error","-f","lavfi","-i","color=c=red:s=64x64:d=1","-c:v","libx264",
                    "-x264-params","info=0","-pix_fmt","yuv420p","-map_metadata","-1","-fflags","+bitexact","-flags:v","+bitexact",v],check=True)
    it = publish.prepare(v, "His last day on my truck.. ❤️🇺🇸", "a"*24, "instagram")
    assert it["status"] == publish.STATUS_WAIT and it["payload"]["saveToDraft"] is True and it["payload"]["mode"] == "addToQueue"
    assert it["payload"]["metadata"]["instagram"]["shouldShareToFeed"]
    raises(publish.ready_payload, it["id"])          # not approved
    raises(publish.approve, it["id"], "agent")       # only Omar
    publish.approve(it["id"], "Omar")
    raises(publish.ready_payload, it["id"])          # no public URL yet
    raises(publish.prepare, v, "  ", "a"*24)         # empty caption
    raises(publish.prepare, v, "His last day on my truck.. ❤️🇺🇸", "a"*24, "instagram")   # duplicate file+channel
    raises(publish.set_video_url, it["id"], "https://drive.google.com/file/d/x/view")       # share link refused
    it2 = publish.set_video_url(it["id"], "https://cdn.example.com/v.mp4")
    assert it2["status"] == publish.STATUS_WAIT                                               # URL change voids approval
    raises(publish.ready_payload, it["id"])
    publish.approve(it["id"], "Omar", approval_quote="ok post it")
    p = publish.ready_payload(it["id"]); assert p["saveToDraft"] is True and p["mode"] == "addToQueue"
    p["mode"] = "shareNow"; assert publish.ready_payload(it["id"])["mode"] == "addToQueue"   # returned copy, item untouched
    j = publish._load(it["id"]); j["payload"]["saveToDraft"] = False; publish._save(j)
    raises(publish.ready_payload, it["id"])                                                   # tampered payload -> re-approve
    j["payload"]["saveToDraft"] = True; publish._save(j)
    publish.mark_drafted(it["id"], "buf123"); assert publish._load(it["id"])["status"] == "BUFFER_DRAFT_CREATED"
    raises(publish.mark_drafted, it["id"], "buf124")
    src = open(publish.__file__).read(); assert "urllib" not in src and "requests" not in src   # no network code
    os.remove(it["staged"])
    print("test_publish OK")

if __name__ == "__main__": main()
