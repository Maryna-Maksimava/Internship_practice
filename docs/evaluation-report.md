# Evaluation report

Short version of the experiment. Full protocol, tables and error analysis: [evidence.md](evidence.md). Code:
`evals/`. Raw results: `evals/results/results.md`.

## Question

Which speech engine reads documents best for a free, local tool, and does our text preparation help?

## Setup

- 22 test sentences in 7 categories (plain, numbers, times, dates, abbreviations, questions, long).
- Systems: eSpeak NG (baseline), Piper `lessac-medium`, Kokoro-82M `af_heart` without and with our text preparation.
- Metrics: word error rate by round trip (synthesize, transcribe with Whisper `base.en`, compare), speed in multiples
  of real time, longest silence inside a clip, and a blinded human listening rating (24 clips, one rater).

## Results

| System | WER | Speed (x real time) | Naturalness 1-5 (human) |
|---|---|---|---|
| eSpeak NG | 12.5% | 56.2 | 1.00 |
| Piper | 2.5% | 24.1 | 3.17 |
| Kokoro, no text prep | 3.6% | 3.1 | 4.67 |
| Kokoro, with text prep | 1.1% | 3.2 | 5.00 |

On time expressions only: WER 17.0% without text preparation vs 2.1% with it, and the pause on the colon
disappears (0.25-0.28 s down to 0.03-0.04 s on "6:05" and "9:15").

## Conclusions

1. Kokoro is the best free option tried for quality; its cost is speed (about 3x real time on CPU).
2. Text preparation is a cheap, measurable improvement on times and numbers.
3. One real defect remains for every neural engine: the abbreviation "St." ("Elm St." read as "Elmsent").

## Threats to validity

22 sentences, one run, one voice, one rater; WER measures intelligibility, not pleasantness; two metric artifacts
(a time written as words counts as an error) slightly understate every system's score. Speed was measured on one
desktop CPU and in a desktop browser; phone speed was not measured.

## Reproduce

`python evals/run_eval.py` then `python evals/score_listening.py` (see [reproduction.md](reproduction.md)).
