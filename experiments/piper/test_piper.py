import sys, wave, winsound, pathlib
from piper import PiperVoice

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "piper_out.wav"
model = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "models" / "en_US-lessac-medium.onnx")
text = (
    "Good morning. Today we are testing speech synthesis with Piper. "
    "The quick brown fox jumps over the lazy dog, while the rain falls softly on the quiet town. "
    "Numbers such as 1984 and 3.14159 are read aloud, and questions are spoken with a rising tone. "
    "Can you tell whether this voice sounds natural? Thank you for listening."
)

voice = PiperVoice.load(model)
with wave.open(str(OUT), "wb") as f:
    voice.synthesize_wav(text, f)
print(f"Saved {OUT}, playing...")
winsound.PlaySound(str(OUT), winsound.SND_FILENAME)
print("Done")
