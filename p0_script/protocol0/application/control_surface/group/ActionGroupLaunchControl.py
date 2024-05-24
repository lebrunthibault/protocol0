from typing import List

from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import MIDI_NOTE_TYPE, MIDI_CC_TYPE
from _Framework.SubjectSlot import subject_slot, SlotManager

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.application.control_surface.TrackEncoder import TrackEncoder
from protocol0.domain.lom.song.components.DeviceComponent import DeviceComponent
from protocol0.domain.lom.song.components.TrackComponent import TrackComponent
from protocol0.shared.Song import Song


class ActionGroupLaunchControl(ActionGroupInterface, SlotManager):
    CHANNEL = 2

    def configure(self) -> None:
        with self._component_guard():
            self._un_solo_listener.subject = ButtonElement(True, MIDI_NOTE_TYPE, 1, 107)
            self._toggle_device_listener.subject = ButtonElement(True, MIDI_NOTE_TYPE, 1, 105)

            self._move_loop_left.subject = ButtonElement(True, MIDI_CC_TYPE, 1, 104)
            self._move_loop_right.subject = ButtonElement(True, MIDI_CC_TYPE, 1, 105)

            self._scroll_device_prev.subject = ButtonElement(True, MIDI_CC_TYPE, 1, 106)
            self._scroll_device_next.subject = ButtonElement(True, MIDI_CC_TYPE, 1, 107)

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

        # noinspection PyAttributeOutsideInit
        self.encoders: List[TrackEncoder] = []

        for track_name, config in track_to_control_values.items():
            self.encoders.append(
                TrackEncoder(
                    channel=self.CHANNEL,
                    track_select_note=config[1],
                    solo_mute_note=config[0],
                    volume_cc=config[2],
                    track_name=track_name,
                    is_top_track=config[3],
                    component_guard=self._component_guard,
                )
            )

    @subject_slot("value")
    def _un_solo_listener(self, value: int) -> None:
        if value:
            return None

        soloed_tracks = any(t for t in Song.simple_tracks() if t.solo)

        if soloed_tracks:
            self._container.get(TrackComponent).un_solo_all_tracks()
            for encoder in self.encoders:
                encoder.init_leds()

    @subject_slot("value")
    def _toggle_device_listener(self, value: int) -> None:
        if not value and Song.selected_device():
            Song.selected_device().toggle()

    @subject_slot("value")
    def _move_loop_left(self, value: int) -> None:
        if not value:
            loop_length = Song.loop_length()
            Song.set_loop_start(max(0.0, Song.loop_start() - Song.loop_length()))
            Song.set_loop_length(loop_length)

    @subject_slot("value")
    def _move_loop_right(self, value: int) -> None:
        if not value:
            loop_length = Song.loop_length()
            Song.set_loop_start(Song.loop_start() + Song.loop_length())
            Song.set_loop_length(loop_length)

    @subject_slot("value")
    def _scroll_device_prev(self, value: int) -> None:
        if not value:
            next_device = Song.selected_track().devices.prev
            if next_device:
                self._container.get(DeviceComponent).select_device(
                    Song.selected_track(), next_device
                )

    @subject_slot("value")
    def _scroll_device_next(self, value: int) -> None:
        if not value:
            next_device = Song.selected_track().devices.next
            if next_device:
                self._container.get(DeviceComponent).select_device(
                    Song.selected_track(), next_device
                )
