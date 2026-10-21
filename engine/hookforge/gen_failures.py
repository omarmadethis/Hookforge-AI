"""Generation failure memory (D42, wired 2026-10-18 ~10:10 PM PT; Omar's 10:00 PM go-ahead).
Ledger of every generation attempt -> outcome class -> failed->working prompt pairs (minimal word diff) -> learned rules
(model family, block class, trigger -> fix) -> pre-flight linter run on every prompt BEFORE any generation.

Files (learning/gen_failures/): ledger.csv (one row per attempt), pairs.csv, rules.csv, failure_rate.csv.
Outcomes: ok / misgen / nsfw / ip / param / preset / credits / pending / other.
  misgen is only ever set by a human or the QA re-roll log (log_attempt(outcome="misgen", cause=...)); the backfill
  cannot see misgens, it only flags 'resubmitted' candidates.
Rule status: 'candidate' (auto word seen in 1 fix pair - stored, NOT linted until it recurs); 'promoted' (>=2 independent pairs, or a deterministic API param error) -> the linter reports it in QA and
  the pre-flight gate shows it as FIX; 'hypothesis' (1 pair) -> reported as INFO only. Nothing here ever blocks a plan
  by itself except param rules (the API would reject the job anyway)."""
import os, re, csv, json, difflib, datetime
import pandas as pd
from zoneinfo import ZoneInfo
from .config import REPO

D = os.path.join(REPO, "learning", "gen_failures")
SRC = "/workspace/team/mac/claude/hf_generations.csv"
PT = ZoneInfo("America/Los_Angeles")
FAMILY = lambda m: (lambda m: "seedance" if "seedance" in m else "kling" if "kling" in m else "gpt_image" if "gpt_image" in m
                    else "ad_multiplier" if "ad_multiplier" in m else "image_other" if any(k in m for k in ("banana", "seedream", "soul", "flux")) else m)(str(m))
STOP = set("a an the and or of to in on with at by for from is are be it its this that same exact exactly only one into as".split())

def classify(status, issue):
    s = str(status or ""); i = str(issue or "")
    last = s.split(";")[-1]
    if "nsfw" in s: return "nsfw"
    if "ip_detected" in s: return "ip"
    if "Out of credits" in i: return "credits"
    if "Preset" in i and "recommended" in i or i == "preset_notice": return "preset" if last != "completed" else "ok"
    if "422" in i or "Unknown media role" in i or "validation" in i: return "param"
    if last == "completed": return "ok"
    if last in ("in_progress", "queued", "?"): return "pending"
    if s in ("", "nan"): return "unknown"          # batch submissions: per-job status not captured in the export
    return "other"

def _words(t): return [w for w in re.findall(r"[a-z0-9'@\-]+", str(t).lower())]

def backfill():
    os.makedirs(D, exist_ok=True)
    g = pd.read_csv(SRC)
    g["outcome"] = [classify(a, b) for a, b in zip(g.final_status, g.submit_issue)]
    g["model"] = g.model.fillna("unknown").astype(object).astype(str); g["family"] = [FAMILY(m) for m in g.model]
    g["ts"] = pd.to_datetime(g.ts, utc=True, errors="coerce")
    g["ts_pt"] = g.ts.dt.tz_convert(PT).dt.strftime("%Y-%m-%d %H:%M PT")
    g["cause"] = g.submit_issue.fillna("").astype(str).str.extract(r'"error":"([^"]{0,160})', expand=False).fillna(g.submit_issue.fillna("").astype(str).str[:160])
    g = g.sort_values("ts").reset_index(drop=True)
    g["attempt_id"] = ["bf%04d" % i for i in range(len(g))]
    # resubmitted-after-ok candidates (possible misgens; never auto-labelled misgen)
    g["resubmitted"] = False
    for (_, _), grp in g.groupby(["session", "model"]):
        idx = grp.index.tolist()
        for a, b in zip(idx, idx[1:]):
            if g.at[a, "outcome"] == "ok" and (g.at[b, "ts"] - g.at[a, "ts"]).total_seconds() < 1800 and \
               difflib.SequenceMatcher(None, _words(g.at[a, "prompt"]), _words(g.at[b, "prompt"])).ratio() > 0.6:
                g.at[a, "resubmitted"] = True
    led = g[["attempt_id", "ts_pt", "project", "session", "model", "family", "mode", "resolution", "duration", "outcome", "cause", "resubmitted", "prompt"]].copy()
    led["source"] = "backfill:hf_generations.csv"; led["fix_of"] = ""
    lp = os.path.join(D, "ledger.csv")   # keep live/QA rows (attempt_id lv*) across backfills - they exist only in the ledger
    live_rows = pd.read_csv(lp, dtype=str) if os.path.exists(lp) else pd.DataFrame()
    live_rows = live_rows[live_rows.attempt_id.astype(str).str.startswith("lv")] if len(live_rows) else live_rows
    # failed -> working pairs: same session (else project) + same family, next ok attempt within 6 h, prompt similarity >= 0.5
    pairs = []
    for i, r in led[led.outcome.isin(["nsfw", "ip", "param", "preset"])].iterrows():
        t0 = g.at[i, "ts"]
        cand = led[(led.index > i) & (led.family == r.family) & (led.outcome == "ok") & ((led.session == r.session) | (led.project == r.project))]
        cand = cand[[(g.at[j, "ts"] - t0).total_seconds() < 6 * 3600 for j in cand.index]]
        best = None
        for j, c in cand.head(12).iterrows():
            sim = difflib.SequenceMatcher(None, _words(r.prompt), _words(c.prompt)).ratio()
            if sim >= 0.5 and (best is None or sim > best[0]): best = (sim, j)
        if best:
            c = led.loc[best[1]]; a, b = _words(r.prompt), _words(c.prompt)
            rem, add = [], []
            for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b).get_opcodes():
                if op in ("delete", "replace"): rem += a[i1:i2]
                if op in ("insert", "replace"): add += b[j1:j2]
            pairs.append(dict(failed=r.attempt_id, working=c.attempt_id, family=r.family, block=r.outcome, similarity=round(best[0], 2),
                              removed=" ".join(w for w in rem if w not in STOP)[:300], added=" ".join(w for w in add if w not in STOP)[:300],
                              failed_prompt=str(r.prompt)[:1500], working_prompt=str(c.prompt)[:1500]))
    pd.DataFrame(pairs).to_csv(os.path.join(D, "pairs.csv"), index=False)
    led.loc[led.attempt_id.isin([p["working"] for p in pairs]), "fix_of"] = led.attempt_id.map({p["working"]: p["failed"] for p in pairs})
    (pd.concat([led, live_rows], ignore_index=True) if len(live_rows) else led).to_csv(lp, index=False)
    rules = learn_rules(pairs, led)
    fr = led[~led.outcome.isin(["pending", "unknown"])].groupby(["family", "outcome"]).size().unstack(fill_value=0)
    fr["n"] = fr.sum(axis=1); fr["fail_rate"] = (1 - fr.get("ok", 0) / fr.n).round(3); fr.to_csv(os.path.join(D, "failure_rate.csv"))
    return dict(attempts=len(led), outcomes=led.outcome.value_counts().to_dict(), pairs=len(pairs), rules=len(rules),
                promoted=sum(r["status"] == "promoted" for r in rules), resubmitted_candidates=int(led.resubmitted.sum()))

# Deterministic API-parameter rules (seen as 422/validation errors in the ledger; the API rejects these every time).
PARAM_RULES = [
    dict(rule_id="GF-P1", family="seedance", block="param", trigger=r"mode 't2v'.*reference|t2v_with_reference",
         fix="use i2v / omni_reference mode when a start image or reference media is attached", status="promoted", kind="param"),
    dict(rule_id="GF-P2", family="*", block="param", trigger=r"media role:? ?mask", fix="'mask' is not a valid media role; use image/start_image/reference roles",
         status="promoted", kind="param"),
]

GENERIC = set("shot shots close-up close-ups extreme current inside blurred every including both hanging frame camera video image "
              "background clip throughout woman man woman's girl scene end start".split())

# Curated from the failed->working pairs above (each fix was confirmed by a working re-run). Thin evidence -> statuses as stated.
CURATED = [
    dict(rule_id="GF-C1", family="*", block="ip", trigger=r"\b(walmart|costco|claire'?s|home depot|ikea|best buy|bath ?& ?body works)\b|\btarget (store|aisle|shelf|shelves|bag|cart|logo)",
         fix="name no real retailer: 'unbranded big-box store, plain shelving, no logos or store names'", status="promoted", kind="curated",
         evidence="ad_multiplier ip pairs: Walmart/Target aisle -> 'unbranded big-box retail, no logos' worked; Claire's -> Claire worked (2 pairs)"),
    dict(rule_id="GF-C2", family="*", block="nsfw", trigger=r"half-exposed|exposed (skin|chest|legs)|undress|lingerie|in bed together|tight (rope|clothes)",
         fix="state 'both fully dressed' (pyjamas/loungewear), sitting upright, no bed framing", status="hypothesis", kind="curated",
         evidence="gpt_image nsfw pair: 'bedroom ... half-exposed' -> 'both fully dressed in pyjamas ... sit upright' worked (1 pair)"),
    dict(rule_id="GF-C3", family="seedance", block="nsfw", trigger=r"(lighter|flame).{0,60}mouth|mouth.{0,60}(lighter|flame)",
         fix="don't put a flame/lighter at a character's mouth cutout; show the flame from top-down or at the base", status="hypothesis", kind="curated",
         evidence="seedance nsfw pair: lighter into the mug's mouth cutout -> top-down stirring shot worked; 'mouth' in 7/21 blocked vs 8/63 ok seedance prompts"),
    dict(rule_id="GF-C4", family="seedance", block="nsfw", trigger=r"grinch (holiday )?mugs? .{0,40}(shelf|display)|full of .{0,20}grinch",
         fix="describe the product display as plain white gift boxes / 'the mug from the reference'; avoid naming the character on retail displays", status="hypothesis", kind="curated",
         evidence="seedance nsfw pair: 'shelf display full of christmas grinch holiday mugs' -> 'pallet of white gift boxes' worked (1 pair). 'grinch' alone is NOT a trigger (d7bf7598 recreate with 'grinch hood' completed)"),
    dict(rule_id="GF-C5", family="*", block="preset", trigger=r"\b(glow|glowing|dark|night)\b",
         fix="not a content block: Higgsfield may answer with a preset recommendation ('IN THE DARK' / 'NIGHT VISION') instead of a job; the runner must decline it and resubmit the same prompt",
         status="hypothesis", kind="runner",
         evidence="'glow' in 7/22 seedance and 11/42 kling preset notices vs 3/63 and 5/32 ok prompts"),
    dict(rule_id="GF-C6", family="seedance", block="nsfw", trigger=r"\bkids?\b.{0,80}\b(react|pyjamas|pajamas)\b|\b(two|young) kids\b",
         fix="keep children out of close/hero framing in video gens: adults react in the foreground, kids only small in the background (or no kids); start frame without children in pyjamas",
         status="hypothesis", kind="curated",
         evidence="mg-tvn-001 B3 (2026-10-18 23:31 PT): seedance 720p NSFW on 'PROOF ... kids react' with a start frame of two small children in pyjamas by the lit tree; B1/B2 with the same family passed (kids at distance / from behind). 1 case, no working pair yet"),
    # ---- D61: Omar's review of mg-tvn-001 (2026-10-19 ~8:00 AM PT): "horrible and unusable". Promoted = FIX in the pre-flight lint.
    dict(rule_id="GF-Q1", family="*", block="quality", trigger=r"\b(look|stare|smil|grin|pos|fac)\w*\s+(straight\s+|directly\s+)?(at|into|to|toward)\s+(the\s+)?(camera|lens)\b",
         fix="nobody faces the camera unless the reference reel does; give each person a task aimed at the tree/box/each other (logic.LG1 + vision facing_camera)",
         status="promoted", kind="curated", evidence="mg-tvn-001 H: whole family sat on the couch staring at the camera (YuNet: 6 frontal faces 0-2.5 s)"),
    dict(rule_id="GF-Q2", family="*", block="quality", trigger=r"$^", fix="then-cards == problem scenes: 1 problem scene = 1 caption, then 'Vs... ⏰', then the solution card over all afters (textcards.check_cards)",
         status="promoted", kind="edit", evidence="mg-tvn-001: 'Christmas 2024' + 'And Christmas 2025' over ONE problem scene"),
    dict(rule_id="GF-Q3", family="*", block="quality", trigger=r"\byay\b|\bwhoosh|\bswoosh|\bboing|cartoon sound|(?<!no )(?<!no added )sound effects? (of|:)|yells? \W?yeah",
         fix="D63: natural ambient sound only (real voices, some cheering, gasps, action sounds); no added SFX/whooshes/cartoon sounds/inserted YAY/music; QA audio check; key real sound boosted 2-4x in the edit",
         status="promoted", kind="curated", evidence="mg-tvn-001 B1/B2: loud generated 'YAY' (prompt said 'Natural sound only: click, gasps, kids cheering')"),
    dict(rule_id="GF-Q4", family="*", block="quality", trigger=r"$^", fix="Apple iOS emoji only: textcards.render_card (Apple PNG overlays); never Noto",
         status="promoted", kind="edit", evidence="mg-tvn-001 final burned Noto Color Emoji"),
    dict(rule_id="GF-Q5", family="*", block="quality", trigger=r"hanging/placing tree lights|hands on the tree lights",
         fix="MerryGlow install = man on a silver step ladder drops the topper + ring stack on the tip and the rings unfold slowly down around the tree (MG-01 2d4f23c9 / OMAR_REF 7.17-9.92 s)",
         status="promoted", kind="curated", evidence="mg-tvn-001 B1 INSTALL: generic hands-placing-lights shot, nothing like our reels"),
    dict(rule_id="GF-Q6", family="*", block="quality", trigger=r"bursts into colou?r - the reveal|hero wide of the whole effect",
         fix="each after shot names its animation (what moves) and shows a DIFFERENT design (logic.LG4 + vision lights_motion / afters_not_distinct)",
         status="promoted", kind="curated", evidence="mg-tvn-001 B2/B3 afters: lights not animated (bright motion 1.46 / 2.51 vs MG-01 train 19.7), afters look the same"),
    dict(rule_id="GF-Q7", family="*", block="quality", trigger=r"$^", fix="RECREATE is the default: plan from refs/recreate/<product>.json (shot list of a posted winner); deviate only in the 20 % innovation slot",
         status="promoted", kind="plan", evidence="mg-tvn-001 planned from the F04 template instead of MG-01: 'it should look like what he's already posted'"),
    dict(rule_id="GF-Q8", family="*", block="quality", trigger=r"family of (four|five|six)[^.]{0,80}\bon the couch\b|\b(sit|sits|sitting)\b[^.]{0,40}\bstar(e|es|ing)\b",
         fix="LOGIC step: every person has a motivated action (logic.LG2): who does what, to what, why",
         status="promoted", kind="curated", evidence="mg-tvn-001 H still: 'five family members in sweaters on the couch' with no action -> robotic staring"),
    dict(rule_id="GF-Q9", family="*", block="quality", trigger=r"$^", fix="CapCut text = first Preset style + stroke thickness 45 (JSON: fill #FFFFFF, border/stroke #000000 width 0.09, SystemFont en.ttf, size 15), clip scale 1.0, y 0.582; box render = Montserrat wght 560, stroke 0.091*px",
         status="promoted", kind="edit", evidence="mg-tvn-001 draft used card scales 0.88/1.2 and y 0.62; box render stroke/weight off vs Omar's reel"),
    dict(rule_id="GF-AF1", family="*", block="audience", trigger=r"(?i)\bphonk\b|super slowed|slowed \+ reverb|brazilian funk", fix="Song = audience_fit.song_rank(<slug>): (a) proven on same/similar product > (b) trending with the buyers on their main platform > (c) reference format; never copy the reference reel's song by default; phonk globally banned",
         status="promoted", kind="audience", evidence="POST-MORTEM 2026-10-19: phonk picked for TrumpGlow because the Hello Kitty reference reels used it; Omar: 'never ever use phonk, it attracts indians' / 'you really think trumpies listen to phonk' - buyers are US Trump supporters on Facebook"),
    dict(rule_id="GF-AF2", family="*", block="audience", trigger=r"$^", fix="Emoji only from audience/<slug>.yaml emoji_allowed (meaning in that niche), rendered as Apple iOS PNGs; Android/Noto/Twemoji = fail",
         status="promoted", kind="audience", evidence="mg-tvn-001 used Noto emoji (D61 #4); Omar: Apple iOS emojis only"),
    dict(rule_id="GF-AF3", family="*", block="audience", trigger=r"$^", fix="Every card + caption needs a caption_proof match or a proven hook source in its niche; US spelling; profile voice/slang",
         status="promoted", kind="audience", evidence="Omar 2026-10-19: 'song matching, emoji matching, caption matching it all needs to fit in that audience/niche always. this isnt amateur hour'"),
]

def learn_rules(pairs, led):
    """Trigger words = removed in the failed->working fix AND over-represented in blocked prompts of that family."""
    rules = list(PARAM_RULES) + list(CURATED); k = 0
    pdf = pd.DataFrame(pairs)
    if len(pdf):
        for (fam, blk), grp in pdf.groupby(["family", "block"]):
            if blk not in ("nsfw", "ip"): continue
            cnt = {}
            for rem, fid in zip(grp.removed, grp.failed):
                for w in set(str(rem).split()):
                    if len(w) > 2 and not w.isdigit(): cnt.setdefault(w, set()).add(fid)
            fam_led = led[led.family == fam]; bad = fam_led[fam_led.outcome == blk]; ok = fam_led[fam_led.outcome == "ok"]
            for w, fids in sorted(cnt.items(), key=lambda x: -len(x[1])):
                rx = r"\b" + re.escape(w) + r"\b"
                pb = bad.prompt.astype(str).str.lower().str.contains(rx).mean() if len(bad) else 0
                po = ok.prompt.astype(str).str.lower().str.contains(rx).mean() if len(ok) else 0
                nb = int(bad.prompt.astype(str).str.lower().str.contains(rx).sum())
                if pb < max(0.15, 2 * po) or w in GENERIC: continue   # must be over-represented in blocked prompts
                promoted = len(fids) >= 2 and nb >= 3 and pb >= 2.5 * max(po, 0.01)
                k += 1
                adds = " ".join(grp[grp.failed.isin(fids)].added.astype(str).head(2))[:160]
                rules.append(dict(rule_id=f"GF-{blk.upper()}{k:02d}", family=fam, block=blk, trigger=rx,
                                  fix=f"remove/rephrase '{w}' (working fixes added: {adds or '-'})",
                                  status="promoted" if promoted else "candidate", kind="word",
                                  evidence=f"{len(fids)} pair(s); in {pb:.0%} of {blk} vs {po:.0%} of ok {fam} prompts"))
                if k > 60: break
    pd.DataFrame(rules).to_csv(os.path.join(D, "rules.csv"), index=False)
    return rules

_RC = {}
def rules():
    """D133: cached by rules.csv mtime/size (read 90x per e2e run); copies so callers can't mutate the cache."""
    p = os.path.join(D, "rules.csv")
    if not os.path.exists(p): return list(PARAM_RULES)
    st = os.stat(p); k = (st.st_mtime_ns, st.st_size)
    if _RC.get("k") != k: _RC.update(k=k, v=pd.read_csv(p).fillna("").to_dict("records"))
    return [dict(r) for r in _RC["v"]]

def lint(prompt, model="seedance_2_5", mode=None):
    """Pre-flight linter: run on every prompt before any generation. Returns hits; promoted -> FIX, hypothesis -> INFO."""
    fam = FAMILY(str(model)); text = f"{prompt} mode:{mode or ''}".lower(); hits = []
    for r in rules():
        if r["family"] not in ("*", fam) or r["status"] == "candidate": continue   # candidates = 1-pair auto words: collected, not linted
        if re.search(r["trigger"], text, re.I):
            hits.append(dict(rule_id=r["rule_id"], status=r["status"], block=r["block"], trigger=r["trigger"].replace("\\b", ""), fix=r["fix"],
                             severity="FIX" if r["status"] == "promoted" else "INFO"))
    return dict(model=model, family=fam, hits=hits, ok=not any(h["severity"] == "FIX" for h in hits))

def log_attempt(project, model, prompt, outcome, cause="", mode="", resolution="", duration="", fix_of="", source="live", job_id=""):
    """Append one live attempt (called by the generation runner and by qa re-roll logging)."""
    p = os.path.join(D, "ledger.csv"); new = not os.path.exists(p)
    row = dict(attempt_id="lv" + datetime.datetime.now(PT).strftime("%Y%m%d%H%M%S%f")[:-3], ts_pt=datetime.datetime.now(PT).strftime("%Y-%m-%d %H:%M PT"),
               project=project, session=job_id, model=model, family=FAMILY(model), mode=mode, resolution=resolution, duration=duration,
               outcome=outcome, cause=cause, resubmitted=False, prompt=prompt, source=source, fix_of=fix_of)
    with open(p, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(row)); new and w.writeheader(); w.writerow(row)
    return row["attempt_id"]

if __name__ == "__main__":
    print(json.dumps(backfill(), indent=1, default=str))
