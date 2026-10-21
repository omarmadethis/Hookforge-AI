"""CLI: python3 learning/results_feed.py [--registry]
Drop Business Suite CSV exports in learning/results/inbox/ (or export META_TOKEN in the shell, never in a file).
Setup steps for Omar: docs/RESULTS_FEED_SETUP.md. Code: engine/hookforge/results_feed.py"""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "engine"))
from hookforge.results_feed import run
if __name__ == "__main__": print(json.dumps(run(rebuild_registry="--registry" in sys.argv), indent=1, default=str))
