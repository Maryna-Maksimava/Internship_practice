"""Extract readable text from a PDF for speech.

PDF text comes out hard-wrapped at the page's line width, which would be read
as a pause on every line. We re-join wrapped lines and keep only real
paragraph breaks as newlines.
"""
import io
import re
import statistics

from pypdf import PdfReader

MAX_PAGES = 300
_END = re.compile(r"[.!?:\"”’)]$")


_HEADING_WORD = re.compile(
    r"^(chapter|part|book|section|prologue|epilogue|appendix|introduction|preface|contents)\b", re.I)
_NUMBERED = re.compile(r"^\d+(\.\d+)*\.?\s+\S")


def is_heading(line: str, typical: float) -> bool:
    """Short title-like line: 'Chapter 1', 'PART TWO', '2.1 Background', or a short line with no end punctuation."""
    if len(line) > 80:
        return False
    if _HEADING_WORD.match(line) and len(line) < 60:
        return True
    if line.endswith((".", "!", "?", ",", ";", ":", "-")) and not _NUMBERED.match(line):
        return False
    if line.isupper() and len(line) > 2:
        return True
    return len(line) < 0.5 * typical and len(line) < 50 and line[:1].isupper() and not line.endswith(("-", ","))


def _page_text(raw: str) -> str:
    lines = [l.strip() for l in raw.splitlines()]
    sizes = [len(l) for l in lines if l]
    if not sizes:
        return ""
    typical = statistics.median(sizes)
    out, cur = [], ""
    for l in lines:
        if not l:                      # blank line = paragraph break
            if cur:
                out.append(cur)
                cur = ""
            continue
        if is_heading(l, typical):     # headings stand alone, with a longer pause around them
            if cur:
                out.append(cur)
                cur = ""
            out += ["", l, ""]
            continue
        if cur.endswith("-") and l[:1].islower():
            cur = cur[:-1] + l         # de-hyphenate "exam-\nple"
        else:
            cur = f"{cur} {l}".strip()
        # a sentence-ending line that is clearly shorter than the rest ends a paragraph
        if _END.search(l) and len(l) < 0.7 * typical:
            out.append(cur)
            cur = ""
    if cur:
        out.append(cur)
    return "\n".join(out)


def pdf_to_text(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))
    if reader.is_encrypted:
        raise ValueError("The PDF is password-protected.")
    if len(reader.pages) > MAX_PAGES:
        raise ValueError(f"Too many pages ({len(reader.pages)}; limit {MAX_PAGES}).")
    pages = [_page_text(p.extract_text() or "") for p in reader.pages]
    text = "\n\n".join(p for p in pages if p)
    if not text.strip():
        raise ValueError("No text found. It may be a scanned PDF (images only), which needs OCR.")
    return text
