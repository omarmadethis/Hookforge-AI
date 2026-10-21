"""Run after every new post / insights export / CapCut draft batch:  python3 learning/update.py [--model] [--no-dashboard]
Schedule tomorrow:  python3 learning/update.py schedule brickhood_mask"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "engine"))
from hookforge.learn import update, schedule, arms, build_day
import json
if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "schedule": arms(); print(json.dumps(schedule(a[1], seed=1), indent=1))
    elif a and a[0] == "day": arms(); print(json.dumps(build_day(a[1]), indent=1, default=str, ensure_ascii=False)[:3000])
    else: print(json.dumps(update(model="--model" in a, dashboard="--no-dashboard" not in a), indent=1))
