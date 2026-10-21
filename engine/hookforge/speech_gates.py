"""D72 speech QA gates (Omar 2026-10-19 9:34 PM PT).
SG1 dialogue completeness: ASR on the final's hook window must contain every expected word in order (e.g. "3 2 1 let's see how it comes out"); a missing word BLOCKs.
SG2 speech audibility: voice-to-music ratio during speech, from the mix stems, must be >= 6 dB (target 6-10); below BLOCKs.
Numbers and words are normalised (three/3, two/2, one/1)."""
import re, numpy as np
from . import asr
NUM = {"three": "3", "two": "2", "one": "1", "to": "2", "too": "2", "won": "1"}
def _norm(t): return [NUM.get(w, w) for w in re.findall(r"[a-z0-9']+", t.lower())]
def _missing(got, exp):
    i = 0; missing = []
    for e in exp:
        j = next((k for k in range(i, len(got)) if got[k] == e), None)
        if j is None: missing.append(e)
        else: i = j + 1
    return missing
def dialogue_complete(final, expected, start=0.0, dur=None):
    """Whisper on short music-bed windows is window-sensitive (it dropped a chanted countdown at one length and
    heard it at another), so decode the hook at 3 window lengths and keep the best; BLOCK only if every decode misses a word."""
    exp = _norm(expected); best = None
    for d in ([dur, (dur or 4) + 0.6, (dur or 4) + 1.2]):
        got = _norm(" ".join(w["w"] for w in asr.words(final, start, d, prompt=None))); m = _missing(got, exp)
        if best is None or len(m) < len(best[1]): best = (got, m)
        if not m: break
    got, missing = best
    return dict(gate="SG1", ok=not missing, level="INFO" if not missing else "BLOCK", heard=" ".join(got), expected=" ".join(exp), missing=missing)
def _rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(np.square(x))) + 1e-9)
def audibility(voice_stem, music_stem, windows, min_db=6.0):
    """windows: [(t0,t1)] of speech in final time. Stems must carry the exact gains used in the mix."""
    v = asr.pcm(voice_stem); m = asr.pcm(music_stem); sr = 16000; rows = []
    for t0, t1 in windows:
        a, b = int(t0 * sr), int(t1 * sr); r = _rms_db(v[a:b]) - _rms_db(m[a:b]); rows.append(round(float(r), 1))
    ok = all(r >= min_db for r in rows)
    return dict(gate="SG2", ok=ok, level="INFO" if ok else "BLOCK", vmr_db=rows, min_db=min_db)
