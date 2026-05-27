from _Framework.Util import find_if

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.application.plugin.PluginLoader import PluginLoader

# noinspection SpellCheckingInspection
from protocol0.plugins.live_set.LiveSetPlugin import LiveSetPlugin


class ActionGroupLive3(ActionGroupInterface):
    CHANNEL = 3

    def configure(self) -> None:
        self.add_encoder(
            identifier=8,
            name="copy piano to bass",
            on_press=lambda: PluginLoader.get(LiveSetPlugin).copy_piano_to_bass,
        )
