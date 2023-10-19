from typing import Optional, Any

from protocol0.shared.AbstractEnum import AbstractEnum


class DeviceParamEnum(AbstractEnum):
    ARP_RATE = "ARP_RATE"
    ARP_GATE = "ARP_GATE"
    ARP_STYLE = "ARP_STYLE"
    AUTO_FILTER_HIGH_PASS_FREQUENCY = "AUTO_FILTER_HIGH_PASS_FREQUENCY"
    AUTO_FILTER_LOW_PASS_FREQUENCY = "AUTO_FILTER_LOW_PASS_FREQUENCY"
    AUTO_PAN_AMOUNT = "AUTO_PAN_AMOUNT"
    CHAIN_SELECTOR = "CHAIN_SELECTOR"
    COMPRESSOR_OUTPUT_GAIN = "COMPRESSOR_OUTPUT_GAIN"
    COMPRESSOR_THRESHOLD = "COMPRESSOR_THRESHOLD"
    DEVICE_ON = "DEVICE_ON"
    DRIVE = "DRIVE"
    EFFECTRIX_GLOBALWET = "EFFECTRIX_GLOBALWET"
    FREQUENCY_1_A = "EQ_EIGHT_FREQUENCY_1_A"
    FREQUENCY_8_A = "EQ_EIGHT_FREQUENCY_8_A"
    GAIN = "GAIN"
    GAIN_4_A = "EQ_EIGHT_GAIN_4_A"
    INPUT = "INPUT"
    LENGTH = "LENGTH"
    LFO_TOOL_LFO_DEPTH = "LFO_TOOL_LFO_DEPTH"
    MIX = "MIX"
    OCTAVA_VEL = "OCTAVA_VEL"
    UTILITY_SILENT_GAIN = "UTILITY_SILENT_GAIN"
    UTILITY_MID_SIDE = "UTILITY_MID_SIDE"
    WET = "WET"

    @property
    def parameter_name(self) -> str:
        return self.get_value_from_mapping(
            {
                DeviceParamEnum.ARP_RATE: "Synced Rate",
                DeviceParamEnum.ARP_GATE: "Gate",
                DeviceParamEnum.ARP_STYLE: "Style",
                DeviceParamEnum.AUTO_FILTER_HIGH_PASS_FREQUENCY: "Frequency",
                DeviceParamEnum.AUTO_FILTER_LOW_PASS_FREQUENCY: "Frequency",
                DeviceParamEnum.AUTO_PAN_AMOUNT: "Amount",
                DeviceParamEnum.CHAIN_SELECTOR: "Chain Selector",
                DeviceParamEnum.COMPRESSOR_OUTPUT_GAIN: "Output Gain",
                DeviceParamEnum.COMPRESSOR_THRESHOLD: "Threshold",
                DeviceParamEnum.DEVICE_ON: "Device On",
                DeviceParamEnum.DRIVE: "Drive",
                DeviceParamEnum.FREQUENCY_1_A: "1 Frequency A",
                DeviceParamEnum.FREQUENCY_8_A: "8 Frequency A",
                DeviceParamEnum.GAIN: "Gain",
                DeviceParamEnum.GAIN_4_A: "4 Gain A",
                DeviceParamEnum.INPUT: "Input",
                DeviceParamEnum.LENGTH: "Time Length",
                DeviceParamEnum.LFO_TOOL_LFO_DEPTH: "LFO Depth",
                DeviceParamEnum.MIX: "Mix",
                DeviceParamEnum.OCTAVA_VEL: "Vel",
                DeviceParamEnum.UTILITY_SILENT_GAIN: "Gain",
                DeviceParamEnum.UTILITY_MID_SIDE: "Mid/Side Balance",
                DeviceParamEnum.WET: "Wet",
            }
        )

    @classmethod
    def from_name(cls, device_name: str, name: str) -> Optional["DeviceParamEnum"]:
        enum_name = f"{device_name.upper()}_{name.upper}".replace(" ", "_")
        try:
            return DeviceParamEnum[enum_name]
        except KeyError:
            return None

    @property
    def default_value(self) -> Any:
        return self.get_value_from_mapping(
            {
                DeviceParamEnum.AUTO_FILTER_HIGH_PASS_FREQUENCY: 20,
                DeviceParamEnum.AUTO_FILTER_LOW_PASS_FREQUENCY: 135,
                DeviceParamEnum.EFFECTRIX_GLOBALWET: 0,
                DeviceParamEnum.UTILITY_SILENT_GAIN: -1,
            }
        )
