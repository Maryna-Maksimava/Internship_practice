# Evidence of individual contribution

Project owner: **Maryna Maksimava** (GitHub: `Maryna-Maksimava`). Supervisor / course / period: *Sergei Audeychik*.
The code was written with an AI coding agent (Claude Code); this page separates what the owner did from what the
agent did. See also [agent-human-roles.md](agent-human-roles.md) and [agent-worklog.md](agent-worklog.md).

## Verifiable in the repository

- Repository: https://github.com/Maryna-Maksimava/Internship_practice, commits authored under the owner's account
  (`git log --format='%an %ad %s'`). Commits made with the agent carry a `Co-Authored-By` trailer.
- GitHub Pages deployment and the CI configuration run under the owner's account (Actions tab, Pages settings).
- The Telegram bot is registered by the owner with BotFather; the token exists only in the owner's `bot/.env`.

## What the owner did

| Area | Contribution |
|---|---|
| Direction | set the goal (natural, free, fast document narration), proposed Telegram delivery and on-device computation, asked for PDF, line-break pauses, sentence highlight, progress bar |
| Decisions | rejected eSpeak after hearing it; chose Piper then Kokoro by ear; accepted WASM on phones; chose the hybrid project type; decided the project passport scope |
| Infrastructure | installed eSpeak NG; connected the git remote and pushed; enabled GitHub Pages; created the Telegram bot and token; found their own Telegram user ID and configured `.env` |
| Testing on real devices | ran the Mini App on the phone and reported garbled sound and slowness; ran the bot and reported the missing button |
| Bug finding | screeching on the phone; huge pause on "7:30"; no pause after "Chapter 1"; red CI run |
| Evaluation | listened to and rated 24 blinded clips (naturalness, odd pause, misread) |
| Review | reviewed and approved each commit and push; asked for documents and artifacts |

## What the agent did

Wrote and refactored the code (Mini App, bot, PDF handling, text preparation), the tests and CI, the demo, the eval
harness and metrics, and drafted all documents; ran tests and scripted browser checks; reported measured numbers
and what could not be verified.

## Fill in before submission

- Name, group, supervisor, dates of the practice.
- A short personal statement of what you learned and which decisions were yours.
- Optional: your own screenshots of the phone test and the Telegram chat as additional evidence.
