import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from hookforge import planner, profiles
r = planner._mock_source(profiles.load("purrventure_carrier"), "F01")
assert r is None or r["views"] is None or isinstance(r["views"], int)
print("test_mock_source_nan OK", r)
