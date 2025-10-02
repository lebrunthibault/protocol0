from typing import Iterable

from protocol0.domain.live_set.LiveSet import LiveTrack
from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.shared.scheduler.BarEndingEvent import BarEndingEvent
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


def _get_instrument_clips_from_scene_index(scene_index: int) -> Iterable[MidiClip]:
    return (
        LiveTrack.BASS.get().clip_slots[scene_index].clip,
        LiveTrack.PIANO.get().clip_slots[scene_index].clip,
    )


def _get_instrument_clips() -> Iterable[MidiClip]:
    clips: Iterable[MidiClip] = (
        LiveTrack.BASS.get().playing_clip,
        LiveTrack.PIANO.get().playing_clip,
    )

    if all(clip is not None for clip in clips):
        return clips
    elif all(clip is None for clip in clips):
        return _get_instrument_clips_from_scene_index(Song.selected_scene().index)
    else:
        clip: MidiClip = next(filter(None, clips))
        return _get_instrument_clips_from_scene_index(clip.index)


def move_clip_loop(go_next: bool) -> Sequence:
    def move_clip_loops() -> None:
        clips = _get_instrument_clips()
        increment = 0
        if go_next:
            increment = 1  # no limit to scrolling right unless we check for notes
        else:
            if all(clip.loop.start >= Song.signature_numerator() for clip in clips):
                increment = -1

        increment *= Song.signature_numerator()

        for clip in clips:
            start_marker = clip.loop.start_marker
            clip.loop.start += increment
            clip.loop.end += increment

            clip.loop.start_marker = start_marker  # maintain playback state

    seq = Sequence()
    seq.add(move_clip_loops)
    return seq.done()


def sync_markers() -> None:
    for clip in _get_instrument_clips():
        clip.loop.sync_markers()
        clip.fire()


def change_clip_loop(bar_length: int) -> Sequence:
    seq = Sequence()
    if Song.is_playing():
        seq.wait_for_event(BarEndingEvent)

    def set_clip_loops() -> None:
        for clip in _get_instrument_clips():
            clip.loop.bar_length = bar_length

            if Song.is_playing():
                clip.fire()

    seq.add(set_clip_loops)
    return seq.done()
