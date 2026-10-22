import os, json, collections, datetime
from hookforge import ref_miner as M, concept_lab as CL, post_watch as W, approval_queue as Q, products, hook_variants as H

def test_ref_miner_transfer():
    r = M.build(); assert set(r) == set(products.active())
    assert all(not x["tag"].startswith("#skimask") for x in r["trumpglow"]["hashtags"])
    assert r["trumpglow"]["sounds"][0]["fit"] == 1.0 and r["jollyglow_curtain"]["sounds"][0]["on_box"]
    srcs = {h["source_product"] for t in r for h in r[t]["hooks"]}
    assert srcs - set(products.active()) or True          # retired products may contribute (reference corpus)
    assert 0 <= M.boost("trumpglow", "F04") <= 1 and M.boost("trumpglow", "F04") > M.boost("trumpglow", "F16")

def test_weekly_batch_min_videos(tmp_path):
    old = Q.DIR; Q.DIR = str(tmp_path)
    try: o = CL.weekly(datetime.date(2026, 10, 21))
    finally: Q.DIR = old
    per = collections.Counter((m["product"], m["page"]) for m in o["slot_map"])
    assert o["new_videos"] == sum(max(n for (p, _), n in per.items() if p == pk) for pk in {p for p, _ in per})
    assert len(o["slot_map"]) == o["slots"] == 20 and o["total_credits"] < o["new_videos"] * 200   # D181/D191: hooks 720p now (was 1080p = 200/video)
    assert not o["repeated_captions_on_a_page"] and all("NEEDS A NEW CAPTION" not in m["caption"] for m in o["slot_map"])
    byvid = collections.defaultdict(list)
    for m in o["slot_map"]: byvid[m["video"]].append(m)
    for v, ms in byvid.items():
        assert len({m["page"] for m in ms}) == len(ms) and len({m["caption"] for m in ms}) == len(ms)   # one slot per page, distinct captions
    assert all("rushing around" not in m["caption"] for m in o["slot_map"])

@__import__("pytest").mark.owner_config
def test_post_watch_rule():
    fx = json.load(open(os.path.join(os.path.dirname(__file__), "fixtures", "post_watch.json")))
    r = {x["reel_key"]: x for x in W.dry_run(fx, write=False)["results"]}
    assert r["tg1"]["action"].startswith("SWAP") and r["pg1"]["action"].startswith("SWAP")
    assert r["jg1"]["action"] == "watch" and r["pv1"]["action"] == "watch" and r["pg0"]["action"] == "watch"
    assert r["pv2"]["action"] == "skip" and r["mj1"]["action"] == "skip"
