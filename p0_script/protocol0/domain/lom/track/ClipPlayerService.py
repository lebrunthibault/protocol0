from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger


class ClipPlayerService(object):
    def toggle_clip(self, track_name: str) -> None:
        track = find_if(lambda t: t.name.lower() == track_name.lower(), Song.simple_tracks())

        if track is None:
            Logger.warning(f"Could not find track '{track_name}' in set")
            return

        clip = track.clip_slots[Song.selected_scene().index].clip

        Logger.dev((clip, track))

        if clip is None:
            track.arm_state.arm()
            return

        if track.is_playing:
            track.stop()
        else:
            clip.is_playing = True