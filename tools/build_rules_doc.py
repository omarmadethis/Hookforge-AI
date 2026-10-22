#!/usr/bin/env python3
"""Render docs/RULES.md (human-readable) from rules/master_rules.json, the same source the master gate enforces.
    python3 tools/build_rules_doc.py           # rewrite docs/RULES.md
    python3 tools/build_rules_doc.py --check   # exit 1 if docs/RULES.md is out of date
Add or change a rule in rules/build_master.py, run it, then run this."""
import json, os, sys
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC, OUT = os.path.join(REPO, "rules", "master_rules.json"), os.path.join(REPO, "docs", "RULES.md")

GROUPS = [
    ("Files and delivery", lambda r: r["id"] in ("MR01", "MR02", "MR46", "MR47")),
    ("Generation (Higgsfield)", lambda r: r["id"] in ("MR03", "MR04", "MR05", "MR06", "MR07", "MR08", "MR09", "MR10")),
    ("Look, cast and realism", lambda r: r["id"] in ("MR11", "MR12", "MR13", "MR14", "MR15", "MR16", "MR17", "MR20", "MR49", "MR51")),
    ("Uniqueness, products and pages", lambda r: r["id"] in ("MR18", "MR19", "MR21")),
    ("Hook and structure", lambda r: r["id"] in ("MR22", "MR23", "MR24", "MR30")),
    ("Music", lambda r: r["id"] in ("MR25", "MR26", "MR27", "MR28")),
    ("Edit and on-screen cards", lambda r: r["id"] in ("MR29",) or 31 <= int(r["id"][2:]) <= 39 or r["id"] == "MR50"),
    ("Captions and publishing", lambda r: 40 <= int(r["id"][2:]) <= 45),
]
CHECK = {"auto": "automatic", "auto+manual": "automatic + reviewer sign-off", "manual": "reviewer sign-off",
         "process": "process rule", "superseded": "SUPERSEDED"}
FIX = {"none": "no auto-fix", "regen": "regenerate footage (within the approved credit cap)"}

def render(rules):
    seen, out = set(), []
    out += ["# Hookforge rules", "",
            "Generated from `rules/master_rules.json` by `tools/build_rules_doc.py`; do not edit by hand. The master gate",
            "(`engine/hookforge/master_gate.py`) enforces these on every file before it is shown to anyone or published.",
            "The machine table with sources is `rules/MASTER_RULES.md`.", "",
            f"**{len(rules)} rules.** How each is checked: *automatic* (the gate measures it), *reviewer sign-off* (a human or",
            "vision reviewer confirms it in the spec's `confirm` block), *process* (a habit, not a file check).", "",
            "**Fix order when a check fails:** free fixes first (strip metadata, re-edit cards, re-lay the song, rewrite the",
            "caption), re-run the gate, loop up to 8 rounds. Footage problems are regenerated only inside an approved credit cap;",
            "otherwise the gate stops at `NEEDS_REGEN_WITHIN_CAP` with the plan. Nothing ships without a PASS report for that exact file.", ""]
    for title, pred in GROUPS:
        rs = [r for r in rules if r["id"] not in seen and pred(r)]
        if not rs: continue
        out += [f"## {title}", ""]
        for r in rs:
            seen.add(r["id"]); fx = r.get("fix", "none")
            fx = FIX.get(fx, fx.replace("free:", "free fix: "))
            how = CHECK.get(r["check"], r["check"]) + (f" (`{r['fn']}`)" if r.get("fn") else "")
            out.append(f"- **{r['id']}** {r['rule']}  \n  _Check:_ {how}. _Fix:_ {fx}. _Applies to:_ {r['applies']}.")
        out.append("")
    rest = [r for r in rules if r["id"] not in seen]
    if rest:
        out += ["## Other", ""] + [f"- **{r['id']}** {r['rule']}  \n  _Check:_ {CHECK.get(r['check'], r['check'])}." for r in rest] + [""]
    return "\n".join(out)

if __name__ == "__main__":
    txt = render(json.load(open(SRC)))
    if "--check" in sys.argv:
        ok = os.path.exists(OUT) and open(OUT).read() == txt
        print("docs/RULES.md in sync" if ok else "docs/RULES.md is OUT OF DATE: run python3 tools/build_rules_doc.py"); sys.exit(0 if ok else 1)
    open(OUT, "w").write(txt); print(f"wrote {OUT}")
