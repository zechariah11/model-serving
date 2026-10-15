---
name: mentor-review
description: Review the learner's latest pushed work on the current step of this learning project, give mentor-style feedback (hints, not fixes), and update docs/progress.md. Use when the learner says "review", "check my work", "I pushed", "feedback", or similar.
---

# Mentor review

You are reviewing a learner's work, not shipping code. The goal is understanding:
point at problems and ask questions, and leave the fixing to them.

## 1. Sync and scope

```bash
git fetch origin model-serving
git status -sb
```

- If the local branch is behind and has no local changes, `git merge --ff-only origin/model-serving`.
- Read `docs/progress.md` for the current step, the last reviewed commit, and open items.
- Scope = `git log --oneline <last reviewed>..HEAD` and `git diff <last reviewed>..HEAD`.
- If the learner names a pull request instead, review that PR's diff and comment
  on GitHub, with the same rules.
- If nothing is new, say so and ask what they'd like help with.

## 2. Run the tests

```bash
uv run pytest -rs
```

Note which steps pass, fail, or are "not started yet". A failure in a step marked
done in `progress.md` is the top item.

## 3. Read the work

- The learner's code in `loadgen/` for the current step, against its docstring
  and the step in `docs/phase-1.md` (or the current phase's guide).
- Their `journal.md` answers for the step. Check the reasoning, not just the conclusion.
- Look for bugs the tests miss. Try edge cases in the scratchpad (empty input,
  None, a single item, errors, timing boundaries). Don't edit the learner's files.

## 4. Write the feedback

Use this shape, in the learner's language:

- **Status:** tests passing / failing / not started; which step they're on.
- **What's good:** 1–3 specific things (name the line or the idea; skip generic praise).
- **Issues:** each one with how severe it is and a *level-1 hint* (a question or a
  pointer to a concept), not the fix. Show a failing input if that's the clearest
  hint. Escalate only when they ask (levels in `docs/workflow.md`).
- **Think about:** one question that deepens the step's concept: a "what if", a
  connection to production systems, or a prediction to check.
- **Next:** the concrete next action.

For journal answers: if the reasoning has a gap, give them a case to try that
exposes it, instead of correcting them outright.

## 5. Close gaps in the material

If you found a bug the tests don't catch:
- Add a test in `tests/` (without fixing their code). If it adds a requirement,
  state it in the docstring too.
- Verify the test three ways: the learner's code fails it, the scratchpad answer
  key passes it, and the untouched stubs report it as "not started yet".
- Mention the new test in the feedback.

If a doc was unclear or wrong, fix it in the same commit.

## 6. Update progress and push

Edit `docs/progress.md`: current step, last reviewed commit (the learner's latest),
open items checked off or added, strengths noticed, and a new row in History.

```bash
git add docs/progress.md tests/ docs/ loadgen/*.py   # loadgen only for docstring changes
git commit -m "progress: review step N"
git push origin model-serving
```

Tell the learner to `git pull` before continuing.
