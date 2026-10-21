#!/usr/bin/env python3
"""Render the format library. Usage: python3 formats/_build.py  (from repo root or formats/)."""
import os, sys, json, glob, importlib
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from _common import render_md, render_json, score, check_prompts, fmt_views, ensure_start_frames, ensure_flags
from _index import render_index

formats = []
for mod in sorted(glob.glob(os.path.join(HERE, "_formats_*.py"))):
    formats += importlib.import_module(os.path.basename(mod)[:-3]).F
slugs = [f["slug"] for f in formats]; assert len(slugs) == len(set(slugs)), "duplicate slug"
for f in formats:
    f["_score"] = score(f["evidence"]); ensure_start_frames(f); ensure_flags(f); check_prompts(f)
formats.sort(key=lambda f: ("ABCX".index(f["tier"]), -f["_score"][0]))
for rank, f in enumerate(formats, 1):
    f["rank"] = rank
    open(os.path.join(HERE, f"{f['slug']}.md"), "w").write(render_md(f))
    open(os.path.join(HERE, f"{f['slug']}.json"), "w").write(render_json(f))
open(os.path.join(HERE, "INDEX.md"), "w").write(render_index(formats))
json.dump([{"rank": f["rank"], "slug": f["slug"], "tier": f["tier"], "score": f["_score"][0],
            "internal_hits": f["_score"][1], "internal_tested": f["_score"][2], "external_winners": f["_score"][3],
            "evidence_rows": len(f["evidence"])} for f in formats],
          open(os.path.join(HERE, "index.json"), "w"), indent=2)
for f in formats:
    print(f"{f['rank']:>2} {f['tier']} {f['_score'][0]:>5} hits {f['_score'][1]}/{f['_score'][2]} ext {f['_score'][3]:>2} rows {len(f['evidence']):>2}  {f['slug']}")
