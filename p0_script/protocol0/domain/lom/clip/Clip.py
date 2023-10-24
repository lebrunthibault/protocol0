from functools import partial

import Live
from _Framework.SubjectSlot import SlotManager
from typing import Optional, List, cast

from protocol0.domain.lom.clip.ClipAppearance import ClipAppearance
from protocol0.domain.lom.clip.ClipColorEnum import ClipColorEnum
from protocol0.domain.lom.clip.ClipConfig import ClipConfig
from protocol0.domain.lom.clip.ClipLoop import ClipLoop
from protocol0.domain.lom.clip.ClipName import ClipName
from protocol0.domain.lom.clip.ClipPlayingPosition import ClipPlayingPosition
from protocol0.domain.lom.clip.automation.ClipAutomation import ClipAutomation
from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.forward_to import ForwardTo
from protocol0.shared.Song import Song
from protocol0.shared.Undo import Undo
from protocol0.shared.observer.Observable import Observable
from protocol0.shared.sequence.Sequence import Sequence


class Clip(SlotManager, Observable):
    def __init__(self, live_clip: Live.Clip.Clip, index: int, config: ClipConfig) -> None:
        super(Clip, self).__init__()
        self._clip = live_clip
        self.index = index
        self._config = config

        self.deleted = False
        self.selected = False

        self.clip_name: ClipName = ClipName(live_clip)
        self.appearance = ClipAppearance(live_clip, self.clip_name, config.color)
        self.loop: ClipLoop = ClipLoop(live_clip)
        self.automation: ClipAutomation = ClipAutomation(live_clip, self.loop)
        self.playing_position: ClipPlayingPosition = ClipPlayingPosition(
            live_clip, self.loop
        )

        self.loop.register_observer(self)
        self._notes_shown = True

        self.previous_hash = 0

    def __eq__(self, clip: object) -> bool:
        return isinstance(clip, Clip) and self._clip == clip._clip

    def __repr__(self) -> str:
        return "%s: %s (%s)" % (self.__class__.__name__, self.name, self.index)

    def update(self, observable: Observable) -> None:
        if isinstance(observable, ClipLoop):
            self.notify_observers()

    name = cast(str, ForwardTo("clip_name", "name"))
    color = cast(int, ForwardTo("appearance", "color"))
    length = cast(float, ForwardTo("loop", "length"))
    bar_length = cast(float, ForwardTo("loop", "bar_length"))
    looping = cast(bool, ForwardTo("loop", "looping"))

    def get_hash(self, device_parameters: List[DeviceParameter]) -> int:
        raise NotImplementedError

    def matches(self, other: "Clip", device_parameters: List[DeviceParameter]) -> bool:
        return self.get_hash(device_parameters) == other.get_hash(
            device_parameters
        ) and self.loop.matches(other.loop)

    @property
    def is_triggered(self) -> bool:
        return self._clip and self._clip.is_triggered

    @property
    def is_recording(self) -> bool:
        return self._clip and self._clip.is_recording

    @property
    def muted(self) -> bool:
        return self._clip and self._clip.muted

    # noinspection PyPropertyAccess
    @muted.setter
    def muted(self, muted: bool) -> None:
        if self._clip:
            self._clip.muted = muted

    _QUANTIZATION_OPTIONS: List[int] = [
        Live.Song.RecordingQuantization.rec_q_no_q,
        Live.Song.RecordingQuantization.rec_q_quarter,
        Live.Song.RecordingQuantization.rec_q_eight,
        Live.Song.RecordingQuantization.rec_q_eight_triplet,
        Live.Song.RecordingQuantization.rec_q_eight_eight_triplet,
        Live.Song.RecordingQuantization.rec_q_sixtenth,
        Live.Song.RecordingQuantization.rec_q_sixtenth_triplet,
        Live.Song.RecordingQuantization.rec_q_sixtenth_sixtenth_triplet,
        Live.Song.RecordingQuantization.rec_q_thirtysecond,
    ]

    @property
    def is_playing(self: "Clip") -> bool:
        return self._clip and self._clip.is_playing

    @is_playing.setter
    def is_playing(self: "Clip", is_playing: bool) -> None:
        if self._clip:
            self._clip.is_playing = is_playing

    def select(self) -> None:
        self.selected = True
        self.notify_observers()
        self.selected = False

    def blink(self) -> None:
        color = self.color
        self.color = ClipColorEnum.BLINK.value
        Scheduler.wait_ms(1500, partial(setattr, self, "color", color))

    def stop(self, immediate: bool = False, wait_until_end: bool = False) -> None:
        """
        immediate: stop is quantized or not
        until_end: stops the clip when it finished playing
        (equivalent to doing nothing on a non looped clip)
        """
        if immediate:
            if not self.muted:
                self.muted = True
                self.muted = False
            return None

        if wait_until_end:
            if self.playing_position.beats_left <= 1:
                self._clip.stop()
            # else clip will stop in ClipTail
            return None

        if self._clip:
            self._clip.stop()

    def fire(self) -> Optional[Sequence]:
        if self._clip:
            self._clip.fire()
        return None

    def delete(self) -> Sequence:
        self.deleted = True
        self.notify_observers()
        return Sequence().wait(3).done()

    def quantize(self, depth: float = 1) -> None:
        if self._clip:
            Undo.begin_undo_step()

            midi_quantization = Song.midi_recording_quantization()
            if midi_quantization == Live.Song.RecordingQuantization.rec_q_no_q:
                midi_quantization = Live.Song.RecordingQuantization.rec_q_eight

            record_quantization_index = self._QUANTIZATION_OPTIONS.index(midi_quantization)
            if record_quantization_index:
                self._clip.quantize(record_quantization_index, depth)
            Undo.end_undo_step()

    @property
    def has_tail(self) -> bool:
        return self.loop.end_marker > self.loop.end

    def remove_tail(self) -> None:
        self.loop.end = self.loop.end

    def crop_to_tail(self) -> None:
        loop_end = self.loop.end
        self.loop.end = self.loop.end_marker
        self.loop.start = loop_end
        self.loop.looping = False

    def show_loop(self) -> None:
        self._clip.view.show_loop()

    def show_notes(self) -> None:
        self.automation.show_envelope()
        self.automation.hide_envelope()

    def toggle_notes(self) -> None:
        if self._notes_shown:
            self.automation.show_envelope()
        else:
            self.automation.hide_envelope()

        self._notes_shown = not self._notes_shown

    def on_added(self) -> Optional[Sequence]:
        """overridden"""
        pass

    def crop(self) -> Optional[Sequence]:
        """implemented in MidiClip and AudioClip"""
        raise NotImplementedError

    def post_record(self, _: int) -> None:
        self.clip_name.update("")

    def disconnect(self) -> None:
        super(Clip, self).disconnect()
        self.clip_name.disconnect()
        self.loop.disconnect()
