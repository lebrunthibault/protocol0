from functools import partial
from typing import Callable, Any

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
from protocol0.domain.shared.utils.utils import db_to_volume
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
                "Filter",
                [
                    InstrumentParam(InstrumentParamEnum.FILTER),
                    DeviceParam(DeviceEnum.EQ_EIGHT, DeviceParamEnum.FREQUENCY_8_A),
                ],
            ),
            XParam("Attack", [InstrumentParam(InstrumentParamEnum.ATTACK)]),
            XParam("Decay", [InstrumentParam(InstrumentParamEnum.DECAY)]),
            XParam("Release", [InstrumentParam(InstrumentParamEnum.RELEASE)]),
            XParam("HPF", [DeviceParam(DeviceEnum.EQ_EIGHT, DeviceParamEnum.FREQUENCY_1_A)]),
            XParam(
                "Octava",
                [DeviceParam(DeviceEnum.OCTAVA, DeviceParamEnum.OCTAVA_VEL, auto_disable=True)],
            ),
            XParam(
                "Reverb",
                [
                    DeviceParam(DeviceEnum.INSERT_REVERB, DeviceParamEnum.INPUT, scrollable=False),
                    DeviceParam(DeviceEnum.INSERT_REVERB, DeviceParamEnum.WET, automatable=False),
                    DeviceParam(DeviceEnum.VALHALLA_VINTAGE_VERB, DeviceParamEnum.MIX),
                    InstrumentParam(InstrumentParamEnum.REVERB),
                    TrackParam(lambda t: t.devices.mixer_device.sends[-1]),
                ],
            ),
            XParam(
                "Delay",
                [
                    DeviceParam(DeviceEnum.INSERT_DELAY, DeviceParamEnum.INPUT, scrollable=False),
                    DeviceParam(DeviceEnum.INSERT_DELAY, DeviceParamEnum.WET, automatable=False),
                    DeviceParam(DeviceEnum.DELAY, DeviceParamEnum.WET, automatable=False),
                    InstrumentParam(InstrumentParamEnum.DELAY),
                ],
            ),
            XParam(
                "Arp",
                [
                    DeviceParam(
                        DeviceEnum.ARPEGGIATOR,
                        DeviceParamEnum.ARP_STYLE,
                        automatable=False,
                        mutable=True,
                    )
                ],
                value_items=arp_styles,
            ),
            XParam(
                "Arp rate",
                [DeviceParam(DeviceEnum.ARPEGGIATOR, DeviceParamEnum.ARP_RATE)],
                value_items=list(range(14)),
            ),
            XParam(
                "Length",
                [
                    DeviceParam(DeviceEnum.NOTE_LENGTH, DeviceParamEnum.LENGTH),
                    DeviceParam(DeviceEnum.ARPEGGIATOR, DeviceParamEnum.ARP_GATE),
                ],
            ),
            XParam(
                "LFOTool", [DeviceParam(DeviceEnum.LFO_TOOL, DeviceParamEnum.LFO_TOOL_LFO_DEPTH)]
            ),
        ]

        def add_x_param_encoder(identifier: int, x_param: XParam) -> None:
            def execute_x_param(method: Callable[[XParam], None], **k: Any) -> None:
                x_param.track = Song.selected_or_soloed_track()
                method(x_param, **k)

            self.add_encoder(
                identifier=identifier,
                name=x_param.name,
                on_press=partial(execute_x_param, instrument_service.toggle_param),
                on_long_press=partial(execute_x_param, instrument_service.toggle_param_automation),
                on_scroll=partial(execute_x_param, instrument_service.scroll_param),
            )

        for index, param in enumerate(params):
            add_x_param_encoder(index + 1, param)

        # VELO encoder
        self.add_encoder(
            identifier=15,
            name="smooth selected clip velocities",
            on_scroll=lambda: Song.selected_clip(MidiClip).scale_velocities,
        )

        add_x_param_encoder(
            16,
            XParam(
                "Volume",
                [
                    TrackParam(
                        lambda t: t.devices.mixer_device.volume,
                        limits=(db_to_volume(-10), db_to_volume(0)),
                    ),
                    DeviceParam(DeviceEnum.H_COMP, DeviceParamEnum.OUTPUT, automatable=False),
                    DeviceParam(
                        DeviceEnum.COMPRESSOR, DeviceParamEnum.OUTPUT_GAIN, automatable=False
                    ),
                    InstrumentParam(InstrumentParamEnum.VOLUME, automatable=False),
                    DeviceParam(DeviceEnum.UTILITY, DeviceParamEnum.GAIN, scrollable=False),
                ],
            ),
        )
