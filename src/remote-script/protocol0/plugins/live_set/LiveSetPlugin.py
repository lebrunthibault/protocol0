"""Live-performance plugin: EC4 encoders always follow the selected device.

The 8 encoders of the EC4 group on MIDI channel 3 (relative CC 0-7) control
the 8 macros of the device currently selected in Live's UI. The handler
re-reads ``Song.selected_device()`` on every encoder tick, so clicking
another device instantly re-targets the knobs — no remapping, no
selection listener.

``parameters[0]`` is "Device On" (an encoder on it would toggle the device
mid-performance), so encoder i drives ``parameters[i + 1]`` — the 8 macros
of a rack.
"""
from functools import partial

from protocol0.application.control_surface.Encoders import Encoders
from protocol0.application.plugin.PluginInterface import PluginInterface
from protocol0.shared.Song import Song


class LiveSetPlugin(PluginInterface):
    name = "live_set"

    CHANNEL = 3
    FIRST_CC = 0
    MACRO_COUNT = 8

    def register_encoders(self, encoders: Encoders) -> None:
        for i in range(self.MACRO_COUNT):
            encoders.add_encoder(
                channel=self.CHANNEL,
                identifier=self.FIRST_CC + i,
                name="selected device macro %s" % (i + 1),
                on_scroll=partial(self._scroll_macro, i),
                scroll_only=True,
            )

    @staticmethod
    def _scroll_macro(macro_index: int, go_next: bool) -> None:
        device = Song.selected_device()
        if device is None:
            return

        param_index = macro_index + 1  # parameters[0] is "Device On"
        if param_index >= len(device.parameters):
            return

        device.parameters[param_index].scroll(go_next)
