import pytest
from hookforge import card_count as C, gates as G
def test_one_ok(): assert C.gate([{"text": "Do NOT show this to an equestrian... 😏"}]) == []
def test_three_blocked():
    assert C.gate([{"text": "a"}, {"text": "b"}, {"text": "c"}], "then-vs-now")                       # 3 cards, no VS in the middle
    assert C.gate([{"text": "VS..."}, {"text": "b"}, {"text": "c"}], "then-vs-now")                   # VS on the first card
    assert C.gate([{"text": "a"}, {"text": "VS..."}, {"text": "c"}, {"text": "d"}], "then-vs-now")    # 4+ cards
def test_three_idea_vs_result_ok(): assert C.gate([{"text": "The idea..."}, {"text": "VS..."}, {"text": "The result"}], "then-vs-now") == []   # MR52 structure
def test_two_vs_ok(): assert C.gate([{"text": "The idea... 😭💡"}, {"text": "The result 😍🙈"}], "then-vs-now") == []
def test_two_plain_blocked(): assert C.gate([{"text": "Wow"}, {"text": "Look at this"}])
def test_two_closing_ok(): assert C.gate([{"text": "Wow"}, {"text": "Get it from the caption below 👇"}]) == []
def test_run_all_g26(): assert not G.g26_card_count({"text_cards": [{"text": "a"}, {"text": "b"}, {"text": "c"}]})[0]["ok"]
def test_edit_enforce():
    with pytest.raises(C.TooManyCards): C.enforce([{"text": "a"}, {"text": "b"}, {"text": "c"}])
