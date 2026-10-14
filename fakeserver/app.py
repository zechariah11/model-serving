"""A fake LLM server that speaks the same streaming API as llama-server and vLLM.

It runs no model. It only simulates the costs that matter when serving one:

  slots    only this many requests are served at once; the rest wait in line
  prefill  delay before the first token (reading the prompt)
  token    delay for each token after the first (generating the reply)

Use it to build and test the load generator on any machine, and as a simple
model of a server that you can reason about on paper before you measure.

Run:   uv run uvicorn fakeserver.app:app --port 8000
Tune:  FAKE_SLOTS=4 FAKE_PREFILL_MS=100 FAKE_TOKEN_MS=20 uv run uvicorn fakeserver.app:app --port 8000
"""

import asyncio
import json
import os
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse


def create_app(slots: int, prefill_ms: float, token_ms: float) -> FastAPI:
    app = FastAPI()
    slot_pool = asyncio.Semaphore(slots)

    def chunk(delta: dict, finish_reason: str | None = None) -> str:
        body = {
            "id": "fake",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": "fake",
            "choices": [{"index": 0, "delta": delta, "finish_reason": finish_reason}],
        }
        return f"data: {json.dumps(body)}\n\n"

    @app.post("/v1/chat/completions")
    async def chat_completions(request: Request):
        body = await request.json()
        if not body.get("stream"):
            return JSONResponse({"error": "this fake server only supports \"stream\": true"}, status_code=400)
        max_tokens = int(body.get("max_tokens", 16))

        async def events():
            # Sent right away, before waiting for a slot. It has no text in it,
            # so it must not count as the first token.
            yield chunk({"role": "assistant", "content": ""})
            async with slot_pool:
                await asyncio.sleep(prefill_ms / 1000)
                for i in range(max_tokens):
                    if i > 0:
                        await asyncio.sleep(token_ms / 1000)
                    yield chunk({"content": f"tok{i} "})
            yield chunk({}, finish_reason="length")
            yield "data: [DONE]\n\n"

        return StreamingResponse(events(), media_type="text/event-stream")

    return app


app = create_app(
    slots=int(os.environ.get("FAKE_SLOTS", "2")),
    prefill_ms=float(os.environ.get("FAKE_PREFILL_MS", "100")),
    token_ms=float(os.environ.get("FAKE_TOKEN_MS", "20")),
)
