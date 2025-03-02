from typing import Generic
from typing import Optional, List, Iterable

from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.utils.utils import clamp
from protocol0.shared.logging.StatusBar import StatusBar
from protocol0.shared.types import T


class ValueScroller(Generic[T]):
    def __init__(self, initial_value: T) -> None:
        self._current_value = initial_value

    def __str__(self) -> str:
        return self.__class__.__name__

    @classmethod
    def scroll_values(
        cls, items: Iterable[T], current_value: Optional[T], go_next: bool, rotate: bool = True
    ) -> T:
        values: List[T] = list(items)
        if len(values) == 0:
            raise Protocol0Warning("empty list handed to scroll_values")

        if current_value not in values:
            # find the neighbor
            if current_value is not None and hasattr(current_value, "index"):
                values.append(current_value)
                values.sort(key=lambda x: x.index)
            else:
                return values[0]

        increment = 1 if go_next else -1
        current_index = values.index(current_value)
        next_index = current_index + increment

        if rotate is False:
            next_index = int(clamp(next_index, 0, len(values) - 1))
        else:
            next_index = (current_index + increment) % len(values)

        return values[next_index]

    @property
    def current_value(self) -> T:
        return self._current_value

    def scroll(self, go_next: bool) -> None:
        values = self._get_values()
        if len(values) == 0:
            return None

        self._current_value = self.scroll_values(
            values, self._get_initial_value(go_next), go_next=go_next
        )
        self._value_scrolled()

    def _get_initial_value(self, go_next: bool) -> T:
        return self._current_value

    def _get_values(self) -> List[T]:
        raise NotImplementedError

    def _value_scrolled(self) -> None:
        StatusBar.show_message("%s : %s" % (self, self.current_value))
