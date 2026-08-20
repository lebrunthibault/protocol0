from unittest.mock import Mock

import pytest

from protocol0.application.plugin.action import iter_actions
from protocol0.domain.track_recorder.RecordService import RecordService
from protocol0.plugins import RecordPlugin as record_plugin_module
from protocol0.plugins.RecordPlugin import RecordPlugin


def test_resample_selected_track_delegates_to_the_record_service(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    record_service = Mock()
    container = Mock()
    container.get.return_value = record_service
    monkeypatch.setattr(record_plugin_module, "get_container", lambda: container)

    RecordPlugin().resample_selected_track()

    container.get.assert_called_once_with(RecordService)
    record_service.resample_selected_track.assert_called_once_with()


def test_exposes_a_single_parameterless_action() -> None:
    actions = iter_actions(RecordPlugin())

    assert [name for name, _ in actions] == ["resample_selected_track"]
