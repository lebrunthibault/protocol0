from dataclasses import dataclass
from functools import partial
from typing import Optional, List, Tuple

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device_parameter.DeviceParamEnum import DeviceParamEnum
from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.domain.lom.track.TrackFactory import TrackFactory
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.ValueScroller import ValueScroller
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


def is_param_automated(track: SimpleTrack, param: DeviceParameter) -> bool:
    return any(clip.automation.get_envelope(param) is not None for clip in track.clips)


@dataclass(frozen=True)
class ParameterEnvelope:
    clip: Clip
    parameter: DeviceParameter
    time: float

    @property
    def value(self) -> float:
        env = self.clip.automation.get_envelope(self.parameter)

        if env:
            return env.value_at_time(self.time)
        else:
            return self.parameter.value


class TrackAutomationService(object):
    def __init__(self, track_factory: TrackFactory) -> None:
        self._track_factory = track_factory
        self._last_selected_parameter: Optional[DeviceParameter] = None
        self._last_scrolled_parameter: Optional[DeviceParameter] = None

    def show_automation(self, go_next: bool) -> Sequence:
        selected_parameter = Song.selected_parameter() or self._last_scrolled_parameter

        seq = Sequence()

        if selected_parameter is not None and not ApplicationView.is_clip_view_visible():
            seq.add(partial(self._show_selected_parameter_automation, selected_parameter))
        else:
            seq.add(partial(self._scroll_automated_parameters, go_next))

        return seq.done()

    def _show_selected_parameter_automation(self, selected_parameter: DeviceParameter) -> None:
        if selected_parameter not in Song.selected_track().devices.parameters:
            self._last_scrolled_parameter = None
            raise Protocol0Warning("parameter does not belong to selected track")

        self._last_scrolled_parameter = selected_parameter
        clip = Song.selected_clip()

        clip.automation.show_parameter_envelope(selected_parameter)

        if selected_parameter not in clip.automation.get_automated_parameters(
            Song.selected_track().devices.parameters
        ):
            bar_length = Song.selected_scene().bar_length
            if bar_length != clip.bar_length:
                Scheduler.defer(partial(Backend.client().set_envelope_loop_length, bar_length))

    def _scroll_automated_parameters(self, go_next: bool) -> Sequence:
        """Scroll the automated parameters of the clip"""
        current_track = Song.current_track()
        index = Song.selected_scene().index

        automated_parameters = current_track.get_automated_parameters(index)

        if len(automated_parameters.items()) == 0:
            raise Protocol0Warning("No automated parameters")

        selected_parameter = ValueScroller.scroll_values(
            automated_parameters.keys(), self._last_selected_parameter, go_next
        )
        track = automated_parameters[selected_parameter]

        seq = Sequence()
        seq.add(track.select)
        seq.add(
            partial(
                track.clip_slots[index].clip.automation.show_parameter_envelope, selected_parameter
            )
        )
        self._last_selected_parameter = selected_parameter
        return seq.done()

    def check_automated_parameters(self) -> None:
        for clip in Song.selected_track().clips:
            clip.color = Song.selected_track().color

        automated_parameters = self._get_automated_parameters()

        if not len(automated_parameters):
            log_line = "No automation"
        else:
            parameters_name = ["%s: %s" % (d.name, p.name) for d, p in set(automated_parameters)]
            log_line = "Automated parameters:\n" + "- {}".format("\n  - ".join(parameters_name))

        log_line += "\n\n"

        inner_boundaries_ok = self._check_automation_inner_boundaries()
        cross_boundaries_ok = self._check_automation_cross_clip_boundaries()

        if inner_boundaries_ok and cross_boundaries_ok:
            log_line += "Automation boundaries ok"
        else:
            log_line += "Automation boundaries problem"

        removed_device_names = self._remove_non_automated_devices(
            [device for device, param in automated_parameters]
        )
        if len(removed_device_names):
            log_line += "\n\nRemoved devices: " + ", ".join(removed_device_names)

        Logger.info(log_line)
        Backend.client().show_info(log_line)

    def _get_automated_parameters(self) -> List[Tuple[Device, DeviceParameter]]:
        track = Song.selected_track()

        device_parameters: List[Tuple[Device, DeviceParameter]] = []

        for clip in track.clips:
            if clip.automation.has_automation(track.devices.parameters):
                for device in track.devices.all:
                    parameters = list(clip.automation.get_automated_parameters(device.parameters))
                    if len(parameters):
                        device_parameters.append((device, parameters[0]))

        return device_parameters

    def _check_automation_inner_boundaries(self) -> bool:
        track = Song.selected_track()
        boundaries_ok = True

        for clip in track.clips:
            if clip.bar_length <= 8:
                continue

            automated_parameters = clip.automation.get_automated_parameters(
                track.devices.parameters
            )
            for param in automated_parameters:
                # check every 8 measures
                for bar_length in range(8, int(clip.bar_length), 8):
                    if not self._check_envelope_boundary(
                        ParameterEnvelope(
                            clip, param, bar_length * Song.signature_numerator() - 0.1
                        ),
                        ParameterEnvelope(
                            clip, param, bar_length * Song.signature_numerator() + 0.1
                        ),
                    ):
                        boundaries_ok = False

        return boundaries_ok

    def _check_automation_cross_clip_boundaries(self) -> bool:
        track = Song.selected_track()
        adjacent_clips: List[Tuple[Clip, Clip]] = []

        for index, clip in enumerate(track.clips):
            if clip == track.clips[-1]:
                break

            next_clip = track.clips[index + 1]
            if next_clip.index == clip.index + 1:
                adjacent_clips.append((clip, next_clip))

        boundaries_ok = True

        for clip, next_clip in adjacent_clips:
            clip_params = clip.automation.get_automated_parameters(track.devices.parameters)
            next_clip_params = next_clip.automation.get_automated_parameters(
                track.devices.parameters
            )
            common_parameters: List[DeviceParameter] = list(
                set(clip_params).union(next_clip_params)
            )
            for param in common_parameters:
                if param in track.devices.mixer_device.sends or param.name in (
                    DeviceParamEnum.INPUT.parameter_name,
                    DeviceParamEnum.LFO_TOOL_LFO_DEPTH.parameter_name,
                ):
                    continue

                if not self._check_envelope_boundary(
                    ParameterEnvelope(clip, param, clip.length - 0.1),
                    ParameterEnvelope(next_clip, param, 0.1),
                ):
                    boundaries_ok = False

        return boundaries_ok

    def _check_envelope_boundary(
        self, param_env: ParameterEnvelope, next_param_env: ParameterEnvelope
    ) -> bool:
        boundary_left = param_env.value
        boundary_right = next_param_env.value

        if boundary_left == 0:
            boundary_ratio = 1.0 if boundary_right == 0 else 0.0
        else:
            boundary_ratio = round(boundary_right / boundary_left, 1)

        if boundary_ratio != 1:
            boundary_type = "cross" if param_env.clip != next_param_env.clip else "inner"
            Logger.info(
                f"{boundary_type} on {next_param_env.clip} : {next_param_env.parameter}. {round(boundary_left, 2)} / {round(boundary_right, 2)} = {boundary_ratio} %",
                debug=False,
            )

            return False

        return True

    def _remove_non_automated_devices(self, automated_devices: List[Device]) -> List[str]:
        track = Song.selected_track()

        deleted_device_names = []

        def is_default_utility(dev: Device) -> bool:
            width_param = dev.get_parameter_by_name(
                DeviceParamEnum.UTILITY_MID_SIDE
            ) or dev.get_parameter_by_name(DeviceParamEnum.UTILITY_WIDTH)
            return (
                dev.enum == DeviceEnum.UTILITY
                and width_param.value == 1
                and dev.get_parameter_by_name(DeviceParamEnum.GAIN).value == 0
            )

        for device in track.devices:
            if (
                not device.is_enabled or is_default_utility(device)
            ) and device not in automated_devices:
                deleted_device_names.append(device.name)
                track.devices.delete(device)

        return deleted_device_names
