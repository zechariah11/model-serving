# Working with Claude

Claude runs **inside your Codespace**, next to your code. It sees your files as
you save them, so getting feedback takes no commits, no pushes, and no
copy-pasting.

## One-time setup (5 minutes)

1. **Rebuild your Codespace** so it picks up Claude Code: open the Command
   Palette (`Ctrl+Shift+P`, or `Cmd+Shift+P` on a Mac), then run
   **Codespaces: Rebuild Container**. A brand-new Codespace has it already.
2. **Sign in once:** open the terminal, run `claude`, and follow the browser
   prompt. If the browser finishes but the terminal keeps waiting, copy the code
   the browser shows and paste it into the terminal.

You can then use Claude either from the **Claude Code panel** in the editor
(look for the Claude icon in the sidebar) or by typing `claude` in a terminal.

Your sign-in survives stopping and starting the Codespace. A rebuild clears it,
so sign in again after one. To skip that, run `claude setup-token` and save the
token as a [Codespaces secret](https://github.com/settings/codespaces) named
`CLAUDE_CODE_OAUTH_TOKEN`.

## The loop

Keep two things open:

```
┌─ terminal: test watcher ────────────┐  ┌─ Claude panel ──────────────────┐
│ uv run ptw .                        │  │ you: review                     │
│                                     │  │ Claude: Status / What's good /  │
│ reruns the tests every time you     │  │   Issues (hints) / Think about /│
│ save a file                         │  │   Next                          │
└─────────────────────────────────────┘  └─────────────────────────────────┘
```

1. Start the watcher once: `uv run ptw .` It reruns the tests on every save, so
   you see red/green within seconds.
2. Work on the step. Save often.
3. When you want feedback, type **"review"** in the Claude panel. Claude reads
   what you have right now, saved but not committed, runs the tests, and replies.
4. Ask anything in between: "why is this test failing?", "explain asyncio.gather",
   "is my journal answer right?". It already knows which step you're on.

## When to commit

Commits become **checkpoints**, not a messaging system:

- **When a step is done,** say "checkpoint step 3". Claude commits your work with
  a clear message, updates `docs/progress.md`, and pushes. CI then confirms it
  on GitHub.
- **Before you stop for the day,** so your work is saved off the Codespace.

You can still commit by hand any time. Practicing git is worthwhile.

## What a review looks like

- **Status:** what passes, what's next
- **What's good:** specific things you did well
- **Issues:** bugs or gaps, each with a hint, not a fix
- **Think about:** one question that pushes your understanding further
- **Next:** what to do now

Claude also keeps [`progress.md`](progress.md) current, so any session, in any
Codespace or on claude.ai, picks up where you left off.

## How hints work

You decide how much help you get. Claude starts at the first level and only goes
further if you ask:

| Level | You get | Ask with |
|---|---|---|
| 1. Nudge | A question that points at the problem | (default) |
| 2. Pointer | Which line, and which concept to look up | "more of a hint" |
| 3. Example | The same idea shown on a *different* problem | "show me an example" |
| 4. Answer | The fix for your code, explained | "just show me" |

Use level 4 when you're truly stuck or short on time, not as a habit. It's fine
to use it; the point is that it's your choice.

## CI: a second opinion on every push

GitHub runs the tests on every push (the ✓/✗ next to each commit, or the
**Actions** tab). Green means everything you've started passes; skipped tests
are steps you haven't reached. Red means something you wrote fails.

## Other ways to work

- **From claude.ai or the Claude app, without a Codespace:** commit and push,
  then say "review". Claude pulls your latest commits instead of reading live files.
- **Pull requests, for line-by-line comments** (the way most teams review code):
  `git switch -c step-4`, commit, `git push -u origin step-4`, open a PR into
  `model-serving`, then say "review my PR".

## If something goes wrong

| Problem | Fix |
|---|---|
| The `claude` command isn't found | The Codespace was created before this setup. Rebuild it (setup step 1). |
| `git push` is rejected ("fetch first") | Run `git pull`, then `git push`. |
| A merge conflict in `docs/progress.md` | Take the incoming version: `git checkout --theirs docs/progress.md`, then commit. |
| Tests changed and something you'd finished is red | Claude added a test for a case you missed. The review will say which, and why. |
