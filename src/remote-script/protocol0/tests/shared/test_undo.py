from unittest.mock import Mock

from protocol0.shared.Undo import Undo


def test_begin_undo_step_opens_a_step() -> None:
    # Regression: begin_undo_step used to call the *end* callable (copy-paste),
    # so no undo step was ever opened and Ctrl-Z could not revert an action.
    begin, end = Mock(), Mock()
    Undo(begin, end)

    Undo.begin_undo_step()

    begin.assert_called_once_with()
    end.assert_not_called()


def test_end_undo_step_closes_a_step() -> None:
    begin, end = Mock(), Mock()
    Undo(begin, end)

    Undo.end_undo_step()

    end.assert_called_once_with()
    begin.assert_not_called()
