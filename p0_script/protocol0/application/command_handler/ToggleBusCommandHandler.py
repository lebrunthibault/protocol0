from protocol0.application.command.ToggleBusCommand import (
    ToggleBusCommand,
)
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.Song import find_track


class ToggleBusCommandHandler(CommandHandlerInterface):
    def handle(self, command: ToggleBusCommand) -> None:
        # unmute all buses
        if not command.bus_name:
            for bus in ("drums", "bass", "vocals", "lead", "fx", "background"):
                bus_track = find_track(bus, exact=False, is_foldable=True)
                if bus_track and bus_track.muted:
                    bus_track.muted = False

            return None

        bus_track = find_track(command.bus_name, exact=False, is_foldable=True)

        assert bus_track, f"Cannot find bus {command.bus_name}"

        bus_track.toggle()
