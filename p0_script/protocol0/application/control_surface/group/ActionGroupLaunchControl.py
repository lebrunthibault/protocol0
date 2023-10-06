from functools import partial

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.lom.track.TrackPlayerService import TrackPlayerService


class ActionGroupLaunchControl(ActionGroupInterface):
    CHANNEL = 10

    def configure(self) -> None:
        top_pad_mapping = {
            41: "Kick",
            42: "Snare",
            43: "Hat Closed",
            44: "Hat Open",
            57: "Hat Open Loop",
            58: None,
            59: None,
            60: "Exhaust",
        }

        for i, note in enumerate(top_pad_mapping):
            track_name = top_pad_mapping[note]

            # DUPLicate clip
            self.add_encoder(
                identifier=note,
                name="toggle clip",
                on_press=partial(self._container.get(TrackPlayerService).play_pause_track, track_name),
            )
