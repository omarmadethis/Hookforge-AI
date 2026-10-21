"""Measure every corpus video once (cached). Run: nice -n 19 python3 -m backtest.measure_corpus [--sources own,external]"""
import os, sys, json, hashlib, argparse
from multiprocessing import Pool
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from hookforge.config import REPO
from hookforge import measure as M

PROMPT = {"wearable_gift": "a fluffy robe or blanket", "decor_light": "christmas lights or a light projector",
          "decor_fire": "a tabletop fire pit", "decor_mug": "a mug", "accessory": "a ski mask", "pet": "a pet carrier",
          "gadget": "a toy gadget", "home": "a home product"}
CACHE = f"{REPO}/private/cache/measure"

def cache_path(f):
    st = os.stat(f); return f"{CACHE}/{hashlib.sha1(f'{f}|{st.st_size}'.encode()).hexdigest()[:16]}.json"

def job(args):
    key, f, cat, ocr_every = args
    cp = cache_path(f)
    if os.path.exists(cp): return key, cp, "cached"
    try:
        os.nice(19)
    except Exception: pass
    try:
        r = M.measure(f, PROMPT.get(cat, "the product"), ocr_every=ocr_every, do_clip=ocr_every > 0)
        r["_key"] = key; r["_file"] = f
        json.dump(r, open(cp, "w"), default=float)
        return key, cp, "ok"
    except Exception as e:
        return key, None, f"err {e}"

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--sources", default="own,external,viral_research,reference_library,library")
    ap.add_argument("--procs", type=int, default=3)
    a = ap.parse_args()
    os.makedirs(CACHE, exist_ok=True)
    df = pd.read_csv(f"{REPO}/private/corpus/corpus.csv")
    jobs = []
    for s in a.sources.split(","):
        for r in df[(df.source == s) & df.file.notna()].itertuples():
            if os.path.exists(r.file): jobs.append((r.key, r.file, r.category, 0 if s == "library" else 1.0))
    print(len(jobs), "videos", flush=True)
    with Pool(a.procs) as p:
        for i, (k, cp, st) in enumerate(p.imap_unordered(job, jobs), 1):
            print(i, k, st, flush=True)
