import inspect
import time
from typing import Optional

from protocol0.application.http.Router import _build_kwargs, _returns_value
from protocol0.application.plugin.action import action, iter_actions
from protocol0.shared.Undo import Undo
from protocol0.shared.sequence.Sequence import Sequence
from protocol0.tests.domain.fixtures.p0 import make_protocol0


def _record_undo() -> list:
    """Swap the Undo facade for recording callables, and return the call log.

    The log is shared with the action bodies below, so it captures the *ordering*
    of begin/body/end — which is the whole point of the undo step.
    """
    calls: list = []
    Undo(lambda: calls.append("begin"), lambda: calls.append("end"))
    return calls


def test_undo_step_wraps_a_synchronous_action() -> None:
    make_protocol0()
    calls = _record_undo()

    class Plugin(object):
        @action
        def act(self) -> None:
            calls.append("body")

    Plugin().act()

    assert calls == ["begin", "body", "end"]


def test_undo_step_stays_open_until_a_deferred_action_completes() -> None:
    # The point of chaining through a Sequence: remove_muted_notes writes to the
    # clip a tick later, so closing the step synchronously would leave the write
    # outside the undo step and break Ctrl-Z.
    make_protocol0()
    calls = _record_undo()

    class Plugin(object):
        @action
        def act(self) -> Optional[Sequence]:
            seq = Sequence()
            seq.defer()
            seq.add(lambda: calls.append("write"))
            return seq.done()

    Plugin().act()
    assert calls == ["begin"], "the deferred write has not run yet"

    time.sleep(0.3)  # TickSchedulerTest uses real timers (1 tick = 10ms)
    assert calls == ["begin", "write", "end"]


def test_decorated_action_keeps_its_typed_parameters() -> None:
    # Router._build_kwargs and the OpenAPI generator introspect the decorated
    # method: the wrapper must stay signature-transparent.
    make_protocol0()
    _record_undo()

    class Plugin(object):
        @action
        def act(self, name: str, count: int) -> None:
            pass

    bound = Plugin().act
    assert list(inspect.signature(bound).parameters) == ["name", "count"]
    assert inspect.signature(bound).parameters["count"].annotation is int
    assert _build_kwargs(bound, {"name": "Serum", "count": 2}) == {"name": "Serum", "count": 2}


def test_action_is_fire_and_forget_even_when_it_returns_a_sequence() -> None:
    # Router._returns_value drives the dispatch: a truthy return annotation would
    # make the HTTP thread block, then fail to JSON-serialize the Sequence. The
    # method may declare what it really returns; the wrapper hides it from HTTP.
    make_protocol0()
    _record_undo()

    class Plugin(object):
        @action
        def returns_none(self) -> None:
            pass

        @action
        def returns_sequence(self) -> Optional[Sequence]:
            return None

    plugin = Plugin()
    assert _returns_value(plugin.returns_none) is False
    assert _returns_value(plugin.returns_sequence) is False


def test_decorated_action_stays_discoverable_and_documented() -> None:
    make_protocol0()
    _record_undo()

    class Plugin(object):
        @action
        def act(self) -> None:
            """Do the thing."""

    plugin = Plugin()
    assert [name for name, _ in iter_actions(plugin)] == ["act"]
    assert plugin.act.__doc__ == "Do the thing."  # OpenAPI summary
    assert plugin.act.__name__ == "act"
