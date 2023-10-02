from protocol0.application.command.LogSongStatsCommand import LogSongStatsCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.audit.SongStatsService import SongStatsService


class LogSongStatsCommandHandler(CommandHandlerInterface):
    def handle(self, command: LogSongStatsCommand) -> None:
        self._container.get(SongStatsService).display_song_stats()