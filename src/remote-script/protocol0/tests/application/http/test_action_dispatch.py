"""Tests of the action executor: uniform envelope + Sequence awaiting
(Router._dispatch_action). Routes are registered ad hoc under /api/action/test/
and cleaned up by the p0 fixture's route snapshot."""
import protocol0.application.http.Router as Router
from protocol0.application.http.Router import get_routes
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.shared.sequence.Sequence import Sequence
from protocol0.tests.domain.fixtures.http import dispatch_action


class ActionDoneEvent(object):
    pass


def _register(name, fn) -> str:
    path = "/api/action/test/%s" % name
    get_routes()[("POST", path)] = fn
    return path


def test_sync_action_done(p0, tick_scheduler):
    path = _register("sync", lambda: {"tempo": 120})

    response = dispatch_action(path, {}, tick_scheduler)

    assert response.code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert response.json == {"status": "done", "res": {"tempo": 120}}


def test_action_exception_is_a_500_error(p0, tick_scheduler):
    def failing() -> None:
        raise Protocol0Warning("no track matching spec")

    path = _register("failing", failing)

    response = dispatch_action(path, {}, tick_scheduler)

    assert response.code == 500
    assert response.json["status"] == "error"
    assert "no track matching spec" in response.json["error"]


def test_sequence_awaited_until_terminated(p0, tick_scheduler):
    def async_action() -> Sequence:
        seq = Sequence()
        seq.wait_for_event(ActionDoneEvent)
        seq.add(lambda: 42)
        return seq.done()

    path = _register("async", async_action)
    # the fake Live thread emits the completion event a few ticks in
    tick_scheduler.schedule(5, lambda: DomainEventBus.emit(ActionDoneEvent()))

    response = dispatch_action(path, {}, tick_scheduler)

    assert response.code == 200
    assert response.json == {"status": "done", "res": 42}


def test_sequence_error_is_a_500(p0, tick_scheduler):
    def erroring_action() -> Sequence:
        seq = Sequence()
        seq.add(_raise)
        return seq.done()

    def _raise() -> None:
        raise RuntimeError("step failed")

    path = _register("erroring", erroring_action)

    response = dispatch_action(path, {}, tick_scheduler)

    assert response.code == 500
    assert response.json["status"] == "error"


def test_sequence_cancelled_is_a_500(p0, tick_scheduler):
    def cancelled_action() -> Sequence:
        seq = Sequence()
        seq.add(seq._cancel)
        return seq.done()

    path = _register("cancelled", cancelled_action)

    response = dispatch_action(path, {}, tick_scheduler)

    assert response.code == 500
    assert response.json == {"status": "cancelled"}


def test_still_running_after_cap_is_a_202(p0, tick_scheduler, monkeypatch):
    monkeypatch.setattr(Router, "_ACTION_TIMEOUT_S", 0.05)

    def never_ending() -> Sequence:
        seq = Sequence()
        seq.wait_for_event(ActionDoneEvent)  # never emitted
        return seq.done()

    path = _register("never_ending", never_ending)

    response = dispatch_action(path, {}, tick_scheduler)

    assert response.code == 202
    assert response.json == {"status": "running"}


def test_non_serializable_result_degrades_to_str(p0, tick_scheduler):
    marker = object()
    path = _register("object_res", lambda: marker)

    response = dispatch_action(path, {}, tick_scheduler)

    assert response.code == 200
    assert response.json["status"] == "done"
    assert isinstance(response.json["res"], str)


def test_missing_required_param_is_a_400(p0, tick_scheduler):
    def needs_name(name: str) -> None:
        pass

    path = _register("needs_name", needs_name)

    response = dispatch_action(path, {}, tick_scheduler)

    assert response.code == 400
