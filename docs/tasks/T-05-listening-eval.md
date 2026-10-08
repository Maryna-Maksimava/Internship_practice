# T-05 Listening / round-trip eval for speech quality

**Goal.** A repeatable quality check beyond text unit tests: does the audio say what the text says?

**Idea.** Synthesize a fixed set of ~20 sentences (numbers, times, abbreviations, headings), transcribe with an open
speech-to-text model (for example faster-whisper `tiny`/`base`), compute word error rate against the source text.
Track WER per release. Plus a human listening sheet: 10 clips, each rated 1-5 for naturalness and flagged for odd pauses.

**Scope.** In: `evals/roundtrip.py`, a fixed `evals/sentences.txt`, a results table in docs/. Out: running it in CI
(model files and Whisper are too heavy; run locally).

**Acceptance.** `python evals/roundtrip.py` prints WER and per-sentence diffs; baseline recorded; threshold proposed
(starting point: WER <= 10 percent, zero errors on numbers and times).

**Roles.** Agent builds the harness. Human does the listening sheet, because the agent cannot hear.
