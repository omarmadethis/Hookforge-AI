# Hookforge

> **Taking over from another assistant? Read [HANDOFF.md](HANDOFF.md) first.** Current state, rules pointer (MR01-MR60), accounts, open items.

Hookforge is an engine for making organic Facebook and Instagram Reels that sell a physical product. It copies
**proven** viral reels (their hook, pacing, card wording and exact song section), regenerates them with AI video
for your product, checks every file against a 60-rule quality gate (`rules/master_rules.json`), and publishes one unique video per page
through Buffer.

It was built and battle-tested on real product pages (Christmas lights, a projector, a cat carrier, LED horse
tack). Every rule in it exists because a video failed or the owner had to say the same thing twice.

## How it works, end to end

```
 research ──> plan ──> start frames ──> generation ──> edit ──> MASTER GATE ──> publish ──> learn
 (proven      (POC    (GPT Image,      (Kling 4.0      (cuts,    (51 rules,      (Buffer,    (views feed
  originals)   format)  refs attached)  1080p, 5 s)    cards,    auto-fix loop)  1 page per  back into
                                                        song)                     video)      the rules)
```

1. **Research.** Find a competitor or own reel that already went viral for this kind of product. Measure it:
   cuts (ffmpeg scene detect), on-screen text (OCR), song and the exact second it starts (audio fingerprint).
   Proven hook formats live in `formats/` (ranked in `formats/INDEX.md`); the evidence is in `docs/PLAYBOOK.md`.
2. **Plan.** Pick a proven ("POC") format and write a plan: hook with a real conflict in the first second,
   shot list, ONE on-screen card (<= 8 words, Apple emoji), the original song + section, caption with SAY "WORD".
   The plan states the credit cost and needs the owner's approval and cap before any spend.
3. **Start frames.** One still per generation with GPT Image, product and cast reference photos always attached.
   Frames are shown to the owner before clips are generated.
4. **Generation.** Since MR60 (2026-10-23): Kling 4.0 (`kling4_0`) on Higgsfield, 1080p 9:16, 3-30 s (5 s is enough); older builds used Seedance 2.5 / 720p. The hook is its own
   generation; body shots are packed 2 per 4 s generation with a hard cut at ~2 s. Every prompt ends with the
   iPhone 12 realism suffix.
5. **Edit.** Hard cuts only, payoff of >= 2 cuts, song from frame 0 with no loops, card visible from its shot's
   first frame and off faces, 720x1280, then strip ALL metadata.
6. **Master gate.** `engine/hookforge/master_gate.py` runs every automatic check, auto-fixes what is free
   (metadata, card text/timing, song re-lay, caption) and loops until PASS. Footage problems are only
   regenerated inside the approved cap. A PASS report is bound to the file's sha256; delivery and publishing
   refuse a file without one.
7. **Publish.** Buffer, one video on ONE page only, never a repost. Caption checked against the approved text.
8. **Learn.** Views and retention come back; at 40K views the caption swaps to the product link; winners and
   flops update `learning/` and the rules.

## Quickstart

```bash
git clone https://github.com/<owner>/Hookforge-AI.git && cd Hookforge-AI
sudo mkdir -p /workspace && sudo ln -s "$PWD" /workspace/hookforge   # several build scripts use this path
pip install -r requirements.txt                                       # + ffmpeg, exiftool, tesseract (see SETUP)
cp .env.example .env
cp config/buffer_routing.example.json config/buffer_routing.json      # your Buffer org + channel IDs
cp config/product_urls.example.json   config/product_urls.json        # your product page URLs
python3 tools/doctor.py                                               # must end with READY
cd engine && PYTHONPATH=. python3 -m pytest -q -m "not needs_data"    # engine self-test
```

Then run a video through the gate:

```bash
cd engine && PYTHONPATH=. python3 -m hookforge.master_gate /path/to/final.mp4 deliver
```

Full walkthrough: **[docs/SETUP.md](docs/SETUP.md)**.

## Docs

| Doc | What's in it |
|---|---|
| [docs/SETUP.md](docs/SETUP.md) | Prerequisites, accounts, config, build, gate, publish, step by step |
| [docs/RULES.md](docs/RULES.md) | Every rule the gate enforces, in plain English (generated from `rules/master_rules.json`) |
| [docs/PLAYBOOK.md](docs/PLAYBOOK.md) | What makes a product reel go viral: hook formats, edit spec, captions, generation craft, psychology |
| [docs/LESSONS.md](docs/LESSONS.md) | What worked, what failed, and why |
| `formats/INDEX.md` | The proven hook formats, ranked by evidence, each with timing, prompts and failure modes |
| `rules/MASTER_RULES.md` | The machine rule table with sources and dates |

## Repo map

| Path | What |
|---|---|
| `engine/hookforge/` | The engine: planner, prompts, textcards + Apple emoji, music/song fingerprint, master gate, deliver, publish, routing |
| `engine/tests/` | Tests (`-m "not needs_data"` runs without private media) |
| `rules/` | `build_master.py` -> `master_rules.json` + `MASTER_RULES.md` |
| `formats/` | Proven hook-format recipes (`.md` + `.json` rendered from one source) |
| `config/` | `*.example.json` templates; your real `buffer_routing.json` / `product_urls.json` are gitignored |
| `assets/emoji_apple/160/` | Apple iOS emoji PNGs used on cards |
| `learning/` | Learned rules, failure memory, caption library, research notes |
| `tools/` | `doctor.py`, `build_rules_doc.py`, example build scripts (`hf3/`, `lumarein/`) |
| `refs/`, `style/`, `audience/`, `voice/`, `psychology/` | Reference reel analyses, style, audience and comment research |

## Safety defaults

- Nothing is posted and no credits are spent without the owner's explicit approval of that post or of a plan + cap.
- No tokens in files or chat; `.env` and real config are gitignored. Run `tools/doctor.py` before pushing.
- Never feature or sexualize minors; no race-based casting.

## License

No license has been chosen yet; all rights reserved by the owner. Ask before redistributing.
`assets/emoji_apple/` images are Apple's emoji artwork (see `assets/emoji_apple/LICENSE` for the data files);
use them at your own risk.
