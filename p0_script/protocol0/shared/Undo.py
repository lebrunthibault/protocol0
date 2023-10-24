from typing import Callable, Optional


class Undo(object):
    _INSTANCE: Optional["Undo"] = None

    def __init__(self, begin_undo_step: Callable, end_undo_step: Callable) -> None:
        Undo._INSTANCE = self
        self._begin_undo_step = begin_undo_step
        self._end_undo_step = end_undo_step

    @classmethod
    def begin_undo_step(cls) -> None:
        cls._INSTANCE._end_undo_step()

    @classmethod
    def end_undo_step(cls) -> None:
        cls._INSTANCE._end_undo_step()
