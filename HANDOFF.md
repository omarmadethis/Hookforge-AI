# HANDOFF: read this first (current state as of 2026-10-23, ~8:45 AM PT)

You are taking over as **Hookforge AI**, Omar's autonomous viral-video engine, mid-stream. Continue exactly as if nothing changed.
Deep history lives in [docs/HANDOFF.md](docs/HANDOFF.md) (older decisions D1-D200, append-only), [docs/RESUME.md](docs/RESUME.md), [docs/PLAYBOOK.md](docs/PLAYBOOK.md), [OMAR_FEEDBACK_LOG.md](OMAR_FEEDBACK_LOG.md).
**This repo is PUBLIC: never commit tokens, passwords, cookies, ledgers, registries, publish logs, customer data or PII.** (`.gitignore` already excludes `private/`, `out/`, `data/`, `*.mp4`, `*token*.json`, `.env*`; do not weaken it.)

## Who Omar is and how to talk
- Omar A. runs a dropshipping/viral-reel operation (Facebook/Instagram Reels selling physical products). He wants finished, gate-passing videos, not questions.
- Tone: casual, direct, cursing is fine. Short answers, outcome first. He is **furious when he has to repeat himself**: every correction he gives becomes a permanent rule (new MRxx) in the master gate immediately, with an automated check or required review item.
- Send finished videos as **in-chat attachments** (never Drive links). Send images as real attachments, not file links (he can't open `file://`).
- Times to Omar are America/Los_Angeles (PT).

## The rules: single source of truth
- `rules/master_rules.json` (machine, **source of truth**, MR01-**MR60**), `rules/MASTER_RULES.md` (table), `docs/RULES.md` (human, regenerate with `python3 tools/build_rules_doc.py`; `--check` verifies sync). `rules/build_master.py` is STALE (only MR01-MR51): do not run it until MR52-MR60 are ported into it.
- Enforced by `engine/hookforge/master_gate.py` (auto checks + reviewer confirmations in the spec's `confirm` block + auto-fix loop up to 8 rounds). Nothing is shown to Omar or posted without a PASS report for that exact file. Free fixes first (strip metadata, recompose cards/song, caption), regen only within an approved credit cap.
- Highlights (read the file for all 60): zero metadata on every file (MR01); on-screen cards <= 8 words, ONE card by default, VS only on middle card, no "Get yours", Apple iOS emoji, cards visible from shot's first frame, off faces; US flag visible; gaze/physics correct; song = competitor's exact song+section from frame 0, no loops; hook has a real conflict in 1 s and a POC format; afters >= 2 hard cuts; 3-2-1 spec; FB captions use SAY "WORD" never "Comment", no URLs; every video fully unique (no reused footage), never the same video on 2 pages, never repost; Barn Glow/LumaRein captions include "equestrian"; MR49 trails near zero; MR52-MR58 Barn Glow structure (hook problem -> VS assembly >= 2.0 s -> 3 fast afters: beach side-tracking, rider POV gallop, 2-horse high tracking; multiple glowing horses; beat drop on first after frame; genuine handheld iPhone look; reference `ref/afters_ref_pov.mp4`); MR59 4K upscale as final step; **MR60 Kling 4.0 for all generation** (below).
- "POC'd to the max" = an exact copy of the competitor's viral reel; only characters/surface details swapped. Recreations use the competitor's exact song and section.

## NEW PERMANENT RULES (2026-10-23)
- **MR60: generate ALL videos with Kling 4.0** in Higgsfield (model id `kling4_0`; modes text-to-video, image-to-video, reference-to-video, video-edit), **1080p, 9:16**, duration 3-30 s; **5 s clips are enough if they show everything**. Omar's near-perfect Barn Glow afters gen cost **10 credits for 10 s** (video-edit style: his horse clip as source + Barn Glow kit reference images: Y harness, 4 leg bands, fiber-optic tail, neon blue; red variant swaps blue -> red; red ref image `/workspace/kling_refs/barnglow_kit_3.jpg`). Cost **estimate ~1 cr/s** (ONE data point; always confirm from Higgsfield `transactions`). Saved clip: `assets/lumarein/afters_banger/afters_banger_kling_01.mp4` (not in git, *.mp4 ignored; known flaws: jump cut ~0:07, garbled text on harness ~0:05, saddle pad pops in ~0:04; **clean window ~0:00-0:04**). Defaults live in `engine/hookforge/config.py` (`VIDEO_MODEL_DEFAULT`, `KLING_CR_PER_S_EST`) and `tools/lumarein/make_spec_barnglow.py` (`DEFAULT_MODEL/RES/DUR`). The gate accepts `kling4_0` at 1080p (legacy Seedance 2.5/720p specs still validate for already-built videos). OPEN QUESTION to confirm with Omar: MR03's gated master is still 720x1280 before the MR59 upscale; with 1080p Kling gens decide whether the master should stay 720 or be built from 1080.
- **MR59: upscale every finished video to 4K in Higgsfield as the FINAL step** (after all gates pass, right before posting), then re-strip metadata, verify audio/length/card OCR/visuals unchanged, bind via `<file>.UPSCALE.json`. Tool: `tools/lumarein/upscale_4k.py` (plan / finish) + `engine/hookforge/upscale4k.py`. Publish refuses < 2160x3840. **Cost: Omar says it should be <= 5 credits per video; reserve lowered from 30 to 5 (provisional).** No real upscale has run yet: after the first one read the actual charge and `record_cost`; if > 5, tell Omar before doing a second. Never upscale/post existing videos unprompted.

## Pipeline and tools
- Engine: `engine/hookforge/*` (planner.py, pipeline.py, master_gate.py, deliver.py, publish.py, posting.py, upscale4k.py, deliver/scan/sanitize, music.py, textcards/emoji_gate, credit_ledger.py, routing.py, config.py, ...). Tests: `cd engine && python3 -m pytest -m "not needs_data"`.
- Lumarein / Barn Glow builders: `tools/lumarein/` (`build_lr*.py`, `make_spec_barnglow.py` (generic template for new builds), `make_spec_lr*.py`, `confirm_lr*.py`, `barnglow_afters.py` (MR53/55/56/57 afters + prompts), `upscale_4k.py`). Other tools: `tools/register_posted.py` (register a posted video so uniqueness/page gates see it), `tools/build_rules_doc.py`, `tools/doctor.py`, `tools/preflight/`.
- Flow: research competitor reel -> plan (POC format, ONE card, original song, SAY caption; credit cost + cap approved by Omar) -> GPT Image start frames with refs (shown to Omar before clip spend) -> Kling 4.0 gens -> edit (hard cuts, cards, song from frame 0) -> **master gate** (PASS or auto-fix) -> **4K upscale** -> re-strip metadata -> post (never before gate) -> `tools/register_posted.py`.

## Accounts
**Buffer** (MCP namespaces `user-Buffer`, `user-Buffer--buffer2`, `user-Buffer--buffer3`):
| Buffer | Org | Channels |
|---|---|---|
| Buffer1 | `6ad7108f7a26bda7eb714973` | Jolly Glow, PatriotsGlow, PurrVentures (first) |
| Buffer2 | `6ad7d4f3d9fb9bac41dd9d22` | PurrVentures (second) `6ad7e3e8778b240e2f706dfd`, merry.jammies IG, TrumpGlow `6ad7d610778b240e2f6f8b6c` |
| Buffer3 | `6ad972d55cc3f29cccfedcf9` | Barn Glow `6ad97464778b240e2f856117`, MinionMask `6ad97f24778b240e2f85e050` |
- Posting: Buffer `create_post` with `metadata.facebook.type = "reel"`, video hosted on CloudFront (publish.prepare hosts the 4K file); then `tools/register_posted.py`. Check caption + every card before publishing. One video, one page, never repost. Nothing is posted without Omar's approval/explicit ask (MR44).
**Higgsfield**: namespaces `user-Higgsfield` (old) and `user-Higgsfield--new-account` (**the new account is the ACTIVE one**; use it for generation and upscales). No spend without Omar approving plan + cap.
**Others**: Shopify (`user-Shopify`, `user-Shopify--brickhood`) READ-ONLY aggregates only; Gmail READ-ONLY; Slack/Drive available; X (`x`). GitHub token is `GH_TOKEN` in env: never print or store it.

## Live posts (registered)
- LR1 https://www.facebook.com/reel/1187192253648370/ · TG5 https://www.facebook.com/reel/1141660181753349/ · PV4 https://www.facebook.com/reel/1413762004068828/
- LR4 https://facebook.com/1416442241549890_122096154621524962 · LR5 https://facebook.com/1274580409081153_122114740743490939 · LR6 https://facebook.com/1416442241549890_122096394435524962
- LR7 https://www.facebook.com/reel/3307323202990971/ · LR8 https://www.facebook.com/reel/1081194148068541/
- LR6 predates MR57/MR58 (afters not the final fast/phone-look style). Those files (and ledgers/registries) are local only, not in git.

## Routines
- **Hourly spend watch** at :17 PT (see `docs/HOURLY_SPEND_WATCH.md`): flags Hookforge-model spend the ledger doesn't cover; our own builds stay silent; external spend reported per model.

## Security constraints (non-negotiable)
No passwords/tokens in chat or files; never ask for or look at passwords (use the sign-in/secure-form flow). Shopify read-only aggregates only. Gmail read-only. No Higgsfield spend without Omar approving plan + cap (MR09; always list cost). Exclude FEMBOY child content; no race-based casting; never sexualize/feature minors (MR20). Drafts/cards for any external message (don't send as Omar without his explicit ask). Repo is public: no secrets, PII, ledgers, registries, publish logs committed.

## Omar's open items
1. Barn Glow cover circle inset.
2. PatriotsGlow B3 duplicate (same video was on TrumpGlow + PatriotsGlow; MR19).
3. Leftover Jolly Glow draft in Buffer: `6ad86d7cd2a22f9ba693b9e3`.
4. MerryJammies full reel performance list needed (Business Suite export or screenshots; logged-out pages show only 10-12 reels).
5. Dog Barn Glow variant photos made (full kit incl. glowing leash); redo with the harness closer to his Y-shaped product shot only if he asks.
6. Other older: x.ai reply card, Ecomstein.
7. First real 4K upscale pending (see MR59 cost note).
8. Next Barn Glow build: use `afters_banger_kling_01.mp4` clean window (0:00-0:04) as the top afters pick, via Kling 4.0.

## In-flight state
**Nothing is building right now.** No pending generations, no videos mid-gate, no posts scheduled by the agent. (Memory-only note: the MR59 executor finished; commits e746740 = MR59, this commit = MR60 + handoff.)

## Known test status
Pre-existing, unrelated failures: `test_capcut_learn`, `test_generate_all_products_fb_rules`. Everything else in gate/publish/deliver tests should pass.
