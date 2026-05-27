from typing import Optional, cast

import Live

from protocol0.domain.lom.clip.ClipEnvelopeShowedEvent import ClipEnvelopeShowedEvent
from protocol0.domain.lom.clip.ClipLoop import ClipLoop
from protocol0.domain.lom.clip.automation.ClipAutomationEnvelope import ClipAutomationEnvelope
from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.errors.error_handler import handle_errors
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus


class ClipAutomation(object):
    def __init__(self, live_clip: Live.Clip.Clip, loop: ClipLoop) -> None:
        self._live_clip = live_clip
        self._loop = loop

    def show_parameter_envelope(self, parameter: DeviceParameter) -> None:
        ApplicationView.show_clip()
        self.show_envelope()
        # noinspection PyArgumentList
        self._live_clip.view.select_envelope_parameter(parameter._device_parameter)
        DomainEventBus.emit(ClipEnvelopeShowedEvent())

    def get_envelope(self, parameter: DeviceParameter) -> Optional[ClipAutomationEnvelope]:
        if self._live_clip and parameter._device_parameter:
            env = self._live_clip.automation_envelope(parameter._device_parameter)
            if env:
                return ClipAutomationEnvelope(env, self._loop.length)

        return None

    def create_envelope(self, parameter: DeviceParameter) -> ClipAutomationEnvelope:
        try:
            self._live_clip.create_automation_envelope(parameter._device_parameter)
        except RuntimeError:
            # envelope already exists
            pass
        self.show_envelope()
        return cast(ClipAutomationEnvelope, self.get_envelope(parameter))

    def clear_envelope(self, parameter: DeviceParameter) -> None:
        if self._live_clip:
            return self._live_clip.clear_envelope(parameter._device_parameter)

    def clear_all_envelopes(self) -> None:
        if self._live_clip:
            return self._live_clip.clear_all_envelopes()

    @handle_errors()
    def show_envelope(self) -> None:
        self.hide_envelope()  # necessary
        self._live_clip.view.show_loop()  # this before seem to work better
        self._live_clip.view.show_envelope()

    @handle_errors()
    def hide_envelope(self) -> None:
        self._live_clip.view.hide_envelope()
