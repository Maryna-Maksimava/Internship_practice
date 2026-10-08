"""Golden cases for the text preparation that feeds Kokoro (the product's core 'eval').

Each case is a bug we actually hit; see docs/tasks/ and specification.md.
"""
import pytest

from textproc import chunks, normalize


@pytest.mark.parametrize("src,expected", [
    ("Every day at 7:30, my alarm went off", "Every day at 7 30, my alarm went off"),
    ("lunch at 12:00", "lunch at 12 o'clock"),
    ("home at 6:05", "home at 6 oh 5"),
    ("ratio 3:1:2", "ratio 3:1:2"),            # not a time
    ("duration 1:23:45", "duration 1:23:45"),   # not a time
    ("Note: done", "Note: done"),               # real colon stays
])
def test_time_normalization(src, expected):
    assert normalize(src) == expected


@pytest.mark.parametrize("src,expected", [
    ("Dr. Smith lives on Elm St. near the park.", "Dr. Smith lives on Elm Street near the park."),
    ("He moved to Baker St.", "He moved to Baker Street."),
    ("Turn left on Main St., then right.", "Turn left on Main Street, then right."),
    ("She visited St. Louis last year.", "She visited Saint Louis last year."),
    ("It was the 1st St. of the list", "It was the 1st St. of the list"),   # not a street name: left alone
])
def test_st_abbreviation(src, expected):
    assert normalize(src) == expected


def test_line_break_pauses():
    out = chunks("Line one. Two.\nLine three\n\nPara two. End")
    assert out == [["Line one. Two.", 1], ["Line three", 2], ["Para two. End", 0]]


def test_long_line_split_under_300_chars():
    text = " ".join(f"This is sentence number {i}." for i in range(40))
    parts = chunks(text)
    assert len(parts) > 1
    assert all(len(p) <= 330 for p, _ in parts)   # 300 + the sentence that crossed the limit
    assert " ".join(p.strip() for p, _ in parts) == text


def test_crlf_and_empty_input():
    assert chunks("a.\r\nb.") == [["a.", 1], ["b.", 0]]
    assert chunks("") == []
    assert chunks("\n\n  \n") == []
