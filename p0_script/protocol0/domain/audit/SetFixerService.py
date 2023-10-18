from typing import Iterator, Tuple

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device_parameter.DeviceParamEnum import DeviceParamEnum
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.validation.ValidatorService import ValidatorService
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger


class SetFixerService(object):
    def __init__(self, validator_service: ValidatorService) -> None:
        self._validator_service = validator_service

    def fix_set(self) -> None:
        """Fix the current set to the current standard regarding naming / coloring etc .."""
        Logger.clear()

        invalid_objects = []

        objects_to_validate = Song.scenes() + list(Song.abstract_tracks())  # noqa
        for obj in objects_to_validate:
            is_valid = self._validator_service.validate_object(obj)
            if not is_valid:
                invalid_objects.append(obj)

        if len(invalid_objects) == 0:
            Backend.client().show_success("Set is valid")
            self._refresh_objects_appearance()
        else:
            Backend.client().show_warning("Invalid set: fixing")
            for invalid_object in invalid_objects:
                self._validator_service.fix_object(invalid_object, log=False)
            Logger.info("set fixed")

    def find_devices_to_remove(self) -> None:
        devices_to_remove = list(self._get_deletable_devices())

        if len(devices_to_remove):
            Logger.warning("Devices to remove: %s" % devices_to_remove)

    def _get_deletable_devices(self) -> Iterator[Tuple[SimpleTrack, Device]]:
        # devices with default values (unchanged)
        for device_enum in DeviceEnum:  # type: DeviceEnum
            try:
                default_parameter_values = device_enum.main_parameters_default
            except Protocol0Error:
                continue

            for track in Song.all_simple_tracks():
                device = track.devices.get_one_from_enum(device_enum, all_devices=True)
                if not device:
                    continue
                device_on = device.get_parameter_by_name(DeviceParamEnum.DEVICE_ON)
                if device_on.value is False and not device_on.is_automated:
                    yield track, device
                if all(
                    [
                        parameter_value.matches(device)
                        for parameter_value in default_parameter_values
                    ]
                ):
                    yield track, device

    def _refresh_objects_appearance(self) -> None:
        clip_slots = [cs for track in Song.simple_tracks() for cs in track.clip_slots]
        clips = [clip for track in Song.simple_tracks() for clip in track.clips]
        # noinspection PyTypeChecker
        objects_to_refresh_appearance = clip_slots + clips + Song.scenes()

        for obj in objects_to_refresh_appearance:
            obj.appearance.refresh()

        for track in Song.external_synth_tracks():
            track.midi_track.name = "m"
            track.audio_track.name = "a"
