"""Tier X: problem → solution (demoted; kept so the engine can refuse it with reasons)."""
from _common import SUFFIX
from _ev import I, X
from _blocks import script_pack

F = []
F.append({
"slug": "problem-solution", "name": "Problem → solution (\"The problem.. → Vs.. → The solution\")", "tier": "X",
"status": "DEMOTED. 0 for 4 on our pages (HJ 5.6K and 2.7K; Purrventure ×2 at ~3 views). The PROBLEM_CHASE opener went 0/3 ≥50K, median 4.2K (hooks REPORT). One external gadget winner (429K). Do not lead with it on gifts, decor or pets.",
"summary": "A chaos/problem scene with no product, a 'Vs..' card, then the product as the fix. It fails because the first frame shows neither the product nor a recipient, and both are proven requirements.",
"why": [
 "PROBLEM_CHASE opener: 3 HJ reels, none ≥50K, median 4.2K, best 5.6K. It was the only archetype that separated statistically from PALLET (hooks REPORT §1.4).",
 "Two of three Purrventure reels used it; both sat at ~3 views (PLAYBOOK §12).",
 "Exception: tryglowmas 'The problem😬' laser-tag set for boy moms, 429K on IG (external §3d).",
],
"product_fit": [{"type": "Gadget / toy", "fit": "EXPERIMENT ONLY", "evidence": "tryglowmas 429K"}, {"type": "Wearable, decor, pet", "fit": "NO", "evidence": "0/4 internal"}],
"timing": {"length": "12-15 s", "basis": "tryglowmas 429K cuts 3.97 | 5.02 | 7.62 | 8.97 | 12.32 | 13.67 | END 15.1 (XA). HJ 5.6K cuts 3.800 | 8.433 (a 4.6 s shot) | 10.533 | 11.467 | 12.400 | END 13.96.",
 "shots": [
  {"t": "0.0 → 3.0", "shot": "HOOK: problem WITH product cue", "content": "the problem scene, but the product is visible in frame by 1 s (fixing the measured failure)", "camera": "locked", "text": "The problem😬", "gen": "H1 (trim 3.0)"},
  {"t": "3.0 → 5.0", "shot": "SOLUTION reveal", "content": "product in hand", "camera": "locked", "text": "Vs..", "gen": "B1·S1"},
  {"t": "5.0 → 7.0", "shot": "USE", "content": "first use", "camera": "locked", "text": "held", "gen": "B1·S2"},
  {"t": "7.0 → 8.5", "shot": "ACTIVATION", "content": "switch-on", "camera": "macro", "text": "The solution 😊 on this cut", "gen": "B2·S1"},
  {"t": "8.5 → 12.5", "shot": "PAYOFF ×2", "content": "kids/family enjoying it", "camera": "locked", "text": "held", "gen": "B2·S2 + B3"},
 ],
 "measured": ["HJ 5.6K: a 4.6 s second shot (slow), violating the ≤2.2 s pre-activation rule.", "tryglowmas 429K: 15.1 s."],
 "rules": ["If used at all: product in frame by 1 s, and no shot longer than 2.2 s before activation."]},
"text": {"style": "House style.", "patterns": [{"pattern": "The problem😬 → (solution)", "tag": "P (ext, IG)", "source": "tryglowmas 429K"}, {"pattern": "The Problem😕🎄 → Vs.. → The solution", "tag": "FAILED", "source": "HJ 5.6K, 2.7K; PV ~3 views"}], "rules": []},
"caption": {"template": "Problem solved 😏\nSAY \"{KEYWORD}\" and we'll send you the link", "keywords": ["FIXED"], "rules": ["SAY not COMMENT."]},
"music": {"picks": [{"rank": "—", "track": "No proven pick (HJ 5.6K used Last Christmas ~2:48 and flopped)", "start": "—", "evidence": "HJ 5.6K"}], "rules": []},
"generation_plan": {"summary": "Only for a gadget/toy experiment: 3-4 gens (H1 + B1 shown; generate fresh B2/B3 - never reuse footage (D180)).",
 "generations": [
  {"id": "H1", "kind": "hook", "resolution": "720p", "duration_s": 4, "title": "Problem scene with product cue", "shots": "one shot", "feeds": "HOOK", "inputs": "<<<image_1>>> product",
   "basis": "tryglowmas 429K; product-at-0 s fix from hooks REPORT §1.3.",
   "prompt": "Vertical 9:16 iPhone video at a family dinner table: two boys aim toy guns at each other across the plates and mom throws her hands up; the boxed {product} from <<<image_1>>> sits on the counter in the foreground, clearly visible from the first second. Locked camera. Natural sound only: kids yelling, cutlery. No music, no text.\n" + SUFFIX},
  {"id": "B1", "kind": "body", "resolution": "720p", "duration_s": 4, "title": "SOLUTION | USE", "shots": "reveal · use", "feeds": "SOLUTION, USE", "inputs": "<<<image_1>>>", "basis": "T5 pattern.",
   "prompt": script_pack("same house, evening", "mom hands the boys the {product} from <<<image_1>>>.", "the boys set it up in the backyard, excited.", "kids cheering")},
 ], "rules": []},
"evidence": [
 I("1800372894614638", "HeatedJammies", 5.6e3, "flop", "The Problem😕🎄 · PROBLEM_CHASE"),
 I("1054634014080122", "HeatedJammies", 2.7e3, "flop", "The problem..😩"),
 I("pv_1131865399523539", "Purrventure", 3, "flop", "The problem... 😕 · ~3 views", url=None),
 I("pv_2881652105537206", "Purrventure", 3, "flop", "The problem 😡 · ~3 views", url=None),
 X("tryglowmas", "429K", "https://www.instagram.com/reel/DeUySooOwf5/", "The problem😬 → laser tag set (boy moms)"),
],
"failures": ["No product at 0 s.", "Long static problem shot (4.6 s on HJ 5.6K)."],
"variants": [{"name": "Gadget-only test", "rule": "Use only for toys/gadgets, with a product cue at 0 s.", "proof": "tryglowmas 429K.", "gate": "1 test; kill on the first result below page median."}],
"checks": [{"id": "ps.blocked_categories", "rule": "reject if the product category is wearable, decor or pet", "cite": "0/4 internal"}],
"open": ["Purrventure was a ~3-view page, so its two flops are weak evidence on their own; HJ's 0/3 PROBLEM_CHASE result carries the demotion."],
"review": ["Kept as a spec so the engine can explicitly refuse it, with reasons, when someone asks for it."]})
