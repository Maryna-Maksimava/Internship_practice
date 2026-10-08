# Deployment and reproduction guide

Everything below was run on Windows 11 with Python 3.12 and Node 20+. Linux/macOS: same steps, except the
Windows-only parts noted. Nothing here costs money.

## What is deployed

| Part | Where | How it is deployed |
|---|---|---|
| Mini App | https://maryna-maksimava.github.io/Internship_practice/miniapp/ | GitHub Pages, "deploy from branch `main`, root". Every push to `main` republishes it (1-2 minutes) |
| CI | GitHub Actions, `.github/workflows/ci.yml` | runs on every push to `main` and on pull requests |
| Bot | the owner's PC | not deployed anywhere: `python bot/bot.py`, works while the PC is on |

## A. Reproduce the tests (no model needed, 2 minutes)

```bash
git clone https://github.com/Maryna-Maksimava/Internship_practice
cd Internship_practice
pip install pytest pypdf fpdf2 numpy num2words
python -m pytest tests -q          # model smoke test skips without models/
node tests/miniapp.test.mjs
```

Expected: all Python tests pass (the synthesis smoke test is skipped), `miniapp tests passed`.
This is exactly what CI runs.

## B. Reproduce the demo (needs the model, about 400 MB download)

```bash
pip install -r requirements.txt
mkdir -p models
curl -L -o models/kokoro-v1.0.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
curl -L -o models/voices-v1.0.bin  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
python demo/run_demo.py            # writes output/demo.ogg, prints stages and speed
```

Expected: `4. wrote ... output/demo.ogg`, and a speed of roughly 3x real time on a modern desktop CPU.

## C. Reproduce the evaluation

```bash
pip install faster-whisper num2words
python -m piper.download_voices en_US-lessac-medium   # then move the two files into models/
# eSpeak NG baseline: install it (Windows MSI from the espeak-ng releases page); the script finds it automatically
python evals/run_eval.py            # first run downloads Whisper base.en (about 140 MB)
python evals/score_listening.py     # averages the human ratings
```

Results land in `evals/results/`. Numbers vary slightly between machines; WER differences of a few percent on
22 sentences are not significant. Engines that are not installed are skipped.

## D. Run the Mini App locally

```bash
python -m http.server 8765 --directory miniapp
```

Open http://localhost:8765/. First generation downloads the model from Hugging Face (cached afterwards).
WebGPU works on localhost; on a phone you need the HTTPS Pages URL above.

## E. Run the bot

1. In Telegram, message @BotFather, `/newbot`, copy the token.
2. Copy `bot/.env.example` to `bot/.env` and fill in `BOT_TOKEN`. Keep `MINIAPP_URL` as the Pages URL.
3. `python bot/bot.py`, send the bot `/start`: if your ID is not allowed it replies with your ID.
4. Put that ID in `ALLOWED_USER_IDS`, restart the bot, send `/start` again. You should see the Mini App button.
5. Send a `.txt`, `.md` or `.pdf`: progress bar, then an `.ogg` file.

## F. Deploy your own copy of the Mini App

1. Fork or push the repo to your own GitHub account (must be public for free Pages).
2. Settings, Pages, Source: "Deploy from a branch", branch `main`, folder `/ (root)`.
3. The page is at `https://<user>.github.io/<repo>/miniapp/`. Put that in `MINIAPP_URL`.

## Known reproduction caveats

- Windows only: `winsound` playback in `experiments/` and `demo --play`; the 64 MB thread-stack workaround in
  `bot/tts.py` is needed there and harmless elsewhere.
- Not verified: these steps on a clean machine (acceptance criterion 9 in the project passport).
