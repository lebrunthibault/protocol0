from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger


class TrackPlayerService(object):
    def play_pause_track(self, track_name: str) -> None:
        track = find_if(lambda t: t.name.lower() == track_name.lower(), Song.simple_tracks())

        if track is None:
            Logger.warning(f"Could not find track '{track_name}' in set")
            return

        if len(track.clips) == 0:
            Logger.warning(f"track '{track_name}' has no clip to play")
            return

        if track.is_playing:
            track.stop()
        else:
            track.clips[0].is_playing = True