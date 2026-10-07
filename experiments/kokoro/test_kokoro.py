import sys, time, winsound, pathlib
import soundfile as sf
from kokoro_onnx import Kokoro

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "kokoro_out.wav"
voice = sys.argv[1] if len(sys.argv) > 1 else "af_heart"
text = (
    "Good morning. Today we are testing speech synthesis with Kokoro. "
    "The quick brown fox jumps over the lazy dog, while the rain falls softly on the quiet town. "
    "Numbers such as 1984 and 3.14159 are read aloud, and questions are spoken with a rising tone. "
    "Can you tell whether this voice sounds natural? Thank you for listening."
)

kokoro = Kokoro(str(ROOT / "models" / "kokoro-v1.0.onnx"), str(ROOT / "models" / "voices-v1.0.bin"))
t = time.time()
samples, sr = kokoro.create(text, voice=voice, speed=1.0, lang="en-us")
dur = len(samples) / sr
print(f"voice {voice}: {dur:.1f}s audio in {time.time() - t:.1f}s")
sf.write(str(OUT), samples, sr)
winsound.PlaySound(str(OUT), winsound.SND_FILENAME)
print("Done")
