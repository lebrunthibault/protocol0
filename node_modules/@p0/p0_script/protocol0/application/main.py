from typing import Any


def create_instance(c_instance: Any) -> Any:
    from protocol0.application.Protocol0 import Protocol0

    return Protocol0(c_instance)


def create_midi_duplicator_instance(c_instance: Any) -> Any:
    from protocol0.application.Protocol0Midi import Protocol0Midi

    return Protocol0Midi(c_instance)
