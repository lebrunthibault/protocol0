from typing import List

import Live
from _Framework.SubjectSlot import Subject

from protocol0.domain.lom.track.routing.OutputRoutingTypeEnum import OutputRoutingTypeEnum
from protocol0.tests.domain.fixtures.clip_slot import AbletonClipSlot
from protocol0.tests.domain.fixtures.device import AbletonDevice
from protocol0.tests.domain.fixtures.device_parameter import AbletonDeviceParameter


class AbletonMixerDevice(Subject):
    """Mutable mixer fake: volume / panning / sends are real parameters whose
    values can be written and asserted."""

    def __init__(self) -> None:
        self._live_ptr = id(self)
        self.volume = AbletonDeviceParameter("Track Volume", default_value=0.85)
        self.panning = AbletonDeviceParameter("Track Panning", default_value=0.0, min=-1.0)
        self.sends: List[AbletonDeviceParameter] = []


class TrackType(object):
    GROUP = "GROUP"
    MIDI = "MIDI"
    AUDIO = "AUDIO"


class TrackRoutingType(object):
    def __init__(self, display_name: str = "") -> None:
        self.display_name = display_name
        self.attached_object = None
        self.category = Live.Track.RoutingTypeCategory.none


class AbletonTrack(Subject):
    __subject_events__ = (
        "name",
        "solo",
        "devices",
        "clip_slots",
        "playing_slot_index",
        "fired_slot_index",
        "color",
        "output_meter_level",
    )

    def __init__(self, track_type: str = TrackType.MIDI) -> None:
        self._live_ptr = id(self)
        self.name = track_type
        self.devices: List[AbletonDevice] = []
        self.mixer_device = AbletonMixerDevice()
        self.can_be_armed = True
        self.arm = False
        self.solo = False
        self.mute = False
        self.current_monitoring_state = 1  # AUTO
        self.fold_state = False
        self.has_midi_input = self.is_foldable = self.fold_state = False
        self.available_input_routing_types = []
        self.available_input_routing_channels = []
        self.available_output_routing_types = [
            TrackRoutingType(OutputRoutingTypeEnum.SENDS_ONLY.label)
        ]
        self.output_routing_type = self.available_output_routing_types[0]
        self.clip_slots = [AbletonClipSlot()]
        self.view = None
        self.group_track = None
        self.color_index = 0
        self.has_audio_input = False
        self.has_midi_input = False

        self.track_type = track_type

        if track_type == TrackType.GROUP:
            self.is_foldable = True
            self.has_audio_input = True
        if track_type == TrackType.MIDI:
            self.has_midi_input = True
        if track_type == TrackType.AUDIO:
            self.has_audio_input = True

    def stop_all_clips(self, quantized: bool = True) -> None:
        for clip_slot in self.clip_slots:
            if clip_slot.clip is not None:
                clip_slot.clip.is_playing = False

    def __repr__(self) -> str:
        return "%s - %s" % (self.track_type, self.name)
