from typing import Optional, Callable, Iterable

from protocol0.shared.types import T


def find_if(predicate: Callable[[T], bool], seq: Iterable[T]) -> Optional[T]:
    for x in seq:
        if predicate(x):
            return x
    return None
