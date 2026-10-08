# Known limitations

Honest list as of the current prototype. "Impact" says who feels it; "Plan" links to a task or says none.

| # | Limitation | Impact | Plan |
|---|---|---|---|
| 1 | Generation on the phone is slow (WASM q8 about 0.5x real time on desktop; phone not measured) | Mini App feels unusable for long texts | T-01, T-02 |
| 2 | WebGPU fp32 produced garbled audio on the owner's phone; mobile defaults to WASM | slower phones | T-01 (fp16 trial) |
| 3 | Bot runs on the owner's PC: works only while it is on, awake and the script is running | availability | none (hosting out of scope) |
| 4 | Scanned PDFs (images only) are rejected; no OCR | those documents cannot be read | none |
| 5 | PDF layout: multi-column pages, headers/footers, page numbers and footnotes are read as they appear; paragraph breaks in the bot rely on a line-length heuristic and may merge paragraphs | extra or missing pauses | improve with real documents |
| 6 | Heading detection is heuristic: a short last line of a paragraph without punctuation can be mistaken for a heading | an extra pause | golden tests grow with each case |
| 7 | English only. Kokoro has few voices for other languages; Russian is not supported in this version | non-English texts | none |
| 8 | Only `.txt`, `.md`, `.pdf` | other formats | T-04 |
| 9 | Highlight follows chunks (a line, split at 300 chars), not words; the model gives no word timings | coarse highlight on long paragraphs | optional per-sentence split |
| 10 | Bot output is Ogg Vorbis sent as a document, not an inline voice message | convenience | T-06 |
| 11 | Per-user settings (`/voice`, `/speed`, `/pause`) reset when the bot restarts | minor | none |
| 12 | First Mini App use downloads the model (roughly 80-330 MB depending on backend) | mobile data | cached afterwards |
| 13 | Privacy of the Mini App and the bot allowlist are implemented but not verified end to end | assurance | T-03 |
| 14 | Pauses at headings and times were checked in text, not by ear (the agent cannot hear) | quality | T-05 human listening sheet |
| 15 | Text logic exists twice (Python and JavaScript) and must be kept in sync | maintenance | shared golden cases in tests |
| 16 | Model licence: Kokoro is Apache 2.0; check any extra voice or model before redistributing | legal | n/a |
