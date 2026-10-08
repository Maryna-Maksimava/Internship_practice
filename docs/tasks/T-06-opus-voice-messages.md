# T-06 Opus output as Telegram voice messages

**Goal.** Bot replies play inline in Telegram (voice-message style) instead of arriving as a downloaded `.ogg` document.

**Context.** The bot writes Ogg *Vorbis* and sends a document. Telegram's voice messages need Ogg *Opus*
(`send_voice`); long audio also hits the 50 MB bot upload limit only with very long texts.

**Scope.** In: encode Opus (libsndfile `OPUS` subtype if available, else ffmpeg); use `send_voice` up to a safe length and
split longer audio into parts of about 20 minutes. Out: MP3.

**Files.** `bot/tts.py` (`_encode_ogg`), `bot/bot.py` (`run_job` reply).

**Acceptance.** A 30-second and a 25-minute text both arrive and play inline; size per part under 50 MB; fallback to
document if Opus encoding is unavailable. Test with the demo sample.
