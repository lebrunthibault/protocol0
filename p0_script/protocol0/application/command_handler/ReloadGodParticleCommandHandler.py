from functools import partial

from protocol0.application.command.ReloadGodParticleCommand import (
    ReloadGodParticleCommand,
)
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device.DeviceService import DeviceService
from protocol0.domain.lom.device_parameter.DeviceParamEnum import DeviceParamEnum
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


class ReloadGodParticleCommandHandler(CommandHandlerInterface):
    def handle(self, command: ReloadGodParticleCommand) -> None:
        god_particle = Song.master_track().devices.get_one_from_enum(DeviceEnum.GOD_PARTICLE)

        Song.master_track().select()

        seq = Sequence()
        seq.add(
            partial(self._container.get(DeviceService).load_device, DeviceEnum.GOD_PARTICLE.name)
        )

        def update_from_previous() -> None:
            Song.selected_device().is_enabled = god_particle.is_enabled
            character_param = Song.selected_device().get_parameter_by_name(
                DeviceParamEnum.GOD_PARTICLE_CHARACTER
            )

            if not character_param:
                return

            character_param.value = god_particle.get_parameter_by_name(
                DeviceParamEnum.GOD_PARTICLE_CHARACTER
            ).value

        if god_particle:
            seq.add(update_from_previous)
            seq.add(partial(Song.master_track().devices.delete, god_particle))

        seq.done()
