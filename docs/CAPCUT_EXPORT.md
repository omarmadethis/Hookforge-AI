# CapCut draft export (evaluation, 2026-10-18 PT)

Goal: Hookforge hands Omar an **editable CapCut project** (not only a flat MP4) so he can tweak in the editor he already uses.

## Target format (measured on the team's 110 drafts)
- CapCut desktop **9.4.1, macOS**, `app_source: cc`, `new_version: 185.0.0`, `version: 360000`.
- Project folder: `draft_info.json` + identical copy under `Timelines/<UUID>/draft_info.json` + `draft_meta_info.json` (+ `template.tmp`).
- Times in microseconds. Text style JSON lives in `materials.texts[].content`; style `range` counts UTF-16 code units (emoji = 2).
- Text y: `segment.clip.transform.y` in [-1, 1], +up. Team median 0.62 → centre 19 % from top. Font size 15, black stroke 0.09.

## Option A: pyJianYingDraft 0.3.1 (venv `/workspace/.venvs/capcut`)
- Works: created a 3-shot + text draft in `/workspace/tmp/capcut_test/drafts/HF_TEST_PYJY`.
- But it writes **`draft_content.json` from a JianYing 5.9 / Windows template (new_version 110)**. The Mac CapCut 9.4 build may upgrade it or may reject it. Untested on the Mac.
- Its loader *does* open our native export (renamed), so it stays useful as a validator.

## Option B (chosen, D29): native clone writer, `engine/hookforge/capcut_export.py`
- Clones a real team draft (`1009 (5)`, MC-02 62.8K: 6 shots, 1 text, 1 song). It deep-copies a segment, its material and every extra material it references (speeds, canvases, sound-channel mappings, colours, animations, vocal separations, placeholder infos), all with fresh UUIDs.
- Test on a throwaway copy (`/workspace/tmp/capcut_test/drafts/HF_TEST_NATIVE`):
  - 4 shots, 1 text, and a song at offset 0.1 s.
  - `verify()` reports no problems: every ref resolves, the timeline is contiguous, there are no duplicate ids, and duration matches the video.
  - Our parser round-trips the exact times and text, and pyJianYingDraft loads it.
- `media_root_map` rewrites box paths to Mac paths, e.g. `/workspace/hookforge/runs` → `/Users/omar/Movies/Hookforge`.

## Not yet done (needs Omar)
- **Open test on the Mac:** copy one throwaway draft into `~/Movies/CapCut/User Data/Projects/com.lveditor.draft/HF_TEST_NATIVE` along with its media, open CapCut and confirm it loads. This requires Omar's approval for a Mac write (capability audit §5). Don't update CapCut before this test, because newer builds can encrypt drafts.
- Effects, filters, speed ramps and keyframes are not written. Shots are cuts only, which matches 62 % of team drafts having no speed change.
