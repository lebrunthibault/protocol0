from unittest.mock import Mock, MagicMock


class ControlSurface:
    def __init__(self, *_, **__):
        self.component_guard = MagicMock()
        self.application = Mock()

    def disconnect(self):
        pass


ControlSurface.show_message = Mock()
ControlSurface._send_midi = Mock()

get_control_surfaces = Mock()
