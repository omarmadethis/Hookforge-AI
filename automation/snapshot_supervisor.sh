#!/usr/bin/env bash
# D102: keeps the read-only hourly results snapshot loop alive (restart on crash, 30 s backoff).
# Single instance: flock on learning/results/.supervisor.lock; the loop itself also holds .snapshot.lock.
# Start (idempotent, survives the shell/agent exiting):  setsid nohup automation/snapshot_supervisor.sh >/dev/null 2>&1 &
# After a box reboot: run `python3 -m hookforge.snapshot_scheduler --ensure` (from engine/) or the line above.
cd "$(dirname "$0")/.." || exit 1
exec 9>learning/results/.supervisor.lock
flock -n 9 || { echo "supervisor already running"; exit 0; }
echo $$ > learning/results/snapshot_supervisor.pid
while true; do
  (cd engine && python3 -m hookforge.snapshot_scheduler --loop) >> learning/results/snapshot_loop.out 2>&1
  echo "{\"ts\": \"$(date -Iseconds)\", \"event\": \"loop exited ($?), restarting in 30s\"}" >> learning/results/snapshot_loop.out
  sleep 30
done
