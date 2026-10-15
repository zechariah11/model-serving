# How the pieces fit

Read this once before Phase 1, and come back whenever something in a step feels like magic.

## The three pieces of a real model server

### 1. The model file: just numbers
`models/qwen2.5-0.5b-instruct-q4_k_m.gguf` holds about half a billion numbers (the
*weights*) learned during training. By itself the file does nothing, like sheet
music with no musician. The name tells you what's inside:

| Part | Meaning |
|---|---|
| `qwen2.5` | Model family and version, from Alibaba's Qwen team |
| `0.5b` | 0.5 billion weights. Tiny: large models have 70 billion or more |
| `instruct` | Tuned to follow instructions and chat, not just continue text |
| `q4_k_m` | **Quantized**: each weight squeezed from 16 bits to about 4. The file is about 4× smaller and runs faster, with a little loss in quality |
| `.gguf` | llama.cpp's file format |

### 2. llama.cpp: the engine
An open-source C++ program that loads those numbers and does the math that turns a
prompt into text, one *token* (roughly a word piece) at a time. It's named after
Meta's LLaMA models, which it first ran, but today it runs most open models. We
use it because it runs well on ordinary CPUs, and your free Codespace has no GPU.

### 3. llama-server: the engine behind a web address
One of the programs the llama.cpp project builds. It wraps the engine in a web
server, so other programs send it HTTP requests (port 8080 here). It speaks
**the same request format as OpenAI's API**, and so do vLLM and our fake server.
That's why one load generator works against all three: same plug, different
power station.

Later, on a GPU, you'll use **vLLM**, an engine built for serving many users at
once. It's closer to what production platforms run.

## What happens to one request

```
load generator ──POST──▶ server
                           │
                           ├─ wait for a free slot      (a slot = one conversation in progress)
                           │
                           ├─ prefill: read the whole prompt in one pass
                           │     ──▶ first token comes back           ← TTFT ends here
                           │
                           ├─ decode: produce one token, send it as a "data:" line,
                           │          repeat until max_tokens         ← TPOT is the gap
                           │
                           └─ send "data: [DONE]"
```

- **Slots** (`-np 4` on llama-server, `FAKE_SLOTS` on the fake) set how many
  conversations run at once. A request beyond that waits in line.
- **KV cache:** each conversation keeps notes about the text so far, so the model
  doesn't have to reread everything to produce each new token. Those notes take
  memory. `-c 8192` is the total memory the slots share, and memory usually limits
  how many conversations fit at once.

## Two terminals, one connection

In Steps 3 and 6, terminal 1 runs a server and terminal 2 runs a client (`curl`,
then your load generator). They share nothing except a network connection to
`localhost:8000`:

```
terminal 2 (client)                         terminal 1 (fake server)
       │  POST /v1/chat/completions                │
       │ ────────────────────────────────────────▶ │
       │ ◀─ data: {"delta": {"content": ""}}       │ empty chunk, sent at once
       │                                           │ wait for a slot, then 100 ms prefill
       │ ◀─ data: {"delta": {"content": "tok0 "}}  │ first real token
       │ ◀─ data: {"delta": {"content": "tok1 "}}  │ every 20 ms after that
       │ ◀─ data: [DONE]                           │
```

The server doesn't know who is calling, and the client doesn't know the server is
fake. Swap the URL to `localhost:8080` and the same client measures llama-server.

**Ports:** only one program can listen on a port at a time. The fake server uses
8000 (uvicorn's default) and llama-server uses 8080 (its default), so both can run
together and you switch between them with `--url`.

## Why a fake server?

1. **To build your tool without a model.** It's fast, predictable, and light, so
   the tests run in seconds on any machine.
2. **To check the tool before trusting it.** You set its delays, so you know the
   right answer. If your load generator disagrees, the bug is in your tool. It's
   like checking a scale with a known 1 kg weight before weighing anything else.
   The empty first chunk is a deliberate trap.
3. **To learn queueing on its own.** Slots, a fixed cost, and a line: simple enough
   to work out on paper.
4. **To see where reality differs.** Wherever llama-server stops matching the
   fake, something real is going on (batching, CPU limits, warm-up).
5. **It comes back later.** In Phase 2 your router needs 10 servers behind it; 10
   fakes fit on a free Codespace and 10 models don't. In Phase 4 you'll kill
   servers on purpose, which is cheaper to try on fakes first.

## Percentiles are positional

A percentile sorts the values and reads what sits at a rank. An average adds
everything up. So:

- 99 requests at 1 ms and 1 at 100 ms: p99 ≈ 1.99 ms. The single slow request
  falls in the 1% that p99 deliberately ignores. Only the max sees it.
- Make 2 of them slow, and p99 jumps to 100 ms.

p99 answers "what's the slowest experience for 99% of requests?" It needs enough
samples to mean anything: with 32 requests, p99 is basically the slowest request.

## Glossary

| Term | Meaning |
|---|---|
| Token | A piece of text the model produces in one step, often part of a word |
| Prefill | Reading the whole prompt in one pass, before the first token |
| Decode | Producing tokens one at a time after that |
| TTFT / TPOT | Time to first token / time per output token after the first |
| Slot | Room for one conversation in progress |
| KV cache | A conversation's saved working state, so earlier text isn't reprocessed |
| Batching | Running several conversations through the model together |
| Quantization | Storing weights with fewer bits, for size and speed |
| Closed / open loop | Users wait for answers before asking again / requests arrive on a schedule regardless |
| Little's law | Requests in the system = arrival rate × time each spends there |
