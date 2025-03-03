from typing import Type

from protocol0.application.ContainerInterface import ContainerInterface
from protocol0.shared.types import T


class TestContainer(ContainerInterface):
    def get(self, cls: Type[T]) -> T:
        raise None
