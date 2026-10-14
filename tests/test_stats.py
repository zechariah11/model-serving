import math

import pytest

from loadgen.client import RequestResult
from loadgen.stats import percentile, summarize


def ok(ttft_s, total_s, n_tokens):
    return RequestResult(ok=True, ttft_s=ttft_s, total_s=total_s, n_tokens=n_tokens)


def failed():
    return RequestResult(ok=False, total_s=0.5, error="connection refused")


# --- percentile ---------------------------------------------------------------

def test_median_of_even_length_list_blends_the_middle_two():
    assert percentile([10, 20, 30, 40], 50) == pytest.approx(25.0)


def test_input_does_not_need_to_be_sorted():
    assert percentile([40, 10, 30, 20], 50) == pytest.approx(25.0)


def test_input_list_is_not_modified():
    values = [3, 1, 2]
    percentile(values, 50)
    assert values == [3, 1, 2]


def test_0_and_100_are_min_and_max():
    assert percentile([3, 1, 2], 0) == 1
    assert percentile([3, 1, 2], 100) == 3


def test_p99_interpolates_between_ranks():
    assert percentile(list(range(1, 101)), 99) == pytest.approx(99.01)


def test_single_value():
    assert percentile([7], 99) == 7


def test_empty_list_raises():
    with pytest.raises(ValueError):
        percentile([], 50)


# --- summarize ----------------------------------------------------------------

def test_summarize_counts_and_timings():
    results = [ok(0.1, 1.0, 10), ok(0.2, 2.0, 10), ok(0.3, 3.0, 10), failed()]
    s = summarize(results, concurrency=2, wall_s=4.0)

    assert s.concurrency == 2
    assert s.requests == 4
    assert s.errors == 1
    assert s.ttft_p50_s == pytest.approx(0.2)
    assert s.latency_p50_s == pytest.approx(2.0)
    # (1.0-0.1)/9 = 0.1 s, (2.0-0.2)/9 = 0.2 s, (3.0-0.3)/9 = 0.3 s -> median 200 ms
    assert s.tpot_p50_ms == pytest.approx(200)
    # 30 tokens over 4 seconds
    assert s.tokens_per_s == pytest.approx(7.5)


def test_failed_requests_do_not_count_toward_timings():
    s = summarize([ok(0.1, 1.0, 10), failed(), failed()], concurrency=1, wall_s=1.0)
    assert s.latency_p99_s == pytest.approx(1.0)


def test_time_per_token_skips_requests_with_one_token():
    s = summarize([ok(0.1, 0.1, 1), ok(0.1, 1.0, 10)], concurrency=1, wall_s=1.0)
    assert s.tpot_p50_ms == pytest.approx(100)


def test_all_failed_gives_nan_timings_and_zero_throughput():
    s = summarize([failed(), failed()], concurrency=1, wall_s=1.0)
    assert s.errors == 2
    assert math.isnan(s.ttft_p50_s)
    assert math.isnan(s.latency_p99_s)
    assert math.isnan(s.tpot_p50_ms)
    assert s.tokens_per_s == 0
