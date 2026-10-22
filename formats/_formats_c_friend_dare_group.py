"""Tier B: friend dare / send-to (group self-purchase accessory)."""
from _common import SUFFIX
from _ev import I, X
from _blocks import script_pack

F = []
F.append({
"slug": "friend-dare-group", "name": "Friend dare / send-to (group self-purchase accessory)", "tier": "B",
"status": "PROVEN only for the ski mask on FB (61.3K and 61.1K; 43.2K below the bar), all among Brick Hood's first 3 posts in a burst window. External friend-group reel 2.3M with no text.",
"summary": "A quoted dare between friends ('If you buy one, I'll buy one too' 😂) over POV gloved hands unbagging the mask on a ski lift, then a lifestyle montage ending on a social payoff (après-ski cheers).",
"why": [
 "Brick Hood 61.3K / 61.1K / 43.2K vs 8.8K for 'Who's your squad?' (PLAYBOOK §2), but all three were the page's first 3 posts, so moderate evidence at best (hooks REPORT §4).",
 "The 61.3K file got 2.6K on IG: page/platform moved it 24×.",
 "External: merlinepulley42, three friends in matching masks, 2.3M; Legohead IG 1M (V).",
],
"product_fit": [
 {"type": "Group/self-purchase accessory (ski mask, matching sets)", "fit": "PRIMARY", "evidence": "BH ×3"},
 {"type": "Gift products", "fit": "NO", "evidence": "HJ 'Send this to someone you'd match with' 1.1K"},
],
"timing": {"length": "10.7-12.4 s",
 "basis": "BH 61.3K exact: HOOK mask CU 0-2.733 | WEAR -4.867 | ACTION -6.300 | GROUP -7.567 | ACTION -9.200 | FUN -10.967 | PAYOFF cheers -12.43.",
 "shots": [
  {"t": "0.0 → 2.7", "shot": "HOOK: POV unbag on lift", "content": "gloved hands pull the mask from its bag on a chairlift; mask 30-35% of frame, bright snow/blue sky", "camera": "POV", "text": "dare line ON", "gen": "H1 (trim 2.7)"},
  {"t": "2.7 → 4.7", "shot": "WEAR", "content": "portrait wearing it; face appears by ~3 s", "camera": "locked", "text": "held", "gen": "B1·S1"},
  {"t": "4.7 → 6.2", "shot": "ACTION", "content": "skiing", "camera": "follow", "text": "held", "gen": "B1·S2 (1.5)"},
  {"t": "6.2 → 7.5", "shot": "GROUP", "content": "friends on chairlift in matching masks", "camera": "locked", "text": "held", "gen": "B2·S1 (1.3)"},
  {"t": "7.5 → 9.1", "shot": "ACTION 2", "content": "carving / jump", "camera": "follow", "text": "held", "gen": "B2·S2 (1.6)"},
  {"t": "9.1 → 10.9", "shot": "FUN", "content": "snow angel / laughing", "camera": "locked", "text": "held", "gen": "B3·S1 (1.8)"},
  {"t": "10.9 → 12.4", "shot": "PAYOFF (88%)", "content": "après-ski beer cheers", "camera": "locked medium", "text": "held", "gen": "B3·S2 (1.5)"},
 ],
 "measured": ["BH 61.3K: 2.733 | 4.867 | 6.300 | 7.567 | 9.200 | 10.967 | END 12.43 · 3s 44%, avg 7 s, drop-off 0:02.", "BH 61.1K: 3.000 | 4.967 | 6.733 | 7.800 | 8.933 | END 10.75.", "BH 43.2K: 3.167 | 5.400 | 6.933 | 8.700 | 10.300 | END 11.82 (ends on GROUP, no payoff)."],
 "rules": ["End on the social PAYOFF (both 61K winners do; the 43.2K reel didn't)."]},
"text": {"style": "In quotes, with 😂.",
 "patterns": [
  {"pattern": "\"If you buy one, I'll buy one too\" 😂", "tag": "P", "source": "BH 61.3K"},
  {"pattern": "\"Send this to someone you'd absolutely wear this with\" 😂", "tag": "P", "source": "BH 61.1K"},
  {"pattern": "POV: You finally found the perfect {ski mask} 😂", "tag": "P", "source": "BH 43.2K"},
 ],
 "rules": ["Never as a caption question ('Who's your squad?' 8.8K, 'Tag your gang' 42)."]},
"caption": {"template": "Squad goals for this season 😂\nSAY \"{KEYWORD}\" and we'll send you the link", "keywords": ["MASK", "SQUAD"], "rules": ["SAY not COMMENT (BH 43.2K's 'Comment MASK' was the weakest of the three)."]},
"music": {"picks": [{"rank": 1, "track": "Boombastic (Shaggy)", "start": "reel 0.0", "evidence": "BH 61.3K, 61.1K"}], "rules": []},
"generation_plan": {"summary": "4 gens. No Brick Hood clip matched in Higgsfield (hf_match: nothing above ~0.83), so the prompts are scripted.",
 "generations": [
  {"id": "H1", "kind": "hook", "resolution": "720p", "duration_s": 4, "title": "POV unbag on chairlift", "shots": "one POV shot", "feeds": "HOOK",
   "inputs": "<<<image_1>>> = mask design", "basis": "hooks REPORT §3 accessory first-frame spec.",
   "prompt": "POV from a chairlift seat on a bright day, blue sky and snowy slopes below. Gloved hands pull the knitted ski mask from <<<image_1>>> out of a clear bag and hold it up to the camera so it fills a third of the frame, then stretch it to show the design. Gentle chairlift sway. Natural sound only: wind, lift cable creak. No music, no text.\n" + SUFFIX},
  {"id": "B1", "kind": "body", "resolution": "720p", "duration_s": 4, "title": "WEAR | ACTION", "shots": "S1 portrait · S2 skiing", "feeds": "WEAR, ACTION", "inputs": "<<<image_1>>>", "basis": "BH 61.3K body.",
   "prompt": script_pack("ski resort on a sunny day", "chest-up portrait of a young man wearing the ski mask from <<<image_1>>> on the slope; he grins through the mouth opening.", "he skis past the camera spraying snow, the mask clearly visible.", "wind, skis carving", guard="The mask design from <<<image_1>>> stays identical in both shots.")},
  {"id": "B2", "kind": "body", "resolution": "720p", "duration_s": 4, "title": "GROUP | ACTION 2", "shots": "S1 three friends on lift · S2 jump", "feeds": "GROUP, ACTION 2", "inputs": "<<<image_1>>>", "basis": "merlinepulley42 2.3M friend group.",
   "prompt": script_pack("ski resort", "three friends sit on a chairlift all wearing the same ski mask from <<<image_1>>>, laughing and pointing at each other.", "one of them takes a small jump in the terrain park and lands.", "laughter, wind", guard="All three masks identical to <<<image_1>>>.")},
  {"id": "B3", "kind": "body", "resolution": "720p", "duration_s": 4, "title": "FUN | PAYOFF", "shots": "S1 snow angel · S2 après cheers", "feeds": "FUN, PAYOFF", "inputs": "<<<image_1>>>", "basis": "BH 61.3K payoff.",
   "prompt": script_pack("ski resort", "a friend in the ski mask from <<<image_1>>> falls back into fresh snow and makes a snow angel.", "après-ski deck: the three friends, masks pulled up on their heads, clink beer glasses and cheer.", "laughter, glasses clinking", guard="Masks identical to <<<image_1>>>.")},
 ], "rules": []},
"evidence": [
 I("bh_post122094925563500948", "Brick Hood", 61290, "winner", "If you buy one, I'll buy one too 😂 · 3s 44%, avg 7 s", src="H,B,I", url=None),
 I("bh_post122094812265500948", "Brick Hood", 61106, "winner", "Send this to someone you'd absolutely wear this with 😂 · 58%", src="H,B,I", url=None),
 I("bh_post122094852045500948", "Brick Hood", 43223, "context", "POV: You finally found the perfect ski mask 😂 · 46% (below 50K)", src="H,B,I", url=None),
 I("ig_2.6K_DeAuaIUPJVK", "merry.jammies", 2592, "flop", "identical file to BH 61.3K, on IG", platform="IG", url="https://www.instagram.com/reel/DeAuaIUPJVK/"),
 I("1073780918870688", "HeatedJammies", 1.1e3, "flop", "Send this to someone you'd match with 😉 (robe)"),
 X("merlinepulley42", 2.3e6, "https://www.tiktok.com/@merlinepulley42/video/7689899316252626207", "3 friends pulling up balaclavas · no text · 39 s", shares="6.4K"),
],
"failures": ["The same file on IG got 2.6K.", "Transplanted to gift products (1.1K).", "Engagement-bait captions (8.8K, 42)."],
"variants": [{"name": "Squad-of-3 first frame", "rule": "Open on 3 friends in matching masks, with the dare line on top.", "proof": "merlinepulley42 2.3M.", "gate": "3 renders."}],
"checks": [{"id": "fd.payoff_social", "rule": "last shot contains ≥2 people", "cite": "BH 61.3K, 61.1K"}],
"open": ["All the evidence comes from a burst window; the ~60K ceiling may be page-level."],
"review": ["Narrow by design: kept only for group/self-purchase accessories."]})
