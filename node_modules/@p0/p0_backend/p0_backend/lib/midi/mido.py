import mido

mido.set_backend("mido.backends.pygame")


def get_output_port(port_name_prefix: str):
    return _get_real_midi_port_name(
        port_name_prefix=port_name_prefix, ports=mido.get_output_names()
    )


def _get_input_port(port_name_prefix: str):
    return _get_real_midi_port_name(port_name_prefix=port_name_prefix, ports=mido.get_input_names())


def _get_real_midi_port_name(port_name_prefix: str, ports):
    for port_name in ports:
        if port_name_prefix in port_name:
            return port_name

    raise Exception(f"couldn't find {port_name_prefix} port")
