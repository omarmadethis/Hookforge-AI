import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from hookforge import ref_sanity as R
REPO = os.path.join(os.path.dirname(__file__), "..", "..")

def test_ref_sanity():
    old = os.path.join(REPO, "refs", "_superseded", "purrventure_ref_bengal_cream_grasscrop.png")
    assert not R.check(old, "a cream bengal cat")["ok"]                                   # the grass crop fails
    assert R.check(os.path.join(REPO, "refs", "purrventure", "ref_bengal_cream.png"), "a cream bengal cat")["ok"]

if __name__ == "__main__":
    test_ref_sanity(); print("PASS test_ref_sanity_d100")
