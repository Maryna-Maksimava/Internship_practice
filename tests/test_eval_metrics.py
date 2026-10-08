import sys

import numpy as np
import pytest

from conftest import ROOT

sys.path.insert(0, str(ROOT / "evals"))
from metrics import longest_internal_silence, normalize_for_wer, wer  # noqa: E402


def test_formatting_differences_do_not_count_as_errors():
    assert normalize_for_wer("at 7:30") == normalize_for_wer("at 730") == normalize_for_wer("at 7.30")
    assert normalize_for_wer("at 6:05") == normalize_for_wer("at 6.05")
    assert normalize_for_wer("in 1984") == normalize_for_wer("in nineteen eighty-four")
    assert normalize_for_wer("the 3rd floor") == normalize_for_wer("the third floor")
    assert normalize_for_wer("Dr. Smith") == normalize_for_wer("doctor smith")
    assert normalize_for_wer("costs 17 dollars") == normalize_for_wer("costs $17")


def test_a_wrong_time_is_still_an_error():
    assert wer("at 7:30", "at 7:35")[0] == 1
    assert wer("at 12:00", "at 12, 0, 0")[0] > 0


def test_wer_counts_errors():
    assert wer("the cat sat", "the cat sat") == (0, 3)
    assert wer("the cat sat", "the hat sat") == (1, 3)
    assert wer("the cat sat", "the cat") == (1, 3)


def test_longest_internal_silence_ignores_edges_and_finds_gap():
    sr = 16000
    tone = np.sin(2 * np.pi * 220 * np.arange(sr // 2) / sr)
    clip = np.concatenate([np.zeros(sr), tone, np.zeros(sr * 3 // 4), tone, np.zeros(sr)])
    assert longest_internal_silence(clip, sr) == pytest.approx(0.75, abs=0.03)
    assert longest_internal_silence(np.concatenate([np.zeros(sr), tone]), sr) == 0.0
