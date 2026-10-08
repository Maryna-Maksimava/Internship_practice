# Roles: agent and human

This project was built by a human (the project owner) working with an AI coding agent (Claude Code).
This page says who does what, so that responsibility and review are clear.

## Division of work

| Area | Agent does | Human does |
|---|---|---|
| Direction | proposes options with trade-offs and a recommendation | sets goals, picks the option, changes course |
| Code | writes, refactors, runs tests, fixes bugs it finds | reviews, runs the product, decides what ships |
| Testing | unit and golden tests, scripted browser checks, measures speed | listens to audio, tests on the real phone and with a second Telegram account |
| Documents | drafts passport, architecture, task briefs, limitations | checks facts, fills in what only they know (names, supervisor, deadlines), owns the final wording |
| Accounts and secrets | never reads or prints tokens; asks the human to create the bot, enter the token, set the user ID | creates the bot with BotFather, keeps the token in `bot/.env` |
| Git and publishing | stages named files, commits and pushes only when asked | asks for the commit/push, owns the repository and GitHub Pages settings |
| Quality claims | reports measured numbers and says what was not verified | accepts or rejects against the acceptance criteria |

## What the agent cannot do

- Hear audio. It checks text, numbers and signal statistics; the human must confirm that speech sounds right.
- Use the owner's phone or a second Telegram account.
- Decide product trade-offs or accept its own work.

## Working rules (also in AGENTS.md)

1. The agent asks before anything outward-facing: push, publish, deleting files, changing settings.
2. Every behavior change comes with a test; every claim comes with a number or an honest "not verified".
3. The human reviews diffs before they are pushed to `main`. CI runs on every push as a second check.
4. Mistakes are recorded as golden test cases so they do not return.

## Examples from this project

- The agent chose Kokoro after the human heard eSpeak and rejected it; the human judged Piper and Kokoro by ear.
- The agent found a Windows stack-overflow crash while testing the progress bar and fixed it; the human found the
  garbled phone audio, which led to the WASM default on mobile.
- The agent flagged that the bot token placeholder was still in `.env` only after the human reported a missing button.
