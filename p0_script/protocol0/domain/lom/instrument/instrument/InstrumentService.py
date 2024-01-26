from functools import partial
from typing import Optional, Union

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceService import DeviceService
from protocol0.domain.lom.instrument.InstrumentLoadedEvent import InstrumentLoadedEvent
from protocol0.domain.lom.instrument.XParam import XParam, DeviceParam, ParamDevice
from protocol0.domain.lom.song.components.DeviceComponent import DeviceComponent
from protocol0.domain.shared.errors.error_handler import handle_errors
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.utils.concurrency import lock
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class InstrumentService(object):
    _DEBUG = False

    def __init__(self, device_service: DeviceService, device_component: DeviceComponent) -> None:
        super(InstrumentService, self).__init__()
        self._device_service = device_service
        self._device_component = device_component
        DomainEventBus.subscribe(InstrumentLoadedEvent, self._on_instrument_loaded_event)

    def _on_instrument_loaded_event(self, event: InstrumentLoadedEvent) -> None:
        instrument = Song.selected_track().instrument
        if instrument and instrument.device.enum == event.device_enum.instrument_enum:
            instrument.on_loaded(event.device_enum)

    def _get_device(
        self,
        x_param: XParam,
        pd: Optional[ParamDevice],
        auto_enable: bool = False,
        automatable: bool = False,
    ) -> Union[None, Device, Sequence]:
        if not pd:
            device_to_load = x_param.get_device_to_load(automatable)
            if device_to_load:
                x_param.track.select()
                return self._device_service.load_device(device_to_load.name)
            else:
                return None

        if pd.device:
            if auto_enable:
                pd.device.is_enabled = True
                pd.device.is_collapsed = False
            if not Song.session_record():
                self._device_component.select_device(x_param.track, pd.device)

            return pd.device

        return None

    def _setup_device_and_clip(
        self,
        x_param: XParam,
        pd: Optional[ParamDevice],
        select_clip: bool = True,
        auto_enable: bool = True,
    ) -> Union[None, Clip, Sequence]:
        device = self._get_device(x_param, pd, auto_enable)
        if isinstance(device, Sequence):
            return device

        if not pd:
            return None

        clip = x_param.track.clip_slots[Song.selected_scene().index].clip
        if not clip:
            Logger.warning("No selected clip")
            return None

        if select_clip:
            clip.select()

        return clip

    @lock
    def toggle_param(self, x_param: XParam) -> Optional[Sequence]:
        pd_mutable = x_param.get_device_param(mutable=True)
        if pd_mutable:
            device = self._get_device(x_param, pd_mutable)
            device.toggle()
            return None

        pd = x_param.get_device_param(automatable=True)

        if not pd:
            device = self._get_device(x_param, pd, automatable=True)
            if not isinstance(device, Device):
                return device

            if not device.is_instrument:
                device.toggle()

            return None

        clip = self._setup_device_and_clip(x_param, pd)
        if not isinstance(clip, Clip):
            return clip

        clip.automation.show_parameter_envelope(pd.param)
        return None

    @lock
    def toggle_param_automation(self, x_param: XParam) -> Optional[Sequence]:
        pd = x_param.get_device_param(automatable=True)

        if not pd:
            return None

        clip = self._setup_device_and_clip(x_param, pd)
        if not isinstance(clip, Clip):
            return clip

        env = clip.automation.get_envelope(pd.param)
        if env:
            clip.automation.clear_envelope(pd.param)
        else:
            env = clip.automation.create_envelope(pd.param)

            # hack to have only one start and one end points
            param_value = pd.param.value
            pd.param.value = pd.param.min

            seq = Sequence().defer()
            seq.add(partial(env.create_start_and_end_points, param_value))
            seq.defer()
            seq.add(partial(setattr, pd.param, "value", param_value))
            seq.done()

        clip.automation.show_parameter_envelope(pd.param)

        return None

    @lock
    @handle_errors(reset=False)
    def scroll_param(self, x_param: XParam, go_next: bool) -> Optional[Sequence]:
        param_conf, pd = x_param.get_scrollable(go_next)
        auto_enable = not isinstance(param_conf, DeviceParam) or param_conf.auto_disable is False

        res = self._setup_device_and_clip(x_param, pd, select_clip=False, auto_enable=auto_enable)
        if isinstance(res, Sequence):
            return res

        if not pd:
            return None

        if callable(pd.param):
            try:
                pd.param(go_next)
            except AttributeError:
                return None
        else:
            if x_param.value_items:
                pd.param.scroll_slowed(go_next, value_items=x_param.value_items)
            else:
                pd.param.scroll(go_next)

            device_param_conf = find_if(lambda p: isinstance(p, DeviceParam), x_param.param_configs)

            # disable the device the the param reaches its minimum
            if device_param_conf and device_param_conf.auto_disable:
                if (pd.param.value == pd.param.min and pd.device.is_enabled) or (
                    pd.param.value != pd.param.min and not pd.device.is_enabled
                ):
                    pd.device.toggle()

        return None
