"""Ingest smoke test on a synthetic Business Suite export (TEST rows, written to a temp dir only).
Run: python analytics/tests/test_ingest.py"""
import os, sys, tempfile, subprocess
import pandas as pd
here = os.path.dirname(os.path.abspath(__file__)); tmp = tempfile.mkdtemp()
env = dict(os.environ, HOOKFORGE_INSIGHTS_DIR=tmp)
cmd = [sys.executable, os.path.join(here, "..", "ingest_insights.py"), "--page", "TEST", "--code", "TST", os.path.join(here, "fixture_business_suite_TEST.csv")]
subprocess.run(cmd, check=True, env=env); subprocess.run(cmd, check=True, env=env)  # re-ingest must not duplicate
d = pd.read_csv(os.path.join(tmp, "TST.csv"), dtype={"post_id": str})
assert len(d) == 2, d
assert "page_id" not in d.columns and not d.astype(str).apply(lambda c: c.str.contains("123456789")).any().any(), "page id leaked"
r = d.set_index("post_id").loc["900000000000002"]
assert r.views == 2000 and r.three_sec_views == 1000 and abs(r.three_sec_rate - 0.5) < 1e-9 and r.avg_watch_s == 8
assert r.posted_pt == "2026-10-21 01:05" and r.shares == 4 and r.link_clicks == 2
print("OK: ingest test passed", tmp)
