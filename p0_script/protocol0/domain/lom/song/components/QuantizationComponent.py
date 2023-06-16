import Live
from _Framework.SubjectSlot import SlotManager

from protocol0.domain.lom.song.components.TempoComponent import TempoComponent


class QuantizationComponent(SlotManager):
    def __init__(self, song: Live.Song.Song, tempo_component: TempoComponent) -> None:
        super(QuantizationComponent, self).__init__()
        self._song = song
        self._tempo_component = tempo_component

    @property
    def midi_recording_quantization(self) -> int:
        return self._song.midi_recording_quantization

    @midi_recording_quantization.setter
    def midi_recording_quantization(self, midi_recording_quantization: int) -> None:
        if self._song:
            self._song.midi_recording_quantization = midi_recording_quantization

    @property
    def clip_trigger_quantization(self) -> int:
        return self._song.clip_trigger_quantization

    @clip_trigger_quantization.setter
    def clip_trigger_quantization(self, clip_trigger_quantization: int) -> None:
        self._song.clip_trigger_quantization = clip_trigger_quantization
