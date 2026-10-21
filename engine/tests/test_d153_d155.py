import copy
from hookforge import buffer_preflight as B, publish, regen

GOOD = publish.build_payload("a" * 24, "facebook", 'Your window is boring. Fix it 🎄 SAY "LIGHTS"', video_url="https://video-pending.invalid/x.mp4")

def test_good_payload_passes():
    assert B.check_payload(GOOD, "facebook", real_url=False) == []

def test_schema_catches_format_errors():
    for mut, needle in ((lambda p: p.update(channelId="nope"), "schema"), (lambda p: p["metadata"]["facebook"].update(type="video"), "schema"),
                        (lambda p: p["metadata"]["facebook"].pop("type"), "facebook"), (lambda p: p["assets"][0]["video"].update(thumbnailUrl="https://x.io/t.jpg"), "thumbnailUrl"),
                        (lambda p: p.update(assets=[{"video": {"url": "not a url"}}]), "schema"), (lambda p: p.pop("schedulingType"), "schema"),
                        (lambda p: p.update(text="no cta here"), "SAY"), (lambda p: p.update(saveToDraft=False), "draft-only")):
        p = copy.deepcopy(GOOD); mut(p); pr = B.check_payload(p, "facebook", real_url=False)
        assert any(needle in x for x in pr), (needle, pr)

def test_real_url_rules_hide_url():
    p = copy.deepcopy(GOOD); p["assets"][0]["video"]["url"] = "https://bucket.s3.amazonaws.com/v.mp4?X-Amz-Signature=abc&X-Amz-Expires=600"
    pr = B.check_payload(p, "facebook", real_url=True); assert any("presigned" in x for x in pr) and not any("abc" in x for x in pr)

def test_weekly_all_pass():
    o = B.run(write=False); assert o["slots"] == 20 and o["passed"] == 20 and o["nothing_sent"]

def test_regen_one_command():
    assert regen.main()
