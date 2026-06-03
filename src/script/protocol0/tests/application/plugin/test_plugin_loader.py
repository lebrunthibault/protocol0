from typing import Callable, Dict, List, Type

from protocol0.application.plugin.PluginInterface import PluginInterface
from protocol0.application.plugin.PluginLoader import PluginLoader
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.tests.application.plugin import stub_plugins


class _StubEvent(object):
    pass


class _StubStartStopPlugin(PluginInterface):
    name = "stub_start_stop"
    started = False
    stopped = False

    def start(self) -> None:
        _StubStartStopPlugin.started = True

    def stop(self) -> None:
        _StubStartStopPlugin.stopped = True


class _StubGatedPlugin(PluginInterface):
    name = "stub_gated"
    started = False

    def should_start(self) -> bool:
        return False

    def start(self) -> None:
        _StubGatedPlugin.started = True

    def stop(self) -> None:
        pass


class _StubFailingStartPlugin(PluginInterface):
    name = "stub_failing"
    stopped = False

    def start(self) -> None:
        raise RuntimeError("boom")

    def stop(self) -> None:
        _StubFailingStartPlugin.stopped = True


class _StubListenerPlugin(PluginInterface):
    name = "stub_listener"
    received: List[_StubEvent] = []

    def _on_event(self, event: _StubEvent) -> None:
        _StubListenerPlugin.received.append(event)

    def register_listeners(self) -> Dict[Type, Callable]:
        return {_StubEvent: self._on_event}


def _reset_loader() -> None:
    PluginLoader._started = []
    PluginLoader._by_class = {}
    PluginLoader._listeners = []
    DomainEventBus.reset()


def test_plugin_start_and_stop() -> None:
    _reset_loader()
    _StubStartStopPlugin.started = False
    _StubStartStopPlugin.stopped = False

    PluginLoader.load_and_start(stub_plugins)

    assert _StubStartStopPlugin.started is True
    assert PluginLoader.get(_StubStartStopPlugin).name == "stub_start_stop"

    PluginLoader._stop_all()
    assert _StubStartStopPlugin.stopped is True


def test_should_start_false_skips_start() -> None:
    _reset_loader()
    _StubGatedPlugin.started = False

    PluginLoader.load_and_start(stub_plugins)

    assert _StubGatedPlugin.started is False
    assert _StubGatedPlugin not in PluginLoader._by_class


def test_start_exception_is_swallowed() -> None:
    _reset_loader()

    PluginLoader.load_and_start(stub_plugins)

    assert _StubFailingStartPlugin not in PluginLoader._by_class
    assert _StubStartStopPlugin in PluginLoader._by_class


def test_listeners_are_subscribed_and_cleaned_up() -> None:
    _reset_loader()
    _StubListenerPlugin.received = []

    PluginLoader.load_and_start(stub_plugins)

    # The loader subscribed the declared listener: emitting reaches the handler.
    DomainEventBus.emit(_StubEvent())
    assert len(_StubListenerPlugin.received) == 1

    # Stopping unsubscribes it: a further emit is not delivered.
    PluginLoader._stop_all()
    DomainEventBus.emit(_StubEvent())
    assert len(_StubListenerPlugin.received) == 1
