"""Track actions — a plugin made of a single ``@action`` for now.

``select`` was historically a core route (``/api/track/select``); it now lives as a
plugin action (``/api/action/track/select``) so it shows up in the agent's action
catalog and is bindable to a shortcut like any other action.
"""
from protocol0.application.plugin.PluginInterface import PluginInterface
from protocol0.application.plugin.action import action
from protocol0.shared.Song import Song, find_track
from protocol0.shared.logging.StatusBar import StatusBar


class TrackPlugin(PluginInterface):
    name = "track"

    @action
    def select(self, name: str) -> None:
        """Select a track by name (use "master" to select the master track)."""
        StatusBar.show_message("selecting track")
        if name.lower() == "master":
            Song.master_track().select()
        else:
            find_track(name).select()
