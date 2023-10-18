from typing import Optional, List, Union

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device.DeviceService import DeviceService
from protocol0.domain.lom.device_parameter.DeviceParamEnum import DeviceParamEnum
from protocol0.domain.lom.instrument.InstrumentLoadedEvent import InstrumentLoadedEvent
from protocol0.domain.lom.instrument.XParam import XParam, DeviceParam
from protocol0.domain.lom.instrument.instrument.InstrumentParamEnum import (
    InstrumentParamEnum,
)
from protocol0.domain.lom.song.components.DeviceComponent import DeviceComponent
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.utils.concurrency import lock
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger
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
        self, param: XParam, auto_enable: bool = False
    ) -> Union[None, Device, Sequence]:
        pd = param.get_device_param()

        if not pd:
            device_to_load = param.get_device_to_load()
            if device_to_load:
                Song.armed_or_selected_track().select()
                return self._device_service.load_device(device_to_load.name)
            else:
                return None

        device = pd.device
        if device:
            if auto_enable:
                device.is_enabled = True
            self._device_component.select_device(Song.armed_or_selected_track(), device)

            return device

        return None

    def _setup_device_and_clip(
        self, param: XParam, select_clip: bool = True, auto_enable: bool = True
    ) -> Union[None, Clip, Sequence]:
        device = self._get_device(param, auto_enable)
        if isinstance(device, Sequence):
            return device

        pd = param.get_device_param()
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
            device = self._get_device(param)
            if not isinstance(device, Device):
                return device

            if device.is_instrument:
                device.toggle()

            return None

        clip = self._setup_device_and_clip(param)
        if not isinstance(clip, Clip):
            return clip

        clip.automation.show_parameter_envelope(pd.param)
        return None

    @lock
    def toggle_param_automation(self, param: XParam) -> Optional[Sequence]:
        pd = param.get_device_param(automatable=True)

        if not pd:
            return None

        clip = self._setup_device_and_clip(param)
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

        res = self._setup_device_and_clip(param, select_clip=False, auto_enable=auto_enable)
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

    def scroll_instrument_param(self, name: InstrumentParamEnum, go_next: bool) -> bool:
        instrument = Song.armed_or_selected_track().instrument

        if instrument and instrument.device and name in instrument.PARAMETER_NAMES:
            self._device_component.select_device(Song.armed_or_selected_track(), instrument.device)
            parameter = instrument.device.get_parameter_by_name(instrument.PARAMETER_NAMES[name])
            parameter.scroll(go_next)
            return True
        elif (
            instrument
            and instrument.device
            and callable(getattr(instrument, f"scroll_{name}", None))
        ):
            self._device_component.select_device(Song.armed_or_selected_track(), instrument.device)
            getattr(instrument, f"scroll_{name}")(go_next)
            return True
        else:
            Logger.warning(f"{instrument} cannot scroll {name}")
            return False

    @lock
    def scroll_device_param(
        self,
        device_enum: DeviceEnum,
        param_name: str,
        go_next: bool,
        auto_enable: bool = False,
        value_items: List[int] = None,
    ) -> Optional[Sequence]:
        device = Song.armed_or_selected_track().devices.get_one_from_enum(device_enum)
        if not device:
            Song.armed_or_selected_track().select()
            return self._device_service.load_device(device_enum.name)

        self._device_component.select_device(Song.armed_or_selected_track(), device)
        device.is_enabled = True
        param = device.get_parameter_by_name(param_name)

        if param is None:
            Logger.warning(f"Couldn't find {param_name} on {device}")
            return None

        if value_items:
            param.scroll_slowed(go_next, value_items=value_items)
        else:
            param.scroll(go_next)

        # disable the device the the param reaches its minimum
        if auto_enable:
            if (param.value == param.min and device.is_enabled) or (
                param.value != param.min and not device.is_enabled
            ):
                device.toggle()

        return None

    def scroll_volume(self, go_next: bool) -> None:
        scrolled = self.scroll_instrument_param(InstrumentParamEnum.VOLUME, go_next)

        if not scrolled:
            Song.armed_or_selected_track().scroll_volume(go_next)

    def scroll_reverb(self, go_next: bool) -> None:
        """
        Controls in this order :
        - the insert reverb device
        - the instrument reverb parameter
        - the last send
        """
        reverb = Song.armed_or_selected_track().devices.get_one_from_enum(DeviceEnum.INSERT_REVERB)
        if reverb:
            self._device_component.select_device(Song.armed_or_selected_track(), reverb)
            reverb.get_parameter_by_name(DeviceParamEnum.WET).scroll(go_next)
        elif self.scroll_instrument_param(InstrumentParamEnum.REVERB, go_next):
            return
        else:
            sends = Song.armed_or_selected_track().devices.mixer_device.sends
            if len(sends):
                sends[-1].scroll(go_next)

    @lock
    def scroll_delay(self, go_next: bool) -> Optional[Sequence]:
        """
        Controls in this order :
        - the insert delay device
        - the instrument delay parameter
        - if none above, inserts an insert delay
        """
        delay = Song.armed_or_selected_track().devices.get_one_from_enum(DeviceEnum.INSERT_DELAY)
        if delay:
            self._device_component.select_device(Song.armed_or_selected_track(), delay)
            delay.get_parameter_by_name(DeviceParamEnum.WET).scroll(go_next)
            return None
        elif self.scroll_instrument_param(InstrumentParamEnum.DELAY, go_next):
            return None
        else:
            return self.scroll_device_param(
                DeviceEnum.INSERT_DELAY, DeviceParamEnum.WET.parameter_name, go_next
            )
