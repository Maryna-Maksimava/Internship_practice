# AGENTS.md

Instructions for AI coding agents (Claude Code, Codex, Copilot, etc.) working in this repo.
Humans: see README.md; roles are described in docs/agent-human-roles.md.

## What this project is

Kokoro Reader: text documents (.txt/.md/.pdf) -> natural speech with the open Kokoro-82M model.
Two front ends share one idea: `miniapp/` (runs in the browser or as a Telegram Mini App, synthesis
on the user's device) and `bot/` (Telegram bot, synthesis on the owner's PC). Architecture: docs/architecture.md.

## Commands

```bash
pip install -r requirements.txt
python -m pytest tests -q            # Python tests (model smoke test auto-skips without models/)
node tests/miniapp.test.mjs          # Mini App text-logic tests
python demo/run_demo.py              # end-to-end demo -> output/demo.ogg (needs models/)
python bot/bot.py                    # run the bot (needs bot/.env)
python -m http.server 8765 --directory miniapp   # serve the Mini App locally
```

Models are not in git. Download steps: README.md "Quick start".

## Layout rules

- `bot/textproc.py`, `bot/pdf_text.py`: pure text logic. No network, no model, no Telegram imports. Keep them that way so CI can test them.
- `bot/tts.py`: synthesis shared by bot and demo. `bot/bot.py`: Telegram glue only.
- `miniapp/index.html`: single static file, no build step. Its `normalize()` and `sentences()` must behave like `textproc.normalize()` / `textproc.chunks()`; `tests/miniapp.test.mjs` and `tests/test_textproc.py` share the same golden cases. Change both together.
- `experiments/`: throwaway comparisons, not product code. Do not build on them.

## Do

- Run both test commands before saying a change works. Report failures with their output.
- Add a golden test case for every text-handling bug you fix (times, headings, pauses).
- Verify audio claims with numbers (audio seconds / wall seconds), not by assuming. An agent cannot hear: say so and ask the human to listen.
- Prefer small commits that touch only the files you changed. Stage files by name.

## Do not

- Never read, print, or commit `bot/.env` or any token. `.env` is git-ignored; only `.env.example` is tracked.
- Never commit models, audio (`*.onnx`, `*.wav`, `*.ogg`, `voices-*.bin`) or build outputs.
- Never push, force-push, or change GitHub Pages / repo settings without the human asking.
- Do not make the bot public: access is limited by `ALLOWED_USER_IDS`.
- Do not add paid or cloud TTS services; the project's constraint is free and local.

## Known traps (each cost real debugging time)

- Windows threads have small stacks: onnxruntime and libsndfile's Vorbis encoder overflow them (`0xC00000FD`). Keep the big-stack handling in `bot/tts.py` and `bot/bot.py`.
- Kokoro reads `:` as a long pause, so times like `7:30` are rewritten (`textproc.normalize`).
- WebGPU fp32 produced garbled audio on the owner's phone; Mini App defaults to WASM on mobile.
- PDF text is hard-wrapped: wrapped lines must be joined and headings kept on their own line, otherwise pauses land on every line.
- Edit tools and git on Windows convert line endings; CI runs on Linux. Do not rely on `\r\n`.

## Where things are tracked

Requirements and status: specification.md. Task briefs: docs/tasks/. Known limitations: docs/limitations.md.
