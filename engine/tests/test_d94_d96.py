import os, sys, json, tempfile, subprocess, datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from hookforge import routing, publish, fb_caption, snapshot_scheduler as SS, results_feed as RF

def _clip(tmp, name, color):
    v = os.path.join(tmp, name)
    subprocess.run(["ffmpeg","-y","-loglevel","error","-f","lavfi","-i",f"color=c={color}:s=64x64:d=1","-c:v","libx264","-x264-params","info=0",
                    "-pix_fmt","yuv420p","-map_metadata","-1","-fflags","+bitexact","-flags:v","+bitexact",v],check=True); return v

def _setup():
    tmp = tempfile.mkdtemp(); publish.QUEUE_DIR = os.path.join(tmp, "q"); fb_caption.SWAP_DIR = os.path.join(tmp, "swaps"); return tmp

def raises(fn, *a, exc=publish.NotAllowed, **k):
    try: fn(*a, **k)
    except exc: return True
    raise AssertionError(f"expected {exc}")

def test_routing():
    tmp = _setup()
    r = routing.route("trumpglow"); assert [p["page"] for p in r["pages"]] == ["trumpglow_fb", "patriotsglow_fb"]
    assert r["pages"][0]["namespace"] == "user-Buffer--buffer2" and r["pages"][1]["org"] == "6ad7108f7a26bda7eb714973"
    raises(routing.route, "grinch_robe", exc=Exception)   # D131: robe family retired -> no routing
    raises(routing.assert_routable, "6ad7c950778b240e2f6f0cfd", exc=routing.RouteRefused)
    raises(routing.assert_routable, "6ad7c63f778b240e2f6ed4e6", live_count=10, exc=routing.RouteRefused)   # free plan full
    assert routing.capacity("buffer3") == 0
    s = routing.slots(); assert s["facebook"]["open"] == 3 and s["instagram"]["open"] == 0
    v = _clip(tmp, "a.mp4", "red")
    raises(publish.prepare, v, "hi", "6ad7c950778b240e2f6f0cfd", "instagram")          # publish refuses locked channel
    raises(publish.prepare, v, "hi", "6ad7d610778b240e2f6f8b6c", "instagram")          # FB channel used as IG
    t = routing.next_window("trumpglow_fb", datetime.datetime(2026, 11, 2, 12, 0, tzinfo=routing.PT), queue=[])
    assert t.hour == 18 and t.day == 2

def test_prepare_fb_all_and_swap():
    tmp = _setup()
    a, b = _clip(tmp, "a.mp4", "red"), _clip(tmp, "b.mp4", "blue")
    raises(publish.prepare_fb_all, "trumpglow", {"trumpglow_fb": a, "patriotsglow_fb": a})            # same file on 2 pages
    raises(publish.prepare_fb_all, "trumpglow", {"trumpglow_fb": a})                                   # missing variant
    raises(publish.prepare_fb_all, "trumpglow", {"trumpglow_fb": a, "patriotsglow_fb": b, "merryjammies_ig": b})
    from hookforge import caption_variants as CV; real_out = CV.OUT; CV.OUT = os.path.join(tmp, "none.json")
    raises(publish.prepare_fb_all, "trumpglow", {"trumpglow_fb": a, "patriotsglow_fb": b})            # only 1 proven TrumpGlow caption
    CV.OUT = os.path.join(tmp, "pv.json"); CV.build(["trumpglow"])                                    # D101 variants make it work
    o2 = publish.prepare_fb_all("trumpglow", {"trumpglow_fb": a, "patriotsglow_fb": b})
    assert o2["items"][1]["poc"].startswith("plan:own corpus") and o2["items"][0]["fb_caption"]["caption"] != o2["items"][1]["fb_caption"]["caption"]
    for i in o2["items"]: os.remove(os.path.join(publish.QUEUE_DIR, i["id"] + ".json"))
    CV.OUT = os.path.join(tmp, "none.json")
    assert not publish.pending()                                                                       # all-or-nothing
    out = publish.prepare_fb_all("trumpglow", {"trumpglow_fb": a, "patriotsglow_fb": b},
                                 plans_by_page={"patriotsglow_fb": {"caption_override": "Your neighbors will know who you vote for 🇺🇸"}})
    CV.OUT = real_out; its = out["items"]; assert len(its) == 2 and all(i["status"] == publish.STATUS_WAIT and i["payload"]["saveToDraft"] for i in its)
    assert its[0]["fb_caption"]["caption"] != its[1]["fb_caption"]["caption"]                         # per-page caption
    assert its[0]["buffer"]["namespace"] == "user-Buffer--buffer2" and its[1]["buffer"]["namespace"] == "user-Buffer"
    assert all(i["suggested_slot_pt"] for i in its) and all("Comment" not in i["caption"] for i in its)
    # swap approval flow
    it = fb_caption.queue_swap(dict(product="grinch_robe", reel_key="fb:x:1", caption="Cozy #grinch #robe", reason="+12,000 in 1h"))
    raises(publish.approve_swap, it["id"], "agent", "ok")
    raises(publish.swap_action, it["id"])
    publish.approve_swap(it["id"], "Omar", "yes swap it")
    act = publish.swap_action(it["id"]); assert act["kind"] == "manual_or_graph" and "merryjammies.com" in act["text"]
    act = publish.swap_action(it["id"], buffer_post=dict(id="p1", status="draft", allowedActions="editPost")); assert act["kind"] == "buffer_edit_post"
    blk = fb_caption.queue_swap(dict(product="trumpglow", reel_key="fb:x:2", caption="x #trump", reason="40K"))
    raises(publish.approve_swap, blk["id"], "Omar", "ok")                                              # placeholder URL -> blocked
    publish.mark_swapped(it["id"], "Meta Business Suite by Omar")

def test_snapshot_tick():
    tmp = _setup(); old = (RF.RES, RF.SNAP, RF.INBOX, SS.LOG)
    RF.RES = tmp; RF.SNAP = os.path.join(tmp, "snap"); RF.INBOX = os.path.join(tmp, "inbox"); SS.LOG = os.path.join(tmp, "log.jsonl")
    try:
        r = SS.tick(use_graph=False); assert r["snapshot"] is None and r["rows"] == 0                 # no new data -> no fake hour
        assert not os.path.exists(RF.SNAP) or not os.listdir(RF.SNAP)
        src = open(RF.__file__).read(); assert "method=\"POST\"" not in src and "data=" not in src.split("def _get")[1].split("def ")[0]   # GET only
        assert len(open(SS.LOG).read().splitlines()) == 1
    finally: RF.RES, RF.SNAP, RF.INBOX, SS.LOG = old

if __name__ == "__main__":
    test_routing(); test_prepare_fb_all_and_swap(); test_snapshot_tick(); print("PASS test_d94_d96")
