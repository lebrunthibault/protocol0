from typing import List

from protocol0.application.command.SoloTracksCommand import SoloTracksCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.song.components.TrackComponent import TrackComponent
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.shared.Song import Song, find_track


class SoloTracksCommandHandler(CommandHandlerInterface):
    _PREVIOUS_SOLO_TRACKS: List[SimpleTrack] = []

    def handle(self, command: SoloTracksCommand) -> None:
        solo_tracks = [t for t in Song.simple_tracks() if t.solo]

        if command.solo_type == "UN_SOLO":
            if solo_tracks:
                SoloTracksCommandHandler._PREVIOUS_SOLO_TRACKS = solo_tracks
                self._container.get(TrackComponent).un_solo_all_tracks()
            else:
                for track in self._PREVIOUS_SOLO_TRACKS:
                    track.solo = True
                    SoloTracksCommandHandler._PREVIOUS_SOLO_TRACKS = []

            return

        self._container.get(TrackComponent).un_solo_all_tracks()

        if command.solo_type == "KICK_SUB":
            find_track("kick").solo = True
            find_track("sub").solo = True
        elif command.solo_type == "KICK_BASS":
            find_track("kick").solo = True
            find_track("bass", exact=False, is_foldable=True).solo = True
        else:
            raise Protocol0Error(f"Unhandled solo type: '{command.solo_type}'")
