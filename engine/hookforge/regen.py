"""D154 one command regenerates everything Omar would approve (no credits, nothing sent):
    cd engine && PYTHONPATH=. python3 -m hookforge.regen
Order: content calendar -> daily concepts (approval queue) -> weekly batch + lean plan (queue item) -> render queue ->
Buffer payload preflight -> approval digest. Prints one line per artifact (times PT)."""
import datetime, sys, traceback
from zoneinfo import ZoneInfo

def main(start=None):
    from . import content_calendar, concept_lab, render_queue, buffer_preflight, approval_digest
    PT = ZoneInfo("America/Los_Angeles"); out = []
    def step(name, fn, fmt):
        try: r = fn(); out.append((name, True, fmt(r)))
        except Exception as e: out.append((name, False, f"{type(e).__name__}: {e}")); traceback.print_exc(file=sys.stderr)
        return out[-1]
    cal = {}
    step("calendar", lambda: cal.setdefault("c", content_calendar.week(start, write=True)), lambda c: f"{len(c['slots'])} slots from {c['start']}")
    step("daily concepts", concept_lab.daily, lambda d: f"{len(d['items'])} concepts, recommended {d['recommended_options']} ({d['recommended_credits']}/{d['innovation_budget']} cr)")
    step("weekly batch", lambda: concept_lab.weekly(start), lambda w: f"{w['new_videos']} videos / {w['slots']} slots, standard {w['total_credits']} cr")
    step("render queue", lambda: render_queue.build(cal.get("c") or content_calendar.week(start, write=False), write=True),
         lambda r: f"{len(r['slots'])} slots {r['summary']}")
    step("buffer preflight", buffer_preflight.run, lambda b: f"{b['passed']}/{b['slots']} payloads pass Buffer create_post schema {b['per_product']}")
    step("approval digest", approval_digest.build, lambda d: f"{d if isinstance(d, str) else (d.get('path') or d.get('out') or 'built')}")
    def _resume():
        import runpy, os
        runpy.run_path(os.path.join(os.path.dirname(__file__), "..", "scripts", "build_resume.py"), run_name="__main__"); return "docs/RESUME.md"
    step("resume doc", _resume, lambda p: p)
    now = datetime.datetime.now(PT).strftime("%-I:%M %p PT")
    for n, ok, msg in out: print(f"[{now}] {'OK ' if ok else 'ERR'} {n}: {msg}")
    return all(ok for _, ok, _ in out)

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
