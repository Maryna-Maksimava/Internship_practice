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
import threading

from dotenv import load_dotenv
from pdf_text import pdf_to_text
from tts import synthesize
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

synth_lock = asyncio.Lock()  # one job at a time; the CPU is the bottleneck


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
