from typing import Optional, Union

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceService import DeviceService
from protocol0.domain.lom.instrument.InstrumentLoadedEvent import InstrumentLoadedEvent
from protocol0.domain.lom.instrument.XParam import XParam, DeviceParam, ParamDevice
from protocol0.domain.lom.song.components.DeviceComponent import DeviceComponent
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.utils.concurrency import lock
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


class InstrumentService(object):
    _DEBUG = True

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
        self, param: XParam, pd: Optional[ParamDevice], auto_enable: bool = False
    ) -> Union[None, Device, Sequence]:
        if not pd:
            device_to_load = param.get_device_to_load()
            if device_to_load:
                Song.armed_or_selected_track().select()
                return self._device_service.load_device(device_to_load.name)
            else:
                return None

        if pd.device:
            if auto_enable:
                pd.device.is_enabled = True
                pd.device.is_collapsed = False
            self._device_component.select_device(Song.armed_or_selected_track(), pd.device)

            return pd.device

        return None

    def _setup_device_and_clip(
        self,
        param: XParam,
        pd: Optional[ParamDevice],
        select_clip: bool = True,
        auto_enable: bool = True,
    ) -> Union[None, Clip, Sequence]:
        device = self._get_device(param, pd, auto_enable)
        if isinstance(device, Sequence):
            return device

        if not pd:
            return None

        clip = Song.armed_or_selected_track().clip_slots[Song.selected_scene().index].clip
        if not clip:
            return None

        if select_clip:
            clip.select()

        return clip

    @lock
    def toggle_param(self, param: XParam) -> Optional[Sequence]:
        pd = param.get_device_param(automatable=True)

        if not pd:
            pd = param.get_device_param()

            device = self._get_device(param, pd)
            if not isinstance(device, Device):
                return device

            if not device.is_instrument:
                device.toggle()

            return None

        clip = self._setup_device_and_clip(param, pd)
        if not isinstance(clip, Clip):
            return clip

        clip.automation.show_parameter_envelope(pd.param)
        return None

    @lock
    def toggle_param_automation(self, param: XParam) -> Optional[Sequence]:
        pd = param.get_device_param(automatable=True)

        if not pd:
            return None

        clip = self._setup_device_and_clip(param, pd)
        if not isinstance(clip, Clip):
            return clip

        env = clip.automation.get_envelope(pd.param)
        if env:
            clip.automation.clear_envelope(pd.param)
        else:
            env = clip.automation.create_envelope(pd.param)
            env.create_start_and_end_points()

        return None

    @lock
    def scroll_param(self, param: XParam, go_next: bool) -> Optional[Sequence]:
        param_conf, pd = param.get_scrollable()
        auto_enable = not isinstance(param_conf, DeviceParam) or param_conf.auto_disable is False

        res = self._setup_device_and_clip(param, pd, select_clip=False, auto_enable=auto_enable)
        if isinstance(res, Sequence):
            return res

        if not pd:
            return None

        if callable(pd.param):
            pd.param(go_next)
        else:
            if param.value_items:
                pd.param.scroll_slowed(go_next, value_items=param.value_items)
            else:
                pd.param.scroll(go_next)

            device_param_conf = find_if(lambda p: isinstance(p, DeviceParam), param.param_configs)

            # disable the device the the param reaches its minimum
            if device_param_conf and device_param_conf.auto_disable:
                if (pd.param.value == pd.param.min and pd.device.is_enabled) or (
                    pd.param.value != pd.param.min and not pd.device.is_enabled
                ):
                    pd.device.toggle()

        return None
