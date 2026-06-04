"""A minimal, generic plugin you can copy to start your own.

It shows the two things a plugin does declaratively:

- **react to an event** — ``register_listeners`` maps a domain event to a
  handler; the loader subscribes it at start and unsubscribes it on stop.
- **expose an action** — a method decorated with ``@action`` becomes an HTTP
  endpoint under ``/api/action/<plugin>/<method>`` (shown in the Swagger UI at
  ``/docs`` and in ``/openapi.json``) and callable by the agent. The method name
  is the action name; its typed parameters become the action's inputs.

Drop this file in as-is, or copy it to start your own. A plugin can be a single
file (``plugins/MyPlugin.py``) or a package (``plugins/my_plugin/``) — both are
discovered automatically.

Full guide: ``docs/plugins.md``.
"""
from typing import Callable, Dict, Type

from protocol0.application.plugin.PluginInterface import PluginInterface
from protocol0.application.plugin.action import action
from protocol0.domain.lom.song.SongStartedEvent import SongStartedEvent
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.logging.StatusBar import StatusBar


class ExamplePlugin(PluginInterface):
    name = "example"

    def should_start(self) -> bool:
        # Disabled by default: this is a copy-me template, not a real plugin.
        # Flip to True (or copy the file) to try it.
        return False

    def register_listeners(self) -> Dict[Type, Callable]:
        return {SongStartedEvent: self._on_song_started}

    @action
    def say_hello(self, name: str) -> None:
        """Show a greeting in Live's status bar (example plugin action)."""
        StatusBar.show_message("Hello %s from the example plugin!" % name)

    def _on_song_started(self, _: SongStartedEvent) -> None:
        Logger.info("example plugin: playback started")
