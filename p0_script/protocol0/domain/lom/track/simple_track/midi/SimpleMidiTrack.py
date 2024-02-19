from typing import List, cast

from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.clip_slot.MidiClipSlot import MidiClipSlot
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device_parameter.DeviceParamEnum import DeviceParamEnum
from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.routing.InputRoutingChannelEnum import InputRoutingChannelEnum
from protocol0.domain.lom.track.routing.InputRoutingTypeEnum import InputRoutingTypeEnum
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.shared.Song import Song


def is_midi_note_track(track: "SimpleTrack") -> bool:
    midi_track_prefixes = ("notes", "rhythm")

    return track.has_midi_output and not any(
        track.lower_name.startswith(prefix) for prefix in midi_track_prefixes
    )


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

    def reset_midi_automation(self) -> None:
        muted_device = self.devices.get_one_from_enum(DeviceEnum.MUTED)
        if not muted_device:
            return None

        clip = self.clip_slots[Song.selected_scene().index].clip
        muted_device_on = muted_device.get_parameter_by_name(DeviceParamEnum.DEVICE_ON)
        if clip and muted_device_on in clip.automation.get_automated_parameters(
            self.devices.parameters
        ):
            return None

        muted_device.is_enabled = True
