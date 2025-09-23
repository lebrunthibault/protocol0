import Live
from _Framework.ControlSurface import ControlSurface, get_control_surfaces
from _Framework.Util import find_if
from functools import partial

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface

# noinspection SpellCheckingInspection
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.set.LiveSet import LiveSet, LiveTrack
from protocol0.domain.lom.track.simple_track.audio.master.MasterTrack import MasterTrack
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.utils.list import find_if
from protocol0.domain.track_recorder.RecordService import RecordService
from protocol0.infra.midi.MidiService import MidiService
from protocol0.shared.Song import Song


class ActionGroupLive3(ActionGroupInterface):
    CHANNEL = 3

    def configure(self) -> None:
        self.add_encoder(
            identifier=16 + 5,
            name="copy piano to bass",
            on_press=lambda: self._container.get(LiveSet).action_copy_piano_to_bass,
        )
