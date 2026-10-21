# Hookforge customer-voice INSIGHTS
Generated 2026-10-18 21:42 PT by `voice/report.py` from `voice/comments.csv` (8,475 de-identified comments on 48 videos) + `voice/support_themes.csv` (Gmail support inbox, aggregated). Counts = comments carrying the code (multi-label); 'liked share' weights each comment by 1+ln(1+likes). Recommendations live in `voice/recommendations.json` and feed `voice/voice_rules.csv`.

## 0. Critical alerts (read first)
- **Robe: what ships does not match what the reels and page promise.** 164 customer threads in the MerryJammies inbox (Sep 13 to Oct 19 PT) break down as: 106 (65%) not received or late, 50 (30%) asking for a refund, return or cancel, 16+ 'no heat controller / USB-only / doesn't heat' (snippet-only count, so the real number is higher), 14 'not as pictured', 8 quality defects (holes, thin, tiny), 5 wrong character, and 8 scam/trust messages including 1-star Loox reviews. The page says the 5-level controller 'comes in the box' and leads with 'Free International Shipping, tracked', but 'allow up to 2 months' making time is buried in the FAQ. Fix the supplier and the page before scaling robe reels: every new viral reel adds orders that come back as refunds, chargebacks and 1-star reviews, and that drags on Meta page quality. _Evidence: voice/support_themes.csv; merryjammies.com product page (fetched 2026-10-18)_
- **MerryFire: pour-in liquid-fuel tabletop fire pits are under a US CPSC consumer alert.** In a Dec 2024 alert, CPSC told consumers to stop using, and sellers to stop selling, fire pits that burn pooled alcohol or other liquid fuel, including bioethanol. Such products violate ASTM F3363-19, and CPSC links them to 2 deaths and 60+ injuries (the Colsen tabletop pits were recalled). The MerryFire page says it 'runs on liquid bio-ethanol', is 'safe to use indoors' and 'toasts marshmallows indoors'. worlds.py lists 'pour fuel into the steel cup' as a natural action. Omar should check with the supplier and a compliance adviser before making more MerryFire content. Until then, the engine should drop fuel-pouring shots and indoor-safety claims. This is not legal advice. _Evidence: cpsc.gov consumer alert (Dec 19 2024) + Colsen recall; merryfire.com page (fetched 2026-10-18)_
- **Testimonials repeat across stores.** The MerryJammies and MerryGlow pages show the same four reviewer names (Danielle P., Rachel T., Bree T., Morgan W.) with templated text. Meanwhile, one-star Loox reviews keep arriving in the inbox. The FTC's 2024 rule on consumer reviews (16 CFR Part 465) carries civil penalties for fake or misattributed reviews. Replace these blocks with genuine Loox reviews. The MerryGlow line 'our social media … contains AI-generated content that has no correlation to our products' also feeds the 'not as advertised' complaints. _Evidence: merryjammies.com + merryglows.com pages (fetched 2026-10-18); support_themes.csv scam_trust/not_as_pictured_
- **Viewers call out AI, and some say it cost a sale.** 102 AI call-outs in 8,475 competitor comments. Examples: 'pls tell me its not AI' (199 likes), 'I would of purchased it if wasn't integrated with AI' (52), 'I can't see the real product so it could literally just be a string', and 'Can you stop using ai and show us what it actually looks like'. The tells they name are: foot pockets that change between shots, the bag ripping, a USB that 'magically fit into the port', and a too-perfect store aisle. The QA gate should log these tells (not re-roll them, per D33) and prompts should prevent them. The 20% experiment slot should test one real-proof shot per product. _Evidence: comments.csv code ai_callout: robe 33, MerryGlow 45, mask 9, carrier 12_

## 1. Cross-product findings
- **'Where do I buy it?' and 'How much?' are the #1 comment on every decor/gift video.** Combined share: projectors/lights 28% (1,000 of 3,572), window/curtain lights 42% (357 of 849), cat carrier 22%, robe 11%. Viewers get angry when an ad never says where to buy ('why advertise when we can't buy it', 'no good advertising if ya can't buy it'). Every reel needs a where-to-buy answer: a final card 'SAY "<KEYWORD>" for the link' plus the link caption (D5/D6). Never leave it implicit.
- **Disbelief is the strongest buying question.** 'No way that little candle melts all that chocolate' (781 likes), 'I'd like to see what it really looks like' and 'If this don't look like hers when I buy it…' / 'it won't..I got it and it sucks'. Answer the doubt on screen with a proof shot in real time (timer card), shot on a normal-sized tree, room or window, not a mansion ('Step one have a massive house with a huge ceiling').
- **The most-liked comments are jokes and wordplay, not questions:** 'cold alcoholics' misread (7,945 likes), 'tripping to your death has never been easier' (4,056), 'Clam Cooker 3000' (993), 'sorry I can't go out, I'm charging my hoodie' (1,021). Hooks that invite a pun or roast drive comment volume. Use customers' jokes as hook or caption lines, especially jokes that also answer an objection (charging, tripping).
- **'Too early for Christmas' backlash is real and it drives comments.** On mug videos 70 of 751 comments (9%) mention Halloween/October, and the defence 'IM SO READY FOR CHRISTMAS' has 3,337 likes. In October, a calm, on-purpose line ('I don't care that it's October 🎄') turns the backlash into a debate in our favour. Test it in the experiment slot.
- Store fakery gets noticed: 'Why say it's from Target if it's not?', 'It's $134 and not at Target', 'price labels… shelves smh'. This supports D4 (keep the JK flip) and D12/D26 (no logos).
- A large share of competitor commenters write in Spanish or Portuguese (TikTok's international distribution). Our FB/IG audience is US-first, so treat non-English intent as a demand signal, not a targeting change.

## 2. Does comment mix track views? (`voice/engagement_correlation.csv`)
| dataset | x | rho (Spearman vs log10 views) | n |
|---|---|---|---|
| competitor/library videos (top comments) | share_q_any | 0.009 | 46 |
| competitor/library videos (top comments) | share_q_where_buy | 0.002 | 46 |
| competitor/library videos (top comments) | share_q_price | 0.026 | 46 |
| competitor/library videos (top comments) | share_tag_friend | -0.113 | 46 |
| competitor/library videos (top comments) | share_desire | 0.146 | 46 |
| competitor/library videos (top comments) | share_objection | 0.059 | 46 |
| competitor/library videos (top comments) | share_humor | 0.161 | 46 |
| competitor/library videos (top comments) | share_complaint | 0.124 | 46 |
| competitor/library videos (top comments) | share_comparison | 0.263 | 46 |
| own reels, Meta Insights exports (MG/MGS/MF/MC/BH, views>=500) | comments_per_1k_views | 0.413 | 42 |
| own reels, Meta Insights exports | comments_count | 0.799 | 42 |
| own reels, Meta Insights exports (MG/MGS/MF/MC/BH, views>=500) | shares_per_1k_views | 0.671 | 16 |
| own reels, Meta Insights exports | shares_count | 0.846 | 16 |

Read: on 47 competitor videos, no comment-mix share tracks views reliably (all |rho| ≤ 0.27; at n=47, |rho| needs about 0.29 for p<0.05). Comparisons (0.27), desire (0.16) and humour (0.13) lean positive; tag-a-friend leans negative (−0.10). On our own pages (Meta Insights, MG/MGS/MF/MC/BH), comments per 1K views (rho 0.41, n=42) and shares per 1K views (rho 0.67, n=16) rise with reach. That fits engagement-weighted distribution, but the causation runs both ways. Use comment mix as a diagnostic, not a predictor (consistent with D35). Re-run once HJ/MJIG Insights and the browser-captured comments on our own reels land.

## 3. Grinch robe (HeatedJammies / MerryJammies)
Base: 2,654 comments on 16 videos; sources {'tiktok_public': 2654}; audience {'competitor': 2654}.

| code | n | share | liked share | videos | top phrases |
|---|---|---|---|---|---|
| Uncoded | 1258 | 47.4% | 45.1% | 16 | robe (60), cold (24), cozy (19), want (12), don t (12), cool (10), blanket (8), need (7) |
| Purchase intent / desire | 320 | 12.1% | 12.7% | 16 | need (83), want (36), quiero (13), yo quiero (8), cold (7), necesito (6), always cold (6), quiero uno (6) |
| Praise | 270 | 10.2% | 12.3% | 16 | love (58), beautiful (18), nice (16), awesome (16), amazing (12), cute (4), i'd love (4), pretty (4) |
| Where to buy / link / name | 223 | 8.4% | 9.0% | 16 | link (47), donde (10), send (5), comprar (4), need (4), quiero uno (4), puedo (4), donde lo puedo (4) |
| Humor | 171 | 6.4% | 6.3% | 16 | need (8), feet (4), cold (3), time (3), knowing my luck (3), live in texas (3), people (2) |
| Tag-a-friend | 158 | 5.9% | 4.9% | 9 | need (2) |
| Other question | 134 | 5.1% | 5.7% | 15 | cold (6), want (4), make (3), need (2), walk (2), foot pockets (2), pockets heated (2), come (2) |
| Price | 78 | 2.9% | 2.7% | 14 | much (20), price (6), precio (5), cost (4), them (3), cuanto cuesta (3), didn t (3), costco (2) |
| Objection | 56 | 2.1% | 2.6% | 11 | fake (4), ai look (4), s ai (3), scam (2), look (2), tripping (2), don t (2), expensive (2) |
| Material / safety | 43 | 1.6% | 1.8% | 12 | wash (12), safe (4), am i supposed (2), supposed to wash (2), someone say (2), know (2), fire hazard (2), know a fire (2) |
| How it works (power, battery, app, noise) | 35 | 1.3% | 1.3% | 10 | battery (4), charge (3), come (2), into (2), portable battery (2), battery pack (2), portable battery pack (2), don t (2) |
| AI call-out | 33 | 1.2% | 1.6% | 5 | ai look (4), s ai (3), look (2), definitely ai (2), price labels (2), shelves smh (2) |
| Size / fit | 27 | 1.0% | 1.1% | 11 | size (4), tall (4), long (2), adult money (2) |
| Shipping / arrive by Christmas | 10 | 0.4% | 0.4% | 5 | s sooooo (2), sooooo hot (2), christmas time (2), australia it s (2), s sooooo hot (2), hot at christmas (2) |
| Complaint (owners) | 9 | 0.3% | 0.2% | 6 | didn't work (2), work after (2), few months (2), powerbank while (2), while using (2), didn't work after (2), after a few (2), months and needs (2) |
| Comparison | 6 | 0.2% | 0.3% | 4 |  |
| Disbelief ('no way that works') | 3 | 0.1% | 0.1% | 2 |  |
| 'Too early for Christmas' | 3 | 0.1% | 0.1% | 2 |  |
| Emotional story (not quoted) | 2 | 0.1% | 0.1% | 2 |  |

**Top questions**
- Where to buy / link / name: 223 (8.4%). "You shouldn’t have properly showed me to where can I get one?" (795 likes) · "How can I get this nonsense🥹" (315 likes) · "Donde se vende esa manta maravillosa?" (65 likes)
- Other question: 134 (5.1%). "Who else misread that as cold alcoholics?! You're my people!" (7945 likes) · "Wouldn't a coldaholic want it to be cold not warm?" (1616 likes) · "Wanna hang out? Yeah. 1 sec im charnging my hoodie." (1021 likes)
- Price: 78 (2.9%). "I thought it was a flying squirrel costume!" (27 likes) · "¿Donde se consigue? ¿Qué precio tiene?" (26 likes) · "How much I do like that I need to get me one of those and where can I get it?" (15 likes)
- Material / safety: 43 (1.6%). "i know ai when i smell it." (88 likes) · "what about washing?? is it safe to wash?" (87 likes) · "how do you wash it" (36 likes)
- How it works (power, battery, app, noise): 35 (1.3%). "sorry I can't go out I need to charge my sweater" (65 likes) · "It needs to be rechargeable so you can use it in a car. A house allready has heat." (12 likes) · "I'm a skinny 67 year old that spends all winters in Mexico and summers in Northern Canada...does it come in blue?" (12 likes)

**Objections, disbelief, AI call-outs**
- Objection: 56 (2.1%). "tripping to your death has never been easier" (4056 likes) · "pls tell me its not AI" (199 likes) · "i know ai when i smell it." (88 likes)
- AI call-out: 33 (1.2%). "pls tell me its not AI" (199 likes) · "i know ai when i smell it." (88 likes) · "Odio los comerciales de IA" (35 likes)
- Complaint (owners): 9 (0.3%). "Don't buy it my daughter got one for Christmas stopped working the next day and now coming out" (1 likes) · "Never got it, pretty sure it's a scam 😳" (1 likes) · "why so many ppl saying never got it. many comments not good." (1 likes)
- Disbelief ('no way that works'): 3 (0.1%). "Is this real? I just have this" (3 likes) · "I need this. Is it real!??" (2 likes) · "is this real and if it is i really want one !" (2 likes)
- 'Too early for Christmas': 3 (0.1%). "Fuck it can we get through Halloween first and then Thanksgiving?" (1 likes) · "fuck off too early" (0 likes) · "WHY CHRISTMAS …!!!!!! It’s September - this is traumatizing" (0 likes)

**Purchase-intent language**
- Purchase intent / desire: 320 (12.1%). "forget my mom i want this" (2316 likes) · "Wouldn't a coldaholic want it to be cold not warm?" (1616 likes) · "I would forget my feet were in there, stand up, step, and...trip and land on my face....but I still want one!😁🤣" (231 likes)

**Our own customers (support inbox, read-only, aggregated; 164 customer threads, multi-label)**
| theme | threads | share | first-last | example |
|---|---|---|---|---|
| never_received_or_late | 105 | 64% | 2026-09-15..2026-10-19 | I still have not gotten any updates or anything on my order I just want to know what's going on it has not been shipped and it's been over a |
| refund_return_cancel | 50 | 30% | 2026-09-15..2026-10-18 | Is it possible to cancel my order? I did realize it would take so long to receive them and I bought them for a bday present next month. |
| missing_heat_controller | 16 | 10% | 2026-10-12..2026-10-18 | Good Morning, I would like to return my. The robe does not have a remote to turn it on, it only has a USB connection , and the robe is very  |
| not_as_pictured | 14 | 9% | 2026-10-12..2026-10-18 | Hello, I am writing you this email because I have not received the robe and was wondering if it arrived to a different address. |
| quality_defect | 8 | 5% | 2026-10-12..2026-10-18 | This is my order number [n]. I just after 2 months got this in the mail. |
| scam_trust | 8 | 5% | 2026-10-06..2026-10-17 | hi, got any proof of when I will get this as I'm now starting to think it's a scam |
| presale_question | 6 | 4% | 2026-09-13..2026-10-16 | My order hasn't arrived do you have a delivery date? |
| wrong_item | 5 | 3% | 2026-10-12..2026-10-16 | I've just received my order. It was a month later than advertised and is the wrong one. |
| sizing | 3 | 2% | 2026-10-14..2026-10-16 | I need a refund for my order. The robe looks absolutely nothing like what I ordered. |
| positive | 1 | 1% | 2026-10-14..2026-10-14 | To whom it may concern, I have not received my order yet!! |

**Competitor weaknesses / gaps we can beat**
- Competitor owners complain about power, durability and delivery: 'I own it and it sucks!', 'didn't work after a few months and needs a Powerbank', 'stopped working the next day', 'Never got it, pretty sure it's a scam'. Our plug-in, 5-level design beats USB power-bank robes, but only if we actually ship the controller (see alert). _(complaint 9 + power/charge 37 mentions)_
- Price objection framed as a comparison: 'Almost the same as the Westinghouse heated wearable blanket which is half the cost. Can I ask what makes yours better?', 'Costco heated throw $29.99 with a forever warranty'. Answer what makes ours different (character design, foot pocket, 5 levels + timer) on screen. _(price_obj 27, comparison 6)_
- Floor length and foot pockets scare people: 'tripping to your death' (4,056 likes) and 28 trip/fall mentions. No competitor answers it. We can. _(trip 28)_

**Recommended VIDEO moves**
- Body card answering the top question (cord/charging, 37): 'Plugs in = actually gets HOT 🔥 (5 levels)'. Shot: the controller dial clicking 1→5. Only use it once the controller ships in the box. _(power/charge 37; support missing_heat_controller 16+)_
- Show the robe going in the washing machine after the controller detaches. Text: 'Yes, it's machine washable 🧺' (31 wash questions; 'is it safe to wash?' 87 likes). _(wash 31)_
- Anti-trip shot: step out of the foot pocket and walk to the kitchen. Customers wrote this joke themselves ('How do I walk back to the fridge…'), so it lands as humour plus proof. _(trip 28; top comment 4,056 likes)_
- Casting proof for 'man size' (20) and 'tall' (14) asks: one packed body shot of a tall adult or husband wearing it with the hem at the ankle. Text: 'Fits up to 5'10"'. _(man/guy 20, tall/length 14)_
- Hook lines in customers' words: 'Forget my mom, I want this 😳' (2,316 likes), 'Sorry I can't go out… I'm charging my robe 😂' (1,021+65+8 likes, also handles the plug objection), 'Women are hard to gift..' (HJ-01 proven). _(desire top examples)_
- Prompt QA: the foot pocket must stay the same across cuts and the bag must open naturally. Commenters cite both as AI tells ('first it is connected to the robe, than not'). Log, don't re-roll (D33). _(ai_callout 33)_

**Recommended WEBSITE / product-page fixes**
- Put making time plus shipping next to the price and the Add to Cart button (e.g. 'Made to order: ships in X weeks. Order by <date> for Christmas'). Remove the 'Free International Shipping, tracked' headline that sets a 1–2-week expectation. 106 of 164 support threads are 'where is my order'. _(support never_received_or_late 106)_
- Add a 'What's in the box' photo showing the robe, the 5-level controller and the plug, and make sure it matches the supplier's shipment. Add 'Plug-in, not battery: no power bank needed'. _(support missing_heat_controller 16+, not_as_pictured 14)_
- FAQ additions: 'Will I trip in the foot pocket?', 'Men's / tall fit?' (one size to about 5'10", say so in inches next to the size), 'How long is the cord?' (15 likes), 'Other characters/colours?' (29). _(trip 28, man/guy 20, colours 29)_
- Replace the templated testimonials with real Loox reviews (alert 3). _(page fetch)_

## 4. MerryFire tabletop fire pit
Base: 32 comments on 1 videos; sources {'tiktok_public': 32}; audience {'competitor': 32}.

| code | n | share | liked share | videos | top phrases |
|---|---|---|---|---|---|
| Praise | 12 | 37.5% | 38.3% | 1 | amazing (2) |
| Uncoded | 9 | 28.1% | 28.8% | 1 |  |
| Purchase intent / desire | 6 | 18.8% | 14.2% | 1 |  |
| Other question | 5 | 15.6% | 13.5% | 1 |  |
| Material / safety | 2 | 6.2% | 6.4% | 1 |  |
| Price | 2 | 6.2% | 9.7% | 1 |  |
| How it works (power, battery, app, noise) | 1 | 3.1% | 5.0% | 1 |  |
| Size / fit | 1 | 3.1% | 2.4% | 1 |  |
| Where to buy / link / name | 1 | 3.1% | 5.0% | 1 |  |

**Top questions**
- Other question: 5 (15.6%). "Wow es perfecto 🤩 oye trae algo para cubrirlo o como lo protejes ?" (1 likes) · "Woo. Seve súper padre. Viene todo incluido. Es fácil de. Armar ?" (0 likes) · "Viene con todos los accesorios que muestras en el video?" (0 likes)
- Material / safety: 2 (6.2%). "Wou que hermoso de que es el material ? No es muy pesado" (1 likes) · "Amiga de qué material es el asador m refiero q si es pesado o lijero" (0 likes)
- Price: 2 (6.2%). "Omg the price us amazing 😍😍😍" (7 likes) · "The price is amazing!! Adding to my cart 😍" (0 likes)
- How it works (power, battery, app, noise): 1 (3.1%). "When does it come back ?" (2 likes)
- Size / fit: 1 (3.1%). "Es facil armar amiga es no me gusta andar batallando 😅" (0 likes)

**Purchase-intent language**
- Purchase intent / desire: 6 (18.8%). "I need it for the children since they love to do marshmallows" (0 likes) · "must have it's amazing 🥰" (0 likes) · "Getting this next week 🥰🥰🥰" (0 likes)

**Competitor weaknesses / gaps we can beat**
- Public comment data is thin (1 on-topic competitor video, 32 comments). Market reviews (Amazon Colsen 4.6★ from 1,632 reviews, bobvila test) praise 'no smoke, no smell'. Their pain points: soot builds up, the bowl stays hot about 30 min after the flame dies, burn time is 30–50 min, a fire marshal advised ventilation, and concrete edges crumble. Ceramic plus a snuffer rim answers several of these, but see the CPSC alert first. _(web reviews 2026-10-18; comments.csv merryfire 32)_

**Recommended VIDEO moves**
- Blocked pending alert 2: no fuel-pouring shots and no indoor-safety claims. If cleared, show the snuffer rim putting the flame out in one second, the flame next to a s'mores tray, and a heat-safe tray underneath. Text: 'Out in 1 second 🔥→💨'. _(CPSC alert; competitor reviews)_
- Capture comments on our own MerryFire reels (browser queue P1/P2) before writing more hook lines. There is no customer-language evidence yet. _(browser_queue.csv)_

**Recommended WEBSITE / product-page fixes**
- State the exact burn time in minutes (currently 'a long evening'), the weight and dimensions, and 'hot for ~30 min after: let it cool'. Re-check every indoor claim against the CPSC alert. _(competitor review pain points)_

## 5. Brick Hood ski mask
Base: 237 comments on 3 videos; sources {'tiktok_public': 237}; audience {'competitor': 237}.

| code | n | share | liked share | videos | top phrases |
|---|---|---|---|---|---|
| Uncoded | 133 | 56.1% | 52.9% | 3 | hood (3), joy tears (3), tears of joy (3), cold (2), good (2), make (2), doesn t (2), winter fun (2) |
| Humor | 42 | 17.7% | 16.3% | 3 |  |
| Praise | 21 | 8.9% | 8.4% | 3 | love (5), awesome (3), wow that's (2), that's awesome (2), wow that's awesome (2), last year (2) |
| Objection | 19 | 8.0% | 11.8% | 3 | people (2), expensive for bucks (2), bank robbers (2), robbers dream (2), bank robbers dream (2) |
| Purchase intent / desire | 14 | 5.9% | 6.9% | 2 | need (6), family need (2) |
| AI call-out | 9 | 3.8% | 5.8% | 3 |  |
| Material / safety | 3 | 1.3% | 1.3% | 1 | still cheap (2), cheap material (2), still cheap material (2) |
| Other question | 3 | 1.3% | 1.4% | 2 |  |
| Price | 3 | 1.3% | 1.7% | 1 |  |
| Where to buy / link / name | 2 | 0.8% | 1.3% | 1 |  |
| Comparison | 1 | 0.4% | 0.6% | 1 |  |
| Complaint (owners) | 1 | 0.4% | 0.6% | 1 |  |
| How it works (power, battery, app, noise) | 1 | 0.4% | 0.8% | 1 |  |
| Size / fit | 1 | 0.4% | 0.7% | 1 |  |

**Top questions**
- Material / safety: 3 (1.3%). "Is this made with 100% cotton and linen or are they plastics involved?" (1 likes) · "Still cheap material on a 0• day" (0 likes)
- Other question: 3 (1.3%). "Michael Scofield?" (0 likes) · "so how long until somebody starts using it for robbing banks and stores?" (0 likes)
- Price: 3 (1.3%). "Awesome ❄️☃️❄️How Much" (0 likes)
- Where to buy / link / name: 2 (0.8%). "where can I get one" (2 likes) · "where can I get it" (1 likes)
- How it works (power, battery, app, noise): 1 (0.4%). "if only the outside was waterproof" (3 likes)

**Objections, disbelief, AI call-outs**
- Objection: 19 (8.0%). "I would of purchased it if wasn’t integrated with AI🙄" (52 likes) · "Nope! I'll pass. People always scared of you when you walk around them. They always thinking you're up to no good" (18 likes) · "get a wildson hood!! same product, but a small business and no AI!!!" (7 likes)
- AI call-out: 9 (3.8%). "I would of purchased it if wasn’t integrated with AI🙄" (52 likes) · "get a wildson hood!! same product, but a small business and no AI!!!" (7 likes) · "I would literally buy this, but now I won’t because of the ai I can’t see the real product so it could literally just be a string." (0 likes)
- Complaint (owners): 1 (0.4%). "I guess they improve it cause I bought one last year and it had me sweating" (1 likes)

**Purchase-intent language**
- Purchase intent / desire: 14 (5.9%). "I would of purchased it if wasn’t integrated with AI🙄" (52 likes) · "Beautiful! Perfect hijab . Need one of those" (1 likes) · "I guess they improve it cause I bought one last year and it had me sweating" (1 likes)

**Competitor weaknesses / gaps we can beat**
- Competitor balaclavas get a 'criminal' stigma: 'People always scared of you… thinking you're up to no good', 'now the robbers will be warm', 'Michael Scofield?' (12). Their street and lifestyle settings invite it. Our slopes-only world (D37) avoids it, so keep it strict. _(stigma 12)_
- Lost sales over AI: 'I would of purchased it if wasn't integrated with AI' (52 likes); 'get a wildson hood!! same product… no AI'. Also 'it ain't even that cold' / 'no winters in Midland TX' (warm-climate viewers). _(ai_callout 9)_

**Recommended VIDEO moves**
- Shots: the mask under goggles and a helmet on the chairlift; a close-up of the double-knit texture; a stretch pull over the head. This answers 'stretchy or tight?' and 'cotton or plastic?'. _(fit/material 5)_
- Hook/caption in customers' words: 'I don't need a mask to look that good 😂' (roast bait). Expect a lot of 'where did you get that?' Use squad shots (55% of orders are multi-packs). _(humor 42; Shopify brickhood report)_

**Recommended WEBSITE / product-page fixes**
- Add a product FAQ (the store has none): stretch and fit (one size? kids?), material ('double-knit acrylic', so not cotton), 'windproof, not waterproof', washing, shipping time to US/EU, and multi-pack pricing. _(q_sizing/q_material questions; page fetch 2026-10-18)_

## 6. MerryGlow tree lights (+ Christmas projector competitors)
Base: 3,572 comments on 16 videos; sources {'tiktok_public': 3572}; audience {'competitor': 3572}.

| code | n | share | liked share | videos | top phrases |
|---|---|---|---|---|---|
| Uncoded | 1883 | 52.7% | 49.8% | 16 | christmas (267), need (60), santa (35), order (26), ganda (14), ang ganda (12), navidad (12), lights (9) |
| Where to buy / link / name | 654 | 18.3% | 20.2% | 14 | donde (109), comprar (66), dónde (44), venden (42), puedo (35), donde lo venden (30), puedo comprar (30), link (25) |
| Price | 346 | 9.7% | 9.4% | 14 | much (56), precio (51), donde (16), price (15), costco (12), venden (9), much po (8), c'est combien (8) |
| Purchase intent / desire | 330 | 9.2% | 9.7% | 13 | quiero (58), eu quero (55), need (42), quero (40), yo quiero (38), quiero uno (38), want (18), comprar (17) |
| Praise | 215 | 6.0% | 6.3% | 15 | love (21), nice (19), beautiful (16), lindo (10), hermoso (8), christmas (6), cute (6), awesome (6) |
| Other question | 141 | 4.0% | 4.4% | 15 | buy them (3), order (3), peut (2), como (2), ang ganda (2), lights (2), mo na (2), na kupi (2) |
| Humor | 101 | 2.8% | 3.6% | 14 | aquí en venezuela (4), jajaja jamás (4), ve así (4), jamás se ve (4), venezuela (4), jajaja (4), uffff caramba (3), estos altos (3) |
| AI call-out | 45 | 1.3% | 1.4% | 10 | pura ia (7), inteligencia artificial (4), pura (4), inteligencia (2), artificial (2), ai vs (2), eso es ia (2) |
| Objection | 44 | 1.2% | 1.5% | 10 | fake (2), temu (2), christmas tree (2), ai vs (2) |
| How it works (power, battery, app, noise) | 12 | 0.3% | 0.7% | 5 | proyector navideño (3), navideño usb (3), proyector navideño usb (3), proyector (2) |
| Tag-a-friend | 11 | 0.3% | 0.2% | 6 |  |
| Shipping / arrive by Christmas | 9 | 0.2% | 0.3% | 7 |  |
| Disbelief ('no way that works') | 7 | 0.2% | 0.3% | 5 |  |
| Complaint (owners) | 6 | 0.2% | 0.3% | 4 |  |
| Emotional story (not quoted) | 6 | 0.2% | 0.4% | 2 | navidad (2) |
| 'Too early for Christmas' | 5 | 0.1% | 0.1% | 3 |  |
| Comparison | 4 | 0.1% | 0.2% | 3 | ai vs (2), vs reality (2) |
| Material / safety | 3 | 0.1% | 0.1% | 1 | asi desde (2), co pro (2), pongan lo co (2) |
| Size / fit | 2 | 0.1% | 0.1% | 2 |  |

**Top questions**
- Where to buy / link / name: 654 (18.3%). "yo quiero comprar una dónde la consigo 😊" (269 likes) · "siempre ponen esas cosas hermosa y nunca dicen donde lo venden no se para que lo ponen[Risita]" (264 likes) · "Donde lo puedo comprar ???" (115 likes)
- Price: 346 (9.7%). "cuánto vale gracias" (44 likes) · "proyector navideño dónde se consigue y precio???" (42 likes) · "donde se piden precios gracias" (36 likes)
- Other question: 141 (4.0%). "Qui regarde cette vidéo dimanche ❤️?" (100 likes) · "То, что в розетке ,только на стену отдаёт , а на потолке откуда, да ещё вращается?" (52 likes) · "Какая красота 😍 где можно купить?" (47 likes)
- How it works (power, battery, app, noise): 12 (0.3%). "solo pongan proyector navideño usb en Amazon ai sale" (442 likes) · "the AI is insane . The huge usb magically fit into the port LOL" (255 likes) · "proyector navideño USB" (120 likes)
- Shipping / arrive by Christmas: 9 (0.2%). "delivery address" (10 likes) · "$19.99 Canada Amazon" (8 likes) · "can u deliver in Georgia (Europe) ?" (1 likes)

**Objections, disbelief, AI call-outs**
- AI call-out: 45 (1.3%). "solo pongan proyector navideño usb en Amazon ai sale" (442 likes) · "the AI is insane . The huge usb magically fit into the port LOL" (255 likes) · "alguien siquiera se ha fijado que es IA" (7 likes)
- Objection: 44 (1.2%). "solo pongan proyector navideño usb en Amazon ai sale" (442 likes) · "the AI is insane . The huge usb magically fit into the port LOL" (255 likes) · "Me running to Temu to see if they have this 🤣" (31 likes)
- Disbelief ('no way that works'): 7 (0.2%). "да не будет оно так светить 100%" (263 likes) · "that's dope but I doubt it looks hard as good" (4 likes) · "How does it really look?" (3 likes)
- Complaint (owners): 6 (0.2%). "eso no funciona en Venezuela casi siempre no hay luz 🤣" (851 likes) · "it won't..I got it and it sucks" (233 likes) · "You folks are going to be Sooooo disappointed….thinking they really project like that….lol. Good luck!" (10 likes)
- 'Too early for Christmas': 5 (0.1%). "ITS SEPTEMBER LEAVE ME ALONE FOR NOW" (73 likes) · "It’s September. SEPTEMBER" (1 likes) · "Can we just get through Halloween first please?" (0 likes)

**Purchase-intent language**
- Purchase intent / desire: 330 (9.2%). "yo quiero comprar una dónde la consigo 😊" (269 likes) · "yo quiero uno.. me encanta la navidad 🎄😊.. soy feliz decorandoi casita ..." (41 likes) · "I need someone to buy this, try this, and report back" (41 likes)

**Our own customers (support inbox, read-only, aggregated; 1 customer threads, multi-label)**
| theme | threads | share | first-last | example |
|---|---|---|---|---|
| never_received_or_late | 1 | 100% | 2026-10-11..2026-10-11 | I have not received my order yet. Can please tell me what the update is? |

**Competitor weaknesses / gaps we can beat**
- Expectation gap on light products: 'I'd like to see what it really looks like', 'If this don't look like hers when I buy it…' → 'it won't..I got it and it sucks', 'yo lo compre y no me sirvió porque mi techo…', 'AI vs reality'. Real-proof footage is the gap competitors leave open. _(real vs ai 57; complaint 6)_
- Cheaper-elsewhere comments: 'They're under firecracker lights on TT shop', 'Costco', 'Amazon USB projector'. Price anchoring has to show what's different (app, 12 designs, pixels). _(costco/amazon 50)_

**Recommended VIDEO moves**
- Final card on EVERY reel: 'SAY "TREE" for the link 🎄' (MG proven 'Say "tree"'). Where-to-buy is 18% and price 10% of competitor comments. _(q_where_buy 654, q_price 346 of 3,572)_
- Proof shot: a phone screen tapping through designs while the tree changes (one packed body shot), on a normal 6 ft tree in a normal living room. _(real vs ai 57; 'massive house' objection)_
- Hook in customers' words: 'I like this idea better than putting up a Christmas tree 🎄' (381 likes), adapted as 'Better than rewrapping your tree every year'. Also 'Absolutely no way would I be wrapping lights' → 'Up in 10 minutes ⏱️'. _(comparison top example; LED tree video)_

**Recommended WEBSITE / product-page fixes**
- Keep the strong FAQ. Remove the 'AI-generated content that has no correlation to our products' line and replace it with real photos and video of the kit on a tree. Add a 1-line tree-height picker above Add to Cart (the 'get the taller one' review). _(page fetch; alert 3)_

## 7. JollyGlow curtain / window lights
Base: 849 comments on 4 videos; sources {'tiktok_public': 849}; audience {'competitor': 849}.

| code | n | share | liked share | videos | top phrases |
|---|---|---|---|---|---|
| Uncoded | 357 | 42.0% | 50.5% | 4 | decor (52), prezzo (7), window (6), como (5), prezzo grazie (5), grazie (5), wystrój (4), imagine (3) |
| Where to buy / link / name | 249 | 29.3% | 22.7% | 4 | comprar (42), donde (32), dónde (22), puedo comprar (20), puedo (17), o link (12), onde (12), link (12) |
| Price | 108 | 12.7% | 7.7% | 4 | precio (28), precio tiene (13), donde (8), tiene (7), favor (7), comprar (6), valor (6), qual valor (6) |
| Purchase intent / desire | 81 | 9.5% | 7.6% | 4 | eu quero (17), quiero (15), quero (15), comprar (8), quero comprar (7), como (6), yo quiero (6), como fa (5) |
| Praise | 54 | 6.4% | 5.2% | 3 | lindo (7), beautiful (4), lindo onde (4), love (4), hermoso (4), donde (3), comprar (3), absolutely love (2) |
| Other question | 44 | 5.2% | 6.1% | 4 | projector (2), cómo hago (2) |
| Shipping / arrive by Christmas | 28 | 3.3% | 1.9% | 2 | hacen (6), envíos (6), hacen envíos (5), hacen envios (4), colombia (3), envios (3), hacen envío (3), envío (2) |
| Humor | 20 | 2.4% | 4.9% | 2 |  |
| Size / fit | 7 | 0.8% | 0.5% | 1 |  |
| How it works (power, battery, app, noise) | 5 | 0.6% | 1.0% | 2 |  |
| Objection | 4 | 0.5% | 0.6% | 2 |  |
| AI call-out | 2 | 0.2% | 0.7% | 2 |  |
| Comparison | 1 | 0.1% | 0.1% | 1 |  |
| Disbelief ('no way that works') | 1 | 0.1% | 0.1% | 1 |  |
| Tag-a-friend | 1 | 0.1% | 0.1% | 1 |  |

**Top questions**
- Where to buy / link / name: 249 (29.3%). "where to buy it?" (78 likes) · "Gente! onde compra isso? pelo amor de Deus, eu necessito disso kkk" (75 likes) · "donde lo consigo 😭" (55 likes)
- Price: 108 (12.7%). "È BELLISSIMO COME SI PER COMPRARLO E DI QUANTO IL COSTO.FATE SAPERE.GRAZIE." (5 likes) · "cuánto cuesta y dónde se consigue." (4 likes) · "Soy de la CDMX en donde la puedo conseguir y que precio tiene" (4 likes)
- Other question: 44 (5.2%). "so you dont have a window in a room?" (150 likes) · "напишите кто знает, как называется и где можно купить?" (125 likes) · "alguien en Español???" (37 likes)
- Shipping / arrive by Christmas: 28 (3.3%). "donde los puedo conseguir. hacen envios a Colombia" (6 likes) · "How long does delivery take to the United Kingdom ?" (1 likes) · "dónde lo puedo conseguir soy de ecuador hacen envío" (1 likes)
- Size / fit: 7 (0.8%). "What are the dimensions?" (1 likes) · "looks nice but no mention of size!" (1 likes) · "How does it go on the wall? Dimensions?" (0 likes)

**Objections, disbelief, AI call-outs**
- Objection: 4 (0.5%). "Am I the only one that would be scared imma see a ghost or sum out the fake window😭" (38 likes) · "u can get a decent projector on temu or Amazon for like $50 and get the same effect" (4 likes) · "AI killing these ads." (1 likes)
- AI call-out: 2 (0.2%). "I can't have that, cause I'd sit with my nose on the wall trying to look out that window, knowing perfectly well that's not real. My delulu would win this one" (6751 likes) · "AI killing these ads." (1 likes)
- Disbelief ('no way that works'): 1 (0.1%). "Does the actually work" (0 likes)

**Purchase-intent language**
- Purchase intent / desire: 81 (9.5%). "Lo quiero, cómo hago para comprarla?" (28 likes) · "I want This so bad , it’s crazy how I could imagine overthinking at night with this view 😍" (20 likes) · "quiero está lámpara angel como hago para comprarla" (18 likes)

**Competitor weaknesses / gaps we can beat**
- Competitors don't say where to buy or how big it is: where+price = 42% of comments. 'What are the measurements??', 'is Lukakaka.com a real store', 'esto fue lo que me llegó' (got something different), 'AI killing these ads'. _(q_where_buy 249, q_price 108 of 849)_
- 'Main question is: is the projector noisy?' (2,369 likes). Nobody answers it. _(q_other top example)_

**Recommended VIDEO moves**
- Show the curtain on a normal window, filmed from the street at night (D37 world). Text card: size, e.g. 'Fits a 6 ft window'. End card: 'SAY "GLOW" for the link'. _(measurements 8; where/price 42%)_
- If the unit is silent (no fan), add text: 'Silent: no fan 🤫'. _(noise question 2,369 likes)_

**Recommended WEBSITE / product-page fixes**
- Window-size table (W×H per variant), a 'silent / no fan' statement if true, real night photos, and trust signals (store contact, return policy) above the fold. _(measurements, trust comments)_

## 8. GrinchMelt mug
Base: 751 comments on 5 videos; sources {'tiktok_public': 751}; audience {'competitor': 751}.

| code | n | share | liked share | videos | top phrases |
|---|---|---|---|---|---|
| Uncoded | 395 | 52.6% | 51.6% | 5 | chocolate (15), christmas (12), halloween (10), wait (8), good (6), october (6), don t (5), white chocolate (5) |
| Tag-a-friend | 154 | 20.5% | 17.6% | 5 | need (4), chocolate (2), don t (2), us xx (2) |
| Humor | 48 | 6.4% | 7.0% | 4 | chocolate (4), halloween (3), b m (2), gonna lie (2), white chocolate (2), halloween yet (2), even halloween (2) |
| Purchase intent / desire | 46 | 6.1% | 5.6% | 5 | need (13), want (6) |
| Praise | 40 | 5.3% | 5.7% | 5 | love (8), cute (2), amazing (2), christmas (2), love christmas (2), beautiful (2) |
| 'Too early for Christmas' | 37 | 4.9% | 6.9% | 3 | halloween (12), even (10), even halloween (7), halloween yet (7), even been halloween (6), october (6), s october (5), hasn t (4) |
| Other question | 21 | 2.8% | 2.8% | 5 | melt (2), halloween (2) |
| Where to buy / link / name | 12 | 1.6% | 1.6% | 4 |  |
| Objection | 10 | 1.3% | 1.7% | 3 |  |
| Material / safety | 7 | 0.9% | 1.7% | 2 |  |
| How it works (power, battery, app, noise) | 5 | 0.7% | 0.6% | 2 |  |
| Price | 3 | 0.4% | 0.4% | 1 |  |
| Disbelief ('no way that works') | 3 | 0.4% | 0.9% | 3 |  |
| Shipping / arrive by Christmas | 2 | 0.3% | 0.3% | 2 | take to melt (2) |
| AI call-out | 1 | 0.1% | 0.1% | 1 |  |
| Comparison | 1 | 0.1% | 0.1% | 1 |  |
| Size / fit | 1 | 0.1% | 0.1% | 1 |  |

**Top questions**
- Other question: 21 (2.8%). "can we actually pay attention to halloween for once?" (15 likes) · "HALLOWEEN ISN'T EVEN HERE YET??" (6 likes) · "Do y’all think a TINY CANDLE is going to melt your stuff? You’ll be waiting a while" (4 likes)
- Where to buy / link / name: 12 (1.6%). "where i can get this??" (51 likes) · "Donde venden eses baso" (6 likes) · "Where can I get this" (2 likes)
- Material / safety: 7 (0.9%). "If everyone keeps saying the chocolate burns quick just blow out the candle?" (2110 likes) · "This looks cool! Once the candle has burned down, can the mug be safely cleaned and used as a normal drinking mug?" (95 likes) · "Can u teach me how to smell comments??" (13 likes)
- How it works (power, battery, app, noise): 5 (0.7%). "does it come w the candle" (3 likes) · "Does it come with a candle?" (2 likes) · "Wait does it come with candles?" (1 likes)
- Price: 3 (0.4%). "The price acc really good ngl" (3 likes) · "What price? It’s basically free!" (2 likes) · "cheap the price is perfect" (2 likes)

**Objections, disbelief, AI call-outs**
- 'Too early for Christmas': 37 (4.9%). "im moreso focused on how halloween isnt even over yet" (722 likes) · "its not even Halloween" (117 likes) · "it hasn't even been halloween yet calm down" (63 likes)
- Objection: 10 (1.3%). "Do people not own microwaves" (131 likes) · "I'd just stick it in the microwave rather than wait for however long that would take" (25 likes) · "I have a microwave" (5 likes)
- Disbelief ('no way that works'): 3 (0.4%). "No way that little candle melts all that chocolate" (781 likes) · "I'd just stick it in the microwave rather than wait for however long that would take" (25 likes) · "there's no way that works" (0 likes)
- AI call-out: 1 (0.1%). 

**Purchase-intent language**
- Purchase intent / desire: 46 (6.1%). "Uuuo I need THIS 😋😋" (157 likes) · "I need that mug thingy nowwww" (5 likes) · "I already finished my Christmas list😭😭" (5 likes)

**Competitor weaknesses / gaps we can beat**
- Disbelief and slowness: 'No way that little candle melts all that chocolate' (781 likes), 'Do people not own microwaves' (131), 'You'll be waiting a while'. Safety: 'Does the cup get really hot?', 'isn't this a safety hazard?', 'chocolate burns quick' → 'just blow out the candle' (2,110 likes). Competitors never show the timing. _(candle doubt 38, microwave 4 (131 likes), safe/hot/burn 24)_

**Recommended VIDEO moves**
- Calm proof (D37 calm world): a real-time melt with a small timer card ('melted in X min'; measure it, never invent), then a dip. Hook in their words: 'No way that tiny candle melts all this… 🕯️🍫'. _(skeptic top example 781 likes)_
- Show it doubling as a normal mug once the candle is out ('can the mug be used as a normal drinking mug?', 95 likes) and the candle included in the box ('does it come with the candle?', 3). _(reuse mug 95 likes; come w candle 3)_
- October experiment: text 'I don't care that it's October 🎄☕' to turn the too-early debate (9% of comments) into comments. _(too_early 70 of 751)_

**Recommended WEBSITE / product-page fixes**
- FAQ: candles included (how many, burn time), minutes to melt, 'does the handle get hot?', dishwasher safe, 'use as a normal mug'. _(q_how_it_works / safety questions)_

## 9. PurrVenture cat carrier
Base: 380 comments on 3 videos; sources {'tiktok_public': 380}; audience {'competitor': 380}.

| code | n | share | liked share | videos | top phrases |
|---|---|---|---|---|---|
| Uncoded | 201 | 52.9% | 51.2% | 3 | corazón ojos (4), ojos de corazón (4), gato (3), mesh (2), pobre (2), cats (2), small fan (2), pobre gatito (2) |
| Where to buy / link / name | 61 | 16.1% | 13.5% | 3 | donde (14), dónde (8), compro (5), información (5), donde lo compro (4), venden (4), consigo (4), puedo comprar (3) |
| Purchase intent / desire | 36 | 9.5% | 9.2% | 2 | quiero (10), yo quiero (9), necesito (6), quiero uno (5), necesito uno (3), yo quiero uno (3), uno para mí (2), quiero dos (2) |
| Praise | 28 | 7.4% | 7.1% | 2 | lindo (2), donde (2), precios (2), corazón rojo (2), rojo corazón (2), corazón rojo corazón (2), rojo corazón rojo (2), hermosos donde (2) |
| Price | 22 | 5.8% | 6.0% | 2 | price (5), precio (2), precios (2), precio tienen (2), precios y tamaños (2) |
| Other question | 18 | 4.7% | 5.6% | 3 |  |
| Humor | 13 | 3.4% | 4.8% | 2 |  |
| AI call-out | 12 | 3.2% | 6.2% | 2 | about ai (2) |
| Objection | 12 | 3.2% | 6.2% | 2 | about ai (2) |
| Tag-a-friend | 7 | 1.8% | 1.2% | 2 |  |
| Size / fit | 3 | 0.8% | 0.9% | 1 |  |
| Shipping / arrive by Christmas | 1 | 0.3% | 0.3% | 1 |  |

**Top questions**
- Where to buy / link / name: 61 (16.1%). "“Oh this is Ai” WHERE??" (131 likes) · "DONDE LO COMPRO DÍGANME" (11 likes) · "Por eso es que yo veo los videos y sigo de largo porque me da mal genio que no den información completa" (11 likes)
- Price: 22 (5.8%). "q manera de subir y no desir donde conseguir y ni precios dan" (7 likes) · "en donde se consigue y que precio tiene" (6 likes) · "mojy ya bag chiye Kiya price ha iski" (5 likes)
- Other question: 18 (4.7%). "Pk son chat il est calme? La mienne elle court et saute partout j’crois je l’es jamais vue calme la mienne …" (104 likes) · "Ой... где, где купить такой рюкзачок???" (27 likes) · "por qué les cortan las uñas a los gatos? eso nunca se hace. Yo jamás se las corto a los míos." (7 likes)
- Size / fit: 3 (0.8%). "necesito uno para mí gato, talla grande xD" (4 likes) · "i have 3 adult cats how can i going ??😂😂" (2 likes) · "Do you guys sell these in jumbo sizes" (1 likes)
- Shipping / arrive by Christmas: 1 (0.3%). "precio y si hacen envíos" (2 likes)

**Objections, disbelief, AI call-outs**
- Objection: 12 (3.2%). "using ai makes you look hella untrustworthy, by the way.." (3052 likes) · "I dont believe you the rest of your videos are ai" (620 likes) · "I hate ai guys, but they’re right 😓 I own a cat rescue and mesh bags are 100% the best" (524 likes)
- AI call-out: 12 (3.2%). "using ai makes you look hella untrustworthy, by the way.." (3052 likes) · "I dont believe you the rest of your videos are ai" (620 likes) · "I hate ai guys, but they’re right 😓 I own a cat rescue and mesh bags are 100% the best" (524 likes)

**Purchase-intent language**
- Purchase intent / desire: 36 (9.5%). "Necesito uno extra extra grande para mi Gordo Tilín de 6 meses 😁" (37 likes) · "Necesito, me urge, que hay que hacer para conseguirlo." (16 likes) · "necesito uno para mí gato, talla grande xD" (4 likes)

**Competitor weaknesses / gaps we can beat**
- Welfare objections on competitor carrier videos: 'poor cat', 'that hurts its neck/spine', 'the cats will tear right through that mesh' (19), plus 'oh this is AI' (12). A calm cat walking in by itself answers both. _(welfare 19, ai 12)_

**Recommended VIDEO moves**
- Shots: the cat walks in voluntarily; inside view showing room to turn; mesh close-up. Hook in their words: 'I need it' (2,560 likes). End card where-to-buy (22% of comments). _(desire top example; where 61+22)_

**Recommended WEBSITE / product-page fixes**
- Weight/size limit in kg and lb ('extra extra grande para mi gordo' 37 likes), ventilation, mesh strength, airline fit. _(q_sizing / desire examples)_

## Method and limits
- Competitor comments are TikTok's top ~150–350 comments per video (relevance order = most-liked first), so they are biased toward jokes and popular takes. Questions are under-represented compared with the full thread.
- FB/IG comments (our reels plus IG competitors) need a logged-in browser. They are queued in voice/browser_queue.csv. Our own-reel comment data is still 0 until that queue runs.
- YouTube is blocked from the box ('Sign in to confirm you're not a bot'; cookies would mean using a credential, so we didn't). Reddit's JSON API returns 403 without OAuth. Amazon reviews: only web-search summaries were used, no scraping.
- Gmail: read-only search_threads snippets only (no bodies), 298 threads from 6 queries (Sep 13 to Oct 19). Snippets are short, so 'missing controller' is undercounted. Raw results were deleted after aggregation; only themes and short name-checked quotes are kept.
- The rules-and-keywords codebook is multi-label and transparent. About 50% of comments stay 'uncoded' (emoji, reactions, off-topic), which is normal for comment sections. Precision was spot-checked by reading top examples, not formally measured.
- One corpus label error found and excluded: EXT stonebrook.home 'portable fire pit' is actually a portable TV.
