# Evals

Round-trip evaluation of speech synthesis: synthesize a fixed set of sentences, transcribe them back with
Whisper, and count word errors. Also measures speed and unwanted pauses.

```bash
pip install faster-whisper num2words          # plus the engines you want to compare
python evals/run_eval.py                       # all engines found on this machine
python evals/run_eval.py --engines kokoro      # a subset
python evals/run_eval.py --rescore             # recompute metrics from results/results.json, no synthesis
```

- `sentences.csv`: the test set (22 sentences, 7 categories).
- `metrics.py`: WER normalization, edit distance, longest-internal-silence (unit-tested in `tests/`).
- `run_eval.py`: the harness. Engines: `espeak` (baseline), `piper`, `kokoro_raw` (no text prep), `kokoro` (with our text prep).
- `results/results.md`, `results.json`: latest run. Human rating: `results/listening_sheet_short.csv` (24 blinded
  clips: 6 sentences x 4 systems, clips in `output/evals/blind/`, git-ignored; regenerate with the script) and
  `listening_key.csv` (which engine is which; do not open before rating). `listening_sheet.csv` is the earlier
  full 88-clip sheet; `python evals/run_eval.py --trim-listening` shrinks it to the short one keeping ratings.

Protocol, results and analysis: [docs/evidence.md](../docs/evidence.md).
