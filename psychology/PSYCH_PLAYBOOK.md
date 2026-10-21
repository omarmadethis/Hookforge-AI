# Consumer psychology playbook for Hookforge reels (2026-10-18 PT)
Every principle below has (a) a peer-reviewed or canonical source, (b) the observable reel features it maps to, (c) our evidence and external evidence with n, and (d) an execution recipe. The machine version is `psych_codebook.csv` (19 codes the backtester can score). The raw flag table is `psych_flag_evidence.csv`.
**Evidence base.** Ours = FB reels with views (n=63; hit ≥50K; IG excluded so platform scales don't mix), plus 41 hand-coded shot sequences of ours (`style/shots.csv`; 12 covered-reveal reels added 2026-10-18 ~10 PM PT, see `style/covered_hooks.csv`) and 33 CapCut-truth emoji rows. External = 120 corpus external/reference/viral-research reels (hit ≥1M; not recency-weighted here, the backtester applies `recency_weight`). Flags come from `taxonomy.code_psych` (rule-coded) unless marked as hand-coded. Our n is small, so read ±15 pp as noise.
**Citation check.** DOIs were confirmed against the Crossref API on 2026-10-18, except the classics marked (book/classic) and three I'm citing from memory (marked *). WebSearch was down during this run.

## Tier 1: principles our data supports (exploit)
### 1. Contrast and reference dependence: the cringe → delight arc
- **Source:** Kahneman & Tversky 1979, prospect theory (outcomes are judged against a reference point), Econometrica doi:10.2307/1914185*. Cialdini's contrast principle, *Influence* (book).
- **Mechanism:** a bad "then" state sets a low reference point, so the same product looks better by contrast.
- **In a 13 s reel:** a WS chaos "then" shot with no product (0–2 s) → a "Vs..." bridge → a POV unbox → a static lit hero. Text cards follow the emotional arc: 😬/🤕/🤮 → ⏳ → 🤩/😻.
- **Evidence:** F04 5/7 ≥50K (152.9K, 84.4K, 70.4K, 67.7K, 64.5K). transformation flag 7/12 (median 66K) vs 26/51. External transformation 7/10 ≥1M; concept-vs-result heated jacket 6.8M.
- **Execute:** hook text "Christmas 2024.. 😬" / "Christmas last year.. 🤕". Shot = handheld "filmed from across the room" disaster. Music = proven upbeat (Last Christmas from 2:50 on lights; Bublé from 0:32 on fire). The caption restates the "now".

### 2. Curiosity / information gap, but only with a visible cue
- **Source:** Loewenstein 1994, Psychol Bull doi:10.1037/0033-2909.116.1.75: curiosity is a felt gap between what we know and want to know, and it peaks when some information is already in hand. Kang et al. 2009, "The wick in the candle of learning" (curiosity follows an inverted U and engages reward circuitry), SSRN doi:10.2139/ssrn.1308286.
- **Observable:** a cut-off word ("doesn't exi-"), "The idea 🤮", "Vs..", "POV: you finally found…", with the product or outcome partly visible by 1.5 s.
- **Evidence:** curiosity_gap 6/10 ≥50K vs 27/53. External 17/24 ≥1M with a higher median (1.95M vs 1.50M).
- **Covered reveal is an allowed, proven version of this gap (Omar, 2026-10-18 9:55 PM PT; D52).** The earlier "covered hook 0/5" result came from a sample missing every robe winner. Recoded across all our FB+IG reels, the covered reveal went **5/16 ≥50K**: HJ-02 2.7M, HJ-05 524K, MJIG-17 241K (IG), HJ-10 147K, HJ-14 97K. On the robe alone it's **5/11 vs 21/48** for other hooks (median 28.9K vs 15.7K), so it's on par with them.
- **The boundary is the cue, not the cover.** When the product's own signal shows at 0 s (fur and Grinch heart/face around a muffin tin or tray, the robe shaped as a "loaf", a drape made of the product's own lime fur/green), it went **5/10 ≥50K (median 63K)**. A fully hidden product (black/cream cloth, a blanket or pot over the ski mask) or a cue that reads as a different product (robe-green cloth over a fire pit) went **0/6 (median 3.0K)**. This is Loewenstein's partial-knowledge curve: the cover creates the gap and the visible cue gives the stakes.
- **Execute:** covered reveal = hold the product under or as the cover with its own colour, texture or face visible, or drape a store display in the product's own fabric/colour. Count 3-2-1 and reveal by 3.0 s (all 5 winners revealed at 1.2–3.0 s). Static eye-level MS with the product at 35–60% of the frame (tray/tin), or a static WS staff unveil (drape). Non-robe products are untested here. Use the product's own cue (fire pit: a glow or flame tip under the lifted cloth edge; ski mask: the yellow smiley peeking out) and put it in the innovation slot until there's data. Other gap hooks: always show a partial cue (the box, the glow, the person's reaction).

### 3. Pattern interrupt / orienting response
- **Source:** Sokolov 1963, the orienting reflex (classic). Itti & Baldi 2009, "Bayesian surprise attracts human attention", Vision Res doi:10.1016/j.visres.2008.09.007.
- **Observable:** in 0–2 s, a fall, flare-up, chaos or absurd image, with high motion in the first second (`measure.motion_0_1`).
- **Evidence:** chaos/fail openers 3/6 ≥50K and 5/6 ≥30K (ladder fall 70.4K, light-tangle chaos 152.9K, smoke room 67.7K, competitor flare 30.9K IG, smoke 40.3K IG; exception: dinner-table fire 2.6K). External cold-fail opener 6.8M.
- **Execute:** prompt "Realistic handheld iPhone footage filmed from across the room, very slight natural phone shake… [event] at 0.5 s"; no shock faces (Omar R18).

### 4. Endowment / mere touch: POV hands on the product
- **Source:** Kahneman, Knetsch & Thaler 1990, JPE doi:10.1086/261737. Peck & Shu 2009, "The effect of mere touch on perceived ownership", JCR doi:10.1086/598614 (touching, even imagined, raises perceived ownership).
- **Observable:** share of shots that are POV/OTS/high-angle with hands on the product.
- **Evidence:** same product (MerryFire, n=12): ≥30K reels have 14–43% high-angle hands shots vs ≤13% in every <10K reel. External hands-only demos: 23.7M, 8.5M, 6.9M.
- **Execute:** ≥2 body shots "over her shoulder" or "looking down at two hands (exactly two hands)". Each packed gen's 2nd shot uses a new angle.

### 5. Gifting psychology
- **Source:** Sherry 1983, "Gift giving in anthropological perspective", JCR doi:10.1086/208956. Flynn & Adams 2009, "Money can't buy love", JESP doi:10.1016/j.jesp.2008.11.003 (givers misjudge what recipients value; the gift signals the relationship).
- **Observable:** recipient or gift framing ("The perfect gift doesn't exi-", "Women are hard to gift..", "Send this to someone you'd absolutely wear this with").
- **Evidence:** gift_framing 5/9 ≥50K (median 90K). External 15/20 ≥1M (median 2.25M, the highest median of any flag).
- **Execute (Q4):** pair gift framing with a recipient reaction payoff. Caption emoji ✨/🎁 (🎁 in the caption, not the hook).

### 6. Peak–end rule
- **Source:** Kahneman, Fredrickson, Schreiber & Redelmeier 1993, "When more pain is preferred to less", Psychol Sci doi:10.1111/j.1467-9280.1993.tb00589.x.
- **Observable:** the last shot is the most rewarding image (static hero, product share ≥0.6), plus a payoff emoji.
- **Evidence:** present on winners AND flops, so it's table stakes and not a differentiator. Required by QA (FIX if missing).

### 7. High-arousal emotion and world fit
- **Source:** Berger & Milkman 2012, "What makes online content viral?", JMR doi:10.1509/jmr.10.0353 (awe, amusement and other high-arousal emotions drive sharing more than low-arousal ones).
- **Evidence:** cozy_payoff 4/7 ≥50K. External 16/20 ≥1M vs 69% base. BrickHood hype/amusement 61K (FB).
- **Execute:** arousal must match the product world (Omar: Boombastic for ski, Last Christmas for exciting Christmas, calm songs for GrinchMelt). The payoff is the lit reveal, a roaring flame, or squad hype.

## Tier 2: context-dependent (use with guards)
### 8. Reactance / forbidden framing ("Don't show this to…")
- **Source:** Brehm 1966, psychological reactance (book). Worchel 1992, censorship raises desirability, BASP doi:10.1207/s15324834basp1301_7.
- **Evidence:** ours 8/15 ≈ base. Wearables 7/10 vs decor 1/6. External 5/12 ≥1M vs 74% without.
- **Rule:** wearables only; decor goes in experiment slots (D19). Use 😳❄️, never 🥹 (0/2).

### 9. Humor: benign violation
- **Source:** McGraw & Warren 2010, Psychol Sci doi:10.1177/0956797610376073: humor needs a violation that's simultaneously benign.
- **Observable:** absurd-but-harmless images (a squad in identical goofy masks, a ladder fall into the tree with nobody hurt) + 😂/🤣.
- **Evidence:** humor 3/5 (FB). BrickHood 61.3K/61.1K. External 5/8. The model weight is negative outside the BrickHood world.
- **Rule:** exploit only where the product is goofy (BrickHood); keep injuries implied as harmless.

### 10. Social proof
- **Source:** Cialdini, *Influence* (book). Goldstein, Cialdini & Griskevicius 2008, JCR doi:10.1086/586910.
- **Evidence:** 2/3 ours ("the whole street is JEALOUS of your house.. 🤭🏠", 63.3K); external 3/5, no lift.
- **Rule:** explore. Show neighbours reacting in WS, not a claimed number.

### 11. Cute / "aww" response
- **Source:** Sherman, Haidt & Coan 2009, Emotion doi:10.1037/a0014904. Nittono et al. 2012, PLoS ONE doi:10.1371/journal.pone.0046362.
- **Evidence:** a golden retriever is in all 60K+ MerryFire prompts (Mac REPORT). External dog-launcher 3.5M, but 🐶 hook 1/3.
- **Rule:** a garnish in body shots (dog catches a marshmallow), never the hook.

### 12. Sensory appeal / ASMR for calm content
- **Source:** Barratt & Davis 2015, "ASMR: a flow-like mental state", PeerJ doi:10.7717/peerj.851.
- **Observable:** CU tactile/sound beats (chocolate melt, flame whoosh, fabric texture, plug click) plus named ambient SFX. Clip audio is boosted 1.3–3.4× on 8% of team clips for exactly these moments.
- **Rule:** for calm worlds (GrinchMelt, robe), 2+ sensory CUs, a calm song, no hype edits.

### 13. Mere exposure: familiar audio and house style
- **Source:** Zajonc 1968, JPSP doi:10.1037/h0025848.
- **Rule:** use proven songs at proven in-points (STYLE_GUIDE §5) and one consistent text style. Variants still get fresh native audio (shadowban rule D23).

### 14. Reciprocity and the keyword CTA
- **Source:** Regan 1971, JESP doi:10.1016/0022-1031(71)90025-4. Meta, "Fighting engagement bait on Facebook" (about.fb.com, 2017-12-18): comment/tag/vote baiting gets demoted.
- **Evidence:** external CTA ✨ 6/7, ❤️ 4/5 ≥1M; 👇 1/5 (ours 0/4).
- **Rule:** SAY "<KEYWORD>" (D5). The end card sits at 60% from the top.

## Tier 3: principles our data contradicts as a primary hook device
### 15. Identity / in-group callouts
- **Source:** Tajfel & Turner 1979, social identity theory (classic). Berger & Heath 2007, JCR, identity signalling*.
- **Evidence:** identity_callout **3/11 (27%) vs 30/52 (58%)** ours. External 11/19 vs 73%. The weakest flag in both sets.
- **Rule:** don't lead with "Calling ALL Christmas-aholics" / "Every Christmas mom". If used, embed the callout inside a gap or contrast hook ("Every Christmas mom NEEDS this 😳❄️", 62.8K).

### 16. Scarcity / urgency
- **Source:** Worchel, Lee & Adewole 1975, JPSP doi:10.1037/0022-3514.32.5.906.
- **Evidence:** ours 2/4, external 0/2. Not a lever for organic reach; keep "RUN" only inside the proven store format with the JK flip.

### 17. Presenter vs first-person (self-referencing)
- **Source:** Escalas 2007, JCR, self-referencing and persuasion*. Green & Brock 2000, narrative transportation, JPSP doi:10.1037/0022-3514.79.5.701*.
- **Evidence:** face share 0.25 in winners vs 0.39 in flops (p=0.30). MerryFire subset: winners ≤0.43 vs flops 0.44–0.88.
- **Rule:** ≤1 face-forward presenter shot. The viewer should be the one holding the product.

## How the parts fit in one 13 s reel (default recipe)
0–2 s orienting event or contrast "then" + gap text with 1 face emoji → 2–4 s partial cue / POV unbox (mere touch) → 4–10 s 2–3 packed hands-on and reaction shots with new angles, sensory CU if calm → 10–13 s static hero payoff (peak–end) + payoff emoji, then caption SAY "<KEYWORD>" ✨.
