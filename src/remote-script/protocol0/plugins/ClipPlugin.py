"""Clip actions over the addressing grammar (session view).

A clip is targeted by a track spec (`track`, default SEL) plus a clip spec
(`clip`, default SEL = the track's clip in the selected scene; or a 1-based
scene index, or a name). MIDI-only actions raise a clean warning on audio clips.
"""
from typing import Optional

from protocol0.application.plugin.PluginInterface import PluginInterface
from protocol0.application.plugin.action import action
from protocol0.domain.lom.addressing.clip import resolve_clip
from protocol0.domain.lom.addressing.scene import resolve_scene
from protocol0.domain.lom.addressing.track import resolve_track
from protocol0.domain.lom.addressing.values import resolve_bool
from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.note.Note import Note
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.shared.sequence.Sequence import Sequence


def _midi_clip(track: str, clip: str) -> MidiClip:
    target = resolve_clip(track, clip)
    if not isinstance(target, MidiClip):
        raise Protocol0Warning("'%s' is not a MIDI clip" % target.name)
    return target


class ClipPlugin(PluginInterface):
    name = "clip"

    @action
    def fire(self, track: str = "SEL", clip: str = "SEL") -> None:
        """Fire (launch) a clip."""
        resolve_clip(track, clip).fire()

    @action
    def stop(self, track: str = "SEL", clip: str = "SEL") -> None:
        """Stop a playing clip (quantized)."""
        resolve_clip(track, clip).stop()

    @action
    def create(self, track: str = "SEL", scene: str = "SEL") -> Optional[Sequence]:
        """Create a 1-bar MIDI clip in the given track / scene slot."""
        target = resolve_track(track)
        scene_index = resolve_scene(scene).index
        clip_slots = target.clip_slots
        if scene_index >= len(clip_slots):
            raise Protocol0Warning("no clip slot %d on '%s'" % (scene_index + 1, target.name))
        return clip_slots[scene_index].create_clip()

    @action
    def delete(self, track: str = "SEL", clip: str = "SEL") -> Sequence:
        """Delete a clip."""
        return resolve_clip(track, clip).delete()

    @action
    def rename(self, name: str, track: str = "SEL", clip: str = "SEL") -> None:
        """Rename a clip."""
        resolve_clip(track, clip).name = name

    @action
    def loop(self, value: str = "TGL", track: str = "SEL", clip: str = "SEL") -> None:
        """Set clip looping (value: ON, OFF or TGL)."""
        target = resolve_clip(track, clip)
        target.looping = resolve_bool(value, target.looping)

    @action
    def loop_start(self, start: float, track: str = "SEL", clip: str = "SEL") -> None:
        """Set the clip loop start (in beats)."""
        resolve_clip(track, clip).loop.start = start

    @action
    def loop_end(self, end: float, track: str = "SEL", clip: str = "SEL") -> None:
        """Set the clip loop end (in beats)."""
        resolve_clip(track, clip).loop.end = end

    @action
    def mute(self, value: str = "TGL", track: str = "SEL", clip: str = "SEL") -> None:
        """Mute (deactivate) a clip (value: ON, OFF or TGL)."""
        target = resolve_clip(track, clip)
        target.muted = resolve_bool(value, target.muted)

    @action
    def add_note(
        self,
        pitch: int,
        start: float,
        duration: float,
        velocity: int = 100,
        track: str = "SEL",
        clip: str = "SEL",
    ) -> Optional[Sequence]:
        """Add a MIDI note (pitch 0-127, start and duration in beats)."""
        return _midi_clip(track, clip).add_note(Note(pitch, start, duration, velocity))

    @action
    def clear_notes(self, track: str = "SEL", clip: str = "SEL") -> Optional[Sequence]:
        """Remove every note of a MIDI clip."""
        return _midi_clip(track, clip).clear_notes()

    @action
    def transpose(self, semitones: int, track: str = "SEL", clip: str = "SEL") -> Optional[Sequence]:
        """Transpose every note of a MIDI clip by the given semitones."""
        return _midi_clip(track, clip).transpose(semitones)

    @action
    def scale_velocities(
        self, direction: str = "<", track: str = "SEL", clip: str = "SEL"
    ) -> None:
        """Compress (<) or expand (>) the velocity spread of a MIDI clip."""
        _midi_clip(track, clip).scale_velocities(go_next=direction.strip() == ">")

    @action
    def remove_muted_notes(self, track: str = "SEL", clip: str = "SEL") -> Optional[Sequence]:
        """Remove the muted notes of a MIDI clip."""
        # Returned so the undo step closes once the clip is rewritten (a tick
        # later). None when nothing was muted.
        return _midi_clip(track, clip).remove_muted_notes()
