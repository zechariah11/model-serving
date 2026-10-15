# Working with Claude: push, get feedback, keep going

## The daily loop

```bash
git pull                      # 1. get any test or doc updates and review notes
# 2. work on the current step
uv run pytest -rs             # 3. check it
git add -A
git commit -m "step 3: answer stream questions"   # 4. start the message with the step
git push                      # 5. push
```

6. In a Claude Code session on this repo, say **"review"** (or run `/mentor-review`).

That's it. You don't need to paste code or explain what changed.

## What happens when you ask for a review

Claude will:
1. Pull your latest commits and look at everything since the last review.
2. Run the tests and note what's passing, failing, or not started.
3. Read your code *and* your journal answers.
4. Try edge cases the tests don't cover, without fixing your code.
5. Reply in chat in this shape:
   - **Status:** what passes, what's next
   - **What's good:** specific things you did well
   - **Issues:** bugs or gaps, each with a hint, not a fix
   - **Think about:** one question that pushes your understanding further
   - **Next:** what to do now
6. Update [`progress.md`](progress.md) with where you are and what's still open,
   and push that. (That's why step 1 of the loop is `git pull`.)

Any new session reads `progress.md` first, so you can pick up from any session
without re-explaining.

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

## CI: feedback on every push

GitHub runs the tests on every push (see the **Actions** tab, or the ✓/✗ next to
each commit):

- **Green:** everything you've started passes. Tests for steps you haven't
  reached show as skipped.
- **Red:** something you wrote fails. Click into the run to see which test.

## Optional: pull requests for line-by-line feedback

If you'd rather get comments on specific lines, the way code review works at most jobs:

```bash
git switch -c step-4
# work, commit
git push -u origin step-4
```

Open a pull request from `step-4` into `model-serving` on GitHub, then tell Claude
"review my PR". The comments appear on the PR, CI shows on it, and you merge it
when you're happy. It's a little more ceremony, but it's real practice for how
teams work.

## If something goes wrong

| Problem | Fix |
|---|---|
| `git push` is rejected ("fetch first") | Claude pushed review notes. Run `git pull`, then `git push`. |
| A merge conflict in `docs/progress.md` | Take Claude's version: `git checkout --theirs docs/progress.md`, then commit. |
| Tests changed and something you'd finished is red | Claude added a test for a case you missed. The review will say which, and why. |
