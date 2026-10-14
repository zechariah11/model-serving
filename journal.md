# Learning journal

The rule: **write the prediction before you run anything.** Then the result. Then
why they differ. Wrong predictions are the useful ones; don't edit them afterward.

## Phase 1

### Step 2 — Why p99 and not the average?



### Step 3 — Looking at the stream

- First chunk:
- What `-N` does:
- A slot, in my own words:

### Step 4 — Timing one request

- Why `perf_counter`:
- Is one chunk one token? How I'd check:

### Step 5 — Closed loop vs open loop



### Step 6 — Fake server (2 slots, 100 ms prefill, 20 ms/token, 50 tokens)

One request on its own takes ____ s, because:

| Concurrency | TTFT p50 predicted | TTFT p50 measured | tok/s predicted | tok/s measured |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 4 | | | | |
| 8 | | | | |

My reasoning:

What surprised me, and why it happened:

### Step 7 — llama-server on CPU (`-np 4`)

| Concurrency | TTFT p50 predicted | TTFT p50 measured | TPOT p50 measured | tok/s predicted | tok/s measured |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| 4 | | | | | |
| 8 | | | | | |

Where the real server stopped matching the fake one, and why:
