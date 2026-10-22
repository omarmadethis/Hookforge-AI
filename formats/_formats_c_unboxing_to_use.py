"""Tier B: unbox-in-hook → use (guard-rail format)."""
from _common import SUFFIX
from _ev import I, X
from _blocks import script_pack

F = []
F.append({
"slug": "unboxing-to-use", "name": "Unbox-in-hook → use (the package opens inside the first 3 s, never later)", "tier": "B",
"status": "MECHANIC. Proven as an opener (Brick Hood POV unbag ×2 at ~61K; MF 63K box carried in by 1 s; MG 98K box in hand) and externally (5.2M, 3.2M, 2.6M, 1.8M). As a BODY block, unboxing is the #1 retention leak.",
"summary": "The product comes out of its package during the hook (POV unbag, lid lift, box handed in), then goes straight into use. Pair it with any text family. The rule that makes it work: no unboxing after 3.8 s, and no box shot longer than 2.0 s.",
"why": [
 "Box/unbox shots are where viewers leave: the biggest drop-off falls inside BOX/UNBOX on 6/7 then-vs-now reels (0:04-0:06) (body REPORT §3).",
 "Moving the box into the hook moved the drop-off to 0:11, with 66% watched (MG 98K).",
 "Openers that ARE an unbox: Brick Hood POV_UNBAG 61.3K / 61.1K; MF 63K; external zombie.crawler POV unpack 3.2M; jinglenap pulling a dog bed from its package 1.8M; hollyglow shelf-grab 5.2M; lockedlovestore 'Suprise them ❤️🥹' box on fur 2.6M.",
],
"product_fit": [{"type": "Any product with branded packaging", "fit": "YES as an opener", "evidence": "see 'why'"}, {"type": "Products with a slow unbox (assembly)", "fit": "Only with metronomic 1.0-1.2 s beats", "evidence": "PLAYBOOK §6.1 B (MerryTables [L])"}],
"timing": {"length": "9.2-13.5 s",
 "basis": "jinglenap 1.8M: 2.33 | 4.07 | 6.37 | 8.10 | END 9.23; zombie.crawler 3.2M: 4.00 | 7.17 | 10.30 | END 12.07 (XA). Internal openers end the unbox at 2.4-3.8 s (MF 2.367, BH 2.733, MG 3.767).",
 "shots": [
  {"t": "0.0 → 3.0", "shot": "HOOK: unbox", "content": "product out of the package by 2 s, product ≥25% of frame by 2 s", "camera": "POV", "text": "family line ON", "gen": "H1 (trim 3.0)"},
  {"t": "3.0 → 5.0", "shot": "FIRST USE", "content": "product placed/worn", "camera": "locked", "text": "held", "gen": "B1·S1"},
  {"t": "5.0 → 7.0", "shot": "FEATURE", "content": "key feature", "camera": "locked", "text": "held", "gen": "B1·S2"},
  {"t": "7.0 → 8.5", "shot": "ACTIVATION (~66%)", "content": "switch-on", "camera": "handheld macro", "text": "held", "gen": "B2·S1 (1.5)"},
  {"t": "8.5 → 10.5", "shot": "REACTION", "content": "recipient/pet/kids react", "camera": "locked", "text": "held", "gen": "B2·S2"},
  {"t": "10.5 → 12.5", "shot": "PAYOFF (~84%)", "content": "hero / cozy; hard cut", "camera": "locked wide", "text": "held", "gen": "B3 (best 2 s of S1 or S2)"},
 ],
 "measured": ["MF 63K: box carried in by 1 s, HOOK 0-2.367.", "MG 98K: box in hand 0-3.767.", "BH 61.3K: unbag 0-2.733."],
 "rules": ["No box/unbox shot starting after 3.8 s; no box shot longer than 2.0 s anywhere."]},
"text": {"style": "Uses the paired family's line.",
 "patterns": [{"pattern": "DO NOT let your {KIDS} see this..👀🎄", "tag": "P (ext)", "source": "zombie.crawler 3.2M"}, {"pattern": "{Dog MOMS}... This is for you 👀🐶", "tag": "P (ext)", "source": "jinglenap 1.8M"}, {"pattern": "Suprise them ❤️🥹", "tag": "P (ext)", "source": "lockedlovestore 2.6M"}],
 "rules": []},
"caption": {"template": "{paired family caption}\nSAY \"{KEYWORD}\" and we'll send you the link", "keywords": ["{PRODUCT}"], "rules": ["SAY not COMMENT."]},
"music": {"picks": [{"rank": 1, "track": "All I Want for Christmas Is You · 0:00", "start": "reel 0.0", "evidence": "jinglenap 1.8M"}], "rules": ["Otherwise use the paired family's pick."]},
"generation_plan": {"summary": "4 gens.",
 "generations": [
  {"id": "H1", "kind": "hook", "resolution": "720p", "duration_s": 4, "title": "POV unbox", "shots": "one shot", "feeds": "HOOK", "inputs": "<<<image_1>>> product; <<<image_2>>> packaging",
   "basis": "B-UNBOX-POV (prompt_templates) compressed into the hook; BH / zombie.crawler POV.",
   "prompt": "POV: hands hold the {brand} box from <<<image_2>>> on denim-clad knees in a festive American living room, flip the lid open within the first second and lift the {product} from <<<image_1>>> up toward the camera so it fills a third of the frame by two seconds. A golden retriever watches. Handheld phone video. Natural sound only, no music, no text.\n" + SUFFIX},
  {"id": "B1", "kind": "body", "resolution": "720p", "duration_s": 4, "title": "FIRST USE | FEATURE", "shots": "S1 place/wear · S2 feature", "feeds": "FIRST USE, FEATURE", "inputs": "<<<image_1>>>", "basis": "T5 pattern.",
   "prompt": script_pack("same living room", "the {product} from <<<image_1>>> is set in place / put on.", "close on its key feature: {feature}.", "soft room tone")},
  {"id": "B2", "kind": "body", "resolution": "720p", "duration_s": 4, "title": "ACTIVATION | REACTION", "shots": "S1 switch on · S2 reaction", "feeds": "ACTIVATION, REACTION", "inputs": "<<<image_1>>>", "basis": "body REPORT activation insert.",
   "prompt": script_pack("same living room", "macro: a finger switches the {product} on, {activation effect}.", "the recipient's face lights up, hands over mouth, laughing.", "click, gasp, laugh")},
  {"id": "B3", "kind": "body", "resolution": "720p", "duration_s": 4, "title": "PAYOFF A | PAYOFF B", "shots": "two payoff takes", "feeds": "PAYOFF", "inputs": "<<<image_1>>>", "basis": "Payoff locked, medium-wide (body REPORT §2).",
   "prompt": script_pack("same living room at night", "locked medium-wide: the family relaxes with the {product} working beside them.", "locked wide hero of the {product} working, tree lit.", "room tone")},
 ], "rules": []},
"evidence": [
 I("mg_post122111714343432799", "Merry Glow", 97955, "winner", "box in hook · drop-off 0:11", src="H,B,I", url=None),
 I("merryfires_1082602281322454", "MerryFires", 62992, "winner", "box carried in by 1 s", src="H,B,I", url="https://www.facebook.com/reel/1082602281322454/"),
 I("bh_post122094925563500948", "Brick Hood", 61290, "winner", "POV unbag on lift", src="H,B,I", url=None),
 I("bh_post122094812265500948", "Brick Hood", 61106, "winner", "POV unbag", src="H,B,I", url=None),
 I("mg_post122110427571432799", "Merry Glow", 119070, "context", "UNBOX at 4.07-7.13 in the body = drop-off at 0:06 (the anti-pattern)", src="B,I", url=None),
 X("hollyglow27", 5.2e6, "https://www.tiktok.com/@hollyglow27/video/7684015670970879262", "shelf grab → install, 7.85 s", shares="39.5K"),
 X("zombie.crawler", 3.2e6, "https://www.tiktok.com/@zombie.crawler/video/7688711916734270733", "POV unpacking crawling Grinch", shares="39.8K"),
 X("lockedlovestore", 2.6e6, "https://www.tiktok.com/@lockedlovestore/video/7687246647495068950", "Suprise them ❤️🥹 · box on fur, one shot", shares="3.8K"),
 X("jinglenap.official", 1.8e6, "https://www.tiktok.com/@jinglenap.official/video/7676241754730941727", "pulling dog bed out of package", shares="38K"),
],
"failures": ["Unbox in the body: drop-off at 0:04-0:06 on 6/7 reels.", "Static unbox >3 s (MerryFires, 33 views)."],
"variants": [{"name": "Single-shot surprise", "rule": "One continuous 10 s shot: box opened, product revealed, reaction.", "proof": "lockedlovestore 2.6M (0 cuts).", "gate": "3 renders."}],
"checks": [{"id": "ub.no_box_after", "rule": "no BOX/UNBOX shot starts after 3.8 s", "cite": "body REPORT §3"}, {"id": "ub.box_le_2s", "rule": "box shots ≤2.0 s", "cite": "same"}],
"open": ["The internal winners overlap with other formats (cutoff-word, pov-ritual-envy, friend-dare-group); this is a mechanic, not an independent hook family."],
"review": ["Written as a guard-rail format: most of its value is stopping the most common body leak. Tier B, not A, because its internal winners are counted under other formats too."]})
