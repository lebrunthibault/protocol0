from unittest.mock import Mock

class ControlSurface:
    def __init__(self, *a, **k):
        pass

ControlSurface.show_message = Mock()
ControlSurface._send_midi = Mock()

get_control_surfaces = Mock()