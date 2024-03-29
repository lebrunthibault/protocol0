from typing import Optional

from protocol0.application.command.SelectTrackCommand import SelectTrackCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.Song import Song


class SelectTrackCommandHandler(CommandHandlerInterface):
    _PREVIOUS_SELECT_TRACK: Optional[SimpleTrack] = None

    def handle(self, command: SelectTrackCommand) -> None:
        if command.track_name.lower() == "master":
            track = Song.master_track()
        else:
            track = find_if(lambda t: t.name == command.track_name, Song.simple_tracks())

        assert track is not None, "Couldn't find track %s" % command.track_name

        cls = SelectTrackCommandHandler

        if Song.selected_track() == track and cls._PREVIOUS_SELECT_TRACK:
            cls._PREVIOUS_SELECT_TRACK.select()
        else:
            cls._PREVIOUS_SELECT_TRACK = Song.selected_track()
            track.select()
