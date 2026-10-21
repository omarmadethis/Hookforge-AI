import os, subprocess, tempfile
from hookforge import gates as G, planner, lean_edit as E

def test_g2_no_exceptions():
    assert not G.g2_hook({"hook": {"text": "POV: the whole street is JEALOUS of your house.. 😏🏠"}})[0]["ok"]
    assert G.g2_hook({"hook": {"text": "POV: the whole street is JEALOUS 😏🏠"}})[0]["ok"]

def test_jolly_f06_hook_8_words():
    p = planner.plan("Gift difficulty POV video for the JollyGlow curtain", override={"format": "F06", "product_key": "jollyglow_curtain"}, mode="original")
    assert p["hook"]["text"] == "POV: the whole street is JEALOUS 😏🏠" and p["gates"]["ok"]

def test_slow_ramp_reveal():
    d = tempfile.mkdtemp(); p = os.path.join(d, "ramp.mp4")    # dark scene, coloured glow fades in 1.5 -> 2.5 s (no hard cut)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "color=c=0x101010:s=180x320:d=4:r=24",
                    "-vf", "drawbox=c=0xff3030@1:t=fill,fade=t=in:st=1.5:d=1:alpha=0" if False else
                    "geq=r='16+clip((T-1.5)/1.0,0,1)*200':g='16+clip((T-1.5)/1.0,0,1)*40':b='16+clip((T-1.5)/1.0,0,1)*40'",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", p], check=True)
    i = E.reveal_info(p); assert i["kind"] == "ramp" and 1.6 <= i["reveal_s"] <= 2.4
