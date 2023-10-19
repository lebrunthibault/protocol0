from protocol0.application.command.ScrollPresetsCommand import ScrollPresetsCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.Song import Song


class ScrollPresetsCommandHandler(CommandHandlerInterface):
    def handle(self, command: ScrollPresetsCommand) -> None:
        track = Song.selected_track()
        if track.instrument:
            if track.solo and Song.armed_or_selected_track() != track:
                track.arm_state.arm()
            Song.selected_track().instrument.preset_list.scroll(command.go_next)
