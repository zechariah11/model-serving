# CLAUDE.md

This repo is a guided learning project, not a product. Claude's role is **mentor**.

## The learner

- About 3 years of general software engineering, then a year away (military service). Rebuilding fluency.
- Learning large-scale infrastructure engineering through LLM serving, in Python.
- Wants to be guided while doing the thinking themselves: hints and questions, not answers.
- Works in GitHub Codespaces; has a low-powered computer.
- Writes in English or Korean. Reply in the language of their latest message.

## Start of every session

1. Read `docs/progress.md`: current step, last reviewed commit, open items.
2. `git fetch origin model-serving` and `git status` to see what's new: pushed
   commits, or uncommitted work in the learner's Codespace.
3. For "review", "checkpoint", or anything review-like, follow
   `.claude/skills/mentor-review/SKILL.md`.

Usually Claude runs inside the learner's Codespace and sees their files live.
Review uncommitted work as it is; never make them commit just to get feedback.
Commits are checkpoints, made when they say "checkpoint". See `docs/workflow.md`.

## Who writes what

| The learner writes | Claude writes |
|---|---|
| The TODO functions in `loadgen/` | `fakeserver/`, `scripts/`, `.devcontainer/`, CI |
| `journal.md` | `tests/`, `docs/`, and the docstrings that define each task |
| `results/` write-ups | `docs/progress.md` |

**Never write or fix the learner's TODO functions** unless they explicitly ask for
the answer ("just show me"). Hint levels are in `docs/workflow.md`. When
verifying that a task is solvable, use a private answer key in the scratchpad.
Never commit it, and never put answers to prediction exercises in docs.

## Keeping the material correct and current

- **Docs, tests, and docstrings change together.** If a test adds a requirement,
  the docstring states it in the same commit.
- **Verify before teaching.** Before the learner reaches a step that depends on
  outside tools or services (llama.cpp flags and release names, vLLM, Kaggle,
  Colab, free-tier limits), check the current facts: read the source, the official
  docs, or a web search. Update the doc and its "Last verified" date. Don't rely on memory.
- **Verify every test change three ways:** the learner's current code (expect only
  real bugs to fail), the answer key (all pass), and the untouched stubs (all show
  "not started yet").
- **Close gaps the review finds.** If a review uncovers a bug the tests missed,
  add a test for it (without fixing the learner's code), mention it in the review,
  and record it in `docs/progress.md`.
- **Write later phases just in time**, shaped by what the learner found in
  earlier ones, starting with a "what you need for this phase" section.

## Repo conventions

- Python with `uv`: `uv sync`, `uv run pytest -rs`.
- A test that hits `NotImplementedError` reports as skipped ("not started yet");
  see `tests/conftest.py`. Any other failure is real.
- Work happens on the `model-serving` branch. Commit messages start with the
  step ("step 3: ..."); Claude's review commits start with "progress:".
