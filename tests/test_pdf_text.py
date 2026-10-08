"""PDF extraction: headings stand alone, wrapped lines are joined, scans are rejected."""
import pytest
from fpdf import FPDF

from pdf_text import pdf_to_text


def make_pdf(blocks):
    """blocks: list of (font_style, size, text)."""
    p = FPDF()
    p.add_page()
    for style, size, text in blocks:
        p.set_font("Helvetica", style, size)
        p.multi_cell(0, size * 0.6, text)
        p.ln(3)
    return bytes(p.output())


BODY = ("Every day at 7:30, my alarm went off, and I dragged myself out of bed to make coffee "
        "before the sun had even come up over the hills.")


def test_heading_is_separate_and_wrapped_lines_joined():
    text = pdf_to_text(make_pdf([("B", 20, "Chapter 1"), ("", 12, BODY)]))
    lines = [l for l in text.split("\n") if l.strip()]
    assert lines[0] == "Chapter 1"
    assert lines[1].startswith("Every day at 7:30")
    assert len(lines) == 2               # the wrapped body is one line


def test_subheading_detected():
    text = pdf_to_text(make_pdf([("", 12, BODY), ("B", 14, "A Quiet Morning"), ("", 12, BODY)]))
    assert "\nA Quiet Morning\n" in "\n" + text + "\n"


def test_pdf_without_text_is_rejected():
    p = FPDF()
    p.add_page()      # blank page: stands in for a scanned PDF
    with pytest.raises(ValueError, match="No text found"):
        pdf_to_text(bytes(p.output()))


def test_garbage_is_rejected():
    with pytest.raises(Exception):
        pdf_to_text(b"not a pdf")
