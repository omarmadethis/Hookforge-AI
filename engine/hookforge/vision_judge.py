"""D33 absurd-failure JUDGE (Omar 2026-10-18 10:35 PM PT: "use your own vision QA (CLIP fidelity plus contact-sheet checks) as the
absurd-failure judge"). Decides automatically, per raw generation, whether one absurd failure is CERTAIN (>= 0.9) -> qa.reroll_decision.

Signals (all measured, nothing generated):
  * CLIP fidelity (open_clip ViT-B-32 laion2b, cached): frame embeddings vs per-product reference banks built from Omar's OWN posted reels
    (learning/vision/refs_<product>.npz, private). own = p90 over frames of max cosine to the planned product's bank; other = same vs every other
    product's bank; scene = max cosine to ALL own banks (is this an own-style home/store scene at all).
  * contact-sheet pixel checks on the 2 fps sheet: blank/black frames, frozen (still image) clips, 9:16 aspect, packed hard cut.
Thresholds are CALIBRATED leave-one-reel-out on the own corpus (calibrate()) and stored in learning/vision/calibration.json:
  a check only reaches 0.95 ("certain") outside the range EVERY genuine own reel fell in (minus a margin); in between it reports
  a scaled confidence < 0.9, which reroll_decision ships/escalates instead of re-rolling (D33).
Not certifiable by these signals (confidence capped at 0.6 -> never auto re-roll): mangled_person_or_limbs, product_deformed, wrong_colour, hook_unusable(text)."""
import os, sys, json, glob, re, numpy as np
from .config import REPO, REROLL

VDIR = os.path.join(REPO, "learning", "vision"); CAL = os.path.join(VDIR, "calibration.json")
_PF = os.path.join(REPO, "tools", "preflight")
if _PF not in sys.path: sys.path.insert(0, _PF)
CAP_UNCERTIFIABLE = 0.6

def _clip():
    import torch; torch.set_num_threads(2)
    import product_fidelity; return product_fidelity

def _emb_frames(path, fps=2.0):
    from PIL import Image; import _frames
    fr, dur = _frames.frames(path, fps, 360)
    if not fr: return np.zeros((0, 512), np.float32), [], dur
    return _clip().embed([Image.fromarray(f) for _, f in fr]), fr, dur

def _own_reels():
    import pandas as pd
    from .worlds import WORLDS
    c = pd.read_csv(os.path.join(REPO, "private", "corpus", "corpus.csv"), low_memory=False, dtype=str)
    o = c[c.source == "own"].copy(); px = os.path.join(REPO, "data", "features", "proxies")   # read-only use of the features worker's proxies
    names = os.listdir(px) if os.path.isdir(px) else []
    pmap = {n.lower(): k for k, v in WORLDS.items() for n in v.get("corpus_products", [])}
    rows = []
    for _, r in o.iterrows():
        pk = pmap.get(str(r["product"]).lower()); path = None
        for v in (r.get("file"), r.get("reel_id"), r.get("url")):
            if not isinstance(v, str): continue
            if os.path.isfile(v): path = v; break
            for i in re.findall(r"[0-9]{15,17}|[A-Za-z0-9_-]{11}", v):
                hit = [n for n in names if i in n]
                if hit: path = os.path.join(px, hit[0]); break
            if path: break
        if pk and path: rows.append(dict(key=r["key"], product=pk, views=float(r.get("views") or 0), path=path))
    return rows

def build_refs(max_reels=8, log=print):
    """Embed every own reel once (cached in learning/vision/own_emb.npz) and write per-product banks from the top-viewed reels."""
    os.makedirs(VDIR, exist_ok=True); cache = os.path.join(VDIR, "own_emb.npz")
    E = dict(np.load(cache, allow_pickle=True)) if os.path.exists(cache) else {}
    rows = _own_reels()
    for r in rows:
        if r["key"] in E: continue
        try: e, _, _ = _emb_frames(r["path"]); E[r["key"]] = e; log("emb", r["key"], len(e))
        except Exception as ex: log("skip", r["key"], ex)
    np.savez(cache, **E)
    json.dump(rows, open(os.path.join(VDIR, "own_reels.json"), "w"), indent=0)
    for pk in sorted({r["product"] for r in rows}):
        top = sorted([r for r in rows if r["product"] == pk and r["key"] in E], key=lambda r: -r["views"])[:max_reels]
        np.savez(os.path.join(VDIR, f"refs_{pk}.npz"), emb=np.concatenate([E[r["key"]] for r in top]), keys=np.array([r["key"] for r in top]),
                 owner=np.concatenate([[r["key"]] * len(E[r["key"]]) for r in top]))
    return rows, E

def _banks(exclude_key=None):
    B = {}
    for p in glob.glob(os.path.join(VDIR, "refs_*.npz")):
        z = np.load(p, allow_pickle=True); m = z["owner"] != exclude_key
        if m.sum(): B[os.path.basename(p)[5:-4]] = z["emb"][m]
    return B

def signals(F, product, banks):
    if len(F) == 0: return dict(own=0.0, other=0.0, other_product=None, scene=0.0)
    q = lambda S: float(np.quantile(S, 0.9))
    own = q((F @ banks[product].T).max(1)) if product in banks else float("nan")
    oth = {k: q((F @ b.T).max(1)) for k, b in banks.items() if k != product}
    best = max(oth, key=oth.get) if oth else None
    scene = q(np.max(np.stack([(F @ b.T).max(1) for b in banks.values()]), 0))
    return dict(own=round(own, 4), other=round(oth.get(best, 0.0), 4), other_product=best, scene=round(scene, 4), margin=round(own - oth.get(best, 0.0), 4))

def pixel_checks(fr):
    if not fr: return dict(blank_share=1.0, motion=0.0)
    A = np.stack([f.astype(np.float32).mean(2) for _, f in fr])
    blank = float(np.mean([(a.mean() < 12) or (a.std() < 4) for a in A]))
    motion = float(np.mean(np.abs(np.diff(A, axis=0)))) if len(A) > 1 else 0.0
    return dict(blank_share=round(blank, 3), motion=round(motion, 3))

def calibrate(neg_glob=None, n_neg=40, log=print):
    """Leave-one-reel-out on own reels: genuine distribution of own / margin / scene / motion / blank. Thresholds sit below the genuine minimum
    minus a margin, so no genuine own reel would ever be judged 'certain'. Optional negatives (non-own reference videos) give a flag rate."""
    rows, E = build_refs(log=log); G = []
    for r in rows:
        if r["key"] not in E or not len(E[r["key"]]): continue
        s = signals(E[r["key"]], r["product"], _banks(exclude_key=r["key"]))
        G.append(dict(key=r["key"], product=r["product"], **s))
    import pandas as pd
    g = pd.DataFrame(G); M = 0.03
    th = dict(missing_own=round(float(g.own.min()) - M, 4), wrong_margin=round(float(g.margin.min()) - M, 4), scene=round(float(g.scene.min()) - M, 4),
              frozen_motion=0.4, blank_share=0.5, margin=M)
    # pixel checks on a sample of genuine reels (must never trip)
    pix = []
    for r in rows[:: max(1, len(rows) // 20)]:
        try:
            import _frames; fr, _ = _frames.frames(r["path"], 2.0, 180); pix.append(dict(key=r["key"], **pixel_checks(fr)))
        except Exception: pass
    neg = []
    if neg_glob:
        import random; vids = sorted(glob.glob(neg_glob)); random.Random(7).shuffle(vids)
        for v in vids[:n_neg]:
            try:
                F, fr, _ = _emb_frames(v)
                for pk in ("grinch_robe", "merryfire", "brickhood_mask"):
                    s = signals(F, pk, _banks()); neg.append(dict(video=os.path.basename(v), as_product=pk, **s, **judge_signals(s, pixel_checks(fr), th)))
            except Exception as ex: log("neg skip", v, ex)
    rep = dict(asof=__import__("datetime").datetime.now(__import__("zoneinfo").ZoneInfo("America/Los_Angeles")).isoformat(timespec="seconds"),
               n_genuine=len(g), thresholds=th,
               genuine=dict(own=g.own.describe().round(4).to_dict(), margin=g.margin.describe().round(4).to_dict(), scene=g.scene.describe().round(4).to_dict()),
               genuine_certain_flags=int(sum(any(f["confidence"] >= 0.9 for f in judge_signals(dict(x), dict(blank_share=0, motion=5), th)["findings"]) for x in G)),
               pixel_genuine=pix, negatives_n=len(neg),
               negatives_flagged_certain=int(sum(any(f["confidence"] >= 0.9 for f in n["findings"]) for n in neg)) if neg else None)
    g.to_csv(os.path.join(VDIR, "genuine_loo.csv"), index=False)
    if neg: pd.DataFrame([{k: v for k, v in n.items() if k != "findings"} | dict(findings="; ".join(f"{f['failure']}:{f['confidence']}" for f in n["findings"])) for n in neg]).to_csv(os.path.join(VDIR, "negatives.csv"), index=False)
    json.dump(rep, open(CAL, "w"), indent=1)
    return recalibrate(log)

def _conf(x, t, lo):
    """0.95 below threshold t; linear 0.5 -> 0.85 between the genuine floor `lo` and t (never certain inside the genuine range)."""
    if x < t: return 0.95
    if x < lo: return round(0.5 + 0.35 * (lo - x) / max(1e-6, lo - t), 2)
    return 0.0

def per_product(g, M=0.03, q=0.05):
    """Per-product thresholds: min(product's genuine minimum, global 5th percentile) - margin. The global floor keeps products with
    only 2-3 own reels (near-duplicate banks) from getting thresholds so tight that a fresh generation would be 'certain'-failed."""
    gq = {k: float(g[k].quantile(q)) for k in ("own", "margin", "scene")}; out = {}
    for pk, x in g.groupby("product"):
        out[pk] = dict(missing_own=round(min(float(x.own.min()), gq["own"]) - M, 4), wrong_margin=round(min(float(x.margin.min()), gq["margin"]) - M, 4),
                       scene=round(min(float(x.scene.min()), gq["scene"]) - M, 4), n=int(len(x)))
    return out

def recalibrate(log=print):
    """Recompute thresholds from the stored genuine LOO + negatives signals (no re-embedding)."""
    import pandas as pd
    g = pd.read_csv(os.path.join(VDIR, "genuine_loo.csv")); rep = json.load(open(CAL)); th = rep["thresholds"]
    th["per_product"] = per_product(g, th.get("margin", 0.03))
    G = g.to_dict("records")
    rep["genuine_certain_flags"] = int(sum(any(f["confidence"] >= 0.9 for f in judge_signals(dict(x), dict(blank_share=0, motion=5), th, x["product"])["findings"]) for x in G))
    npth = os.path.join(VDIR, "negatives.csv")
    if os.path.exists(npth):
        n = pd.read_csv(npth); rows = []
        for x in n.to_dict("records"):
            fs = judge_signals(dict(x), dict(blank_share=0, motion=5), th, x["as_product"])["findings"]
            rows.append(dict(video=x["video"], as_product=x["as_product"], certain=";".join(f["failure"] for f in fs if f["confidence"] >= 0.9)))
        r = pd.DataFrame(rows); rep["negatives_flagged_certain"] = int((r.certain != "").sum()); rep["negatives_certain_by_failure"] = r.certain[r.certain != ""].value_counts().to_dict()
        r.to_csv(os.path.join(VDIR, "negatives_judged.csv"), index=False)
    rep["recalibrated_pt"] = __import__("datetime").datetime.now(__import__("zoneinfo").ZoneInfo("America/Los_Angeles")).isoformat(timespec="seconds")
    json.dump(rep, open(CAL, "w"), indent=1); return rep

def judge_signals(s, px, th, product=None):
    f = []; M = th.get("margin", 0.03)
    if product and product in (th.get("per_product") or {}): th = dict(th, **th["per_product"][product])
    if px.get("blank_share", 0) >= th["blank_share"]: f.append(dict(failure="hook_unusable", confidence=0.95, note=f"blank/black frames {px['blank_share']:.0%}"))
    if px.get("motion", 9) < th["frozen_motion"]: f.append(dict(failure="hook_unusable", confidence=0.9, note=f"frozen clip (mean frame diff {px['motion']})"))
    if s.get("scene") is not None and (c := _conf(s["scene"], th["scene"], th["scene"] + M)): f.append(dict(failure="scene_unrelated", confidence=c, note=f"scene sim {s['scene']} (cert < {th['scene']})"))
    if (c := _conf(s["own"], th["missing_own"], th["missing_own"] + M)) and s.get("other", 0) < th["missing_own"] + M:
        f.append(dict(failure="product_missing", confidence=c, note=f"own-product CLIP p90 {s['own']} (cert < {th['missing_own']})"))
    elif (c := _conf(s.get("margin", 1), th["wrong_margin"], th["wrong_margin"] + M)) and s.get("margin", 1) < 0:
        f.append(dict(failure="wrong_product", confidence=c, note=f"looks more like {s.get('other_product')} (margin {s.get('margin')}, cert < {th['wrong_margin']})"))
    return dict(findings=f)

def judge(clip, product, gen_id="B", packed=True, context="", attempts_so_far=0, log=True, raw_rep=None):
    """The D33 judge: returns the single most certain finding and the reroll_decision record (logged)."""
    from . import qa
    th = json.load(open(CAL))["thresholds"]   # incl. per_product (recalibrate())
    F, fr, dur = _emb_frames(clip); s = signals(F, product, _banks()); px = pixel_checks(fr)
    finds = judge_signals(s, px, th, product)["findings"]
    rep = raw_rep or qa.raw_gen_checks(clip, packed=packed)
    for x in rep.get("d33_findings", []):
        if x["failure"] in ("mangled_person_or_limbs", "product_deformed", "wrong_colour"): x["confidence"] = min(x["confidence"], CAP_UNCERTIFIABLE)
        finds.append(x)
    absurd = [x for x in finds if x["failure"] in REROLL["absurd_failures"]]
    top = max(absurd, key=lambda x: x["confidence"]) if absurd else (finds[0] if finds else dict(failure=None, confidence=0.0, note="clean"))
    dec = qa.reroll_decision(gen_id, dict(top, model=""), attempts_so_far=attempts_so_far, log=log, context=context)
    return dict(clip=os.path.basename(clip), product=product, signals=s, pixels=px, findings=finds, decision=dec, contact_sheet=rep.get("contact_sheet"))
