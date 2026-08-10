from typing import TYPE_CHECKING, Callable, ClassVar, Dict, Type

if TYPE_CHECKING:
    from protocol0.application.control_surface.Encoders import Encoders


class PluginInterface(object):
    """Base class for remote-script plugins.

    A plugin extends the script declaratively: it can react to domain events
    (``register_listeners``), expose new actions by decorating methods with
    ``@action`` (see ``protocol0.application.plugin.action``), and bind
    control-surface encoders (``register_encoders``). The ``PluginLoader``
    wires everything up at startup — subscribing listeners, binding encoders
    and generating one ``POST /api/action/<plugin>/<method>`` route per
    ``@action`` method — and tears it all down on disconnect. A plugin never
    calls ``DomainEventBus.subscribe``/``un_subscribe`` nor ``@api_route``
    itself.

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

    def register_encoders(self, encoders: "Encoders") -> None:
        """Bind control-surface encoders (EC4-style knobs).

        Called right after ``start()`` with a fresh ``Encoders`` binder; every
        encoder added on it is disconnected automatically on stop. The channel
        is 1-indexed, scrolls are relative (the handler receives
        ``go_next: bool``) — see ``Encoders.add_encoder`` for the gestures::

            def register_encoders(self, encoders):
                encoders.add_encoder(
                    channel=3, identifier=0, name="my knob",
                    on_scroll=self._on_scroll, scroll_only=True,
                )
        """
        pass
