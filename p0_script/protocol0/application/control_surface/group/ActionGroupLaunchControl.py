from _Framework.SubjectSlot import SlotManager

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.application.control_surface.TrackEncoder import TrackEncoder


class ActionGroupLaunchControl(ActionGroupInterface, SlotManager):
    CHANNEL = 2

    def configure(self) -> None:
        track_to_control_values = {
            "Kick": (73, 41, 13, False),
            "Hat": (74, 42, 14, False),
            "Perc": (75, 43, 15, False),
            "FX": (76, 44, 16, True),
            "Harmony": (89, 57, 17, True),
            "Lead": (90, 58, 18, True),
            "Bass": (91, 59, 19, True),
            "Sub": (92, 60, 20, False),
        }

        for track_name, config in track_to_control_values.items():
            TrackEncoder(
                channel=self.CHANNEL,
                track_select_note=config[0],
                solo_mute_note=config[1],
                volume_cc=config[2],
                track_name=track_name,
                is_top_track=config[3],
                component_guard=self._component_guard,
            )
