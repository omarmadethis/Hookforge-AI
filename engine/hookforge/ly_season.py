"""ly_season (PD-G5 -> D88): last season's holiday benchmark tier, Nov 1 2025 - Jan 10 2026, 1M+ views.
Sources (existing corpus only, no new scraping): private/corpus/corpus.csv external rows with posted dates, and
team/viral_research/work/tt_tags_1018.jsonl (TikTok tag scans with create times). Each row gets a phase from the
2026 calendar shifted back one year. prior() returns phase-specific format and music shares weighted 0.5 that
can NEVER outrank own data: blend(own, prior) caps the prior's weight at min(0.5, own_weight) per option."""
import os, re, json, datetime as dt
import pandas as pd
from .config import REPO
from .taxonomy import format_of
W = "/workspace"
OUT = os.path.join(REPO, "research", "ly_season", "ly_season.csv")
WINDOW = (dt.date(2025, 11, 1), dt.date(2026, 1, 10)); MIN_VIEWS = 1_000_000; WEIGHT = 0.5
# 2026 calendar shifted -1y (gift cutoff unknown last year -> USPS ground ~Dec 17 2025)
PHASES = [("pre_season", "2025-10-18", "2025-11-15"), ("peak_gift", "2025-11-16", "2025-12-17"),
          ("post_cutoff", "2025-12-18", "2025-12-25"), ("post_christmas", "2025-12-26", "2026-01-15")]
BFCM = ("2025-11-27", "2025-12-02")

def phase_of(d):
    d = d if isinstance(d, dt.date) else pd.to_datetime(d).date()
    out = next((p for p, a, b in PHASES if dt.date.fromisoformat(a) <= d <= dt.date.fromisoformat(b)), "off_season")
    return "bfcm" if dt.date.fromisoformat(BFCM[0]) <= d <= dt.date.fromisoformat(BFCM[1]) else out

def _music(s):
    s = str(s or "").strip()
    if not s or s.lower() in ("nan", "original sound", "оригинальный звук", "原聲", "som original", "sonido original") or "original" in s.lower(): return "original_sound"
    s = s.lower()
    if re.fullmatch(r"(\w ){3,}\w", s): s = s.replace(" ", "")   # "l a s t c h r i s t m a s"
    return {"lastchristmas": "last christmas"}.get(s, s)

def build(save=True):
    rows = []
    c = pd.read_csv(os.path.join(REPO, "private", "corpus", "corpus.csv"), low_memory=False)
    c = c[c.source != "own"]
    for r in c.itertuples(index=False):
        d = pd.to_datetime(r.posted_pt, errors="coerce", format="mixed")
        if pd.isna(d) or not (WINDOW[0] <= d.date() <= WINDOW[1]) or not (r.views >= MIN_VIEWS): continue
        rows.append(dict(key=r.key, src="corpus_external", platform=r.platform, posted=d.date().isoformat(), views=int(r.views),
                         format=r.format, music=_music(r.audio), category=r.category, hook=r.hook_text))
    p = os.path.join(W, "team", "viral_research", "work", "tt_tags_1018.jsonl")
    if os.path.exists(p):
        seen = set()
        for l in open(p):
            j = json.loads(l); d = str(j.get("created", ""))[:10]
            if j["id"] in seen or not d or not (WINDOW[0].isoformat() <= d <= WINDOW[1].isoformat()) or (j.get("plays") or 0) < MIN_VIEWS: continue
            if j.get("isAd"): continue
            seen.add(j["id"])
            rows.append(dict(key=f"TT-{j['id']}", src="vr_tt_tags", platform="TikTok", posted=d, views=int(j["plays"]),
                             format=format_of("", "", j.get("desc", "")), music=_music(j.get("music")), category=j.get("q"), hook=(j.get("desc") or "")[:120]))
    df = pd.DataFrame(rows)
    df["phase"] = df.posted.map(phase_of); df["tier"] = "ly_season"; df["weight"] = WEIGHT
    if save: os.makedirs(os.path.dirname(OUT), exist_ok=True); df.to_csv(OUT, index=False)
    return df

def prior(phase, field="format", df=None):
    """Share of ly_season 1M+ reels per option for a phase, views-weighted (log), times WEIGHT. {} if phase empty."""
    import numpy as np
    df = df if df is not None else (pd.read_csv(OUT) if os.path.exists(OUT) else build())
    g = df[df.phase == phase]
    if field == "format": g = g[~g.format.isin(["F99"]) & g.format.notna()]   # F99 = unclassified, not a format
    if not len(g): return {}
    w = np.log10(g.views.astype(float)); s = w.groupby(g[field]).sum() / w.sum()
    return {k: dict(share=round(float(v), 3), prior_weight=WEIGHT, score=round(float(v) * WEIGHT, 3), n=int((g[field] == k).sum()), thin=len(g) < 5) for k, v in s.sort_values(ascending=False).items()}

def blend(own, prior_d):
    """own: {option: score in 0..1 from OUR data}. Prior adds at most WEIGHT*share and never lifts an option above
    the best own-data option when own data exists (D28: own data outranks external)."""
    best_own = max(own.values()) if own else None
    out = dict(own)
    for k, p in prior_d.items():
        add = p["score"]; v = out.get(k, 0) + add
        if best_own is not None and k not in own: v = min(v, best_own * 0.999)
        out[k] = round(v, 4)
    return dict(sorted(out.items(), key=lambda kv: -kv[1]))

if __name__ == "__main__":
    d = build(); print(d.groupby("phase").size().to_string()); print(json.dumps({p: prior(p, "format", d) for p in d.phase.unique()}, indent=1, ensure_ascii=False)[:2500])
    print(json.dumps({p: dict(list(prior(p, "music", d).items())[:5]) for p in d.phase.unique()}, indent=1, ensure_ascii=False))

# ---- D92: curated Viral Research set (150 rows, /workspace/research/ly_season) -------------------------------
CURATED = os.path.join(W, "research", "ly_season", "ly_season.csv")
CURATED_SUMMARY = os.path.join(W, "research", "ly_season", "SUMMARY.md")
PAID_KEYS = {"EXT-01", "EXT-07", "EXT-32"}          # corpus_public paid_flag=1 -> dropped (strictly non-ad)
# Proven song in-points from last season (seconds into the track at video frame 0). Mariah is a range.
SONG_STARTS = {"brenda_lee_rockin_around": dict(in_point_s=0.0, match=("brenda lee", "rockin")),
               "darlene_love_baby_please": dict(in_point_s=14.9, match=("darlene love", "baby please come home")),
               "mariah_all_i_want": dict(in_point_s=49.5, range_s=(48.0, 51.0), match=("mariah", "all i want for christmas")),
               "coldplay_viva_la_vida": dict(in_point_s=8.3, match=("viva la vida",))}
CONCEPT_SUBTYPES = ("white_elephant", "haul", "outfit", "gift_exchange", "diy")
OCR_HOOK_CONFIDENCE = "low"   # hook formats/subtypes were OCR-classified, not hand-checked
OCR_HOOK_WEIGHT = 0.5         # extra discount on format priors from OCR-tagged rows

def load(path=CURATED):
    """Curated 150-row set minus paid rows; marks hook classifications as low confidence."""
    df = pd.read_csv(path)
    df = df[~df.key.isin(PAID_KEYS)].copy()
    df["hook_confidence"] = OCR_HOOK_CONFIDENCE
    return df.reset_index(drop=True)

def song_in_point(song):
    """Seasonal proven in-point for a song title/key, or None. Used by song-start logic when songs.json lacks one."""
    s = str(song or "").lower()
    for k, v in SONG_STARTS.items():
        if s == k or any(m in s for m in v["match"]): return dict(key=k, **{x: v[x] for x in v if x != "match"})
    return None

def concept_signals(phase=None, df=None):
    """Seasonal concept signals from hook_subtype: share (log-views weighted) x WEIGHT x OCR_HOOK_WEIGHT, low confidence."""
    import numpy as np
    df = df if df is not None else load()
    g = df[df.hook_subtype.isin(CONCEPT_SUBTYPES)]
    if phase: g = g[g.phase == phase]
    if not len(g): return {}
    w = np.log10(g.views.astype(float)); s = w.groupby(g.hook_subtype).sum() / np.log10(df.views.astype(float)).sum()
    return {k: dict(share=round(float(v), 3), score=round(float(v) * WEIGHT * OCR_HOOK_WEIGHT, 4), n=int((g.hook_subtype == k).sum()),
                    confidence=OCR_HOOK_CONFIDENCE) for k, v in s.sort_values(ascending=False).items()}

_prior_raw = prior
def prior(phase, field="format", df=None):
    """D92: defaults to the curated non-ad set; format priors are discounted (OCR-classified = low confidence)."""
    if df is None and os.path.exists(CURATED): df = load()
    out = _prior_raw(phase, field, df)
    if field == "format":
        for v in out.values(): v["score"] = round(v["score"] * OCR_HOOK_WEIGHT, 4); v["confidence"] = OCR_HOOK_CONFIDENCE
    return out
