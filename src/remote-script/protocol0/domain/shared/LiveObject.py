from typing import Protocol


class LiveObject(Protocol):
    @property
    def _live_ptr(self) -> int:
        raise NotImplementedError
