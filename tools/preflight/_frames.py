"""Shared frame sampler (ffmpeg -> numpy). Light: default 2 fps, 360 px wide."""
import subprocess, json, numpy as np

def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height:format=duration", "-of", "json", path], capture_output=True, text=True).stdout
    j = json.loads(out); s = j["streams"][0]
    return int(s["width"]), int(s["height"]), float(j["format"]["duration"])

def frames(path, fps=2.0, width=360):
    w, h, dur = probe(path)
    H = int(round(h * width / w / 2) * 2)
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={fps},scale={width}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True).stdout
    n = len(raw) // (width * H * 3)
    arr = np.frombuffer(raw[: n * width * H * 3], np.uint8).reshape(n, H, width, 3)
    return [(i / fps, arr[i]) for i in range(n)], dur
