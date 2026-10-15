# model-serving

A small LLM serving platform, built one phase at a time to learn infrastructure
engineering: performance, scaling, failure, and cost. Think of it as a tiny
version of what model API providers run.

## How we work

- **You write the core logic.** Claude writes the plumbing (configs, setup
  scripts, the fake server, tests), reviews your code, and asks questions.
- **Predict before you measure.** Write your guess in [`journal.md`](journal.md),
  run the experiment, then explain the gap. The gap is where the learning is.
- **Tests define "done"** for each coding step. Start red, make it green.
- **Every phase ends with a short write-up** in `results/`. That's the portfolio.
- **Push, then ask for a review.** Claude pulls your work, runs the tests, and
  replies with hints, not fixes. How it works: [`docs/workflow.md`](docs/workflow.md).
- **Stuck for 30+ minutes?** Ask for a hint and say what you've tried. You choose
  how much help you get.

## Roadmap

| Phase | What you build | What you learn |
|---|---|---|
| **1. One server, measured** | A load generator. Use it on a fake server, then llama.cpp on CPU, then vLLM on a free GPU | Latency vs throughput, queueing, batching |
| 2. Several copies | Your own router in front of 3+ servers | Load balancing, cache-aware routing |
| 3. Watch and scale | Metrics, dashboards, autoscaling on Kubernetes (kind) | Monitoring, latency targets, cold starts |
| 4. Break it | Kill servers, cut the network, fill disks | Failure modes, retries, turning away load |
| 5. Cost | Compare model sizes, batch sizes, machine types | Cost per million tokens |

Phase 1 is laid out in [`docs/phase-1.md`](docs/phase-1.md). Later phases get
written when you reach them, shaped by what you found in the earlier ones.

## Start here

1. Read [`docs/compute.md`](docs/compute.md) to see where this runs for free, and
   [`docs/concepts.md`](docs/concepts.md) for how the pieces fit together.
2. Open a Codespace on the `model-serving` branch: on GitHub, **Code → Codespaces →
   Create codespace on model-serving**. Setup runs by itself.
3. In its terminal, run `uv run pytest -rs`. Tests for work you haven't started
   show as "not started yet". Turning them green is your Phase 1 coding work.
4. Follow [`docs/phase-1.md`](docs/phase-1.md). Where you are right now is in
   [`docs/progress.md`](docs/progress.md).

## Layout

```
loadgen/        the load generator; you fill in client.py, stats.py, run.py
fakeserver/     a fake LLM server with knobs you control (done for you)
tests/          what "correct" means for each step
scripts/        downloads llama.cpp and a small model
docs/           guides, concepts, workflow, and your progress log
results/        your measurements and write-ups
journal.md      predictions vs reality
CLAUDE.md       instructions Claude follows as your mentor
```
