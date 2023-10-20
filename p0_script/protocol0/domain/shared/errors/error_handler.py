from functools import wraps

from typing import Any

from protocol0.shared.types import Func


def handle_errors(reset: bool = True) -> Func:
    def wrap(func: Func) -> Func:
        @wraps(func)
        def decorate(*a: Any, **k: Any) -> Any:
            # noinspection PyBroadException
            try:
                return func(*a, **k)
            except Exception:
                from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
                from protocol0.domain.shared.errors.ErrorRaisedEvent import ErrorRaisedEvent

                DomainEventBus.emit(ErrorRaisedEvent(reset=reset))

        return decorate

    return wrap