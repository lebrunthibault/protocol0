from dataclasses import dataclass
from functools import partial
from typing import Optional, cast, List, Tuple

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.clip.ClipColorEnum import ClipColorEnum
from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.domain.lom.track.TrackFactory import TrackFactory
from protocol0.domain.lom.track.group_track.ext_track.ExternalSynthTrack import (
    ExternalSynthTrack,
)
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.ValueScroller import ValueScroller
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


@dataclass(frozen=True)
class ParameterEnvelope:
    clip: Clip
    parameter: DeviceParameter
    time: float

    @property
    def value(self) -> float:
        env = self.clip.automation.get_envelope(self.parameter)

        return env.value_at_time(self.time)


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

    def select_or_sync_automation(self) -> None:
        """
        Either we have a midi clip focused and we sync the automation (rev2) layers
        Or we create a new automation lane for the selected parameter
        """
        current_track = Song.current_track()
        selected_track = Song.selected_track()

        if (
            isinstance(current_track, ExternalSynthTrack)
            and selected_track == current_track.midi_track
        ):
            Song.selected_clip(MidiClip).synchronize_automation_layers(
                Song.selected_track().devices.parameters
            )
        else:
            self._create_automation_from_selected_parameter()

    def _create_automation_from_selected_parameter(self) -> Sequence:
        selected_track = Song.selected_track()
        selected_clip = selected_track.clip_slots[Song.selected_scene().index].clip
        selected_parameter = Song.selected_parameter()

        if selected_parameter is None:
            raise Protocol0Warning("No selected parameter")

        seq = Sequence()
        if selected_clip is None:
            raise Protocol0Warning("No selected clip")

        seq.add(
            lambda: Song.selected_clip().automation.select_or_create_envelope(
                cast(DeviceParameter, selected_parameter)
            )
        )

        return seq.done()

    def check_automated_parameters(self) -> None:
        for clip in Song.selected_track().clips:
            clip.color = Song.selected_track().color

        if (
            self._check_automation_inner_boundaries()
            and self._check_automation_cross_clip_boundaries()
        ):
            log_line = "Automation boundaries ok"
        else:
            log_line = "Automation boundaries problem"

        log_line += "\n\nAutomated parameters:\n" + self._get_automated_parameters_log()

        Logger.info(log_line)
        Backend.client().show_info(log_line)

    def _get_automated_parameters_log(self) -> str:
        track = Song.selected_track()

        device_parameters = []

        # colors_on = any(c.color != track.color for c in track.clips)
        # if colors_on:
        #     for clip in track.clips:
        #         clip.color = track.color
        #     return

        for clip in track.clips:
            if clip.automation.has_automation(track.devices.parameters):
                for device in track.devices.all:
                    parameters = list(clip.automation.get_automated_parameters(device.parameters))
                    if len(parameters):
                        device_parameters.append((device, parameters[0]))

                # clip.color = ClipColorEnum.BLINK.value

        if not len(device_parameters):
            return "No automation"
        else:
            parameters_name = ["%s: %s" % (d.name, p.name) for d, p in set(device_parameters)]

            return "- {}".format("\n  - ".join(parameters_name))

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
                if not self._check_envelope_boundary(
                    ParameterEnvelope(clip, param, 8 * Song.signature_numerator() - 0.1),
                    ParameterEnvelope(clip, param, 8 * Song.signature_numerator() + 0.1),
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
            common_parameters = list(set(clip_params).intersection(next_clip_params))
            for param in common_parameters:
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
            boundary_type = "cross" if param_env != next_param_env else "inner"
            Logger.info(
                f"""Discontinuous {boundary_type} boundary for {next_param_env.clip} : {next_param_env.parameter}.
                    Env values: {round(boundary_left, 2)}, {round(boundary_right, 2)}. Ratio: {boundary_ratio}
                """,
                debug=False,
            )
            next_param_env.clip.color = ClipColorEnum.BLINK.value

            return False

        return True
