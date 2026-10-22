import os, sys, json, tempfile, io
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from hookforge import graph_caption as G, publish, fb_caption, approval_queue as AQ, concept_lab as CL, pv_p2_redo as P2, runner
REPO = os.path.join(os.path.dirname(__file__), "..", "..")

class FakeGraph:
    def __init__(self, desc): self.desc = desc; self.calls = []
    def __call__(self, req, timeout=30):
        self.calls.append((req.get_method(), req.full_url.split("?")[0]))
        if req.get_method() == "POST":
            from urllib.parse import parse_qs
            self.desc = parse_qs(req.data.decode())["description"][0]; body = {"success": True}
        else: body = {"id": "123", "description": self.desc}
        class R(io.BytesIO):
            def __enter__(s): return s
            def __exit__(s, *a): pass
        return R(json.dumps(body).encode())

@__import__("pytest").mark.owner_config
def test_graph_caption():
    tmp = tempfile.mkdtemp(); fb_caption.SWAP_DIR = os.path.join(tmp, "s")
    it = fb_caption.queue_swap(dict(product="grinch_robe", reel_key="fb:t:9", caption="Cozy #grinch", reason="+11K/h"))
    try: G.plan(it["id"], "123"); raise AssertionError
    except G.Refused: pass                                                        # not approved
    publish.approve_swap(it["id"], "Omar", "yes")
    p = G.plan(it["id"], "123"); assert p["data"]["access_token"].startswith("<") and "merryjammies" in p["data"]["description"]
    os.environ.pop(G.TOKEN_ENV, None)
    try: G.execute(it["id"], "123", opener=FakeGraph("Cozy #grinch")); raise AssertionError
    except G.Refused as e: assert "Secure Form" in str(e)                         # no token -> refuse
    try: G.execute(it["id"], "123", opener=FakeGraph("someone edited it"), token="T0K"); raise AssertionError
    except G.Refused as e: assert "differs" in str(e)                             # live caption changed -> refuse
    fg = FakeGraph("Cozy #grinch"); r = G.execute(it["id"], "123", opener=fg, token="T0K")
    assert r["status"] == "SWAPPED" and [c[0] for c in fg.calls] == ["GET", "POST", "GET"]
    assert "T0K" not in open(os.path.join(fb_caption.SWAP_DIR, it["id"] + ".json")).read()      # token never persisted
    assert "T0K" not in open(G.__file__).read()

def test_concept_and_redo_queue():
    tmp = tempfile.mkdtemp(); AQ.DIR = os.path.join(tmp, "q")
    appr = os.path.join(REPO, "learning", "approvals"); before = set(os.listdir(appr))
    r = CL.daily(products=["jollyglow_curtain", "nosuchproduct"])   # D131: robe retired
    a, b = r["items"]
    assert a["status"] == "AWAITING_OMAR_APPROVAL" and a["credits"] > 0 and a["approval_file_draft"]["approved_by"] == "" and a["poc"]
    assert "gates" in a and "preflight" in a and "error" in b                     # a product without a profile -> reported, not faked (trumpglow got one in D109)
    qd = os.path.join(os.path.dirname(appr), "approval_queue"); qb = set(os.listdir(qd))
    it = P2.queue(); assert it["status"] == "ARCHIVED_STALE" and not it["ready_for_approval"] and it["credits"] is None   # D141
    assert set(os.listdir(qd)) == qb and set(os.listdir(appr)) == before

def test_cast_crops_pass():
    from hookforge import ref_sanity as R
    for s, f in [("grinchmelt", "cast_woman_top.png"), ("merryfire", "cast_woman_top.png"), ("merryfire", "cast_woman_family_top.png"), ("merryglow", "cast_woman_top.png")]:
        assert R.check(os.path.join(REPO, "refs", s, "cast", f), "a woman")["ok"], (s, f)
    ids = json.load(open(os.path.join(REPO, "refs", "purrventure", "higgsfield_new_account_media_ids.json")))
    assert ids["ref_bengal_cream.png"] == "f14b458e-bbb1-4ee8-870e-dc710d42d7b2"

if __name__ == "__main__":
    test_graph_caption(); test_concept_and_redo_queue(); test_cast_crops_pass(); print("PASS test_d104_d108")
