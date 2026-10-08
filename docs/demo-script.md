# Demo script (5-7 minutes)

Goal: show that a document goes in and natural speech comes out, that it was measured, and where it falls short.
Say the sentences in quotes; the rest are actions. Prepare everything the evening before.

## Before you start (5 minutes of prep)

- Bot running: `python bot/bot.py` in a terminal, PC awake and on power, model files in `models/`.
- Phone: Telegram open on the bot chat; Mini App page opened once so the model is cached.
- Laptop browser tabs: the repo on GitHub (Actions tab visible), the Mini App page, `docs/evidence.md`.
- Backup in case something fails live: `output/demo.ogg` (made by `python demo/run_demo.py`) and a screen recording.
- Files ready: `demo/sample.md` and one small text PDF with a "Chapter 1" heading and a time like "7:30".

## Script

| Time | Action | Say |
|---|---|---|
| 0:00 | Slide 1-2: problem and idea | "Reading long documents is tiring. I wanted to listen to them, for free, with a voice that does not sound like a robot." |
| 0:45 | Slide 3: how it works | "Two paths: a Telegram bot on my PC, and a Mini App that runs the model on the user's own device, so text never leaves it." |
| 1:30 | Terminal: `python demo/run_demo.py` | "Document in, speech out, the same code the bot uses. 30 seconds of audio, about three times faster than real time." Play `output/demo.ogg`. |
| 2:30 | Browser: Mini App, upload `demo/sample.md`, Generate | "Pauses at the heading, no pause on 7:30, and the current sentence is highlighted. Click a sentence to jump." |
| 3:30 | Phone: send the PDF to the bot | "Progress bar while it works, then the audio comes back as a file. Only my Telegram ID is allowed." |
| 4:30 | Slide: evaluation table (or `evals/results/results.md`) | "I compared four systems. Kokoro is the most natural by blind listening, 5 out of 5 against 3.2 for Piper and 1 for eSpeak. Text preparation cut errors on times from 17 to 2 percent." |
| 5:30 | Slide: limitations | "What does not work yet: speed on the phone is slow, only English, no OCR, and the quality rating comes from one listener." |
| 6:15 | GitHub Actions tab | "Tests run on every push, both checks are green." |
| 6:30 | Questions | |

## Likely questions and honest answers

- *Why not a cloud API?* The goal was free and private; cloud TTS costs money and sends text away.
- *Why is the phone slow?* On a phone the browser runs on WASM; WebGPU produced garbled audio there. Streaming playback and multi-threading are the next tasks (T-01, T-02).
- *Did you write the code yourself?* It was written with an AI agent; I set the goals, decided, tested on devices and rated the audio. See `docs/contribution.md`.
- *Is the 5.0 reliable?* It is one listener, six clips per system, blinded. It is a signal, not statistics.
- *Does it cost anything to keep?* No paid resources; see `docs/cloud-resources.md`.

## If something breaks live

| Failure | Do |
|---|---|
| Bot silent | check the terminal for errors; fall back to `output/demo.ogg` and the Mini App |
| Mini App slow on phone | show the desktop browser; mention WASM vs WebGPU |
| No internet for the model download | use the laptop tab that already has the model cached |
