# Architecture

## Goal and constraints

Turn documents into natural speech, **free** (open model, no paid API), **fast enough** to be useful,
and **private** where possible. One model (Kokoro-82M, Apache 2.0), two places to run it.

## Components

```
                           +--------------------------+
 Telegram user ----------> |  Telegram Bot (bot/)     |   runs on the owner's PC
  (phone)                  |  bot.py  Telegram glue   |
      |                    |  pdf_text.py  PDF->text  |
      |   "Read on my      |  textproc.py  normalize, |
      |    device" button  |               chunks     |
      |                    |  tts.py  Kokoro (ONNX)   |--> .ogg file back to chat
      v                    +--------------------------+
 Telegram Mini App
 (miniapp/index.html)  hosted on GitHub Pages (static, HTTPS)
   - pdf.js           PDF -> text            (in browser)
   - normalize/sentences  same rules as textproc.py
   - kokoro-js        Kokoro ONNX via WebGPU or WASM   (in browser)
   - player + sentence highlight + WAV download
```

Two synthesis paths, same text rules:

| Path | Where the model runs | Text leaves the device? | Speed measured | When to use |
|---|---|---|---|---|
| Mini App | user's phone/PC browser | no | desktop WebGPU 2.5x, WASM 0.5x real time; phone: not measured | privacy, no server needed |
| Bot | owner's PC (CPU) | yes (Telegram + owner's PC) | about 3x real time | long files, slow phone |

## Data flow (both paths)

1. **Input**: `.txt`, `.md`, `.pdf`, or pasted text.
2. **Extract** (PDF only): join wrapped lines, de-hyphenate, keep headings on their own line, reject scans.
3. **Normalize**: rewrite times (`7:30` -> `7 30`) because Kokoro reads `:` as a long pause.
4. **Split**: by line, then into groups of at most ~300 characters; each group carries a pause multiplier
   (1 after a line break, 2 after a blank line or heading).
5. **Synthesize** each group with Kokoro (24 kHz), insert silence of `pause x multiplier` seconds.
6. **Output**: bot encodes Ogg Vorbis and replies with a file; Mini App builds a WAV, plays it, highlights
   the current group by its start time, and offers download.

## Key decisions

| Decision | Why | Alternative rejected |
|---|---|---|
| Kokoro-82M | best naturalness among free models that run on a CPU at >= real time | eSpeak (robotic), Piper (good, less natural), XTTS/F5 (need a GPU) |
| Mini App + bot, not bot only | on-device synthesis costs nothing and keeps text private | server-only: needs an always-on machine |
| Static Mini App on GitHub Pages | free HTTPS hosting, required by Telegram | own server |
| Text logic duplicated in Python and JS | the Mini App must work with no backend | shared WASM/JS module (more build tooling for little gain); kept in sync by shared golden tests |
| Desktop default WebGPU, phone default WASM | WebGPU fp32 gave garbled audio on the owner's phone | WebGPU everywhere |
| Allowlist of Telegram IDs | synthesis burns the owner's CPU; bot is private | public bot |

## Files

| Path | Role |
|---|---|
| `bot/bot.py` | Telegram handlers, per-user settings, progress bar, allowlist |
| `bot/tts.py` | Kokoro loading + synthesis + Ogg encoding (big-stack thread on Windows) |
| `bot/textproc.py` | `normalize`, `chunks` (pure) |
| `bot/pdf_text.py` | PDF text extraction + heading detection (pure) |
| `miniapp/index.html` | whole Mini App, no build step |
| `tests/` | pytest + node tests; golden cases for text handling |
| `demo/` | `run_demo.py` end-to-end demo and `sample.md` |
| `.github/workflows/ci.yml` | tests on every push |
| `experiments/` | eSpeak / Piper / Kokoro comparisons, not product code |

## Security and privacy

- Bot token only in `bot/.env` (ignored by git); `ALLOWED_USER_IDS` gates every handler.
- Input caps: 2 MB text, 20 MB PDF, 300 pages, 60,000 characters.
- Mini App sends no text anywhere; it only downloads the model and libraries from Hugging Face and jsDelivr.
  (Not yet verified with a network trace; see docs/tasks/T-03.)

## Operational notes

- The bot works only while the owner's PC is on and `python bot/bot.py` is running (long polling, no open ports).
- Synthesis jobs run one at a time (a lock); extra jobs queue.
