import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from hookforge import ref_gate as R, runner
P, C = "11111111-2222-3333-4444-555555555555", "66666666-7777-8888-9999-000000000000"
def bad(params, refs):
    try: R.check(params, refs)
    except R.RefMissing: return
    raise AssertionError("expected RefMissing")
bad(dict(prompt="cat in ball"), None)
bad(dict(prompt="cat in ball", medias=[dict(value=P)]), dict(product=[P]))                 # no cast
bad(dict(prompt="cat in ball", medias=[dict(value=P)]), dict(product=[P], cast=[C]))        # cast not attached
bad(dict(prompt="x", medias=[]), dict(product=["<PRODUCT_MEDIA_ID>"], cast=[C]))
assert R.check(dict(prompt="cat in ball", medias=[dict(value=P), dict(value=C)]), dict(product=[P], cast=[C]))
assert R.check(dict(prompt="no product anywhere in frame", medias=[dict(value=C)]), dict(cast=[C]))
plan = dict(gens=[dict(id="G1", model="seedance_2_5", res="1080p", dur=4, prompt="p", start_frame=dict(prompt="s"))])
cs = runner.build_calls(plan, P, cast_media_ids=[C]); assert all(R.check(c["params"] if "{job:" not in str(c["params"]) else dict(c["params"], medias=[m for m in c["params"]["medias"]]), c["refs"]) for c in cs)
print("test_ref_gate OK")
