from protocol0.application.plugin.PluginInterface import PluginInterface
from protocol0.application.plugin.PluginLoader import PluginLoader
from protocol0.tests.application.plugin import stub_plugins
from protocol0.tests.domain.fixtures.container import TestContainer


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


def _reset_loader() -> None:
    PluginLoader._started = []
    PluginLoader._by_class = {}


def test_plugin_start_and_stop() -> None:
    _reset_loader()
    _StubStartStopPlugin.started = False
    _StubStartStopPlugin.stopped = False

    PluginLoader.load_and_start(TestContainer(), stub_plugins)

    assert _StubStartStopPlugin.started is True
    assert PluginLoader.get(_StubStartStopPlugin).name == "stub_start_stop"

    PluginLoader._stop_all()
    assert _StubStartStopPlugin.stopped is True


def test_should_start_false_skips_start() -> None:
    _reset_loader()
    _StubGatedPlugin.started = False

    PluginLoader.load_and_start(TestContainer(), stub_plugins)

    assert _StubGatedPlugin.started is False
    assert _StubGatedPlugin not in PluginLoader._by_class


def test_start_exception_is_swallowed() -> None:
    _reset_loader()

    PluginLoader.load_and_start(TestContainer(), stub_plugins)

    assert _StubFailingStartPlugin not in PluginLoader._by_class
    assert _StubStartStopPlugin in PluginLoader._by_class
