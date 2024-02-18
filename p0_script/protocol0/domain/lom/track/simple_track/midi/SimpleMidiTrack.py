from typing import List, cast

from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.clip_slot.MidiClipSlot import MidiClipSlot
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.routing.InputRoutingChannelEnum import InputRoutingChannelEnum
from protocol0.domain.lom.track.routing.InputRoutingTypeEnum import InputRoutingTypeEnum
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.shared.Song import Song


def _get_midi_note_track(track: SimpleTrack) -> "SimpleMidiTrack":
    if isinstance(track.input_routing.track, SimpleMidiTrack):
        return track.input_routing.track
    else:
        try:
            midi_note_track = list(Song.simple_tracks())[track.index - 1]
        except IndexError:
            midi_note_track = None

        assert isinstance(midi_note_track, SimpleMidiTrack), "Could not find Midi note track"

    return midi_note_track


def toggle_note_track_routing(track: SimpleTrack, force_routing: bool = False) -> None:
    midi_note_track = _get_midi_note_track(track)

    if track.input_routing.type == InputRoutingTypeEnum.ALL_INS or force_routing:
        # listen to Cthulhu
        track.current_monitoring_state = CurrentMonitoringStateEnum.IN
        track.input_routing.track = midi_note_track
        if midi_note_track.devices.get_one_from_enum(DeviceEnum.CTHULHU):
            track.input_routing.channel = InputRoutingChannelEnum.CTHULHU
        else:
            track.input_routing.channel = InputRoutingChannelEnum.POST_FX
    else:
        # listen to synth track
        track.current_monitoring_state = CurrentMonitoringStateEnum.AUTO
        track.input_routing.type = InputRoutingTypeEnum.ALL_INS


class SimpleMidiTrack(SimpleTrack):
    CLIP_SLOT_CLASS = MidiClipSlot

    @property
    def clip_slots(self) -> List[MidiClipSlot]:
        return cast(List[MidiClipSlot], super(SimpleMidiTrack, self).clip_slots)

    @property
    def clips(self) -> List[MidiClip]:
        return super(SimpleMidiTrack, self).clips  # noqa
