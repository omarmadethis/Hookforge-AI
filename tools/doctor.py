#!/usr/bin/env python3
"""Hookforge doctor: checks that a machine can build, gate and publish. Read-only; never prints secret values.

    python3 tools/doctor.py          # exit 0 = ready, 1 = something to fix
"""
import importlib, json, os, re, shutil, subprocess, sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OK, WARN, FAIL = "OK  ", "WARN", "FAIL"
results = []
def rep(level, what, hint=""):
    results.append(level); print(f"[{level}] {what}" + (f"\n        -> {hint}" if hint else ""))

# 1. Python
v = sys.version_info
rep(OK if v >= (3, 10) else FAIL, f"python {v.major}.{v.minor}", "" if v >= (3, 10) else "install Python 3.10+")

# 2. pip packages (required / optional)
REQ = {"numpy": "numpy", "pandas": "pandas", "PIL": "Pillow", "cv2": "opencv-python-headless", "pytesseract": "pytesseract",
       "scipy": "scipy", "sklearn": "scikit-learn", "matplotlib": "matplotlib", "pytest": "pytest", "jsonschema": "jsonschema", "requests": "requests"}
OPT = {"open_clip": "open_clip_torch", "torch": "torch"}
for mod, pkg in REQ.items():
    try: importlib.import_module(mod); rep(OK, f"python package {pkg}")
    except Exception: rep(FAIL, f"python package {pkg} missing", "pip install -r requirements.txt")
for mod, pkg in OPT.items():
    try: importlib.import_module(mod); rep(OK, f"optional package {pkg}")
    except Exception: rep(WARN, f"optional package {pkg} missing (only used for the product-share estimate)")

# 3. System tools
for tool, hint in [("ffmpeg", "apt install ffmpeg / brew install ffmpeg"), ("ffprobe", "comes with ffmpeg"),
                   ("exiftool", "apt install libimage-exiftool-perl / brew install exiftool (metadata strip + verify, MR01)"),
                   ("tesseract", "apt install tesseract-ocr / brew install tesseract (card OCR, MR39)")]:
    rep(OK if shutil.which(tool) else FAIL, f"{tool} on PATH", "" if shutil.which(tool) else hint)
if shutil.which("ffmpeg"):
    cfg = subprocess.run(["ffmpeg", "-hide_banner", "-buildconf"], capture_output=True, text=True).stdout
    for lib in ("libx264", "libass", "libx265"):
        rep(OK if lib in cfg else WARN, f"ffmpeg built with {lib}", "" if lib in cfg else "install a full ffmpeg build")

# 4. Repo location (several build scripts use /workspace/hookforge)
want = "/workspace/hookforge"
here_ok = os.path.realpath(want) == os.path.realpath(REPO) if os.path.exists(want) else False
rep(OK if here_ok else WARN, f"repo reachable at {want}",
    "" if here_ok else f"sudo mkdir -p /workspace && sudo ln -s {REPO} {want}")

# 5. Apple iOS emoji assets (MR35)
ed = os.path.join(REPO, "assets", "emoji_apple", "160")
n = len([f for f in os.listdir(ed) if f.endswith(".png")]) if os.path.isdir(ed) else 0
rep(OK if n else FAIL, f"Apple emoji PNGs: {n} in assets/emoji_apple/160", "" if n else "restore assets/emoji_apple/160 from the repo")
font = os.path.join(REPO, "assets", "emoji_apple", "AppleColorEmoji-Linux.ttf")
rep(OK if os.path.exists(font) else WARN, "AppleColorEmoji-Linux.ttf (optional, only to render NEW emoji PNGs)",
    "" if os.path.exists(font) else "only the emoji already in assets/emoji_apple/160 can be used on cards until you add more (see docs/SETUP.md)")

# 6. Config
for name in ("buffer_routing", "product_urls"):
    real, ex = os.path.join(REPO, "config", f"{name}.json"), os.path.join(REPO, "config", f"{name}.example.json")
    if os.path.exists(real):
        txt = open(real).read()
        rep(WARN if "YOUR_" in txt else OK, f"config/{name}.json", "still has YOUR_* placeholders" if "YOUR_" in txt else "")
    else:
        rep(WARN, f"config/{name}.json not created (using the example)", f"cp config/{name}.example.json config/{name}.json and fill it in")
try:
    prods = json.load(open(os.path.join(REPO, "config", "products.json")))["products"]
    act = [k for k, p in prods.items() if p.get("active")]
    rep(OK if act else WARN, f"active products in config/products.json: {', '.join(act) or 'none'}", "" if act else "mark your product \"active\": true")
except Exception as e: rep(FAIL, f"config/products.json unreadable: {e}")

# 7. Env + secret hygiene (values are never printed)
envf = os.path.join(REPO, ".env")
rep(OK if os.path.exists(envf) else WARN, ".env present" if os.path.exists(envf) else ".env not created (optional)", "" if os.path.exists(envf) else "cp .env.example .env")
for k in ("META_TOKEN", "GH_TOKEN"):
    rep(OK if os.environ.get(k) else WARN, f"env {k} {'is set' if os.environ.get(k) else 'not set (optional)'}")
try:
    tracked = subprocess.run(["git", "-C", REPO, "ls-files"], capture_output=True, text=True).stdout.split("\n")
    bad = [f for f in tracked if re.search(r"(^|/)\.env$|config/buffer_routing\.json$|config/product_urls\.json$|spend_ledger\.csv$", f)]
    rep(FAIL if bad else OK, "no private config/.env/ledger tracked by git", f"git rm --cached {' '.join(bad)}" if bad else "")
except Exception: rep(WARN, "git not available to check tracked files")

# 8. Engine imports
sys.path.insert(0, os.path.join(REPO, "engine"))
try:
    from hookforge import master_gate, userconfig  # noqa
    rep(OK, f"engine imports (master gate: {len(json.load(open(master_gate.RULES_JSON)))} rules)")
except Exception as e: rep(FAIL, f"engine import failed: {e}")

print("\nREADY" if FAIL not in results else "\nNOT READY: fix the FAIL lines above")
sys.exit(1 if FAIL in results else 0)
