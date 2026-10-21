# Hourly unlogged-spend watch (D129) — read-only, messages nobody
The box cannot call MCP tools from cron, so an agent runs this every hour:
1. Higgsfield `transactions` (read-only), namespace `user-Higgsfield--new-account`, size 100 (write_to_file).
2. `PYTHONPATH=engine python3 -c "from hookforge import spend_watch as W; print(W.check(open('<file>').read()))"`
3. Surface `learning/alerts/unledgered_spend.json` only when `"flag": true` (new unlogged spend > 20 cr since the last check).
Baseline set 2026-10-20 4:12 PM PT (298.15 cr already unlogged today, recorded but not re-flagged). History: learning/alerts/unledgered_spend.jsonl.

## D161 Attribution (2026-10-20)
Each spend is tagged by `hookforge/spend_attrib.py` by model type, against the ledger's known Hookforge job rows:
- `hookforge`: exact match on amount ±15 min, or a pool match on the same Hookforge model ±45 min while the row's logged credits are not used up. The record includes run_id and job_ids.
- `hookforge_unaccounted`: GPT Image 2.0 or Seedance 2.5 spend with no ledger row that covers it. **This is the only tag that raises the flag** (threshold still 20 cr).
- `external`: models Hookforge never submits (GPT Image 2.5 Flare, Seed Audio, Sound Effects, Text to Music ...). Shown under `new_external_credits`/`new_by_model` and never flagged.
`unledgered_spend.json` now has `new_by_model` and `window_by_model` (per display name: hookforge / unaccounted / external credits). Edit `HOOKFORGE_MODELS` when the pipeline starts using a new model.
Heuristic limit: if another user runs Seedance 2.5 or GPT Image 2.0 it lands in unaccounted and gets flagged. The watch fails safe.
