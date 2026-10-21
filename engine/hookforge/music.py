"""Music library (D38): every song must be PROVEN and match niche + energy.
build() -> learning/music_library.csv from (a) our CapCut drafts joined to posted reels (song file, version, offset),
(b) our corpus song column (frame-matched audio), (c) research-library reels (audio_label, views, category).
select(profile, fmt, slot) -> proven song or (experiment slot only) unproven. Hard bans from the product profile.
"""
import os, json, re
import pandas as pd, numpy as np
from .config import REPO, HIT_ABS_VIEWS

# canonical song -> (regex, version note, energy 1-5, mood tags, niche)
SONGS = {
 "last_christmas":   (r"last.?christmas|wham", "Wham! Last Christmas (official) ~2:50 chorus", 4, "exciting|festive|hype|store", "christmas"),
 "holly_jolly":      (r"holly.?jolly", "Michael Bublé Holly Jolly Christmas from 0:00", 3, "upbeat|cozy|playful", "christmas"),
 "beginning_to_look":(r"beginning.?to.?look", "Michael Bublé It's Beginning to Look a Lot Like Christmas ~0:31.6", 2, "warm|cozy|nostalgic", "christmas"),
 "aiwfc_intro":      (r"all.?i.?want", "Mariah Carey AIWFC, slow intro (Make My Wish Come True ed. ~0:49.6)", 3, "build|festive|reveal", "christmas"),
 "let_it_snow":      (r"let.?it.?snow", "Dean Martin Let It Snow from 0:00.9", 2, "calm|cozy|classic", "christmas"),
 "chestnuts":        (r"chestnuts", "Nat King Cole The Christmas Song ~0:11.7", 1, "calm|cozy|fireside", "christmas"),
 "somewhere_memory": (r"somewhere.?in.?my.?memory", "John Williams Somewhere in My Memory (Home Alone)", 1, "calm|nostalgic|tender", "christmas"),
 "jingle_bells_viibez": (r"jingle.?bells", "Viibez Jingle Bells remix 0:00", 4, "upbeat|playful|hype", "christmas"),
 "rockin_around":    (r"rockin.?around", "Brenda Lee Rockin' Around the Christmas Tree", 4, "upbeat|retro|festive", "christmas"),
 "baby_please":      (r"baby.?please.?come.?home", "Darlene Love Christmas (Baby Please Come Home)", 4, "upbeat|retro", "christmas"),
 "boombastic_tiktok":(r"boombastic", "Shaggy - Boombastic (Sting Remix), normal speed, TikTok music id 6926732577592051713; in-point ~0:21.6 on the CapCut file (Shazam song in-point 18-21 s; second own cluster 18.5)", 5, "hype|goofy|funny|swagger", "ski|streetwear|funny"),
 "free_bird":        (r"free.?bird", "Lynyrd Skynyrd Free Bird solo ~0:14 (meme cue)", 4, "goofy|epic|meme|funny", "ski|funny"),
 "be_my_baby":       (r"be.?my.?baby", "The Ronettes Be My Baby", 3, "retro|romantic", "general"),
 "mambo_no_5":       (r"mambo", "Perez Prado - Mambo No. 5 from 1.2 s (RollyMew 20.8M)", 4, "playful|retro|funny", "pet|oldies"),
 "give_it_up":       (r"give.?it.?up.?to.?me", "Sean Paul Give It Up To Me", 5, "hype|party", "ski|party"),
 "velvet_glow":      (r"velvet.?glow", "Velvet Glow (TikTok sound)", 1, "calm|cozy|ASMR", "christmas|cozy"),
 "family_christmas": (r"^family christmas", "Family Christmas (TikTok sound)", 2, "calm|cozy", "christmas|cozy"),
}

def canon(name):
    s = str(name).lower()
    for k, (rx, *_) in SONGS.items():
        if re.search(rx, s): return k
    return None

def _product_group(prod):
    from .worlds import WORLDS
    for k, w in WORLDS.items():
        if prod in w["corpus_products"]: return k
    return None

def build():
    rows = []
    e = pd.read_csv(f"{REPO}/private/edits/edits.csv")
    c = pd.read_csv(f"{REPO}/private/corpus/corpus.csv", low_memory=False)
    m = e.merge(c[["key", "product", "format"]], left_on="reel_key", right_on="key", how="left")
    for r in m.itertuples():
        k = canon(r.song)
        if k: rows.append(dict(song=k, src="own_capcut", version_file=r.song, offset=r.song_offset_s, views=r.views if r.primary else None,
                               product=_product_group(r.product) if isinstance(r.product, str) else None, format=r.format, category=None, reel=r.reel_key))
    for r in c[(c.source == "own") & c.song.notna()].itertuples():
        k = canon(r.song)
        if k: rows.append(dict(song=k, src="own_audio_match", version_file=r.song, offset=r.song_offset, views=r.views,
                               product=_product_group(r.product), format=r.format, category=r.category, reel=r.key))
    inv = pd.read_csv(f"{REPO}/data/features/inventory.csv", low_memory=False)
    for r in inv[(inv.source != "own") & inv.audio_label.notna()].itertuples():
        k = canon(r.audio_label)
        if k: rows.append(dict(song=k, src="research_library", version_file=r.audio_label, offset=None, views=r.views,
                               product=None, format=r.format_ref if isinstance(r.format_ref, str) else None, category=r.category, reel=r.corpus_key if isinstance(r.corpus_key, str) else r.uid))
    ev = pd.DataFrame(rows)
    ev.to_csv(f"{REPO}/private/evidence/music_evidence.csv", index=False)
    out = []
    for k, (rx, ver, en, mood, niche) in SONGS.items():
        g = ev[ev.song == k] if len(ev) else ev
        own = g[g.src != "research_library"].dropna(subset=["views"]).drop_duplicates("reel")
        ext = g[g.src == "research_library"].dropna(subset=["views"]).drop_duplicates("reel")
        offs = g[g.src == "own_capcut"].offset.dropna()
        prov = []
        for p, gg in own.groupby("product"):
            prov.append(f"{p}:{int(gg.views.max())}({'|'.join(sorted(set(gg.format.dropna())))})")
        out.append(dict(song=k, version=ver, energy=en, mood=mood, niche=niche,
                        capcut_offset_s=round(float(offs.median()), 2) if len(offs) else None,
                        n_own_drafts=int((g.src == "own_capcut").sum()) if len(g) else 0, own_posted=len(own),
                        own_best_views=int(own.views.max()) if len(own) else 0, own_hits=int((own.views >= HIT_ABS_VIEWS).sum()),
                        proven_on=";".join(prov), ext_n=len(ext), ext_best_views=int(ext.views.max()) if len(ext) else 0,
                        ext_categories="|".join(sorted(set(ext.category.dropna().astype(str))))[:120],
                        proven=bool((len(own) and own.views.max() >= HIT_ABS_VIEWS) or (len(ext) and ext.views.max() >= 1e6))))
    STYLE_INPOINTS = {"last_christmas": 170.5, "beginning_to_look": 32.4, "free_bird": 15.0, "aiwfc_intro": 49.6, "holly_jolly": 0.1,
                      "boombastic_tiktok": 21.9, "let_it_snow": 0.9, "chestnuts": 14.2, "somewhere_memory": 104.0}   # style/STYLE_GUIDE.md §5
    for r in out:
        if r["song"] in STYLE_INPOINTS: r["capcut_offset_s"] = STYLE_INPOINTS[r["song"]]
    reg = _regions()
    for r in out: r["region_skew"] = reg.get(r["song"], "unknown")
    lib = pd.DataFrame(out).sort_values(["proven", "own_best_views"], ascending=False)
    os.makedirs(f"{REPO}/learning", exist_ok=True)
    lib.to_csv(f"{REPO}/learning/music_library.csv", index=False)
    return lib

def _regions():
    """region_skew per song id from audience/audio_regions.md (table: `song_id` ... | region_skew | note)."""
    p = os.path.join(REPO, "audience", "audio_regions.md"); out = {}
    if not os.path.exists(p): return out
    for line in open(p, encoding="utf-8"):
        m = re.search(r"\(`([a-z0-9_]+)`\)", line)
        if m and line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 4: out[m.group(1)] = cells[3].replace("*", "").strip()
    return out

def load():
    p = f"{REPO}/learning/music_library.csv"
    return pd.read_csv(p) if os.path.exists(p) else build()

def select(profile, fmt, video_energy, slot="core", n=3):
    """Rank songs for (product, format). Core slots: proven songs only, niche + energy match, no profile bans.
    Returns list of dicts with song, offset, score, why; and rejected list with reasons."""
    lib = load(); pk = profile["product_key"]; bans = [b.lower() for b in profile.get("music_forbidden", [])]
    niche = {"brickhood_mask": "ski", "minionmask": "ski", "trumpglow": "patriot"}.get(pk, "christmas")   # D115: minionmask got Christmas songs, trumpglow Wham!
    ranked, rejected = [], []
    if niche == "patriot":                   # TrumpGlow/PatriotGlow songs live in music/songs.json (slug patriotglow, research/trumpglow/SONGS.md), not the Christmas library
        sj = json.load(open(os.path.join(REPO, "music", "songs.json")))
        for k, v in sj.items():
            if "patriotglow" in (v.get("slug") or []) and os.path.exists(v.get("file", "") or ""):
                ranked.append(dict(song=k, version=v["song"], offset_s=v.get("in_point_s", 0), energy=4, region="US-skewed", score=2.0,
                                   why="patriotglow audience song (songs.json slug; research/trumpglow/SONGS.md; in-point verified)"))
        return ranked[:n], [dict(song=r.song, reason="niche christmas != patriot") for r in lib.itertuples()]
    for r in lib.itertuples():
        why = []
        if any(b.split(" (")[0] in r.version.lower() or b.split(" (")[0] in r.song.replace("_", " ") for b in bans) or \
           (niche == "ski" and "christmas" in r.niche and "ski" not in r.niche and any("christmas songs" in b for b in bans)):
            rejected.append(dict(song=r.song, reason="banned by product profile")); continue
        if niche not in r.niche.split("|") and not (niche == "christmas" and "cozy" in r.niche):
            rejected.append(dict(song=r.song, reason=f"niche {r.niche} != {niche}")); continue
        own_here = [x for x in str(r.proven_on).split(";") if x.startswith(pk + ":")]
        own_here_best = max([int(x.split(":")[1].split("(")[0]) for x in own_here] or [0])
        gap = abs(r.energy - video_energy)
        if own_here_best >= HIT_ABS_VIEWS: score = 3 + 0.5 * np.log10(own_here_best / HIT_ABS_VIEWS);   # log scale: a 2x own-product views gap beats the 0.1 region prior why.append(f"proven on this product ({own_here[0]})")
        elif r.proven and gap <= 1: score = 2 - gap * 0.3 + min(r.own_best_views, 5e5) / 1e6; why.append(f"proven in niche (own best {r.own_best_views:,}, ext best {r.ext_best_views:,}); energy gap {gap}")
        elif r.proven:
            rejected.append(dict(song=r.song, reason=f"energy {r.energy} vs video {video_energy}")); continue
        else:
            if slot != "experiment": rejected.append(dict(song=r.song, reason="unproven (experiment slots only)")); continue
            score = 0.5 - gap * 0.2; why.append("UNPROVEN - experiment slot")
        if gap > 1 and own_here_best < HIT_ABS_VIEWS and slot != "experiment":
            rejected.append(dict(song=r.song, reason=f"energy {r.energy} vs video {video_energy}")); continue
        from . import perf_feedback as _pf; pw = _pf.weight(pk, "song", r.song)                # D119
        if pw != 1.0: score *= pw; why.append(f"own-post perf weight x{pw}")
        if r.song in profile.get("music_preferred", []): score += 1.0; why.append("Omar-preferred for this product world")
        rs = str(getattr(r, "region_skew", "unknown"))
        if rs in ("US-skewed", "tier1_global"): score += 0.1; why.append(f"region {rs}")
        elif rs in ("UK-only", "non-target") and slot != "experiment": rejected.append(dict(song=r.song, reason=f"region {rs}")); continue
        ranked.append(dict(song=r.song, version=r.version, offset_s=r.capcut_offset_s, energy=int(r.energy), region=str(getattr(r, "region_skew", "unknown")), score=round(score, 3), why="; ".join(why)))
    ranked.sort(key=lambda d: -d["score"])
    return ranked[:n], rejected

if __name__ == "__main__":
    lib = build(); print(lib[["song", "energy", "niche", "capcut_offset_s", "own_posted", "own_best_views", "own_hits", "proven_on", "ext_n", "ext_best_views", "proven"]].to_string())
