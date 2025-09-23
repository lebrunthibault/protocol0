from protocol0.application.command.BusTrackToZeroDBCommand import BusTrackToZeroDBCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.set.MixingService import balance_bus_levels_to_zero
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.Song import Song


class BusTrackToZeroDBCommandHandler(CommandHandlerInterface):
    def handle(self, command: BusTrackToZeroDBCommand) -> None:
        if Song.selected_track() == Song.master_track():
            bus_compressors = Song.master_track().balance_levels_to_zero()
        else:
            bus_compressors = balance_bus_levels_to_zero(Song.selected_track())

        if not bus_compressors:
            return None

        message = [f"{track}: {compressors}\n" for track, compressors in bus_compressors.items()]
        Backend.client().show_warning(f"Update bus compressors:\n\n{message}")
