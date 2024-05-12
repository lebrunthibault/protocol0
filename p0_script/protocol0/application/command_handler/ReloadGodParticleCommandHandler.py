from functools import partial
from typing import cast

from protocol0.application.command.ReloadGodParticleCommand import (
    ReloadGodParticleCommand,
)
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceChain import DeviceChain
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device.DeviceService import DeviceService
from protocol0.domain.lom.device_parameter.DeviceParamEnum import DeviceParamEnum
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


class ReloadGodParticleCommandHandler(CommandHandlerInterface):
    def handle(self, command: ReloadGodParticleCommand) -> None:
        god_particle = Song.master_track().god_particle

        assert god_particle, "Cannot find God Particle"

        god_particle_enabled = god_particle.is_enabled
        god_particle_character_param = god_particle.get_parameter_by_name(
            DeviceParamEnum.GOD_PARTICLE_CHARACTER
        ).value
        god_particle_chain = Song.master_track().devices.all_devices_with_chain[god_particle]

        Song.master_track().select()

        seq = Sequence()

        def move_device() -> Sequence:
            return self._container.get(DeviceService).move_device(
                cast(Device, Song.selected_device()),
                cast(DeviceChain, god_particle_chain),
                len(god_particle_chain.devices),
            )

        if god_particle_chain:
            seq.add(partial(Song.master_track().devices.delete, god_particle))
            seq.add(
                partial(
                    self._container.get(DeviceService).load_device, DeviceEnum.GOD_PARTICLE.name
                )
            )
            seq.add(move_device)
        else:
            seq.add(
                partial(
                    self._container.get(DeviceService).load_device, DeviceEnum.GOD_PARTICLE.name
                )
            )
            seq.add(partial(Song.master_track().devices.delete, god_particle))

        def update_from_previous() -> None:
            Song.selected_device().is_enabled = god_particle_enabled
            Song.selected_device().get_parameter_by_name(
                DeviceParamEnum.GOD_PARTICLE_CHARACTER
            ).value = god_particle_character_param

        seq.add(update_from_previous)

        seq.done()
