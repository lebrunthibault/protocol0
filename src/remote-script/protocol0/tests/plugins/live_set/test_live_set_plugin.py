from unittest.mock import Mock

import pytest

from protocol0.plugins.live_set.LiveSetPlugin import LiveSetPlugin
from protocol0.shared.Song import Song


def _make_device(param_count: int) -> Mock:
    device = Mock()
    device.parameters = [Mock() for _ in range(param_count)]
    return device


def test_scroll_macro_targets_the_parameter_after_device_on(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    device = _make_device(9)
    monkeypatch.setattr(Song, "selected_device", lambda: device)

    LiveSetPlugin._scroll_macro(0, True)

    # encoder 0 drives parameters[1]: parameters[0] is "Device On"
    device.parameters[1].scroll.assert_called_once_with(True)
    device.parameters[0].scroll.assert_not_called()

    LiveSetPlugin._scroll_macro(7, False)
    device.parameters[8].scroll.assert_called_once_with(False)


def test_scroll_macro_without_selected_device_is_a_noop(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(Song, "selected_device", lambda: None)

    LiveSetPlugin._scroll_macro(0, True)  # must not raise


def test_scroll_macro_out_of_range_is_a_noop(monkeypatch: pytest.MonkeyPatch) -> None:
    device = _make_device(3)
    monkeypatch.setattr(Song, "selected_device", lambda: device)

    LiveSetPlugin._scroll_macro(7, True)  # must not raise

    for param in device.parameters:
        param.scroll.assert_not_called()


def test_registers_eight_scroll_only_encoders() -> None:
    encoders = Mock()

    LiveSetPlugin().register_encoders(encoders)

    assert encoders.add_encoder.call_count == 8
    for i, call in enumerate(encoders.add_encoder.call_args_list):
        assert call.kwargs["channel"] == 3
        assert call.kwargs["identifier"] == i
        assert call.kwargs["scroll_only"] is True
        assert callable(call.kwargs["on_scroll"])
