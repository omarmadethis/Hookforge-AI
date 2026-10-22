"""Tier C: gift outcome (external-only experiment)."""
from _common import SUFFIX
from _ev import X
from _blocks import script_pack

F = []
F.append({
"slug": "gift-outcome", "name": "Gift outcome (\"got my {wife} this & now she won't stop {using it}😂\")", "tier": "C",
"status": "EXPERIMENT. External 12.1M (IG), 2.6M, 2.5M, 1.0M. Never tested on our pages; the husband-buyer framing is untested.",
"summary": "The buyer reports the recipient's obsessive use after the gift: social proof and gift intent in one line. The body shows the recipient using it again and again.",
"why": [
 "ccreamyco IG 'got my gf this & now she won't stop making ice cream😂' 12.1M; ccreamyco TikTok 'pov: you finally found the perfect gift for your teenag…' 2.5M (X).",
 "thefacetribee 'The best Christmas gift for your husband😉🎄' 1.0M; lockedlovestore 'Suprise them ❤️🥹' 2.6M (X).",
 "No internal evidence. The closest internal reel is the 6.6M POV handoff (a gift moment, but a different line).",
],
"product_fit": [{"type": "Repeat-use products (wearable, mug, fire pit)", "fit": "TEST", "evidence": "external REPORT §4 #3 suggestions"}],
"timing": {"length": "13-15 s on FB (external 15-17.6 s)",
 "basis": "ccreamyco 12.1M cuts 1.00 | 2.35 | 3.58 | 4.60 | 6.22 | 7.75 | 9.20 | 12.77 | END 17.63: a fast 1.0-1.6 s usage montage (XA). Trimmed to our 13 s house length.",
 "shots": [
  {"t": "0.0 → 3.0", "shot": "HOOK: recipient already using it", "content": "recipient mid-use, delighted; product ≥30% of frame", "camera": "handheld", "text": "outcome line ON", "gen": "H1 (trim 3.0)"},
  {"t": "3.0 → 5.0", "shot": "USE 2", "content": "using it in another moment (morning)", "camera": "locked", "text": "held", "gen": "B1·S1"},
  {"t": "5.0 → 7.0", "shot": "USE 3", "content": "another room / time", "camera": "locked", "text": "held", "gen": "B1·S2"},
  {"t": "7.0 → 8.5", "shot": "ACTIVATION (~62%)", "content": "switch-on macro", "camera": "handheld macro", "text": "held", "gen": "B2·S1 (1.5)"},
  {"t": "8.5 → 10.5", "shot": "USE 4", "content": "won't take it off (funny moment)", "camera": "locked", "text": "held", "gen": "B2·S2"},
  {"t": "10.5 → 12.5", "shot": "PAYOFF (~84%)", "content": "buyer + recipient together, cozy; hard cut", "camera": "locked wide", "text": "held", "gen": "B3 (best 2 s)"},
 ],
 "measured": ["ccreamyco 12.1M: 8 cuts in 17.63 s.", "thefacetribee 1.0M: 1 cut (13.54) in 15.08 s.", "lockedlovestore 2.6M: 0 cuts, 10.21 s."],
 "rules": ["The recipient is already using it at 0 s (outcome first, not the unwrap)."]},
"text": {"style": "Lower-case and conversational, with 😂.",
 "patterns": [{"pattern": "got my {gf} this & now she won't stop {making ice cream}😂", "tag": "P (ext)", "source": "ccreamyco 12.1M"}, {"pattern": "The best Christmas gift for your {husband}😉🎄", "tag": "P (ext)", "source": "thefacetribee 1.0M"}, {"pattern": "got my {wife} this & now she won't take it off😂", "tag": "F", "source": "12.1M formula applied to the robe (external REPORT §4)"}],
 "rules": []},
"caption": {"template": "She hasn't taken it off since 😂\nSAY \"{KEYWORD}\" and we'll send you the link", "keywords": ["WIFE", "GIFT"], "rules": ["SAY not COMMENT."]},
"music": {"picks": [{"rank": 1, "track": "Christmas (Baby Please Come Home)", "start": "reel 0.0", "evidence": "ccreamyco TT 2.5M"}, {"rank": 2, "track": "Rockin' Around the Christmas Tree", "start": "reel 0.0", "evidence": "thefacetribee 1.0M"}], "rules": []},
"generation_plan": {"summary": "4 gens.",
 "generations": [
  {"id": "H1", "kind": "hook", "resolution": "720p", "duration_s": 4, "title": "Recipient mid-use", "shots": "one shot", "feeds": "HOOK", "inputs": "<<<image_1>>> product; cast image",
   "basis": "ccreamyco outcome framing; product-hero-at-0 s rule (hooks REPORT §1.3).",
   "prompt": "Vertical 9:16 handheld iPhone video, filmed by her husband: in the kitchen at breakfast a woman is wearing the {product} from <<<image_1>>> with the hood up, sipping coffee and laughing at the camera, the {product} filling a third of the frame. Natural sound only: kitchen sounds, her laugh. No music, no text.\n" + SUFFIX},
  {"id": "B1", "kind": "body", "resolution": "720p", "duration_s": 4, "title": "USE 2 | USE 3", "shots": "two usage moments", "feeds": "USE 2, USE 3", "inputs": "<<<image_1>>>, cast", "basis": "ccreamyco usage montage.",
   "prompt": script_pack("American home", "she is on the couch in the {product} from <<<image_1>>>, typing on a laptop, hood up.", "she walks the dog in the backyard, still wearing the {product} over her pajamas.", "keyboard taps, dog tags jingling", guard="Same woman and same {product} in both shots.")},
  {"id": "B2", "kind": "body", "resolution": "720p", "duration_s": 4, "title": "ACTIVATION | USE 4", "shots": "remote macro · funny use", "feeds": "ACTIVATION, USE 4", "inputs": "<<<image_1>>>, <<<image_2>>> controller", "basis": "wearable REM beat.",
   "prompt": script_pack("same home", "POV: her thumb presses the controller from <<<image_2>>> and the heat LEDs step up.", "she stirs a pot at the stove still in the {product}, hood up, dancing a little.", "button clicks, laughter")},
  {"id": "B3", "kind": "body", "resolution": "720p", "duration_s": 4, "title": "PAYOFF A | PAYOFF B", "shots": "two payoff takes", "feeds": "PAYOFF", "inputs": "same", "basis": "two-person payoff (PLAYBOOK §6).",
   "prompt": script_pack("living room at night, tree lit", "she and her husband on the couch; she pulls him under the {product} with her.", "locked wide: both snuggled inside, laughing.", "laughter")},
 ], "rules": []},
"evidence": [
 X("ccreamyco", "12.1M", "https://www.instagram.com/reel/DU95uUgESlP/", "got my gf this & now she won't stop making ice cream😂"),
 X("lockedlovestore", 2.6e6, "https://www.tiktok.com/@lockedlovestore/video/7687246647495068950", "Suprise them ❤️🥹", shares="3.8K"),
 X("ccreamyco", 2.5e6, "https://www.tiktok.com/@ccreamyco/video/7695966577279175966", "pov: you finally found the perfect gift for your teenag…", shares="9.8K"),
 X("thefacetribee", 1.0e6, "https://www.tiktok.com/@thefacetribee/video/7692189098047474976", "The best Christmas gift for your husband😉🎄", shares="4.9K"),
 X("ohanawithstitch3", 13.5e6, "https://www.tiktok.com/@ohanawithstitch3/video/7611048295040945421", "I found the best gift for my wife", shares="11.3K", flag=True),
],
"failures": ["None measured internally."],
"variants": [{"name": "Husband-buyer robe", "rule": "'got my wife this & now she won't take it off😂' on the robe.", "proof": "12.1M formula.", "gate": "3 renders; promote if any reaches ≥3× page median."}],
"checks": [{"id": "go.use_at_0s", "rule": "product in use at 0 s", "cite": "ccreamyco"}],
"open": ["Purely external. ccreamyco's own cross-platform swing (IG 12.1M vs TikTok 2.5M) shows how much platform matters."],
"review": ["Tier C until 3 FB renders exist."]})
