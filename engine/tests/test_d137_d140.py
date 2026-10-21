from hookforge import political_lint as P, publish, concept_lab as C, lean_plan as L, gates
def test_pl6_warn():
    assert any(r == "PL6" and s == "WARN" for r, s, _ in P.lint_text("Fake Trump Fans.. 🤢👎"))
def test_listing_blocked():
    assert publish.is_listing("Christmas Lighted Hanging Door Decor with Stained Glass")
    assert not publish.is_listing("They'll be asking where you got it..")
def test_weekly_clean_distinct():
    o = C.weekly(); caps = [m["caption"] for m in o["slot_map"]]
    assert not any("fake" in c.lower() or publish.is_listing(c) for c in caps)
    assert o["repeated_captions_on_a_page"] == []
def test_price_and_lean():
    assert gates.PRICES["still_gpt_image_2"] == 6.5
    q = L.quote(); assert q["total_credits"] < q["standard_total"] and q["total_credits"] == 1227.0
