# T-01 Measure and speed up generation on the phone

**Goal.** Know the real speed on the owner's phone and raise it to at least 0.3x real time on WASM
(acceptance criterion 4 in the project passport).

**Context.** WebGPU fp32 gave garbled audio on the phone, so mobile defaults to WASM q8, which is slow
(0.5x on a desktop; the phone is slower). WASM is probably single-threaded because GitHub Pages cannot send
the cross-origin-isolation headers that ONNX Runtime needs for threads.

**Scope.** In: measure; try `coi-serviceworker` for multi-threaded WASM; try WebGPU with fp16 as an opt-in.
Out: server-side changes.

**Files.** `miniapp/index.html` (load(), backend select), possibly a new `miniapp/coi-serviceworker.js`.

**Steps.**
1. Human: open the Mini App on the phone, generate the sample text, write down the log line ("X s of audio in Y s").
2. Agent: add the service worker, reload, check `crossOriginIsolated === true`, repeat the measurement on desktop.
3. Human: repeat on the phone, also inside Telegram's in-app browser.

**Acceptance.** Numbers recorded in specification.md section 6; WASM on the phone >= 0.3x; no regression on desktop.

**Decides.** Human: whether the speed is acceptable. Agent: implementation. Fallback if not: server path (bot).
