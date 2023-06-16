import time

from typing import List, Optional, Type

from protocol0.application.command.SerializableCommand import SerializableCommand
from protocol0.shared.AbstractEnum import T


class HistoryEntry(object):
    def __init__(self, command: SerializableCommand) -> None:
        self.command = command
        self.executed_at = time.time()


class CommandBusHistory(object):
    _SIZE = 20

    def __init__(self) -> None:
        self._history: List[Optional[HistoryEntry]] = [None] * self._SIZE

    def push(self, command: SerializableCommand) -> None:
        """Expect only increasing time.time"""
        self._history.append(HistoryEntry(command))

        # rotate history
        self._history = self._history[-20:]

    def get_recent_command(self, command_class: Type[T], delay: float, except_current: bool) -> Optional[T]:
        """Delay in ms"""
        time_limit = time.time() - delay

        for entry in reversed(list(filter(None, self._history))):
            if entry.executed_at < time_limit:
                return None
            if isinstance(entry.command, command_class):
                if except_current and entry.executed_at > time.time() - 0.005:  # type: ignore[unreachable]
                    continue
                return entry.command

        return None
