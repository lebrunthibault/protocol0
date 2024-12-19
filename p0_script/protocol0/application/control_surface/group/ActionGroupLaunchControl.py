from functools import partial
from typing import List, Optional

from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import MIDI_NOTE_TYPE, MIDI_CC_TYPE
from _Framework.SubjectSlot import subject_slot, SlotManager

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.application.control_surface.TrackEncoder import TrackEncoder, MidiIdentifiers
from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceService import find_parent_rack
from protocol0.domain.lom.device.RackDevice import RackDevice
from protocol0.domain.lom.device.SimpleTrackDevices import SimpleTrackDevices
from protocol0.domain.lom.song.components.DeviceComponent import DeviceComponent
from protocol0.domain.lom.song.components.TrackComponent import TrackComponent
from protocol0.domain.lom.track.ControlledTracks import ControlledTracksRegistry
from protocol0.domain.lom.track.ControlledTracksEnum import ControlledTracksEnum
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.error_handler import handle_errors
from protocol0.domain.shared.utils.timing import debounce
from protocol0.domain.shared.utils.utils import map_to_range
from protocol0.shared.Song import Song


@handle_errors()
def _scroll_macro_control(macro_index: int, value: int) -> None:
    device: Optional[Device] = Song.selected_device()

    if device and not isinstance(device, RackDevice):
        device = find_parent_rack(Song.selected_track(), device)

    assert device, "Device is not a rack"

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

            self._scroll_loop_length.subject = ButtonElement(True, MIDI_CC_TYPE, 1, 36)
            self._move_loop_left.subject = ButtonElement(True, MIDI_CC_TYPE, 1, 104)
            self._move_loop_right.subject = ButtonElement(True, MIDI_CC_TYPE, 1, 105)

            def get_devices() -> SimpleTrackDevices:
                return Song.selected_track().devices

            self.add_encoder(
                identifier=106,
                name="scroll devices prev",
                on_press=lambda: partial(self._select_track_device, get_devices().prev),
                on_long_press=lambda: partial(self._select_track_device, get_devices().first),
                use_cc=True,
            )

            self.add_encoder(
                identifier=107,
                name="scroll devices next",
                on_press=lambda: partial(self._select_track_device, get_devices().next),
                on_long_press=lambda: partial(self._select_track_device, get_devices().last),
                use_cc=True,
            )

            self._toggle_master_view.subject = ButtonElement(True, MIDI_NOTE_TYPE, 1, 108)

            for macro_index, cc_number in enumerate((29, 30, 31, 32, 49, 50, 51, 52)):
                getattr(self, f"_scroll_macro_control_{macro_index}").subject = ButtonElement(
                    True, MIDI_CC_TYPE, 1, cc_number
                )

        controlled_tracks = (
            (
                ControlledTracksRegistry[ControlledTracksEnum.DRUMS],
                MidiIdentifiers(73, 41, 13),
            ),
            (
                ControlledTracksRegistry[ControlledTracksEnum.KICK],
                MidiIdentifiers(74, 42, 14),
            ),
            (
                ControlledTracksRegistry[ControlledTracksEnum.HAT],
                MidiIdentifiers(75, 43, 15),
            ),
            (ControlledTracksRegistry[ControlledTracksEnum.PERC], MidiIdentifiers(76, 44, 16)),
            (ControlledTracksRegistry[ControlledTracksEnum.HARMONY], MidiIdentifiers(89, 57, 17)),
            (ControlledTracksRegistry[ControlledTracksEnum.MELODY], MidiIdentifiers(90, 58, 18)),
            (
                ControlledTracksRegistry[ControlledTracksEnum.BASS],
                MidiIdentifiers(91, 59, 19),
            ),
            (ControlledTracksRegistry[ControlledTracksEnum.SUB], MidiIdentifiers(92, 60, 20)),
        )

        # noinspection PyAttributeOutsideInit
        self.encoders: List[TrackEncoder] = []

        for controlled_track, midi_identifiers in controlled_tracks:
            self.encoders.append(
                TrackEncoder(
                    channel=self.CHANNEL,
                    controlled_tracks=controlled_track,
                    midi_identifiers=midi_identifiers,
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
            Song.jump_to_prev_cue()

    @subject_slot("value")
    def _move_loop_right(self, value: int) -> None:
        if not value:
            Song.jump_to_next_cue()

    def _select_track_device(self, device: Optional[Device]) -> None:
        if device:
            self._container.get(DeviceComponent).select_device(Song.selected_track(), device)

    @subject_slot("value")
    def _toggle_master_view(self, value: int) -> None:
        if not value:
            if Song.selected_track() != Song.master_track():
                self._PREVIOUS_SELECTED_TRACK = Song.selected_track()
                self._PREVIOUS_SELECTED_TRACK_CLIP_VIEW = ApplicationView.is_clip_view_visible()

                Song.master_track().select()
                ApplicationView.show_device()
                Backend.client().show_plugins()
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
