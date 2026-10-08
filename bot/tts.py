"""Server-side speech synthesis shared by the bot and the demo (no Telegram imports)."""
import io
import pathlib
import threading

import numpy as np
import soundfile as sf

from textproc import chunks, normalize

ROOT = pathlib.Path(__file__).resolve().parent.parent
_kokoro = None


def get_kokoro():
    """Load the model once, on first use."""
    global _kokoro
    if _kokoro is None:
        from kokoro_onnx import Kokoro
        _kokoro = Kokoro(str(ROOT / "models" / "kokoro-v1.0.onnx"), str(ROOT / "models" / "voices-v1.0.bin"))
    return _kokoro


def synthesize(text: str, voice: str, speed: float, pause: float, on_progress=None) -> bytes:
    """Text -> Ogg Vorbis bytes, with pauses at line breaks and headings."""
    kokoro = get_kokoro()
    parts, sr = [], 24000
    pieces = chunks(normalize(text))
    for i, (sentence, mult) in enumerate(pieces):
        samples, sr = kokoro.create(sentence, voice=voice, speed=speed, lang="en-us")
        parts.append(samples)
        if mult and pause:
            parts.append(np.zeros(int(sr * pause * mult), dtype=np.float32))
        if on_progress:
            on_progress(i + 1, len(pieces))
    return _encode_ogg(np.concatenate(parts), sr)


def _encode_ogg(wav, sr: int) -> bytes:
    """libsndfile's Vorbis encoder overflows the default ~1 MB thread stack on Windows for
    longer audio, so encode in a thread with a big stack, whoever calls us."""
    result = {}

    def work():
        try:
            buf = io.BytesIO()
            sf.write(buf, wav, sr, format="OGG", subtype="VORBIS")
            result["data"] = buf.getvalue()
        except BaseException as e:  # re-raised in the caller
            result["error"] = e

    old = threading.stack_size(64 * 1024 * 1024)
    try:
        t = threading.Thread(target=work)
        t.start()
    finally:
        threading.stack_size(old)
    t.join()
    if "error" in result:
        raise result["error"]
    return result["data"]
