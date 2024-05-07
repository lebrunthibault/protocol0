from typing import Optional

from protocol0.application.command.SelectTrackCommand import SelectTrackCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.track.simple_track.audio.master.MasterTrack import MasterTrack
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.Song import Song


class SelectTrackCommandHandler(CommandHandlerInterface):
    def handle(self, command: SelectTrackCommand) -> None:
        track: Optional[MasterTrack]

        if command.track_name.lower() == "master":
            track = Song.master_track()
        else:
            track = find_if(
                lambda t: t.lower_name == command.track_name.strip().lower(), Song.simple_tracks()
            )

        assert track is not None, "Couldn't find track %s" % command.track_name

        track.select()
