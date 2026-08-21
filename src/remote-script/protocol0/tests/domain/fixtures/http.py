"""Drives HTTP dispatch through the real router, headless.

The real setup has two threads: the http thread (blocks awaiting the action
outcome) and the Live thread (executes the action, drains the submit queue at
every tick). Here the test thread plays the http side while a background pump
advances the synchronous tick scheduler — the fake Live thread.
"""
import json
import threading
import time

from protocol0.application.http import HttpServer
from protocol0.application.http.Router import HttpRequestHandler
from protocol0.tests.infra.scheduler.TickSchedulerSync import TickSchedulerSync


class FakeHttpResponse:
    def __init__(self) -> None:
        self.code = None
        self.headers = {}
        self.body = b""

    @property
    def json(self):
        return json.loads(self.body.decode()) if self.body else None


class _FakeWFile:
    def __init__(self, response: FakeHttpResponse) -> None:
        self._response = response

    def write(self, data: bytes) -> None:
        self._response.body += data


def _make_handler(path: str, response: FakeHttpResponse) -> HttpRequestHandler:
    handler = HttpRequestHandler.__new__(HttpRequestHandler)
    handler.path = path
    handler.send_response = lambda code: setattr(response, "code", code)
    handler.send_header = lambda name, value: response.headers.__setitem__(name, value)
    handler.end_headers = lambda: None
    handler.wfile = _FakeWFile(response)
    return handler


def dispatch(
    method: str, path: str, body: dict, tick_scheduler: TickSchedulerSync
) -> FakeHttpResponse:
    """Runs one request through HttpRequestHandler._dispatch, pumping the tick
    scheduler in the background until the response is written."""
    response = FakeHttpResponse()
    handler = _make_handler(path, response)
    stop = threading.Event()

    def pump() -> None:
        while not stop.is_set():
            tick_scheduler.advance()
            time.sleep(0.001)

    original_submit = HttpServer.submit
    HttpServer.submit = lambda callback: tick_scheduler.schedule(1, callback)
    pump_thread = threading.Thread(target=pump, daemon=True)
    pump_thread.start()
    try:
        handler._dispatch(method, body)
    finally:
        stop.set()
        pump_thread.join(timeout=1)
        HttpServer.submit = original_submit
    return response


def dispatch_action(
    path: str, body: dict, tick_scheduler: TickSchedulerSync
) -> FakeHttpResponse:
    """POSTs an action (/api/action/...) through the real dispatch path:
    kwargs building, envelope, Sequence awaiting."""
    return dispatch("POST", path, body, tick_scheduler)
