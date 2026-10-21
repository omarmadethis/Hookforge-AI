import os, sys, json, shutil, tempfile
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from hookforge import results_feed as RF, tracked_links as TL, sales_attribution as SA, ly_season as LY

HJ = "/workspace/hookforge/audience/fb_heatedjammies_insights.csv"
MG = "/workspace/merryglow/insights_reels.csv"

def test_csv_exports_parse():
    a = RF.read_csv_export(HJ, snapshot_pt="2026-10-20 09:00"); b = RF.read_csv_export(MG, snapshot_pt="2026-10-20 09:00")
    assert len(a) > 5 and a.views.notna().all() and a.platform.eq("fb").all() and a.reel_key.str.startswith("fb:id:").all()
    assert a.avg_watch_s.notna().any() and len(b) > 5 and b.three_sec_views.notna().any()

def test_graph_parse():
    fb = RF.parse_fb({"id": "1", "description": "Hi utm_content=abc", "created_time": "2026-10-20T16:00:00+0000", "length": 12.0},
                     {"data": [{"name": "blue_reels_play_count", "values": [{"value": 5000}]}, {"name": "post_video_avg_time_watched", "values": [{"value": 6500}]}]})
    assert fb["views"] == 5000 and fb["avg_watch_s"] == 6.5 and fb["posted_pt"] == "2026-10-20 09:00"
    ig = RF.parse_ig({"id": "9", "caption": "x", "timestamp": "2026-10-20T16:00:00+0000"},
                     {"data": [{"name": "views", "values": [{"value": 900}]}, {"name": "reels_skip_rate", "values": [{"value": 41.2}]}, {"name": "saved", "values": [{"value": 3}]}]})
    assert ig["views"] == 900 and ig["skip_rate"] == 41.2 and ig["saves"] == 3

def test_no_token_no_network(monkeypatch):
    monkeypatch.delenv("META_TOKEN", raising=False)
    assert len(RF.fetch_graph()) == 0

def test_velocity():
    s = pd.DataFrame([dict(reel_key="k", posted_pt="2026-10-01 10:00", snapshot_pt=t, views=v) for t, v in
                      [("2026-10-01 22:00", 100), ("2026-10-03 10:00", 1000), ("2026-10-08 10:00", 5000)]])
    v = RF.velocity(s).iloc[0]
    assert abs(v.views_d1 - 400) < 1 and abs(v.views_d3 - 1800) < 1 and v.views_d7 == 5000 and abs(v.growth_d1_d7 - 12.5) < 0.01

def test_match_utm_caption_duration():
    reg = pd.DataFrame([dict(video_id="tg-a-abc123", caption="His last day on my truck.. ❤️🇺🇸 {url}", duration_s=10.1, phash=None, queued_pt=None),
                        dict(video_id="jg-b-def456", caption="Your neighbors are gonna be jealous", duration_s=14.0, phash=None, queued_pt="2026-10-21 18:00")])
    reels = pd.DataFrame([dict(reel_key="r1", caption="buy https://x.com/p?utm_content=jg-b-def456", posted_pt=None, duration_s=None, file=None),
                          dict(reel_key="r2", caption="His last day on my truck.. ❤️🇺🇸 #trump", posted_pt=None, duration_s=10.0, file=None),
                          dict(reel_key="r3", caption="unrelated", posted_pt="2026-01-01 00:00", duration_s=99, file=None)])
    m = RF.match(reels, reg).set_index("reel_key")
    assert m.loc["r1", "video_id"] == "jg-b-def456" and m.loc["r1", "match_on"] == "utm_content"
    assert m.loc["r2", "video_id"] == "tg-a-abc123" and "caption" in m.loc["r2", "match_on"]
    assert pd.isna(m.loc["r3", "video_id"])

def test_phash_same_video_close():
    f = next((os.path.join(dp, x) for dp, _, fs in os.walk("/workspace/hookforge/out/live") for x in fs if x.endswith(".mp4")), None)
    if not f: return
    h = RF.phash(f); assert RF.phash_dist(h, h) == 0

def test_run_end_to_end(tmp_path, monkeypatch):
    monkeypatch.delenv("META_TOKEN", raising=False)
    for d in ("RES", "INBOX", "SNAP", "RAW"): monkeypatch.setattr(RF, d, str(tmp_path / d.lower()))
    monkeypatch.setattr(RF, "REGISTRY", str(tmp_path / "reg.csv")); os.makedirs(RF.INBOX); os.makedirs(RF.RES, exist_ok=True)
    shutil.copy(HJ, os.path.join(RF.INBOX, "hj.csv"))
    pd.DataFrame([dict(video_id="x-1", caption="The best when cold❄️", duration_s=13, phash=None, queued_pt=None)]).to_csv(RF.REGISTRY, index=False)
    r = RF.run(use_graph=False)
    assert r["reels"] > 5 and r["matched"] >= 1 and os.path.exists(os.path.join(RF.RES, "outcomes.csv"))

def test_tracked_links():
    u = TL.tracked_url("https://shop.com/products/x?ref=1&utm_source=old", "tg-A-v7", "Instagram", "TrumpGlow")
    assert "utm_source=ig" in u and "utm_content=tg-a-v7" in u and "utm_campaign=trumpglow" in u and "ref=1" in u and "old" not in u
    assert TL.fill_caption("Get it 👉 {url}", "v", "fb", "p") == "Get it 👉 {url}"
    assert "utm_source=fb" in TL.fill_caption("👉 {url}", "v", "fb", "p", "https://a.com/p")

def test_sales_attribution_readonly():
    for q in SA.QUERIES.values(): SA.check_query(q)
    try: SA.check_query("FROM sales SHOW orders GROUP BY customer_email"); assert False
    except ValueError: pass
    a = SA.load_attribution(); c = SA.coverage()
    assert "video_id" in a.columns and c["sessions"] > 0

def test_ly_season_prior_never_beats_own():
    d = LY.build(save=False)
    assert len(d) >= 10 and d.views.min() >= 1e6 and d.posted.min() >= "2025-11-01" and d.posted.max() <= "2026-01-10"
    p = LY.prior("post_cutoff", "music", d); assert p and all(v["score"] <= 0.5 for v in p.values())
    b = LY.blend({"song_a": 0.3}, {"song_b": dict(score=0.5)})
    assert b["song_a"] > b["song_b"]
    assert LY.phase_of("2025-11-28") == "bfcm" and LY.phase_of("2025-12-20") == "post_cutoff"


class _MP:
    def __init__(self): self.undo = []
    def setattr(self, o, n, v): self.undo.append((o, n, getattr(o, n))); setattr(o, n, v)
    def delenv(self, k, raising=True): self.undo.append(("env", k, os.environ.pop(k, None)))
    def restore(self):
        for o, n, v in reversed(self.undo):
            if o == "env":
                if v is not None: os.environ[n] = v
            else: setattr(o, n, v)

if __name__ == "__main__":
    import inspect, pathlib
    fails = 0
    for name, fn in list(globals().items()):
        if not name.startswith("test_") or not callable(fn): continue
        mp = _MP(); kw = {}
        ps = inspect.signature(fn).parameters
        if "monkeypatch" in ps: kw["monkeypatch"] = mp
        if "tmp_path" in ps: kw["tmp_path"] = pathlib.Path(tempfile.mkdtemp())
        try: fn(**kw); print("PASS", name)
        except Exception as e: fails += 1; print("FAIL", name, repr(e)[:300])
        finally: mp.restore()
    print(f"{fails} failed"); sys.exit(1 if fails else 0)
