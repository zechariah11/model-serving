import socket
import threading
import time

import pytest
import uvicorn

from fakeserver.app import create_app


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Report tests for steps you haven't started as skipped, not failed.

    A test that hits a NotImplementedError is waiting on a TODO function, so it
    shows up as "not started yet". Every other failure is real and stays red.
    """
    outcome = yield
    report = outcome.get_result()
    if call.when == "call" and call.excinfo is not None and call.excinfo.errisinstance(NotImplementedError):
        todo = call.excinfo.traceback[-1].name
        report.outcome = "skipped"
        report.longrepr = (str(item.path), item.location[1], f"not started yet: {todo}()")


@pytest.fixture
def start_fake_server():
    """Start a fake server in the background and return its base URL."""
    running = []

    def start(slots: int = 2, prefill_ms: float = 100, token_ms: float = 20) -> str:
        sock = socket.socket()
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
        config = uvicorn.Config(create_app(slots, prefill_ms, token_ms), log_level="warning")
        server = uvicorn.Server(config)
        thread = threading.Thread(target=server.run, kwargs={"sockets": [sock]}, daemon=True)
        thread.start()
        deadline = time.monotonic() + 10
        while not server.started:
            if time.monotonic() > deadline:
                raise RuntimeError("fake server did not start")
            time.sleep(0.01)
        running.append((server, thread))
        return f"http://127.0.0.1:{port}"

    yield start

    for server, thread in running:
        server.should_exit = True
        thread.join(timeout=5)


@pytest.fixture
def closed_port():
    """A port with nothing listening on it."""
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port
