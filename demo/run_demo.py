"""End-to-end demo: document in -> speech out, with the same code the bot uses.

    python demo/run_demo.py                      # demo/sample.md -> output/demo.ogg
    python demo/run_demo.py my.pdf --voice bf_emma --play

Stages printed: extract text -> prepare (normalize + split) -> synthesize -> write file.
Needs the model files in models/ (see README).
"""
import argparse
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bot"))

from pdf_text import pdf_to_text  # noqa: E402
from textproc import chunks, normalize  # noqa: E402
from tts import synthesize  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?", default=str(ROOT / "demo" / "sample.md"))
    ap.add_argument("--voice", default="af_heart")
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--pause", type=float, default=0.7)
    ap.add_argument("--out", default=str(ROOT / "output" / "demo.ogg"))
    ap.add_argument("--play", action="store_true", help="play the result (Windows only)")
    a = ap.parse_args()

    path = pathlib.Path(a.file)
    t = time.time()
    raw = path.read_bytes()
    text = pdf_to_text(raw) if path.suffix.lower() == ".pdf" else raw.decode("utf-8", errors="replace")
    print(f"1. extract   {len(text):>6} chars            ({time.time() - t:.2f}s)")

    pieces = chunks(normalize(text))
    print(f"2. prepare   {len(pieces):>6} chunks, pauses at line breaks and headings")

    t = time.time()
    data = synthesize(text, a.voice, a.speed, a.pause,
                      on_progress=lambda d, n: print(f"\r3. synthesize {d}/{n}", end="", flush=True))
    took = time.time() - t
    print()

    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)

    import io
    import soundfile as sf
    info = sf.info(io.BytesIO(data))
    print(f"4. wrote     {out}  ({len(data) // 1024} KB, {info.duration:.1f}s audio)")
    print(f"   speed: {info.duration / took:.1f}x real time")

    if a.play:
        import winsound
        import numpy as np
        wav, sr = sf.read(io.BytesIO(data), dtype="int16")
        tmp = out.with_suffix(".wav")
        sf.write(str(tmp), np.asarray(wav), sr)
        winsound.PlaySound(str(tmp), winsound.SND_FILENAME)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
