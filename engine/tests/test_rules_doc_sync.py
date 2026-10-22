import os, subprocess, sys
R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
def test_rules_doc_in_sync():
    r = subprocess.run([sys.executable, os.path.join(R, "tools", "build_rules_doc.py"), "--check"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout
