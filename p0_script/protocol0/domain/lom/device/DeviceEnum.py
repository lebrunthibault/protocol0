from pathlib import Path
from typing import List, Optional, Union, Any, TYPE_CHECKING

from protocol0.domain.lom.device.DeviceEnumGroup import DeviceEnumGroup
from protocol0.domain.lom.device_parameter.DeviceParamEnum import DeviceParamEnum
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.shared.AbstractEnum import AbstractEnum

if TYPE_CHECKING:
    from protocol0.domain.lom.device.Device import Device


class DeviceEnum(AbstractEnum):
    ADPTR_METRIC_AB = "ADPTR MetricAB"
    API_2500 = "API-2500 Stereo"
    ARPEGGIATOR = "Arpeggiator"
    AUDIO_EFFECT_RACK = "Audio Effect Rack"
    AUTO_FILTER = "Auto Filter"
    AUTO_FILTER_HIGH_PASS = "Auto Filter High Pass"
    AUTO_FILTER_LOW_PASS = "Auto Filter Low Pass"
    AUTO_PAN = "AutoPan"
    BEAT_REPEAT = "Beat Repeat"
    BLACK_BOX = "Black Box Analog Design HG-2.2"
    BLACK_BOX_MS = "Black Box Analog Design HG-2MS"
    CHANNEL_EQ = "Channel EQ"
    C4 = "C4 Stereo"
    COMPRESSOR = "Compressor"
    CTHULHU = "Cthulhu_x64"
    DECAPITATOR = "Decapitator"
    DE_ESSER = "DeEsser Stereo"
    DELAY = "Delay"
    DRUM_BUSS = "Drum Buss"
    DOUBLER2 = "Doubler2 Stereo"
    DOUBLER4 = "Doubler4 Stereo"
    DRUM_RACK = "Drum Rack"
    EFFECTRIX = "Effectrix"
    ENIGMA = "Enigma Stereo"
    EQ_EIGHT = "EQ Eight"
    EQ_ROOM = "EQ Room"
    EXTERNAL_AUDIO_EFFECT = "Ext. Audio Effect"
    EXTERNAL_INSTRUMENT = "Ext. Instrument"
    FREE_CLIP = "FreeClip"
    GATE = "Gate"
    GATEKEEPER = "Gatekeeper"
    GLUE_COMPRESSOR = "Glue Compressor"
    H_COMP = "H-Comp Stereo.vstpreset"
    H_DELAY = "H-Delay Stereo"
    KONTAKT = "Kontakt 7.vstpreset"
    INSERT_DELAY = "Delay Rack"
    INSERT_FILTER = "Auto Filter"
    INSERT_REVERB = "Reverb Rack"
    INSERT_VOLUME = "Volume"
    INSTRUMENT_RACK = "Instrument Rack"
    JJP_STRINGS = "JJP-Strings-Keys Stereo"
    LFO_TOOL = "LFOTool_x64"
    L1_LIMITER = "L1 limiter Stereo"
    L1_ULTRAMAXIMIZER = "L1+ Ultramaximizer Stereo"
    L2_LIMITER = "L2 Stereo"
    LIMITER = "Limiter"
    NOTE_LENGTH = "Note Length"
    OCTAVA = "Octava.adg"
    OPUS = "Opus"
    OPUS_VIOLINS = "Opus Violins.vstpreset"
    OPUS_CELLO = "Opus Cello.vstpreset"
    OPUS_CELLI = "Opus Celli.vstpreset"
    OPUS_STRINGS = "Opus Strings.vstpreset"
    OPUS_HORNS = "Opus Horns.vstpreset"
    OPUS_TRUMPETS = "Opus Trumpets.vstpreset"
    OPUS_POP_BRASS = "Opus Pop Brass.vstpreset"
    OPUS_GLOCKENSPIEL = "Opus Glockenspiel.vstpreset"
    OZONE = "Ozone 9"
    PITCH = "Pitch"
    PLAY = "play_VST_x64"
    PRO_Q_3 = "Pro-Q 3"
    PRO_Q_3_VST3 = "FabFilter Pro-Q 3"
    REFERENCE = "REFERENCE"
    REVERB = "Reverb"
    REV2_EDITOR = "REV2Editor"
    R_VERB = "RVerb Stereo"
    SATURATOR = "Saturator"
    SATURN_2 = "Saturn 2"
    SAUSAGE_FATTENER = "Sausage Fattener"
    SERUM = "Serum_x64"
    SERUM_RACK = "Serum Rack.adg"
    SERUM_BASS = "Serum_x64"
    SERUM_KEYS = "Serum_x64"
    SERUM_LEAD = "Serum_x64"
    SERUM_PLUCK = "Serum_x64"
    SIMPLER = "Simpler"
    SOOTHE2 = "soothe2"
    SOUNDID_REFERENCE_PLUGIN = "SoundID Reference Plugin"
    SPLICE = "Splice Bridge"
    SPIFF = "spiff"
    SSL_COMP = "SSLComp Stereo"
    STANDARD_CLIP = "StandardCLIP.vstpreset"
    SUPER_TAP_2 = "SuperTap 2-Taps Stereo"
    SUPER_TAP_6 = "SuperTap 6-Taps Stereo"
    SURFEREQ = "SurferEQ"
    SYLENTH1 = "Sylenth1"
    SYLENTH1_RACK = "Sylenth1 Rack.adg"
    SYLENTH1_BASS = "Sylenth1 Rack.adg "
    SYLENTH1_KEYS = "Sylenth1 Rack.adg  "
    SYLENTH1_LEAD = "Sylenth1 Rack.adg   "
    SYLENTH1_PLUCK = "Sylenth1 Rack.adg    "
    SYNTH_MASTER_2 = "SynthMaster 2.vstpreset"
    TRACK_SPACER = "Trackspacer 2.5"
    TRUE_VERB = "TrueVerb Stereo"
    TUNER = "Tuner"
    USAMO = "usamo_x64"
    UTILITY = "Utility"
    VALHALLA_VINTAGE_VERB = "ValhallaVintageVerb"
    VCOMP = "VComp Stereo"
    VEQ = "VEQ3 Stereo"
    YOULEAN = "Youlean Loudness Meter 2"

    @classmethod
    def from_value(cls, value: Any) -> "DeviceEnum":  # type: ignore[override]
        for _, enum in cls.__members__.items():
            if value == Path(enum.value).stem:  # removes the extension
                return enum

        raise Protocol0Error("Couldn't find matching enum for value %s" % value)

    @property
    def is_device_preset(self) -> bool:
        return self in [
            DeviceEnum.AUTO_FILTER_HIGH_PASS,
            DeviceEnum.AUTO_FILTER_LOW_PASS,
            DeviceEnum.EQ_ROOM,
        ]

    @property
    def is_rack_preset(self) -> bool:
        return self in [
            DeviceEnum.INSERT_DELAY,
            DeviceEnum.INSERT_FILTER,
            DeviceEnum.INSERT_REVERB,
            DeviceEnum.INSERT_VOLUME,
        ]

    @property
    def is_external_device(self) -> bool:
        return self.value in ("Ext. Audio Effect", "Ext. Instrument")

    @property
    def can_be_saved(self) -> bool:
        return self not in [DeviceEnum.REV2_EDITOR, DeviceEnum.PLAY, DeviceEnum.OPUS]

    @property
    def browser_name(self) -> str:
        try:
            return self.get_value_from_mapping(
                {
                    DeviceEnum.EXTERNAL_AUDIO_EFFECT: "External Audio Effect",
                    DeviceEnum.EXTERNAL_INSTRUMENT: "External Instrument",
                }
            )
        except Protocol0Error:
            if self.is_device_preset:
                return "%s.adv" % self.value
            elif self.is_rack_preset:
                return "%s.adg" % self.value
            else:
                return self.value.strip()

    @property
    def class_name(self) -> str:
        try:
            return self.get_value_from_mapping(
                {
                    DeviceEnum.AUDIO_EFFECT_RACK: "AudioEffectGroupDevice",
                    DeviceEnum.AUTO_FILTER: "AutoFilter",
                    DeviceEnum.EQ_EIGHT: "Eq8",
                    DeviceEnum.EXTERNAL_AUDIO_EFFECT: "ProxyAudioEffectDevice",
                    DeviceEnum.EXTERNAL_INSTRUMENT: "ProxyInstrumentDevice",
                    DeviceEnum.INSTRUMENT_RACK: "InstrumentGroupDevice",
                    DeviceEnum.PITCH: "MidiPitcher",
                }
            )
        except Protocol0Error:
            return self.value

    def matches(self, device: "Device") -> bool:
        from protocol0.domain.lom.device.RackDevice import RackDevice

        insert_devices = {
            DeviceEnum.INSERT_DELAY: DeviceEnum.DELAY,
            DeviceEnum.INSERT_REVERB: DeviceEnum.VALHALLA_VINTAGE_VERB,
        }

        for insert_enum, device_enum in insert_devices.items():
            if self == insert_enum and isinstance(device, RackDevice):
                for chain in device.chains:
                    if any(device.enum == device_enum for device in chain.devices):
                        return True

        return device.enum == self

    @property
    def default_parameter(self) -> Optional[DeviceParamEnum]:
        """Represents the main parameter for a specific device. We want to make it easily accessible"""
        try:
            return self.get_value_from_mapping(
                {
                    DeviceEnum.AUTO_FILTER_HIGH_PASS: DeviceParamEnum.AUTO_FILTER_HIGH_PASS_FREQUENCY,
                    DeviceEnum.AUTO_FILTER_LOW_PASS: DeviceParamEnum.AUTO_FILTER_LOW_PASS_FREQUENCY,
                    DeviceEnum.AUTO_PAN: DeviceParamEnum.AUTO_PAN_AMOUNT,
                    DeviceEnum.INSERT_DELAY: DeviceParamEnum.INPUT,
                    DeviceEnum.INSERT_REVERB: DeviceParamEnum.INPUT,
                    DeviceEnum.LIMITER: DeviceParamEnum.GAIN,
                    DeviceEnum.LFO_TOOL: DeviceParamEnum.LFO_TOOL_LFO_DEPTH,
                    DeviceEnum.SATURATOR: DeviceParamEnum.DRIVE,
                    DeviceEnum.UTILITY: DeviceParamEnum.GAIN,
                }
            )
        except Protocol0Error:
            return None

    @classmethod
    def favorites(cls) -> List[List[Union["DeviceEnum", DeviceEnumGroup]]]:
        return [
            [
                DeviceEnumGroup(
                    "Filter",
                    [cls.AUTO_FILTER_LOW_PASS, cls.AUTO_FILTER_HIGH_PASS],
                ),
                DeviceEnumGroup("EQ", [cls.EQ_EIGHT, cls.PRO_Q_3, cls.CHANNEL_EQ]),
                cls.UTILITY,
            ],
            [
                DeviceEnumGroup("Comp", [cls.H_COMP, cls.SSL_COMP, cls.COMPRESSOR, cls.C4]),
                DeviceEnumGroup(
                    "Sat",
                    [
                        cls.BLACK_BOX,
                        cls.SAUSAGE_FATTENER,
                        cls.SATURN_2,
                        cls.SATURATOR,
                        cls.DECAPITATOR,
                    ],
                ),
                DeviceEnumGroup("Clip", [cls.STANDARD_CLIP]),
            ],
            [
                cls.LFO_TOOL,
                DeviceEnumGroup(
                    "Delay", [cls.INSERT_DELAY, cls.SUPER_TAP_6, cls.SUPER_TAP_2, cls.DELAY]
                ),
                DeviceEnumGroup(
                    "Reverb", [cls.INSERT_REVERB, cls.VALHALLA_VINTAGE_VERB, cls.TRUE_VERB]
                ),
            ],
            [
                cls.DRUM_RACK,
                cls.KONTAKT,
                cls.SERUM,
            ],
        ]

    @property
    def load_time(self) -> int:
        """
        load time in ms : by how much loading a single device / plugin instance slows down the set startup
        measured by loading multiple device instances (20) in an empty set and timing multiple times the set load
        very rough approximation of the performance impact of a device on the whole set
        """
        try:
            return self.get_value_from_mapping(
                {
                    DeviceEnum.API_2500: 95,
                    DeviceEnum.AUDIO_EFFECT_RACK: 8,
                    DeviceEnum.AUTO_FILTER: 7,
                    DeviceEnum.BEAT_REPEAT: 7,
                    DeviceEnum.COMPRESSOR: 11,
                    DeviceEnum.DECAPITATOR: 309,
                    DeviceEnum.DE_ESSER: 90,
                    DeviceEnum.DELAY: 10,
                    DeviceEnum.DRUM_BUSS: 18,
                    DeviceEnum.DOUBLER2: 43,
                    DeviceEnum.DOUBLER4: 46,
                    DeviceEnum.EFFECTRIX: 133,
                    DeviceEnum.ENIGMA: 0,
                    DeviceEnum.EQ_EIGHT: 31,
                    DeviceEnum.EQ_ROOM: 31,
                    DeviceEnum.EXTERNAL_AUDIO_EFFECT: 5,
                    DeviceEnum.EXTERNAL_INSTRUMENT: 20,
                    DeviceEnum.FREE_CLIP: 40,
                    DeviceEnum.KONTAKT: 1000,
                    DeviceEnum.GATE: 7,
                    DeviceEnum.GATEKEEPER: 130,
                    DeviceEnum.GLUE_COMPRESSOR: 6,
                    DeviceEnum.H_COMP: 75,
                    DeviceEnum.INSTRUMENT_RACK: 10,
                    DeviceEnum.JJP_STRINGS: 280,
                    DeviceEnum.LFO_TOOL: 180,
                    DeviceEnum.L1_LIMITER: 64,
                    DeviceEnum.L1_ULTRAMAXIMIZER: 64,
                    DeviceEnum.LIMITER: 5,
                    DeviceEnum.PITCH: 2,
                    DeviceEnum.PLAY: 214,
                    DeviceEnum.PRO_Q_3: 53,
                    DeviceEnum.PRO_Q_3_VST3: 53,
                    DeviceEnum.REVERB: 9,
                    DeviceEnum.REV2_EDITOR: 80,
                    DeviceEnum.R_VERB: 114,
                    DeviceEnum.SATURATOR: 8,
                    DeviceEnum.SATURN_2: 50,
                    DeviceEnum.SERUM: 147,
                    DeviceEnum.SIMPLER: 56,
                    DeviceEnum.SOOTHE2: 206,
                    DeviceEnum.SOUNDID_REFERENCE_PLUGIN: 0,
                    DeviceEnum.SPIFF: 270,
                    DeviceEnum.SSL_COMP: 81,
                    DeviceEnum.SUPER_TAP_2: 45,
                    DeviceEnum.SUPER_TAP_6: 45,
                    DeviceEnum.SURFEREQ: 116,
                    DeviceEnum.SYLENTH1: 314,
                    DeviceEnum.TRACK_SPACER: 207,
                    DeviceEnum.TRUE_VERB: 82,
                    DeviceEnum.TUNER: 0,
                    DeviceEnum.USAMO: 78,
                    DeviceEnum.UTILITY: 4,
                    DeviceEnum.VALHALLA_VINTAGE_VERB: 71,
                    DeviceEnum.VCOMP: 52,
                    DeviceEnum.VEQ: 55,
                }
            )
        except Protocol0Error:
            return 0

    @property
    def device_group_position(self) -> int:
        predicates = [
            lambda d: d.is_instrument,
            lambda d: d.is_eq,
            lambda d: d.is_filter,
            lambda d: d.is_compressor,
            lambda d: d.is_saturator,
            lambda d: d.is_volume,
            lambda d: d.is_delay,
            lambda d: d.is_reverb,
            lambda d: d.is_fx,
            lambda d: d.is_limiter,
            lambda d: d == DeviceEnum.UTILITY,
            lambda d: d == DeviceEnum.STANDARD_CLIP,
        ]

        for index, predicate in enumerate(predicates):
            if predicate(self):  # type: ignore[no-untyped-call]
                return index

        return 0

    @property
    def is_instrument(self) -> bool:
        return self in [
            DeviceEnum.DRUM_RACK,
            DeviceEnum.KONTAKT,
            DeviceEnum.OPUS,
            DeviceEnum.PLAY,
            DeviceEnum.REV2_EDITOR,
            DeviceEnum.SERUM,
            DeviceEnum.SERUM_RACK,
            DeviceEnum.SERUM_BASS,
            DeviceEnum.SERUM_KEYS,
            DeviceEnum.SERUM_LEAD,
            DeviceEnum.SERUM_PLUCK,
            DeviceEnum.SPLICE,
            DeviceEnum.SYLENTH1,
            DeviceEnum.SYLENTH1_RACK,
            DeviceEnum.SYLENTH1_BASS,
            DeviceEnum.SYLENTH1_KEYS,
            DeviceEnum.SYLENTH1_LEAD,
            DeviceEnum.SYLENTH1_PLUCK,
            DeviceEnum.SYNTH_MASTER_2,
        ]

    @property
    def is_harmony_instrument(self) -> bool:
        return self in [
            DeviceEnum.SERUM_KEYS,
            DeviceEnum.SYLENTH1_KEYS,
            DeviceEnum.SERUM_PLUCK,
            DeviceEnum.SYLENTH1_PLUCK,
        ]

    @property
    def is_melody_instrument(self) -> bool:
        return self in [
            DeviceEnum.SERUM_LEAD,
            DeviceEnum.SYLENTH1_LEAD,
        ]

    @property
    def is_bass_instrument(self) -> bool:
        return self in [
            DeviceEnum.SERUM_BASS,
            DeviceEnum.SYLENTH1_BASS,
        ]

    @property
    def is_limiter(self) -> bool:
        return self in [
            DeviceEnum.LIMITER,
            DeviceEnum.L1_LIMITER,
            DeviceEnum.L1_ULTRAMAXIMIZER,
            DeviceEnum.L2_LIMITER,
        ]

    @property
    def is_eq(self) -> bool:
        return self in [
            DeviceEnum.EQ_EIGHT,
            DeviceEnum.DE_ESSER,
            DeviceEnum.PRO_Q_3,
            DeviceEnum.PRO_Q_3_VST3,
            DeviceEnum.SOOTHE2,
            DeviceEnum.SURFEREQ,
            DeviceEnum.VEQ,
        ]

    @property
    def is_compressor(self) -> bool:
        return self in [
            DeviceEnum.API_2500,
            DeviceEnum.COMPRESSOR,
            DeviceEnum.GLUE_COMPRESSOR,
            DeviceEnum.H_COMP,
            DeviceEnum.L1_LIMITER,
            DeviceEnum.SSL_COMP,
            DeviceEnum.VCOMP,
        ]

    @property
    def is_saturator(self) -> bool:
        return self in [
            DeviceEnum.BLACK_BOX,
            DeviceEnum.DECAPITATOR,
            DeviceEnum.DRUM_BUSS,
            DeviceEnum.JJP_STRINGS,
            DeviceEnum.SATURATOR,
            DeviceEnum.SATURN_2,
            DeviceEnum.SAUSAGE_FATTENER,
        ]

    @property
    def is_filter(self) -> bool:
        return self in [
            DeviceEnum.AUTO_FILTER,
            DeviceEnum.AUTO_FILTER_HIGH_PASS,
            DeviceEnum.AUTO_FILTER_LOW_PASS,
            DeviceEnum.INSERT_FILTER,
        ]

    @property
    def is_volume(self) -> bool:
        return self in [
            DeviceEnum.GATEKEEPER,
            DeviceEnum.INSERT_VOLUME,
            DeviceEnum.LFO_TOOL,
            DeviceEnum.TRACK_SPACER,
        ]

    @property
    def is_delay(self) -> bool:
        return self in [
            DeviceEnum.DELAY,
            DeviceEnum.ENIGMA,
            DeviceEnum.H_DELAY,
            DeviceEnum.INSERT_DELAY,
            DeviceEnum.SUPER_TAP_2,
            DeviceEnum.SUPER_TAP_6,
        ]

    @property
    def is_reverb(self) -> bool:
        return self in [
            DeviceEnum.INSERT_REVERB,
            DeviceEnum.REVERB,
            DeviceEnum.R_VERB,
            DeviceEnum.TRUE_VERB,
            DeviceEnum.VALHALLA_VINTAGE_VERB,
        ]

    @property
    def is_fx(self) -> bool:
        return self in [
            DeviceEnum.AUTO_PAN,
            DeviceEnum.DOUBLER2,
            DeviceEnum.DOUBLER4,
            DeviceEnum.EFFECTRIX,
        ]

    @property
    def instrument_enum(self) -> "DeviceEnum":
        """Different device enums can be linked to one instrument"""
        assert self.is_instrument, f"{self} is not an instrument"

        if self in [
            DeviceEnum.SYLENTH1,
            DeviceEnum.SYLENTH1_RACK,
            DeviceEnum.SYLENTH1_BASS,
            DeviceEnum.SYLENTH1_KEYS,
            DeviceEnum.SYLENTH1_LEAD,
            DeviceEnum.SYLENTH1_PLUCK,
        ]:
            return DeviceEnum.SYLENTH1

        if self in [
            DeviceEnum.SERUM,
            DeviceEnum.SERUM_RACK,
            DeviceEnum.SERUM_BASS,
            DeviceEnum.SERUM_KEYS,
            DeviceEnum.SERUM_LEAD,
            DeviceEnum.SERUM_PLUCK,
        ]:
            return DeviceEnum.SERUM

        return self

    @property
    def track_name(self) -> str:
        assert self.is_instrument
        return {
            DeviceEnum.SYLENTH1: "Sylenth1",
            DeviceEnum.SYLENTH1_RACK: "Sylenth1",
            DeviceEnum.SYLENTH1_BASS: "Bass",
            DeviceEnum.SYLENTH1_KEYS: "Keys",
            DeviceEnum.SYLENTH1_LEAD: "Lead",
            DeviceEnum.SYLENTH1_PLUCK: "Pluck",
            DeviceEnum.SERUM: "Serum",
            DeviceEnum.SERUM_RACK: "Serum",
            DeviceEnum.SERUM_BASS: "Bass",
            DeviceEnum.SERUM_KEYS: "Keys",
            DeviceEnum.SERUM_LEAD: "Lead",
            DeviceEnum.SERUM_PLUCK: "Pluck",
        }.get(self, self.instrument_enum.value)
