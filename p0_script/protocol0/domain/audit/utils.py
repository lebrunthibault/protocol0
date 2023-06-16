from typing import Callable, Any

from protocol0.domain.shared.backend.Backend import Backend


def tail_logs(func: Callable) -> Callable:
    def decorate(*a: Any, **k: Any) -> None:
        res = func(*a, **k)

        Backend.client().tail_logs()

        return res

    return decorate
