from typing import List, Optional

from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import MIDI_NOTE_TYPE, MIDI_CC_TYPE
from _Framework.SubjectSlot import subject_slot, SlotManager

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.application.control_surface.TrackEncoder import TrackEncoder, ControlledTrack
from protocol0.domain.lom.device.RackDevice import RackDevice
from protocol0.domain.lom.song.components.DeviceComponent import DeviceComponent
from protocol0.domain.lom.song.components.PlaybackComponent import PlaybackComponent
from protocol0.domain.lom.song.components.TrackComponent import TrackComponent
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.utils.timing import debounce
from protocol0.domain.shared.utils.utils import map_to_range
from protocol0.shared.Song import Song, find_track


def _scroll_macro_control(macro_index: int, value: int) -> None:
    device = Song.selected_device()
    assert isinstance(device, RackDevice), "Device is not a rack"

    macro_index += 1

    macros_count = device.macros_count

    index_to_macro = {}
    if macros_count == 1:
        index_to_macro = {1: 1}
    elif macros_count == 2:
        index_to_macro = {1: 1, 5: 2}
    elif macros_count == 3 or macros_count == 4:
        index_to_macro = {1: 1, 2: 2, 5: 3, 6: 4}
    elif macros_count == 5 or macros_count == 6:
        index_to_macro = {1: 1, 2: 2, 3: 3, 5: 4, 6: 5, 7: 6}
    elif macros_count == 7 or macros_count == 8:
        index_to_macro = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8}

    assert macro_index in index_to_macro, "Macro not mapped"

    param = device.parameters[index_to_macro[macro_index]]
    param.set_value(value, 0, 127)


class ActionGroupLaunchControl(ActionGroupInterface, SlotManager):
    CHANNEL = 2
    _PREVIOUS_SELECTED_TRACK: Optional[SimpleTrack] = None
    _PREVIOUS_SELECTED_TRACK_CLIP_VIEW = False

    def configure(self) -> None:
        with self._component_guard():
            self._un_solo_listener.subject = ButtonElement(True, MIDI_NOTE_TYPE, 1, 107)
            self._toggle_device_listener.subject = ButtonElement(True, MIDI_NOTE_TYPE, 1, 105)

            self._move_loop_left.subject = ButtonElement(True, MIDI_CC_TYPE, 1, 104)
            self._move_loop_right.subject = ButtonElement(True, MIDI_CC_TYPE, 1, 105)

            self._scroll_device_prev.subject = ButtonElement(True, MIDI_CC_TYPE, 1, 106)
            self._scroll_device_next.subject = ButtonElement(True, MIDI_CC_TYPE, 1, 107)

            self._toggle_master_view.subject = ButtonElement(True, MIDI_NOTE_TYPE, 1, 108)

            for macro_index, cc_number in enumerate((29, 30, 31, 32, 49, 50, 51, 52)):
                getattr(self, f"_scroll_macro_control_{macro_index}").subject = ButtonElement(
                    True, MIDI_CC_TYPE, 1, cc_number
                )

            self._scroll_loop_length.subject = ButtonElement(True, MIDI_CC_TYPE, 1, 36)

        def find_kick() -> SimpleTrack:
            return find_track("Kick", is_foldable=False)

        controlled_tracks = (
            ControlledTrack("Kick", 73, 41, 13, False, select_getter=find_kick),
            ControlledTrack("Hat", 74, 42, 14, False),
            ControlledTrack("Perc", 75, 43, 15, False, track_names=["Perc", "FX"]),
            ControlledTrack("Vocals", 76, 44, 16, True),
            ControlledTrack("Harmony", 89, 57, 17, True),
            ControlledTrack("Lead", 90, 58, 18, True),
            ControlledTrack("Bass", 91, 59, 19, True),
            ControlledTrack("Sub", 92, 60, 20, False),
        )

        # noinspection PyAttributeOutsideInit
        self.encoders: List[TrackEncoder] = []

        for controlled_track in controlled_tracks:
            self.encoders.append(
                TrackEncoder(
                    channel=self.CHANNEL,
                    controlled_track=controlled_track,
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

            # self._container.get(PlaybackComponent).restart()
            # time = (60.0 / Song.tempo()) * Song.loop_start()
            # Song.set_current_song_time(time)

    @subject_slot("value")
    def _move_loop_right(self, value: int) -> None:
        if not value:
            loop_length = Song.loop_length()
            Song.set_loop_start(Song.loop_start() + Song.loop_length())
            Song.set_loop_length(loop_length)

            self._container.get(PlaybackComponent).restart()

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

    @subject_slot("value")
    def _toggle_master_view(self, value: int) -> None:
        if not value:
            if Song.selected_track() != Song.master_track():
                self._PREVIOUS_SELECTED_TRACK = Song.selected_track()
                self._PREVIOUS_SELECTED_TRACK_CLIP_VIEW = ApplicationView.is_clip_view_visible()

                Song.master_track().select(un_collapse=False)
                ApplicationView.show_device()
            else:
                if self._PREVIOUS_SELECTED_TRACK:
                    self._PREVIOUS_SELECTED_TRACK.select()
                    if self._PREVIOUS_SELECTED_TRACK_CLIP_VIEW:
                        ApplicationView.show_clip()

    @subject_slot("value")
    def _scroll_macro_control_0(self, value: int) -> None:
        _scroll_macro_control(0, value)

    @subject_slot("value")
    def _scroll_macro_control_1(self, value: int) -> None:
        _scroll_macro_control(1, value)

    @subject_slot("value")
    def _scroll_macro_control_2(self, value: int) -> None:
        _scroll_macro_control(2, value)

    @subject_slot("value")
    def _scroll_macro_control_3(self, value: int) -> None:
        _scroll_macro_control(3, value)

    @subject_slot("value")
    def _scroll_macro_control_4(self, value: int) -> None:
        _scroll_macro_control(4, value)

    @subject_slot("value")
    def _scroll_macro_control_5(self, value: int) -> None:
        _scroll_macro_control(5, value)

    @subject_slot("value")
    def _scroll_macro_control_6(self, value: int) -> None:
        _scroll_macro_control(6, value)

    @subject_slot("value")
    def _scroll_macro_control_7(self, value: int) -> None:
        _scroll_macro_control(7, value)

    @subject_slot("value")
    def _scroll_macro_control_8(self, value: int) -> None:
        _scroll_macro_control(8, value)

    @subject_slot("value")
    @debounce(duration=50)
    def _scroll_loop_length(self, value: int) -> None:
        values = (1, 2, 4, 8, 16)
        loop_index = map_to_range(value, 0, 127, 0, 4)
        Song.set_loop_length(values[loop_index] * Song.signature_numerator())
