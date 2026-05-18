from enum import Enum
from typing import List, TYPE_CHECKING

from protocol0.domain.shared.ui.ColorEnum import ColorEnum

if TYPE_CHECKING:
    from protocol0.domain.lom.device.Device import Device


class DeviceEnum(Enum):
    ADPTR_METRIC_AB = "ADPTR MetricAB"
    ARPEGGIATOR = "Arpeggiator"
    AUDIO_EFFECT_RACK = "Audio Effect Rack"
    AUTO_FILTER = "Auto Filter"
    AUTO_FILTER_HIGH_PASS = "Auto Filter High Pass"
    AUTO_FILTER_LOW_PASS = "Auto Filter Low Pass"
    AUTO_PAN = "AutoPan"
    BEAT_REPEAT = "Beat Repeat"
    BLACK_BOX = "Black Box Analog Design HG-2"
    COMPRESSOR = "Compressor"
    CTHULHU = "Cthulhu_x64"
    DECAPITATOR = "Decapitator"
    DE_ESSER = "DeEsser Stereo"
    DELAY = "Delay"
    DIVA = "Diva"
    DP_METER_5 = "dpMeter5"
    DRUM_BUSS = "Drum Buss"
    DRUM_RACK = "Drum Rack"
    DUCK = "Duck"
    EFFECTRIX = "Effectrix"
    EQ_EIGHT = "EQ Eight"
    EXTERNAL_AUDIO_EFFECT = "Ext. Audio Effect"
    EXTERNAL_INSTRUMENT = "Ext. Instrument"
    GATE = "Gate"
    GATEKEEPER = "Gatekeeper"
    GLUE_COMPRESSOR = "Glue Compressor"
    GOD_PARTICLE = "The God Particle"
    H_COMP = "H-Comp Stereo.vstpreset"
    H_DELAY = "H-Delay Stereo"
    KONTAKT = "Kontakt"
    INSERT_DELAY = "Delay"
    INSERT_ECHO = "Echo"
    INSERT_FILTER = "Auto Filter"
    INSERT_REVERB = "Reverb"
    INSERT_VOLUME = "Volume"
    INSTRUMENT_RACK = "Instrument Rack"
    LFO_TOOL = "LFOTool_x64"
    L2_LIMITER = "L2 Stereo"
    LIMITER = "Limiter"
    M_ANALYZER = "MAnalyzer"
    M_STEREO_SCOPE = "MStereoScope"
    MONO_SWITCH = "Mono"
    NOTE_LENGTH = "Note Length"
    OCTAVA = "Octava.adg"
    OZONE = "Ozone 9"
    OVERDRIVE = "Overdrive"
    PITCH = "Pitch"
    PRO_Q_3 = "Pro-Q 3"
    PRO_Q_3_VST3 = "FabFilter Pro-Q 3"
    PRO_Q_4 = "Pro-Q 4"
    PSY_SCOPE = "PsyScope_Pro"
    R_COMPRESSOR = "RCompressor Stereo"
    REVERB = "Reverb"
    REV2_EDITOR = "REV2Editor"
    R_VERB = "RVerb Stereo"
    SATURATOR = "Saturator"
    SATURN_2 = "Saturn 2"
    SERUM = "Serum_x64"
    SIMPLER = "Simpler"
    SOOTHE2 = "soothe2"
    SOUNDID_REFERENCE_PLUGIN = "SoundID Reference Plugin"
    SPAN = "SPAN"
    SPLICE_BRIDGE = "Splice Bridge"
    SPIFF = "spiff"
    SPECTRE = "Spectre"
    SSL_COMP = "SSLComp Stereo"
    STANDARD_CLIP = "StandardCLIP"
    SUPER_TAP_2 = "SuperTap 2-Taps Stereo"
    SUPER_TAP_6 = "SuperTap 6-Taps Stereo"
    SURFEREQ = "SurferEQ"
    SYLENTH1 = "Sylenth1"
    SYLENTH1_RACK = "Sylenth1 Rack.adg"
    SYNTH_MASTER_2 = "SynthMaster 2.vstpreset"
    TDR_KOTELNIKOV = "TDR Kotelnikov"
    TONAL_BALANCE_CONTROL = "Tonal Balance Control 2"
    TRACK_SPACER = "Trackspacer 2.5"
    TRUE_VERB = "TrueVerb Stereo"
    TUNER = "Tuner"
    UTILITY = "Utility"
    VALHALLA_VINTAGE_VERB = "ValhallaVintageVerb"
    VCOMP = "VComp Stereo"
    VEQ = "VEQ3 Stereo"
    WAVETABLE = "Wavetable"
    YOULEAN = "Youlean Loudness Meter 2"

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
            DeviceEnum.INSERT_ECHO,
            DeviceEnum.INSERT_FILTER,
            DeviceEnum.INSERT_REVERB,
            DeviceEnum.INSERT_VOLUME,
        ]

    @property
    def browser_name(self) -> str:
        try:
            return {
                DeviceEnum.EXTERNAL_AUDIO_EFFECT: "External Audio Effect",
                DeviceEnum.EXTERNAL_INSTRUMENT: "External Instrument",
            }[self]
        except KeyError:
            if self.is_device_preset:
                return "%s.adv" % self.value
            elif self.is_rack_preset:
                return "%s.adg" % self.value
            else:
                return self.value.strip()

    @property
    def class_name(self) -> str:
        try:
            return {
                DeviceEnum.AUDIO_EFFECT_RACK: "AudioEffectGroupDevice",
                DeviceEnum.AUTO_FILTER: "AutoFilter",
                DeviceEnum.EQ_EIGHT: "Eq8",
                DeviceEnum.EXTERNAL_AUDIO_EFFECT: "ProxyAudioEffectDevice",
                DeviceEnum.EXTERNAL_INSTRUMENT: "ProxyInstrumentDevice",
                DeviceEnum.INSTRUMENT_RACK: "InstrumentGroupDevice",
                DeviceEnum.PITCH: "MidiPitcher",
            }[self]
        except KeyError:
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
    def device_group_position(self) -> int:
        predicates = [
            lambda d: d.is_instrument,
            lambda d: d.is_eq,
            lambda d: d.is_filter,
            lambda d: d.is_compressor,
            lambda d: d.is_volume,
            lambda d: d.is_saturator,
            lambda d: d.is_delay,
            lambda d: d.is_reverb,
            lambda d: d.is_fx,
            lambda d: d.is_clipper,
            lambda d: d.is_limiter,
            lambda d: d == DeviceEnum.UTILITY,
            lambda d: d.is_meter,
        ]

        for index, predicate in enumerate(predicates):
            if predicate(self):  # type: ignore[no-untyped-call]
                return index

        return 0

    @property
    def is_instrument(self) -> bool:
        return self in [
            DeviceEnum.DIVA,
            DeviceEnum.DRUM_RACK,
            DeviceEnum.KONTAKT,
            DeviceEnum.REV2_EDITOR,
            DeviceEnum.SERUM,
            DeviceEnum.SPLICE_BRIDGE,
            DeviceEnum.SYLENTH1,
            DeviceEnum.SYLENTH1_RACK,
            DeviceEnum.SYNTH_MASTER_2,
            DeviceEnum.WAVETABLE,
        ]

    @property
    def is_clipper(self) -> bool:
        return self in [
            DeviceEnum.STANDARD_CLIP,
        ]

    @property
    def is_limiter(self) -> bool:
        return self in [
            DeviceEnum.LIMITER,
            DeviceEnum.L2_LIMITER,
            DeviceEnum.GOD_PARTICLE,
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
            DeviceEnum.COMPRESSOR,
            DeviceEnum.GLUE_COMPRESSOR,
            DeviceEnum.H_COMP,
            DeviceEnum.SSL_COMP,
            DeviceEnum.TDR_KOTELNIKOV,
            DeviceEnum.VCOMP,
        ]

    @property
    def is_saturator(self) -> bool:
        return self in [
            DeviceEnum.BLACK_BOX,
            DeviceEnum.DECAPITATOR,
            DeviceEnum.DRUM_BUSS,
            DeviceEnum.OVERDRIVE,
            DeviceEnum.SATURATOR,
            DeviceEnum.SATURN_2,
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
            DeviceEnum.EFFECTRIX,
        ]

    @property
    def is_meter(self) -> bool:
        return self in [
            DeviceEnum.PSY_SCOPE,
            DeviceEnum.ADPTR_METRIC_AB,
            DeviceEnum.SPAN,
            DeviceEnum.YOULEAN,
            DeviceEnum.M_ANALYZER,
        ]

    @property
    def instrument_enum(self) -> "DeviceEnum":
        """Different device enums can be linked to one instrument"""
        assert self.is_instrument, f"{self} is not an instrument"

        if self in [
            DeviceEnum.SYLENTH1,
            DeviceEnum.SYLENTH1_RACK,
        ]:
            return DeviceEnum.SYLENTH1

        if self in [
            DeviceEnum.SERUM,
        ]:
            return DeviceEnum.SERUM

        return self

    @property
    def track_name(self) -> str:
        assert self.is_instrument

        return {
            DeviceEnum.DIVA: "Diva",
            DeviceEnum.KONTAKT: "Kontakt",
            DeviceEnum.SERUM: "Serum",
            DeviceEnum.SPLICE_BRIDGE: "Splice",
            DeviceEnum.SYLENTH1: "Sylenth1",
            DeviceEnum.SYLENTH1_RACK: "Sylenth1",
        }.get(self, self.instrument_enum.value)

    @property
    def track_color(self) -> int:
        assert self.is_instrument
        return {
            DeviceEnum.SPLICE_BRIDGE: ColorEnum.FOCUSED.value,
        }.get(self, 0)
