from functools import partial

from protocol0.application.command.ReloadGodParticleCommand import (
    ReloadGodParticleCommand,
)
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device.DeviceService import DeviceService
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


class ReloadGodParticleCommandHandler(CommandHandlerInterface):
    def handle(self, command: ReloadGodParticleCommand) -> None:
        god_particle = Song.master_track().devices.get_one_from_enum(DeviceEnum.GOD_PARTICLE)

        from protocol0.shared.logging.Logger import Logger

        Logger.dev(god_particle)

        Song.master_track().select()

        seq = Sequence()
        seq.add(
            partial(self._container.get(DeviceService).load_device, DeviceEnum.GOD_PARTICLE.name)
        )

        if god_particle:
            seq.add(partial(Song.master_track().devices.delete, god_particle))

        seq.done()
