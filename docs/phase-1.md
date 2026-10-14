# Phase 1: one server, measured

**Goal:** measure how a model server behaves as more users arrive, and be able to
explain *why* it behaves that way.

You'll build a load generator, point it at a fake server whose behavior you can
work out on paper, then at a real model. Most of the learning happens where the
real server stops matching your model of it.

Rough time: 10–15 hours, spread over a couple of weeks.

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

Open your Codespace (see the [README](../README.md)) and run:

```bash
uv run pytest
```

You should see 19 failures, each a `NotImplementedError`. That's your to-do list.

## Step 2 — Warm-up: percentiles (30–60 minutes)

Implement `percentile()` and `summarize()` in [`loadgen/stats.py`](../loadgen/stats.py).
The docstrings say exactly what to compute.

```bash
uv run pytest tests/test_stats.py
```

**Think, then write in your journal:** why do serving teams watch p99 instead of
the average? Make up a small example where the average looks fine but some users
are clearly unhappy.

<details><summary>Hint</summary>

`sorted()` returns a new list. `int(pos)` gives the lower index; `pos - int(pos)`
is how far you are toward the next one. Watch out for the last index.
</details>

## Step 3 — Look at the stream (15 minutes)

Before writing a client, look at what one sees.

```bash
# terminal 1
uv run uvicorn fakeserver.app:app --port 8000

# terminal 2
curl -N http://localhost:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model": "x", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 5, "stream": true}'
```

Then read [`fakeserver/app.py`](../fakeserver/app.py). It's about 70 lines.

**Answer in your journal:**
- What's in the first chunk, and when does it arrive compared with the second?
- What does `-N` do? Run it without and compare.
- In your own words: what does a "slot" do, and what happens to a request when all slots are busy?

## Step 4 — Time one request (1–2 hours)

Implement `send_one()` in [`loadgen/client.py`](../loadgen/client.py).

```bash
uv run pytest tests/test_client.py
```

<details><summary>Hints</summary>

- `async with client.stream("POST", url, json=body) as response:` opens a
  streaming request; `async for line in response.aiter_lines():` reads it line by line.
- `response.status_code` tells you whether it worked before you read anything.
- Network failures raise `httpx.HTTPError` subclasses. Think about whether to catch
  only those or everything. Catching everything means your own bugs come back as
  "errors" instead of crashing loudly. Which do you want while developing?
</details>

**Think:**
- Why `time.perf_counter()` and not `time.time()`?
- Why must errors be *returned* and not raised?
- We count chunks and call them tokens. Is one chunk always one token? How could
  you check on a real server?

## Step 5 — Many at once (1–2 hours)

Implement `run_level()` in [`loadgen/run.py`](../loadgen/run.py).

```bash
uv run pytest tests/test_run.py
```

<details><summary>Hints</summary>

- `asyncio.Semaphore(n)` lets at most `n` tasks past an `async with` at a time.
- `asyncio.gather(*tasks)` runs them together and returns results in order.
- The classic mistake is `await`-ing each request inside a `for` loop, which sends
  them one at a time. `test_requests_run_in_parallel` exists to catch that.
</details>

**Think:** this test models "8 users who each wait for their answer before asking
again" (a *closed loop*). A real website sees "8 new requests arrive per second,
whether or not earlier ones finished" (an *open loop*). How would the results
differ once the server is overloaded? (When you're curious, search for
"coordinated omission".)

## Step 6 — Predict, then measure the fake server (1 hour)

The fake server's defaults are 2 slots, 100 ms prefill, and 20 ms per token after
the first. You'll send 50-token requests.

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

<details><summary>A tool for the reasoning (try without it first)</summary>

**Little's law:** requests in the system = arrival rate × time each one spends in it.
It holds for any stable queue: a coffee shop, a server, a highway. If 2 slots are
always busy and each request holds a slot for *S* seconds, how many requests
finish per second? What happens to the requests that don't fit in a slot?
</details>

## Step 7 — A real model on CPU (2–3 hours)

```bash
scripts/get_llama_server.sh            # if the prebuilt download fails, add --from-source
bin/llama-server -m models/qwen2.5-0.5b-instruct-q4_k_m.gguf --port 8080 -np 4 -c 8192
```

`-np 4` gives the real server 4 slots, and `-c 8192` is the total context memory
they share.

1. Use what you learned from the fake to predict the real server's table. Write it down.
2. Run the same command with `--url http://localhost:8080 --label cpu-np4`.
3. Look hard at **TPOT across concurrency levels**. On the fake server, a token
   costs 20 ms whether 1 or 2 requests are running. Is that true on the real
   one? Why or why not? (Search for "LLM batching memory bandwidth".)
4. Predict, then try `-np 1` and `-np 8`.
5. Is the first request after starting the server slower than the rest? Why might
   that be, and should your measurements include it?

## Step 8 — Write it up (1 hour)

Create `results/phase-1-cpu.md` with:
- the setup: machine, model, server flags
- your results table (commit the JSON files from `results/` too)
- 3–5 sentences explaining the *shape* of the results
- one thing that surprised you, and what you now think is going on

## Next

The same load generator against vLLM on a free Kaggle GPU. A GPU behaves very
differently from a CPU here, and you'll be able to see exactly how. We'll set it
up together when you get there.
