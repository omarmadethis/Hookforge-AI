"""Build the scrubbed, shareable repo at /workspace/hookforge_public (NOT pushed). Excludes private data and media and
scrubs reel ids, URLs, emails and $ amounts from text files, then audits the result and fails loudly on any leak."""
import os, re, shutil, sys
SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")); DST = "/workspace/hookforge_public"
EXCL_DIRS = {"private", "out", "approvals", "vision", ".git", "__pycache__", "proxies", "cache", "frames", "strips", "_work", ".venv", "node_modules",
             "gen_failures", "inbox", "screenshots", "insights", "product_profiles"}   # prompts ledger, support inbox, IG/FB screenshots, insights exports, captions
EXCL_REL = re.compile(r"^(FIRST_LIVE_RUN\.md|analytics/data/public_audit\.json|voice/(comments|support_themes|browser_queue|targets|engagement_correlation|voice_rules)\.csv|voice/INSIGHTS\.md|voice/recommendations\.json|voice/voice_stats\.json|"
                      r"analytics/dashboard\.html|analytics/data/crosschecks\.csv|audience/ig_reel_audience\.csv|audience/data/.*|learning/(reroll_log|ai_tells_log|update_log)\.(csv|jsonl)|"
                      r"style/(covered_hooks|shots_by_reel|emoji_usage_rows|verification_textrows)\.csv|engine/backtest/data/(?!validation\.json).*)$")
EXCL_FILES = re.compile(r"\.(mp4|mov|m4a|mp3|wav|jpg|jpeg|png|tgz|zip|log)$|inventory\.csv$|music_evidence\.csv$|segments\.csv$|text_styles\.csv$", re.I)
SCRUB = [(re.compile(r"https?://\S+"), "<url>"), (re.compile(r"\b[\w.-]+\.(?:myshopify\.com|com)\b\S*"), "<domain>"),
         (re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "<email>"), (re.compile(r"\b\d{12,}\b"), "<id>"), (re.compile(r"\$\s?\d[\d,]*(\.\d+)?k?"), "<$>"),
         (re.compile(r"\b(fb|ig|tt)_[\w.]*_?\d{9,}\b"), "<reel>"), (re.compile(r"/Users/\w+"), "/Users/<user>")]
TEXT = re.compile(r"\.(py|md|json|csv|txt|toml|cfg|sh|html|yml|yaml)$")
def main():
    if os.path.exists(DST): shutil.rmtree(DST)
    n = 0
    for root, dirs, files in os.walk(SRC):
        dirs[:] = [d for d in dirs if d not in EXCL_DIRS]
        for f in files:
            if EXCL_FILES.search(f): continue
            s = os.path.join(root, f)
            if EXCL_REL.search(os.path.relpath(s, SRC)): continue
            d = os.path.join(DST, os.path.relpath(s, SRC)); os.makedirs(os.path.dirname(d), exist_ok=True)
            if TEXT.search(f):
                t = open(s, encoding="utf-8", errors="ignore").read()
                for rx, rep in SCRUB: t = rx.sub(rep, t)
                open(d, "w").write(t)
            else: shutil.copy2(s, d)
            n += 1
    leaks = []
    for root, _, files in os.walk(DST):
        for f in files:
            if TEXT.search(f):
                t = open(os.path.join(root, f), errors="ignore").read()
                for rx, _ in SCRUB:
                    if rx.search(t): leaks.append((f, rx.pattern[:30]))
    open(os.path.join(DST, "PUBLIC_PACKAGE.txt"), "w").write(f"Scrubbed copy of Hookforge, {n} files. Not pushed. Leaks found by audit: {len(leaks)}\n")
    print(n, "files;", len(leaks), "leaks", leaks[:10]); return 1 if leaks else 0
if __name__ == "__main__": sys.exit(main())
