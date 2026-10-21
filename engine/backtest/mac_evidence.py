"""Merge the Mac mining (team/mac) into Hookforge evidence.

Outputs
  private/evidence/prompts_ledger.csv   every recovered prompt (1,926) sanitized for casting, with reel_key joins from
                                        (a) the Mac CLIP matcher outcome and (b) CapCut draft clip placement; post_date; age
  learning/rules_core.csv               Omar's standing rules (verbatim, dated) + Hookforge resolutions; status + freshness scope
Run: cd engine && python3 -m backtest.mac_evidence
"""
import os, re, sys, json
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from hookforge.config import REPO, sanitize_casting, casting_violations

MAC = "/workspace/team/mac"

def reel_map():
    c = pd.read_csv(f"{REPO}/private/corpus/corpus.csv")
    m = {}
    for r in c.itertuples():
        rid = str(r.reel_id)
        for tok in re.findall(r"\d{12,}", rid): m[tok] = r.key
        m[rid] = r.key
    return c, m

def prompts():
    c, m = reel_map()
    p = pd.read_csv(f"{MAC}/out/prompts.csv")
    p["prompt"] = p.prompt.map(sanitize_casting)
    assert p.prompt.fillna("").map(lambda x: not casting_violations(x)).all()
    p["gen_id"] = p.job_ids.astype(str).str.extract(r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})")[0]
    def key_from(s):
        for tok in re.findall(r"\d{12,}", str(s)):
            if tok in m: return m[tok]
        return None
    p["reel_key_mac"] = [key_from(f"{a} {b}") for a, b in zip(p.posted_reel_match, p.outcome)]
    p["in_reel_mac"] = p.outcome.astype(str).str.contains(r"Mac-clip in posted reel|in posted", regex=True)
    cl = pd.read_csv(f"{REPO}/private/edits/edit_clips.csv")
    cl = cl[cl.gen_id.notna()]
    first = cl.sort_values("views", ascending=False).drop_duplicates("gen_id")
    p = p.merge(first[["gen_id", "draft", "reel_key", "variant_of", "slot", "t_start", "t_dur", "speed"]].rename(
        columns={"reel_key": "reel_key_capcut", "t_start": "capcut_t", "t_dur": "capcut_dur"}), on="gen_id", how="left")
    p["reel_key"] = p.reel_key_capcut.fillna(p.reel_key_mac.where(p.in_reel_mac))
    p["used_in_posted"] = p.reel_key.notna()
    p["join_source"] = (p.reel_key_capcut.notna().map({True: "capcut", False: ""}) + "+" + (p.reel_key_mac.notna() & p.in_reel_mac).map({True: "mac", False: ""})).str.strip("+")
    views = c.set_index("key").views; posted = c.set_index("key").posted_pt
    p["views"] = p.reel_key.map(views); p["post_date"] = p.reel_key.map(posted)
    p["gen_date"] = pd.to_datetime(p.ts_utc, errors="coerce", utc=True).dt.tz_convert("America/Los_Angeles").dt.date
    p["has_suffix"] = p.prompt.fillna("").str.lower().str.contains("shot on iphone 12")
    p["packed"] = p.prompt.fillna("").str.contains(r"HARD CUT|hard cut", regex=True)
    p["us_flag"] = p.prompt.fillna("").str.lower().str.contains("flag")
    p["scope"] = "craft"   # prompts are execution evidence: no recency decay (D28)
    os.makedirs(f"{REPO}/private/evidence", exist_ok=True)
    p.to_csv(f"{REPO}/private/evidence/prompts_ledger.csv", index=False)
    u = p[p.used_in_posted]
    print("prompts", len(p), "used in posted reels", len(u), "by source", u.join_source.value_counts().to_dict(),
          "reels", u.reel_key.nunique(), "with prompt text", u.prompt.notna().sum())
    return p

# Hookforge resolution per Omar rule (status: active | amended | overridden-by). Freshness: craft rules don't decay.
RESOLUTION = {
 "R02": ("active", "D32: suffix on EVERY prompt (video + stills); stills = 'iPhone photo of… Sharp, clean, realistic phone photo.' + suffix"),
 "R14": ("amended", "D33: auto re-roll only on absurd failures at >=0.9 confidence (max 1/shot), logged with reason+cost; minor flaws ship + are logged"),
 "R15": ("active", "D18: every plan prints credits per video; budget 100-175 (variants <=100)"),
 "R07": ("active", "D20: packing multiple shots per gen is the standard; playbook §7.5 'one action per clip' retired"),
 "R21": ("active", "D21: Ad Multiplier = whole video; background/character swaps allowed ONLY in Ad Multiplier mode"),
 "R22": ("active", "D21: variant reposts via Ad Multiplier only"),
}
EXTRA = [
 ("H01", "Exclude race/ethnicity casting and slur content from every rule, prompt and output", "(compliance; REPORT §7)", "all", "active", "D27: config.sanitize_casting + QA casting_violations block"),
 ("H02", "'Don't show this to…' on decor = experiment-only (MerryFire 0/3: 457/33/3K); prefer then-vs-now + POV on decor", "(team data)", "decor", "active", "D19 pending Omar"),
 ("H03", "Hooks <=5 s; every gen <=5 s", "\"im sorry 8 seconds? that can be done in 5 tops\"", "all", "active", "D25"),
]

def rules():
    r = pd.read_csv(f"{MAC}/rules.csv")
    r["status"] = [RESOLUTION.get(i, ("active", ""))[0] for i in r.id]
    r["hookforge_resolution"] = [RESOLUTION.get(i, ("", ""))[1] for i in r.id]
    r["freshness_scope"] = "craft (no decay)"
    for x in EXTRA:
        r.loc[len(r)] = dict(id=x[0], rule=x[1], verbatim_quote=x[2], date_PT="2026-10-18", source_session_or_file="Hookforge integration",
                             scope=x[3], evolution_or_superseded_by="", playbook_conflict_or_note="", status=x[4], hookforge_resolution=x[5],
                             freshness_scope="craft (no decay)")
    for col in ("rule", "verbatim_quote"):
        r[col] = r[col].map(sanitize_casting)
    os.makedirs(f"{REPO}/learning", exist_ok=True)
    r.to_csv(f"{REPO}/learning/rules_core.csv", index=False)
    print("rules_core", len(r))

if __name__ == "__main__":
    prompts(); rules()
