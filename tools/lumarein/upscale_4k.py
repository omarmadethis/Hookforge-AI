#!/usr/bin/env python3
"""MR59 final-step template (Barn Glow / LumaRein and every other product). Run AFTER the master gate PASSED, immediately before posting.
  python3 tools/lumarein/upscale_4k.py plan   <gated.mp4>                    # prints the exact Higgsfield upscale_video call + credit reserve (runs nothing)
  python3 tools/lumarein/upscale_4k.py finish <gated.mp4> <downloaded.mp4> [job_id] [credits]   # strip metadata, verify audio/length/cards/visuals, bind -> <gated>_4k.mp4
Then post/host ONLY the printed *_4k.mp4 (publish.prepare refuses anything below 4K)."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "engine"))
from hookforge import upscale4k as U
if sys.argv[1] == "plan": print(json.dumps(U.plan(sys.argv[2]), indent=1))
elif sys.argv[1] == "finish":
    a = sys.argv; print(U.finish(a[2], a[3], job_id=a[4] if len(a) > 4 else None, credits=float(a[5]) if len(a) > 5 else None))
