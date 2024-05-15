import time
from typing import Optional, Callable

from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import MIDI_NOTE_TYPE, MIDI_CC_TYPE
from _Framework.SubjectSlot import subject_slot, SlotManager

from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.utils.error import log_exceptions
from protocol0.shared.Song import find_track


class TrackEncoder(SlotManager):
    LONG_PRESS_THRESHOLD = 0.25  # maximum time in seconds we consider a simple press

    def __init__(
        self,
        channel: int,
        track_select_note: int,
        solo_mute_note: int,
        volume_cc: int,
        track_name: str,
        is_top_track: bool,
        component_guard: Callable,
    ) -> None:
        super(TrackEncoder, self).__init__()

        channel -= 1

        self._track_name = track_name
        self._is_top_track = is_top_track

        with component_guard():
            self._track_select_listener.subject = ButtonElement(
                True, MIDI_NOTE_TYPE, channel, track_select_note
            )
            self._solo_mute_listener.subject = ButtonElement(
                True, MIDI_NOTE_TYPE, channel, solo_mute_note
            )
            self._volume_listener.subject = ButtonElement(True, MIDI_CC_TYPE, channel, volume_cc)

        self._pressed_at: Optional[float] = None

    def __repr__(self) -> str:
        return f"TrackEncoder('{self._track_name}')"

    @property
    def track(self) -> SimpleTrack:
        track = find_track(self._track_name, exact=False, is_top=self._is_top_track)
        assert track, f"Couldn't find track '{self._track_name}'"

        return track

    @property
    def _is_long_pressed(self) -> bool:
        return bool(
            self._pressed_at and (time.time() - self._pressed_at) > self.LONG_PRESS_THRESHOLD
        )

    @subject_slot("value")
    @log_exceptions
    def _solo_mute_listener(self, value: int) -> None:
        from protocol0.shared.logging.Logger import Logger

        Logger.dev(f"_solo_mute_listener: {self}, {value}")
        if value:
            self._pressed_at = time.time()
        else:
            if self._is_long_pressed:
                self.track.solo_toggle()
            else:
                self.track.toggle()

    @subject_slot("value")
    @log_exceptions
    def _track_select_listener(self, value: int) -> None:
        from protocol0.shared.logging.Logger import Logger

        Logger.dev(f"_track_select_listener: {self}, {value}")
        if not value:
            self.track.select()

    @subject_slot("value")
    @log_exceptions
    def _volume_listener(self, value: int) -> None:
        from protocol0.shared.logging.Logger import Logger

        Logger.dev(f"volume cc value: {self}, {value}")
        pass


#
#  @subject_slot("value")
#  def _scroll_listener(self, value: int) -> None:
#      self._find_and_execute_action(move_type=EncoderMoveEnum.SCROLL, go_next=value == 1)
#
