import asyncio

import httpx

from loadgen.client import send_one


def send(url, max_tokens=20, timeout_s=30):
    async def go():
        async with httpx.AsyncClient(timeout=timeout_s) as client:
            return await send_one(client, url, "fake", "hi", max_tokens)

    return asyncio.run(go())


def test_counts_tokens(start_fake_server):
    r = send(start_fake_server(slots=1, prefill_ms=50, token_ms=5), max_tokens=20)
    assert r.ok, r.error
    assert r.error is None
    assert r.n_tokens == 20


def test_first_token_waits_for_text(start_fake_server):
    # The fake server sends a chunk with no text straight away, then the first
    # real token after the 100 ms prefill. Only the real token counts.
    r = send(start_fake_server(slots=1, prefill_ms=100, token_ms=5))
    assert r.ok, r.error
    assert 0.1 <= r.ttft_s < 0.5


def test_total_time_covers_the_whole_stream(start_fake_server):
    # After the first token: 19 more at 10 ms each.
    r = send(start_fake_server(slots=1, prefill_ms=50, token_ms=10), max_tokens=20)
    assert r.ok, r.error
    assert r.total_s >= r.ttft_s + 0.19


def test_connection_refused_is_returned_not_raised(closed_port):
    r = send(f"http://127.0.0.1:{closed_port}")
    assert not r.ok
    assert r.error


def test_error_status_is_a_failure(start_fake_server):
    r = send(start_fake_server() + "/wrong-path")
    assert not r.ok
    assert r.error


def test_single_token_reply(start_fake_server):
    r = send(start_fake_server(slots=1, prefill_ms=50, token_ms=5), max_tokens=1)
    assert r.ok, r.error
    assert r.n_tokens == 1
    assert r.total_s >= r.ttft_s


def test_timeout_is_returned_not_raised(start_fake_server):
    # The server goes quiet for 2 s after its first (empty) chunk; the client
    # gives up after 0.3 s of silence.
    r = send(start_fake_server(slots=1, prefill_ms=2000, token_ms=5), timeout_s=0.3)
    assert not r.ok
    assert r.error
    assert r.total_s < 1.5  # it gave up, it didn't sit through the whole wait
