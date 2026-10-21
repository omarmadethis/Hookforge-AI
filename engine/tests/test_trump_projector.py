import os, sys, numpy as np, cv2
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "tools", "trump_projector"))
import composite as C

def test_detect_and_composite():
    f = np.full((540, 960, 3), 12, np.uint8); cv2.ellipse(f, ((480, 270), (300, 220), 0), (200, 200, 210), -1)
    e = C.detect_disc(f); assert e is not None and abs(e[0] - 480) < 5 and abs(e[1] - 270) < 5
    art = np.zeros((256, 256, 3), np.uint8); art[:128] = (0, 0, 255)   # red top half -> must stay on top (upright)
    o = C.composite(f, e, art)
    assert o[200, 480, 2] > o[340, 480, 2] and o[30, 30].max() < 40   # top red, outside the disc stays dark

def test_crop_follows_disc_tail():
    W, H, fps = 1920, 1080, 30
    cx = np.r_[np.full(200, 900.0), np.linspace(900, 1500, 30)]   # disc runs right in the last second
    xs = C.crop_track(cx, W, H, fps); cw = int(H * 9 / 16)
    off = np.abs(cx - (xs + cw / 2)); fixed = np.abs(cx - float(np.median(cx)))
    assert fixed[-1] > 500 and off[-30:].max() < cw * 0.3 and (xs >= 0).all() and (xs <= W - cw).all()
    assert np.abs(np.diff(xs)).max() <= W * 0.6 / fps + 1   # speed-limited, no jumps

if __name__ == "__main__":
    test_detect_and_composite(); test_crop_follows_disc_tail(); print("PASS test_trump_projector")
