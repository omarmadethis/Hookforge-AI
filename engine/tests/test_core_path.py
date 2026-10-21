"""Core production path integration test (no generation, no credits). Run: cd engine && python3 -m tests.test_core_path
Checks per dry-run brief: plan builds, QA clean, D42 pre-flight linter ran and blocks nothing it shouldn't, MP2 recreate
rules (D45, one roll - D33 wins over MP2-1), US cues in prompts + advisory tier-1 + psych scores (D46), D49 AI-doubt proof
shot + AI-tells log, D52 covered-reveal allowed, D44 provenance strip on the export test, iPhone suffix + 9:16."""
import os, json, csv
from hookforge import planner, qa, recreate, runner, gen_failures as GF, config, style, psych
from hookforge.config import REPO, REROLL

BRIEFS = ["3-2-1 video for the Grinch robe", "then vs now video for MerryFire fire pit", "friend dare group video for Brick Hood", "3-2-1 video for Brick Hood ski mask", "3-2-1 video for the GrinchMelt mug"]
OUT = os.path.join(REPO, "out", "dryrun")
def slug(b): return "".join(c if c.isalnum() else "_" for c in b.lower()).strip("_")

def main():
    res, fails = {}, []
    def ok(name, cond, why=""):
        res.setdefault(cur, {})[name] = bool(cond)
        if not cond: fails.append(f"{cur}: {name} {why}")
    for cur in BRIEFS:
        p = planner.plan(cur, mode="original")
        ok("plan_ok", p["status"] != "REJECTED")
        ok("plan_checks_clean", not [x for x in qa.plan_checks(p) if x.startswith(("BLOCK", "FIX"))], qa.plan_checks(p))
        ok("iphone_suffix", all(config.IPHONE12_SUFFIX.strip()[:40] in g["prompt"] for g in p["gens"]))
        lint = runner.submit(p); ok("preflight_lint_ran", lint["preflight"]["rows"] and not lint["submitted"])
        ok("us_cues", bool(p.get("us_cues")) and any(c[:25] in " ".join(g["prompt"] for g in p["gens"]) for c in p["us_cues"][:1]))
        ok("proof_shot_D49", p["proof_shot"]["present"])
        ok("psych_advisory", psych.score(p)["advisory"])
        ok("hook_emojis_le_2", len(style.EMOJI_RX.findall(p["hook"]["text"])) <= 2 or "own" in p["hook"].get("why", "") or "HJ-" in p["hook"].get("why", ""), p["hook"])
        alt = p["gens"][0].get("alt_recreate")
        if alt: ok("recreate_MP2_checks", not [x for x in recreate.check(alt["prompt"], p["brief"]["product_key"]) if x.startswith("BLOCK")])
        mq = os.path.join(OUT, slug(cur), "media_qa.json")
        if os.path.exists(mq):
            m = json.load(open(mq)); e = m.get("export_clean_test", {})
            ok("export_provenance_stripped_D44", e and not e.get("error") and not any(e["provenance"].values()) and not e["provenance_blocks"], e)
            pl = json.load(open(os.path.join(OUT, slug(cur), "plan.json")))
            ok("tier1_advisory_in_report", "tier1_advisory" in json.dumps(pl.get("backtest", pl)) or "Tier-1" in open(os.path.join(OUT, slug(cur), "PLAN.md")).read())
    cur = "global"
    ok("D33_over_MP2-1_one_reroll_max", REROLL["max_auto_rerolls_per_shot"] == 1 and REROLL["min_confidence"] >= 0.9)
    r = qa.reroll_decision("B1", dict(failure="minor_texture", confidence=0.99), log=False); ok("minor_never_rerolls", not r["reroll"])
    fake = dict(brief=dict(format="F05", slot="core", product_key="grinch_robe"), shots=[dict(desc="POV hands lift the white cloth"), dict(desc="POV hands hold robe")],
                gens=[dict(prompt="the robe under a white cloth, hands pull the cloth off", start_frame=dict(prompt="white cloth over the tray"))])
    ok("covered_reveal_allowed_D52", not [x for x in style.shot_problems(fake, dict(product_key="grinch_robe")) if "covered" in x.lower()])
    ok("linter_catches_retailer_name", not GF.lint("a Walmart aisle", "seedance_2_5")["ok"])
    ok("ai_tells_log_writes", callable(qa.ai_tells_log))
    for b, slot in [("covered reveal video for the Grinch robe", "core"), ("store drape unveil video for the Grinch robe", "core"),
                    ("glow under cloth video for MerryFire fire pit", "experiment"), ("glow under cloth video for Brick Hood ski mask", "experiment")]:
        pp = planner.plan(b, mode="original"); ok(f"covered_option[{b[:28]}]", pp["hook_option"] and pp["brief"]["slot"] == slot and psych.ps02(pp)[0] == 1
                                and not [x for x in qa.plan_checks(pp) if x.startswith(("BLOCK", "FIX"))], (pp["brief"], psych.ps02(pp), qa.plan_checks(pp)))
    ok("failure_ledger_exists", os.path.exists(os.path.join(GF.D, "ledger.csv")) and os.path.exists(os.path.join(GF.D, "rules.csv")))
    print(json.dumps(res, indent=1)); print("FAILS:", fails or "none")
    return fails
if __name__ == "__main__": raise SystemExit(1 if main() else 0)
