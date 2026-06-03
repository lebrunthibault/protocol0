from typing import Callable, ClassVar, Dict, List, Type


class PluginInterface(object):
    """Base class for remote-script plugins.

    A plugin extends the script declaratively: it can react to domain events
    (``register_listeners``) and expose new actions to the HTTP catalog
    (``register_actions``). The ``PluginLoader`` wires both up at startup and
    tears the listeners down on disconnect — a plugin never calls
    ``DomainEventBus.subscribe``/``un_subscribe`` itself.

    See ``docs/plugins.md`` for the full guide.
    """

    name: ClassVar[str] = ""

    def should_start(self) -> bool:
        """Return False to skip this plugin (e.g. only run on a given set)."""
        return True

    def start(self) -> None:
        """Optional one-time setup, called once if ``should_start`` is True."""
        pass

    def stop(self) -> None:
        """Optional teardown. Listeners from ``register_listeners`` are already
        unsubscribed by the loader before this runs."""
        pass

    def register_listeners(self) -> Dict[Type, Callable]:
        """Map a domain-event type to a handler.

        Each ``event_type: handler`` pair is subscribed on the ``DomainEventBus``
        right after ``start()`` and unsubscribed automatically on stop. The
        handler receives the event instance::

            def register_listeners(self):
                return {SongStartedEvent: self._on_song_started}
        """
        return {}

    def register_actions(self) -> List[Callable]:
        """Return ``@api_route``-decorated functions to expose as catalog actions.

        Returning a route makes it assignable to a keyboard shortcut, exactly
        like the core actions under ``application/http/routes/``::

            def register_actions(self):
                return [say_hello]  # say_hello is decorated with @api_route(...)
        """
        return []
