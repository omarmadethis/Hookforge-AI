import copy, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from hookforge import gates as G
def b(rows, g): return [r for r in rows if r["gate"] == g and not r["ok"]]
def w(rows, g): return [r for r in rows if r["gate"] == g and r["level"] == "WARN"]
def test_g14_vs_first_blocks():
    assert b(G.g14_vs_card({"text_cards": [{"text": "Last day Vs.. first day"}]}), "G14")
    assert not b(G.g14_vs_card({"text_cards": [{"text": "Last day 😔"}, {"text": "Vs.."}]}), "G14")
def test_g15_linger():
    tl = [{"gen": "H", "dur": 2}, {"gen": "B1", "dur": 4.0}, {"gen": "R", "dur": 3.5, "role": "reveal"}]
    assert b(G.g15_linger({"shots": tl}), "G15") and not b(G.g15_linger({"shots": [tl[0], tl[2]]}), "G15")
def test_g16_models():
    assert b(G.g16_models({"gens": [{"id": "H", "model": "kling 2.1"}]}), "G16")
    assert b(G.g16_models({"gens": [{"id": "H", "model": "seedance_2_5", "end_frame": "x.png"}]}), "G16")
    assert not b(G.g16_models({"gens": [{"id": "H", "model": "seedance_2_5", "start_frame": {"model": "gpt_image_2"}}]}), "G16")
def test_g17_budget():
    big = {"gens": [{"id": f"B{i}", "res": "720p", "dur": 4} for i in range(8)]}
    assert b(G.g17_budget(big), "G17") and not b(G.g17_budget(dict(big, budget=400)), "G17")
def test_g18_len():
    assert b(G.g18_gen_len({"gens": [{"id": "B", "dur": 8}]}), "G18") and not b(G.g18_gen_len({"gens": [{"id": "B", "dur": 4}]}), "G18")
def test_g19_emoji():
    assert w(G.g19_emoji({"text_cards": [{"text": "Last day 💔"}]}), "G19")
    assert w(G.g19_emoji({"text_cards": [{"text": "Last day 😔"}]}), "G19")
    # POC-based (Omar 23:30): proven + paired passes (❤️ POC-0255 2.4M, 🇺🇸 Omar cards); 😔 is never forced
    assert not w(G.g19_emoji({"text_cards": [{"text": "His last day on my truck.. ❤️🇺🇸"}]}), "G19")
    assert not b(G.g19_emoji({"text_cards": [{"text": "Last day 😔🇺🇸"}]}), "G19")   # never a block
@__import__("pytest").mark.owner_config
def test_g18_approved_exception():
    p = {"run_id": "jollyglow_combo", "gens": [{"id": "garage_afters", "dur": 6}]}
    assert not b(G.g18_gen_len(p), "G18") and b(G.g18_gen_len(dict(p, run_id="other")), "G18")
def test_g20_afters():
    assert b(G.g20_afters({"gens": [{"id": "A1", "role": "after", "prompt": "curtain shows a tree"}]}), "G20")
    assert b(G.g20_afters({"gens": [{"id": "A1", "role": "after", "prompt": "snowman animates", "design": "snowman"}, {"id": "A2", "role": "after", "prompt": "snowman animates", "design": "snowman"}]}), "G20")
    assert not b(G.g20_afters({"gens": [{"id": "A1", "role": "after", "prompt": "snowman animates", "design": "snowman"}, {"id": "A2", "role": "after", "prompt": "sleigh flies across", "design": "sleigh"}]}), "G20")
def test_g21_structure():
    ok = {"format": "then_vs_now", "text_cards": [{"text": "Christmas 2025.."}, {"text": "Vs..."}, {"text": "Christmas 2026 😏"}]}
    assert not b(G.g21_vs_structure(ok), "G21")
    assert b(G.g21_vs_structure(dict(ok, text_cards=[{"text": "2025 Vs 2026"}, {"text": "Christmas 2026"}])), "G21")
def test_g22_caption():
    assert b(G.g22_post_caption({}), "G22") and not b(G.g22_post_caption({"post_caption": {"text": "Get yours👉{url}", "poc": "FBHJ"}}), "G22")
def test_splice_requires_timeline_per_variant():
    import inspect
    from hookforge import qa
    assert "BLOCK no timeline passed" in inspect.getsource(qa.final_checks) and hasattr(qa, "final_checks_variants")
