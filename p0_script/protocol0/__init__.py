import sys

from protocol0.shared.module import EmptyModule

live_environment_loaded = "Live" in sys.modules

# allows accessing lint from this module from outside the Live python environment
if not live_environment_loaded:
    sys.modules["Live"] = EmptyModule("Live")
    sys.modules["MidiRemoteScript"] = EmptyModule("MidiRemoteScript")
    sys.modules["multipledispatch"] = EmptyModule("multipledispatch")
