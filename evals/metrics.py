"""Metrics for the TTS eval. Pure functions, unit-tested in tests/test_eval_metrics.py."""
import re

import numpy as np
from num2words import num2words

_ABBREV = {"dr": "doctor", "mr": "mister", "mrs": "missus", "misses": "missus", "st": "street", "vs": "versus"}
_TIME = re.compile(r"\b(\d{1,2})[:.](\d{2})\b")
_ORD = re.compile(r"\b(\d+)(?:st|nd|rd|th)\b")
_DOLLARS = re.compile(r"\$\s?(\d+)")


def _num(n: str) -> str:
    v = int(n)
    return num2words(v, to="year") if 1100 <= v <= 2099 else num2words(v)


def normalize_for_wer(text: str) -> list[str]:
    """Lowercase, spell out digits/ordinals/dollars, expand common abbreviations, drop punctuation.
    Applied to both the source text and the speech-to-text output so formatting differences
    do not count as errors: '7:30', '7.30' and '730' are the same token, 'Dr.' equals 'doctor',
    '$17' equals '17 dollars'.
    Known limit: Whisper writing a time in words ('seven thirty') is counted as an error."""
    t = text.lower().replace("’", "'")
    t = _TIME.sub(lambda m: m.group(1) + m.group(2), t)     # 7:30 / 7.30 -> 730
    t = _DOLLARS.sub(lambda m: f"{m.group(1)} dollars", t)
    t = _ORD.sub(lambda m: num2words(int(m.group(1)), to="ordinal"), t)
    t = re.sub(r"\d+", lambda m: _num(m.group(0)), t)
    t = re.sub(r"[^a-z' ]+", " ", t.replace("-", " "))
    return [_ABBREV.get(w, w) for w in t.split()]


def edit_distance(a: list[str], b: list[str]) -> int:
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]


def wer(reference: str, hypothesis: str) -> tuple[int, int]:
    """Return (word errors, reference word count)."""
    r, h = normalize_for_wer(reference), normalize_for_wer(hypothesis)
    return edit_distance(r, h), len(r)


def longest_internal_silence(samples: np.ndarray, sr: int, frame_ms: int = 10, rel_thresh: float = 0.02) -> float:
    """Longest run of near-silent frames (seconds) between the first and last speech frame.
    Used to detect unwanted long pauses (e.g. on a colon)."""
    x = np.asarray(samples, dtype=np.float64)
    if x.ndim > 1:
        x = x.mean(axis=1)
    n = int(sr * frame_ms / 1000)
    if len(x) < n * 3:
        return 0.0
    frames = np.sqrt(np.mean(x[: len(x) // n * n].reshape(-1, n) ** 2, axis=1))
    active = frames > rel_thresh * frames.max()
    idx = np.flatnonzero(active)
    if len(idx) < 2:
        return 0.0
    longest = run = 0
    for a in active[idx[0]: idx[-1] + 1]:
        run = 0 if a else run + 1
        longest = max(longest, run)
    return longest * frame_ms / 1000
