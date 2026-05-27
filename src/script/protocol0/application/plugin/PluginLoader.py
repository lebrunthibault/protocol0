import types
from typing import Dict, List, Type, TypeVar

from protocol0.application.ScriptDisconnectedEvent import ScriptDisconnectedEvent
from protocol0.application.plugin.PluginInterface import PluginInterface
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.utils.utils import import_package
from protocol0.shared.logging.Logger import Logger

P = TypeVar("P", bound=PluginInterface)


class PluginLoader(object):
    _started: List[PluginInterface] = []
    _by_class: Dict[Type[PluginInterface], PluginInterface] = {}

    @classmethod
    def load_and_start(cls, plugins_package: types.ModuleType) -> None:
        import_package(plugins_package)

        for plugin_class in PluginInterface.__subclasses__():
            try:
                plugin = plugin_class()
                if not plugin.should_start():
                    Logger.info("Plugin %s skipped (should_start=False)" % plugin.name)
                    continue
                plugin.start()
                cls._started.append(plugin)
                cls._by_class[plugin_class] = plugin
                Logger.info("Plugin %s started" % plugin.name)
            except Exception as e:
                Logger.warning("Plugin %s failed to start: %s" % (plugin_class.__name__, e))

        DomainEventBus.subscribe(ScriptDisconnectedEvent, lambda _: cls._stop_all())

    @classmethod
    def get(cls, plugin_class: Type[P]) -> P:
        return cls._by_class[plugin_class]  # type: ignore[return-value]

    @classmethod
    def _stop_all(cls) -> None:
        for plugin in cls._started:
            try:
                plugin.stop()
            except Exception as e:
                Logger.warning("Plugin %s stop error: %s" % (plugin.name, e))
        cls._started = []
        cls._by_class = {}
