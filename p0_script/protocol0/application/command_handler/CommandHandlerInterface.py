from typing import Any, Optional

from protocol0.application.ContainerInterface import ContainerInterface
from protocol0.shared.sequence.Sequence import Sequence


class CommandHandlerInterface(object):
    def __init__(self, container: ContainerInterface) -> None:
        self._container = container

    def handle(self, message: Any) -> Optional[Sequence]:
        raise NotImplementedError
