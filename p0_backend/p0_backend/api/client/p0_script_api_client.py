import sys

import mido


from loguru import logger

from p0_backend.lib.enum.notification_enum import NotificationEnum
from p0_backend.lib.notification import notify
from p0_backend.settings import Settings
from p0_backend.lib.midi.mido import get_output_port
from p0_backend.lib.utils import make_sysex_message_from_command
from protocol0.application.command.SerializableCommand import SerializableCommand


class P0ScriptClient(object):
    FROM_HTTP = None

    def __init__(self, midi_port_name: str):
        self._midi_port_name = midi_port_name
        self._midi_port = mido.open_output(get_output_port(self._midi_port_name), autoreset=False)

    def dispatch(self, command: SerializableCommand, log=True) -> None:
        # Pass the focused set info to the script in case of multiple sets
        from p0_backend.lib.ableton.ableton_set.ableton_set_manager import get_focused_set

        focused_set = get_focused_set()
        if focused_set is not None and command.set_id is None:
            command.set_id = focused_set.path_info.filename

        msg = make_sysex_message_from_command(command=command)
        self._midi_port.send(msg)
        if log:
            logger.info(f"Sent command to script: {command}")


def p0_script_client():
    is_midi = "midi_server" in sys.argv[0]

    if is_midi:
        notify("Cannot call p0 script from midi", NotificationEnum.WARNING)
        raise Exception("Cannot call p0 script from midi")
    else:
        if P0ScriptClient.FROM_HTTP is None:
            P0ScriptClient.FROM_HTTP = P0ScriptClient(Settings().p0_input_port_name)
        return P0ScriptClient.FROM_HTTP
