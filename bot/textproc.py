"""Pure text preparation for speech (no model, no network): safe to unit-test in CI."""
import re

_TIME = re.compile(r"(?<![\d:.])(\d{1,2}):([0-5]\d)(?![\d:])")


def _say_time(m: re.Match) -> str:
    h, mi = m.group(1), m.group(2)
    if mi == "00":
        return f"{h} o'clock"
    return f"{h} oh {int(mi)}" if mi[0] == "0" else f"{h} {mi}"


# "Elm St. near" -> Street (after a capitalized word, before a lowercase word or the end);
# "St. Louis" -> Saint. Kokoro reads a bare "St." as "sent".
_STREET_END = re.compile(r"\b([A-Z][a-z]+) St\.(?=[ \t]*$)", re.M)       # keeps the sentence-final period
_STREET = re.compile(r"\b([A-Z][a-z]+) St\.(?=\s+[a-z]|[,;:!?)])")
_SAINT = re.compile(r"\bSt\.\s+(?=[A-Z])")


def normalize(text: str) -> str:
    """Prepare text for Kokoro: '7:30' becomes '7 30' (':' is read as a long pause) and
    'Elm St.' becomes 'Elm Street'."""
    text = _STREET_END.sub(r"\1 Street.", text)
    text = _STREET.sub(r"\1 Street", text)
    text = _SAINT.sub("Saint ", text)
    return _TIME.sub(_say_time, text)


def chunks(text: str):
    """Return [[sentence_group, pause_multiplier], ...]. Pause multiplier is 1 after a
    line break, 2 after a blank line, 0 inside a line. Groups are at most ~300 chars."""
    out, blank = [], 0
    for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if not line.strip():
            blank += 1
            continue
        if out:
            out[-1][1] = 2 if blank else 1
        blank = 0
        cur = ""
        for s in re.findall(r"[^.!?]+[.!?]*\s*", re.sub(r"\s+", " ", line)):
            if len(cur + s) > 300 and cur:
                out.append([cur, 0])
                cur = s
            else:
                cur += s
        if cur.strip():
            out.append([cur, 0])
    return out
