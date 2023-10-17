from typing import Optional, Any, TYPE_CHECKING

from protocol0.shared.AbstractEnum import AbstractEnum

if TYPE_CHECKING:
    pass


class DeviceParameterEnum(AbstractEnum):
    AUTO_FILTER_HIGH_PASS_FREQUENCY = "AUTO_FILTER_HIGH_PASS_FREQUENCY"
    AUTO_FILTER_LOW_PASS_FREQUENCY = "AUTO_FILTER_LOW_PASS_FREQUENCY"
    AUTO_PAN_AMOUNT = "AUTO_PAN_AMOUNT"
    CHAIN_SELECTOR = "CHAIN_SELECTOR"
    COMPRESSOR_OUTPUT_GAIN = "COMPRESSOR_OUTPUT_GAIN"
    COMPRESSOR_THRESHOLD = "COMPRESSOR_THRESHOLD"
    DEVICE_ON = "DEVICE_ON"
    EFFECTRIX_GLOBALWET = "EFFECTRIX_GLOBALWET"
    EQ_EIGHT_FREQUENCY_1_A = "EQ_EIGHT_FREQUENCY_1_A"
    EQ_EIGHT_FREQUENCY_8_A = "EQ_EIGHT_FREQUENCY_8_A"
    EQ_EIGHT_GAIN_4_A = "EQ_EIGHT_GAIN_4_A"
    INPUT = "INPUT"
    INSERT_DELAY_INPUT = "INSERT_DELAY_INPUT"
    LFO_TOOL_LFO_DEPTH = "LFO_TOOL_LFO_DEPTH"
    LIMITER_GAIN = "LIMITER_GAIN"
    SATURATOR_DRIVE = "SATURATOR_DRIVE"
    SATURATOR_OUTPUT = "SATURATOR_OUTPUT"
    UTILITY_GAIN = "UTILITY_GAIN"
    UTILITY_SILENT_GAIN = "UTILITY_SILENT_GAIN"
    UTILITY_MID_SIDE = "UTILITY_MID_SIDE"
    WET = "WET"

    @property
    def parameter_name(self) -> str:
        return self.get_value_from_mapping(
            {
                DeviceParameterEnum.AUTO_FILTER_HIGH_PASS_FREQUENCY: "Frequency",
                DeviceParameterEnum.AUTO_FILTER_LOW_PASS_FREQUENCY: "Frequency",
                DeviceParameterEnum.AUTO_PAN_AMOUNT: "Amount",
                DeviceParameterEnum.CHAIN_SELECTOR: "Chain Selector",
                DeviceParameterEnum.COMPRESSOR_OUTPUT_GAIN: "Output Gain",
                DeviceParameterEnum.COMPRESSOR_THRESHOLD: "Threshold",
                DeviceParameterEnum.DEVICE_ON: "Device On",
                DeviceParameterEnum.EQ_EIGHT_FREQUENCY_1_A: "1 Frequency A",
                DeviceParameterEnum.EQ_EIGHT_FREQUENCY_8_A: "8 Frequency A",
                DeviceParameterEnum.EQ_EIGHT_GAIN_4_A: "4 Gain A",
                DeviceParameterEnum.INPUT: "Input",
                DeviceParameterEnum.INSERT_DELAY_INPUT: "Input",
                DeviceParameterEnum.LFO_TOOL_LFO_DEPTH: "LFO Depth",
                DeviceParameterEnum.LIMITER_GAIN: "Gain",
                DeviceParameterEnum.SATURATOR_DRIVE: "Drive",
                DeviceParameterEnum.SATURATOR_OUTPUT: "Output",
                DeviceParameterEnum.UTILITY_GAIN: "Gain",
                DeviceParameterEnum.UTILITY_SILENT_GAIN: "Gain",
                DeviceParameterEnum.UTILITY_MID_SIDE: "Mid/Side Balance",
                DeviceParameterEnum.WET: "Wet",
            }
        )

    @classmethod
    def from_name(cls, device_name: str, name: str) -> Optional["DeviceParameterEnum"]:
        enum_name = f"{device_name.upper()}_{name.upper}".replace(" ", "_")
        try:
            return DeviceParameterEnum[enum_name]
        except KeyError:
            return None

    @property
    def default_value(self) -> Any:
        return self.get_value_from_mapping(
            {
                DeviceParameterEnum.AUTO_FILTER_HIGH_PASS_FREQUENCY: 20,
                DeviceParameterEnum.AUTO_FILTER_LOW_PASS_FREQUENCY: 135,
                DeviceParameterEnum.EFFECTRIX_GLOBALWET: 0,
                DeviceParameterEnum.UTILITY_SILENT_GAIN: -1,
            }
        )
