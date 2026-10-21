#!/usr/bin/env bash
# D159: idempotent session-start check for the read-only hourly snapshot supervisor. Safe to run any number of times.
#   automation/ensure.sh            -> start the supervisor only if it is not running, then print one status line
#   automation/ensure.sh --status   -> report only, never start anything
# Exit 0 = healthy (or just started), 1 = running but unhealthy (loop missing / no tick in > 75 min), 2 = could not start.
set -u
cd "$(dirname "$0")/.." || exit 2
R=learning/results; LOCK=$R/.supervisor.lock; mkdir -p "$R"
now(){ date '+%-I:%M %p %Z'; }
sup_running(){ [ -e "$LOCK" ] || return 1; ( exec 8>>"$LOCK"; ! flock -n 8 ); }   # lock held = supervisor alive
action="none"
if ! sup_running; then
  if [ "${1:-}" = "--status" ]; then echo "[$(now)] supervisor NOT running (status only, nothing started)"; exit 1; fi
  setsid nohup automation/snapshot_supervisor.sh >/dev/null 2>&1 < /dev/null &
  for _ in 1 2 3 4 5 6 7 8 9 10; do sleep 0.5; sup_running && break; done
  sup_running || { echo "[$(now)] supervisor FAILED to start - see $R/snapshot_loop.out"; exit 2; }
  action="started"
fi
spid=$(cat $R/snapshot_supervisor.pid 2>/dev/null || echo "?")
lpid=$(pgrep -f "hookforge.snapshot_scheduler --loop" | head -1)
last=$(tail -1 $R/snapshot_log.jsonl 2>/dev/null | python3 -c 'import sys,json
try: print(json.loads(sys.stdin.read())["ts_pt"])
except Exception: print("")')
age=""
if [ -n "$last" ]; then age=$(( ( $(date +%s) - $(date -d "$last" +%s) ) / 60 )); fi
health=0; note=""
[ -z "$lpid" ] && { [ "$action" = "started" ] || { note="loop process missing (supervisor may be in its 30 s backoff)"; health=1; }; }
[ -n "$age" ] && [ "$age" -gt 75 ] && [ "$action" != "started" ] && { note="${note:+$note; }last tick ${age} min ago (> 75)"; health=1; }
echo "[$(now)] supervisor $([ "$action" = started ] && echo STARTED || echo running) pid=$spid loop=${lpid:-starting} last_tick=${last:-none}${age:+ (${age} min ago)}${note:+ WARN: $note}"
exit $health
