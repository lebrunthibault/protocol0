import types
from typing import Callable, Dict, List, Tuple, Type, TypeVar

from protocol0.application.ScriptDisconnectedEvent import ScriptDisconnectedEvent
from protocol0.application.http.Router import API_PREFIX, get_routes
from protocol0.application.plugin.PluginInterface import PluginInterface
from protocol0.application.plugin.action import iter_actions
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
        # Generate one HTTP route per @action method, bound to this started
        # instance. We register the bound method directly in the global route
        # table (not via @api_route) because the instance only exists now, at
        # load time. Bound methods hide ``self``, so inspect.signature still
        # shows the typed params — the OpenAPI generator and the router pick them
        # up unchanged, so the action appears in the Swagger UI ("/docs") and
        # /openapi.json. This runs before HttpServer.start(), and _ROUTES is a
        # module global, so the routes are live for both dispatch and OpenAPI.
        routes = get_routes()
        for name, bound in iter_actions(plugin):
            path = "%s/action/%s/%s" % (API_PREFIX, plugin.name, name)
            key = ("POST", path)
            if key in routes:
                Logger.warning("Action %s/%s already registered, skipping" % (plugin.name, name))
                continue
            routes[key] = bound
            Logger.info("Plugin %s exposes action %s -> POST %s" % (plugin.name, name, path))

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
