# Paid and cloud resources: removal or continuation plan

## Inventory

The project uses **no paid cloud resources**. Everything is free-tier or local.

| Resource | Cost | Holds | Owner |
|---|---|---|---|
| GitHub repository `Maryna-Maksimava/Internship_practice` | free (public) | code, docs, evals | project owner |
| GitHub Pages (serves `miniapp/`) | free | static page only | project owner |
| GitHub Actions (CI) | free for public repos | no data; logs of runs | project owner |
| Telegram bot (via BotFather) | free | bot token (secret) | project owner |
| Hugging Face / jsDelivr / GitHub releases | free downloads | model and libraries, fetched by users | third parties |
| Owner's PC | already owned | runs the bot, holds `models/` (about 400 MB) and `bot/.env` | project owner |

Not used: any VPS, cloud GPU, paid TTS API (ElevenLabs, Azure, OpenAI), database, domain name, or storage bucket.

## If the project is stopped (shutdown checklist)

1. **Stop the bot:** close the `python bot/bot.py` terminal.
2. **Revoke the bot token:** BotFather, `/mybots`, select the bot, API Token, Revoke. Or delete the bot with `/deletebot`.
   Then delete `bot/.env` locally.
3. **Take down the Mini App:** repo Settings, Pages, Unpublish (or set Source to None). The URL stops working.
4. **Optional:** make the repo private or archive it (Settings, General). Archiving keeps the code for the report.
5. **Optional local cleanup:** delete `models/`, `output/`, and the Hugging Face cache (`~/.cache/huggingface`) to free disk.

## If the project continues

- Free path (recommended): nothing to do. Pages and CI keep running at no cost; the bot runs on demand on the PC.
- Always-on bot: the only paid option considered is a small VPS (about a few dollars a month, 2 GB RAM). It would be
  slower than the owner's PC for synthesis and is **not** needed: the Mini App already gives on-device synthesis.
  If ever added: set a billing alert, keep the token in the server's environment (not in git), shut down when idle.
- Secrets hygiene: the token lives only in `bot/.env` (git-ignored). Rotate it with BotFather if it is ever shared.

## Decision

No paid resources exist, so there is nothing to delete for cost reasons. Free resources stay up until the owner
unpublishes them (steps 1-3 above).
