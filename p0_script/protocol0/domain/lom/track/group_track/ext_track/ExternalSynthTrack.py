from typing import Optional, cast

from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.domain.lom.track.group_track.ext_track.ExtArmState import ExtArmState
from protocol0.domain.lom.track.group_track.ext_track.ExtMonitoringState import ExtMonitoringState
from protocol0.domain.lom.track.group_track.ext_track.ExtSoloState import ExtSoloState
from protocol0.domain.lom.track.group_track.ext_track.SimpleAudioExtTrack import SimpleAudioExtTrack
from protocol0.domain.lom.track.group_track.ext_track.SimpleBaseExtTrack import SimpleBaseExtTrack
from protocol0.domain.lom.track.group_track.ext_track.SimpleMidiExtTrack import (
    SimpleMidiExtTrack,
)
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.utils.forward_to import ForwardTo


class ExternalSynthTrack(AbstractGroupTrack):
    def __init__(self, base_group_track: SimpleTrack) -> None:  # noqa
        super(ExternalSynthTrack, self).__init__(base_group_track)

        # swapping the base track
        self.base_track = SimpleBaseExtTrack(base_group_track._track, base_group_track.index)
        self.base_track.group_track = base_group_track.group_track
        self.base_track.abstract_group_track = self
        self.base_track.sub_tracks = base_group_track.sub_tracks

        # swapping the midi track
        midi_track = self.base_track.sub_tracks[0]
        self.midi_track = SimpleMidiExtTrack(midi_track._track, midi_track.index)
        self.link_sub_track(self.midi_track)
        self.midi_track.devices.build()

        # swapping the audio track
        audio_track = self.base_track.sub_tracks[1]
        self.audio_track = SimpleAudioExtTrack(audio_track._track, audio_track.index)
        self.link_sub_track(self.audio_track)

        # use the ext tracks instead of simple tracks
        self.base_track.sub_tracks = self.sub_tracks

        self._solo_state = ExtSoloState(self.base_track)

        self.monitoring_state = ExtMonitoringState(self.base_track)

        self.arm_state = ExtArmState(self.base_track, self.midi_track)
        self.arm_state.register_observer(self.monitoring_state)

    is_armed = cast(bool, ForwardTo("arm_state", "is_armed"))
    solo = cast(bool, ForwardTo("_solo_state", "solo"))

    def on_tracks_change(self) -> None:
        super(ExternalSynthTrack, self).on_tracks_change()
        self._solo_state.update()

    def get_view_track(self, scene_index: int) -> Optional[SimpleTrack]:
        if ApplicationView.is_clip_view_visible():
            return self.midi_track
        else:
            return self.base_track

    @property
    def instrument(self) -> Optional[InstrumentInterface]:
        return self.midi_track.instrument
