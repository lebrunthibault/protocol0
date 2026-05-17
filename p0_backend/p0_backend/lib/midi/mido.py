import mido

mido.set_backend("mido.backends.rtmidi")


def get_output_port(port_name_prefix: str):
    return _get_real_midi_port_name(
        port_name_prefix=port_name_prefix, ports=mido.get_output_names()
    )


def _get_input_port(port_name_prefix: str):
    return _get_real_midi_port_name(port_name_prefix=port_name_prefix, ports=mido.get_input_names())


def _get_real_midi_port_name(port_name_prefix: str, ports):
    # rtmidi appends " <index>" to port names (e.g. "P0_IN 4"), so we match on the
    # prefix word rather than a plain substring — otherwise "P0_IN" would match
    # "P0_IN_HTTP" because of substring containment.
    for port_name in ports:
        if port_name == port_name_prefix or port_name.startswith(f"{port_name_prefix} "):
            return port_name

    raise Exception(f"couldn't find {port_name_prefix} port")
