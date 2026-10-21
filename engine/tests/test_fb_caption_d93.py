import os, sys, json, re, csv, datetime as dt
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from hookforge import fb_caption as F

def test_library_has_poc():
    lib, tags = F.build_library()
    for k, v in lib.items():
        for p in v["patterns"]:
            assert p["poc"] and all("views" in e and "ref" in e for e in p["poc"]), k
    assert tags["grinch_robe"]["default_set"][0] == "#christmas"

def test_generate_all_products_fb_rules():
    for k in F.PRODUCTS:
        g = F.generate(k, {})
        assert not re.search(r"(?i)\bcomment", g["text"]), g
        assert g["hashtags"] and g["text"].endswith(" ".join(g["hashtags"]))
        assert g["poc"] and g["audience_fit"]["ok"]
        assert g["swap_text"].startswith("Get it here 👉 ")

def test_comment_to_say():
    assert F.fb_safe('Comment "DISNEY" if you want one') == 'SAY "DISNEY" if you want one'

def test_traction_thresholds_d93_6():
    assert F.traction(dict(views=41000, posted_pt="2026-10-01 10:00", snapshot_pt="2026-10-20 12:00"))["swap"]
    # 10K in the first hour
    assert F.traction(dict(views=10500, posted_pt="2026-10-20 11:10", snapshot_pt="2026-10-20 12:00"))["swap"]
    # 10K gained in a later one-hour window between snapshots
    assert F.traction(dict(views=25000, posted_pt="2026-10-19 08:00", snapshot_pt="2026-10-20 12:00"), [("2026-10-20 11:15", 14000)])["swap"]
    # old rules gone: 1.5K v/h at 4h, 6K views -> no swap; 9.9K in first hour -> no swap
    assert not F.traction(dict(views=6000, posted_pt="2026-10-20 08:00", snapshot_pt="2026-10-20 12:00"))["swap"]
    assert not F.traction(dict(views=9900, posted_pt="2026-10-20 11:30", snapshot_pt="2026-10-20 12:00"))["swap"]
    # 30K over 2h with no <=1h window showing 10K
    assert not F.traction(dict(views=30000, posted_pt="2026-10-10 12:00", snapshot_pt="2026-10-20 12:00"), [("2026-10-20 10:00", 25000)])["swap"]

def test_swap_keeps_hashtags_and_is_approval_item(tmp_path, monkeypatch):
    monkeypatch.setattr(F, "SWAP_DIR", str(tmp_path))      # D169: no leak into later tests
    it = F.queue_swap(dict(reel_key="fb:t:x", product="grinch_robe", caption="All moms need this🎁 #christmas #mom", reason="test"))
    assert it["status"] == "AWAITING_OMAR_APPROVAL"
    assert it["new_caption"] == "Get it here 👉 https://merryjammies.com/products/merryjammies-festive-heating-robe\n#christmas #mom"
    it2 = F.queue_swap(dict(reel_key="fb:t:y", product="brickhood_mask", caption="x #skimask", reason="t"))
    assert it2["blocked"]

def test_buffer_published_post_refused():
    try: F.swap_buffer_payload(dict(id="a" * 24, status="sent"), "x"); assert False
    except ValueError: pass

def test_trending_relevance(tmp_path):
    f = tmp_path / "t.csv"
    with open(f, "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["product", "caption", "hashtags", "source_url", "views", "date"])
        w.writerow(["", "Trump 2028 lights up the porch", "#trump #maga", "https://x/1", "900000", "2026-10-19"])
        w.writerow(["", "this heated robe is everything", "#heatedrobe", "https://x/2", "500000", "2026-10-19"])
        w.writerow(["GrinchMelt", "best mug for cocoa", "#mug", "https://x/3", "300000", "2026-10-19"])
        w.writerow(["GrinchMelt", "my dog skiing", "#ski", "https://x/4", "300000", "2026-10-19"])
    r = F.ingest_trending([str(f)], write=False)
    got = {a["source_url"]: a["product"] for a in r["accepted"]}
    assert got == {"https://x/1": "trumpglow", "https://x/2": "grinch_robe", "https://x/3": "grinchmelt_mug"}

def test_real_vr_batch():
    p = "/workspace/research/trending_captions/2026-10-20.csv"
    if not os.path.exists(p): return
    r = F.ingest_trending([p], write=False)
    assert len(r["accepted"]) + len(r["rejected"]) == 44
    assert all(not re.search(r"(?i)\bcomment", a["body_fb"]) for a in r["accepted"])
