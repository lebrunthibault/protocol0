from functools import partial

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device_parameter.DeviceParamEnum import DeviceParamEnum
from protocol0.domain.lom.instrument.XParam import (
    XParam,
    InstrumentParam,
    DeviceParam,
    TrackParam,
)
from protocol0.domain.lom.instrument.instrument.InstrumentParamEnum import (
    InstrumentParamEnum,
)
from protocol0.domain.lom.instrument.instrument.InstrumentService import InstrumentService
from protocol0.domain.lom.set.MixingService import MixingService
from protocol0.shared.Song import Song


class ActionGroupRack(ActionGroupInterface):
    CHANNEL = 2

    def configure(self) -> None:
        instrument_service = self._container.get(InstrumentService)

        arp_styles = [
            0,  # "Up",
            1,  # "Down",
            # 2, "UpDown",
            # 3, "DownUp",
            # 4, "Up & Down",
            # 5, "Down & Up",
            6,  # "Converge",
            # 7, "Diverge",
            # 8, "Con & Diverge",
            9,  # "Pinky Up",
            # 10, "Pinky UpDown",
            11,  # "Thumb Up",
            # 12, "Thumb UpDown",
            # 13, "Play Order",
            14,  # "Chord Trigger",
            # 15, "Random",
            # 16, "Random Other",
            # 17, "Random Once",
        ]

        params = [
            XParam(
                [
                    InstrumentParam(InstrumentParamEnum.FILTER),
                    DeviceParam(DeviceEnum.EQ_EIGHT, DeviceParamEnum.FREQUENCY_8_A),
                ]
            ),
            XParam([InstrumentParam(InstrumentParamEnum.ATTACK)]),
            XParam([InstrumentParam(InstrumentParamEnum.DECAY)]),
            XParam([InstrumentParam(InstrumentParamEnum.RELEASE)]),
            XParam([DeviceParam(DeviceEnum.EQ_EIGHT, DeviceParamEnum.FREQUENCY_1_A)]),
            XParam([DeviceParam(DeviceEnum.OCTAVA, DeviceParamEnum.OCTAVA_VEL, auto_disable=True)]),
            XParam(
                [
                    DeviceParam(DeviceEnum.INSERT_REVERB, DeviceParamEnum.INPUT, scrollable=False),
                    DeviceParam(DeviceEnum.INSERT_REVERB, DeviceParamEnum.WET, automatable=False),
                    DeviceParam(DeviceEnum.VALHALLA_VINTAGE_VERB, DeviceParamEnum.MIX),
                    InstrumentParam(InstrumentParamEnum.REVERB),
                    TrackParam(lambda t: t.devices.mixer_device.sends[-1]),
                ]
            ),
            XParam(
                [
                    DeviceParam(DeviceEnum.INSERT_DELAY, DeviceParamEnum.INPUT, scrollable=False),
                    DeviceParam(DeviceEnum.INSERT_DELAY, DeviceParamEnum.WET, automatable=False),
                    InstrumentParam(InstrumentParamEnum.DELAY),
                ]
            ),
            XParam(
                [DeviceParam(DeviceEnum.ARPEGGIATOR, DeviceParamEnum.ARP_STYLE, automatable=False)],
                value_items=arp_styles,
            ),
            XParam(
                [DeviceParam(DeviceEnum.ARPEGGIATOR, DeviceParamEnum.ARP_RATE)],
                value_items=list(range(14)),
            ),
            XParam(
                [
                    DeviceParam(DeviceEnum.NOTE_LENGTH, DeviceParamEnum.LENGTH),
                    DeviceParam(DeviceEnum.ARPEGGIATOR, DeviceParamEnum.ARP_GATE),
                ]
            ),
            XParam([DeviceParam(DeviceEnum.LFO_TOOL, DeviceParamEnum.LFO_TOOL_LFO_DEPTH)]),
            XParam(
                [
                    InstrumentParam(InstrumentParamEnum.VOLUME, automatable=False),
                    DeviceParam(DeviceEnum.UTILITY, DeviceParamEnum.GAIN, scrollable=False),
                    TrackParam(lambda t: t.devices.mixer_device.volume),
                ],
            ),
        ]

        for index, param in enumerate(params):
            self.add_encoder(
                identifier=index + 1,
                name=f"control {param.name}",
                on_press=partial(instrument_service.toggle_param, param),
                on_long_press=partial(instrument_service.toggle_param_automation, param),
                on_scroll=partial(instrument_service.scroll_param, param),
            )

        # -----

        # VELO encoder
        self.add_encoder(
            identifier=15,
            name="smooth selected clip velocities",
            on_scroll=lambda: Song.selected_clip(MidiClip).scale_velocities,
        )
        # VOLume encoder
        self.add_encoder(
            identifier=16,
            name="volume",
            on_scroll=self._container.get(MixingService).scroll_all_tracks_volume,
        )
