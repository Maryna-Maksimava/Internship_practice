"""End-to-end synthesis smoke test. Needs the model files in models/ (not available in CI)."""
import io
import os
import pathlib
import time

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODEL = ROOT / "models" / "kokoro-v1.0.onnx"
VOICES = ROOT / "models" / "voices-v1.0.bin"

pytestmark = pytest.mark.skipif(not (MODEL.exists() and VOICES.exists()),
                                reason="Kokoro model files not downloaded (see README)")


def test_text_to_speech_is_audible_and_fast_enough():
    import numpy as np
    import soundfile as sf
    from kokoro_onnx import Kokoro
    from textproc import chunks, normalize

    k = Kokoro(str(MODEL), str(VOICES))
    text = "Good morning.\nEvery day at 7:30, my alarm went off."
    t0 = time.time()
    audio, sr = [], 24000
    for sentence, _ in chunks(normalize(text)):
        s, sr = k.create(sentence, voice="af_heart", speed=1.0, lang="en-us")
        audio.append(s)
    took = time.time() - t0
    wav = np.concatenate(audio)
    secs = len(wav) / sr

    assert secs > 2.0                                   # something was actually spoken
    assert float(np.sqrt(np.mean(wav ** 2))) > 0.01     # not silence
    assert secs / took > 0.5, f"too slow: {secs / took:.2f}x real time"   # eval threshold, see spec F-criteria 3

    buf = io.BytesIO()
    sf.write(buf, wav, sr, format="OGG", subtype="VORBIS")
    assert buf.getvalue()[:4] == b"OggS"
