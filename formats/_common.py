"""Shared constants + renderer for the Hookforge format library.
Single source of truth: formats are defined as Python dicts in _formats_*.py,
_build.py renders <slug>.md + <slug>.json + INDEX.md. Edit the dicts, re-run
`python3 formats/_build.py`. Never hand-edit the generated .md/.json."""
import json, re, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "engine"))
from hookforge.config import IPHONE12_SUFFIX as SUFFIX, recency_weight, RECENCY   # single source of truth (D28/D34)

# Source keys used in evidence rows
SOURCES = {
    "H": "/workspace/team/hooks/hook_features.csv (78 posted reels, hand-coded + measured first 3 s)",
    "B": "/workspace/team/body/reels_summary.csv + shots.csv (frame-accurate cuts, songs, Insights retention)",
    "X": "/workspace/team/external/external_reels.csv (72 external Q4 reels, TikTok/IG public counters, paid flag)",
    "XA": "/workspace/team/external/analysis.jsonl (auto scene cuts of external files; misses Seedance jump cuts, so counts are lower bounds)",
    "V": "/workspace/team/viral_research/REPORT.md (Viral Research bot, Oct 4-18 2026 window)",
    "P": "/workspace/playbook/PLAYBOOK.md v2.1",
    "M": "/workspace/hf_match/matches.csv + prompt_analysis.md (Higgsfield generations verified shot-for-shot against posted reels)",
    "I": "Business Suite Insights (/workspace/merryglow/insights_reels.csv etc., via PLAYBOOK §2.1)",
}

PACK_RULE = ("Omar rule 2026-10-18 19:49 PT: hook = its own single 4 s generation at full resolution (1080p); "
             "every other generation 720p; body shots packed 2 per 4 s Seedance 2.5 generation, joined by "
             "'HARD CUT at 2s, no transition'. Every prompt ends with the iPhone 12 realism suffix.")

def views_num(v):
    if v in (None, ""): return 0.0
    if isinstance(v, (int, float)): return float(v)
    s = str(v).replace(",", "").strip()
    m = {"K": 1e3, "M": 1e6}
    return float(s[:-1]) * m[s[-1]] if s[-1] in m else float(s)

def fmt_views(v):
    n = views_num(v)
    if n >= 1e6: return f"{n/1e6:.1f}M".replace(".0M", "M")
    if n >= 1e3: return f"{n/1e3:.1f}K".replace(".0K", "K")
    return f"{int(n)}"

import datetime as _dt
AS_OF = _dt.date(2026, 10, 18)
FRESH_DAYS = RECENCY["full_days"]

def ext_age(e):
    try: return (AS_OF - _dt.date.fromisoformat(e.get("posted") or "")).days
    except ValueError: return None

def ext_weight(e):
    """config.recency_weight with the row's inclusion_rule: 90d_20m = near-full (no decay); else RECENCY decay.
    Undated external rows get the weak-prior floor."""
    a = ext_age(e); rule = e.get("inclusion_rule")
    if a is None and rule != "90d_20m": return RECENCY["prior_floor"]
    return recency_weight(a, "external", inclusion_rule=rule)

def ext_fresh(e):
    return ext_weight(e) >= 0.9

def score(evidence):
    """Transparent evidence-strength score (documented in INDEX.md).
    Internal (Omar's pages, organic per Omar): >=1M 4, >=100K 3, >=50K 2, >=20K 1.
    External organic (no paid/Spark flag): >=5M 3, >=1M 2, >=400K 1, >=100K 0.5.
    External flagged (paid/Spark possible): half weight. Flops add 0 but count toward hit rate.
    Freshness (Omar 2026-10-18): internal reels keep FULL weight regardless of age. The 14-day freshness
    rule applies only to external reels via config.recency_weight (+ inclusion_rule): 14d_1m rows decay after
    14 days (exp, tau 7 d, floor 0.05; undated = floor); 90d_20m mega-viral rows keep weight 0.95. An external
    reel counts as an external winner only when its weight >= 0.9."""
    s = 0.0; iw = it = xw = 0
    for e in evidence:
        n = views_num(e.get("views"))
        if e["origin"] == "internal":
            if e["role"] == "context": continue
            it += 1
            if n >= 50e3: iw += 1
            s += 4 if n >= 1e6 else 3 if n >= 1e5 else 2 if n >= 5e4 else 1 if n >= 2e4 else 0
        else:
            w = (0.5 if e.get("flag") else 1.0) * ext_weight(e)
            pts = 3 if n >= 5e6 else 2 if n >= 1e6 else 1 if n >= 4e5 else 0.5 if n >= 1e5 else 0
            s += w * pts
            if pts and not e.get("flag") and ext_fresh(e): xw += 1
    return round(s, 1), iw, it, xw

FLAG_VIDEO_RECREATE = "Add a small American flag somewhere in the background."
FLAG_SCRIPTED = "A small American flag is visible in the background."

def _with_flag(p, recreate):
    """D24 (Omar R03): US flag in the background of EVERY clip/still. Inserted before the realism suffix."""
    if p is None or "flag" in p.lower(): return p
    body = p.rstrip()
    tail = ""
    if body.endswith(SUFFIX): body, tail = body[: -len(SUFFIX)].rstrip(), SUFFIX
    line = FLAG_VIDEO_RECREATE if recreate else FLAG_SCRIPTED
    return (body + "\n" + line + ("\n\n" + tail if tail else "")).strip()

def ensure_flags(f):
    for g in f["generation_plan"]["generations"]:
        rec = "<<<video_1>>>" in (g.get("prompt") or "")
        g["prompt"] = _with_flag(g["prompt"], rec)
        if g.get("alt_prompt"): g["alt_prompt"] = _with_flag(g["alt_prompt"], "<<<video_1>>>" in g["alt_prompt"])
        sf = g.get("start_frame")
        if sf and sf.get("prompt"): sf["prompt"] = _with_flag(sf["prompt"], False)

def ensure_start_frames(f):
    """Omar 2026-10-18: start-frame (still image) prompts must ALSO end with the realism suffix.
    Every gen whose prompt or alt_prompt animates 'the start image' gets a start_frame: hand-written
    (T8/T9) where given, chained from another render's last frame, or auto-built from SHOT 1 of a scripted pack."""
    from _blocks import still_from_pack
    for g in f["generation_plan"]["generations"]:
        texts = [g["prompt"]] + ([g["alt_prompt"]] if g.get("alt_prompt") else [])
        if g.get("start_frame") or not any("start image" in t for t in texts): continue
        inp = g.get("inputs", "")
        if "last frame" in inp:
            g["start_frame"] = {"template": "chained", "source": inp.split(";")[0].strip(), "prompt": None}
            continue
        assert "Image-to-video from the start image" not in g["prompt"], f"{f['slug']} {g['id']}: image-to-video hook needs a hand-written start_frame"
        for t in texts:
            p = still_from_pack(t)
            if p:
                g["start_frame"] = {"template": "T8 (auto: first instant of SHOT 1)" + (" · for alt_prompt" if t is not g["prompt"] else ""), "prompt": p}
                break
        assert g.get("start_frame"), f"{f['slug']} {g['id']}: references a start image but has no start_frame"

def check_prompts(f):
    for g in f["generation_plan"]["generations"]:
        p = g["prompt"].rstrip()
        assert p.endswith(SUFFIX), f"{f['slug']} {g['id']} missing suffix"
        if g["kind"] == "hook":
            assert g["resolution"] == "1080p" and g["duration_s"] == 4, f"{f['slug']} hook gen rule"
        else:
            assert g["resolution"] == "720p", f"{f['slug']} body res rule"
            assert "HARD CUT at 2s, no transition" in p, f"{f['slug']} {g['id']} missing hard cut"
        assert "flag" in p.lower(), f"{f['slug']} {g['id']} missing US flag (D24)"
        sf = g.get("start_frame")
        if sf and sf.get("prompt"):
            assert "flag" in sf["prompt"].lower(), f"{f['slug']} {g['id']} still missing US flag (D24)"
            assert sf["prompt"].rstrip().endswith(SUFFIX), f"{f['slug']} {g['id']} start-frame still missing suffix"
        if any("start image" in t for t in [p, g.get("alt_prompt") or ""]):
            assert sf and (sf.get("prompt") or "last frame" in (sf.get("source") or "")), f"{f['slug']} {g['id']} start image without a suffixed still or a chain"
        if g.get("alt_prompt"):
            a = g["alt_prompt"].rstrip()
            assert a.endswith(SUFFIX), f"{f['slug']} {g['id']} alt missing suffix"
            if g["kind"] != "hook":
                assert "HARD CUT at 2s, no transition" in a, f"{f['slug']} {g['id']} alt missing hard cut"

def posted_cell(e):
    if e["origin"] == "internal": return "full weight"
    w = ext_weight(e)
    tag = " (90d_20m mega-viral)" if e.get("inclusion_rule") == "90d_20m" else ("" if w >= 0.9 else f" (aging, w={w:.2f})")
    return (e.get("posted") or "undated") + tag

def render_md(f):
    sc, iw, it, xw = f["_score"]
    L = []
    A = L.append
    A(f"# {f['name']}  (`{f['slug']}`)")
    A(f"**Tier {f['tier']} · evidence score {sc} · internal hits {iw}/{it} reels ≥50K · external organic winners {xw}**  ")
    A(f"Status: {f['status']}  ")
    A("Generated by `formats/_build.py` from `formats/_formats_*.py`. Do not hand-edit; edit the source dict.\n")
    A("## 1. What it is, and why it works (evidence-backed)")
    A(f["summary"] + "\n")
    for w in f["why"]: A(f"- {w}")
    A("\n## 2. Product fit")
    A("| Product type | Fit | Evidence |"); A("|---|---|---|")
    for p in f["product_fit"]: A(f"| {p['type']} | {p['fit']} | {p['evidence']} |")
    A("\n## 3. Timing template")
    A(f"Target length **{f['timing']['length']}**. {f['timing']['basis']}\n")
    A("| # | Start → end (s) | Shot | Content | Camera | On-screen text | Gen slot |"); A("|---|---|---|---|---|---|---|")
    for i, s in enumerate(f["timing"]["shots"], 1):
        A(f"| {i} | {s['t']} | **{s['shot']}** | {s['content']} | {s['camera']} | {s.get('text','—')} | {s.get('gen','—')} |")
    A("\n**Measured winner cut lists (the template is built from these):**")
    for m in f["timing"]["measured"]: A(f"- {m}")
    A("\n**Timing rules:**")
    for r in f["timing"]["rules"]: A(f"- {r}")
    A("\n## 4. On-screen text")
    A(f"**Placement/style:** {f['text']['style']}\n")
    A("| Pattern (slots in {braces}) | Tag | Source reel(s) |"); A("|---|---|---|")
    for t in f["text"]["patterns"]: A(f"| `{t['pattern']}` | {t['tag']} | {t['source']} |")
    A("\n**Text rules:**")
    for r in f["text"]["rules"]: A(f"- {r}")
    A("\n## 5. Caption + CTA")
    A(f"```\n{f['caption']['template']}\n```")
    A(f"Keyword bank: {', '.join('`'+k+'`' for k in f['caption']['keywords'])}  ")
    for r in f["caption"]["rules"]: A(f"- {r}")
    A("\n## 6. Music")
    A("| Pick | Track · section | Reel start | Evidence |"); A("|---|---|---|---|")
    for m in f["music"]["picks"]: A(f"| {m['rank']} | {m['track']} | {m['start']} | {m['evidence']} |")
    for r in f["music"]["rules"]: A(f"- {r}")
    gp = f["generation_plan"]
    A("\n## 7. Higgsfield generation plan (Seedance 2.5)")
    A(f"_{PACK_RULE}_\n")
    A(f"{gp['summary']}\n")
    A("| Gen | Kind | Res | Len | Shots inside | Feeds timing rows |"); A("|---|---|---|---|---|---|")
    for g in gp["generations"]:
        A(f"| {g['id']} | {g['kind']} | {g['resolution']} | {g['duration_s']} s | {g['shots']} | {g['feeds']} |")
    A("")
    for g in gp["generations"]:
        A(f"### {g['id']} · {g['title']}")
        A(f"Inputs: {g['inputs']}  ")
        A(f"Basis: {g['basis']}")
        A("```\n" + g["prompt"].strip() + "\n```")
        if g.get("alt_prompt"):
            A(f"Alt (no reference clip available; scripted, T5-style): ")
            A("```\n" + g["alt_prompt"].strip() + "\n```")
        sf = g.get("start_frame")
        if sf:
            if sf.get("prompt"):
                A(f"Start-frame still ({sf['template']}; image model, ends with the iPhone 12 suffix): ")
                A("```\n" + sf["prompt"].strip() + "\n```")
            else:
                A(f"Start frame: chained, {sf['source']} (no new still).")
    A("**Generation rules:**")
    for r in gp["rules"]: A(f"- {r}")
    A("\n## 8. Evidence table")
    A("Origin: internal = Omar's pages (organic per Omar). external = competitor reels (TikTok plays ≠ FB views; read family patterns, not absolutes). ⚑ = TikTok paid/Spark flag present (half weight). Posted: external reels older than 14 days before " + str(AS_OF) + " (or undated) are weighted by config.recency_weight (full ≤14 d, exp decay τ=7 d, floor 0.05; undated = floor; 90d_20m mega-viral rows 0.95); internal reels keep full weight at any age.\n")
    A("| Reel | Platform · page | Views | Shares | Posted | Role | Hook / note | Source |"); A("|---|---|---|---|---|---|---|---|")
    for e in sorted(f["evidence"], key=lambda e: (e["origin"] != "internal", -views_num(e.get("views")))):
        ref = f"[{e['id']}]({e['url']})" if e.get("url") else e["id"]
        A(f"| {ref} | {e['platform']} · {e['page']} | {fmt_views(e.get('views'))}{' ⚑' if e.get('flag') else ''} | {e.get('shares') or '—'} | {posted_cell(e)} | {e['role']} | {e['note']} | {e['src']} |")
    A("\n## 9. Known failure modes")
    for x in f["failures"]: A(f"- {x}")
    A("\n## 10. Original-variant rules (experiments, ≤20% of output)")
    for v in f["variants"]:
        A(f"- **{v['name']}.** {v['rule']} _Proof of concept:_ {v['proof']} _Kill/promote:_ {v['gate']}")
    A("\n## 11. Backtest hooks (machine checks for engine/backtest)")
    for c in f["checks"]: A(f"- `{c['id']}`: {c['rule']} ({c['cite']})")
    A("\n## 12. Open questions / confidence limits")
    for q in f["open"]: A(f"- {q}")
    A("\n## 13. Creative-director self-review (done before publishing this spec)")
    for q in f["review"]: A(f"- {q}")
    return "\n".join(L) + "\n"

def render_json(f):
    d = {k: v for k, v in f.items() if not k.startswith("_")}
    sc, iw, it, xw = f["_score"]
    d["evidence_strength"] = {"score": sc, "internal_hits_ge50k": iw, "internal_tested": it, "external_organic_winners": xw}
    d["realism_suffix"] = SUFFIX
    d["pack_rule"] = PACK_RULE
    return json.dumps(d, ensure_ascii=False, indent=2)
