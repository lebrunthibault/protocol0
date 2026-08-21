import os
import sys
from unittest.mock import Mock

live_environment_loaded = "Live" in sys.modules

# allows accessing lint from this module from outside the Live python environment:
# Live and _Framework resolve to the stub package, where enum members and
# listener notifications are real objects instead of Mock attributes
if not live_environment_loaded:
    _stub_path = os.path.join(
        os.path.dirname(__file__), "tests", "domain", "fixtures", "protocol0_stub"
    )
    if _stub_path not in sys.path:
        sys.path.insert(0, _stub_path)

    sys.modules["MidiRemoteScript"] = Mock()
