from functools import wraps
from typing import Any

from protocol0.domain.shared.errors.ErrorRaisedEvent import ErrorRaisedEvent
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.shared.types import Func


def log_exceptions(func: Func) -> Func:
    @wraps(func)
    def decorate(*a: Any, **k: Any) -> None:
        # noinspection PyBroadException
        try:
            func(*a, **k)
        except Exception as e:
            print(e)
            DomainEventBus.emit(ErrorRaisedEvent())

    return decorate
