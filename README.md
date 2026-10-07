# Kokoro Reader

Turn text files into natural-sounding speech with the free, open-source [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) model, with a planned Telegram front end where synthesis runs **on the user's own device**.

Status: prototype. See [specification.md](specification.md) for goals and design.

## Layout

```
miniapp/       Static web page: runs Kokoro in the browser (kokoro-js, WebGPU/WASM). Works as a Telegram Mini App.
bot/           Planned Telegram bot that opens the Mini App. .env.example lists its settings.
experiments/   Early TTS comparisons: espeak (C + Python), piper, kokoro (Python, desktop).
models/        Downloaded model files (git-ignored).
output/        Generated audio (git-ignored).
docs/          Extra notes.
```

## Quick start

### Desktop Kokoro test (Python)

```bash
pip install -r requirements.txt
```

Download the model files into `models/`:

```bash
curl -L -o models/kokoro-v1.0.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
curl -L -o models/voices-v1.0.bin  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
```

```bash
python experiments/kokoro/test_kokoro.py af_heart
```

### Mini App (browser)

```bash
python -m http.server 8765 --directory miniapp
```

Open http://localhost:8765/. The model downloads from Hugging Face on first use and is cached by the browser. WebGPU needs HTTPS (localhost is exempt), so testing on a phone requires hosting the page (e.g. GitHub Pages).

### Other experiments

- `experiments/piper/test_piper.py` needs `python -m piper.download_voices en_US-lessac-medium` (then move the files into `models/`).
- `experiments/espeak/` needs eSpeak NG installed and MinGW-w64; see the build line in the file header. It sounds robotic and is kept only for comparison.

## Findings so far

| Engine | Quality | Speed (CPU) |
|---|---|---|
| eSpeak NG | Robotic | Instant |
| Piper (lessac-medium) | Good | Several x real time |
| Kokoro (af_heart) | Best of the free options tried | ~3x real time (desktop), ~1.4x (browser WebGPU) |

## Secrets

The bot token lives in `bot/.env` (git-ignored). Never commit it.
