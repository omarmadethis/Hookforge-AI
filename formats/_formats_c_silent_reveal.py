"""Tier C: silent reveal (external-only experiment)."""
from _common import SUFFIX
from _ev import X
from _blocks import script_pack

F = []
F.append({
"slug": "silent-reveal", "name": "Silent reveal (no hook text, plug-in → wow)", "tier": "C",
"status": "EXPERIMENT. Huge external numbers (23.7M and 8.0M, both organic), but 63/63 of our FB reels had text at 0 s, so there is zero internal evidence. Max 1 test per decor/pet product per week.",
"summary": "No on-screen text at all. The first frame is a hand plugging in or switching on the product, and the transformation lands by ~4 s. It only works when the effect explains itself visually.",
"why": [
 "sarvina450 silent plug-in projector, AIWFCIY, 12.14 s: 23.7M / 175.5K shares (no paid flag); a second reel did 2.5M (X).",
 "pet.scanner.pk kitten in a carrier pouch, no text, 13 cuts: 8.0M / 98.3K shares (X).",
 "Contradiction with our house rule: all 63 FB reels had hook text at 0.0 s (hooks REPORT §3). That is why this is Tier C.",
],
"product_fit": [{"type": "Decor with a dramatic visual effect (projector, animated lights)", "fit": "TEST", "evidence": "sarvina450 23.7M, 2.5M"}, {"type": "Pet (a cute animal carries it)", "fit": "TEST", "evidence": "pet.scanner 8.0M"}, {"type": "Wearable", "fit": "NO", "evidence": "the only wearable example (neilaswgza6 5.5M) is paid-flagged"}],
"timing": {"length": "12-15.5 s",
 "basis": "sarvina450 23.7M: 3 long shots, cuts 4.70 | 8.97 | END 12.14; sarvina 2.5M: 3.20 | 5.73 | 9.10 | 10.97 | 12.03 | END 14.23 (XA).",
 "shots": [
  {"t": "0.0 → 4.0", "shot": "HOOK: plug-in", "content": "hand plugs the product into a wall socket in a dark room; first light by 2 s", "camera": "locked close", "text": "none", "gen": "H1"},
  {"t": "4.0 → 6.0", "shot": "WOW 1", "content": "room transforms (exactly the real effect)", "camera": "locked wide", "text": "none", "gen": "B1·S1"},
  {"t": "6.0 → 8.0", "shot": "WOW 2", "content": "different angle / kid reacts", "camera": "locked", "text": "none", "gen": "B1·S2"},
  {"t": "8.0 → 10.0", "shot": "WOW 3", "content": "escalation", "camera": "locked", "text": "none", "gen": "B2·S1"},
  {"t": "10.0 → 12.0", "shot": "HERO", "content": "hero; hard cut", "camera": "locked wide", "text": "none", "gen": "B2·S2"},
 ],
 "measured": ["sarvina450 23.7M: 4.70 | 8.97 | END 12.14.", "pet.scanner 8.0M: 13 cuts in 15.54 s (~1.2 s shots)."],
 "rules": ["The effect must explain itself with the sound off."]},
"text": {"style": "No text. A/B it against the same body carrying the decor then-vs-now text.", "patterns": [{"pattern": "(no text)", "tag": "P (ext)", "source": "sarvina450 23.7M, pet.scanner 8.0M"}], "rules": []},
"caption": {"template": "Wait for it 😳\nSAY \"{KEYWORD}\" and we'll send you the link", "keywords": ["MAGIC", "LIGHTS"], "rules": ["SAY not COMMENT."]},
"music": {"picks": [{"rank": 1, "track": "All I Want for Christmas Is You · 0:00", "start": "reel 0.0", "evidence": "sarvina450 23.7M, 2.5M"}], "rules": []},
"generation_plan": {"summary": "3 gens.",
 "generations": [
  {"id": "H1", "kind": "hook", "resolution": "720p", "duration_s": 4, "title": "Plug-in in the dark", "shots": "one shot", "feeds": "HOOK", "inputs": "<<<image_1>>> product; reference video of the real effect",
   "basis": "sarvina450 hook visual; 4dabfa47 integrity guard.",
   "prompt": "Vertical 9:16 iPhone video in a dark bedroom at night. Close on a wall socket: a hand plugs in the {product} from <<<image_1>>>, and at two seconds it switches on and the first light of exactly the effect in the reference video spreads across the ceiling. Locked camera. Natural sound only: plug click, a soft hum. No music, no text. The effect is only what the real product does.\n" + SUFFIX},
  {"id": "B1", "kind": "body", "resolution": "720p", "duration_s": 4, "title": "WOW 1 | WOW 2", "shots": "two angles", "feeds": "WOW 1, WOW 2", "inputs": "room still; effect reference",
   "basis": "4dabfa47 locked multi-cut shots.",
   "prompt": script_pack("the same dark bedroom, the {product} switched on", "locked wide: the whole room is filled with exactly the effect from the reference video.", "low angle: a child in pajamas sits up in bed looking up, mouth open.", "soft hum, a child's gasp", guard="The effect matches the reference video exactly; nothing glows beyond the surfaces it really lights.")},
  {"id": "B2", "kind": "body", "resolution": "720p", "duration_s": 4, "title": "WOW 3 | HERO", "shots": "escalation + hero", "feeds": "WOW 3, HERO", "inputs": "same", "basis": "same",
   "prompt": script_pack("same bedroom", "the effect changes to its next scene exactly as in the reference video.", "locked hero wide of the room glowing, the child lying back smiling.", "soft hum")},
 ], "rules": ["Never exaggerate the effect (projector reels are being fact-checked, V)."]},
"evidence": [
 X("sarvina450", 23.7e6, "https://www.tiktok.com/@sarvina450/video/7686197199415397662", "silent plug-in projector reveal · AIWFCIY", shares="175.5K"),
 X("pet.scanner.pk", 8.0e6, "https://www.tiktok.com/@pet.scanner.pk/video/7687859112628981013", "kitten in carrier pouch, no text", shares="98.3K"),
 X("sarvina450", 2.5e6, "https://www.tiktok.com/@sarvina450/video/7686186954047704350", "same plug-in reveal", shares="15.1K"),
 X("beamllyhome", 48.5e6, "https://www.tiktok.com/@beamllyhome/video/7571121863569444118", "fake-window panel, no text", shares="510.7K", flag=True),
 X("finds.worth.keeping", 1.4e6, "https://www.tiktok.com/@finds.worth.keeping/video/7684203385494539533", "wall-mounted train light scene, no text", shares="12.6K", flag=True),
],
"failures": ["Untested on FB; our 63/63 text-at-0 s pattern may be FB-specific."],
"variants": [{"name": "Text A/B", "rule": "Post the same render twice on different days: once silent, once with then-vs-now text (re-render the hook so the files differ).", "proof": "external REPORT §5 test plan.", "gate": "If silent ≥ text on 2 of 3 pairs, promote to Tier B."}],
"checks": [{"id": "sr.no_text", "rule": "no OCR text in any frame", "cite": "sarvina450"}],
"open": ["TikTok plays ≠ FB views (cross-platform swings up to 500×, external REPORT §1).", "All the supporting reels are older than 14 days, so they count half weight under the external freshness rule."],
"review": ["Labelled an experiment, not a default, because it contradicts 63/63 internal reels."]})
