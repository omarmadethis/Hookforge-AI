# Hookforge setup

From zero to a published, gate-passed reel. Budget about an hour for setup, then ~30-60 min per video.

## 1. Prerequisites

| Need | Why | Install |
|---|---|---|
| Python 3.10+ (3.13 tested) | engine, gate, tests | python.org / your package manager |
| ffmpeg + ffprobe with libx264, libass (libx265 nice to have) | cutting, cards, song lay, measurements | `apt install ffmpeg` / `brew install ffmpeg` |
| exiftool | metadata strip + verify (MR01) | `apt install libimage-exiftool-perl` / `brew install exiftool` |
| tesseract-ocr | card OCR check (MR39) | `apt install tesseract-ocr` / `brew install tesseract` |
| Python packages | see `requirements.txt` | `pip install -r requirements.txt` (torch/open_clip are optional and large; skip them if you like) |
| Apple iOS emoji PNGs | cards must use Apple emoji (MR35) | shipped in `assets/emoji_apple/160/` (see 1.1) |
| Montserrat font | card text | vendored in `assets/fonts/` (OFL) |

Clone and make the repo reachable at `/workspace/hookforge` (several build scripts and tests use that path):

```bash
git clone https://github.com/<owner>/Hookforge-AI.git ~/Hookforge-AI
sudo mkdir -p /workspace && sudo ln -s ~/Hookforge-AI /workspace/hookforge
cd /workspace/hookforge && pip install -r requirements.txt
python3 tools/doctor.py
```

`tools/doctor.py` checks everything below and ends with `READY` or tells you exactly what to fix. It never prints secret values.

### 1.1 Apple emoji and the card font
Cards are rendered with Apple's iOS emoji art, never Noto or system emoji; the gate pixel-checks this (MR35).
The repo ships the 160 px Apple PNGs already used (`assets/emoji_apple/160/`, file name = lowercase codepoint,
e.g. `1f1fa.png` + `1f1f8.png` for 🇺🇸, `2744-fe0f.png` for ❄️). A new emoji is fetched automatically the first
time a card uses it, from the `iamcal/emoji-data` repo's `img-apple-160/` folder, so the box needs internet then.
Commit newly fetched PNGs so builds stay offline-safe.

The card font is Montserrat (SIL Open Font License), vendored at `assets/fonts/`. Override it with
`HOOKFORGE_CARD_FONT=/path/to/font.ttf` if you must, but the calibrated card style assumes Montserrat.

## 2. Accounts

| Account | Needed for | Notes |
|---|---|---|
| **Higgsfield** | start frames (GPT Image) and clips (Seedance 2.5) | Pay-as-you-go credits. At the time of writing a 720p 4 s Seedance clip was ~28 credits, a GPT Image frame 1-6.5. Turn off auto top-up if you want a hard spend ceiling. |
| **Buffer** | scheduling/publishing to FB pages (and IG) | Free plan = 3 channels and 10 scheduled posts per account; use several Buffer accounts for more pages. |
| **Facebook pages** (+ optional Instagram) | where the reels go | One niche page per product family. New pages work: >98% of reel views come from non-followers. |
| **An AI agent with connectors** (e.g. Grok Bot) | runs Higgsfield + Buffer through their OAuth connectors | Hookforge's code plans, edits, gates and prepares payloads; the generation and posting calls are made by the agent through the Higgsfield and Buffer connectors, so no API keys live in this repo. |
| **GitHub** | your fork + CI | CI runs the tests on every push (`.github/workflows`). |
| Optional: Shazam / an audio-ID tool, yt-dlp | identifying and fetching a reference reel's song and section | `pip install yt-dlp`; song files are gitignored (copyright). |
| Optional: Meta Graph token | reading your own page Insights for the results feed and caption swap | read-only scopes, in `.env` only |

## 3. Environment

```bash
cp .env.example .env     # .env is gitignored
```

Fill in only what you use (`META_TOKEN`, `GH_TOKEN` are optional). Never put tokens in code, docs, config JSON or chat.
Load it with `set -a; . ./.env; set +a` before running scripts that need it.

## 4. Configure your products, pages and channels

1. **Products**: edit `config/products.json`. Add your product key and set `"active": true`; set the retired ones
   to `false` (inactive products stay as reference data only). The gate's MR21 only allows active products.
2. **Buffer routing**: `cp config/buffer_routing.example.json config/buffer_routing.json`, then fill in each Buffer
   account's org ID and each page's channel ID (ask your agent to list your Buffer organizations and channels, or
   read them from the Buffer URL), and map each product to the pages that may carry it. IDs only, never tokens.
3. **Product URLs**: `cp config/product_urls.example.json config/product_urls.json`. Used only for the 40K-view
   caption swap; URLs never go on screen or in the first caption.
4. **Page plans** (optional): `config/pages.example.json` shows per-page audience, quotas and posting windows.
5. **References**: put your product photos and cast refs under `refs/<product>/` (frames always attach refs).

Both real config files are gitignored. `engine/hookforge/userconfig.py` loads the real file if present and falls back
to the `.example.json`, so a fresh clone still runs the tests.

## 5. Make a video (the build)

Follow `docs/PLAYBOOK.md`; the short version:

1. **Pick a proven original** for your product type (`formats/INDEX.md`, or a competitor reel with big views).
   Measure it: `ffmpeg -i ref.mp4 -vf "select='gt(scene,0.3)',showinfo" -f null -` for cuts, OCR the cards,
   identify the song and the second its section starts.
2. **Write the plan** (see `tools/hf3/plan.json` for a real one): hook with a conflict by 1 s, shots, ONE card
   (two only for problem/solution or then-vs-now, or a closing "get it from the caption below 👇"), song + `in_s`,
   caption with `SAY "WORD"`, total credit cost. Get the owner's OK on the plan and cap.
3. **Start frames**: GPT Image with refs attached, prompt ends with the realism suffix (`hookforge.config.still_prompt`).
   Show them before spending on clips.
4. **Clips**: Seedance 2.5 image-to-video at 720p, 4 s each. Hook = its own generation; body = 2 shots per generation
   with `HARD CUT at 2s, no transition` in the prompt. Never end frames.
5. **Edit**: `tools/hf3/build.py` is a complete worked example (cut list -> concat -> Apple-emoji cards -> song from
   frame 0 at the original section -> 720x1280 -> metadata strip). Copy it into `tools/<your_run>/` and adapt.

## 6. Run the master gate

Write a sidecar spec next to the final (`<final>.mp4.gate.json`; template: `docs/examples/gate_spec.example.json`), then:

```bash
cd /workspace/hookforge/engine
PYTHONPATH=. python3 -m hookforge.master_gate /path/to/final.mp4 deliver   # exit 0 = PASS, 2 = not yet
```

The gate runs every automatic rule, applies free fixes (strip metadata, re-render cards, re-lay song, rewrite caption)
and loops up to 8 rounds. Judgment rules (realism, gaze/physics, logical setting...) need a reviewer entry in the
spec's `confirm` block. On PASS it writes `<file>.PASS.json` + `.PASS.md` bound to the file's sha256; `deliver.stage`
and `publish.prepare` refuse anything without it. If it ends at `NEEDS_REGEN_WITHIN_CAP`, the report lists exactly
which clips to regenerate and what it costs.

Engine self-test: `cd engine && PYTHONPATH=. python3 -m pytest -q -m "not needs_data"`.

## 7. Publish

1. Host the PASSed file somewhere Buffer can fetch (a public URL; e.g. the generation platform's storage).
2. Re-run the gate at the publish stage with the exact caption: `python3 -m hookforge.master_gate final.mp4 publish`
   (checks SAY wording, caption == approved caption, no repeated caption lines on that page, no repost, one page only).
3. `hookforge.publish.prepare(video, caption, channel_id, service="facebook", page=..., product=..., video_url=...)`
   builds and validates the Buffer payload for a channel from your routing config.
4. Have your agent create the Buffer post (now or scheduled; 6 PM-4 AM local tends to win) with that payload, then
   record the live post so the uniqueness checks know about it (`tools/register_posted.py` reads Buffer post dumps).
5. At 40K views (or 10K+ inside one hour) swap the caption to "Get it here 👉 <product URL>" (`hookforge.fb_caption`).

## 8. Keep it yours and safe

- Run `python3 tools/doctor.py` before every push; it fails if `.env`, real config or a spend ledger is tracked.
- Changing a rule: edit `rules/build_master.py`, run it, then `python3 tools/build_rules_doc.py` (a test fails if
  `docs/RULES.md` is out of date).
- Spend ledger, publish logs and the footage registry are local-only (gitignored); back them up yourself.
