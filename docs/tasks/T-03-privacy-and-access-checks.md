# T-03 Verify Mini App privacy and the bot allowlist

**Goal.** Turn two "implemented, not verified" acceptance criteria (7 and 8) into verified ones.

**Steps.**
1. Privacy: open the Mini App with DevTools, Network tab, generate; list every host contacted. Expected: only the
   page host (GitHub Pages), jsDelivr (libraries), Hugging Face (model). No request carries the text.
   Record the hosts in docs/architecture.md.
2. Allowlist: from a second Telegram account (not in `ALLOWED_USER_IDS`) send `/start` and a `.txt` file.
   Expected: "Not authorised" and no synthesis.
3. If anything fails, open a fix task with the failing trace.

**Roles.** Human: needs the second account and the phone. Agent: can script the network check in the desktop browser
and add an automated test for the allowlist handler (mock `Update`).

**Acceptance.** Both checks recorded with date and result in specification.md.
