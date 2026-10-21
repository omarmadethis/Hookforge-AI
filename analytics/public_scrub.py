"""Public-dashboard scrub (Omar 2026-10-18 10:35 PM PT): no product or brand names and no hook text in the public build.
scrub_reels() replaces product -> category label, page -> 'Page N', hook_text -> '<format> · <hook type>' and blanks every free-text
column; audit_html() is a last line of defence over the finished HTML (deny-list of brand/product/page names + every hook text)."""
import os, re, sys, json, html as _html
import pandas as pd

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO, "engine"))
CAT = {"wearable_gift": "Wearable gift", "decor_fire": "Decor (fire)", "accessory": "Accessory", "decor_mug": "Kitchen gift", "decor_light": "Decor (lights)", "pet": "Pet product"}
TEXT_COLS = ["caption", "all_text", "transcript", "transcript_speech", "hook_text_ocr", "hook_text_ref", "vo_first_words", "audio_label", "song", "url", "file",
             "dup_note", "note", "body_desc", "hook_visual", "product_prompt", "lib_name", "mac_name", "lib_folder", "frames_dir", "lowres_proxy", "text_events",
             "hook_words", "audio", "reel_id", "uid", "team_id", "same_edit_as", "views_inherited_from", "dup_of", "corpus_key"]

def _worlds():
    from hookforge.worlds import WORLDS; return WORLDS

def product_labels():
    W = _worlds(); m, seen = {}, {}
    for k, v in W.items():
        base = CAT.get(v["category"], "Product"); seen[base] = seen.get(base, 0) + 1
        lab = base if list(x["category"] for x in W.values()).count(v["category"]) == 1 else f"{base} {chr(64 + seen[base])}"
        for name in [k, v["display"], v.get("brand", "")] + list(v.get("corpus_products", [])): 
            if name: m[name.lower()] = lab
    return m

def page_labels(codes):
    return {c: f"Page {i + 1}" for i, c in enumerate(sorted({str(x) for x in codes if isinstance(x, str) and x}))}

def scrub_reels(df):
    df = df.copy(); pl = product_labels()
    if "product" in df: df["product"] = [pl.get(str(p).lower(), "Other product" if isinstance(p, str) and p else p) for p in df["product"]]
    pg = page_labels(df.get("page_code", pd.Series(dtype=str)).dropna().unique())
    if "page_code" in df: df["page_code"] = df["page_code"].map(lambda x: pg.get(str(x), "External") if isinstance(x, str) else "External")
    if "page" in df: df["page"] = df["page_code"] if "page_code" in df else "Page"
    fam = df["hook_family"].fillna("uncoded").astype(str) if "hook_family" in df else "uncoded"
    fmt = df["format"].fillna("F?").astype(str) if "format" in df else "F?"
    if "hook_text" in df: df["hook_text"] = fmt + " · " + fam
    for c in TEXT_COLS:
        if c in df: df[c] = None
    if "key" in df: df["key"] = [f"R{i:03d}" for i in range(len(df))]
    return df

def deny_terms():
    W = _worlds(); t = set()
    for k, v in W.items():
        t |= {v["display"], v.get("brand", ""), v.get("product_look", "")} | set(v.get("corpus_products", []))
    try:
        import hf_load as L; t |= set(L.PAGE_NAMES.values())
    except Exception: pass
    t |= {"Grinch", "Jammies", "HeatedJammies", "MerryFire", "MerryFires", "Merry Fire", "Merry Glow", "MerryGlow", "Merry Glows", "Brick Hood", "BrickHood",
          "GrinchMelt", "JollyGlow", "Merry Jammies", "MerryJammies", "Heated Jammies", "PurrVenture", "Purrventure", "Merry Carrier", "merry.jammies", "merryjammies", "brickhood", "merryglow"}
    return sorted({x for x in t if x and len(x) >= 4}, key=len, reverse=True)

def hook_texts():
    p = os.path.join(REPO, "private", "corpus", "corpus.csv")
    c = pd.read_csv(p, low_memory=False) if os.path.exists(p) else pd.DataFrame(columns=["hook_text"])
    out = set()
    for h in c.hook_text.dropna().astype(str):
        a = re.sub(r"[^A-Za-z0-9 ']", " ", h); a = re.sub(r"\s+", " ", a).strip()
        if len(a) >= 14: out.add(a[:28])
    return sorted(out, key=len, reverse=True)

def reel_ids():
    """Public reel shortcodes / FB reel ids identify the pages; redact them too."""
    p = os.path.join(REPO, "private", "corpus", "corpus.csv"); ids = set()
    if os.path.exists(p):
        c = pd.read_csv(p, low_memory=False, usecols=lambda x: x in ("url", "file", "key"))
        for col in c.columns:
            for v in c[col].dropna().astype(str):
                ids |= set(re.findall(r"(?:reels?|p)/([A-Za-z0-9_-]{9,14})", v)) | set(re.findall(r"(?<![0-9])([0-9]{15,17})(?![0-9])", v))
    for f in ("instagram/merryjammies_ig_reels.md",):
        q = os.path.join(REPO, "team", f)
        if os.path.exists(q): ids |= set(re.findall(r"\b(D[A-Za-z0-9_-]{10})\b", open(q, errors="ignore").read()))
    return sorted(ids, key=len, reverse=True)

STORE_LABELS = {"Merry Jammies": "Store A", "merryjammies": "store-a", "Merry Glow": "Store B", "merryglow": "store-b", "Brick Hood": "Store C", "brickhood": "store-c"}

def audit_html(s, fix=True):
    """Count (and optionally redact) any deny-listed name or hook text left in the finished HTML. Store names become neutral Store A/B/C labels."""
    found = {}
    for term, lab in STORE_LABELS.items():
        rx = re.compile(re.escape(term).replace("\\ ", r"[\s_.-]?"), re.I); n = len(rx.findall(s))
        if n: found[term] = n; s = rx.sub(lab, s) if fix else s
    for term in deny_terms():
        rx = re.compile(re.escape(term).replace("\\ ", r"[\s_.-]?"), re.I)
        n = len(rx.findall(s))
        if n: found[term] = n; s = rx.sub("[redacted]", s) if fix else s
    for h in hook_texts():
        rx = re.compile(re.escape(h).replace("\\ ", r"\s+").replace("'", "(?:'|&#x27;|\\\\u2019|’)"), re.I)
        n = len(rx.findall(s))
        if n: found["hook:" + h] = n; s = rx.sub("[hook text]", s) if fix else s
    for r in reel_ids():
        n = s.count(r)
        if n: found["reel_id:" + r[:3] + "…"] = n; s = s.replace(r, "[reel]") if fix else s
    return s, found
