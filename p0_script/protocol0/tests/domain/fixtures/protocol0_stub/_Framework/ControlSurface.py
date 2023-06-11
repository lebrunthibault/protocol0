from unittest.mock import Mock


class ControlSurface:
    def __init__(self, *a, **k):
        self.component_guard = Mock()
        self.set_highlighting_session_component = Mock()
        self.application = Mock()

    def disconnect(self):
        pass


ControlSurface.show_message = Mock()
ControlSurface._send_midi = Mock()

get_control_surfaces = Mock()
