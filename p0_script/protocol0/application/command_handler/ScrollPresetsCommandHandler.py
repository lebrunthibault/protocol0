from protocol0.application.command.ScrollPresetsCommand import ScrollPresetsCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.Song import Song


class ScrollPresetsCommandHandler(CommandHandlerInterface):
    def handle(self, command: ScrollPresetsCommand) -> None:
        track = Song.selected_track()
        if track.instrument:
            if not track.arm_state.is_armed:
                track.arm_state.arm()

            Scheduler.defer(
                lambda: Song.selected_track().instrument.preset_list.scroll(command.go_next)
            )
