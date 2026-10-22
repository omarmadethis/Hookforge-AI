"""Tier B: cut-off word."""
from _common import SUFFIX
from _ev import I, X
from _blocks import decor_body, still_t8

F = []
cdrows, cdgens = decor_body(3.8)
F.append({
"slug": "cutoff-word", "name": "Cut-off word (\"The perfect {gift} doesn't exi-\")", "tier": "B",
"status": "MID-TIER and reliable on decor when the box is in the hook (MG 98K, the best avg-watch % on that page) and on store footage (HJ 91K). External: 488K, 701K⚑.",
"summary": "An unfinished sentence implying the perfect thing now exists, over a first frame where the product or box is already in hand. The cut-off creates a micro open loop, and the box-in-hook fixes the decor prep-block leak.",
"why": [
 "Merry Glow 98K 'The perfect christmas decor doesn't exi-': box already in hand at 0 s; drop-off moved to 0:11; 66% average watched, the best on Merry Glow (body REPORT §1B, §3).",
 "HJ 91K 'The perfect X-MAS gift doesnt exi-' on a store reaction.",
 "External: snugbaby00 'The perfect gift for BABY MOM doesn't exi-' 488K / 4,722 shares (V); my_everorb⚑ 701K.",
 "Flop: 'The perfect Christmas Gift doesn't exi-😳❄️' 3.9K at home, 15.4 s.",
],
"product_fit": [
 {"type": "Decor / lights", "fit": "PRIMARY", "evidence": "MG 98K"},
 {"type": "Wearable gift", "fit": "YES on store footage", "evidence": "HJ 91K; ext 488K (baby carrier hoodie)"},
],
"timing": {"length": "12.6-13.6 s",
 "basis": "MG 98K exact: HOOK (box in hand) 0-3.767 | BOX -6.500 | INSTALL -8.800 | LIT -9.867 | LIT -10.767 | LIT -12.57.",
 "shots": [{"t": "0.0 → 3.8", "shot": "HOOK: box in hand", "content": "woman holds the branded box up, product visible on the art; she opens the lid by 2 s", "camera": "locked medium", "text": "cut-off line ON", "gen": "H1 (trim 3.8)"}] + cdrows[1:],
 "measured": ["MG 98K: 3.767 | 6.500 | 8.800 | 9.867 (LIT, 78%) | 10.767 | END 12.61 · avg 9 s, 66%.", "HJ 91K: 4.067 | 5.567 | 7.767 | 8.600 | 10.567 | END 13.63.", "snugbaby 488K: 11.4 s, 4 shots (store → driveway → porch → kitchen) (V)."],
 "rules": ["Because the box is in the hook, drop the THEN2 row of the decor master; any BOX shot in the body stays ≤2.0 s."]},
"text": {"style": "Quotes optional. The word is always cut with a hyphen and never finished.",
 "patterns": [
  {"pattern": "The perfect {christmas decor} doesn't exi-", "tag": "P", "source": "MG 98K"},
  {"pattern": "The perfect {X-MAS gift} doesnt exi-", "tag": "P", "source": "HJ 91K"},
  {"pattern": "The perfect gift for {BABY MOM} doesn't exi-", "tag": "P (ext)", "source": "snugbaby00 488K"},
 ],
 "rules": ["Pair with a recipient where possible (488K)."]},
"caption": {"template": "Until now 😏\nSAY \"{KEYWORD}\" and we'll send you the link", "keywords": ["PERFECT", "TREE", "MOM"], "rules": ["SAY not COMMENT."]},
"music": {"picks": [
  {"rank": 1, "track": "Last Christmas (Wham!) · ~2:48", "start": "reel 0.0", "evidence": "MG 98K (offset 171.0 s)"},
  {"rank": 2, "track": "Let It Snow · 0:00", "start": "reel 0.0", "evidence": "HJ 91K"},
 ], "rules": []},
"generation_plan": {"summary": "4 gens: H1 box-in-hand at 720p, then the decor master (B1 starts at BOX).",
 "generations": [
  {"id": "H1", "kind": "hook", "resolution": "720p", "duration_s": 4, "title": "Box in hand, lid opens by 2 s",
   "shots": "one shot", "feeds": "HOOK", "inputs": "<<<image_1>>> = {brand} box; room still",
   "basis": "MG 98K opener (hand-coded WEAR_HOLD, 15% product share): the box-in-hook retention fix.",
   "prompt": "Vertical 9:16 iPhone video in a dim American living room with an unlit Christmas tree. A woman stands centred holding the {brand} box from <<<image_1>>> up at chest height toward the camera, then lifts the lid at 1.5 seconds and tilts the box so the {product} inside is visible. Locked camera, top fifth clear. Natural sound only, no music, no text.\n" + SUFFIX,
   "start_frame": {"template": "T8 (room still; also the base for the decor body's T9 edits)", "prompt": still_t8("in a dim American living room in the evening with an unlit, undecorated Christmas tree: a woman stands centred at chest-up framing holding the closed {brand} box from the first image toward the camera, the product art clearly legible.")}},
 ] + cdgens, "rules": ["B1's first shot (THEN2) can be replaced by a second BOX angle, since there is no 'then' scene."]},
"evidence": [
 I("mg_post122111714343432799", "Merry Glow", 97955, "winner", "The perfect christmas decor doesn't exi- · box in hook · 66% watched, drop-off 0:11", src="H,B,I", url=None),
 I("28171203645867196", "HeatedJammies", 91e3, "winner", "The perfect X-MAS gift doesnt exi- · store reaction"),
 I("1696343398581029", "HeatedJammies", 3.9e3, "flop", "The perfect Christmas Gift doesn't exi- · home, 15.4 s"),
 X("snugbaby00", 488.4e3, "https://www.tiktok.com/@snugbaby00/video/7696948793941478687", "The perfect gift for BABY MOM doesn't exi- · 'Comment \"Mom\"' end card (we use SAY)", shares="4.7K", src="V"),
 X("my_everorb", 701.1e3, "https://www.tiktok.com/@my_everorb/video/7688325319979273504", "the perfect Christmas ornament for moms doesn't exi-", shares="4.6K", flag=True),
],
"failures": ["At-home footage with no box/product hero and a 15 s runtime (3.9K)."],
"variants": [{"name": "Recipient cut-off", "rule": "'The perfect gift for {grandma} doesn't exi-' on the wearable body.", "proof": "snugbaby 488K.", "gate": "3 renders."}],
"checks": [{"id": "cw.hyphen", "rule": "hook ends with '-' mid-word", "cite": "all winners"}, {"id": "cw.box_0s", "rule": "box/product visible at 0 s", "cite": "MG 98K"}],
"open": ["Only n=2 internal winners."],
"review": ["Kept despite mid-tier views because MG 98K is our best retention evidence for putting the box in the hook."]})
