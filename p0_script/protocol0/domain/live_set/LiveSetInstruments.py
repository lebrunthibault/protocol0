from typing import Iterable, List

from protocol0.domain.live_set.LiveSet import LiveTrack
from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.track.simple_track.midi.SimpleMidiTrack import SimpleMidiTrack
from protocol0.domain.shared.scheduler.BarEndingEvent import BarEndingEvent
from protocol0.shared.Song import Song
from protocol0.shared.logging.StatusBar import StatusBar
from protocol0.shared.sequence.Sequence import Sequence


def _get_tracks(include_vocals: bool) -> Iterable[SimpleMidiTrack]:
    tracks = [
        LiveTrack.BASS.get(),
        LiveTrack.SYNTH.get(),
        LiveTrack.PIANO.get(),
    ]

    if include_vocals:
        tracks.append(LiveTrack.VOCALS.get())

    return tracks


def _get_instrument_clips(include_vocals: bool = False) -> List[MidiClip]:
    return list(filter(None, (track.playing_clip for track in _get_tracks(include_vocals))))


def move_clip_loop(go_next: bool) -> Sequence:
    def move_clip_loops() -> None:
        clips = _get_instrument_clips()

        if go_next:
            increment = 1  # no limit to scrolling right unless we check for notes
        else:
            increment = -1

            if all(clip.loop.start < Song.signature_numerator() for clip in clips):
                StatusBar.show_message("Reached 1.1.1 on all clips")
                return None

        increment *= Song.signature_numerator()

        for clip in list(clips):
            start_marker = clip.loop.start_marker
            if increment > 0:
                clip.loop.end += increment
                clip.loop.start += increment
            elif clip.loop.start >= Song.signature_numerator():
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


def scrub_clips(bar_number: int) -> None:
    for clip in _get_instrument_clips():
        scrub_position = ((bar_number - 1) * Song.signature_numerator()) + clip.loop.start
        if scrub_position < clip.loop.end:
            clip.scrub(scrub_position)
