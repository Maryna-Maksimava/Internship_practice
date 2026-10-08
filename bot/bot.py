"""Telegram bot for Kokoro Reader.

- /start: button that opens the on-device Mini App (MINIAPP_URL).
- Send a .txt/.md/.pdf file (or plain text): the bot synthesizes it on THIS machine
  with Kokoro and replies with an audio file.
- /voice <name>, /speed <0.5-2.0>, /pause <seconds>: per-user settings.

Run:  python bot/bot.py   (reads bot/.env, see bot/.env.example)
"""
import asyncio
import io
import os
import pathlib
import re
import threading

import numpy as np
import soundfile as sf
from dotenv import load_dotenv
from kokoro_onnx import Kokoro
from pdf_text import pdf_to_text
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Kokoro/onnxruntime overflow the small default stack of worker threads on Windows
# (synthesis runs in asyncio.to_thread). Must be set before any thread is created.
threading.stack_size(64 * 1024 * 1024)

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
load_dotenv(HERE / ".env")

TOKEN = os.environ["BOT_TOKEN"]
MINIAPP_URL = os.environ.get("MINIAPP_URL", "")
ALLOWED = {int(x) for x in os.environ.get("ALLOWED_USER_IDS", "").split(",") if x.strip()}
MAX_FILE_BYTES = 2 * 1024 * 1024   # input size cap (text)
MAX_PDF_BYTES = 20 * 1024 * 1024   # Telegram lets bots download up to 20 MB
MAX_CHARS = 60_000                 # ~1 hour of audio; protects your CPU
VOICES = ["af_heart", "af_bella", "af_nicole", "am_michael", "am_adam", "bf_emma", "bm_george"]
DEFAULTS = {"voice": "af_heart", "speed": 1.0, "pause": 0.7}

kokoro = Kokoro(str(ROOT / "models" / "kokoro-v1.0.onnx"), str(ROOT / "models" / "voices-v1.0.bin"))
synth_lock = asyncio.Lock()  # one job at a time; the CPU is the bottleneck


_TIME = re.compile(r"(?<![\d:.])(\d{1,2}):([0-5]\d)(?![\d:])")


def _say_time(m: re.Match) -> str:
    h, mi = m.group(1), m.group(2)
    if mi == "00":
        return f"{h} o'clock"
    return f"{h} oh {int(mi)}" if mi[0] == "0" else f"{h} {mi}"


def normalize(text: str) -> str:
    """Kokoro treats ':' as a long pause, so '7:30' becomes '7 30' (read 'seven thirty')."""
    return _TIME.sub(_say_time, text)


def chunks(text: str):
    """Yield (sentence_group, pause_multiplier). 1 after a line break, 2 after a blank line."""
    out, blank = [], 0
    for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if not line.strip():
            blank += 1
            continue
        if out:
            out[-1][1] = 2 if blank else 1
        blank = 0
        cur = ""
        for s in re.findall(r"[^.!?]+[.!?]*\s*", re.sub(r"\s+", " ", line)):
            if len(cur + s) > 300 and cur:
                out.append([cur, 0])
                cur = s
            else:
                cur += s
        if cur.strip():
            out.append([cur, 0])
    return out


def synthesize(text: str, voice: str, speed: float, pause: float, on_progress=None) -> bytes:
    parts, sr = [], 24000
    pieces = chunks(normalize(text))
    for i, (sentence, mult) in enumerate(pieces):
        samples, sr = kokoro.create(sentence, voice=voice, speed=speed, lang="en-us")
        parts.append(samples)
        if mult and pause:
            parts.append(np.zeros(int(sr * pause * mult), dtype=np.float32))
        if on_progress:
            on_progress(i + 1, len(pieces))
    buf = io.BytesIO()
    sf.write(buf, np.concatenate(parts), sr, format="OGG", subtype="VORBIS")
    return buf.getvalue()


def bar(done: int, total: int, width: int = 20) -> str:
    filled = round(width * done / total)
    return f"[{'█' * filled}{'░' * (width - filled)}] {100 * done // total}% ({done}/{total})"


def settings(ctx: ContextTypes.DEFAULT_TYPE) -> dict:
    return ctx.user_data.setdefault("s", dict(DEFAULTS))


async def allowed(update: Update) -> bool:
    uid = update.effective_user.id
    if uid in ALLOWED:
        return True
    await update.effective_message.reply_text(f"Not authorised. Your user ID is {uid}.")
    return False


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await allowed(update):
        return
    rows = []
    if MINIAPP_URL:
        rows.append([InlineKeyboardButton("Read on my device", web_app=WebAppInfo(url=MINIAPP_URL))])
    await update.message.reply_text(
        "Send me a .txt, .md or .pdf file (or paste text) and I'll turn it into audio on the server.\n"
        "Or open the Mini App to generate on your own phone.\n\n"
        "/voice <name>  /speed <0.5-2>  /pause <seconds>\n"
        "Voices: " + ", ".join(VOICES),
        reply_markup=InlineKeyboardMarkup(rows) if rows else None,
    )


async def set_voice(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await allowed(update):
        return
    v = ctx.args[0] if ctx.args else ""
    if v not in VOICES:
        await update.message.reply_text("Choose one of: " + ", ".join(VOICES))
        return
    settings(ctx)["voice"] = v
    await update.message.reply_text(f"Voice set to {v}.")


def num_setting(key, lo, hi):
    async def handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if not await allowed(update):
            return
        try:
            val = float(ctx.args[0])
            assert lo <= val <= hi
        except (IndexError, ValueError, AssertionError):
            await update.message.reply_text(f"Usage: /{key} <{lo}-{hi}>")
            return
        settings(ctx)[key] = val
        await update.message.reply_text(f"{key} set to {val}.")
    return handler


async def run_job(update: Update, ctx: ContextTypes.DEFAULT_TYPE, text: str, name: str):
    text = text.strip()
    if not text:
        await update.message.reply_text("That file has no text.")
        return
    if len(text) > MAX_CHARS:
        await update.message.reply_text(f"Too long ({len(text):,} chars; limit {MAX_CHARS:,}).")
        return
    s = settings(ctx)
    status = await update.message.reply_text(
        f"Queued ({len(text):,} chars, voice {s['voice']}). Waiting for the current job…"
        if synth_lock.locked() else "Starting…"
    )
    progress = {"done": 0, "total": 0}
    finished = asyncio.Event()

    async def updater():
        shown = None
        while not finished.is_set():
            try:
                await asyncio.wait_for(finished.wait(), timeout=3)  # Telegram rate-limits edits
            except asyncio.TimeoutError:
                pass
            if finished.is_set():
                break
            if progress["total"] and (progress["done"], progress["total"]) != shown:
                shown = (progress["done"], progress["total"])
                try:
                    await status.edit_text("Generating " + bar(*shown))
                except Exception:
                    pass  # e.g. "message is not modified" or a flood-wait; skip this tick

    task = asyncio.create_task(updater())
    try:
        async with synth_lock:
            data = await asyncio.to_thread(
                synthesize, text, s["voice"], s["speed"], s["pause"],
                lambda d, t: progress.update(done=d, total=t),
            )
    finally:
        finished.set()
        await task
    await update.message.reply_document(io.BytesIO(data), filename=f"{name}.ogg", caption="Done.")
    await status.delete()


async def on_document(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await allowed(update):
        return
    doc = update.message.document
    stem, ext = os.path.splitext(doc.file_name or "text")
    ext = ext.lower()
    if ext not in (".txt", ".md", ".pdf"):
        await update.message.reply_text("Only .txt, .md and .pdf files for now.")
        return
    limit = MAX_PDF_BYTES if ext == ".pdf" else MAX_FILE_BYTES
    if doc.file_size and doc.file_size > limit:
        await update.message.reply_text(f"File too large (limit {limit // 1024 // 1024} MB).")
        return
    raw = bytes(await (await doc.get_file()).download_as_bytearray())
    if ext == ".pdf":
        try:
            text = await asyncio.to_thread(pdf_to_text, raw)
        except Exception as e:  # corrupt/encrypted/scanned
            await update.message.reply_text(f"Couldn't read that PDF: {e}")
            return
    else:
        text = raw.decode("utf-8", errors="replace")
    await run_job(update, ctx, text, stem)


async def on_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await allowed(update):
        return
    await run_job(update, ctx, update.message.text, "speech")


def main():
    if not ALLOWED:
        print("Warning: ALLOWED_USER_IDS is empty, so nobody can use the bot. "
              "Message the bot once to see your ID, then add it to bot/.env.")
    app = Application.builder().token(TOKEN).concurrent_updates(True).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("voice", set_voice))
    app.add_handler(CommandHandler("speed", num_setting("speed", 0.5, 2.0)))
    app.add_handler(CommandHandler("pause", num_setting("pause", 0.0, 5.0)))
    app.add_handler(MessageHandler(filters.Document.ALL, on_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    app.run_polling()


if __name__ == "__main__":
    main()
