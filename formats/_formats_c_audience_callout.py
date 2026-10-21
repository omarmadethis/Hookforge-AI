"""Tier B: audience / identity callout."""
from _common import SUFFIX
from _ev import I, X
from _blocks import wearable_body

F = []
rows, gens = wearable_body(3.5)
F.append({
"slug": "audience-callout", "name": "Audience / identity callout (\"{Tribe}-aholics… this is for you 🥹\")", "tier": "B",
"status": "STRONG externally (6.0M, 1.8M, 1.3M, 1.3M organic). Internally one moderate result: 'Calling ALL Christmas-aholics' 35.4K, with the best retention we measured (81%). The biggest untested family on our pages (external REPORT §4 #1).",
"summary": "Name a tribe and hand them the product: hold it up to the camera like a gift made for the viewer, with a soft 🥹 tone. Identity is the share trigger, because people send it to the tribe member they know.",
"why": [
 "warmly.official 'Cold-aholics this is for you... 🥹💕' 6.0M / 74.4K shares: rolled pink robe held at chest (X).",
 "jinglenap.official 'Dog MOMS... This is for you 👀🐶' 1.8M / 38K shares in 9.23 s; goth.robes 1.3M; nocturne.robes0 1.3M (X).",
 "grumpyriderr 'Christmas HATERS... this is for YOU' 211K, with shares (1,808) above likes (1,619): a send-to-a-friend signal (V).",
 "Internal: Merry Glows 'Calling ALL Christmas-aholics 😁' 35.4K, 3s 54%, avg watch 12 s = 81% (store FaceTime body). 'For my Christmas Lovers 🇺🇸🎄' did 5.9K on a tray, with no 'for you' reveal.",
],
"product_fit": [
 {"type": "Wearable gift", "fit": "PRIMARY", "evidence": "ext 6.0M, 1.3M ×2"},
 {"type": "Pet products", "fit": "PRIMARY", "evidence": "ext Dog MOMS 1.8M; GrumpyRider 211K"},
 {"type": "Decor / fire", "fit": "YES", "evidence": "MGS 35.4K (81% watched)"},
 {"type": "Mug", "fit": "TRANSFER", "evidence": "'Hot-cocoa-aholics… this is for you' (external REPORT §4)"},
],
"timing": {"length": "12.5-13.5 s on FB (external range 9.2-18.2 s)",
 "basis": "Hook copies the external held-reveal (goth.robes first cut 4.30 s, jinglenap 2.33 s); body = wearable master for robes. warmly 6.0M is ONE held shot to 11.17 s, kept as an experiment.",
 "shots": [{"t": "0.0 → 3.5", "shot": "HOOK: held-for-you", "content": "talent holds the rolled/folded product at chest toward camera, soft smile; unrolls or lifts it by 2 s", "camera": "locked, eye level", "text": "callout ON at 0.0", "gen": "H1"}] + rows,
 "measured": [
  "warmly 6.0M: one shot 0-11.17 | 11.93 | 12.67 | 15.97 | END 18.17 (XA).",
  "jinglenap 1.8M: 2.33 | 4.07 | 6.37 | 8.10 | END 9.23.",
  "goth.robes 1.3M: 4.30 | 10.23 | 10.87 | 12.20 | END 13.21.",
  "MGS 35.4K store FaceTime: 2.100 | 6.167 | 7.900 | 9.033 | 10.167 (ACT 69%) | 11.667 | 13.533 | END 14.84.",
 ],
 "rules": ["Product legible at 0 s, as in all four external winners.", "Keep the house 66% activation / 84% payoff on FB until the long-shot experiment says otherwise."]},
"text": {"style": "House placement; ellipsis plus a 🥹/👀 emotional emoji.",
 "patterns": [
  {"pattern": "{Cold}-aholics this is for you... 🥹💕", "tag": "P (ext)", "source": "warmly 6.0M"},
  {"pattern": "{Dog MOMS}... This is for you 👀🐶", "tag": "P (ext)", "source": "jinglenap 1.8M"},
  {"pattern": "{Cold}-aholics, this one's for you. 😏", "tag": "P (ext)", "source": "goth.robes 1.3M"},
  {"pattern": "I made this for the {Goths}... 🥹", "tag": "P (ext)", "source": "nocturne.robes0 1.3M"},
  {"pattern": "Calling ALL {Christmas-aholics} 😁", "tag": "P", "source": "MGS 35.4K"},
  {"pattern": "{Christmas HATERS}... this is for YOU → Link in bio if you NEED this", "tag": "P (ext)", "source": "grumpyriderr 211K"},
 ],
 "rules": ["'For my {Christmas Lovers}' without the 'this is for you' reveal flopped (5.9K)."]},
"caption": {"template": "Made for you 🥹\nSAY \"{KEYWORD}\" and we'll send you the link\n#{tribe} #christmasgift #{product_tag}", "keywords": ["COLD", "MINE", "{TRIBE}"], "rules": ["SAY not COMMENT."]},
"music": {"picks": [
  {"rank": 1, "track": "All I Want for Christmas Is You · 0:00", "start": "reel 0.0", "evidence": "jinglenap 1.8M"},
  {"rank": 2, "track": "Let It Snow · 0:00 (robe default)", "start": "reel 0.0", "evidence": "robe family default (6.6M; ext robes)"},
  {"rank": 3, "track": "Last Christmas · ~2:48", "start": "reel 0.0", "evidence": "MGS 35.4K"},
 ], "rules": ["warmly, goth.robes and nocturne used original sound; no music claim beyond that."]},
"generation_plan": {"summary": "4 gens: H1 held-for-you at 1080p, then the wearable master (or decor master).",
 "generations": [
  {"id": "H1", "kind": "hook", "resolution": "1080p", "duration_s": 4, "title": "Held-for-you reveal",
   "shots": "one shot", "feeds": "HOOK", "inputs": "<<<image_1>>> product rolled; cast image styled for the tribe",
   "basis": "warmly 6.0M / goth.robes 1.3M hook visuals (X hook_visual); use T1 if a reference clip exists.",
   "prompt": "Vertical 9:16 iPhone video. A {tribe-styled} woman stands centred in a {tribe-matching room}, holding the rolled {product} from <<<image_1>>> at chest height toward the camera so it fills the middle third, a soft emotional smile. At 1.5 seconds she unrolls it to full length toward the lens. Locked camera, eye level, top fifth clear. Natural room sound only, no music, no text.\n" + SUFFIX},
 ] + gens, "rules": ["Tribe styling lives in H1 only; the body is reused (see same-product-new-audience)."]},
"evidence": [
 I("mgs_5_35K_1074627768726306", "Merry Glows", 35390, "context", "Calling ALL Christmas-aholics 😁 · store FaceTime · 81% watched (moderate; below the page's winner level)", src="H,B,I", url="https://www.facebook.com/reel/1074627768726306/"),
 I("1606892301089465", "HeatedJammies", 5.9e3, "flop", "For my Christmas Lovers 🇺🇸🎄 · tray, no 'for you' reveal"),
 X("warmly.official", 6.0e6, "https://www.tiktok.com/@warmly.official/video/7677579852140055809", "Cold-aholics this is for you... 🥹💕", shares="74.4K"),
 X("jinglenap.official", 1.8e6, "https://www.tiktok.com/@jinglenap.official/video/7676241754730941727", "Dog MOMS... This is for you 👀🐶", shares="38K"),
 X("goth.robes", 1.3e6, "https://www.tiktok.com/@goth.robes/video/7688918162326261022", "Cold-aholics, this one's for you. 😏", shares="26.5K"),
 X("nocturne.robes0", 1.3e6, "https://www.tiktok.com/@nocturne.robes0/video/7684104805748411679", "I made this for the Goths... 🥹 · muffin tin", shares="14.9K"),
 X("grumpyriderr", 211.1e3, "https://www.tiktok.com/@grumpyriderr/video/7695198899010686238", "Christmas HATERS... this is for YOU → Link in bio if you NEED this", shares="1.8K", src="V"),
],
"failures": ["Callout without a product-for-you reveal (5.9K).", "A tribe too narrow for the 45-65+ FB buyer (PLAYBOOK §2: top ages 55-64/65+) [I]."],
"variants": [
 {"name": "One-shot hold", "rule": "Hold the reveal as one continuous shot to ~11 s, then 3 fast payoff cuts.", "proof": "warmly 6.0M (0-11.17 single shot).", "gate": "Judge on avg-watch %; kill after 3 renders below page median."},
 {"name": "Haters callout", "rule": "'Christmas HATERS... this is for YOU 😂' for Grinch-branded products, flipping to 'SAY \"GRINCH\" if you NEED this' on the activation cut.", "proof": "grumpyriderr 211K (shares > likes).", "gate": "1 test per Grinch product."},
],
"checks": [{"id": "ac.for_you", "rule": "hook matches /(for you|for YOU|this one's for)/", "cite": "all 5 external winners"}, {"id": "ac.product_0s", "rule": "product_pct_0 ≥ 25", "cite": "external hook visuals"}],
"open": ["We have zero FB-native callout reels with the 'for you' reveal. Treat the first 3 renders as pure tests.", "All 4 big external winners are older than 14 days, so they count half weight under the external freshness rule."],
"review": ["Tier B, not A: the only internal data point (35.4K) is below our winner bar. The external case is strong and the retention (81%) is the best we have."]})
