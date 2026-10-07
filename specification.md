# Specification: Kokoro Reader

## 1. Goal

Convert text documents into natural-sounding audio using only free, open-source tools, with synthesis running on the end user's device (no paid APIs, no server compute cost). Delivered through a Telegram Mini App.

## 2. Non-goals

- Voice cloning, SSML, or multi-speaker dialogue.
- Non-English languages (Kokoro support is limited; revisit later).
- Hosting an always-on synthesis server (kept only as a fallback, see 7).

## 3. Users and use cases

- A user opens the Telegram bot, taps a button, picks a file, and listens to or saves the generated audio.
- Primary inputs: `.txt`, `.md`. Later: `.pdf`, `.epub`, `.docx`.

## 4. Architecture

```
Telegram bot (Python)  --button-->  Mini App (static HTML/JS, HTTPS)
                                        |
                                  kokoro-js (ONNX Runtime Web)
                                  WebGPU (fp32) or WASM (q8)
                                        |
                                  WAV/MP3 in browser -> play / download / share
```

- **miniapp/**: single static page, no backend. Loads `kokoro-js` from a CDN and the model `onnx-community/Kokoro-82M-v1.0-ONNX` from Hugging Face; the browser caches it.
- **bot/**: minimal `python-telegram-bot` service. Replies to `/start` with a WebApp button pointing to `MINIAPP_URL`. Restricts access to `ALLOWED_USER_IDS`.
- **experiments/**: throwaway comparisons; not part of the product.

## 5. Functional requirements

| ID | Requirement | Status |
|---|---|---|
| F1 | Load text from file picker or paste | Done (.txt/.md) |
| F2 | Choose voice from a fixed list | Done |
| F3 | Split text into sentence-sized chunks (<=300 chars) and synthesize sequentially | Done |
| F4 | Show progress and real-time factor | Done |
| F5 | Play result and offer WAV download | Done |
| F6 | Speed control | Todo |
| F7 | PDF / EPUB / DOCX text extraction | Todo |
| F8 | MP3/Opus encoding to shrink output | Todo |
| F9 | Telegram bot with WebApp button and allowlist | Todo |
| F10 | Resume/cancel long jobs; avoid losing work when the app is backgrounded | Todo |

## 6. Non-functional requirements

- **Cost:** zero ongoing; static hosting only.
- **Privacy:** user text never leaves the device.
- **Performance target:** at least real time on a mid-range phone with WebGPU; WASM fallback may be slower. Measured so far: 1.4x real time on a desktop browser with WebGPU.
- **Size:** first-run model download of roughly 80-330 MB depending on quantization; must be cached and the user warned about mobile data.
- **Security:** bot token only in `bot/.env`; never committed; allowlist of user IDs.

## 7. Risks and open questions

- WebGPU availability inside Telegram's in-app browser varies by device and OS; WASM fallback may be too slow or run out of memory on older phones. **Needs a real phone test.**
- Mobile browsers suspend background tabs, so long jobs may stall.
- Getting audio back into a chat requires the user to save/share manually, since the Mini App cannot post files as the user.
- Fallback if on-device is impractical: server-side synthesis in the bot (Kokoro via `kokoro-onnx`, about 3x real time on a desktop CPU), with queueing, file-size caps (Telegram bot upload limit 50 MB) and ffmpeg conversion.

## 8. Milestones

1. Prototype Mini App on desktop. **Done.**
2. Host over HTTPS and test on a real phone.
3. Bot with WebApp button and allowlist.
4. Document extraction (PDF/EPUB), speed control, compressed output.
5. Decide: ship on-device only, or add the server fallback.

## 9. Licensing notes

Kokoro-82M is Apache 2.0. Piper voices carry individual licences; check before redistributing. eSpeak NG is GPL-3 and is used only in local experiments.
