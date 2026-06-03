"""A minimal, generic plugin you can copy to start your own.

It shows the two things a plugin does declaratively:

- **react to an event** — ``register_listeners`` maps a domain event to a
  handler; the loader subscribes it at start and unsubscribes it on stop.
- **expose an action** — an ``@api_route`` function becomes an HTTP endpoint
  under ``/api`` (shown in the Swagger UI at ``/docs`` and in ``/openapi.json``)
  and callable by the agent; ``register_actions`` declares it.

It is disabled by default (``should_start`` returns ``False``) so it never runs
in a real session. Flip it to ``True`` — or copy this file — to try it.

Full guide: ``docs/plugins.md``.
"""
from typing import Callable, Dict, List, Type

from protocol0.application.http.Router import api_route
from protocol0.application.plugin.PluginInterface import PluginInterface
from protocol0.domain.lom.song.SongStartedEvent import SongStartedEvent
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.logging.StatusBar import StatusBar


@api_route("POST", "/example/hello")
def say_hello() -> None:
    """Show a greeting in Live's status bar (example plugin action)."""
    StatusBar.show_message("Hello from the example plugin!")


class ExamplePlugin(PluginInterface):
    name = "example"

    def should_start(self) -> bool:
        # Disabled by default — this is a template, not a real feature.
        return True

    def register_listeners(self) -> Dict[Type, Callable]:
        return {SongStartedEvent: self._on_song_started}

    def register_actions(self) -> List[Callable]:
        return [say_hello]

    def _on_song_started(self, _: SongStartedEvent) -> None:
        Logger.info("example plugin: playback started")
