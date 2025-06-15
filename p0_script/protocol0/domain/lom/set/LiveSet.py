import enum
from functools import partial

import Live
from _Framework.SubjectSlot import SlotManager
from _Framework.CompoundElement import subject_slot_group

from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.Song import find_track


class LiveTrack(enum.Enum):
    KICK = "KICK"
    # HATS = "HATS"
    # PERC = "PERC"
    FX = "FX"
    # VOCALS = "VOCALS"
    BASS = "BASS"
    SYNTH = "SYNTH"
    PIANO = "PIANO"

    def get(self) -> SimpleTrack:
        return find_track(self.value.title(), exact=False)


class LiveSet(SlotManager):
    def __init__(self) -> None:
        super().__init__()
        from protocol0.shared.logging.Logger import Logger

        Logger.dev("activating Live set mode")
        self._bass_track = LiveTrack.BASS.get()
        self._bass_track_pitch = self._bass_track.devices.get_one_from_enum(DeviceEnum.PITCH)
        self._synth_track = LiveTrack.SYNTH.get()
        self._synth_track_pitch = self._synth_track.devices.get_one_from_enum(DeviceEnum.PITCH)
        self._piano_track = LiveTrack.PIANO.get()

        self._bass_and_synth_tracks_arm_listener.replace_subjects(
            [self._bass_track._track, self._synth_track._track, self._piano_track._track]
        )

    @subject_slot_group("arm")
    def _bass_and_synth_tracks_arm_listener(self, _: Live.Track.Track) -> None:
        activate_bass_pitch = False
        activate_synth_pitch = False

        if self._bass_track.arm_state.is_armed:
            if self._synth_track.arm_state.is_armed:
                activate_bass_pitch = True
                activate_synth_pitch = True
            elif self._piano_track.arm_state.is_armed:
                activate_bass_pitch = True

        Scheduler.defer(partial(setattr, self._bass_track_pitch, "is_enabled", activate_bass_pitch))
        Scheduler.defer(
            partial(setattr, self._synth_track_pitch, "is_enabled", activate_synth_pitch)
        )
