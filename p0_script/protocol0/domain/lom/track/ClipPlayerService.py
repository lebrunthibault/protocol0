from functools import partial

from protocol0.domain.lom.song.components.TrackComponent import get_track_by_name
from protocol0.domain.shared.scheduler.BarChangedEvent import BarChangedEvent
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class ClipPlayerService(object):
    def select_clip(self, track_name: str) -> None:
        track = get_track_by_name(track_name)
        if track is None:
            return

        track.is_folded = False
        track.clip_slots[Song.selected_scene().index].select()
        track.arm_state.toggle()

    def toggle_clip(self, track_name: str) -> None:
        track = get_track_by_name(track_name)
        if track is None:
            return

        scene_index = Song.selected_scene().index
        cs = track.clip_slots[scene_index]

        if cs.clip is None:
            # look for another clip to copy in previous or next scenes
            other_clip_slots = list(reversed(track.clip_slots[:scene_index])) + track.clip_slots[scene_index:]
            previous_or_next_cs = next((cs for cs in other_clip_slots if cs.clip), None)
            if previous_or_next_cs is None:
                Logger.info("No clip")
            else:
                previous_or_next_cs.duplicate_clip_to(cs)
                seq = Sequence()
                if previous_or_next_cs.clip.muted:
                    seq.defer()
                    seq.add(lambda: setattr(cs.clip, "muted", False))
                seq.defer()
                seq.add(lambda: setattr(cs.clip, "is_playing", True))
                seq.done()
                return

        if cs.clip.muted:
            cs.clip.muted = False

        if cs.clip.is_playing:
            cs.clip.stop()
            seq = Sequence()
            seq.wait_for_event(BarChangedEvent)
            seq.add(partial(setattr, cs.clip, "muted", True))
            seq.done()
        else:
            Scheduler.defer(partial(setattr, cs.clip, "is_playing", True))
