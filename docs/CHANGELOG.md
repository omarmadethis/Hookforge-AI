
## 2026-10-18 ~10:00 PM PT - style/psych integration (queued after core path)
- engine/hookforge/style.py: text scale by length (<=17 ch 1.0, 18-22 0.88, 23-28 0.76, >28 0.72, Vs card 1.2); emoji rules (max 2 hook emojis, 🎄 not as hook emoji); PS12 >=2 hands-on shots (planner auto-rewrites a handling shot to high-angle POV), PS19 <=1 face-to-camera; Brick Hood hooks must be chairlift/slope/snowmobile (BLOCK). F04 stays exempt from product-at-0s.
- Covered-reveal hooks NOT blocked (D52, Omar 9:55 PM PT).
- autoedit: text cards rendered with style/render_text.py (colour emoji, CapCut geometry, per-card scale); no animations. capcut_export writes per-card scale.
- music: STYLE_GUIDE §5 in-points override library offsets (Last Christmas 170.5 s, Bublé 32.4 s, Free Bird 15.0 s ...).
- profiles: CapCut emojis replace frame-read emojis only when the draft text agrees (>=0.8 word sim and same recipient word). capcut_drafts join: recipient-word mismatch halves the score -> HJ-13 (mom reel vs "dad" 🏎️ draft) and MJIG-04 ("cozy mom" vs "Christmas-aholic") unjoined; HJ-15 join kept (😳☃️). Primary joins 35 -> 33.
- engine/hookforge/psych.py: PS01-PS19 advisory scorer in the backtest report (shot evidence from style/shots.csv); pure audience-callout hooks rank last in the hook picker and score -2.
- Fixes: sanitize_casting no longer splits "2.1s" into "2. 1s" or drops newlines; preflight OCR conf str->float; "Same a family..." prompt wording.

## 2026-10-18 ~10:40 PM PT - open items closed, queued items wired, Phase E + F
- Open items: robe controller activation confirmed in PLAN (PLUG/REM shots); views model retrained after HJ-13/MJIG-04 unjoin (B2 LOO AUC 0.629->0.616, still advisory D35); preflight OCR conf fix in place.
- D42 failure memory wired (gen_failures.py, runner.py pre-flight linter, ledger/pairs/rules/failure_rate, misgen logging from qa.reroll_decision).
- D44: structural provenance detector (old byte match false-positived); tests/test_c2pa_strip.py; every dry run runs clean_export + assert.
- D53: covered-reveal hook options (robe covered_reveal + covered_drape, fire pit / ski mask covered_glow innovation-only), advisory PS02.
- US cues: snippet parser fixed (ski-lodge flag cues for Brick Hood). Off-world hook fallback fixed ('grinch'/'mom' lines no longer land on MerryFire/Brick Hood).
- tests/test_core_path.py: all green on 4 core + 4 covered briefs.
- Phase E: learn.build_day (5/day/product, pages, windows, originality, lint, credits), option arms, evaluate_experiments, update() adds gen_failures + experiments; dashboard engine panels (arms/schedule, failure memory, model, windows, dry runs). Loader: data/features hookforge.db is opt-in until adapted.
- Phase F: AUTOMATION.md updated; package_public excludes failure ledger, support inbox data, voice INSIGHTS/rules, screenshots, insights, product profiles; 227 files, 0 regex leaks (not pushed).
