"""Turn a pile of request timings into the few numbers that matter.

YOUR TASK (step 2 in docs/phase-1.md): implement percentile() and summarize().
Check them with:  uv run pytest tests/test_stats.py
"""

from dataclasses import dataclass

from loadgen.client import RequestResult


def percentile(values: list[float], p: float) -> float:
    """Return the p-th percentile of values, where p runs from 0 to 100.

    Use linear interpolation between the two nearest ranks (numpy's default rule):
      1. sort the values (without changing the caller's list)
      2. position = (p / 100) * (len(values) - 1)
      3. if position lands between two indexes, blend the two values there,
         weighted by how close position is to each

    Example: percentile([10, 20, 30, 40], 50) == 25.0
    Raise ValueError for an empty list.
    Don't use numpy or the statistics module; write it yourself once.
    """
    raise NotImplementedError


@dataclass
class Summary:
    concurrency: int
    requests: int  # requests sent
    errors: int  # requests that failed
    ttft_p50_s: float  # time to first token, median
    ttft_p99_s: float
    latency_p50_s: float  # whole request, from sending to the last token
    latency_p99_s: float
    tpot_p50_ms: float  # time per output token after the first, median
    tokens_per_s: float  # tokens from successful requests / wall-clock seconds of the run


def summarize(results: list[RequestResult], concurrency: int, wall_s: float) -> Summary:
    """Build a Summary from one run.

    - Only successful requests count toward the timings and the token total.
    - Time per output token for one request = (total_s - ttft_s) / (n_tokens - 1).
      Skip requests with fewer than 2 tokens when computing it.
    - If there is nothing to take a percentile of (say, every request failed),
      that field is float("nan").
    """
    raise NotImplementedError
