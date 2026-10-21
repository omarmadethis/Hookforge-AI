"""Word-level ASR helper (faster-whisper, decoded via ffmpeg to avoid the av version clash)."""
import subprocess, numpy as np, functools
@functools.lru_cache()
def _model(size="small"):
    from faster_whisper import WhisperModel
    return WhisperModel(size, compute_type="int8")
def pcm(path, start=0.0, dur=None, sr=16000):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(start), "-i", path] + (["-t", str(dur)] if dur else []) + ["-ac", "1", "-ar", str(sr), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32)
def words(path, start=0.0, dur=None, prompt=None):
    segs, _ = _model().transcribe(pcm(path, start, dur), word_timestamps=True, language="en", initial_prompt=prompt)
    return [dict(w=w.word.strip(), s=round(w.start + start, 2), e=round(w.end + start, 2)) for s in segs for w in s.words]
