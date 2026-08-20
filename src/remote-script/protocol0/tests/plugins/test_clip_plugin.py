from unittest.mock import Mock

import pytest

from protocol0.application.plugin.action import iter_actions
from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.plugins.ClipPlugin import ClipPlugin
from protocol0.shared.Song import Song


def test_remove_muted_notes_delegates_to_the_selected_clip(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clip = Mock()
    selected_clip = Mock(return_value=clip)
    monkeypatch.setattr(Song, "selected_clip", selected_clip)

    ClipPlugin().remove_muted_notes()

    # The MidiClip guard is what turns an audio clip into a clean Protocol0Warning.
    selected_clip.assert_called_once_with(MidiClip)
    clip.remove_muted_notes.assert_called_once_with()


def test_exposes_a_single_parameterless_action() -> None:
    actions = iter_actions(ClipPlugin())

    assert [name for name, _ in actions] == ["remove_muted_notes"]
