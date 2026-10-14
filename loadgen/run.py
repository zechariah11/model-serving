"""Load generator: hit a server at several concurrency levels and record what happens.

YOUR TASK (step 5 in docs/phase-1.md): implement run_level().
Everything else in this file is done for you.
Check it with:  uv run pytest tests/test_run.py

Usage:
  uv run python -m loadgen.run --url http://localhost:8000 --concurrency 1,2,4,8 --label fake
"""

import argparse
import asyncio
import dataclasses
import json
import time
from pathlib import Path

import httpx

from loadgen.client import RequestResult, send_one
from loadgen.stats import Summary, summarize

PROMPT = "Write a short story about a lighthouse keeper who finds a message in a bottle."


async def run_level(
    base_url: str, model: str, concurrency: int, n_requests: int, max_tokens: int
) -> tuple[list[RequestResult], float]:
    """Send n_requests in total, with at most `concurrency` in flight at any moment.

    Return (results, wall_s): one RequestResult per request, and the seconds
    from the start of the first request to the end of the last.

    This is a "closed loop" test. Picture `concurrency` users who each send a
    request, wait for the whole reply, then send the next one straight away.

    Share one httpx.AsyncClient across all requests, and give it
    timeout=httpx.Timeout(300): the default of 5 seconds is far too short for
    a slow model under load.
    """
    raise NotImplementedError


def print_row(s: Summary) -> None:
    print(
        f"{s.concurrency:>5} {s.requests:>5} {s.errors:>5} "
        f"{s.ttft_p50_s:>9.3f} {s.ttft_p99_s:>9.3f} "
        f"{s.latency_p50_s:>8.2f} {s.latency_p99_s:>8.2f} "
        f"{s.tpot_p50_ms:>9.1f} {s.tokens_per_s:>8.1f}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--url", default="http://localhost:8000", help="server base URL, without /v1")
    parser.add_argument("--model", default="default", help="model name (vLLM checks it; llama-server ignores it)")
    parser.add_argument("--concurrency", default="1,2,4,8", help="comma-separated levels to test")
    parser.add_argument("--requests", type=int, default=32, help="requests per level")
    parser.add_argument("--max-tokens", type=int, default=64)
    parser.add_argument("--label", default="run", help="name for the results file")
    args = parser.parse_args()

    print(f"{'conc':>5} {'reqs':>5} {'errs':>5} {'ttft p50':>9} {'ttft p99':>9} "
          f"{'lat p50':>8} {'lat p99':>8} {'tpot p50':>9} {'tok/s':>8}")
    print(f"{'':>17} {'(s)':>9} {'(s)':>9} {'(s)':>8} {'(s)':>8} {'(ms)':>9}")

    summaries = []
    for concurrency in [int(c) for c in args.concurrency.split(",")]:
        results, wall_s = asyncio.run(
            run_level(args.url, args.model, concurrency, args.requests, args.max_tokens)
        )
        summary = summarize(results, concurrency, wall_s)
        summaries.append(summary)
        print_row(summary)
        first_error = next((r.error for r in results if not r.ok), None)
        if first_error:
            print(f"      first error: {first_error}")

    out = Path("results") / f"{args.label}-{time.strftime('%Y%m%d-%H%M%S')}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(
        {"args": vars(args), "summaries": [dataclasses.asdict(s) for s in summaries]}, indent=2
    ))
    print(f"\nsaved {out}")


if __name__ == "__main__":
    main()
