"""Shared-learning client (DISABLED by default). See docs/SHARED_LEARNING_PLAN.md.
Builds anonymized event payloads only; never sends unless config shared_learning.enabled AND user opt-in AND endpoint set.
No network code runs in this scaffold: send() writes to a local outbox for inspection."""
import hashlib, json, os, re, time

ENABLED = False  # hard kill switch; flipping requires Omar's decision (docs/SHARED_LEARNING_PLAN.md §10)
OUTBOX = os.path.join(os.path.dirname(__file__), "..", "..", "shared", "outbox")
ALLOWED = {
 "gen": {"format", "hook_type", "card_pattern", "emoji", "song_id", "song_offset_s", "n_shots", "mean_shot_s", "len_s",
         "prompt_template_id", "model", "res", "fail_type", "credits", "qa_gate_results", "niche"},
 "result": {"format", "hook_type", "niche", "views_bucket", "views_log10", "retention_3s", "avg_watch_pct", "skip_rate",
            "shares_per_1k", "saves_per_1k", "post_hour_local", "weekday", "utm_orders_bucket", "utm_rev_bucket"},
 "feedback": {"category", "gate_id", "target", "action", "rule_sig", "summary", "niche", "severity", "is_repeat"},
}
PII = [re.compile(p, re.I) for p in [r"[\w.+-]+@[\w-]+\.[\w.]+", r"https?://\S+", r"\+?\d[\d\s().-]{7,}\d",
       r"\b(EA|sk|pk|shpat|ghp|xox[bp])[-_A-Za-z0-9]{10,}", r"@\w{3,}"]]

def client_id(seed: str) -> str:
    return hashlib.sha256(("hf-v1:" + seed).encode()).hexdigest()[:16]

def scrub_text(s: str, deny=()) -> str:
    s = str(s)[:200]
    for p in PII: s = p.sub("<x>", s)
    for d in deny:
        if d: s = re.sub(re.escape(d), "<brand>", s, flags=re.I)
    return s

def build_event(kind: str, fields: dict, deny=()) -> dict:
    if kind not in ALLOWED: raise ValueError(kind)
    out = {k: v for k, v in fields.items() if k in ALLOWED[kind]}
    if "summary" in out: out["summary"] = scrub_text(out["summary"], deny)
    return {"v": 1, "kind": kind, "ts_day": time.strftime("%Y-%m-%d"), "data": out}

def send(events, cfg: dict) -> str:
    if not (ENABLED and cfg.get("enabled") and cfg.get("opt_in") and cfg.get("endpoint")):
        return "disabled"
    os.makedirs(OUTBOX, exist_ok=True)
    with open(os.path.join(OUTBOX, f"{int(time.time())}.jsonl"), "a") as f:
        for e in events: f.write(json.dumps(e) + "\n")
    return "queued_local"
