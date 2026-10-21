from hookforge import ly_season as LY
def test_load_drops_paid():
    d = LY.load(); assert len(d) == 147 and not set(d.key) & LY.PAID_KEYS and (d.hook_confidence == "low").all()
def test_song_starts():
    assert LY.song_in_point("Rockin' Around The Christmas Tree - Brenda Lee")["in_point_s"] == 0.0
    assert LY.song_in_point("Christmas (Baby Please Come Home) - Darlene Love")["in_point_s"] == 14.9
    m = LY.song_in_point("All I Want for Christmas Is You - Mariah Carey"); assert 48 <= m["in_point_s"] <= 51
    assert LY.song_in_point("Viva La Vida - Coldplay")["in_point_s"] == 8.3 and LY.song_in_point("nope") is None
def test_concepts_low_conf():
    c = LY.concept_signals(); assert set(c) <= set(LY.CONCEPT_SUBTYPES) and c
    assert all(v["confidence"] == "low" and v["score"] <= 0.25 for v in c.values())
def test_format_prior_discounted():
    for ph in LY.load().phase.unique():
        for v in LY.prior(ph, "format").values(): assert v["confidence"] == "low" and v["score"] <= 0.25
