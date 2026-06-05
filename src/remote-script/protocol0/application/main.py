from typing import Any


def create_instance(c_instance: Any) -> Any:
    from protocol0.application.Protocol0 import Protocol0

    return Protocol0(c_instance)
