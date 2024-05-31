from enum import Enum
from typing import Optional, Any


class DeviceParamEnum(Enum):
    AB_SWITCH = "AB_SWITCH"
    ARP_RATE = "ARP_RATE"
    ARP_GATE = "ARP_GATE"
    ARP_STYLE = "ARP_STYLE"
    AUTO_FILTER_HIGH_PASS_FREQUENCY = "AUTO_FILTER_HIGH_PASS_FREQUENCY"
    AUTO_FILTER_LOW_PASS_FREQUENCY = "AUTO_FILTER_LOW_PASS_FREQUENCY"
    AUTO_PAN_AMOUNT = "AUTO_PAN_AMOUNT"
    CHAIN_SELECTOR = "CHAIN_SELECTOR"
    DECAY = "DECAY"
    DELAY_INPUT = "DELAY_INPUT"
    DEVICE_ON = "DEVICE_ON"
    DRIVE = "DRIVE"
    DRY_WET = "DRY_WET"
    FB = "FB"
    FILTER_PRESET = "FILTER_PRESET"
    FILTER_SWITCH = "FILTER_SWITCH"
    EQ_EIGHT_1_FREQUENCY_A = "FREQUENCY_1_A"
    EQ_EIGHT_8_FREQUENCY_A = "FREQUENCY_8_A"
    GAIN = "GAIN"
    GAIN_4_A = "EQ_EIGHT_GAIN_4_A"
    GOD_PARTICLE_CHARACTER = "GOD_PARTICLE_MIX"
    INPUT = "INPUT"
    INPUT_GAIN = "INPUT_GAIN"
    LENGTH = "LENGTH"
    LFO_TOOL_LFO_DEPTH = "LFO_TOOL_LFO_DEPTH"
    MIX = "MIX"
    OCTAVA_VEL = "OCTAVA_VEL"
    OUTPUT = "OUTPUT"
    OUTPUT_GAIN = "OUTPUT_GAIN"
    PATTERN = "PATTERN"
    REVERB_INPUT = "REVERB_INPUT"
    STEREO_MODE = "STEREO_MODE"
    UTILITY_SILENT_GAIN = "UTILITY_SILENT_GAIN"
    UTILITY_MID_SIDE = "UTILITY_MID_SIDE"
    UTILITY_WIDTH = "UTILITY_WIDTH"
    WET = "WET"

    @property
    def parameter_name(self) -> str:
        return {
            DeviceParamEnum.AB_SWITCH: "AB Switch",
            DeviceParamEnum.ARP_RATE: "Synced Rate",
            DeviceParamEnum.ARP_GATE: "Gate",
            DeviceParamEnum.ARP_STYLE: "Style",
            DeviceParamEnum.AUTO_FILTER_HIGH_PASS_FREQUENCY: "Frequency",
            DeviceParamEnum.AUTO_FILTER_LOW_PASS_FREQUENCY: "Frequency",
            DeviceParamEnum.AUTO_PAN_AMOUNT: "Amount",
            DeviceParamEnum.CHAIN_SELECTOR: "Chain Selector",
            DeviceParamEnum.DECAY: "Decay",
            DeviceParamEnum.DEVICE_ON: "Device On",
            DeviceParamEnum.DRIVE: "Drive",
            DeviceParamEnum.FB: "FB",
            DeviceParamEnum.FILTER_PRESET: "Filter Preset",
            DeviceParamEnum.FILTER_SWITCH: "Filter Switch",
            DeviceParamEnum.EQ_EIGHT_1_FREQUENCY_A: "1 Frequency A",
            DeviceParamEnum.EQ_EIGHT_8_FREQUENCY_A: "8 Frequency A",
            DeviceParamEnum.GAIN: "Gain",
            DeviceParamEnum.GAIN_4_A: "4 Gain A",
            DeviceParamEnum.GOD_PARTICLE_CHARACTER: "Character",
            DeviceParamEnum.INPUT: "Input",
            DeviceParamEnum.INPUT_GAIN: "Input Gain",
            DeviceParamEnum.LENGTH: "Time Length",
            DeviceParamEnum.LFO_TOOL_LFO_DEPTH: "LFO Depth",
            DeviceParamEnum.MIX: "Mix",
            DeviceParamEnum.OCTAVA_VEL: "Vel",
            DeviceParamEnum.OUTPUT: "Output",
            DeviceParamEnum.OUTPUT_GAIN: "Output Gain",
            DeviceParamEnum.PATTERN: "Pattern",
            DeviceParamEnum.STEREO_MODE: "Stereo Mode",
            DeviceParamEnum.UTILITY_SILENT_GAIN: "Gain",
            DeviceParamEnum.UTILITY_MID_SIDE: "Mid/Side Balance",
            DeviceParamEnum.UTILITY_WIDTH: "Stereo Width",
            DeviceParamEnum.WET: "Wet",
        }[self]

    @classmethod
    def from_name(cls, device_name: str, name: str) -> Optional["DeviceParamEnum"]:
        enum_name = f"{device_name.upper()}_{name.upper()}".replace(" ", "_")
        try:
            return DeviceParamEnum[enum_name]
        except KeyError:
            return None

    @property
    def default_value(self) -> Any:
        return {
            DeviceParamEnum.AUTO_FILTER_HIGH_PASS_FREQUENCY: 20,
            DeviceParamEnum.AUTO_FILTER_LOW_PASS_FREQUENCY: 135,
            DeviceParamEnum.DELAY_INPUT: 0,
            DeviceParamEnum.EQ_EIGHT_1_FREQUENCY_A: 0,
            DeviceParamEnum.EQ_EIGHT_8_FREQUENCY_A: 1,
            DeviceParamEnum.REVERB_INPUT: 0,
            DeviceParamEnum.UTILITY_SILENT_GAIN: -1,
        }[self]
