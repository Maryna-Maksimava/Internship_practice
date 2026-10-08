# T-02 Start playback before generation finishes

**Goal.** The user hears the first sentence within seconds, even when generation is slower than real time.

**Context.** The Mini App generates all chunks, builds one WAV, then plays. On a slow phone that means minutes of silence.
Chunk start times are already tracked for highlighting (`marks` in the generate handler).

**Scope.** In: play each chunk via Web Audio (`AudioContext`, scheduled buffers) as soon as it is ready; keep highlight
and click-to-seek working; keep the final WAV download. Out: changing the model or text rules.

**Files.** `miniapp/index.html` (`go` handler, `buildReader`, `syncReader`).

**Acceptance.**
- First audio starts after the first chunk, not after the last.
- If generation is slower than playback, playback pauses and resumes without glitches or a lost position.
- Highlight stays within 0.5 s of the audio. The final WAV is identical in length to before.

**Verify.** Desktop WASM backend (slow): time to first sound under 10 s for the demo text; manual listen.
