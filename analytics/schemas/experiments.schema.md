# learning/experiments.csv schema (read by analytics/build_dashboard.py)

One row per **arm** (a posted or planned reel). Rows sharing `experiment_id` are compared; the arm
named `control` is the baseline. Leave outcome fields empty until the numbers exist (never estimate).

| column | type | meaning |
|---|---|---|
| experiment_id | str | e.g. `EXP-2026-10-19-01`; `EXAMPLE-*` rows are ignored by stats |
| is_example | 0/1 | 1 = schema demo row, never counted |
| created_pt | `YYYY-MM-DD HH:MM` (PT) | when the experiment was planned |
| product | str | product name |
| page_code | str | HJ, MG, BH, ... (same codes as the corpus) |
| arm | `control` / `variant` / `variant_b`... | |
| is_innovation | 0/1 | 1 = counts toward the ~20% innovation budget (config.INNOVATION_SHARE) |
| format | F01..F99 | engine/hookforge/taxonomy.py |
| hook_family | str | |
| variable_changed | str | the ONE thing changed vs control |
| hypothesis | str | what we expect and why |
| proof_keys | `;`-separated corpus keys | the viral reels this arm is derived from (proof of concept) |
| reel_key | str | corpus key once posted |
| posted_pt | `YYYY-MM-DD HH:MM` (PT) | |
| status | planned / live / done / killed | |
| views_24h, views_7d | int | from Insights |
| three_sec_rate | 0-1 | 3-s views / views |
| avg_watch_s | float | |
| shares, profile_visits | int | |
| orders_per_1k | float | from Shopify allocation, if computed |
| decision | keep / kill / iterate | |
| notes | str | |
