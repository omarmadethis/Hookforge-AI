import os, sys, json, struct, zlib, tempfile, datetime, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from PIL import Image
from hookforge import deliver as D, results_feed as RF, snapshot_scheduler as SS

def test_c2pa_block_and_preview():
    tmp = tempfile.mkdtemp(); D.OUT_DIR = os.path.join(tmp, "out"); D.MANIFEST = os.path.join(D.OUT_DIR, "manifest.json")
    Image.new("RGB", (32, 32), "red").save(f"{tmp}/a.png"); b = open(f"{tmp}/a.png", "rb").read()
    dat = b"jumb....jumdc2pa"; ch = struct.pack(">I", len(dat)) + b"caBX" + dat + struct.pack(">I", zlib.crc32(b"caBX" + dat))
    open(f"{tmp}/c.png", "wb").write(b[:33] + ch + b[33:])
    Image.new("RGB", (32, 32), "red").save(f"{tmp}/a.jpg"); b = open(f"{tmp}/a.jpg", "rb").read(); seg = b"JP\x00\x00jumbjumdc2pa"
    open(f"{tmp}/c.jpg", "wb").write(b[:2] + b"\xff\xeb" + struct.pack(">H", len(seg) + 2) + seg + b[2:])
    Image.new("RGB", (32, 32), "red").save(f"{tmp}/a.webp", "WEBP", lossless=True); b = open(f"{tmp}/a.webp", "rb").read()
    nb = b + b"C2PA" + struct.pack("<I", 8) + b"jumdc2pa"; nb = nb[:4] + struct.pack("<I", len(nb) - 8) + nb[8:]; open(f"{tmp}/c.webp", "wb").write(nb)
    mp = f"{tmp}/c.mp4"; ft = struct.pack(">I", 16) + b"ftypisom" + b"\x00" * 4; uu = struct.pack(">I", 8 + 16 + 4) + b"uuid" + D.C2PA_UUID + b"abcd"
    open(mp, "wb").write(ft + uu)
    for f in ("c.png", "c.jpg", "c.webp", "c.mp4"):
        assert D.c2pa_manifests(f"{tmp}/{f}"), f
        assert any("C2PA" in p for p in D.scan(f"{tmp}/{f}")), f                    # hard block in the delivery scan
    for f in ("a.png", "a.jpg", "a.webp"): assert not D.c2pa_manifests(f"{tmp}/{f}") and not D.scan(f"{tmp}/{f}"), (f, D.scan(f"{tmp}/{f}"))
    for f in ("c.png", "c.jpg", "c.webp"):
        out = D.preview(f"{tmp}/{f}"); assert os.path.basename(out).startswith("preview__") and not D.scan(out) and not D.c2pa_manifests(out)
    try: D.preview(f"{tmp}/x.txt"); raise AssertionError
    except D.Refused: pass

def test_meta_csv_ingest():
    tmp = tempfile.mkdtemp(); old = (RF.RES, RF.SNAP, RF.INBOX, SS.LOG)
    RF.RES = tmp; RF.SNAP = os.path.join(tmp, "snap"); RF.INBOX = os.path.join(tmp, "inbox"); SS.LOG = os.path.join(tmp, "log.jsonl"); os.makedirs(RF.INBOX)
    hdr = "Post ID,Page ID,Page name,Title,Description,Duration (sec),Publish time,Permalink,Post type,Date,Views,Reach,Reactions,Comments,Shares,Total clicks,Link clicks,Seconds viewed,Average Seconds viewed,3-second video views,1-minute video views\n"
    row = '1234567890,999,TrumpGlow,"Fake Trump fans","Don\'t show this to a liberal #trump",12,10/20/2026 13:05,https://www.facebook.com/reel/1234567890,Reels,Lifetime,15200,9100,410,22,35,40,12,61000,4.1,7000,0\n'
    open(os.path.join(RF.INBOX, "TrumpGlow_insights_reels.csv"), "w").write(hdr + row)
    ig = "Post ID,Account ID,Account username,Account name,Description,Duration (sec),Publish time,Permalink,Post type,Date,Views,Reach,Likes,Shares,Follows,Comments,Saves\n" \
         "555,1,merry.jammies,Merry Jammies,cozy #grinch,9,10/20/2026 12:00,https://www.instagram.com/reel/abc/,IG reel,Lifetime,3000,2000,100,5,2,3,9\n"
    open(os.path.join(RF.INBOX, "merry_ig_insights.csv"), "w").write(ig)
    try:
        df = RF.read_csv_export(os.path.join(RF.INBOX, "TrumpGlow_insights_reels.csv"))
        r = df.iloc[0]; assert r.views == 15200 and r.page == "TrumpGlow" and r.platform == "fb" and r.avg_watch_s == 4.1 and r.three_sec_views == 7000
        assert "Page ID" not in df.columns and "999" not in df.to_csv()
        rec = SS.tick(use_graph=False, queue_swaps=False)
        assert rec["rows"] == 2 and rec["snapshot"] and os.listdir(os.path.join(RF.INBOX, "processed"))
        s = __import__("pandas").read_csv(rec["snapshot"]); assert set(s.platform) == {"fb", "ig"} and s.views.max() == 15200
    finally: RF.RES, RF.SNAP, RF.INBOX, SS.LOG = old


def test_publishing_panel():
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "analytics"))
    import engine_panels as E
    sid, title, body, note = E.publishing_panel(public=False)[0]
    assert "TrumpGlow" in body and "LOCKED" in body and "Routing map" in body and "Caption swaps pending" in body and "(reserved slot)" in body
    pub = E.publishing_panel(public=True)[0][2]; assert "6ad7d610778b240e2f6f8b6c" not in pub      # no channel ids in the public build

if __name__ == "__main__":
    test_c2pa_block_and_preview(); test_meta_csv_ingest(); test_publishing_panel(); print("PASS test_d99_d102")
