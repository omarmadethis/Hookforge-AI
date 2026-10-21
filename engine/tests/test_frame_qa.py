import os, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from hookforge import frame_qa as Q
from PIL import Image
d = tempfile.mkdtemp(); Image.new("RGB", (90, 160)).save(os.path.join(d, "A.png")); Image.new("RGB", (90, 160)).save(os.path.join(d, "B.png"))
ok = {k: True for k in Q.CHECKS}
try: Q.record(d, "A", {"gaze_ok": True}); raise SystemExit("incomplete checklist accepted")
except ValueError: pass
Q.record(d, "A", ok); Q.record(d, "B", dict(ok, physics_no_clipping=False), "paw through mesh")
try: Q.build_sheet(d, ["A", "B"], os.path.join(d, "s.jpg")); raise SystemExit("sheet built with a failing frame")
except Q.FrameQAFail as e: assert "paw through mesh" in str(e)
try: Q.require_all_pass(d, ["A", "C"]); raise SystemExit("unreviewed frame passed")
except Q.FrameQAFail: pass
Q.record(d, "B", ok); assert Q.build_sheet(d, ["A", "B"], os.path.join(d, "s.jpg"))
print("test_frame_qa OK")
