"""D62 AUDIENCE-FIT stage (Omar 2026-10-19: "song matching, emoji matching, caption matching it all needs to fit in that
audience/niche always. this isnt amateur hour"). Mandatory: a plan fails if any song, emoji or caption lacks an
audience-fit PASS with evidence.

Profiles: audience/<slug>.yaml (+ audience/_global.yaml bans: phonk, Android/Noto emoji).
  song_rank(slug, candidates)  -> tiers (a) proven on same/similar product, (b) trending with the audience on its main
                                  platform, (c) reference format. Each song needs evidence (URL / own-data ref) + in-point.
  check_song / check_emoji / check_text -> dict(ok, reason, evidence)
  check_plan(plan)             -> dict(ok, slug, rows); every row logged to learning/audience_fit_log.csv
  trumpglow_songs()            -> candidates parsed from research/trumpglow/SONGS.md (the song placeholder for PatriotGlow)
"""
import os, re, csv, json, glob, datetime
import yaml
from .config import REPO

AUD = os.path.join(REPO, "audience"); LOG = os.path.join(REPO, "learning", "audience_fit_log.csv")
TIER_W = {"a": 3.0, "b": 2.0, "c": 1.0}
# genre of each library song (music.SONGS keys) so genre bans/allows can be checked
SONG_GENRE = {"last_christmas": "christmas pop", "holly_jolly": "christmas crooner", "beginning_to_look": "christmas crooner",
              "aiwfc_intro": "christmas pop", "let_it_snow": "christmas classic", "chestnuts": "christmas classic",
              "somewhere_memory": "christmas classic", "jingle_bells_viibez": "christmas remix", "rockin_around": "christmas classic",
              "baby_please": "christmas classic", "boombastic_tiktok": "reggae dancehall", "free_bird": "southern rock",
              "be_my_baby": "oldies", "mambo_no_5": "oldies mambo", "give_it_up": "reggae dancehall", "velvet_glow": "cozy lofi christmas", "family_christmas": "cozy lofi christmas"}
GENRE_ALIASES = {"christmas classic slow": "christmas classic", "meme classic rock": "southern rock", "classic rock": "southern rock",
                 "christmas remix": "christmas pop"}

def _now(): return datetime.datetime.now(__import__("zoneinfo").ZoneInfo("America/Los_Angeles")).isoformat(timespec="seconds")

_YC = {}
def _yaml(path):
    """D133 cache: parsed YAML keyed by (path, mtime, size); deep-copied so callers can't mutate the cache."""
    import copy
    st = os.stat(path); k = (path, st.st_mtime_ns, st.st_size)
    if _YC.get(path, (None,))[0] != k: _YC[path] = (k, yaml.safe_load(open(path)))
    return copy.deepcopy(_YC[path][1])

def glob_rules(): return _yaml(os.path.join(AUD, "_global.yaml"))

def slugs(): return sorted(os.path.basename(f)[:-5] for f in glob.glob(os.path.join(AUD, "*.yaml")) if not os.path.basename(f).startswith("_"))

def slug_for(product_key):
    for s in slugs():
        p = _yaml(os.path.join(AUD, s + ".yaml"))
        if product_key == s or product_key in (p.get("product_keys") or []) or product_key in (p.get("aliases") or []): return s
    return None

def load(slug):
    s = slug_for(slug) or slug; f = os.path.join(AUD, s + ".yaml")
    if not os.path.exists(f): raise FileNotFoundError(f"no audience profile for {slug}: audience-fit cannot pass (D62)")
    p = _yaml(f); p["_global"] = glob_rules(); return p

# ---------------- songs ----------------
def _genre_ok(p, genre, text):
    g = glob_rules()
    for b in g["music_banned_genres"]:
        if re.search(b["match"], f"{genre} {text}"): return False, f"GLOBAL BAN {b['genre']}: {b['why']}"
    for b in p.get("music_banned_genres") or []:
        if genre and (b.lower() in genre.lower() or re.search(r"\b" + re.escape(b.lower()) + r"\b", text.lower())): return False, f"genre '{b}' banned for {p['slug']}"
    for b in p.get("banned") or []:
        if not b.startswith("(?i)") and b.lower() in text.lower() and len(b) > 6: return False, f"banned for {p['slug']}: {b}"
    allowed = [GENRE_ALIASES.get(a, a) for a in p.get("music_allowed_genres") or []]
    gg = GENRE_ALIASES.get(genre, genre)
    if gg not in allowed: return False, f"genre '{genre}' not in {p['slug']} allowed genres {p.get('music_allowed_genres')}"
    return True, f"genre '{genre}' fits {p['slug']} ({p['tone']})"

def check_song(slug, cand):
    """cand: dict(song, genre, in_point, tier a|b|c, evidence=[str url or 'own:...'/'omar:...'])."""
    p = load(slug); text = f"{cand.get('song','')} {cand.get('version','')}"
    ok, why = _genre_ok(p, cand.get("genre", ""), text)
    ev = [e for e in cand.get("evidence") or [] if e and (str(e).startswith(("http", "own:", "omar:", "ref:", "ext:")))]
    if ok and not ev: ok, why = False, "NO EVIDENCE: a song needs a proof URL / own-data reference (D62)"
    if ok and cand.get("in_point") in (None, "", "nan"): ok, why = False, "no in-point recorded"
    ipe = [e for e in cand.get("in_point_evidence") or [] if e]
    if ok and not ipe: ok, why = False, "NO IN-POINT EVIDENCE: the in-point must be the section people actually use on similar videos (TikTok/IG audio-page popular clip or most-used start in reference reels / own drafts)"
    if ok and cand.get("tier") not in TIER_W: ok, why = False, "no evidence tier (a proven / b trending / c reference)"
    return dict(kind="song", item=cand.get("song"), ok=ok, reason=why, tier=cand.get("tier"), in_point=cand.get("in_point"), evidence=ev + [f"in-point: {e}" for e in ipe])

def song_rank(slug, candidates):
    rows = [dict(c, **{"check": check_song(slug, c)}) for c in candidates]
    for r in rows: r["score"] = TIER_W.get(r.get("tier"), 0) + 0.1 * len(r["check"]["evidence"]) - 0.01 * r.get("rank_hint", 0)
    ok = sorted([r for r in rows if r["check"]["ok"]], key=lambda r: -r["score"]); bad = [r for r in rows if not r["check"]["ok"]]
    return dict(ranked=ok, rejected=bad, pick=ok[0] if ok else None)

def library_candidates(slug):
    """Songs from learning/music_library.csv: tier a when proven on this product or a sibling with the same audience."""
    p = load(slug); keys = set(p.get("product_keys") or []); sib = set()
    if p.get("inherits_from"): sib |= set(load(p["inherits_from"]).get("product_keys") or [])
    out = []
    with open(os.path.join(REPO, "learning", "music_library.csv")) as f:
        for r in csv.DictReader(f):
            ev, tier = [], None
            for x in filter(None, r["proven_on"].split(";")):
                if ":" not in x: continue
                pk, rest = x.split(":", 1)
                if pk in keys or pk in sib: ev.append(f"own:learning/music_library.csv {r['song']} on {pk} {rest}"); tier = "a"
            if not tier and r.get("proven") == "True" and int(float(r.get("ext_best_views") or 0)) > 0 and r["niche"] and any(n in (p.get("tone", "") + " ".join(p.get("music_allowed_genres", []))) for n in r["niche"].split("|")):
                ev.append(f"ext:learning/music_library.csv {r['song']} ext best {r['ext_best_views']} ({r['ext_categories']})"); tier = "c"
            m = re.search(r"(\d+:\d+(?:\.\d+)?)", r["version"])
            inp = r["capcut_offset_s"] or (m.group(1) if m else ("0:00" if "0:00" in r["version"] else ""))
            ipe = [f"own: most-used start {r['capcut_offset_s']} s on the CapCut file across {r['n_own_drafts']} own drafts (learning/music_library.csv)"] if r["capcut_offset_s"] and int(float(r["n_own_drafts"] or 0)) >= 2 else []
            out.append(dict(song=r["song"], version=r["version"], genre=SONG_GENRE.get(r["song"], ""), in_point=inp, tier=tier, evidence=ev, in_point_evidence=ipe))
    return out

def trumpglow_songs(path=None):
    """PatriotGlow/TrumpGlow song placeholder: parsed from research/trumpglow/SONGS.md (do not duplicate that research)."""
    path = path or os.path.join(REPO, "research", "trumpglow", "SONGS.md")
    if not os.path.exists(path): return dict(status="PENDING", file=path, candidates=[])
    t = open(path).read(); fin = t.split("## Final ranking", 1)[-1]
    genre = {"free bird": "southern rock", "y.m.c.a": "disco rally anthem", "american bad ass": "southern rock",
             "courtesy of the red": "patriotic country", "try that in a small town": "country", "last thing you need": "country"}
    out = []
    for i, line in enumerate(re.findall(r"^\d+\.\s+(.+)$", fin, re.M)):
        name = re.split(r"\.\s+Start", line)[0].strip(); low = name.lower()
        m = re.search(r"[Ss]tart\D*?(~?\d+:\d+)", line)
        g = next((v for k, v in genre.items() if k in low), "")
        key = re.sub(r"[^a-z]", "", low.split('"')[1] if '"' in low else low)
        ev = []
        for row in re.findall(r"^\|(.+)\|$", t, re.M):           # evidence rows that mention this song
            if key[:6] and key[:6] in re.sub(r"[^a-z]", "", row.lower()):
                ev += [u.rstrip(" ).,") for u in re.findall(r"https?://\S+", row)]
                if "confirmed by omar" in row.lower(): ev.append("omar: Omar confirmed Free Bird on past Trump products (2026-10-19 chat)")
        proof_rows = t.split("## Proof of concept", 1)[-1].split("## Final ranking", 1)[0]
        on_product = key[:6] in re.sub(r"[^a-z]", "", proof_rows.lower()) and not re.search(re.escape(key[:6]) + r"[^|]*\|\s*0 on products", re.sub(r'[^a-z|0-9 ]', '', proof_rows.lower()))
        tier = "a" if on_product and ev else ("b" if ev else None)
        from . import music
        lib = {c["song"]: c for c in library_candidates("patriotglow")}.get(music.canon(name) or "")
        ipe = list(lib["in_point_evidence"]) if lib and lib.get("in_point_evidence") else []
        inp = (f"{lib['in_point']} s (CapCut file; SONGS.md album note: {m.group(1).strip() if m else '-'})" if ipe else (m.group(1).strip() if m else ""))
        out.append(dict(song=name, genre=g, in_point=inp, tier=tier, evidence=sorted(set(ev)), in_point_evidence=ipe, rank_hint=i, source="research/trumpglow/SONGS.md"))
    return dict(status="FILLED", file=path, candidates=out)

# ---------------- emoji + text ----------------
def emojis(text):
    import emoji as E
    return [d["emoji"] for d in E.emoji_list(text)]

def check_emoji(slug, e, render="apple_ios"):
    p = load(slug); g = p["_global"]; norm = e.replace("\ufe0f", "")
    allowed = {k.replace("\ufe0f", ""): v for k, v in (p.get("emoji_allowed") or {}).items()}
    if render in g["emoji_render_banned"] or render != g["emoji_render"]: return dict(kind="emoji", item=e, ok=False, reason=f"render '{render}' banned: Apple iOS emoji only", evidence=[])
    if e in g.get("emoji_banned", []): return dict(kind="emoji", item=e, ok=False, reason="globally banned emoji", evidence=[])
    if norm not in allowed:
        from . import proof_guard as PG   # D68: allowlist can't block an emoji proven in Omar's own data
        cats = PG.niche_categories(p); ev = PG.emoji_proof(e, cats) if cats else []
        if ev and not PG.omar_banned(p, e): return dict(kind="emoji", item=e, ok=True, reason=f"not in {p['slug']} set but proven in own data (D68 guard)", evidence=ev)
        return dict(kind="emoji", item=e, ok=False, reason=f"not in {p['slug']} emoji set (meaning in this niche unproven)", evidence=[])
    return dict(kind="emoji", item=e, ok=True, reason=f"{p['slug']}: {allowed[norm]}", evidence=[f"profile:audience/{p['slug']}.yaml emoji_allowed"])

def check_text(slug, text, kind="caption", extra_evidence=None):
    """Caption / card line: bans, US spelling, voice/slang score, PoC evidence (profile caption_proof or a proven hook source)."""
    p = load(slug); g = p["_global"]; plain = re.sub(r"\{url\}", "", text)
    for b in list(g.get("caption_banned", [])) + [b for b in p.get("banned") or [] if b.startswith("(?i)")]:
        if re.search(b, plain): return dict(kind=kind, item=text, ok=False, reason=f"banned pattern {b}", evidence=[])
    ev = [c["evidence"] for c in p.get("caption_proof") or [] if re.search(c["pattern"], plain.strip())]
    if extra_evidence: ev.append(extra_evidence)
    slang = [s for s in p.get("slang") or [] if s.lower().rstrip(".") in plain.lower()]
    boost = 0.0
    if kind == "caption":  # D63: profile caption_boosts learned from FB page insights (link clicks / views)
        for cb in p.get("caption_boosts") or []:
            if re.search(cb["pattern"], text): boost += float(cb["weight"]); ev.append(cb["evidence"]) if cb["weight"] > 0 else None
        ne = len(emojis(plain))
        if ne == 0 or ne > 3: boost -= 0.1  # FB insights: 0 emoji median 2.3K views (n=3)
    if kind in ("caption", "hook", "card"):  # D67: short proven formats win; long POV sentences lose
        nw = len(re.sub(r"[^\w\s'-]", " ", plain).split())
        if re.search(r"(?i)^do(n'?t|nt| not) show this to", plain.strip()): boost += 0.2
        if nw > int(p.get("hook_max_words", 8)): boost -= 0.15 + 0.05 * (nw - int(p.get("hook_max_words", 8)))
        if re.match(r"(?i)^pov\b", plain.strip()) and nw > 8: boost -= 0.25
    score = round(max(0.0, min(1.0, 0.5 * bool(ev) + 0.25 * bool(slang) + 0.25 * (len(plain) <= 70) + boost)), 2)
    if not ev: return dict(kind=kind, item=text, ok=False, score=score, reason=f"no proof for this line in the {p['slug']} niche (caption_proof / proven hook needed)", evidence=[])
    return dict(kind=kind, item=text, ok=True, score=score, reason=f"voice: {p['caption_voice'][:60]}; slang {slang or '-'}", evidence=ev)

# ---------------- plan ----------------
def _plan_slug(plan):
    pk = plan.get("product_key") or (plan.get("product") or {}).get("key")
    return slug_for(pk) if pk else None, pk

def _song_cand(plan, slug):
    m = plan.get("music") or {}
    if m.get("audience_fit_song"): return m["audience_fit_song"]
    name = (m.get("pick") or {}).get("song") if isinstance(m.get("pick"), dict) else m.get("song")
    if not name: return None
    from . import music
    key = music.canon(name) or name
    lib = {c["song"]: c for c in library_candidates(slug)}
    if key in lib: return dict(lib[key], song=key)
    return dict(song=name, genre="", in_point="", tier=None, evidence=[])

def check_plan(plan, log=True):
    slug, pk = _plan_slug(plan); rows = []
    if not slug:
        rows.append(dict(kind="profile", item=pk, ok=False, reason="no audience profile: audience-fit cannot pass", evidence=[]))
        return dict(ok=False, slug=None, rows=rows)
    render = (plan.get("text_style") or {}).get("emoji_render", "apple_ios")
    sc = _song_cand(plan, slug)
    rows.append(check_song(slug, sc) if sc else dict(kind="song", item=None, ok=False, reason="no song picked", evidence=[]))
    hk = plan.get("hook") or {}
    hook_ev = f"own/ext hook: {hk['why']}" if hk.get("why") and re.search(r"own|proven|EXT-|views", hk["why"]) else None
    for c in plan.get("text_cards") or []:
        t = c["text"]; base = re.sub(r"\s+", " ", t).strip()
        hev = hook_ev if hook_ev and (base == re.sub(r"\s+", " ", hk.get("text", "")).strip() or base in [re.sub(r"\s+", " ", x) for x in (hk.get("cards") or [])]) else None
        rows.append(check_text(slug, t, "card", hev))
        rows += [check_emoji(slug, e, render) for e in emojis(t)]
    cap = plan.get("caption")
    if cap:
        ct = cap["text"] if isinstance(cap, dict) else cap
        rows.append(check_text(slug, ct, "caption", f"own: {cap.get('why')}" if isinstance(cap, dict) and "views" in str(cap.get("why")) else None))
        rows += [check_emoji(slug, e, render) for e in emojis(ct)]
    res = dict(ok=all(r["ok"] for r in rows), slug=slug, rows=rows)
    if log: _log(plan, res)
    return res

def _log(plan, res):
    new = not os.path.exists(LOG); os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a", newline="") as f:
        w = csv.writer(f)
        if new: w.writerow(["ts_pt", "slug", "plan", "kind", "item", "ok", "reason", "evidence"])
        tag = plan.get("brief", {}).get("brief") if isinstance(plan.get("brief"), dict) else plan.get("mode", "")
        for r in res["rows"]: w.writerow([_now(), res["slug"], tag, r["kind"], r["item"], r["ok"], r["reason"], " | ".join(r.get("evidence") or [])])

def lint_rows(plan):
    """Linter rows (rule AF1 song / AF2 emoji / AF3 caption+card), severity FIX on any failure."""
    r = check_plan(plan); code = dict(song="AF1", emoji="AF2", card="AF3", caption="AF3", profile="AF0")
    return r, [dict(gen="-", kind="audience", rule=code.get(x["kind"], "AF0"), severity="FIX", text=f"{x['item']}: {x['reason']}",
                    fix="pick an item from audience/<slug>.yaml with evidence (D62)") for x in r["rows"] if not x["ok"]]

def song_slot(slug):
    """Song placeholder for a plan: PatriotGlow/TrumpGlow reads research/trumpglow/SONGS.md; others use the music library."""
    p = load(slug)
    cands = trumpglow_songs()["candidates"] if p.get("songs_source") else library_candidates(slug)
    r = song_rank(slug, cands)
    return dict(status="FILLED" if cands else "PENDING", source=p.get("songs_source") or "learning/music_library.csv",
                pick=r["pick"], ranked=[(x["song"], x["tier"], x["in_point"]) for x in r["ranked"]],
                rejected=[(x["song"], x["check"]["reason"]) for x in r["rejected"]])
