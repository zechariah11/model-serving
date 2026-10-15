"""Send one streaming request to an LLM server and time it.

YOUR TASK (step 4 in docs/phase-1.md): implement send_one().
Check it with:  uv run pytest tests/test_client.py
"""

from dataclasses import dataclass

import httpx


@dataclass
class RequestResult:
    ok: bool
    ttft_s: float | None = None  # seconds from sending to the first chunk that has text
    total_s: float = 0.0  # seconds from sending to the end of the stream (or the failure)
    n_tokens: int = 0  # chunks that carried text (roughly one token each)
    error: str | None = None


async def send_one(
    client: httpx.AsyncClient, base_url: str, model: str, prompt: str, max_tokens: int
) -> RequestResult:
    """Send one chat request with streaming turned on, read the whole stream, and time it.

    The request is  POST {base_url}/v1/chat/completions  with this JSON body:

        {"model": model,
         "messages": [{"role": "user", "content": prompt}],
         "max_tokens": max_tokens,
         "stream": True}

    The response arrives as lines of text ("server-sent events"). The ones that
    matter look like this:

        data: {"choices": [{"delta": {"content": "Hello"}, ...}], ...}

    and the stream ends with:

        data: [DONE]

    Blank lines separate events; skip them.

    Rules:
      - Time with time.perf_counter(), not time.time(). (Find out why.)
      - The first token is the first chunk whose delta has non-empty "content".
        Some chunks carry no text; they don't count. If the whole stream had
        no text, the request still succeeded: ok=True, ttft_s=None, n_tokens=0.
      - Never raise. If anything goes wrong (connection refused, error status,
        timeout), return RequestResult(ok=False, error=<short description>).
        A load test that crashes on its first error measures nothing.
    """
    raise NotImplementedError
