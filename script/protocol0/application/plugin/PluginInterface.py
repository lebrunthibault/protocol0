from typing import ClassVar

from protocol0.application.ContainerInterface import ContainerInterface


class PluginInterface(object):
    name: ClassVar[str] = ""

    def __init__(self, container: ContainerInterface) -> None:
        self._container = container

    def should_start(self) -> bool:
        return True

    def start(self) -> None:
        raise NotImplementedError

    def stop(self) -> None:
        raise NotImplementedError
