# Phase 1: one server, measured

**Goal:** measure how a model server behaves as more users arrive, and be able to
explain *why* it behaves that way.

You'll build a load generator, point it at a fake server whose behavior you can
work out on paper, then at a real model. Most of the learning happens where the
real server stops matching your picture of it.

Rough time: 12–18 hours, spread over two or three weeks.

**Each step has the same parts:**
- **Do:** the task.
- **Check:** the command that tells you it works.
- **Think:** questions to answer in [`journal.md`](../journal.md) before moving on.
- **Go deeper** (optional): how this shows up in production systems, and what to read next.

When you finish a step, push it and ask for a review (see [`workflow.md`](workflow.md)).

## Before you start

You need basic Python (functions, lists, dicts, sorting, dataclasses), a terminal,
git, and the idea of HTTP requests and responses. You do **not** need ML math,
C++, Docker, or Kubernetes. The one new skill is `asyncio`, and you need it from
Step 4. [`concepts.md`](concepts.md) explains how the pieces fit together; read it
once now and come back to it as you go.

## Words you'll use

| Term | Meaning | Why a user cares |
|---|---|---|
| **TTFT** (time to first token) | Time from sending a request to the first word coming back | How long they stare at a blank screen |
| **TPOT** (time per output token) | Average gap between words after the first | How fast the text streams |
| **Latency** | The whole request, start to finish | How long the full answer takes |
| **Throughput** | Tokens per second across *all* users | How many users one machine can serve, and so what it costs |
| **p50 / p99** | Half of requests are faster than p50; 1 in 100 is slower than p99 | p99 is what your unluckiest regular users feel |
| **Concurrency** | Requests in flight at the same moment | The load you're applying |

---

## Step 1 — Set up (15 minutes)

**Do:** open your Codespace (see the [README](../README.md)) and run:

```bash
uv run pytest -rs
```

**Check:** every test shows as `SKIPPED ... not started yet: <function>()`. A
test that needs a function you haven't written yet is reported as skipped, not
failed. Once you write that function, its tests turn green or red for real.

---

## Step 2 — Percentiles (1–2 hours)

**Do:** implement `percentile()` and `summarize()` in [`loadgen/stats.py`](../loadgen/stats.py).
The docstrings say exactly what to compute, including the edge cases.

**Check:** `uv run pytest tests/test_stats.py`

<details><summary>Hint</summary>

`sorted()` returns a new list. `int(pos)` gives the lower index; `pos - int(pos)`
is how far you are toward the next one. Watch out for the last index.

For `summarize()`: decide "is there anything to take a percentile of?" separately
for each list, not once for the whole run.
</details>

**Think:**
- Why do serving teams watch p99 instead of the average? Make up an example where
  the average looks fine but some users are clearly unhappy.
- Percentiles are *positional*: they read the value at a rank. Averages are
  *aggregate*: they add everything up. Look at the two tests named
  `test_one_slow_request_in_100...` and `test_two_slow_requests_in_100...`. What
  does p99 miss, and what does it catch?
- With 32 requests per run, how many slow requests does it take to move p99?
  What does that tell you about trusting p99 from a small run?

<details><summary>Go deeper</summary>

- **You can't average percentiles.** If server A's p99 is 100 ms and server B's is
  300 ms, the p99 across both is *not* 200 ms. It depends on how many requests each
  served and what their slow tails look like. This mistake shows up in real dashboards.
  To combine servers, you need the raw values or a histogram.
- **Production systems don't keep every value.** At millions of requests a minute,
  they count values into buckets (a histogram) and estimate percentiles from the
  buckets. Prometheus histograms and HdrHistogram both work this way. The trade-off
  is precision for memory.
- **Tail latency multiplies.** If one page load calls 10 services and each is slow
  1% of the time, about 10% of page loads hit at least one slow call. That's why
  big systems care so much about p99 and p99.9. Read: *The Tail at Scale*
  (Dean and Barroso, 2013).
</details>

---

## Step 3 — Look at the stream (20 minutes)

**Do:** before writing a client, look at what one sees.

```bash
# terminal 1
uv run uvicorn fakeserver.app:app --port 8000

# terminal 2
curl -N http://localhost:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model": "x", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 5, "stream": true}'
```

Then read [`fakeserver/app.py`](../fakeserver/app.py). It's about 70 lines.

**Check:** you see `data:` lines appear over about a quarter of a second, ending with `data: [DONE]`.

**Think:**
- What's in the first chunk, and when does it arrive compared with the second?
- What does `-N` do? Run it without and compare.
- In your own words: what does a "slot" do, and what happens to a request when all slots are busy?
- Try `"stream": false`. What does the fake server say, and why might a real
  server behave differently?

<details><summary>Go deeper</summary>

- **This format is called server-sent events (SSE).** It's plain HTTP: the server
  keeps the response open and writes `data: ...` lines followed by a blank line.
  OpenAI, Anthropic, vLLM, and llama.cpp all stream this way.
- **Streaming changes what "fast" means.** Without streaming, the user waits for
  the whole answer. With it, they start reading after the TTFT. The total time is
  the same, but it feels much faster. That's why TTFT is the number chat products
  watch most closely.
- **Proxies can silently break streaming.** A reverse proxy such as nginx buffers
  responses by default. Put one in front of a streaming server without turning
  buffering off, and the user gets every token at once at the end. You'll meet
  this in Phase 2, when you build your own router.
</details>

---

## Step 4 — Time one request (2–3 hours, including asyncio)

**Do first, if asyncio is new to you (1–2 hours):** read Python's official guide
*Coroutines and Tasks* (docs.python.org/3/library/asyncio-task.html). Focus on
`async def`, `await`, `asyncio.run`, `asyncio.gather`, and `asyncio.Semaphore`.
Then skim the httpx docs pages on *Async Support* and *Streaming Responses*.

**Do:** implement `send_one()` in [`loadgen/client.py`](../loadgen/client.py).

**Check:** `uv run pytest tests/test_client.py`

<details><summary>Hints</summary>

- `async with client.stream("POST", url, json=body) as response:` opens a
  streaming request; `async for line in response.aiter_lines():` reads it line by line.
- `response.status_code` tells you whether it worked before you read anything.
- Network failures raise `httpx.HTTPError` subclasses, and a timeout is one of them.
  Think about whether to catch only those or everything. Catching everything means
  your own bugs come back as "errors" instead of crashing loudly. Which do you want
  while developing?
</details>

**Think:**
- Why `time.perf_counter()` and not `time.time()`?
- Why must errors be *returned* and not raised?
- We count chunks and call them tokens. Is one chunk always one token? How could
  you check on a real server?
- `test_timeout_is_returned_not_raised` uses a 0.3 s timeout against a server
  that waits 2 s. Which kind of timeout fired: connecting, or waiting for data?

<details><summary>Go deeper</summary>

- **Clocks.** `time.time()` follows the wall clock, which can jump when the system
  syncs with a time server. `perf_counter()` is *monotonic*: it only moves forward,
  and it has the highest resolution available. Always measure durations with a
  monotonic clock.
- **Your TTFT includes more than the model.** Measured from the client, it also
  includes opening a TCP connection (and a TLS handshake over HTTPS), sending the
  request, and any queueing. Reusing one `AsyncClient` keeps connections open
  between requests (keep-alive), so only the first request pays the setup cost. A
  server's own metrics usually show a smaller TTFT than users see, so always ask
  *where* a number was measured.
- **There are several kinds of timeout.** httpx has separate *connect*, *read*,
  *write*, and *pool* timeouts. A read timeout fires when no data arrives for that
  long, not when the whole request takes that long. So a stream that keeps
  trickling can run far longer than its "timeout".
</details>

---

## Step 5 — Many at once (1–2 hours)

**Do:** implement `run_level()` in [`loadgen/run.py`](../loadgen/run.py).

**Check:** `uv run pytest tests/test_run.py`, then the whole suite with `uv run pytest -rs`.

<details><summary>Hints</summary>

- `asyncio.Semaphore(n)` lets at most `n` tasks past an `async with` at a time.
- `asyncio.gather(*tasks)` runs them together and returns results in order.
- The classic mistake is `await`-ing each request inside a `for` loop, which sends
  them one at a time. `test_requests_run_in_parallel` exists to catch that.
</details>

**Think:**
- This test models "8 users who each wait for their answer before asking again"
  (a *closed loop*). A real website sees "8 new requests per second, whether or not
  earlier ones finished" (an *open loop*). How would the results differ once the
  server is overloaded?
- Your load generator and the server share the same 2 CPU cores in Step 7. How
  could the load generator distort its own measurements? How would you check?

<details><summary>Go deeper</summary>

- **Coordinated omission.** In a closed loop, when the server slows down, your
  users slow down too, so you send *less* load exactly when the server is
  struggling. That hides how bad overload really is. Real load tools (wrk2, k6 in
  arrival-rate mode, Vegeta) send on a fixed schedule instead. Search "coordinated
  omission Gil Tene" for the classic talk.
- **The load generator can be the bottleneck.** asyncio runs on one thread. If
  parsing JSON for thousands of streams uses up that thread, your timings include
  your own queueing. Rule of thumb: watch the load generator's CPU, and stop
  trusting results once it's near 100%.
</details>

---

## Step 6 — Predict, then measure the fake server (1–2 hours)

The fake server's defaults are 2 slots, 100 ms prefill, and 20 ms per token after
the first. You'll send 50-token requests.

**Do:**
1. On paper: how long does **one** request take when nobody else is around?
2. Fill in the Step 6 table in [`journal.md`](../journal.md) with your predicted
   TTFT p50 and tokens/s at concurrency 1, 2, 4, and 8. Show your reasoning.
3. Only then run it:
   ```bash
   uv run uvicorn fakeserver.app:app --port 8000     # terminal 1
   uv run python -m loadgen.run --url http://localhost:8000 \
     --concurrency 1,2,4,8 --requests 16 --max-tokens 50 --label fake   # terminal 2
   ```
4. Compare. For every number that surprised you, find the reason.
5. Change one knob (`FAKE_SLOTS=4`, or a longer `FAKE_PREFILL_MS`). Predict, then run.

**Check:** your measured numbers are within about 10% of your corrected
predictions, and you can explain any that aren't.

<details><summary>A tool for the reasoning (try without it first)</summary>

**Little's law:** requests in the system = arrival rate × time each one spends in it.
It holds for any stable queue: a coffee shop, a server, a highway. If 2 slots are
always busy and each request holds a slot for *S* seconds, how many requests
finish per second? What happens to the requests that don't fit in a slot?
</details>

**Think:**
- Throughput stops growing at some concurrency. Why there? What sets the ceiling?
- Past that point, what does adding users buy you, and what does it cost them?

<details><summary>Go deeper</summary>

- **The knee of the curve.** Plot latency against load on any system and you get a
  flat stretch, a bend, then a steep wall. Production teams try to run just before
  the bend. That's why "maximum throughput" is the wrong goal: what matters is
  maximum throughput *while meeting a latency target*.
- **Utilization and waiting.** In queueing theory, waiting time grows like
  1 / (1 − utilization). At 50% busy, waits are modest; at 90%, about 10× the
  service time; at 99%, about 100×. That's why servers run "hot" feel fine until
  suddenly they don't.
</details>

---

## Step 7 — A real model on CPU (2–4 hours)

**Do:**
```bash
scripts/get_llama_server.sh            # if the prebuilt download fails, add --from-source
bin/llama-server -m models/qwen2.5-0.5b-instruct-q4_k_m.gguf --port 8080 -np 4 -c 8192
```

`-np 4` gives the real server 4 slots, and `-c 8192` is the total context memory
they share.

1. Use what you learned from the fake to predict the real server's table. Write it down.
2. Run the same command with `--url http://localhost:8080 --label cpu-np4`.
3. Look hard at **TPOT across concurrency levels**. On the fake server, a token
   costs 20 ms whether 1 or 2 requests are running. Is that true on the real one?
4. Predict, then try `-np 1` and `-np 8`.
5. Is the first request after starting the server slower than the rest?

**Check:** you have results files for at least three `-np` settings, and a
journal entry explaining where the real server stopped matching the fake one.

**Think:**
- Why does TPOT behave the way it does as concurrency rises?
- Should your measurements include the first, slower request? What would you do about it?
- The load generator runs on the same 2 cores as the model. How does that affect
  what you measured? (Look back at your Step 5 answer.)

<details><summary>Go deeper (read after you've made your own guess)</summary>

- **Prefill and decode are different kinds of work.** Prefill processes the whole
  prompt in one pass, so it's limited by arithmetic (*compute-bound*). Decode
  produces one token per pass, and each pass must read every weight from memory.
  So decode is limited by how fast memory moves (*memory-bandwidth-bound*).
- **That's why batching works.** Reading the weights once and using them for
  4 conversations costs little more than using them for 1. The machine was mostly
  waiting on memory anyway. But it's not free: each extra conversation adds some
  arithmetic and its own KV cache to read. How much each one costs is what your
  TPOT column measures.
- **Continuous batching** means new requests join the running batch between
  tokens, instead of waiting for the whole batch to finish. llama.cpp and vLLM
  both do this. The idea comes from the Orca paper (OSDI 2022).
- **The KV cache is the hidden limit.** Each conversation's cache grows with every
  token. Total memory, not arithmetic, usually caps how many conversations fit at
  once. vLLM's PagedAttention paper (SOSP 2023) is about managing exactly this.
</details>

---

## Step 8 — Write it up (1–2 hours)

**Do:** create `results/phase-1-cpu.md` with:
- **Setup:** the machine (cores, RAM), the model file, the server flags, and the load generator settings
- **Results:** a table per `-np` setting (commit the JSON files from `results/` too)
- **Explanation:** 3–5 sentences on the *shape* of the results: where throughput
  levels off, what happens to TTFT and TPOT, and why
- **Surprise:** one thing that didn't match your prediction, and what you now think is going on
- **Caveats:** what might be wrong with your measurement (sample size, a shared CPU, warm-up)

**Check:** someone who hasn't seen this project could read it and rerun your
experiment. The caveats section is what makes a write-up trustworthy. Engineers
who list their own measurement's weaknesses are the ones whose numbers get believed.

## Next

The same load generator against vLLM on a free Kaggle GPU. A GPU behaves very
differently from a CPU here, and you'll be able to see exactly how. That guide
gets written when you get there, using the latest versions and free-tier rules.
