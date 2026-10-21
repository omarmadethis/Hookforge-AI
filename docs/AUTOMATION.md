# Hookforge automation design (Phase F) — 5 videos/day/product, 20% innovation

Status: DESIGN + dry-run code. Nothing generates, posts or spends credits until Omar approves each live switch.

## Daily loop (America/Los_Angeles)
1. **06:00 — learning/update.py** re-ingests new insights exports, CapCut drafts and Higgsfield job metadata (read-only). It then rebuilds the corpus, edits, posting_time (Holm, D36), music_library, product_profiles, arms.csv and the dashboard. `--model` re-validates the virality model weekly or after every 25 new posts.
2. **06:30 — schedule** (`learning/update.py schedule <product>`): each product gets 5 slots. 4 core slots come from Thompson sampling over arms.csv (product×format Beta posteriors; fit-REJECT arms are excluded). 1 experiment slot (20%) goes to an untested or WEAK, world-compatible format, new hook or unproven song. Each slot carries its posting window: core uses the page's exploit windows, experiment uses the explore windows (learning/posting_windows.json).
2b. **06:40 — day package** (`learning/update.py day <product>`): schedule → one plan per slot → QA + D42 pre-flight lint + credit estimate → pages assigned round-robin over the active pages (pages.py) with per-page window rotation → originality check across the day (same page or same format, similarity ≤0.45; song/caption/hook/setting rotated, format repeats become variants; max 2 per format). Output: out/daily/<date>/<product>/{DAY.md, day.json}. Hook options (D53) are arms too: robe covered_reveal / covered_drape in core, covered_glow only in the 20% slot.
3. **07:00 — plan + gate** (`hookforge.pipeline`) runs once per slot: brief → planner (product world, fit, music, caption) → QA (plan checks + logic check) → backtest gate (D35). BLOCK stops the slot. FIX auto-applies timing fixes and re-plans once.
4. **07:30 — generate** (LIVE SWITCH 1, needs Omar's approval): every job goes through `runner.submit(plan, live, approved)`, which runs the D42 failure-memory linter first (promoted rules = FIX, stop) and refuses unless live AND approved. Each attempt is logged with `gen_failures.log_attempt` (outcome ok/misgen/nsfw/ip/param/preset + cause; fixes link failed→working). Stills (GPT Image 2) and then Seedance 2.5 gens. The per-video budget is checked before submit (175, variants 100). A daily cap stops everything if exceeded.
5. **QA per gen**: a vision judge plus human spot-check fill the D33 judgement. `qa.reroll_decision` re-rolls only on a certain absurd failure (max 1/shot) and logs to learning/reroll_log.csv with cost.
6. **Edit**: autoedit.final_cmd (2160×3840 export, D44 clean flags) → autoedit.clean_export (fresh re-encode, asserts no C2PA/IPTC/trainedAlgorithmicMedia remains) → qa.final_checks (BLOCK on any provenance, aspect, loudness, safe zones) + capcut_export draft (music at the proven offset, text preset from style/). edit_checks verifies cuts, length and resolution.
7. **Post** (LIVE SWITCH 2, needs Omar's approval): Omar or a scheduler posts in the slot's window. Captions come from the proven caption list. CTA is SAY, never COMMENT.
8. **+24 h / +72 h**: insights are pulled and fed back into step 1. Experiments are evaluated in learning/experiments.csv. Arms update automatically.

## Guards
- **Credit:** per-video budget, daily cap, and the re-roll reserve is printed. No generation without the live switch.
- **World:** fit REJECT is never scheduled. The logic check must pass. The reviewer question is answered on the render before posting.
- **Music/caption:** core slots use only proven items (D38). Unproven items are allowed only in the experiment slot.
- **Privacy:** private/ stays local. tools/package_public.py builds the scrubbed repo (not pushed).
- **Kill rules:** each format's kill_rule (format_defaults) is evaluated by update.py. An arm with 0 hits in ≥5 fresh posts is down-weighted, not deleted.

## Status (2026-10-18 ~10:35 PM PT)
Working end to end, dry: brief → plan → QA/logic/style/psych → lint → backtest gate → animatic (render_text cards) → CapCut draft → clean export + provenance assert; learning/update.py (corpus, drafts, posting_time, failure memory, music, profiles, arms, experiments, dashboard); day packages. Tests: engine/tests/test_core_path.py, engine/tests/test_c2pa_strip.py.

## Open before going live
- **Live generation:** built, DISABLED (D57). The first run needs Omar's approval: FIRST_LIVE_RUN.md, 174 credits, new-account.
- **Video-reference (recreate) billing:** still unconfirmed.
- **D33 judge:** vision_judge (D56), automatic. It sees the generated clip for each video step.
- **Posting backend (posting.py):** disabled until Omar picks a tool.
- **Reels source:** hookforge.db is the default (D54). The review re-runs on each learning/update.py, and the loop falls back to the corpus if the DB file changes and the review fails.

## Session start: ensure the snapshot supervisor (D159)
Run this at the start of every session (idempotent, safe to repeat, read-only loop):
```
/workspace/hookforge/automation/ensure.sh            # starts automation/snapshot_supervisor.sh only if it is not running
/workspace/hookforge/automation/ensure.sh --status   # report only, never starts anything
```
- **Running:** the supervisor holds `learning/results/.supervisor.lock`, so a second start is a no-op. ensure.sh tests the lock with `flock -n` instead of trusting the pid file.
- **Not running** (e.g. after a box reboot; there is no cron or systemd): it runs `setsid nohup automation/snapshot_supervisor.sh` and waits up to 5 s for the lock.
- **Output:** one line, `[time PT] supervisor running|STARTED pid=… loop=… last_tick=… (N min ago)`.
- **Exit codes:**
  - 0: healthy, or just started.
  - 1: unhealthy. Either the loop process is missing (normal for up to 30 s during a restart backoff) or the last tick in `learning/results/snapshot_log.jsonl` is more than 75 min old. `--status` also returns 1 when the supervisor is down.
  - 2: failed to start; see `learning/results/snapshot_loop.out`.
- The supervisor itself restarts the loop after 30 s if it crashes. The loop ticks hourly at :00:05 and is read-only (results ingest + traction check; it only queues caption swaps, it never edits or posts).
