"""Tier B: same product, new audience (hook-only re-target of a proven body)."""
from _common import SUFFIX
from _ev import I, X

F = []
F.append({
"slug": "same-product-new-audience", "name": "Same product, new audience (re-target a proven body to a new tribe or use-case)", "tier": "B",
"status": "STRATEGY FORMAT. Proven externally on one product category (heated robes: 834K, 509K, 417K, 1.3M ×2). Internally, the same robe body carried 4 different recipients to 165K-6.6M. The cheapest format: 1 new generation per video.",
"summary": "Keep a proven body's generations and replace only the hook generation and text with a new tribe or use-case ('period cramps', 'BTS army', 'Goths', 'grandma', 'nurses'). New first frames make it a new video to Meta's similarity matcher, at a quarter of the credit cost.",
"why": [
 "warmrobestore 'Period girls RUN don't walk to Target 🩸🙃' 834K / 29K shares: the same robe sold as cramp relief (X).",
 "obsidianrobes '“Just wear slippers”🙄' 509K; thecozybts 417K; goth.robes 1.3M; nocturne.robes0 1.3M: one product category, five tribes (external REPORT §4 #2).",
 "Internal: one robe body under women (6.6M), mom (2.7M), grandma (183K) and wife (165K) recipients.",
 "Reusing body clips is safe when the hook changes: gen c0ede3c3 sits in both the 1.4M Walmart and the 1.4M Target reels, and 13 generations were reused across 2-3 reels (PLAYBOOK §15.6). Only identical FILES collapse (6.6M → 2.2K).",
],
"product_fit": [
 {"type": "Any product with a proven body on file", "fit": "PRIMARY", "evidence": "robe (4 recipients internally; 5 tribes externally)"},
 {"type": "New product with no proven body", "fit": "NO (build a body with an A-tier format first)", "evidence": "—"},
],
"timing": {"length": "identical to the source body's format",
 "basis": "Copy the source reel's cut list exactly. Bodies are never the limiting factor: identical bodies ran from 2.2K to 6.6M (body REPORT §4). Only 0 s → first cut changes.",
 "shots": [{"t": "0.0 → first cut (2.7-3.9)", "shot": "NEW HOOK", "content": "talent/props signal the tribe (wardrobe, room, prop) while the product stays ≥30% of frame", "camera": "as source", "text": "tribe line ON", "gen": "H1"}, {"t": "first cut → END", "shot": "REUSED BODY", "content": "the source winner's body renders (re-ordering is allowed; never the same file)", "camera": "as source", "text": "as source family", "gen": "reuse B1-B3 renders"}],
 "measured": ["warmrobestore 834K: 1.42 | 2.50 | 3.90 | 4.73 | 7.40 | 9.03 | 9.63 | 10.40 | 12.73 | END 15.70.", "thecozybts 417K: 3.37 | 8.20 | 9.20 | 10.03 | 11.10 | END 12.54.", "obsidianrobes 509K: 3.57 | 4.73 | 6.40 | 7.32 | 10.48 | 11.13 | 11.97 | END 14.75."],
 "rules": ["Change at least the H1 render, the hook text, the song or song offset, and the caption. Never upload a file whose first 3 s match an earlier post."]},
"text": {"style": "Use the source format's text pattern with the tribe in the slot.",
 "patterns": [
  {"pattern": "{Tribe} RUN don't walk to {Store} {emoji} → It's a {product} for your {use case}!", "tag": "P (ext)", "source": "warmrobestore 834K"},
  {"pattern": "DO NOT show this to a {BTS army}😱😂", "tag": "P (ext)", "source": "thecozybts 417K"},
  {"pattern": "“{Objection the tribe hears}”🙄", "tag": "P (ext)", "source": "obsidianrobes 509K"},
  {"pattern": "DONT show this to your {Grandma} ❄️😳", "tag": "P", "source": "HJ 183K (recipient re-target of the mom line)"},
 ],
 "rules": ["Pick tribes the 35-65+ FB buyer belongs to or buys for (grandma, nurse, teacher, cat mom) before youth tribes [I, from Insights ages]."]},
"caption": {"template": "Finally, one for us {tribe emoji}\nSAY \"{KEYWORD}\" and we'll send you the link\n#{tribe} #{product_tag}", "keywords": ["{TRIBE}", "WARM"], "rules": ["SAY not COMMENT."]},
"music": {"picks": [{"rank": 1, "track": "Source winner's song + offset (or the next pick in that format's list, to avoid duplicate audio)", "start": "as source", "evidence": "Let It Snow on robe tribes: thecozybts 417K"}], "rules": []},
"generation_plan": {"summary": "1 new generation (H1, 1080p). The body uses existing renders from the source winner.",
 "generations": [
  {"id": "H1", "kind": "hook", "resolution": "1080p", "duration_s": 4, "title": "Tribe-signalling hook",
   "shots": "one shot", "feeds": "NEW HOOK", "inputs": "<<<video_1>>> = the source winner's own hook clip; <<<image_1>>> = cast image of the tribe",
   "basis": "T3 background/cast-only swap (88K; gens 8463df4d, 633c0bb6, 00384ba0). The person swap is the one change.",
   "prompt": "Recreate <<<video_1>>> 1:1 perfectly. Do not change the camera angle and movements. There are only 2 changes you are going to make.\nChange 1: Replace the woman in <<<video_1>>> with the woman in <<<image_1>>> ({tribe styling}); the {product} stays exactly the same.\nChange 2: Remove the caption from <<<video_1>>>.\nOther than change 1 and change 2, replicate <<<video_1>>> 1:1 perfectly.\n" + SUFFIX},
 ], "rules": ["Person swaps were rarer in used prompts (4% of used vs 17% of unused, PLAYBOOK §15.8), so roll 3-4 takes and reject face artefacts.", "This is the default innovation-budget slot: it's cheap, and each tribe is a fresh lottery ticket."]},
"evidence": [
 I("1624473615929591", "HeatedJammies", 6.6e6, "winner", "robe body · recipient 'Women'"),
 I("1381141263599559", "HeatedJammies", 2.7e6, "winner", "robe body · recipient 'mom'"),
 I("1103827319264144", "HeatedJammies", 183e3, "winner", "robe body · recipient 'Grandma'"),
 I("2176512149911383", "HeatedJammies", 165e3, "winner", "robe body · recipient 'wife'"),
 X("warmrobestore", 833.6e3, "https://www.tiktok.com/@warmrobestore/video/7584679343121616141", "Period girls RUN don't walk to Target → cramp use-case", shares="29K"),
 X("obsidianrobes", 509.1e3, "https://www.tiktok.com/@obsidianrobes/video/7692033957075897631", "“Just wear slippers”🙄 · gothic tribe", shares="10.7K"),
 X("thecozybts", 416.6e3, "https://www.tiktok.com/@thecozybts/video/7687784086643002637", "DO NOT show this to a BTS army😱😂", shares="6.9K"),
 X("goth.robes", 1.3e6, "https://www.tiktok.com/@goth.robes/video/7688918162326261022", "Goth tribe", shares="26.5K"),
 X("nocturne.robes0", 1.3e6, "https://www.tiktok.com/@nocturne.robes0/video/7684104805748411679", "Goth tribe + muffin tin", shares="14.9K"),
],
"failures": ["Uploading the identical file (6.6M → 2.2K; 1.4M → 16K).", "Brick Hood's identical file did 61.3K on FB and 2.6K on IG: audience/platform moved results 24×, so tribe fit per platform matters."],
"variants": [{"name": "Use-case flip", "rule": "Same body; the hook reframes the use ('for your period cramps', 'for night-shift nurses').", "proof": "warmrobestore 834K.", "gate": "Max 2 use-cases per product per week."}],
"checks": [{"id": "spna.first3s_unique", "rule": "pHash of 0-3 s differs from every prior post on the page", "cite": "repost collapse 6.6M → 2.2K"}],
"open": ["Which tribes work for 45-65+ FB audiences is untested."],
"review": ["Tier B, not A: the 4 internal winners share the robe body and differ only by recipient line, so they show the body carries new hooks, not that a new TRIBE works on FB. Included because Omar named it and it's the cheapest proven way to buy fresh lottery tickets (1 gen vs 4)."]})
