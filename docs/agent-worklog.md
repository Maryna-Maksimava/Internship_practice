# Agent worklog

Reconstructed from the working session with the AI agent (Claude Code), in order. Exact timestamps were not
recorded; the session ran over roughly 2026-10-04 to 2026-10-08. "Human" = the project owner.

## Log

| # | What happened | Who | Result |
|---|---|---|---|
| 1 | Human installed eSpeak NG and asked to build the C "hello world" example | human, agent | agent found no C compiler or headers on the machine; wrote `test-espeak.c`, proved the same API call through Python |
| 2 | Installed MinGW-w64 via winget, downloaded eSpeak headers, compiled and ran the C program | agent (human approved) | worked; human heard audio |
| 3 | Human judged eSpeak quality "absolutely unnatural"; agent explained why (formant synthesis) and offered Piper, Kokoro, cloud | human decides | Piper chosen first |
| 4 | Piper installed, voice `en_US-lessac-medium` downloaded (63 MB) | agent | human: "so much better, even better than Edge read aloud" |
| 5 | Kokoro-82M installed; model 326 MB + voices 28 MB downloaded | agent (human approved) | human: "Amazing"; about 3x real time on CPU |
| 6 | Idea: Telegram bot where synthesis runs on the user's device | human proposes, agent assesses | agent explained a bot cannot run on the phone; proposed a Mini App with `kokoro-js` |
| 7 | Mini App prototype built and tested in the in-app browser | agent | WebGPU 1.4x real time on desktop |
| 8 | Repo structure, `.gitignore`, `README.md`, `specification.md` | agent | human connected the remote and pushed; enabled GitHub Pages |
| 9 | Pause at line breaks added to Mini App | agent | pushed on request |
| 10 | On the phone the sound was garbled | human found | agent defaulted to WASM q8 and added a backend selector; human: sound good, but slow |
| 11 | Telegram bot written (`bot/bot.py`): Mini App button, allowlist, server-side synthesis | agent | human created the bot and token, put the user ID in `.env` |
| 12 | PDF support in bot (pypdf) and Mini App (pdf.js) | agent | tested on generated PDFs |
| 13 | Progress bar in the bot; test crashed with a Windows stack overflow | agent found and fixed | 64 MB thread stack |
| 14 | Human reported: no pause after "Chapter 1", huge pause on "7:30" | human found | agent added heading detection and time normalization in both front ends |
| 15 | Desktop default WebGPU, phone default WASM; sentence highlight with click-to-seek | agent | verified by script in the in-app browser; human to confirm by ear |
| 16 | Project passport (online doc and `docs/passport.docx`) | agent drafts, human reviews | assumptions flagged in a comment |
| 17 | Missing Mini App button in the bot | human reported | agent found the placeholder `MINIAPP_URL` in `bot/.env` and fixed that line only |
| 18 | Architecture doc, `AGENTS.md`, task briefs, demo, CI, tests, limitations, roles | agent | pushed; the first CI run failed |
| 19 | CI failed on invalid YAML (colon in a step name) | human showed screenshot | agent fixed, validated YAML, CI green |
| 20 | Evals: 22-sentence test set, four systems, Whisper round trip, speed, silence metric | agent | first scoring was wrong (formatting artifacts); agent fixed the normalizer and rescored |
| 21 | Listening sheet cut from 88 to 24 clips; human rated all 24 blind | human | Kokoro 5.0, Piper 3.2, eSpeak 1.0 (one rater) |
| 22 | Evidence, reproduction guide, cloud plan, final report, presentation | agent | this batch |
| 23 | Fixed the "St." misreading ("Elm St." to "Elm Street", "St. Louis" to "Saint Louis") in both text-preparation implementations, added golden tests, reran the eval; human ratings left untouched | agent (human asked) | Kokoro WER 1.1% to 0.4%; Piper also moved (2.5% to 1.8%) with no code change, which gives the run-to-run noise (about 1 point); eval script now creates a new rating sheet only with `--new-listening-sheet` |

## Agent mistakes and corrections (kept for honesty)

- Bot first version could crash on Windows (stack overflow in the worker thread); found only while testing the progress bar.
- The `bot/.env` placeholder stayed in place and the Mini App button pointed to a non-existent URL until the human reported it.
- CI workflow shipped with invalid YAML; found by the human on GitHub.
- First WER scoring counted "730" vs "7:30" and "$17" as errors; normalizer fixed and the same transcripts rescored.
- The eval script regenerated the rating sheet on every full run, which would have overwritten the human's ratings; caught before the rerun, now behind a flag.
- A draft sentence claimed Kokoro sounded more natural than Piper, which the human had not compared; replaced by the blind listening result.

## Things the agent could not do

Hear audio, use the phone, create the Telegram bot or its token, create accounts, or decide what ships.
