from functools import partial

from typing import List, cast, Optional

from protocol0.application.CommandBus import CommandBus
from protocol0.application.command.LoadDeviceCommand import LoadDeviceCommand
from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.clip_slot.MidiClipSlot import MidiClipSlot
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.track.group_track.DrumsTrack import DrumsTrack
from protocol0.domain.lom.track.group_track.VocalsTrack import VocalsTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


class SimpleMidiTrack(SimpleTrack):
    CLIP_SLOT_CLASS = MidiClipSlot

    @property
    def clip_slots(self) -> List[MidiClipSlot]:
        return cast(List[MidiClipSlot], super(SimpleMidiTrack, self).clip_slots)

    @property
    def clips(self) -> List[MidiClip]:
        return super(SimpleMidiTrack, self).clips  # noqa

    def on_added(self) -> Optional[Sequence]:
        super(SimpleMidiTrack, self).on_added()

        if (
            any(isinstance(track, (DrumsTrack, VocalsTrack)) for track in self.group_tracks)
            and len(list(self.devices)) == 0
        ):
            CommandBus.dispatch(LoadDeviceCommand(DeviceEnum.DRUM_RACK.name))

        return None
