"""Minimal Live API stub for running the remote script outside Ableton.

Classes and enum members actually referenced by the production code are real
(so enum comparisons and isinstance checks are meaningful); any other
attribute resolves to a Mock via the module-level __getattr__.
"""
from unittest.mock import Mock

from . import (  # noqa: F401
    Application,
    Base,
    Browser,
    Chain,
    Clip,
    ClipSlot,
    Device,
    DeviceParameter,
    DrumPad,
    MixerDevice,
    PluginDevice,
    RackDevice,
    Sample,
    Scene,
    SimplerDevice,
    Song,
    Track,
)


def __getattr__(name):
    return Mock()
