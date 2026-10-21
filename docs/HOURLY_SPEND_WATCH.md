# Hourly unlogged-spend watch (D129) — read-only, messages nobody
The box cannot call MCP tools from cron, so an agent runs this every hour:
1. Higgsfield `transactions` (read-only), namespace `user-Higgsfield--new-account`, size 100 (write_to_file).
2. `PYTHONPATH=engine python3 -c "from hookforge import spend_watch as W; print(W.check(open('<file>').read()))"`
3. Surface `learning/alerts/unledgered_spend.json` only when `"flag": true` (new unlogged spend > 20 cr since the last check).
Baseline set 2026-10-20 4:12 PM PT (298.15 cr already unlogged today, recorded but not re-flagged). History: learning/alerts/unledgered_spend.jsonl.
