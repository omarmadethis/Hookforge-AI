"""D115 end-to-end DRY RUN for every product: concept -> plan -> gates -> quote -> CapCut draft -> post caption ->
Buffer route -> draft payload. Nothing is generated, uploaded or sent: no Higgsfield call, no Buffer call, no write to
learning/approvals, publish's queue or approval_queue. Output: learning/e2e_dryrun/<day>/<product>/ (report.json, capcut/,
buffer_payloads.json) + learning/e2e_dryrun/<day>/SUMMARY.json.
CapCut media are placeholder slates (one 4 s slate per planned gen, labelled with its id) so the draft opens with the
real cut list, text cards and song; swap the slates for the generated clips after an approved run."""
import os, json, datetime, subprocess, shutil, traceback
from zoneinfo import ZoneInfo
from .config import REPO
PT = ZoneInfo("America/Los_Angeles")
OUT = os.path.join(REPO, "learning", "e2e_dryrun")
from . import products as _products
PRODUCTS = _products.active()   # D117: retired products excluded; see config/products.json
MAC = "/Users/omar/Movies/CapCut/User Data/Projects/com.lveditor.draft"

SLATE_CACHE = os.path.join(REPO, ".cache", "slates")
def _slate(path, label):
    """D133: placeholder slates are cached by label (they were 85% of e2e time); copied, never regenerated."""
    if os.path.exists(path): return path
    import hashlib, shutil
    os.makedirs(SLATE_CACHE, exist_ok=True); c = os.path.join(SLATE_CACHE, hashlib.sha1(label.encode()).hexdigest()[:16] + ".mp4")
    if os.path.exists(c) and os.path.getsize(c) > 0: shutil.copyfile(c, path); return path
    _render_slate(c, label); shutil.copyfile(c, path); return path

def _render_slate(path, label):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "color=c=0x202020:s=1080x1920:d=4:r=30",
                    "-vf", f"drawtext=text='{label}':fontcolor=white:fontsize=96:x=(w-text_w)/2:y=(h-text_h)/2",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-map_metadata", "-1", path], check=True, timeout=120)
    return path

def capcut(plan, d, name):
    from . import capcut_export, music
    md = os.path.join(d, "slates"); os.makedirs(md, exist_ok=True)
    files = {g["id"]: _slate(os.path.join(md, f"{g['id']}.mp4"), f"{g['id']} (placeholder)") for g in plan["gens"]}
    shots, gen_t = [], {}
    for s in plan["shots"]:                     # each shot plays from its gen's slate at the gen-local time (trims from the plan)
        g = next(x for x in plan["gens"] if x["id"] == s["gen"]); tr = (g.get("trims") or {}).get(s["code"])
        cs = tr[0] if tr else gen_t.get(s["gen"], 0.0); dur = round(s["t1"] - s["t0"], 3)
        if cs + dur > 4.0: cs = max(0.0, 4.0 - dur)
        gen_t[s["gen"]] = cs + dur
        shots.append(dict(file=files[s["gen"]], clip_start=round(cs, 3), dur=dur, speed=1.0, clip_dur=4.0, w=1080, h=1920))
    mu = None; pick = ((plan.get("music") or {}).get("pick") or {})
    songs = json.load(open(os.path.join(REPO, "music", "songs.json")))
    key = pick.get("song"); norm = lambda x: str(x).replace("_", "").lower()
    key = key if key in songs else next((k for k in songs if key and norm(k) == norm(key)), None) or (music.canon(key) if key else None)
    if key in songs and os.path.exists(songs[key].get("file", "")):
        mu = dict(file=songs[key]["file"], offset=float(songs[key].get("in_point_s", pick.get("offset_s", 0)) or 0), dur_total=240, volume=1.0)
    ts = plan.get("text_style") or {}
    cp = dict(name=name, canvas=[1080, 1920], fps=30, clip_audio_volume=1.0, mac_draft_root=MAC, media_root_map=(md, f"{MAC}/{name}/media"),
              shots=shots, texts=[dict(t=c["t"], dur=c["dur"], text=c["text"], y=ts.get("capcut_y", 0.62), scale=c.get("scale")) for c in plan["text_cards"]], music=mu)
    cdir = capcut_export.export(cp, os.path.join(d, "capcut"))
    dst = os.path.join(cdir, "media"); shutil.rmtree(dst, ignore_errors=True); shutil.move(md, dst)
    return dict(dir=cdir, problems=capcut_export.verify(cdir), music=key if mu else None, music_missing=None if mu else (key or "no pick"))

def caption_for(product, plan, service, page_key=None, avoid=()):
    """Same caption path as publish.prepare_fb_all: per-page POC variant (caption_variants, D101) first, else fb_caption
    with sibling-page captions avoided (no two pages share a line). IG: plan caption with the real URL, else a SAY caption."""
    from . import fb_caption, publish, caption_variants
    pv = caption_variants.for_page(product, page_key) if page_key else None
    vp = dict(plan, caption_override=pv["caption"], caption_poc=pv["poc"]) if pv else plan
    if service == "facebook":
        c = fb_caption.generate(product, vp, platform="facebook", avoid=tuple(avoid)); txt, poc, body = c["text"], c.get("poc"), c["caption"]
    else:
        c = plan.get("caption") or {}; txt, poc = (c.get("text") if isinstance(c, dict) else c), (c.get("why") if isinstance(c, dict) else None)
        u = fb_caption.product_url(product)
        if "{url}" in (txt or "") and u: txt = txt.replace("{url}", u)
        if not txt or "{url}" in txt:      # D115: no product URL yet -> proven SAY caption instead of a dead {url}
            c = fb_caption.generate(product, vp, platform="instagram", avoid=tuple(avoid)); txt, poc = c["text"], c.get("poc")
        body = txt
    return dict(text=txt, body=body, poc=poc, problems=publish._caption_checks(txt))

def run_product(product, day, root):
    from . import concept_lab, approval_queue, gates, runner, routing, publish, political_lint
    d = os.path.join(root, product); os.makedirs(d, exist_ok=True); rep = dict(product=product, day=day.isoformat(), stages={}, breaks=[])
    def stage(name, ok, **kw): rep["stages"][name] = dict(ok=ok, **kw); (None if ok else rep["breaks"].append(name))
    old = approval_queue.DIR; approval_queue.DIR = os.path.join(d, "queue")          # dry run: never the real approval queue
    try: c = concept_lab.propose(product, day)
    finally: approval_queue.DIR = old
    if c.get("error"): stage("concept", False, error=c["error"]); return rep
    p = c["plan"]; stage("concept", True, id=c["id"], format=c["format"], hook=p["hook"]["text"])
    stage("plan", bool(p.get("gens")), gens=len(p["gens"]), setting=p.get("setting"))
    gr = gates.run_all(p); pl = political_lint.check(p)
    stage("gates", gr["ok"] and runner.preflight(p)["ok"], blocks=[b["msg"] for b in gr["blocks"]], warns=[w["msg"] for w in gr["warns"]][:6],
          political=pl if pl["applies"] else "n/a")
    q = p.get("quote") or {}; calls = runner.build_calls(p)
    stage("quote", q.get("total") == c["credits"] and sum(x.get("expected_credits", 0) for x in calls) == q.get("total"),
          credits=q.get("total"), calls=len(calls), calls_credits=sum(x.get("expected_credits", 0) for x in calls))
    try:
        cc = capcut(p, d, f"DRY_{day:%m%d}_{product}_{c['format']}"); stage("capcut", not cc["problems"], **cc)
    except Exception as e: stage("capcut", False, error=f"{type(e).__name__}: {e}", trace=traceback.format_exc()[-600:])
    try: r = routing.route(product)
    except routing.RouteRefused as e: r = dict(pages=[], refused=[dict(reason=str(e))])
    if not r["pages"]:                       # no connected Buffer page: not a code break - a template the agent fills once a page is connected
        reason = r["refused"] or "no Buffer page mapped (config/buffer_routing.json products[%s] is empty)" % product
        cap = caption_for(product, p, "facebook")
        tpl = dict(page=None, status="NEEDS_BUFFER_CHANNEL", reason=reason, caption=cap["text"], caption_problems=cap["problems"],
                   payload_template={"channelId": "<CONNECT_A_PAGE_IN_BUFFER>", "schedulingType": "automatic", "mode": "addToQueue", "saveToDraft": True,
                                     "text": cap["text"], "assets": [], "metadata": {"facebook": {"type": "reel"}}})
        json.dump([tpl], open(os.path.join(d, "buffer_payloads.json"), "w"), indent=1, ensure_ascii=False)
        rep["stages"]["route"] = dict(ok=None, blocked="NEEDS_BUFFER_CHANNEL", reason=reason); rep["needs"] = ["connect a Buffer page"]
        rep["stages"]["payload"] = dict(ok=None, template=True, caption_ok=not cap["problems"])
        json.dump(rep, open(os.path.join(d, "report.json"), "w"), indent=1, ensure_ascii=False, default=str)
        return rep
    stage("route", True, pages=[x["page"] for x in r["pages"]], refused=r["refused"])
    payloads, used = [], []
    for pg in r["pages"]:
        cap = caption_for(product, p, pg["service"], pg["page"], used); used.append(cap["body"])
        if cap["problems"] or not cap["text"]: stage(f"caption:{pg['page']}", False, **cap); continue
        pay = publish.build_payload(pg["channel"], pg["service"], cap["text"], video_url=None)
        pl2 = political_lint.check(dict(caption=cap["text"]), product)
        payloads.append(dict(page=pg["page"], name=pg["name"], namespace=pg["namespace"], tool="create_post (NOT CALLED)", status="DRY_RUN_DRAFT_PAYLOAD",
                             needs=["Omar approval (publish.approve)", "rendered video staged via deliver.stage/verify_staged", "public video_url"],
                             caption_poc=cap["poc"], political=pl2 if pl2["applies"] else "n/a", payload=pay))
        stage(f"caption:{pg['page']}", pl2["ok"], text=cap["text"])
    json.dump(payloads, open(os.path.join(d, "buffer_payloads.json"), "w"), indent=1, ensure_ascii=False)
    stage("payload", bool(payloads), n=len(payloads))
    txts = [" ".join(__import__("re").findall(r"[a-z0-9']+", x["payload"].get("text", "").split("#")[0].lower())) for x in payloads]   # D139: text, not hashtags
    stage("distinct_captions", len(set(txts)) == len(txts), n=len(txts))          # D118: every page gets its own caption
    json.dump(rep, open(os.path.join(d, "report.json"), "w"), indent=1, ensure_ascii=False, default=str)
    return rep

def run(day=None, products=None):
    day = day or datetime.datetime.now(PT).date(); root = os.path.join(OUT, day.isoformat()); os.makedirs(root, exist_ok=True)
    reps = []
    for pk in [p for p in (products or PRODUCTS) if _products.is_active(p)]:
        try: reps.append(run_product(pk, day, root))
        except Exception as e: reps.append(dict(product=pk, breaks=["crash"], error=f"{type(e).__name__}: {e}", trace=traceback.format_exc()[-800:]))
    s = dict(day=day.isoformat(), ran_pt=datetime.datetime.now(PT).isoformat(timespec="seconds"),
             products={r["product"]: (r.get("breaks") or ("OK, " + "; ".join(r["needs"]) if r.get("needs") else "OK")) for r in reps})
    json.dump(s, open(os.path.join(root, "SUMMARY.json"), "w"), indent=1)
    return s, reps
