import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from hookforge import omar_style as O
lv = lambda c, d: next(r["level"] for r in c["rows"] if r["dim"] == d)
sh = [dict(dur=2.0)] + [dict(dur=1.5)] * 5
c = O.compare(dict(dur=9.7, shots=sh, lufs=-14.1)); assert lv(c, "total") == "WARN" and lv(c, "loudness") == "OK"
c = O.compare(dict(dur=12.5, shots=sh[:4], lufs=-18.0)); assert lv(c, "total") == "OK" and lv(c, "shot_count") == "WARN" and lv(c, "loudness") == "WARN"
print("test_omar_style_d79 OK")
