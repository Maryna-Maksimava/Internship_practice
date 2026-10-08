"""TTS eval: which engine says what the text says, how fast, and without odd pauses?

    python evals/run_eval.py                 # all engines found on this machine
    python evals/run_eval.py --engines kokoro,espeak

Protocol (see docs/evidence.md):
  1. For every sentence in evals/sentences.csv, synthesize with each engine.
  2. Transcribe the audio with Whisper (faster-whisper base.en, CPU, greedy).
  3. WER = word errors / reference words, after normalizing digits, times, ordinals, abbreviations.
  4. Speed = audio seconds / synthesis wall seconds (x real time).
  5. Longest internal silence per clip (catches the long pause on ':' in times).
  6. Write results to evals/results/ and blinded clips + a rating sheet for human listening.

Engines: espeak (baseline), piper, kokoro_raw (Kokoro, no text prep), kokoro (Kokoro + our text prep).
"""
import argparse
import csv
import json
import pathlib
import random
import shutil
import subprocess
import sys
import time
import wave

import numpy as np
import soundfile as sf

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bot"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from metrics import longest_internal_silence, wer  # noqa: E402
from textproc import normalize  # noqa: E402

CLIPS = ROOT / "output" / "evals"
RESULTS = pathlib.Path(__file__).resolve().parent / "results"
ESPEAK = shutil.which("espeak-ng") or r"C:\Program Files\eSpeak NG\espeak-ng.exe"


def load_sentences():
    with open(pathlib.Path(__file__).resolve().parent / "sentences.csv", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


# ---- engines: each returns (path_to_wav, synth_seconds) ----------------------------------

def make_engines(wanted):
    engines = {}

    if pathlib.Path(ESPEAK).exists():
        def espeak(text, out):
            t = time.time()
            subprocess.run([ESPEAK, "-v", "en-us", "-w", str(out), text], check=True, capture_output=True)
            return time.time() - t
        engines["espeak"] = espeak

    piper_model = ROOT / "models" / "en_US-lessac-medium.onnx"
    if piper_model.exists():
        from piper import PiperVoice
        voice = PiperVoice.load(str(piper_model))

        def piper(text, out):
            t = time.time()
            with wave.open(str(out), "wb") as f:
                voice.synthesize_wav(text, f)
            return time.time() - t
        engines["piper"] = piper

    if (ROOT / "models" / "kokoro-v1.0.onnx").exists():
        from tts import get_kokoro
        k = get_kokoro()

        def kokoro_with(prep):
            def run(text, out):
                t = time.time()
                samples, sr = k.create(normalize(text) if prep else text, voice="af_heart", speed=1.0, lang="en-us")
                took = time.time() - t
                sf.write(str(out), samples, sr)
                return took
            return run
        engines["kokoro_raw"] = kokoro_with(False)
        engines["kokoro"] = kokoro_with(True)

    return {n: e for n, e in engines.items() if not wanted or n in wanted}


def to_16k_mono(x, sr):
    """Whisper input without going through PyAV (its newest release breaks faster-whisper's decoder)."""
    x = np.asarray(x, dtype=np.float32)
    if x.ndim > 1:
        x = x.mean(axis=1)
    if sr == 16000:
        return x
    n = int(round(len(x) * 16000 / sr))
    return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x).astype(np.float32)


# ---- main -------------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engines", default="", help="comma list; default all available")
    ap.add_argument("--whisper", default="base.en")
    ap.add_argument("--rescore", action="store_true",
                    help="recompute WER and the summary from results/results.json without synthesizing again")
    ap.add_argument("--new-listening-sheet", action="store_true",
                    help="create a fresh blinded rating sheet and key. DANGER: overwrites entered human ratings")
    ap.add_argument("--trim-listening", action="store_true",
                    help="shrink the existing listening sheet to the small subset, keeping entered ratings")
    a = ap.parse_args()

    if a.trim_listening:
        trim_listening()
        return
    if a.rescore:
        rows = json.loads((RESULTS / "results.json").read_text(encoding="utf-8"))
        for r in rows:
            r["word_errors"], r["ref_words"] = wer(r["text"], r["heard"])
        (RESULTS / "results.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
        write_summary(rows)
        print("rescored", len(rows), "clips")
        return

    sentences = load_sentences()
    engines = make_engines({e for e in a.engines.split(",") if e})
    if not engines:
        sys.exit("No engines available (need espeak-ng, models/ for piper or kokoro).")
    print("engines:", ", ".join(engines))

    from faster_whisper import WhisperModel
    stt = WhisperModel(a.whisper, device="cpu", compute_type="int8")

    # warm up so the first clip's speed is not dominated by model loading
    CLIPS.mkdir(parents=True, exist_ok=True)
    for run in engines.values():
        run("Warm up.", CLIPS / "warmup.wav")

    rows = []
    for name, run in engines.items():
        out_dir = CLIPS / name
        out_dir.mkdir(parents=True, exist_ok=True)
        for s in sentences:
            path = out_dir / f"{s['id']}.wav"
            took = run(s["text"], path)
            samples, sr = sf.read(str(path))
            dur = len(samples) / sr
            segs, _ = stt.transcribe(to_16k_mono(samples, sr), language="en", beam_size=1, temperature=0.0,
                                     condition_on_previous_text=False)
            heard = " ".join(seg.text.strip() for seg in segs)
            errs, nref = wer(s["text"], heard)
            rows.append({
                "engine": name, "id": s["id"], "category": s["category"], "text": s["text"], "heard": heard,
                "word_errors": errs, "ref_words": nref, "audio_s": round(dur, 2), "synth_s": round(took, 3),
                "speed_x": round(dur / took, 2) if took else None,
                "max_silence_s": round(longest_internal_silence(samples, sr), 2),
            })
        print(f"  {name}: done")

    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "results.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    write_summary(rows)
    if a.new_listening_sheet:
        write_listening_sheet(sentences, list(engines))
    else:
        print("listening sheets untouched (pass --new-listening-sheet to create fresh blinded ones)")
    print("wrote", RESULTS)


def agg(rows, key):
    out = {}
    for r in rows:
        g = out.setdefault(r[key], {"err": 0, "ref": 0, "audio": 0.0, "synth": 0.0, "n": 0, "sil": []})
        g["err"] += r["word_errors"]; g["ref"] += r["ref_words"]
        g["audio"] += r["audio_s"]; g["synth"] += r["synth_s"]; g["n"] += 1; g["sil"].append(r["max_silence_s"])
    return out


def write_summary(rows):
    engines = list(dict.fromkeys(r["engine"] for r in rows))
    cats = list(dict.fromkeys(r["category"] for r in rows))
    lines = ["# Eval results (generated by evals/run_eval.py)", ""]
    lines += ["## Overall", "", "| Engine | WER | Speed (x real time) | Median longest silence (s) | Clips |", "|---|---|---|---|---|"]
    for e, g in agg(rows, "engine").items():
        lines.append(f"| {e} | {100 * g['err'] / g['ref']:.1f}% | {g['audio'] / g['synth']:.1f} | "
                     f"{float(np.median(g['sil'])):.2f} | {g['n']} |")
    lines += ["", "## WER by category", "", "| Category | " + " | ".join(engines) + " |", "|---|" + "---|" * len(engines)]
    for c in cats:
        cells = []
        for e in engines:
            sub = [r for r in rows if r["engine"] == e and r["category"] == c]
            cells.append(f"{100 * sum(r['word_errors'] for r in sub) / max(1, sum(r['ref_words'] for r in sub)):.1f}%")
        lines.append(f"| {c} | " + " | ".join(cells) + " |")
    lines += ["", "## Longest internal silence on time sentences (s): effect of text preparation", "",
              "| Sentence | " + " | ".join(engines) + " |", "|---|" + "---|" * len(engines)]
    for r0 in [r for r in rows if r["engine"] == engines[0] and r["category"] == "times"]:
        cells = [str(next(r["max_silence_s"] for r in rows if r["engine"] == e and r["id"] == r0["id"])) for e in engines]
        lines.append(f"| {r0['id']} {r0['text']} | " + " | ".join(cells) + " |")
    lines += ["", "## Every word error", "", "| Engine | Id | Expected | Heard |", "|---|---|---|---|"]
    for r in rows:
        if r["word_errors"]:
            lines.append(f"| {r['engine']} | {r['id']} | {r['text']} | {r['heard']} |")
    (RESULTS / "results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


# Human listening uses a small subset: one or two sentences per category that matters, all engines.
LISTEN_SUBSET = ["s02", "s09", "s11", "s14", "s16", "s21"]


def trim_listening(keep=LISTEN_SUBSET):
    """Shrink the existing blinded sheet to the subset, keeping clip ids and any ratings already entered."""
    blind_dir = CLIPS / "blind"
    with open(RESULTS / "listening_key.csv", encoding="utf-8-sig", newline="") as f:
        key = list(csv.DictReader(f))
    with open(RESULTS / "listening_sheet.csv", encoding="utf-8-sig", newline="") as f:
        sheet = list(csv.DictReader(f))
    keep_ids = {k["clip"] for k in key if k["sentence"] in keep}
    sheet = [r for r in sheet if r["clip"] in keep_ids]
    for wav in blind_dir.glob("c*.wav"):
        if wav.stem not in keep_ids:
            wav.unlink()
    fields = ["clip", "text", "naturalness_1_5", "odd_pause_y_n", "misread_y_n", "rater"]
    out = RESULTS / "listening_sheet_short.csv"   # separate file: the full sheet may be open in Excel
    with open(out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, restval=""); w.writeheader(); w.writerows(sheet)
    print(f"{out.name}: {len(sheet)} clips")


def write_listening_sheet(sentences, engines, seed=7):
    """Blind the engines: clips get random ids; the key is kept apart from the rating sheet."""
    sentences = [s for s in sentences if s["id"] in LISTEN_SUBSET]
    blind_dir = CLIPS / "blind"
    shutil.rmtree(blind_dir, ignore_errors=True)
    blind_dir.mkdir(parents=True)
    ids = [f"c{n:03d}" for n in range(len(engines) * len(sentences))]
    random.Random(seed).shuffle(ids)
    key, sheet = [], []
    for (e, s), cid in zip([(e, s) for e in engines for s in sentences], ids):
        shutil.copy(CLIPS / e / f"{s['id']}.wav", blind_dir / f"{cid}.wav")
        key.append({"clip": cid, "engine": e, "sentence": s["id"]})
        sheet.append({"clip": cid, "text": s["text"], "naturalness_1_5": "", "odd_pause_y_n": "", "misread_y_n": "", "rater": ""})
    sheet.sort(key=lambda r: r["clip"])
    for name, data in (("listening_key.csv", key), ("listening_sheet.csv", sheet)):
        with open(RESULTS / name, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(data[0])); w.writeheader(); w.writerows(data)


if __name__ == "__main__":
    main()
