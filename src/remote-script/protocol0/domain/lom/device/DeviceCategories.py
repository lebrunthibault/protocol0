"""Built-in Live device categories and the rule deciding which devices need a
MIDI track.

The tuples list the built-in Live device names per category. They live in the
domain so both the domain (``DeviceService``) and infra (``BrowserLoaderService``)
can read them without crossing the layer boundary the wrong way.
"""

AUDIO_FX = (
    "Amp",
    "Audio Effect Rack",
    "Auto Filter",
    "Auto Pan",
    "Beat Repeat",
    "Cabinet",
    "Chorus",
    "Compressor",
    "Corpus",
    "Dynamic Tube",
    "EQ Eight",
    "EQ Three",
    "Erosion",
    "External Audio Effect",
    "Filter Delay",
    "Flanger",
    "Frequency Shifter",
    "Gate",
    "Glue Compressor",
    "Grain Delay",
    "Limiter",
    "Looper",
    "Multiband Dynamics",
    "Overdrive",
    "Phaser",
    "Ping Pong Delay",
    "Redux",
    "Resonators",
    "Reverb",
    "Saturator",
    "Simple Delay",
    "Spectrum",
    "Tuner",
    "Utility",
    "Vinyl Distortion",
    "Vocoder",
    "Drum Buss",
    "Echo",
    "Pedal",
    "Channel EQ",
    "Delay",
)
MIDI_FX = (
    "Arpeggiator",
    "Chord",
    "MIDI Effect Rack",
    "Note Length",
    "Pitch",
    "Random",
    "Scale",
    "Velocity",
)
INSTRUMENTS = (
    "Analog",
    "Collision",
    "Drum Rack",
    "Electric",
    "External Instrument",
    "Impulse",
    "Instrument Rack",
    "Operator",
    "Sampler",
    "Simpler",
    "Tension",
    "Wavetable",
)

# Lower-cased sets for case-insensitive category routing.
_MIDI_FX_LOWER = {n.lower() for n in MIDI_FX}
_INSTRUMENTS_LOWER = {n.lower() for n in INSTRUMENTS}
_AUDIO_FX_LOWER = {n.lower() for n in AUDIO_FX}


def needs_midi_track(device_name: str) -> bool:
    """True if the device can only be loaded on a MIDI track.

    Instruments and MIDI effects require a MIDI track (Live rejects loading them
    onto an audio track). Audio effects and unknown names (third-party plugins /
    presets) load on the current track.
    """
    name_lower = device_name.lower()
    return name_lower in _INSTRUMENTS_LOWER or name_lower in _MIDI_FX_LOWER
