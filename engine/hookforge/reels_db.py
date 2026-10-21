"""Shared reel loader over data/hookforge.db (features workstream, owner: data/features worker) + the Phase A corpus.
The DB is opened READ-ONLY (sqlite URI mode=ro) and never written; the features build keeps running and may rewrite it.
merged(): corpus-first identity + DB measured features (new columns) + DB values filling corpus gaps; see merged().
review(): checks the DB against the corpus and writes learning/db_review.json; the DB becomes the default source only
while the latest review passes for the DB file currently on disk (same mtime+size)."""
import os, re, json, sqlite3, datetime
import sys, warnings
import pandas as pd
warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)
from zoneinfo import ZoneInfo
from .config import REPO

DB = os.path.join(REPO, "data", "hookforge.db")
CORPUS = os.path.join(REPO, "private", "corpus", "corpus.csv")
REVIEW = os.path.join(REPO, "learning", "db_review.json")
LABELLED = ("own", "external", "viral_research")
REQUIRED = ["uid", "source", "page_code", "views", "posted", "corpus_key", "hook_text", "hook_family", "duration_s", "n_cuts", "first_cut_s", "schema_version"]

def _sig(): st = os.stat(DB); return f"{int(st.st_mtime)}:{st.st_size}"

def read_db():
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=5)
    try: return pd.read_sql("select * from reels", con)
    finally: con.close()

IDENTITY = ["key", "source", "page", "page_code", "platform", "product", "category", "hook_text", "posted_pt", "format", "views"]

def merged(db=None):
    """Corpus-first identity (page, product, category, hook text, format, views stay as the validated Phase A values), DB measured
    features added as new columns, and DB values filling corpus gaps (e.g. shares, 3-s rate) - never overwriting a corpus value.
    Labelled DB rows with no corpus key are appended (db_row=True, corpus_row=False)."""
    db = read_db() if db is None else db
    db = db[db.source.isin(LABELLED)].copy()
    c = pd.read_csv(CORPUS, low_memory=False)
    # externals carry no corpus_key in the DB: map by the platform reel id found in the corpus url/file
    if db.corpus_key.isna().any():
        idx = {}
        for k, u, f in zip(c.key, c.get("url", pd.Series("", index=c.index)).fillna("").astype(str), c.get("file", pd.Series("", index=c.index)).fillna("").astype(str)):
            for rid in re.findall(r"\d{15,}|[A-Za-z0-9_-]{11}(?=[/?]|$)", u + " " + f): idx.setdefault(rid, k)
        miss = db.corpus_key.isna()
        db.loc[miss, "corpus_key"] = db.loc[miss, "reel_id"].fillna("").astype(str).map(idx)
    out = c.copy(); out["corpus_row"] = True
    d = db.set_index("corpus_key")
    d = d[d.index.notna() & ~d.index.duplicated()]
    new_cols = [x for x in d.columns if x not in out.columns]
    out = pd.concat([out, d[new_cols].reindex(out["key"]).reset_index(drop=True)], axis=1)
    for col in [x for x in d.columns if x in out.columns and x not in IDENTITY]:
        fill = out["key"].map(d[col])
        out[col] = out[col].where(out[col].notna(), fill)
    out = out.assign(hook_family_db=out["key"].map(d["hook_family"]) if "hook_family" in d else None, db_row=out["key"].isin(d.index)).copy()
    extra = db[db.corpus_key.isna()].copy()
    if len(extra):
        extra["key"] = extra["uid"]; extra["db_row"] = True; extra["corpus_row"] = False
        out = pd.concat([out, extra], ignore_index=True, sort=False)
    return out

def load_reels():
    """What the engine and dashboard read: merged() when the DB review passed for the file on disk, else the corpus."""
    if db_is_default():
        try: return merged(), "hookforge.db+corpus"
        except Exception as e: print(f"[reels_db] DB merge failed, using corpus: {e}", file=sys.stderr)
    return pd.read_csv(CORPUS, low_memory=False), "corpus.csv"

def review(write=True):
    t = datetime.datetime.now(ZoneInfo("America/Los_Angeles")).isoformat(timespec="seconds")
    res = dict(ts_pt=t, db=DB, checks={}, passed=False)
    try:
        db = read_db(); res["db_sig"] = _sig()
    except Exception as e:
        res["error"] = f"unreadable: {e}"; write and json.dump(res, open(REVIEW, "w"), indent=1); return res
    c = pd.read_csv(CORPUS, low_memory=False); lab = db[db.source.isin(LABELLED)]
    ck = res["checks"]
    ck["required_columns"] = dict(missing=[x for x in REQUIRED if x not in db.columns]); ck["required_columns"]["ok"] = not ck["required_columns"]["missing"]
    own_c = c[(c.source == "own") & (c.get("insights_only", 0).fillna(0).astype(int) == 0)] if "insights_only" in c else c[c.source == "own"]
    missing_own = sorted(set(own_c.key) - set(lab.corpus_key.dropna()))
    ck["own_coverage"] = dict(corpus_own=len(own_c), in_db=len(own_c) - len(missing_own), missing=missing_own[:20], ok=len(missing_own) == 0)
    m = lab.merge(c, left_on="corpus_key", right_on="key", suffixes=("_db", "_c"))
    v = m[m.views_db.notna() & m.views_c.notna()]
    agree = float(((v.views_db - v.views_c).abs() / v.views_c.clip(lower=1) < 0.02).mean()) if len(v) else 0.0
    ck["views_agreement"] = dict(n=len(v), within_2pct=round(agree, 3), ok=agree >= 0.98)
    ck["unique_uid"] = dict(dups=int(lab.uid.duplicated().sum()), ok=not lab.uid.duplicated().any())
    pv = pd.to_datetime(m.posted, errors="coerce"); pc = pd.to_datetime(m.posted_pt.astype(str).str.replace(" PT", ""), errors="coerce")
    both = pv.notna() & pc.notna()
    pt_ok = float(((pv - pc)[both].abs() <= pd.Timedelta(minutes=5)).mean()) if both.any() else 0.0
    ck["posted_time_agreement_pt"] = dict(n=int(both.sum()), within_5min=round(pt_ok, 3), ok=pt_ok >= 0.95)
    ck["hook_family_codebook"] = dict(note="DB uses the features codebook (data/features/codebook.csv); corpus family kept as hook_family_corpus",
                                      agreement_raw=round(float((m.hook_family_db == m.hook_family_c).mean()), 3), ok=True)
    ck["format_present"] = dict(db_format_ref_filled=int(lab.get("format_ref", pd.Series(dtype=str)).notna().sum()),
                                note="format comes from the corpus overlay until the DB fills format_ref", ok=True)
    res["passed"] = all(x.get("ok") for x in ck.values()); res["rows_labelled"] = len(lab); res["schema_version"] = str(lab.schema_version.dropna().unique()[:3].tolist())
    if write: json.dump(res, open(REVIEW, "w"), indent=1, default=str)
    return res

def db_is_default():
    """True when the last review passed for the DB file currently on disk. HOOKFORGE_USE_DB=0 forces the corpus."""
    if os.environ.get("HOOKFORGE_USE_DB") == "0" or not os.path.exists(DB) or not os.path.exists(REVIEW): return False
    r = json.load(open(REVIEW))
    try: return bool(r.get("passed")) and r.get("db_sig") == _sig()
    except FileNotFoundError: return False

if __name__ == "__main__":
    print(json.dumps(review(), indent=1, default=str))
