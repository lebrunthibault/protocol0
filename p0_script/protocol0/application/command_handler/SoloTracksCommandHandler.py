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
        if command.bus_name:
            bus_track = find_track(command.bus_name, exact=False, is_foldable=True)

            assert bus_track, f"Cannot find bus {command.bus_name}"
            solo_active = bus_track.solo

            self._container.get(TrackComponent).un_solo_all_tracks()

            if not solo_active:
                bus_track.solo_toggle()

            return None

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

        if command.solo_type == "KICK_SUB":
            tracks_to_solo = (find_track("kick"), find_track("sub"))
        elif command.solo_type == "KICK_BASS":
            tracks_to_solo = (find_track("kick"), find_track("bass", exact=False, is_foldable=True))
        else:
            raise Protocol0Error(f"Unhandled solo type: '{command.solo_type}'")

        solo_active = all(t.solo for t in tracks_to_solo)

        self._container.get(TrackComponent).un_solo_all_tracks()

        if not solo_active:
            for track_to_solo in tracks_to_solo:
                track_to_solo.solo = True
