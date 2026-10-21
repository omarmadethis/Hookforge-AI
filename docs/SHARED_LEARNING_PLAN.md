# Hookforge Shared Learning — design (2026-10-20, PT)
Status: DESIGN + local disabled scaffold. No accounts, purchases, or deploys. `engine/hookforge/telemetry.py` has `ENABLED = False`.

## 0. Principle
Every Hookforge install learns locally (as today: OMAR_FEEDBACK_LOG F-rules → gates, arms.csv bandits, rules_learned.csv, failure_memory).
A central server pools **anonymized** signals so everyone gets (a) fewer **genuine algorithm mistakes** and (b) better-calibrated **performance priors**.
**Style never goes global.** A user's own data always outranks the global prior.

## 1. What a client sends (default = anonymized features only)
Whitelist enforced in `telemetry.ALLOWED`; anything not listed is dropped before send.
- **gen**: format, hook_type, caption-card *pattern* (e.g. `POV:{x}` / `Vs.` middle card, never literal text), emoji ids, song_id + offset, n_shots, mean shot s, length, prompt *template id* (not filled prompt), model/res, fail_type (misgen/nsfw/ip/param), credits, QA gate pass/fail vector (G1–G22, SG1/2, frame_qa), niche/category (public_scrub CAT labels, not product names).
- **result** (+24 h/+72 h from results_feed): views (log10 + bucket), 3 s retention, avg watch %, skip rate, shares/saves per 1k, local post hour/weekday, Shopify **UTM aggregates as buckets** (orders/revenue ranges, from sales_attribution).
- **feedback**: see §3 — category, gate id, action, rule signature, scrubbed ≤200-char summary.
- **Never** (unless separate explicit opt-in): raw videos/frames, captions/hook text verbatim, page/store/product names, URLs, customer data, tokens, emails, Drive/Shopify IDs. Client ID = salted hash; reuses `analytics/public_scrub.py` deny-lists + regex PII scrub (emails, URLs, phones, token prefixes, @handles).
- Opt-in tiers: 0 off (default) · 1 mistakes+gen stats · 2 + results · 3 + raw media samples for model training (separate consent).

## 2. Central server
- **Ingest API** (FastAPI): `POST /v1/events` (batched JSONL, per-client API key, schema-validated, rate-limited), `GET /v1/release/latest`, `GET /v1/release/{ver}`, `DELETE /v1/client/{id}` (erasure).
- **DB** Postgres: `clients`, `events_gen`, `events_result`, `feedback`, `rule_signatures`, `rule_candidates`, `releases`, `rule_effects`.
- **Nightly job** (cron, 03:00 PT): dedupe → outlier/poison filter → refit virality model (same features as learning/update.py --model) → recompute per-niche bandit Beta priors (arms) → promote/demote mistake rules (§3) → refresh POC library (format×niche winners, pattern-level only) → emit signed, versioned **release** `rules-YYYY.MM.DD.N` (JSON: global_rules, gate candidates, priors, model weights, changelog).
- **Guardrails**
  - *Own data outranks global*: client blends prior as pseudo-counts capped at k=10 (global Beta(a,b) scaled so total ≤10); after ~20 own posts on an arm, the user's data dominates. Local F-rules always override global ones.
  - *Poisoning/outliers*: per-client contribution cap (≤5% of any statistic), min 5 distinct clients before any stat/rule ships, winsorize views at p1/p99, drop clients with improbable data (views without posts, identical bursts), new keys quarantined 14 days, all releases shadow-tested on held-out clients before rollout.
  - *Niche segmentation*: priors computed per niche (pet, wearable gift, decor lights…) with hierarchical shrinkage to global; region/market (US) tag.
  - Performance data shifts **priors only**; it never injects a format/style rule into another user's plan.

## 3. Learning from user interactions & feedback (major)
Generalizes OMAR_FEEDBACK_LOG (F-rules → gate) to every user.
**Captured events** (local, always — the local log is the user's own F-log):
corrections/critiques in chat · frame/video approve/reject (+reason) · fix requests · CapCut draft diffs (cut points, durations, text, music offset — via capcut_export round-trip) · caption edits (before/after pattern) · option choices (widget answers) · spend approvals/denials (amount bucket, reason).

**Pipeline**
1. *Normalize*: each event → `{category, gate_id, target (frame/video/caption/edit/spend), action, rule_sig}`. rule_sig = canonical form (e.g. `physics.subject_intersects_product`).
2. *Classify mistake vs preference* (`shared/server/classify.py`, v0 rules; v1 LLM with rubric run **locally** before upload):
   - **Mistake (globally eligible)** — objective errors: cat phasing through ball, paws through mesh, deformed/wrong product, off-reference cast, oversized flag vs ref, C2PA/Lavf traces, splice/loop in a take, cut-off hook dialogue, A/V desync, AI-look tells (grain, plastic skin), gate misses, crashes (PurrVenture NaN), cost overruns, missing references at generation.
   - **Preference (local only)** — pacing ("Free Bird lingers"), emoji choice (😔), cast gender, song, format/structure, CTA wording (SAY vs Comment), tone, length, caption style.
   - Threshold: mistake requires conf ≥0.8; mixed/ambiguous → **local**. Users can relabel; server never upgrades a local label.
3. *Privacy*: text summarized + scrubbed on-device (brand/product/page deny-list, PII regex), ≤200 chars; raw chat never leaves.
4. *Dedupe across users*: cluster by rule_sig (+ embedding similarity of summaries ≥0.85); count **distinct clients**, not events.
5. *Promote*: `promote.decide` — Wilson lower bound on (users reporting / users exposed to the situation):
   - ≥3 clients → *candidate* (shipped as warn-only gate);
   - ≥5 clients, Wilson LB ≥0.55, contradictions ≤20%, ≥2 niches → **global rule**; 1 niche → **niche rule**.
6. *Auto gate candidate*: if checkable (maps to an existing detector: frame_qa physics, ref_gate, deliver metadata scan, splice_detect, repeat_detect, speech_gates, ai_look, budget), generate a gate spec (detector, threshold, BLOCK/WARN). Ships WARN first; becomes BLOCK after it catches true positives ≥90% on ≥30 labeled cases.
7. *Effect tracking* (`rule_effects`): repeat-mistake rate for that rule_sig before vs after (per 100 gens), plus views/credits deltas.
8. *Rollback*: `promote.rollback` — auto-revert in next release if no reduction in repeats **and** median results drop >10% over ≥20 posts, or false-block rate >10%. Every rule versioned with superseded_by (merge-append, like the F-log).
9. Local prefs stay in the user's own rules file; optional "style packs" a user may choose to import are a future, explicit feature.

## 4. Client changes
- `engine/hookforge/telemetry.py` (scaffolded): whitelist, scrub, salted client id, local outbox, hard kill switch.
- `config/shared_learning.json`: `{enabled:false, opt_in_tier:0, endpoint:null}`; consent prompt on first run.
- `learning/feedback_capture.py`: hooks in approvals, gates, capcut diff, spend ledger → local F-log + scrubbed queue.
- `learning/update_puller.py`: daily fetch release, verify signature, diff-preview, apply into `rules_global.csv` / priors; local rules win; `--pin`/`--rollback` to a version.
- Gates loader reads global gate candidates (WARN only until promoted).

## 5. Hosting (prices checked 2026-10-20; confirm at checkout)
| Option | Monthly | Notes |
|---|---|---|
| **A. Single VPS: Hetzner CX22** (2 vCPU/4 GB/40 GB) + Postgres + FastAPI + cron, Docker/Coolify | **≈ €4.59 (~$5)** + ~$1 backups/snapshots | Cheapest; you own ops (patching, backups) |
| B. Render web $7 + Supabase Pro $25 | ~$32 | Managed DB, daily backups; Supabase Free pauses after 1 wk idle, so not prod |
| C. Fly.io smallest machine ~$2.19 + Neon Launch (usage: $0.106/CU-h, $0.35/GB-mo) | ~$5–15 | Cheap, usage-variable |
| D. Railway Hobby $5 + usage | ~$5–20 | Easy DX |
**Recommendation (<50 users): A** — one Hetzner VPS, ~$6/mo incl. backups + offsite backup to object storage (~$1). Data volume is tiny (KB per video). Scaling path: move Postgres to managed (Supabase Pro $25 / Neon) at ~200 users or when ops time hurts → split nightly job to a worker → Render/Fly autoscaled API at 1k+. Alt if Omar wants zero ops: B at ~$32/mo.

## 6. Privacy & terms
- **Consent notice** (first run): "Hookforge can share anonymized stats (formats, QA results, view/sales ranges, summarized mistake reports) to improve the engine for all users. No videos, captions, store, customer or account data are sent. Off by default; change anytime in settings." Separate checkbox for tier 3.
- **Retention**: raw events 13 months; aggregates/rules indefinitely (non-identifying); feedback summaries 6 months; logs 30 days.
- **Deletion**: `DELETE /v1/client/{id}` + client "forget me" → purge within 30 days; contributions removed from next release.
- Terms/privacy policy needed before external users (have a lawyer review; CCPA applies for US users). Data processed in US region.

## 7. Build plan
| Phase | Scope | Effort |
|---|---|---|
| P0 (done today, disabled) | telemetry.py, classify.py, promote.py, tests | — |
| P1 | Local feedback capture for all interaction types + classifier v1 + local F-log per user | 2–3 days |
| P2 | Server: FastAPI ingest, Postgres schema, auth keys, deletion, run locally in Docker | 2–3 days |
| P3 | Nightly job: dedupe, poisoning guards, niche priors, model refit, promotion, signed releases | 3–4 days |
| P4 | Client update puller + gate-candidate loader + effect tracking + rollback | 2 days |
| P5 | Consent UI, privacy policy, deploy to VPS (needs Omar approval), beta with 3–5 users | 2 days |
| P6 | Shadow-testing releases, dashboard of rule effects, scaling | ongoing |

## 8. Decisions for Omar
1. Host: Hetzner VPS (~$6/mo, I run ops) vs managed Render+Supabase (~$32/mo).
2. Default opt-in tier for new users (recommend 0/off with prompt; or tier 1 as condition of a free plan).
3. Promotion threshold (default ≥5 independent users, ≥2 niches).
4. Should Omar's own data seed the global priors (it's the largest dataset; anonymized)?
5. Legal entity/name on the privacy policy and terms.
6. Whether tier 3 (raw media for training) is ever offered.
