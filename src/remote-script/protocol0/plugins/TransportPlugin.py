"""Transport actions: playback, tempo, metronome, record toggles, cues, undo.

Value specs follow the catalog's uniform grammar (see domain/lom/addressing):
booleans take ON / OFF / TGL, the tempo takes BPM values or < / > steps, the
quantizations take an option name or < / > cycling.
"""
from typing import Optional

from protocol0.application.http.HttpServer import get_container
from protocol0.application.plugin.PluginInterface import PluginInterface
from protocol0.application.plugin.action import action
from protocol0.domain.lom.addressing.values import (
    resolve_adjustable,
    resolve_bool,
    resolve_quasi_continuous,
)
from protocol0.domain.lom.song.components.PlaybackComponent import PlaybackComponent
from protocol0.domain.lom.song.components.QuantizationComponent import QuantizationComponent
from protocol0.domain.lom.song.components.RecordingComponent import RecordingComponent
from protocol0.domain.lom.song.components.TempoComponent import TempoComponent
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence

# Live.Song.Quantization order (index = Live enum value)
_CLIP_QUANTIZATIONS = [
    "none",
    "8_bars",
    "4_bars",
    "2_bars",
    "bar",
    "half",
    "half_triplet",
    "quarter",
    "quarter_triplet",
    "eighth",
    "eighth_triplet",
    "sixteenth",
    "sixteenth_triplet",
    "thirty_second",
]

# Live.Song.RecordingQuantization order (index = Live enum value)
_MIDI_QUANTIZATIONS = [
    "none",
    "quarter",
    "eighth",
    "eighth_triplet",
    "eighth_and_triplet",
    "sixteenth",
    "sixteenth_triplet",
    "sixteenth_and_triplet",
    "thirty_second",
]


class TransportPlugin(PluginInterface):
    name = "transport"

    @action
    def play_pause(self) -> None:
        """Toggle playback: start if stopped, stop if playing."""
        get_container().get(PlaybackComponent).play_pause()

    @action
    def start_playback(self) -> None:
        """Start playing the set."""
        get_container().get(PlaybackComponent).start_playing()

    @action
    def stop_playback(self) -> Sequence:
        """Stop playback and all clips."""
        return get_container().get(PlaybackComponent).stop()

    @action
    def stop_all_clips(self) -> None:
        """Stop every playing session clip (playback keeps running)."""
        get_container().get(PlaybackComponent).stop_all_clips()

    @action
    def restart_playback(self) -> None:
        """Stop then restart playback from the beginning."""
        get_container().get(PlaybackComponent).restart()

    @action
    def metronome(self, value: str = "TGL") -> None:
        """Set the metronome (value: ON, OFF or TGL)."""
        playback = get_container().get(PlaybackComponent)
        playback.metronome = resolve_bool(value, playback.metronome)

    @action
    def tempo(self, value: str) -> None:
        """Set the tempo (value: BPM like "124", or < / > steps like ">5")."""
        component = get_container().get(TempoComponent)
        component.tempo = resolve_quasi_continuous(value, component.tempo, 20.0, 999.0)

    @action
    def session_record(self, value: str = "TGL") -> None:
        """Set session record (value: ON, OFF or TGL)."""
        recording = get_container().get(RecordingComponent)
        recording.session_record = resolve_bool(value, recording.session_record)

    @action
    def back_to_arranger(self) -> None:
        """Resume arrangement playback (disables the session override)."""
        get_container().get(RecordingComponent).back_to_arranger = False

    @action
    def clip_trigger_quantization(self, value: str) -> None:
        """Set the global launch quantization (value: none, 8_bars, 4_bars, 2_bars,
        bar, half, half_triplet, quarter, quarter_triplet, eighth, eighth_triplet,
        sixteenth, sixteenth_triplet, thirty_second, or < / > cycling)."""
        component = get_container().get(QuantizationComponent)
        current = _CLIP_QUANTIZATIONS[component.clip_trigger_quantization]
        component.clip_trigger_quantization = _CLIP_QUANTIZATIONS.index(
            resolve_adjustable(value, _CLIP_QUANTIZATIONS, current)
        )

    @action
    def midi_recording_quantization(self, value: str) -> None:
        """Set the MIDI record quantization (value: none, quarter, eighth,
        eighth_triplet, eighth_and_triplet, sixteenth, sixteenth_triplet,
        sixteenth_and_triplet, thirty_second, or < / > cycling)."""
        component = get_container().get(QuantizationComponent)
        current = _MIDI_QUANTIZATIONS[component.midi_recording_quantization]
        component.midi_recording_quantization = _MIDI_QUANTIZATIONS.index(
            resolve_adjustable(value, _MIDI_QUANTIZATIONS, current)
        )

    @action
    def jump_to_cue(self, direction: str = ">") -> None:
        """Jump to the next (>) or previous (<) cue marker."""
        if direction.strip() == "<":
            Song.jump_to_prev_cue()
        else:
            Song.jump_to_next_cue()

    @action
    def capture_midi(self) -> Optional[Sequence]:
        """Capture the recently played MIDI into a clip."""
        return Song.capture_midi()

    @action
    def undo(self) -> None:
        """Undo the last Live action."""
        Song.undo()

    @action
    def redo(self) -> None:
        """Redo the last undone Live action."""
        Song.redo()
