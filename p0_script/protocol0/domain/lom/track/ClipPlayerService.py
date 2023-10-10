from functools import partial

from protocol0.domain.lom.song.components.TrackComponent import get_track_by_name
from protocol0.domain.shared.scheduler.BarChangedEvent import BarChangedEvent
from protocol0.domain.shared.scheduler.Scheduler import Scheduler

from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


class ClipPlayerService(object):
    def select_clip(self, track_name: str) -> None:
        track = get_track_by_name(track_name)
        from protocol0.shared.logging.Logger import Logger
        Logger.dev(("select", track))
        if track is None:
            return

        track.clip_slots[Song.selected_scene().index].select()
        track.arm_state.toggle()

    def toggle_clip(self, track_name: str) -> None:
        track = get_track_by_name(track_name)
        from protocol0.shared.logging.Logger import Logger
        Logger.dev(("toggle", track))
        if track is None:
            return

        cs = track.clip_slots[Song.selected_scene().index]

        if cs.clip is None:
            Logger.info("No clip")
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
