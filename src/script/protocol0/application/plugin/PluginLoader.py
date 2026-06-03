import types
from typing import Callable, Dict, List, Tuple, Type, TypeVar

from protocol0.application.ScriptDisconnectedEvent import ScriptDisconnectedEvent
from protocol0.application.plugin.PluginInterface import PluginInterface
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.utils.utils import import_package
from protocol0.shared.logging.Logger import Logger

P = TypeVar("P", bound=PluginInterface)


class PluginLoader(object):
    _started: List[PluginInterface] = []
    _by_class: Dict[Type[PluginInterface], PluginInterface] = {}
    # Listeners the loader subscribed on behalf of plugins, so it can undo them
    # on stop without the plugin tracking anything.
    _listeners: List[Tuple[Type, Callable]] = []

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
                cls._subscribe_listeners(plugin)
                cls._register_actions(plugin)
                cls._started.append(plugin)
                cls._by_class[plugin_class] = plugin
                Logger.info("Plugin %s started" % plugin.name)
            except Exception as e:
                Logger.warning("Plugin %s failed to start: %s" % (plugin_class.__name__, e))

        DomainEventBus.subscribe(ScriptDisconnectedEvent, lambda _: cls._stop_all())

    @classmethod
    def _subscribe_listeners(cls, plugin: PluginInterface) -> None:
        for event_type, handler in plugin.register_listeners().items():
            DomainEventBus.subscribe(event_type, handler)
            cls._listeners.append((event_type, handler))

    @classmethod
    def _register_actions(cls, plugin: PluginInterface) -> None:
        # The @api_route decorator already registered each action in the global
        # route table at import time, so it shows up in the Swagger UI ("/docs")
        # and /openapi.json, and is callable over HTTP. We just surface what the
        # plugin exposes.
        for fn in plugin.register_actions():
            Logger.info("Plugin %s exposes action %s" % (plugin.name, fn.__name__))

    @classmethod
    def get(cls, plugin_class: Type[P]) -> P:
        return cls._by_class[plugin_class]  # type: ignore[return-value]

    @classmethod
    def _stop_all(cls) -> None:
        for event_type, handler in cls._listeners:
            DomainEventBus.un_subscribe(event_type, handler)
        cls._listeners = []

        for plugin in cls._started:
            try:
                plugin.stop()
            except Exception as e:
                Logger.warning("Plugin %s stop error: %s" % (plugin.name, e))
        cls._started = []
        cls._by_class = {}
