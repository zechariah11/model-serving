import asyncio

from loadgen.run import run_level


def run(url, concurrency, n_requests, max_tokens=10):
    return asyncio.run(run_level(url, "fake", concurrency, n_requests, max_tokens))


def test_one_result_per_request(start_fake_server):
    results, _ = run(start_fake_server(slots=8, prefill_ms=10, token_ms=1), concurrency=4, n_requests=10)
    assert len(results) == 10
    assert all(r.ok for r in results), [r.error for r in results if not r.ok]


def test_requests_run_in_parallel(start_fake_server):
    # Each request takes about 0.1 + 9 * 0.01 = 0.19 s, and the server has
    # room for all of them. Four at once should take about as long as one;
    # four in a row would take about 0.76 s.
    _, wall_s = run(start_fake_server(slots=8, prefill_ms=100, token_ms=10), concurrency=4, n_requests=4)
    assert wall_s < 0.5


def test_never_more_than_concurrency_in_flight(start_fake_server):
    # 8 requests, 2 at a time: 4 rounds of about 0.19 s each.
    _, wall_s = run(start_fake_server(slots=8, prefill_ms=100, token_ms=10), concurrency=2, n_requests=8)
    assert wall_s >= 0.7


def test_more_users_than_requests(start_fake_server):
    results, _ = run(start_fake_server(slots=8, prefill_ms=10, token_ms=1), concurrency=8, n_requests=3)
    assert len(results) == 3


def test_a_dead_server_does_not_stop_the_run(closed_port):
    # Every request fails, but the run still finishes and reports each failure.
    results, _ = run(f"http://127.0.0.1:{closed_port}", concurrency=2, n_requests=5)
    assert len(results) == 5
    assert not any(r.ok for r in results)
    assert all(r.error for r in results)
