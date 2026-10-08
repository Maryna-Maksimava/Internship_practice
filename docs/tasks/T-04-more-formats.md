# T-04 EPUB and DOCX input

**Goal.** Accept `.epub` and `.docx` in the bot and the Mini App (requirement F7).

**Scope.** Bot: `ebooklib` or plain `zipfile` + HTML text extraction; `python-docx`. Mini App: JSZip for both formats.
Reuse heading logic: chapter titles and Word heading styles map to "heading" (own line, double pause).
Out: DRM-protected books, images, footnotes.

**Files.** `bot/` new `docx_text.py`, `epub_text.py` (pure, testable), `bot/bot.py` extension check,
`miniapp/index.html` file picker + reader.

**Acceptance.** A sample EPUB and a sample DOCX (committed under `tests/data/`, small, self-made) each produce text
with headings on their own lines; pytest golden cases added; both front ends accept the new extensions.
