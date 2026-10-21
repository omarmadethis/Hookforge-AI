import pytest
from hookforge import card_count as C, gates as G
def test_one_ok(): assert C.gate([{"text": "Do NOT show this to an equestrian... 😏"}]) == []
def test_three_blocked(): assert C.gate([{"text": "a"}, {"text": "VS..."}, {"text": "c"}], "then-vs-now")
def test_two_vs_ok(): assert C.gate([{"text": "The idea... 😭💡"}, {"text": "The result 😍🙈"}], "then-vs-now") == []
def test_two_plain_blocked(): assert C.gate([{"text": "Wow"}, {"text": "Look at this"}])
def test_two_closing_ok(): assert C.gate([{"text": "Wow"}, {"text": "Get it from the caption below 👇"}]) == []
def test_run_all_g26(): assert not G.g26_card_count({"text_cards": [{"text": "a"}, {"text": "b"}, {"text": "c"}]})[0]["ok"]
def test_edit_enforce():
    with pytest.raises(C.TooManyCards): C.enforce([{"text": "a"}, {"text": "b"}, {"text": "c"}])
