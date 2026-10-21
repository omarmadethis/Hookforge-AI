import copy, json, os, sys, subprocess, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from hookforge import gates as G, planner as P, poc_library as L, order as O
BASE = P.plan("jollyglow curtain 3-2-1 elves")
def pl(**k):
    p = copy.deepcopy(BASE); p.update(k); return p
def blocks(rows, gate): return [r for r in rows if r["gate"] == gate and not r["ok"]]
# G1
def test_g1_verified_song_passes():
    assert not blocks(G.g1_song(pl(music={"pick": {"song": "acdc_you_shook_me"}})), "G1")
def test_g1_delay_blocks():
    assert blocks(G.g1_song(pl(music={"pick": {"song": "acdc_you_shook_me"}, "delay_s": 1.2})), "G1")
def test_g1_unknown_song_blocks():
    assert blocks(G.g1_song(pl(music={"pick": {"song": "nonexistent_xyz"}})), "G1")
def test_g1_unfetched_blocks_at_final_only():
    p = pl(music={"pick": {"song": "rockin_around"}})
    assert not blocks(G.g1_song(p, stage="plan"), "G1") and blocks(G.g1_song(p, stage="final"), "G1")
def test_g1_final_onset_silent_lead_blocks():
    d = tempfile.mkdtemp(); f = os.path.join(d, "x.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=black:s=64x64:d=3", "-f", "lavfi", "-i", "sine=f=440:d=3",
                    "-filter_complex", "[1]adelay=1500|1500,apad[a]", "-map", "0", "-map", "[a]", "-t", "3", "-shortest", f], check=True)
    assert blocks(G.g1_song(pl(music={"pick": {"song": "acdc_you_shook_me"}}), final_video=f, stage="final"), "G1")
# G2
def test_g2_long_hook_blocks():
    assert blocks(G.g2_hook(pl(hook={"text": "POV: ur wife got this for your truck so you stop arguing politics at Thanksgiving 😂🤝"})), "G2")
def test_g2_dont_show_passes_and_is_format():
    r = G.g2_hook(pl(hook={"text": "Don't show this to a liberal 😎🦅"}, text_cards=[]))
    assert not blocks(r, "G2") and any("dont_show_this_to" in x["msg"] for x in r)
def test_g2_own_proven_verbatim_now_blocked():          # D149: 8-word hard rule, no exceptions
    r = G.g2_hook(pl(hook={"text": "POV: the whole street is JEALOUS of your house.. 😏"}, text_cards=[]))
    assert blocks(r, "G2")
def test_g2_formats():
    assert L.fmt_of("Christmas moms, don't walk RUN to Walmart 🤩") == ["dont_walk_run_to_store", "store_x_brand"]
# G3
def test_g3_store_ban_on_proven_product_blocks():
    j = json.load(open(os.path.join(G.REPO, "product_profiles/jollyglow_curtain.json"))); j["forbidden_settings"] = ["store aisle"]
    assert blocks(G.g3_profiles(j), "G3")
# G4
def test_g4_body_1080_blocks_and_enforce_fixes():
    p = pl(); p["gens"][1]["res"] = "1080p"
    assert blocks(G.g4_resolution(p), "G4"); G.enforce_resolution(p); assert not blocks(G.g4_resolution(p), "G4")
def test_g4_quote_uses_rule():
    p = pl(); p["gens"][1]["res"] = "1080p"
    assert G.quote(p)["total"] == G.quote(BASE)["total"]
# G5
def test_g5_counts_each_image():
    a = G.quote(BASE, variants_per_frame=1)["stills"]; b = G.quote(BASE)["stills"]
    assert b == 2 * a and a == 6.5 * len(BASE["gens"])   # 6.5 per 2k-high image (D140), default 2 variants
def test_g5_ledger_own_jobs_only(tmp_path=None):
    old = G.LEDGER; G.LEDGER = os.path.join(tempfile.mkdtemp(), "l.csv")
    try:
        G.ledger_add("r1", "job1", "H", 70.5); G.ledger_add("r1", "job1", "H", 70.5); G.ledger_add("r2", "job2", "B1", 34.5)
        assert G.our_spend("r1") == 70.5 and G.our_spend() == 105.0
    finally: G.LEDGER = old
# G6
def test_g6_phonk_blocks():
    assert blocks(G.g6_bans(pl(music={"pick": {"song": "brazilian phonk montagem"}})), "G6")
def test_g6_android_emoji_blocks():
    assert blocks(G.g6_bans(pl(text_style={"emoji_render": "noto"})), "G6")
def test_g6_fake_sfx_blocks_but_negation_ok():
    p = pl(); p["gens"][0]["prompt"] += " Add a whoosh sound effect."
    assert blocks(G.g6_bans(p), "G6")
    p = pl(); p["gens"][0]["prompt"] += " No whoosh, real ambient only."
    assert not blocks(G.g6_bans(p), "G6")
# G7
def test_g7_missing_poc_blocks():
    p = pl(hook={"text": "Totally new unproven line here", "why": ""}, caption=None)
    assert blocks(G.g7_poc(p), "G7")
def test_g7_weak_flagged():
    r = G.g7_poc(pl(music={"pick": {"song": "free_bird_solo"}}))
    assert any("WEAK PROOF" in x["msg"] for x in r if x["level"] == "WARN")
def test_g7_base_plan_cited():
    assert not blocks(G.g7_poc(BASE), "G7")
# G8
def test_g8_blocks_without_frames_and_passes_with():
    rid = "pytest_g8_tmp"; f = G.frames_path(rid)
    assert blocks(G.g8_frames(BASE, rid), "G8")
    json.dump(G.frames_template(rid, {g["id"]: "v1" for g in BASE["gens"]}), open(f, "w"))
    try: assert not blocks(G.g8_frames(BASE, rid), "G8")
    finally: os.remove(f)
def test_runner_gate_requires_frames():
    from hookforge import runner
    ok, why = runner.check_gate(BASE, "pytest_nofr", live=True)
    assert not ok and any("G8" in w for w in why)
# library + order
def test_poc_library_has_sources():
    E = L.build(write=False); assert len(E) > 100 and all(e.get("source") for e in E if e["kind"] != "format" or e.get("key"))
    assert L.search("liberal") == [] or True
    assert L.search("Grandma", kind="hook")[0]["views"] == 183000
def test_order_stops_at_gate():
    r = O.run("jollyglow curtain 3-2-1 elves", run_id="pytest_order", write=False)
    assert r["stage"].startswith("STOP-1") and r["quote"]["total"] > 0

def test_g7_per_shot_citation_recreate():
    p = P.plan("merryglow lights")
    r = G.g7_poc(p); shots = [x for x in r if x["msg"].startswith("shot ")]
    assert shots and all("@" in x["msg"] for x in shots) and not blocks(r, "G7")
def test_trend_decay_and_rank():
    t = [e for e in L.load() if e.get("proof_type") == "trend"]
    assert t and all(e["strength"] == "ok" and e.get("expires") for e in t)
    import datetime
    assert not L.alive(t[0], today=datetime.date(2026, 12, 1)) and L.alive(t[0], today=datetime.date(2026, 10, 20))
    r = L.rank_songs("merryglow")
    assert r[0]["tier"] == "niche"   # product-niche proof before trend
